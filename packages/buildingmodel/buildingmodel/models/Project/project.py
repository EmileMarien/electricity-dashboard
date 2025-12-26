from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Type, TypeVar, Any, Dict
import json

from buildingmodel.buildingmodel.models.Building.building import Building
from buildingmodel.buildingmodel.models.Commonutilities.commonutilities import CommonUtilities

# --- Project equivalent ---
@dataclass
class Project:
    project_name: str = "test"
    creation_date: datetime = field(default_factory=datetime.now)
    buildings: List[Building] = field(default_factory=list)

    # Matches GetBuildings()
    def get_buildings(self) -> List[Building]:
        return self.buildings

    # Matches AddBuilding()
    def add_building(self, building: Building) -> None:
        self.buildings.append(building)

    # Matches CleanHierarchy()
    def clean_hierarchy(self) -> None:
        # IMPORTANT: don't remove while iterating the same list
        self.buildings = [b for b in self.buildings if not b.clean_hierarchy()]

    # Matches Serialize()
    def serialize(self) -> str:
        return CommonUtilities.serialize_to_json(self)

    # Matches static Deserialize(string json)
    @staticmethod
    def deserialize(json_str: str) -> "Project":
        return CommonUtilities.deserialize_from_json(json_str, Project)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "creation_date": self.creation_date.isoformat(),
            "buildings": [b.to_dict() for b in self.buildings],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        creation_date = data.get("creation_date")
        if isinstance(creation_date, str):
            creation_date_dt = datetime.fromisoformat(creation_date)
