import os
import streamlit as st
import streamlit.components.v1 as components

# When you build the frontend, it will output to: three_builder_component/frontend/dist
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# Prefer built assets by default; allow explicit dev override via env.
_use_dev = os.environ.get("THREE_BUILDER_USE_DEV", "").lower() in ("1", "true", "yes")

if not _use_dev and os.path.isdir(_BUILD_DIR):
    _component = components.declare_component("three_builder", path=_BUILD_DIR)
else:
    dev_url = os.environ.get("THREE_BUILDER_DEV_URL", "http://127.0.0.1:5173")
    try:
        _component = components.declare_component("three_builder", url=dev_url)
    except Exception as e:
        # Surface a helpful message in the app rather than failing silently.
        st.warning(
            f"Three Builder frontend not available at {dev_url}. "
            "Run 'npm run dev' or build the frontend (npm run build)."
        )
        # Fallback to a no-op that returns default values
        def _component(**kwargs):
            return kwargs.get("default", {"instances": [], "selectedId": None})


def three_builder(
    catalog: list,
    initial_instances: list = None,
    command: dict = None,
    project_id: str = None,
    height: int = 640,
    key: str = None,
):
    """
    3D Builder component for placing and moving building components.
    
    Args:
        catalog: list of component definitions with shape/size info
            [{"id": "wall", "label": "Muur", "category": "structuur", 
              "size": [3, 2.8, 0.3], "color": "#b0bec5"}, ...]
        initial_instances: list of existing instances to display
            [{"id": "abc", "definitionId": "wall", "position": [0, 1.4, 0], "rotationY": 0}, ...]
        command: {"token": int, "type": "insert"|"delete"|"clear", "definitionId": str|None}
        project_id: optional project reference for tracking
        height: component height in pixels
        key: streamlit component key
        
    Returns:
        {"instances": [...], "selectedId": str|None}
    """
    if command is None:
        command = {"token": 0, "type": "insert", "definitionId": None}
    if initial_instances is None:
        initial_instances = []
    
    return _component(
        catalog=catalog,
        initialInstances=initial_instances,
        command=command,
        projectId=project_id,
        height=height,
        key=key,
        default={"instances": initial_instances, "selectedId": None},
    )
