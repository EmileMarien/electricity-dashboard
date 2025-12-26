"""House Builder domain & backend logic.

This module contains *all* non-UI logic for the House Builder:
- component catalog (dimensions, cost, lead-time meta)
- scene insights (BOM, extents)
- concept generation from high-level client parameters
- rough daylight requirement estimation
- rough EPB-like energy indicators (placeholder, not a certified EPB report)
- pricing + lead-time estimation
- minimal IFC export (coordination / permit handoff starter)

The Streamlit frontend should only call the FastAPI endpoints; it should not
re-implement any of this logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math
import uuid
import pathlib
import datetime


CatalogItem = Dict[str, Any]
SceneState = Dict[str, Any]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


@dataclass(frozen=True)
class HouseComponentService:
    """Component catalog + basic scene insights."""

    # You can later move this to Firestore / DB; keep the IDs stable for the UI.
    catalog: Tuple[CatalogItem, ...] = (
        {
            "id": "wall_1m",
            "label": "Wall (1m)",
            "shape": "box",
            "size": [1.0, 2.8, 0.12],  # L, H, T (meters)
            "meta": {"unit_cost_eur": 85.0, "prod_days_per_100": 2.0, "ifc_type": "IfcWall"},
        },
        {
            "id": "floor_2m",
            "label": "Floor (2m)",
            "shape": "box",
            "size": [2.0, 0.16, 2.0],  # L, T, W
            "meta": {"unit_cost_eur": 420.0, "prod_days_per_100": 3.0, "ifc_type": "IfcSlab"},
        },
        {
            "id": "column",
            "label": "Column",
            "shape": "cylinder",
            "radius": 0.12,
            "height": 2.8,
            "meta": {"unit_cost_eur": 140.0, "prod_days_per_100": 2.0, "ifc_type": "IfcColumn"},
        },
        {
            "id": "window_1m",
            "label": "Window (1m)",
            "shape": "box",
            "size": [1.0, 1.2, 0.12],
            "meta": {"unit_cost_eur": 260.0, "prod_days_per_100": 4.0, "ifc_type": "IfcWindow"},
        },
        {
            "id": "door_1m",
            "label": "Door (1m)",
            "shape": "box",
            "size": [1.0, 2.1, 0.12],
            "meta": {"unit_cost_eur": 310.0, "prod_days_per_100": 4.0, "ifc_type": "IfcDoor"},
        },
    )

    def get_catalog(self) -> List[CatalogItem]:
        return [dict(x) for x in self.catalog]

    def compute_insights(self, scene_state: SceneState) -> Dict[str, Any]:
        """Compute simple insights about a scene.

        Returns:
          - num_instances
          - bom_counts: dict[definitionId] -> count
          - extents_xz: min/max extents for X and Z based on instance positions
          - selected_id
        """
        instances = (scene_state or {}).get("instances", []) or []

        counts: Dict[str, int] = {}
        xs: List[float] = []
        zs: List[float] = []

        for inst in instances:
            did = (inst or {}).get("definitionId", "unknown")
            counts[did] = counts.get(did, 0) + 1

            p = (inst or {}).get("position", [0, 0, 0]) or [0, 0, 0]
            try:
                xs.append(float(p[0]))
                zs.append(float(p[2]))
            except Exception:
                pass

        extents: Optional[Dict[str, float]] = None
        if xs and zs:
            extents = {"min_x": min(xs), "max_x": max(xs), "min_z": min(zs), "max_z": max(zs)}

        return {
            "num_instances": len(instances),
            "bom_counts": counts,
            "extents_xz": extents,
            "selected_id": (scene_state or {}).get("selectedId"),
        }


@dataclass
class HouseDesignService:
    """Concept generation and reporting.

    Important: This is an MVP-grade generator. It produces a *starting* layout from
    a limited component kit and provides indicative calculations. It is **not**
    a replacement for an architect/EPB reporter.
    """

    components: HouseComponentService
    ifc_output_dir: str = "generated_ifc"

    def _catalog_index(self) -> Dict[str, CatalogItem]:
        return {c["id"]: c for c in self.components.get_catalog()}

    # ----------------------------
    # Inputs -> footprint geometry
    # ----------------------------
    def _footprint_dims(self, shape: str, area_m2: float) -> Dict[str, Any]:
        a = max(10.0, float(area_m2))
        shape_key = (shape or "rechthoek").strip().lower()

        if shape_key in {"vierkant", "square"}:
            side = math.sqrt(a)
            return {"kind": "rect", "w": side, "d": side}
        if shape_key in {"rechthoek", "rectangle"}:
            # gentle aspect ratio
            w = math.sqrt(a * 1.5)
            d = a / w
            return {"kind": "rect", "w": w, "d": d}
        if shape_key in {"l-vorm", "l", "lvorm"}:
            # split into two rectangles (2/3 + 1/3)
            w = math.sqrt(a * 1.4)
            d = a / w
            return {"kind": "l", "w": w, "d": d, "cut_w": 0.45 * w, "cut_d": 0.45 * d}
        if shape_key in {"u-vorm", "u", "uvorm"}:
            w = math.sqrt(a * 1.6)
            d = a / w
            courtyard_w = 0.35 * w
            courtyard_d = 0.35 * d
            return {"kind": "u", "w": w, "d": d, "courtyard_w": courtyard_w, "courtyard_d": courtyard_d}
        if shape_key in {"h-vorm", "h", "hvorm"}:
            w = math.sqrt(a * 1.8)
            d = a / w
            gap = 0.22 * w
            return {"kind": "h", "w": w, "d": d, "gap": gap}
        # fallback
        w = math.sqrt(a * 1.5)
        d = a / w
        return {"kind": "rect", "w": w, "d": d}

    def _quantize_to_module(self, value: float, module: float) -> float:
        if module <= 0:
            return value
        return max(module, round(value / module) * module)

    # ----------------------------
    # Footprint -> components
    # ----------------------------
    def _place_floor_tiles(self, w: float, d: float, tile: float = 2.0) -> List[Dict[str, Any]]:
        # tile is floor_2m size in X/Z
        nx = max(1, int(math.ceil(w / tile)))
        nz = max(1, int(math.ceil(d / tile)))
        instances = []
        for ix in range(nx):
            for iz in range(nz):
                instances.append(
                    {
                        "id": str(uuid.uuid4()),
                        "definitionId": "floor_2m",
                        "position": [ix * tile, 0.0, iz * tile],
                        "rotation": [0.0, 0.0, 0.0],
                    }
                )
        return instances

    def _place_perimeter_walls(self, w: float, d: float, segment: float = 1.0, y: float = 0.0) -> List[Dict[str, Any]]:
        # perimeter along rectangle outline in X/Z plane, using wall_1m.
        nx = max(1, int(math.ceil(w / segment)))
        nz = max(1, int(math.ceil(d / segment)))
        inst: List[Dict[str, Any]] = []

        # along +Z edge (front)
        for ix in range(nx):
            inst.append({"id": str(uuid.uuid4()), "definitionId": "wall_1m", "position": [ix * segment, y, 0.0], "rotation": [0.0, 0.0, 0.0]})
        # along -Z edge (back)
        for ix in range(nx):
            inst.append({"id": str(uuid.uuid4()), "definitionId": "wall_1m", "position": [ix * segment, y, d], "rotation": [0.0, 0.0, 0.0]})
        # along +X edge (right) rotated
        for iz in range(nz):
            inst.append({"id": str(uuid.uuid4()), "definitionId": "wall_1m", "position": [0.0, y, iz * segment], "rotation": [0.0, math.pi / 2, 0.0]})
        # along -X edge (left) rotated
        for iz in range(nz):
            inst.append({"id": str(uuid.uuid4()), "definitionId": "wall_1m", "position": [w, y, iz * segment], "rotation": [0.0, math.pi / 2, 0.0]})

        return inst

    def _apply_party_walls(self, building_type: str, shape_kind: str, w: float, d: float, instances: List[Dict[str, Any]]) -> None:
        # For Belgian context:
        # - open: all facade walls
        # - halfopen: 1 party wall (no windows) -> we keep wall, later can change meta
        # - gesloten: 2 party walls
        bt = (building_type or "open").strip().lower()
        if bt not in {"open", "halfopen", "gesloten"}:
            bt = "open"

        # MVP: mark some wall instances as 'party_wall' in meta (so window placement avoids them).
        if bt == "open":
            return

        # Determine "left" and "right" sides in this simple rect model:
        # party walls on x=0 and/or x=w
        for inst in instances:
            if inst.get("definitionId") != "wall_1m":
                continue
            x = float((inst.get("position") or [0, 0, 0])[0])
            rot_y = float((inst.get("rotation") or [0, 0, 0])[1])
            is_side_wall = abs(rot_y - (math.pi / 2)) < 1e-6
            if not is_side_wall:
                continue
            if bt == "halfopen":
                if abs(x - 0.0) < 1e-6:
                    inst["meta"] = {**(inst.get("meta") or {}), "party_wall": True}
            else:  # gesloten
                if abs(x - 0.0) < 1e-6 or abs(x - w) < 1e-6:
                    inst["meta"] = {**(inst.get("meta") or {}), "party_wall": True}

    # ----------------------------
    # Functions -> daylight needs
    # ----------------------------
    def _default_function_ratios(self) -> Dict[str, float]:
        # Window-to-floor-area ratio (WFR) indicative targets per function
        return {
            "living": 0.18,
            "keuken": 0.14,
            "kitchen": 0.14,
            "slaapkamer": 0.16,
            "bedroom": 0.16,
            "bureau": 0.20,
            "office": 0.20,
            "badkamer": 0.08,
            "bathroom": 0.08,
            "berging": 0.04,
            "storage": 0.04,
            "circulatie": 0.05,
            "circulation": 0.05,
            "default": 0.12,
        }

    def _split_area_over_functions(self, area_m2: float, functions: List[str]) -> Dict[str, float]:
        funcs = [f.strip().lower() for f in (functions or []) if str(f).strip()]
        if not funcs:
            funcs = ["living", "kitchen", "bedroom", "bathroom"]
        # Simple equal split MVP (later: program templates)
        per = float(area_m2) / float(len(funcs))
        return {f: per for f in funcs}

    def daylight_requirements(self, area_m2: float, functions: List[str]) -> Dict[str, Any]:
        ratios = self._default_function_ratios()
        area_split = self._split_area_over_functions(area_m2, functions)
        req = {}
        total_glazing = 0.0
        for f, a in area_split.items():
            wfr = ratios.get(f, ratios["default"])
            glazing = a * wfr
            req[f] = {"area_m2": a, "target_wfr": wfr, "required_glazing_m2": glazing}
            total_glazing += glazing
        return {"per_function": req, "total_required_glazing_m2": total_glazing}

    # ----------------------------
    # EPB-like indicative calc
    # ----------------------------
    def epb_indicative(self, area_m2: float, footprint: Dict[str, Any], building_type: str) -> Dict[str, Any]:
        # NOT a certified EPB. Indicative envelope indicators only.
        w = float(footprint.get("w", 10.0))
        d = float(footprint.get("d", 10.0))
        perimeter = 2.0 * (w + d)
        facade_area = perimeter * 2.8  # 1 storey
        roof_area = w * d

        # Assumed U-values (placeholder). Later: pull from component meta.
        U_wall = 0.24
        U_roof = 0.18
        U_floor = 0.22

        Ht = U_wall * facade_area + U_roof * roof_area + U_floor * roof_area  # W/K (very rough)
        # Convert to a crude annual heating demand proxy kWh/(m2·y)
        # Using degree-days style factor; purely illustrative.
        annual_kwh = (Ht * 24 * 2000) / 1000.0  # 2000 K·days equivalent
        kwh_m2y = annual_kwh / max(10.0, float(area_m2))

        bt = (building_type or "open").strip().lower()
        adj = 1.0
        if bt == "halfopen":
            adj = 0.92  # one shared wall reduces losses
        elif bt == "gesloten":
            adj = 0.84  # two shared walls
        kwh_m2y *= adj

        return {
            "note": "Indicative only (not a certified EPB report). Use an EPB-verslaggever for compliance.",
            "assumptions": {"U_wall": U_wall, "U_roof": U_roof, "U_floor": U_floor, "storeys": 1},
            "envelope": {"footprint_w_m": w, "footprint_d_m": d, "facade_area_m2": facade_area, "roof_area_m2": roof_area},
            "heat_loss_coefficient_W_per_K": Ht * adj,
            "indicative_space_heating_kwh_per_m2y": kwh_m2y,
        }

    # ----------------------------
    # Pricing + lead time
    # ----------------------------
    def _bom_from_instances(self, instances: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for inst in instances:
            did = (inst or {}).get("definitionId", "unknown")
            counts[did] = counts.get(did, 0) + 1
        return counts

    def price_and_leadtime(self, bom: Dict[str, int]) -> Dict[str, Any]:
        cat = self._catalog_index()

        subtotal = 0.0
        prod_days = 0.0

        for cid, qty in bom.items():
            item = cat.get(cid)
            if not item:
                continue
            meta = item.get("meta") or {}
            unit = float(meta.get("unit_cost_eur", 0.0))
            subtotal += unit * float(qty)

            days_per_100 = float(meta.get("prod_days_per_100", 0.0))
            prod_days += (float(qty) / 100.0) * days_per_100

        # Add fixed costs & margin (MVP)
        engineering = 0.08 * subtotal
        transport = 0.04 * subtotal
        margin = 0.15 * (subtotal + engineering + transport)
        total = subtotal + engineering + transport + margin

        # Lead time: production + QC + transport buffer
        lead_days = int(math.ceil(prod_days + 5.0))

        return {
            "currency": "EUR",
            "cost_breakdown": {
                "components_subtotal": round(subtotal, 2),
                "engineering": round(engineering, 2),
                "transport": round(transport, 2),
                "margin": round(margin, 2),
                "total": round(total, 2),
            },
            "lead_time_days": lead_days,
            "lead_time_note": "Indicative MVP estimate based on assumed production rates and buffers.",
        }

    # ----------------------------
    # IFC export (minimal)
    # ----------------------------
    def _ensure_ifc_dir(self) -> pathlib.Path:
        p = pathlib.Path(self.ifc_output_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def export_ifc_minimal(self, design_name: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write a minimal IFC4 STEP file.

        This is a *starter* coordination file: spatial structure + IfcProxy elements
        with placements, without full geometry.
        """
        out_dir = self._ensure_ifc_dir()
        file_id = str(uuid.uuid4())
        filename = f"housebuilder_{file_id}.ifc"
        path = out_dir / filename

        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Minimal IFC4 skeleton with IfcProxy elements.
        # Many BIM tools can open this, but it is not a detailed model.
        lines: List[str] = []
        lines.append("ISO-10303-21;")
        lines.append("HEADER;")
        lines.append("FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');")
        lines.append(f"FILE_NAME('{filename}','{now}',('HouseBuilder'),('HouseBuilder'),'HouseBuilder','HouseBuilder','');")
        lines.append("FILE_SCHEMA(('IFC4'));")
        lines.append("ENDSEC;")
        lines.append("DATA;")
        lines.append("#1=IFCPERSON($,$,'HouseBuilder',$,$,$,$,$);")
        lines.append("#2=IFCORGANIZATION($,'HouseBuilder',$,$,$);")
        lines.append("#3=IFCPERSONANDORGANIZATION(#1,#2,$);")
        lines.append("#4=IFCAPPLICATION(#2,'0.1','HouseBuilder','HB');")
        lines.append("#5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,$,$,0);")
        lines.append("#10=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#20,$);")
        lines.append("#20=IFCAXIS2PLACEMENT3D(#21,$,$);")
        lines.append("#21=IFCCARTESIANPOINT((0.,0.,0.));")
        lines.append("#30=IFCPROJECT('P1',#5,$,$,$,$,$,(#10),$);")
        lines.append("#40=IFCSITE('S1',#5,$,$,$,$,$,$,$,$,$,$,$,$);")
        lines.append("#50=IFCBUILDING('B1',#5,$,$,$,$,$,$,$,$,$,$);")
        lines.append("#60=IFCBUILDINGSTOREY('ST1',#5,$,$,$,$,$,$,$,$,$);")
        lines.append("#70=IFCRELAGGREGATES('RA1',#5,$,$,#30,(#40));")
        lines.append("#71=IFCRELAGGREGATES('RA2',#5,$,$,#40,(#50));")
        lines.append("#72=IFCRELAGGREGATES('RA3',#5,$,$,#50,(#60));")

        # Create placements and proxies
        next_id = 100
        rel_ids: List[str] = []
        proxy_ids: List[str] = []

        for inst in instances:
            did = (inst or {}).get("definitionId", "unknown")
            iid = (inst or {}).get("id", str(uuid.uuid4()))
            p = (inst or {}).get("position", [0, 0, 0]) or [0, 0, 0]
            x, y, z = float(p[0]), float(p[1]), float(p[2])

            pt_id = next_id
            ax_id = next_id + 1
            plc_id = next_id + 2
            prx_id = next_id + 3
            next_id += 10

            lines.append(f"#{pt_id}=IFCCARTESIANPOINT(({x:.4f},{y:.4f},{z:.4f}));")
            lines.append(f"#{ax_id}=IFCAXIS2PLACEMENT3D(#{pt_id},$,$);")
            lines.append(f"#{plc_id}=IFCLOCALPLACEMENT($,#{ax_id});")
            lines.append(f"#{prx_id}=IFCPROXY('{iid}',#5,'{did}',$,$,#{plc_id},$,$);")

            proxy_ids.append(f"#{prx_id}")

        # Containment relationship
        if proxy_ids:
            lines.append(f"#{next_id}=IFCRELCONTAINEDINSPATIALSTRUCTURE('RC1',#5,$,$,({','.join(proxy_ids)}),#60);")
            next_id += 1

        lines.append("ENDSEC;")
        lines.append("END-ISO-10303-21;")

        path.write_text("\n".join(lines), encoding="utf-8")

        return {"ifc_file_id": file_id, "filename": filename, "path": str(path)}

    # ----------------------------
    # Main orchestration endpoint
    # ----------------------------
    def generate_concept(
        self,
        building_type: str,
        shape: str,
        area_m2: float,
        functions: List[str],
        design_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        footprint = self._footprint_dims(shape=shape, area_m2=area_m2)

        # Quantize to module sizes (floor tiles 2m)
        w = self._quantize_to_module(float(footprint.get("w", 10.0)), 2.0)
        d = self._quantize_to_module(float(footprint.get("d", 10.0)), 2.0)
        footprint["w"], footprint["d"] = w, d

        # MVP only supports rect perimeter for now; other shapes use rect envelope but we tag it.
        instances: List[Dict[str, Any]] = []
        instances += self._place_floor_tiles(w=w, d=d, tile=2.0)
        instances += self._place_perimeter_walls(w=w, d=d, segment=1.0, y=0.0)
        self._apply_party_walls(building_type=building_type, shape_kind=str(footprint.get("kind")), w=w, d=d, instances=instances)

        # Daylight requirements
        daylight = self.daylight_requirements(area_m2=float(area_m2), functions=functions)

        # Window count rough: distribute glazing over 1m windows of ~1.2m2 (1.0x1.2)
        glazing_total = float(daylight["total_required_glazing_m2"])
        window_area = 1.0 * 1.2
        n_windows = int(math.ceil(glazing_total / window_area))

        # Place windows on non-party walls: simply add as BOM items (not placed precisely in MVP)
        for _ in range(n_windows):
            instances.append({"id": str(uuid.uuid4()), "definitionId": "window_1m", "position": [0.0, 1.0, 0.0], "rotation": [0.0, 0.0, 0.0], "meta": {"unplaced": True}})

        # Add one door
        instances.append({"id": str(uuid.uuid4()), "definitionId": "door_1m", "position": [0.0, 0.0, 0.0], "rotation": [0.0, 0.0, 0.0], "meta": {"unplaced": True}})

        bom = self._bom_from_instances(instances)
        pricing = self.price_and_leadtime(bom)
        epb = self.epb_indicative(area_m2=float(area_m2), footprint=footprint, building_type=building_type)

        design_name = design_name or "Concept"
        ifc_info = self.export_ifc_minimal(design_name=design_name, instances=instances)

        return {
            "inputs": {"building_type": building_type, "shape": shape, "area_m2": float(area_m2), "functions": functions},
            "footprint": footprint,
            "scene_state": {"instances": instances, "selectedId": None},
            "daylight": daylight,
            "epb": epb,
            "bom": bom,
            "pricing": pricing,
            "delivery": {"lead_time_days": pricing["lead_time_days"]},
            "ifc": {"ifc_file_id": ifc_info["ifc_file_id"], "filename": ifc_info["filename"]},
        }
