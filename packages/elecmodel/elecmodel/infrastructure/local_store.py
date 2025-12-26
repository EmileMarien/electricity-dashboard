# packages/elecmodel/elecmodel/infrastructure/local_store.py
from __future__ import annotations

import json
from pathlib import Path
from elecmodel.models.solarpowermodel.solarpowermodel import SolarPowerModel


class LocalJsonSolarModelRepository:
    def __init__(self, root: str = ".local_elecmodel"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, reference_id: str) -> Path:
        return self.root / f"{reference_id}.json"

    def load(self, reference_id: str) -> SolarPowerModel:
        p = self._path(reference_id)
        if not p.exists():
            m = SolarPowerModel()
            m.set_reference_id(reference_id)
            self.save(m)
            return m
        data = json.loads(p.read_text(encoding="utf-8"))
        return SolarPowerModel.from_dict(data)

    def save(self, model: SolarPowerModel) -> None:
        p = self._path(model.get_reference_id() or "default")
        p.write_text(json.dumps(model.to_dict()), encoding="utf-8")
