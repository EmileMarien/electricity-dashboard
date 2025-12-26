from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import uuid


def generate_new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Building:
    name: str
    id: str = field(default_factory=generate_new_id)
    protected_volumes: List[ProtectedVolume] = field(default_factory=list)

    def get_protected_volumes(self) -> List[ProtectedVolume]:
        return self.protected_volumes

    def add_protected_volume(self, pv: ProtectedVolume) -> None:
        self.protected_volumes.append(pv)

    def remove_protected_volume(self, pv: ProtectedVolume) -> None:
        self.protected_volumes.remove(pv)

    def clean_hierarchy(self) -> bool:
        """
        Calls clean_hierarchy() on each ProtectedVolume.
        If a protected volume returns True, it is removed.
        Returns True if there are no protected volumes left.
        """
        # Don't mutate list while iterating; rebuild instead
        kept: List[ProtectedVolume] = []
        for pv in self.protected_volumes:
            should_remove = pv.clean_hierarchy()
            if not should_remove:
                kept.append(pv)
        self.protected_volumes = kept
        return len(self.protected_volumes) == 0

    def get_energetic_sectors(self) -> List[str]:
        """
        Collects energetic sectors from all protected volumes, returns unique list.
        Preserves first-seen order.
        """
        seen = set()
        result: List[str] = []
        for pv in self.protected_volumes:
            for s in pv.get_energetic_sectors():
                if s not in seen:
                    seen.add(s)
                    result.append(s)
        return result
