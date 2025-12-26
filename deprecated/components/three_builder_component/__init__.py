import os
import streamlit.components.v1 as components

# When you build the frontend, it will output to: three_builder_component/frontend/dist
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# If dist exists, use the built frontend; otherwise assume dev server (Vite)
if os.path.isdir(_BUILD_DIR):
    _component = components.declare_component("three_builder", path=_BUILD_DIR)
else:
    _component = components.declare_component("three_builder", url="http://localhost:5173")

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
