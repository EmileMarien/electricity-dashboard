from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, List, Optional
import xml.etree.ElementTree as ET


class XMLCreator:
    """
    Python port of the C# XMLCreator.

    Notes vs C#:
    - Uses xml.etree.ElementTree for XML building.
    - No WinForms MessageBox/SaveFileDialog here; provide `save_xml(path)` and return strings.
    - Keeps a per-instance `stored_ids` list like the C# class field.
    - Stores the generated XML at the *class* level (`_generated_xml`) to match the static field behavior.
    """

    _generated_xml: Optional[ET.Element] = None

    def __init__(self, energy_project, energetic_sectors):
        self.stored_ids: List[str] = []

        try:
            ns_uri = "urn:peb:bim"
            ns = f"{{{ns_uri}}}"  # ElementTree namespace syntax
            ET.register_namespace("urn", ns_uri)

            root = ET.Element(
                f"{ns}Project",
                {
                    f"{{http://www.w3.org/2000/xmlns/}}urn": ns_uri,
                    "name": self.validate_name(getattr(energy_project, "ProjectName", None)),
                    "Version": "1.0.0",
                },
            )

            creation_date = getattr(energy_project, "CreationDate", None)
            creation_date_str = self._fmt_date_yyyy_mm_dd(creation_date)

            project_info = ET.SubElement(
                root,
                f"{ns}ProjectInformation",
                {"xml-creation-date": creation_date_str},
            )
            xsd_version = ET.SubElement(project_info, f"{ns}xsd-version")
            xsd_version.text = "2.0.0"

            # Buildings
            for building in getattr(energy_project, "Buildings", []) or []:
                building_elem = ET.SubElement(
                    root,
                    f"{ns}Building",
                    {
                        "name": self.validate_name(getattr(building, "Name", None)),
                        "id": self.validate_id(getattr(building, "Id", None)),
                    },
                )

                for pv in getattr(building, "ProtectedVolumes", []) or []:
                    pv_elem = ET.SubElement(
                        building_elem,
                        f"{ns}ProtectedVolume",
                        {
                            "name": self.validate_name(getattr(pv, "Name", None)),
                            "id": self.validate_id(getattr(pv, "Id", None)),
                        },
                    )

                    for epb in getattr(pv, "EpbUnits", []) or []:
                        epb_elem = ET.SubElement(
                            pv_elem,
                            f"{ns}EpbUnit",
                            {
                                "name": self.validate_name(getattr(epb, "Name", None)),
                                "id": self.validate_id(getattr(epb, "Id", None)),
                            },
                        )

                        total_surface = ET.SubElement(epb_elem, f"{ns}total-surface")
                        total_surface.text = str(
                            self.validate_double(float(getattr(epb, "TotalSurface", 0.0)), "total-surface")
                        )

                        for vz in getattr(epb, "VentilationZones", []) or []:
                            vz_elem = ET.SubElement(
                                epb_elem,
                                f"{ns}VentilationZone",
                                {
                                    "name": self.validate_name(getattr(vz, "Name", None)),
                                    "id": self.validate_id(getattr(vz, "Id", None)),
                                },
                            )

                            # C# calls vz.GetEnergeticSectors(energeticSectors)
                            sectors = vz.GetEnergeticSectors(energetic_sectors)

                            for sector in sectors or []:
                                sector_elem = ET.SubElement(
                                    vz_elem,
                                    f"{ns}EnergeticSector",
                                    {
                                        "name": self.validate_name(getattr(sector, "Name", None)),
                                        "id": self.validate_id(getattr(sector, "Id", None)),
                                    },
                                )

                                volume = ET.SubElement(sector_elem, f"{ns}volume")
                                volume.text = str(
                                    self.validate_double(float(getattr(sector, "Volume", 0.0)), "volume")
                                )

                                content_elem = ET.SubElement(sector_elem, f"{ns}EnergeticSectorContent")

                                # Spaces
                                for space in getattr(sector, "Spaces", []) or []:
                                    space_elem = ET.SubElement(
                                        content_elem,
                                        f"{ns}Space",
                                        {
                                            "name": self.validate_name(getattr(space, "Name", None)),
                                            "id": self.validate_id(str(getattr(space, "Id", ""))),
                                        },
                                    )
                                    usage_surface = ET.SubElement(space_elem, f"{ns}usage-surface")
                                    usage_surface.text = str(
                                        self.validate_double(float(getattr(space, "Area", 0.0)), "usage-surface")
                                    )

                                # Components (Walls/Windows/Floors/Roofs/Doors)
                                for component in getattr(sector, "Components", []) or []:
                                    category = getattr(component, "Category", None)

                                    construction_type = None
                                    if category == "Walls":
                                        construction_type = "wall"
                                    elif category == "Windows":
                                        construction_type = "window"
                                    elif category == "Floors":
                                        construction_type = "floor-ground"
                                        # In C# they log if missing; here we just pass through/validate later.
                                    elif category == "Roofs":
                                        construction_type = "roof"
                                    elif category == "Doors":
                                        construction_type = "door"

                                    if not construction_type:
                                        continue

                                    env_type = getattr(component, "EnvironmentType", None)
                                    epb_id = getattr(component, "EpbId", None)

                                    constr_elem = ET.SubElement(
                                        content_elem,
                                        f"{ns}Construction",
                                        {
                                            "name": self.validate_name(getattr(component, "Name", None)),
                                            "id": self.validate_id(epb_id),
                                        },
                                    )

                                    env_el = ET.SubElement(constr_elem, f"{ns}environmentType")
                                    env_el.text = self.validate_enum(env_type, "EnvironmentType")

                                    ct_el = ET.SubElement(constr_elem, f"{ns}constructionType")
                                    ct_el.text = construction_type

                                    surface = ET.SubElement(constr_elem, f"{ns}surface")
                                    surface.text = str(
                                        self.validate_double(float(getattr(component, "Area", 0.0)), "surface")
                                    )

                                    u_value = ET.SubElement(constr_elem, f"{ns}u-value")
                                    u_value.text = str(
                                        self.validate_double(float(getattr(component, "UValue", 0.0)), "u-value")
                                    )

            XMLCreator._generated_xml = root

        except Exception as ex:
            # Replace MessageBox with a raised exception; callers can catch.
            raise RuntimeError(f"Error generating XML: {ex}") from ex

    # -----------------------------
    # Validators / helpers
    # -----------------------------
    @staticmethod
    def validate_name(name: Optional[str]) -> str:
        if name is None or str(name).strip() == "":
            return "Unnamed"
        return str(name)

    def validate_id(self, id_value: Optional[str]) -> str:
        s = "" if id_value is None else str(id_value).strip()

        if s == "":
            s = "X" + uuid.uuid4().hex[:8]

        if s[0].isdigit():
            s = "X" + s

        if not re.match(r"^[A-Za-z_][A-Za-z0-9_-]*$", s):
            raise ValueError(f"Invalid ID format: {s}.")

        if s in self.stored_ids:
            s = s + "1"
        else:
            self.stored_ids.append(s)

        return s

    @staticmethod
    def validate_enum(value: Optional[str], enum_type: str) -> str:
        v = "" if value is None else str(value).strip()

        if v == "":
            if enum_type == "EnvironmentType":
                v = "outside"
            elif enum_type == "ConstructionType":
                v = "wall"
            else:
                v = "outside"

        valid_environment_types = {
            "outside",
            "heated-space",
            "unheated-space",
            "another-unit-space",
            "same-unit-space",
            "industrial-space",
            "ground",
            "cellar",
            "crawlspace",
        }

        valid_construction_types = {
            "wall",
            "window",
            "floor-ground",
            "roof",
            "door",
            "curtain-wall",
            "glass-building-blocks",
            "solar-wall",
            "dome-light",
        }

        is_valid = False
        if enum_type == "EnvironmentType":
            is_valid = v in valid_environment_types
        elif enum_type == "ConstructionType":
            is_valid = v in valid_construction_types

        if not is_valid:
            raise ValueError(f"Invalid {enum_type}: {v}")

        return v

    @staticmethod
    def validate_double(value: float, field_name: str) -> float:
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        if value == 0:
            return 0.01
        return value

    @staticmethod
    def _fmt_date_yyyy_mm_dd(d: object) -> str:
        if isinstance(d, (datetime, date)):
            return d.strftime("%Y-%m-%d")
        # Fall back: try string, else use today's date
        if d is None:
            return datetime.today().strftime("%Y-%m-%d")
        try:
            # if it's already a string like "2025-12-26", keep it
            return str(d)
        except Exception:
            return datetime.today().strftime("%Y-%m-%d")

    # -----------------------------
    # Output / save
    # -----------------------------
    @classmethod
    def display_xml(cls) -> str:
        """
        C# showed a MessageBox. Here we return the pretty-printed XML string.
        """
        if cls._generated_xml is None:
            raise RuntimeError("No XML has been generated yet.")
        return cls.to_string(pretty=True)

    @classmethod
    def to_string(cls, pretty: bool = True, omit_xml_declaration: bool = True) -> str:
        if cls._generated_xml is None:
            raise RuntimeError("No XML has been generated yet.")

        root = cls._generated_xml

        if pretty:
            cls._indent_in_place(root, level=0, indent="  ")

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=not omit_xml_declaration)
        return xml_bytes.decode("utf-8")

    def save_xml(self, file_path: str, pretty: bool = True, omit_xml_declaration: bool = True) -> None:
        """
        Saves XML to `file_path` (replaces the WinForms SaveFileDialog flow).
        """
        if XMLCreator._generated_xml is None:
            raise RuntimeError("No XML has been generated yet.")

        root = XMLCreator._generated_xml
        if pretty:
            self._indent_in_place(root, level=0, indent="  ")

        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=not omit_xml_declaration)

    @staticmethod
    def _indent_in_place(elem: ET.Element, level: int = 0, indent: str = "  ") -> None:
        """
        Minimal pretty printer for ElementTree (adds whitespace text/tail).
        """
        i = "\n" + level * indent
        if len(list(elem)):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent
            for child in elem:
                XMLCreator._indent_in_place(child, level + 1, indent)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
