# packages/buildingmodel/buildingmodel/api/schemas.py

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal


# =============================================================================
# Project-centric API schemas (NEW)
# =============================================================================

BuildingType = Literal["open", "halfopen", "gesloten"]
BuildingShape = Literal["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"]


class CreateProjectRequest(BaseModel):
    # If omitted, backend generates an id
    reference_id: Optional[str] = None
    project_name: Optional[str] = "test"


class CreateProjectResponse(BaseModel):
    reference_id: str


class UpdateProjectParametersRequest(BaseModel):
    building_type: Optional[BuildingType] = None
    shape: Optional[BuildingShape] = None
    area_m2: Optional[float] = None
    functions: Optional[List[str]] = None


class ProjectParametersResponse(BaseModel):
    building_type: BuildingType
    shape: BuildingShape
    area_m2: float
    functions: List[str]


class ComponentPayload(BaseModel):
    # payload used in requests (single + batch)
    type: str
    label: Optional[str] = ""
    quantity: Optional[float] = 1.0
    unit: Optional[str] = "st"
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AddComponentRequest(ComponentPayload):
    pass


class AddComponentsRequest(BaseModel):
    components: List[ComponentPayload] = Field(default_factory=list)


class ComponentResponse(BaseModel):
    id: str
    type: str
    label: str
    quantity: float
    unit: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    reference_id: Optional[str] = None
    project_name: str
    creation_date: str  # ISO string (Project.to_dict uses isoformat)
    parameters: ProjectParametersResponse
    buildings: List[Any] = Field(default_factory=list)
    components: List[ComponentResponse] = Field(default_factory=list)


# ---- Meetstaat / Lastenboek responses ----

class MeetstaatLineResponse(BaseModel):
    component_type: str
    label: str
    quantity: float
    unit: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class MeetstaatResponse(BaseModel):
    lines: List[MeetstaatLineResponse] = Field(default_factory=list)


class LastenboekSectionResponse(BaseModel):
    title: str
    content: str


class LastenboekResponse(BaseModel):
    sections: List[LastenboekSectionResponse] = Field(default_factory=list)


class IfcExportResponse(BaseModel):
    ifc_file_id: str
    filename: str
    path: str


# =============================================================================
# Legacy schemas (KEEP for now if still used elsewhere)
# =============================================================================

class CreateModelRequest(BaseModel):
    reference_id: str


class ChangeComponentsRequest(BaseModel):
    # keep flexible for now; adapt to what app.change_components expects
    components: Dict[str, Any] = {}


class HouseCatalogItem(BaseModel):
    id: str
    label: str
    category: str
    width: float
    height: float
    depth: float
    color: Optional[str] = None


class HouseSceneState(BaseModel):
    instances: List[Dict[str, Any]] = []
    selectedId: Optional[str] = None


class HouseInsightsResponse(BaseModel):
    num_instances: int
    bom_counts: Dict[str, int]
    extents_xz: Dict[str, float]
    selected_id: Optional[str] = None
