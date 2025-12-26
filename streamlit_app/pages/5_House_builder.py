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

st.title("Shelter Builder")

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
        st.write(f"Debug: API_BASE = {API_BASE}")
        try:
            # Step 1: Create project
            reference_id = f"project-{uuid.uuid4().hex[:8]}"
            st.write(f"Debug: Creating project with reference_id: {reference_id}")
            create_payload = {
                "reference_id": reference_id,
                "project_name": project_name,
            }
            st.write(f"Debug: Create payload: {create_payload}")
            create_resp = api_post("/projects", create_payload)
            st.write(f"Debug: Create response: {create_resp}")
            ref_id = create_resp.get("reference_id", reference_id)
            st.session_state.project_reference_id = ref_id

            # Step 2: Set project parameters
            st.write(f"Debug: Setting parameters for project {ref_id}")
            param_payload = {
                "building_type": building_type,
                "shape": shape,
                "area_m2": float(area_m2),
                "functions": functions,
            }
            st.write(f"Debug: Parameters payload: {param_payload}")
            project = api_patch(f"/projects/{ref_id}/parameters", param_payload)
            st.write(f"Debug: Parameters response: {project}")
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
            st.write(f"URL: {e.request.url}")
            st.write(f"Method: {e.request.method}")
            if hasattr(e.request, 'body') and e.request.body:
                st.write(f"Request body: {e.request.body}")
        except requests.RequestException as e:
            st.error(f"Request Error during project generation: {e}")
        except Exception as e:
            st.error(f"Unexpected error during project generation: {e}")
            import traceback
            st.write(f"Traceback: {traceback.format_exc()}")

# ----------------------------
# 2) Component catalog with 3D properties
# ----------------------------
CATALOG = [
    {"id": "wall", "label": "Muur", "category": "structuur", "size": [3.0, 2.8, 0.3], "color": "#b0bec5"},
    {"id": "floor", "label": "Vloer", "category": "structuur", "size": [4.0, 0.2, 4.0], "color": "#8d6e63"},
    {"id": "roof", "label": "Dak", "category": "structuur", "size": [5.0, 0.3, 5.0], "color": "#d84315"},
    {"id": "window", "label": "Raam", "category": "openingen", "size": [1.2, 1.5, 0.1], "color": "#81d4fa"},
    {"id": "door", "label": "Deur", "category": "openingen", "size": [1.0, 2.2, 0.1], "color": "#5d4037"},
]

def get_catalog_item(type_id: str):
    for item in CATALOG:
        if item["id"] == type_id:
            return item
    return None

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
    st.session_state.pending_command = {"token": 0, "type": "insert", "definitionId": None}

