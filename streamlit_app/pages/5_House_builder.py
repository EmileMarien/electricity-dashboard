import json
import uuid
import requests
import streamlit as st

from elec_dashboard_components.three_builder_component import three_builder
from ui.css import apply_custom_css
from ui.menu import menu_with_redirect

st.set_page_config(page_title="House Builder MVP", layout="wide")

API_BASE = st.secrets.get("BUILDINGMODEL_API", "http://localhost:8000/building")

apply_custom_css()
menu_with_redirect()

# ----------------------------
# Custom CSS for Component Sidebar
# ----------------------------
st.markdown("""
<style>
    /* Component sidebar container */
    .component-sidebar {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        height: 600px;
        overflow-y: auto;
    }
    
    /* Search input styling */
    .component-search {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 14px;
    }
    
    .component-search:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Category folder styling */
    .category-folder {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        font-weight: 600;
        color: #374151;
    }
    
    .category-folder:hover {
        background: #f1f5f9;
    }
    
    .category-count {
        margin-left: auto;
        background: #e5e7eb;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        color: #6b7280;
    }
    
    /* Component card styling */
    .component-card {
        display: flex;
        align-items: center;
        padding: 12px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 8px;
        margin-left: 24px;
        cursor: pointer;
        transition: all 0.2s ease;
        background: #ffffff;
    }
    
    .component-card:hover {
        border-color: #2563eb;
        background: #f0f7ff;
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
    }
    
    .component-emoji {
        font-size: 28px;
        margin-right: 12px;
        width: 40px;
        text-align: center;
    }
    
    .component-info {
        flex: 1;
    }
    
    .component-name {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 2px;
    }
    
    .component-desc {
        font-size: 12px;
        color: #6b7280;
    }
    
    .component-size {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 2px;
    }
    
    /* Results section styling */
    .results-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
    
    /* Floor selector styling */
    div[data-testid="stRadio"] > label {
        font-size: 14px;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 4px !important;
    }
    
    div[data-testid="stRadio"] > div > label {
        padding: 6px 12px !important;
        border-radius: 8px !important;
        background: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        font-size: 13px !important;
    }
    
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
    }
    
    /* Scrollbar styling */
    .component-sidebar::-webkit-scrollbar {
        width: 6px;
    }
    
    .component-sidebar::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    .component-sidebar::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    .component-sidebar::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# API helpers
# ----------------------------
def api_get(path: str):
    r = requests.get(f"{API_BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()

def api_post(path: str, payload: dict):
    r = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def api_patch(path: str, payload: dict):
    r = requests.patch(f"{API_BASE}{path}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def api_put(path: str, payload: dict):
    r = requests.put(f"{API_BASE}{path}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def api_delete(path: str):
    r = requests.delete(f"{API_BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()

# ----------------------------
# 1) Health check (non-blocking)
# ----------------------------
if "api_available" not in st.session_state:
    st.session_state.api_available = False

try:
    health = api_get("/health")
    st.session_state.api_available = health.get("ok", False)
    if not st.session_state.api_available:
        st.warning("API health check returned unexpected response.")
except Exception as e:
    st.session_state.api_available = False
    st.warning(f"⚠️ API niet bereikbaar ({API_BASE}/health). Start de server met: `uvicorn platform_service.platform_service.api.main:app --reload --port 8000`")
    with st.expander("Error details"):
        st.error(str(e))
        
# Initialize session state for input form
if "show_input_form" not in st.session_state:
    st.session_state.show_input_form = False

st.title("House Builder")

# ----------------------------
# Project laden
# ----------------------------
st.subheader("Project laden")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    load_ref_id = st.text_input("Reference ID", placeholder="project-xxx")

with col2:
    load_project = st.button("Laad project", disabled=not st.session_state.get("api_available", False))

with col3:
    if st.button("Genereer nieuw project", disabled=not st.session_state.get("api_available", False)):
        st.session_state.show_input_form = True
        st.rerun()

# Conditional input form
if st.session_state.show_input_form:
    st.subheader("Nieuwe project parameters")
    
    # Project name
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Projectnaam:")
    with col2:
        project_name = st.text_input("", value="Nieuw project", help="Geef je project een naam.", label_visibility="collapsed", key="project_name")
    
    # Building type
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Bebouwingstype:")
    with col2:
        building_type = st.selectbox("", ["open", "halfopen", "gesloten"], index=0, help="Belgische context: open/halfopen/gesloten bebouwing.", label_visibility="collapsed", key="building_type")
    
    # Shape
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Vorm:")
    with col2:
        shape = st.selectbox("", ["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"], index=1, label_visibility="collapsed", key="shape")
    
    # Area
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Vloeroppervlakte (m²):")
    with col2:
        area_m2 = st.number_input("", min_value=10.0, value=120.0, step=5.0, label_visibility="collapsed", key="area_m2")
    
    # Functions
    st.write("Functies (één per lijn):")
    functions_raw = st.text_area("", value="living\nkeuken\nslaapkamer\nbadkamer", help="Gebruik bv. living, keuken, slaapkamer, bureau, badkamer, berging…", label_visibility="collapsed", key="functions_raw")
    functions = [x.strip() for x in functions_raw.splitlines() if x.strip()]
    
    if st.button("Genereer project", type="primary"):
        try:
            # Step 1: Create project
            reference_id = f"project-{uuid.uuid4().hex[:8]}"
            create_payload = {
                "reference_id": reference_id,
                "project_name": project_name,
            }
            create_resp = api_post("/projects", create_payload)
            ref_id = create_resp.get("reference_id", reference_id)
            st.session_state.project_reference_id = ref_id

            # Step 2: Set project parameters
            param_payload = {
                "building_type": building_type,
                "shape": shape,
                "area_m2": float(area_m2),
                "functions": functions,
            }
            project = api_patch(f"/projects/{ref_id}/parameters", param_payload)
            st.session_state.project_data = project

            # Reset instances for new project
            st.session_state.instances = []
            st.session_state.command_token = 0
            st.session_state.pending_command = {"token": 0, "type": "insert", "definitionId": None}
            st.success(f"Project aangemaakt: {ref_id}")
            st.session_state.show_input_form = False
            st.rerun()

        except requests.HTTPError as e:
            st.error(f"HTTP Error during project generation: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            st.error(f"Request Error during project generation: {e}")
        except Exception as e:
            st.error(f"Unexpected error during project generation: {e}")

# ----------------------------
# 2) Component catalog with 3D properties - Expanded with emojis and descriptions
# ----------------------------
CATALOG = [
    # Wall components (4)
    {"id": "wall_standard", "label": "Standaard Muur", "category": "wall", "emoji": "🧱", "description": "Binnenmuur 30cm", "size": [3.0, 2.8, 0.3], "color": "#b0bec5"},
    {"id": "wall_exterior", "label": "Buitenmuur", "category": "wall", "emoji": "🧱", "description": "Geïsoleerde buitenmuur 40cm", "size": [3.0, 2.8, 0.4], "color": "#78909c"},
    {"id": "wall_partition", "label": "Scheidingswand", "category": "wall", "emoji": "🧱", "description": "Lichte tussenwand 10cm", "size": [3.0, 2.8, 0.1], "color": "#cfd8dc"},
    {"id": "wall_load_bearing", "label": "Dragende Muur", "category": "wall", "emoji": "🧱", "description": "Dragende muur 35cm", "size": [3.0, 2.8, 0.35], "color": "#90a4ae"},
    
    # Roof components (3)
    {"id": "roof_flat", "label": "Plat Dak", "category": "roof", "emoji": "🏠", "description": "Plat dak element", "size": [5.0, 0.3, 5.0], "color": "#455a64"},
    {"id": "roof_pitched", "label": "Hellend Dak", "category": "roof", "emoji": "🏠", "description": "Dakpannen segment", "size": [5.0, 0.4, 5.0], "color": "#d84315"},
    {"id": "roof_gutter", "label": "Dakgoot", "category": "roof", "emoji": "🏠", "description": "Aluminium dakgoot", "size": [3.0, 0.15, 0.2], "color": "#607d8b"},
    
    # Door components (4)
    {"id": "door_interior", "label": "Binnendeur", "category": "door", "emoji": "🚪", "description": "Standaard binnendeur", "size": [0.93, 2.1, 0.04], "color": "#8d6e63"},
    {"id": "door_exterior", "label": "Buitendeur", "category": "door", "emoji": "🚪", "description": "Geïsoleerde voordeur", "size": [1.0, 2.2, 0.08], "color": "#5d4037"},
    {"id": "door_sliding", "label": "Schuifdeur", "category": "door", "emoji": "🚪", "description": "Glazen schuifdeur", "size": [2.4, 2.2, 0.06], "color": "#a1887f"},
    {"id": "door_garage", "label": "Garagepoort", "category": "door", "emoji": "🚪", "description": "Sectionaalpoort", "size": [3.0, 2.4, 0.08], "color": "#6d4c41"},
    
    # Window components (3)
    {"id": "window_standard", "label": "Standaard Raam", "category": "window", "emoji": "🪟", "description": "Draaikiepraam 1.2x1.5m", "size": [1.2, 1.5, 0.1], "color": "#81d4fa"},
    {"id": "window_large", "label": "Groot Raam", "category": "window", "emoji": "🪟", "description": "Panoramisch raam 2.4x1.8m", "size": [2.4, 1.8, 0.1], "color": "#4fc3f7"},
    {"id": "window_skylight", "label": "Dakraam", "category": "window", "emoji": "🪟", "description": "VELUX dakraam", "size": [0.8, 1.2, 0.1], "color": "#29b6f6"},
    
    # Floor components (2)
    {"id": "floor_concrete", "label": "Betonvloer", "category": "floor", "emoji": "⬛", "description": "Gewapende betonplaat", "size": [4.0, 0.2, 4.0], "color": "#9e9e9e"},
    {"id": "floor_wooden", "label": "Houten Vloer", "category": "floor", "emoji": "⬛", "description": "Parketvloer", "size": [4.0, 0.15, 4.0], "color": "#8d6e63"},
]

# Category metadata with emojis
CATEGORIES = {
    "wall": {"label": "Wall", "emoji": "📁", "icon": "🧱"},
    "roof": {"label": "Roof", "emoji": "📁", "icon": "🏠"},
    "door": {"label": "Door", "emoji": "📁", "icon": "🚪"},
    "window": {"label": "Window", "emoji": "📁", "icon": "🪟"},
    "floor": {"label": "Floor", "emoji": "📁", "icon": "⬛"},
}

def get_catalog_item(type_id: str):
    for item in CATALOG:
        if item["id"] == type_id:
            return item
    return None

def get_components_by_category(search_filter: str = ""):
    """Group components by category, optionally filtered by search term."""
    grouped = {}
    for item in CATALOG:
        # Apply search filter
        if search_filter:
            search_lower = search_filter.lower()
            if (search_lower not in item["label"].lower() and 
                search_lower not in item.get("description", "").lower() and
                search_lower not in item["category"].lower()):
                continue
        
        cat = item["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)
    return grouped

def render_component_sidebar():
    """Render the component sidebar with search, categories, and items."""
    # Search input
    search_filter = st.text_input("🔍 Zoek componenten...", key="component_search", placeholder="bijv. deur, raam, muur...")
    
    # Get filtered components grouped by category
    grouped = get_components_by_category(search_filter)
    
    if not grouped:
        st.info("Geen componenten gevonden.")
        return None
    
    selected_component = None
    
    # Container with fixed height
    with st.container():
        for cat_id in ["wall", "roof", "door", "window", "floor"]:
            if cat_id not in grouped:
                continue
                
            items = grouped[cat_id]
            cat_meta = CATEGORIES.get(cat_id, {"label": cat_id, "emoji": "📁", "icon": "📦"})
            
            # Category header
            with st.expander(f"{cat_meta['emoji']} {cat_meta['label']} ({len(items)})", expanded=False):
                for item in items:
                    # Component card using columns for layout
                    col_emoji, col_info, col_btn = st.columns([0.15, 0.6, 0.25])
                    
                    with col_emoji:
                        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{item.get('emoji', '📦')}</div>", unsafe_allow_html=True)
                    
                    with col_info:
                        st.markdown(f"**{item['label']}**")
                        st.caption(f"{item.get('description', '')} | {item['size'][0]:.1f}×{item['size'][1]:.1f}×{item['size'][2]:.1f}m")
                    
                    with col_btn:
                        if st.button("➕", key=f"add_{item['id']}", help=f"Voeg {item['label']} toe"):
                            selected_component = item
    
    return selected_component

# ----------------------------
# 3) Initialize session state
# ----------------------------
if "project_reference_id" not in st.session_state:
    st.session_state.project_reference_id = None
if "project_data" not in st.session_state:
    st.session_state.project_data = None
if "instances" not in st.session_state:
    st.session_state.instances = []
if "command_token" not in st.session_state:
    st.session_state.command_token = 0
if "pending_command" not in st.session_state:
    st.session_state.pending_command = {"token": 0, "type": "insert", "definitionId": None, "floor": 0}
if "active_floor" not in st.session_state:
    st.session_state.active_floor = 0  # 0 = ground floor, None = all floors view
if "total_floors" not in st.session_state:
    st.session_state.total_floors = 3  # Default 3 floors (0, 1, 2)

def components_to_instances(components: list) -> list:
    """Convert backend components to 3D instances for the viewer."""
    instances = []
    for c in components:
        props = c.get("properties", {})
        pos = props.get("position", [0, 0, 0])
        rot = props.get("rotation_y", 0)
        floor = props.get("floor", 0)
        
        # Ensure position is a list of 3 floats
        if isinstance(pos, list) and len(pos) >= 3:
            position = [float(pos[0]), float(pos[1]), float(pos[2])]
        else:
            # Default position based on component type
            cat_item = get_catalog_item(c.get("type", "wall"))
            height = cat_item["size"][1] if cat_item else 1.0
            position = [0, height / 2, 0]
        
        instances.append({
            "id": c.get("id", str(uuid.uuid4())),
            "definitionId": c.get("type", "unknown"),
            "position": position,
            "rotationY": float(rot) if rot else 0,
            "floor": int(floor) if floor else 0,
        })
    return instances

def instances_to_components(instances: list) -> list:
    """Convert 3D instances to backend component format."""
    components = []
    for inst in instances:
        components.append({
            "id": inst.get("id"),
            "type": inst.get("definitionId", "unknown"),
            "label": inst.get("definitionId", ""),
            "quantity": 1.0,
            "unit": "st",
            "properties": {
                "position": list(inst.get("position", [0, 0, 0])),
                "rotation_y": inst.get("rotationY", 0),
                "floor": inst.get("floor", 0),
            },
        })
    return components

# ----------------------------
# 5) Load existing project
# ----------------------------
if load_project and load_ref_id:
    try:
        project = api_get(f"/projects/{load_ref_id}")
        st.session_state.project_reference_id = load_ref_id
        st.session_state.project_data = project
        
        # Convert components to instances for 3D view
        components = project.get("components", [])
        st.session_state.instances = components_to_instances(components)
        st.success(f"Project '{load_ref_id}' geladen met {len(components)} componenten!")
        st.rerun()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            st.error("Project niet gevonden.")
        else:
            st.error(f"Fout bij laden project: {e}")
    except Exception as e:
        st.error(f"Fout bij laden project: {e}")

# ----------------------------
# Project properties (when active project exists)
# ----------------------------
if st.session_state.project_reference_id and st.session_state.project_data:
    st.subheader("Project eigenschappen")
    
    # Get current parameters
    params = st.session_state.project_data.get("parameters", {})
    
    # Editable fields
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Projectnaam:")
    with col2:
        new_project_name = st.text_input("", value=st.session_state.project_data.get("project_name", ""), label_visibility="collapsed", key="edit_project_name")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Bebouwingstype:")
    with col2:
        new_building_type = st.selectbox("", ["open", "halfopen", "gesloten"], 
                                        index=["open", "halfopen", "gesloten"].index(params.get("building_type", "open")),
                                        label_visibility="collapsed", key="edit_building_type")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Vorm:")
    with col2:
        new_shape = st.selectbox("", ["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"],
                               index=["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"].index(params.get("shape", "vierkant")),
                               label_visibility="collapsed", key="edit_shape")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Vloeroppervlakte (m²):")
    with col2:
        new_area_m2 = st.number_input("", min_value=10.0, value=params.get("area_m2", 120.0), step=5.0,
                                    label_visibility="collapsed", key="edit_area_m2")
    
    st.write("Functies (één per lijn):")
    current_functions = params.get("functions", ["living", "keuken", "slaapkamer", "badkamer"])
    new_functions_raw = st.text_area("", value="\n".join(current_functions), 
                                   label_visibility="collapsed", key="edit_functions_raw")
    new_functions = [x.strip() for x in new_functions_raw.splitlines() if x.strip()]
    
    if st.button("🔄 Update project", type="secondary"):
        try:
            updated_project = api_patch(f"/projects/{st.session_state.project_reference_id}/parameters", {
                "building_type": new_building_type,
                "shape": new_shape,
                "area_m2": float(new_area_m2),
                "functions": new_functions,
            })
            # Also update project name if changed
            if new_project_name != st.session_state.project_data.get("project_name"):
                # Note: The API might not support updating project name, but we can try
                try:
                    api_patch(f"/projects/{st.session_state.project_reference_id}", {"project_name": new_project_name})
                except:
                    pass  # Ignore if not supported
                updated_project["project_name"] = new_project_name
            
            st.session_state.project_data = updated_project
            st.success("✅ Project bijgewerkt!")
            st.rerun()
        except Exception as e:
            st.error(f"Project update faalde: {e}")

# ----------------------------
# 6) 3D builder UI (only when project is active)
# ----------------------------
if st.session_state.project_reference_id:
    # Initialize scene_result to avoid NameError
    scene_result = None
    
    # Get project parameters for grid sizing
    params = st.session_state.project_data.get("parameters", {}) if st.session_state.project_data else {}
    area_m2 = params.get("area_m2", 120.0)
    shape = params.get("shape", "rechthoek")
    
    # Calculate grid dimensions based on area and shape
    import math
    if shape == "vierkant":
        grid_width = math.sqrt(area_m2)
        grid_depth = grid_width
    elif shape == "rechthoek":
        # Assume 2:1 ratio for rectangle
        grid_depth = math.sqrt(area_m2 / 2)
        grid_width = area_m2 / grid_depth
    else:
        # For L, U, H shapes, approximate with square root
        grid_width = math.sqrt(area_m2) * 1.2
        grid_depth = math.sqrt(area_m2) * 1.2
    
    # Main layout: sidebar | 3D view
    sidebar_col, builder_col = st.columns([1, 3], gap="medium")
    
    with sidebar_col:
        st.subheader("🧩 Componenten")
        
        # Render component sidebar and get selected component
        selected_component = render_component_sidebar()
        
        # If a component was selected, trigger insert command (no rerun needed - component picks it up)
        if selected_component:
            st.session_state.command_token += 1
            # Use active floor for the command, default to 0 if viewing all floors
            insert_floor = st.session_state.active_floor if st.session_state.active_floor is not None else 0
            st.session_state.pending_command = {
                "token": st.session_state.command_token,
                "type": "insert",
                "definitionId": selected_component["id"],
                "floor": insert_floor,
            }
            st.toast(f"➕ {selected_component['label']} toegevoegd aan verdieping {insert_floor}!", icon="✅")
            # Don't rerun - the 3D component will pick up the command on next render
    
    with builder_col:
        st.subheader("3D Builder")
        
        # Floor selector - horizontal row
        floor_col1, floor_col2 = st.columns([5, 1])
        with floor_col1:
            floor_options = ["🏠 Alle"] + [f"Verdieping {i}" for i in range(st.session_state.total_floors)]
            floor_selection = st.radio(
                "Verdieping",
                floor_options,
                index=0 if st.session_state.active_floor is None else st.session_state.active_floor + 1,
                horizontal=True,
                label_visibility="collapsed",
                key="floor_selector"
            )
            # Update active floor based on selection
            if floor_selection == "🏠 Alle":
                st.session_state.active_floor = None
            else:
                st.session_state.active_floor = floor_options.index(floor_selection) - 1
        with floor_col2:
            if st.button("➕ Verdieping", key="add_floor", help="Voeg een verdieping toe"):
                st.session_state.total_floors += 1
                st.toast(f"➕ Verdieping {st.session_state.total_floors - 1} toegevoegd!", icon="🏢")
        
        floor_info = "Alle verdiepingen" if st.session_state.active_floor is None else f"Verdieping {st.session_state.active_floor}"
        st.caption(f"Project: `{st.session_state.project_reference_id}` | {floor_info} | Oppervlakte: {area_m2:.0f} m² ({grid_width:.1f}m × {grid_depth:.1f}m)")
        
        # 3D Canvas with grid dimensions and floor parameters passed
        scene_result = three_builder(
            catalog=CATALOG,
            initial_instances=st.session_state.instances,
            command=st.session_state.pending_command,
            project_id=st.session_state.project_reference_id,
            height=550,
            grid_size=(grid_width, grid_depth),
            active_floor=st.session_state.active_floor,
            total_floors=st.session_state.total_floors,
            key="three_builder_main",
        )
        
        # Update instances from 3D builder result
        if scene_result and "instances" in scene_result:
            new_instances = scene_result.get("instances", [])
            # Check if instances changed
            if new_instances != st.session_state.instances:
                st.session_state.instances = new_instances
        
        # Action buttons row
        btn_cols = st.columns([1, 1, 1, 2])
        with btn_cols[0]:
            sync_clicked = st.button("💾 Opslaan", type="primary", use_container_width=True)
        with btn_cols[1]:
            if scene_result and scene_result.get("selectedId"):
                delete_clicked = st.button("🗑️ Verwijder", type="secondary", use_container_width=True)
            else:
                delete_clicked = st.button("🗑️ Verwijder", type="secondary", use_container_width=True, disabled=True)
        with btn_cols[2]:
            clear_clicked = st.button("🧹 Wis alles", type="secondary", use_container_width=True)
        
        # Handle sync to backend
        if sync_clicked and st.session_state.project_reference_id:
            try:
                components = instances_to_components(st.session_state.instances)
                project = api_put(f"/projects/{st.session_state.project_reference_id}/components", {
                    "components": components,
                })
                st.session_state.project_data = project
                st.success(f"✅ {len(components)} componenten opgeslagen!")
            except Exception as e:
                st.error(f"Opslaan faalde: {e}")
        
        # Handle delete (no rerun needed - component picks it up)
        if delete_clicked and scene_result and scene_result.get("selectedId"):
            st.session_state.command_token += 1
            st.session_state.pending_command = {
                "token": st.session_state.command_token,
                "type": "delete",
                "definitionId": None,
            }
        
        # Handle clear all (no rerun needed - component picks it up)
        if clear_clicked:
            st.session_state.command_token += 1
            st.session_state.pending_command = {
                "token": st.session_state.command_token,
                "type": "clear",
                "definitionId": None,
            }
    
    # ----------------------------
    # Results section BELOW the 3D view
    # ----------------------------
    st.divider()
    st.subheader("📊 Rapport & Statistieken")
    
    results_col1, results_col2, results_col3 = st.columns(3)
    
    with results_col1:
        st.markdown("**Scene statistieken:**")
        instance_count = len(st.session_state.instances)
        st.metric("Componenten in scene", instance_count)
        
        # Count by type
        type_counts = {}
        for inst in st.session_state.instances:
            t = inst.get("definitionId", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        if type_counts:
            st.markdown("**Stuklijst:**")
            for t, count in sorted(type_counts.items()):
                cat_item = get_catalog_item(t)
                label = cat_item["label"] if cat_item else t
                emoji = cat_item.get("emoji", "📦") if cat_item else "📦"
                st.write(f"{emoji} {label}: {count}")
    
    with results_col2:
        # Selected component info
        if scene_result and scene_result.get("selectedId"):
            sel_id = scene_result["selectedId"]
            sel_inst = next((i for i in st.session_state.instances if i.get("id") == sel_id), None)
            if sel_inst:
                st.markdown("**Geselecteerd component:**")
                cat_item = get_catalog_item(sel_inst.get("definitionId", ""))
                if cat_item:
                    st.write(f"{cat_item.get('emoji', '📦')} **{cat_item['label']}**")
                    st.caption(cat_item.get("description", ""))
                else:
                    st.write(f"Type: {sel_inst.get('definitionId')}")
                pos = sel_inst.get("position", [0, 0, 0])
                st.write(f"📍 Positie: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
                rot_deg = sel_inst.get("rotationY", 0) * 180 / 3.14159
                st.write(f"🔄 Rotatie: {rot_deg:.0f}°")
                st.write(f"🏢 Verdieping: {sel_inst.get('floor', 0)}")
                st.write(f"🔄 Rotatie: {rot_deg:.0f}°")
        else:
            st.markdown("**Geselecteerd component:**")
            st.info("Klik op een component om details te zien")
    
    with results_col3:
        # Project info
        if st.session_state.project_data:
            st.markdown("**Projectgegevens:**")
            params = st.session_state.project_data.get("parameters", {})
            st.write(f"📝 **{st.session_state.project_data.get('project_name', '-')}**")
            st.write(f"🏠 Type: {params.get('building_type', '-')}")
            st.write(f"📐 Vorm: {params.get('shape', '-')}")
            st.write(f"📏 Oppervlakte: {params.get('area_m2', 0)} m²")
            functions = params.get("functions", [])
            if functions:
                st.write(f"🏷️ Functies: {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''}")
    
    # Export and report section
    st.divider()
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    
    ref_id = st.session_state.project_reference_id
    
    with export_col1:
        if st.button("📊 Meetstaat", use_container_width=True):
            try:
                meetstaat = api_get(f"/projects/{ref_id}/meetstaat")
                st.session_state.meetstaat = meetstaat
            except Exception as e:
                st.error(f"Meetstaat ophalen faalde: {e}")
    
    with export_col2:
        if st.button("📝 Lastenboek", use_container_width=True):
            try:
                lastenboek = api_get(f"/projects/{ref_id}/lastenboek")
                st.session_state.lastenboek = lastenboek
            except Exception as e:
                st.error(f"Lastenboek ophalen faalde: {e}")
    
    with export_col3:
        if st.button("📦 Exporteer IFC", use_container_width=True):
            try:
                ifc_resp = api_post(f"/projects/{ref_id}/ifc", {})
                filename = ifc_resp.get("filename", "model.ifc")
                ifc_url = f"{API_BASE}/ifc/{filename}"
                st.session_state.ifc_export = {"filename": filename, "url": ifc_url}
            except Exception as e:
                st.error(f"IFC export faalde: {e}")
    
    # Show export results
    show_results_col1, show_results_col2 = st.columns(2)
    
    with show_results_col1:
        if "meetstaat" in st.session_state:
            with st.expander("📊 Meetstaat", expanded=True):
                lines = st.session_state.meetstaat.get("lines", [])
                if lines:
                    for line in lines:
                        st.write(f"- {line.get('label', line.get('component_type'))}: {line.get('quantity', 1)} {line.get('unit', 'st')}")
                else:
                    st.info("Geen componenten in meetstaat.")
    
    with show_results_col2:
        if "lastenboek" in st.session_state:
            with st.expander("📝 Lastenboek", expanded=True):
                sections = st.session_state.lastenboek.get("sections", [])
                for sec in sections:
                    st.markdown(f"**{sec.get('title')}**")
                    st.write(sec.get("content", ""))
        
        if "ifc_export" in st.session_state:
            with st.expander("📦 IFC Export", expanded=True):
                st.markdown(f"**Bestand:** {st.session_state.ifc_export['filename']}")
                st.markdown(f"[⬇️ Download IFC]({st.session_state.ifc_export['url']})")

else:
    st.info("Genereer eerst een project of laad een bestaand project.")
# ----------------------------
# Debug
with st.expander("🔧 Debug: scene state"):
    st.json({
        "project_id": st.session_state.project_reference_id,
        "active_floor": st.session_state.active_floor,
        "total_floors": st.session_state.total_floors,
        "instance_count": len(st.session_state.instances),
        "instances": st.session_state.instances,
        "command": st.session_state.pending_command,
    })
