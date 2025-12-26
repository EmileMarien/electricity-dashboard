@dataclass
class ProtectedVolume:
    name: str
    id: str = field(default_factory=generate_new_id)
    epb_units: List["EpbUnit"] = field(default_factory=list)

    def get_epb_units(self) -> List["EpbUnit"]:
        return self.epb_units

    def add_epb_unit(self, eu: "EpbUnit") -> None:
        self.epb_units.append(eu)

    def remove_epb_unit(self, eu: "EpbUnit") -> None:
        self.epb_units.remove(eu)

    def clean_hierarchy(self) -> bool:
        """
        Calls clean_hierarchy() on each EpbUnit.
        If an EpbUnit returns True, it is removed.
        Returns True if there are no EpbUnits left.
        """
        kept: List[EpbUnit] = []
        for epb in self.epb_units:
            if not epb.clean_hierarchy():
                kept.append(epb)
        self.epb_units = kept
        return len(self.epb_units) == 0

    def get_energetic_sectors(self) -> List[str]:
        """
        Collects energetic sectors from all EpbUnits, returns unique list (stable order).
        """
        seen = set()
        result: List[str] = []
        for epb in self.epb_units:
            for sid in epb.get_energetic_sectors():
                if sid not in seen:
                    seen.add(sid)
                    result.append(sid)
        return result

    # JSON
    def serialize(self) -> str:
        return serialize_to_json(self)

    @staticmethod
    def deserialize(json_str: str) -> "ProtectedVolume":
        return deserialize_from_json(ProtectedVolume, json_str)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ProtectedVolume":
        epb_units = [EpbUnit.from_dict(d) for d in data.get("epb_units", [])]
        return ProtectedVolume(
            id=data.get("id", generate_new_id()),
            name=data["name"],
            epb_units=epb_units,
        )



@dataclass
class EpbUnit:
    name: str
    id: str = field(default_factory=generate_new_id)
    total_surface: float = 0.0
    ventilation_zones: List[VentilationZone] = field(default_factory=list)

    def get_ventilation_zones(self) -> List[VentilationZone]:
        return self.ventilation_zones

    def add_ventilation_zone(self, vz: VentilationZone) -> None:
        self.ventilation_zones.append(vz)

    def remove_ventilation_zone(self, vz: VentilationZone) -> None:
        self.ventilation_zones.remove(vz)

    def clean_hierarchy(self) -> bool:
        """
        Calls clean_hierarchy() on each VentilationZone.
        If a VentilationZone returns True, it is removed.
        Returns True if there are no VentilationZones left.
        """
        kept: List[VentilationZone] = []
        for vz in self.ventilation_zones:
            if not vz.clean_hierarchy():
                kept.append(vz)
        self.ventilation_zones = kept
        return len(self.ventilation_zones) == 0

    def get_energetic_sectors(self) -> List[str]:
        """
        Collects energetic sector ids from all ventilation zones, returns unique list (stable order).
        """
        seen = set()
        result: List[str] = []
        for vz in self.ventilation_zones:
            for sid in vz.energetic_sector_ids:
                if sid not in seen:
                    seen.add(sid)
                    result.append(sid)
        return result

    def calculate_total_surface(self, energetic_sectors: List[EnergeticSector]) -> None:
        """
        Equivalent to the LINQ query:
        - take energetic sectors referenced by ventilation zones
        - take their components (and nested components recursively)
        - filter floors
        - sum their area
        """
        # Collect all referenced energetic sectors
        es_objs: List[EnergeticSector] = []
        for vz in self.ventilation_zones:
            es_objs.extend(vz.get_energetic_sectors(energetic_sectors))

        total = 0.0
        for es in es_objs:
            for c in (es.components or []):
                for sub in c.get_all_components_recursive():
                    if sub.category == "Floors":
                        total += float(sub.area)

        self.total_surface = total

    # JSON
    def serialize(self) -> str:
        return serialize_to_json(self)

    @staticmethod
    def deserialize(json_str: str) -> "EpbUnit":
        return deserialize_from_json(EpbUnit, json_str)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EpbUnit":
        vzs = []
        for d in data.get("ventilation_zones", []):
            # if your VentilationZone becomes a richer class, expand this
            vzs.append(VentilationZone(energetic_sector_ids=d.get("energetic_sector_ids", [])))
        return EpbUnit(
            id=data.get("id", generate_new_id()),
            name=data["name"],
            total_surface=float(data.get("total_surface", 0.0)),
            ventilation_zones=vzs,
        )