def components_to_instances(components: list) -> list:
    """Convert backend components to 3D instances for the viewer."""
    instances = []
    for c in components:
        props = c.get("properties", {})
        pos = props.get("position", [0, 0, 0])
        rot = props.get("rotation_y", 0)
        
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
    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("3D Builder")
        st.caption(f"Project: `{st.session_state.project_reference_id}`")
        
        # Component toolbar
        st.markdown("**Component toevoegen:**")
        cols = st.columns(len(CATALOG))
        for i, item in enumerate(CATALOG):
            with cols[i]:
                if st.button(f"➕ {item['label']}", key=f"add_{item['id']}", use_container_width=True):
                    st.session_state.command_token += 1
                    st.session_state.pending_command = {
                        "token": st.session_state.command_token,
                        "type": "insert",
                        "definitionId": item["id"],
                    }
    
    # 3D Canvas
    scene_result = three_builder(
        catalog=CATALOG,
        initial_instances=st.session_state.instances,
        command=st.session_state.pending_command,
        project_id=st.session_state.project_reference_id,
        height=550,
        key="three_builder_main",
    )
    
    # Update instances from 3D builder result
    if scene_result and "instances" in scene_result:
        new_instances = scene_result.get("instances", [])
        # Check if instances changed
        if new_instances != st.session_state.instances:
            st.session_state.instances = new_instances
    
    # Sync and delete buttons
    btn_cols = st.columns([1, 1, 2])
    with btn_cols[0]:
        sync_clicked = st.button("💾 Opslaan", type="primary", use_container_width=True)
    with btn_cols[1]:
        if scene_result and scene_result.get("selectedId"):
            delete_clicked = st.button("🗑️ Verwijder", type="secondary", use_container_width=True)
        else:
            delete_clicked = st.button("🗑️ Verwijder", type="secondary", use_container_width=True, disabled=True)
    
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
    
    # Handle delete
    if delete_clicked and scene_result and scene_result.get("selectedId"):
        st.session_state.command_token += 1
        st.session_state.pending_command = {
            "token": st.session_state.command_token,
            "type": "delete",
            "definitionId": None,
        }
        st.rerun()

    with right:
        st.subheader("Rapport")

        if st.session_state.project_reference_id:
            ref_id = st.session_state.project_reference_id

            # Project info
            if st.session_state.project_data:
                with st.expander("📋 Projectgegevens", expanded=False):
                    params = st.session_state.project_data.get("parameters", {})
                    st.markdown(f"""
                    - **Naam:** {st.session_state.project_data.get('project_name', '-')}
                    - **Type:** {params.get('building_type', '-')}
                    - **Vorm:** {params.get('shape', '-')}
                    - **Oppervlakte:** {params.get('area_m2', 0)} m²
                    - **Functies:** {', '.join(params.get('functions', []))}
                    """)
            
            # Current scene stats
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
                    st.write(f"- {label}: {count}")
            
            # Selected component info
            if scene_result and scene_result.get("selectedId"):
                sel_id = scene_result["selectedId"]
                sel_inst = next((i for i in st.session_state.instances if i.get("id") == sel_id), None)
                if sel_inst:
                    st.markdown("---")
                    st.markdown("**Geselecteerd component:**")
                    cat_item = get_catalog_item(sel_inst.get("definitionId", ""))
                    st.write(f"Type: {cat_item['label'] if cat_item else sel_inst.get('definitionId')}")
                    pos = sel_inst.get("position", [0, 0, 0])
                    st.write(f"Positie: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
                    rot_deg = sel_inst.get("rotationY", 0) * 180 / 3.14159
                    st.write(f"Rotatie: {rot_deg:.0f}°")

            st.divider()
            
            # Output actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Meetstaat"):
                    try:
                        meetstaat = api_get(f"/projects/{ref_id}/meetstaat")
                        st.session_state.meetstaat = meetstaat
                    except Exception as e:
                        st.error(f"Meetstaat ophalen faalde: {e}")
            
            with col2:
                if st.button("📝 Lastenboek"):
                    try:
                        lastenboek = api_get(f"/projects/{ref_id}/lastenboek")
                        st.session_state.lastenboek = lastenboek
                    except Exception as e:
                        st.error(f"Lastenboek ophalen faalde: {e}")
            
            # Show meetstaat if available
            if "meetstaat" in st.session_state:
                with st.expander("📊 Meetstaat", expanded=True):
                    lines = st.session_state.meetstaat.get("lines", [])
                    if lines:
                        for line in lines:
                            st.write(f"- {line.get('label', line.get('component_type'))}: {line.get('quantity', 1)} {line.get('unit', 'st')}")
                    else:
                        st.info("Geen componenten in meetstaat.")
            
            # Show lastenboek if available
            if "lastenboek" in st.session_state:
                with st.expander("📝 Lastenboek", expanded=True):
                    sections = st.session_state.lastenboek.get("sections", [])
                    for sec in sections:
                        st.markdown(f"**{sec.get('title')}**")
                        st.write(sec.get("content", ""))
            
            st.divider()
            
            # IFC Export
            if st.button("📦 Exporteer IFC"):
                try:
                    ifc_resp = api_post(f"/projects/{ref_id}/ifc", {})
                    filename = ifc_resp.get("filename", "model.ifc")
                    ifc_url = f"{API_BASE}/ifc/{filename}"
                    st.markdown(f"**IFC export**: {filename}")
                    st.markdown(f"[⬇️ Download IFC]({ifc_url})")
                except Exception as e:
                    st.error(f"IFC export faalde: {e}")

else:
    st.info("Genereer eerst een project of laad een bestaand project.")
# ----------------------------
# Debug
with st.expander("🔧 Debug: scene state"):
    st.json({
        "project_id": st.session_state.project_reference_id,
        "instance_count": len(st.session_state.instances),
        "instances": st.session_state.instances,
        "command": st.session_state.pending_command,
    })
