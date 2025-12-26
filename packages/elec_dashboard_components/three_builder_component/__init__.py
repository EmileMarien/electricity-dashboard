import os
import streamlit.components.v1 as components

# When you build the frontend, it will output to: three_builder_component/frontend/dist
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# If dist exists, use the built frontend; otherwise assume dev server (Vite)
if os.path.isdir(_BUILD_DIR):
    _component = components.declare_component("three_builder", path=_BUILD_DIR)
else:
    _component = components.declare_component("three_builder", url="http://localhost:5173")


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
