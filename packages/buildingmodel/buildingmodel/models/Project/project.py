from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import uuid

from buildingmodel.buildingmodel.models.Building.building import Building
from buildingmodel.buildingmodel.models.Commonutilities.commonutilities import CommonUtilities
from buildingmodel.buildingmodel.models.Component.component import Component

BuildingType = Literal["open", "halfopen", "gesloten"]
BuildingShape = Literal["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"]


@dataclass
class ProjectParameters:
    building_type: BuildingType = "open"
    shape: BuildingShape = "rechthoek"
    area_m2: float = 100.0
    functions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_type": self.building_type,
            "shape": self.shape,
            "area_m2": self.area_m2,
            "functions": list(self.functions),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectParameters":
        return cls(
            building_type=data.get("building_type", "open"),
            shape=data.get("shape", "rechthoek"),
            area_m2=float(data.get("area_m2", 100.0)),
            functions=list(data.get("functions", []) or []),
        )


# --- Project equivalent ---
@dataclass
class Project:
    reference_id: Optional[str] = None
    project_name: str = "test"
    creation_date: datetime = field(default_factory=datetime.now)
    parameters: ProjectParameters = field(default_factory=ProjectParameters)

    # keep your existing buildings if you still need them
    buildings: List[Any] = field(default_factory=list)

    components: List[Component] = field(default_factory=list)

    def set_reference_id(self, reference_id: str) -> None:
        self.reference_id = reference_id

    def get_reference_id(self) -> Optional[str]:
        return self.reference_id

    def set_parameters(self, *, building_type: Optional[str] = None, shape: Optional[str] = None, area_m2: Optional[float] = None, functions: Optional[List[str]] = None) -> None:
        if building_type is not None:
            self.parameters.building_type = building_type  # trust API validation
        if shape is not None:
            self.parameters.shape = shape
        if area_m2 is not None:
            self.parameters.area_m2 = float(area_m2)
        if functions is not None:
            self.parameters.functions = list(functions)

    def add_component(self, component: Component) -> None:
        self.components.append(component)

    def get_components(self) -> List[Component]:
        return list(self.components)

    def set_components(self, components: List[Component]) -> None:
        """Replace all components with the given list."""
        self.components = list(components)

    def get_component_by_id(self, component_id: str) -> Optional[Component]:
        """Find a component by its ID."""
        for c in self.components:
            if c.id == component_id:
                return c
        return None

    def update_component(self, component_id: str, updates: Dict[str, Any]) -> bool:
        """Update a component by ID. Returns True if found and updated."""
        for i, c in enumerate(self.components):
            if c.id == component_id:
                # Update properties if provided
                if "properties" in updates:
                    # Merge properties (don't replace entirely)
                    for key, value in updates["properties"].items():
                        c.properties[key] = value
                # Update other fields
                if "type" in updates:
                    c.type = updates["type"]
                if "label" in updates:
                    c.label = updates["label"]
                if "quantity" in updates:
                    c.quantity = float(updates["quantity"])
                if "unit" in updates:
                    c.unit = updates["unit"]
                return True
        return False

    def delete_component(self, component_id: str) -> bool:
        """Delete a component by ID. Returns True if found and deleted."""
        for i, c in enumerate(self.components):
            if c.id == component_id:
                del self.components[i]
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "project_name": self.project_name,
            "creation_date": self.creation_date.isoformat(),
            "parameters": self.parameters.to_dict(),
            "buildings": self.buildings,  # or serialize if you still use them
            "components": [c.to_dict() for c in self.components],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        creation_date = data.get("creation_date")
        if isinstance(creation_date, str):
            creation_date_dt = datetime.fromisoformat(creation_date)
        else:
            creation_date_dt = datetime.now()

        return cls(
            reference_id=data.get("reference_id"),
            project_name=data.get("project_name", "test"),
            creation_date=creation_date_dt,
            parameters=ProjectParameters.from_dict(data.get("parameters", {}) or {}),
            buildings=list(data.get("buildings", []) or []),
            components=[Component.from_dict(x) for x in (data.get("components", []) or [])],
        )