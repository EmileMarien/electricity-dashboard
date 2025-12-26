from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class MeetstaatLine:
    component_type: str
    label: str
    quantity: float
    unit: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_type": self.component_type,
            "label": self.label,
            "quantity": self.quantity,
            "unit": self.unit,
            "properties": dict(self.properties),
        }

@dataclass
class Meetstaat:
    lines: List[MeetstaatLine] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"lines": [l.to_dict() for l in self.lines]}

@dataclass
class LastenboekSection:
    title: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "content": self.content}

@dataclass
class Lastenboek:
    sections: List[LastenboekSection] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"sections": [s.to_dict() for s in self.sections]}

@dataclass
class IfcExporter:
    output_dir: str = "generated_ifc"

    def _ensure_dir(self) -> pathlib.Path:
        p = pathlib.Path(self.output_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def export_project_minimal(self, project: Project) -> Dict[str, Any]:
        out_dir = self._ensure_dir()
        file_id = str(uuid.uuid4())
        filename = f"project_{project.get_reference_id() or 'noid'}_{file_id}.ifc"
        path = out_dir / filename

        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        lines = []
        lines.append("ISO-10303-21;")
        lines.append("HEADER;")
        lines.append("FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');")
        lines.append(f"FILE_NAME('{filename}','{now}',('BuildingModel'),('BuildingModel'),'BuildingModel','BuildingModel','');")
        lines.append("FILE_SCHEMA(('IFC4'));")
        lines.append("ENDSEC;")
        lines.append("DATA;")
        lines.append("#1=IFCPERSON($,$,'BuildingModel',$,$,$,$,$);")
        lines.append("#2=IFCORGANIZATION($,'BuildingModel',$,$,$);")
        lines.append("#3=IFCPERSONANDORGANIZATION(#1,#2,$);")
        lines.append("#4=IFCAPPLICATION(#2,'0.1','BuildingModel','BM');")
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

        # Put each component as IfcProxy (MVP)
        next_id = 100
        proxy_ids = []

        for comp in project.components:
            prx_id = next_id
            next_id += 1
            label = (comp.label or comp.type).replace("'", "")
            lines.append(f"#{prx_id}=IFCPROXY('{comp.id}',#5,'{label}',$,$,$,$,$);")
            proxy_ids.append(f"#{prx_id}")

        if proxy_ids:
            lines.append(f"#{next_id}=IFCRELCONTAINEDINSPATIALSTRUCTURE('RC1',#5,$,$,({','.join(proxy_ids)}),#60);")
            next_id += 1

        lines.append("ENDSEC;")
        lines.append("END-ISO-10303-21;")

        path.write_text("\n".join(lines), encoding="utf-8")
        return {"ifc_file_id": file_id, "filename": filename, "path": str(path)}