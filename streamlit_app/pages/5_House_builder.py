import json
import uuid
import requests
import streamlit as st

from packages.elec_dashboard_components.three_builder_component import three_builder
from ui.css import apply_custom_css
from ui.menu import menu_with_redirect
st.set_page_config(page_title="House Builder MVP", layout="wide")

API_BASE = st.secrets.get("ELECMODEL_API", "http://localhost:8000")

apply_custom_css()
menu_with_redirect()

def api_get(path: str):
    r = requests.get(f"{API_BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()

def api_post(path: str, payload: dict):
    r = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

st.title("House Builder (concept → components)")

# ----------------------------
# 1) Client input parameters
# ----------------------------
with st.sidebar:
    st.subheader("Input parameters")

    building_type = st.selectbox(
        "Bebouwingstype",
        ["open", "halfopen", "gesloten"],
        index=0,
        help="Belgische context: open/halfopen/gesloten bebouwing."
    )

    shape = st.selectbox(
        "Vorm",
        ["vierkant", "rechthoek", "L-vorm", "U-vorm", "H-vorm"],
        index=1,
    )

    area_m2 = st.number_input(
        "Te bouwen vloeroppervlakte (m²)",
        min_value=10.0,
        value=120.0,
        step=5.0,
    )

    functions_raw = st.text_area(
        "Functies (één per lijn)",
        value="living\nkeuken\nslaapkamer\nbadkamer",
        help="Gebruik bv. living, keuken, slaapkamer, bureau, badkamer, berging…"
    )
    functions = [x.strip() for x in functions_raw.splitlines() if x.strip()]

    generate = st.button("Genereer conceptontwerp", type="primary")

# ----------------------------
# 2) Fetch catalog from backend
# ----------------------------
try:
    catalog = api_get("/house/catalog")
except Exception as e:
    st.error(f"Kan catalog niet laden via API ({API_BASE}/house/catalog).\n\n{e}")
    st.stop()

# ----------------------------
# 3) Generate concept via backend
# ----------------------------
if "scene_state" not in st.session_state:
    st.session_state.scene_state = {"instances": [], "selectedId": None}

if generate:
    try:
        concept = api_post(
            "/house/concept",
            {
                "building_type": building_type,
                "shape": shape,
                "area_m2": float(area_m2),
                "functions": functions,
            },
        )
        st.session_state.scene_state = concept.get("scene_state") or {"instances": [], "selectedId": None}
        st.session_state.concept_report = concept
    except Exception as e:
        st.error(f"Concept genereren faalde.\n\n{e}")

# ----------------------------
# 4) 3D builder UI (pure UI)
# ----------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("3D Builder")
    scene_state = three_builder(
        catalog=catalog,
        initial_state=st.session_state.scene_state,
        height=650,
    )
    st.session_state.scene_state = scene_state

with right:
    st.subheader("Rapport")
    # Always compute insights via backend to keep frontend logic thin
    try:
        insights = api_post("/house/insights", st.session_state.scene_state)
    except Exception as e:
        insights = None
        st.error(f"Insights berekenen faalde.\n\n{e}")

    if insights:
        st.markdown("**Stuklijst (BOM) uit huidige scene**")
        st.json(insights.get("bom_counts", {}), expanded=False)

    if "concept_report" in st.session_state:
        rep = st.session_state.concept_report

        st.markdown("**Daglicht (indicatief)**")
        st.json(rep.get("daylight", {}), expanded=False)

        st.markdown("**EPB (indicatief)**")
        st.json(rep.get("epb", {}), expanded=False)

        st.markdown("**Prijscalculatie (indicatief)**")
        st.json(rep.get("pricing", {}), expanded=False)

        ifc = rep.get("ifc") or {}
        if ifc.get("ifc_file_id"):
            ifc_url = f"{API_BASE}/house/ifc/{ifc['ifc_file_id']}"
            st.markdown(f"**IFC export**: {ifc.get('filename','model.ifc')}")
            st.markdown(f"[Download IFC]({ifc_url})")

# Debug
with st.expander("Debug: scene_state JSON"):
    st.code(json.dumps(st.session_state.scene_state, indent=2), language="json")
