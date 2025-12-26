from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# ----------------------------
# Generic building model API schemas
# ----------------------------

class CreateModelRequest(BaseModel):
    reference_id: str

class ChangeComponentsRequest(BaseModel):
    # keep flexible for now; adapt to what app.change_components expects
    components: Dict[str, Any] = {}

# ----------------------------
# House Builder (catalog/scene) schemas
# ----------------------------

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
