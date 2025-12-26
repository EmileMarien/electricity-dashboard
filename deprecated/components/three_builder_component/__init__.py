import os
from pathlib import Path
import streamlit.components.v1 as components

# Built frontend output (after `npm run build`)
_BUILD_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

# Dev server URL (Vite)
_DEV_URL = os.getenv("THREE_BUILDER_DEV_URL", "http://localhost:5173")

# Explicit flag: default to RELEASE everywhere.
# Set THREE_BUILDER_DEV=1 locally when you want hot-reload dev mode.
_USE_DEV_SERVER = os.getenv("THREE_BUILDER_DEV", "0") == "1"

if _USE_DEV_SERVER:
    _component = components.declare_component("three_builder", url=_DEV_URL)
else:
    if not _BUILD_DIR.exists():
        raise RuntimeError(
            f"three_builder_component frontend build not found at {_BUILD_DIR}. "
            "Run `npm install && npm run build` in `three_builder_component/frontend` "
            "and commit the `dist/` folder for Streamlit Cloud/Render."
        )
    _component = components.declare_component("three_builder", path=str(_BUILD_DIR))


def three_builder(catalog, project_id, command, height=640, key=None):
    """
    catalog: list of component definitions
    command: {"token": int, "type": "insert", "definitionId": str|None}
    returns: {"instances": [...], "selectedId": str|None}
    """
    return _component(
        catalog=catalog,
        projectId=project_id,
        command=command,
        height=height,
        key=key,
        default={"instances": [], "selectedId": None},
    )
