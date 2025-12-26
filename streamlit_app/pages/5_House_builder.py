import json
import uuid
import streamlit as st

from components.three_builder_component import three_builder

st.set_page_config(page_title="House Builder MVP", layout="wide")

# --- Component catalog (replace with your own) ---
CATALOG = [
    {"id": "wall_1m", "label": "Wall (1m)", "shape": "box", "size": [1.0, 0.3, 0.1]},
    {"id": "floor_2m", "label": "Floor (2m)", "shape": "box", "size": [2.0, 0.05, 2.0]},
    {"id": "column", "label": "Column", "shape": "cylinder", "radius": 0.1, "height": 1.0},
]

def compute_insights(scene_state: dict):
    """Simple insights: BOM + counts + bounding extents."""
    instances = scene_state.get("instances", [])
    counts = {}
    for inst in instances:
        did = inst.get("definitionId", "unknown")
        counts[did] = counts.get(did, 0) + 1

    # crude extents
    xs, zs = [], []
    for inst in instances:
        p = inst.get("position", [0, 0, 0])
        xs.append(p[0])
        zs.append(p[2])

    extents = None
    if xs and zs:
        extents = {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_z": min(zs),
            "max_z": max(zs),
        }

    return {
        "num_instances": len(instances),
        "bom_counts": counts,
        "extents_xz": extents,
        "selected_id": scene_state.get("selectedId"),
    }

# --- Session state ---
if "insert_counter" not in st.session_state:
    st.session_state.insert_counter = 0
if "insert_def_id" not in st.session_state:
    st.session_state.insert_def_id = None
if "project_id" not in st.session_state:
    st.session_state.project_id = str(uuid.uuid4())
if "last_scene" not in st.session_state:
    st.session_state.last_scene = {"instances": [], "selectedId": None}

st.title("🏠 House Builder — Streamlit + Three.js MVP")

left, mid, right = st.columns([0.22, 0.56, 0.22], gap="large")

# --- LEFT: catalog ---
with left:
    st.subheader("Components")
    st.caption("Click **Insert** to add to the 3D scene.")
    for item in CATALOG:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.write(item["label"])
        with c2:
            if st.button("Insert", key=f"ins_{item['id']}"):
                st.session_state.insert_def_id = item["id"]
                st.session_state.insert_counter += 1

    st.divider()
    if st.button("Clear scene"):
        # send a "clear" command via counter token
        st.session_state.insert_def_id = "__CLEAR__"
        st.session_state.insert_counter += 1

# --- MIDDLE: 3D view ---
with mid:
    st.subheader("3D View")
    st.caption("Controls: drag to move on plane • click to select • press **R** to rotate 15° • mouse wheel to zoom.")

    scene_state = three_builder(
        catalog=CATALOG,
        project_id=st.session_state.project_id,
        command={
            "token": st.session_state.insert_counter,
            "type": "insert",
            "definitionId": st.session_state.insert_def_id,
        },
        height=640,
        key="three_builder",
    )

    # Persist last known state
    if isinstance(scene_state, dict) and scene_state.get("instances") is not None:
        st.session_state.last_scene = scene_state

# --- RIGHT: insights ---
with right:
    st.subheader("Insights")
    scene = st.session_state.last_scene
    insights = compute_insights(scene)

    st.metric("Placed components", insights["num_instances"])

    st.write("**BOM (counts)**")
    if insights["bom_counts"]:
        st.json(insights["bom_counts"])
    else:
        st.info("No components yet.")

    st.write("**Selected**")
    st.code(str(insights["selected_id"]))

    st.write("**Scene state**")
    st.json(scene)
