# --- CommonUtilities equivalent ---
import datetime
import json
from typing import Any, Type, TypeVar


T = TypeVar("T")

class CommonUtilities:

    @staticmethod
    def _json_default(o: Any) -> Any:
        """Fallback converter for json.dumps."""
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "to_dict") and callable(getattr(o, "to_dict")):
            return o.to_dict()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)

    @staticmethod
    def serialize_to_json(obj: Any) -> str:
        return json.dumps(obj, default=CommonUtilities._json_default, ensure_ascii=False, indent=2)

    @staticmethod
    def deserialize_from_json(json_str: str, cls: Type[T]) -> T:
        data = json.loads(json_str)
        # Expect cls to provide from_dict
        if hasattr(cls, "from_dict") and callable(getattr(cls, "from_dict")):
            return cls.from_dict(data)  # type: ignore
        raise TypeError(f"{cls.__name__} does not implement from_dict")
