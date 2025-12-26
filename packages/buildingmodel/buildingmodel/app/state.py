from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from buildingmodel.buildingmodel.models.Project.project import Project, Component
from buildingmodel.buildingmodel.models.Project.utils.output import Meetstaat, MeetstaatLine, Lastenboek, LastenboekSection, IfcExporter
from buildingmodel.buildingmodel.repositories.project import DataRepositoryProject

@dataclass
class BuildingModelApp:
    project_repo: DataRepositoryProject
    ifc_exporter: IfcExporter

    # ----------------------------
    # Project lifecycle
    # ----------------------------
    def create_project(self, reference_id: Optional[str] = None, project_name: str = "test") -> Project:
        p = Project(project_name=project_name)
        if reference_id:
            p.set_reference_id(reference_id)
        new_id = self.project_repo.add_project(p)
        # ensure we return id even if auto-generated
        p.set_reference_id(new_id)
        return p

    def load_project(self, reference_id: str) -> Project:
        return self.project_repo.get_project(reference_id)

    def save_project(self, project: Project) -> None:
        self.project_repo.update(project)

    # ----------------------------
    # Project parameters
    # ----------------------------
    def set_project_parameters(
        self,
        reference_id: str,
        *,
        building_type: Optional[str] = None,
        shape: Optional[str] = None,
        area_m2: Optional[float] = None,
        functions: Optional[List[str]] = None,
    ) -> Project:
        p = self.load_project(reference_id)
        p.set_parameters(building_type=building_type, shape=shape, area_m2=area_m2, functions=functions)
        self.save_project(p)
        return p

    # ----------------------------
    # Components
    # ----------------------------
    def add_component(self, reference_id: str, component: Component) -> Project:
        p = self.load_project(reference_id)
        p.add_component(component)
        self.save_project(p)
        return p

    def add_components(self, reference_id: str, components: List[Component]) -> Project:
        p = self.load_project(reference_id)
        for c in components:
            p.add_component(c)
        self.save_project(p)
        return p

    def set_components(self, reference_id: str, components: List[Component]) -> Project:
        """Replace all components in the project with the given list."""
        p = self.load_project(reference_id)
        p.set_components(components)
        self.save_project(p)
        return p

    def update_component(self, reference_id: str, component_id: str, updates: Dict[str, Any]) -> Project:
        """Update a specific component by ID."""
        p = self.load_project(reference_id)
        p.update_component(component_id, updates)
        self.save_project(p)
        return p

    def update_component_position(
        self, 
        reference_id: str, 
        component_id: str, 
        position: List[float],
        rotation_y: Optional[float] = None
    ) -> Project:
        """Update position and optionally rotation of a component."""
        p = self.load_project(reference_id)
        updates = {"position": position}
        if rotation_y is not None:
            updates["rotation_y"] = rotation_y
        p.update_component(component_id, {"properties": updates})
        self.save_project(p)
        return p

    def delete_component(self, reference_id: str, component_id: str) -> Project:
        """Delete a component by ID."""
        p = self.load_project(reference_id)
        p.delete_component(component_id)
        self.save_project(p)
        return p

    def get_components(self, reference_id: str) -> List[Component]:
        p = self.load_project(reference_id)
        return p.get_components()

    # ----------------------------
    # Outputs
    # ----------------------------
    def compute_meetstaat(self, reference_id: str) -> Meetstaat:
        p = self.load_project(reference_id)

        # MVP: 1 line per component
        lines = [
            MeetstaatLine(
                component_type=c.type,
                label=c.label or c.type,
                quantity=c.quantity,
                unit=c.unit,
                properties=c.properties,
            )
            for c in p.components
        ]
        return Meetstaat(lines=lines)

    def compute_lastenboek(self, reference_id: str) -> Lastenboek:
        p = self.load_project(reference_id)

        sections = [
            LastenboekSection(
                title="Project parameters",
                content=f"Bebouwing: {p.parameters.building_type}, Vorm: {p.parameters.shape}, Opp: {p.parameters.area_m2} m2, Functies: {', '.join(p.parameters.functions)}",
            ),
            LastenboekSection(
                title="Componenten",
                content="\n".join([f"- {c.label or c.type}: {c.quantity} {c.unit}" for c in p.components]) or "(geen)",
            ),
        ]
        return Lastenboek(sections=sections)

    def export_ifc(self, reference_id: str) -> Dict[str, Any]:
        p = self.load_project(reference_id)
        return self.ifc_exporter.export_project_minimal(p)
