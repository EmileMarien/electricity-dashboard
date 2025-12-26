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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import uuid
import pathlib
import datetime


CatalogItem = Dict[str, Any]
SceneState = Dict[str, Any]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))




@dataclass
class Component:
    id: str
    type: str                      # e.g. "wall", "floor", "window"
    label: str = ""
    quantity: float = 1.0
    unit: str = "st"               # "st", "m2", "m", ...
    properties: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new(type: str, label: str = "", quantity: float = 1.0, unit: str = "st", properties: Optional[Dict[str, Any]] = None) -> "Component":
        return Component(
            id=str(uuid.uuid4()),
            type=type,
            label=label,
            quantity=float(quantity),
            unit=unit,
            properties=dict(properties or {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "quantity": self.quantity,
            "unit": self.unit,
            "properties": dict(self.properties),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        return cls(
            id=str(data.get("id")),
            type=str(data.get("type")),
            label=str(data.get("label", "")),
            quantity=float(data.get("quantity", 1.0)),
            unit=str(data.get("unit", "st")),
            properties=dict(data.get("properties", {}) or {}),
        )
    