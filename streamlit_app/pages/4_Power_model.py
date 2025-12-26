import streamlit as st
import requests

API_BASE = st.secrets.get("ELECMODEL_API", "http://localhost:8000")

st.title("⚡ Power Model")
from ui.menu import menu_with_redirect
st.set_page_config(page_title="ELECmodel", page_icon="🌍")
from ui.css import apply_custom_css
# Hide Streamlit's default menu and footer using custom CSS
apply_custom_css()
menu_with_redirect()
ref_id = st.text_input("Model reference_id", value="demo")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Create/Load model"):
        r = requests.post(f"{API_BASE}/models", json={"reference_id": ref_id}, timeout=10)
        st.success(r.json())

with col2:
    if st.button("Update data (prices + profiles)"):
        r = requests.post(f"{API_BASE}/models/{ref_id}/update-data", timeout=30)
        st.success(r.json())

with col3:
    if st.button("Recompute"):
        r = requests.post(f"{API_BASE}/models/{ref_id}/recompute", timeout=30)
        st.success(r.json())

st.divider()

st.subheader("Change components")
battery_type = st.text_input("Battery type (optional)", value="")
inverter_type = st.text_input("Inverter type (optional)", value="")
solarpanel_type = st.text_input("Solar panel type (optional)", value="")

if st.button("Apply component changes"):
    payload = {
        "battery_type": battery_type or None,
        "inverter_type": inverter_type or None,
        "solarpanel_type": solarpanel_type or None,
    }
    r = requests.post(f"{API_BASE}/models/{ref_id}/components", json=payload, timeout=30)
    st.success(r.json())

st.divider()

st.subheader("KPIs")
if st.button("Refresh KPIs"):
    r = requests.get(f"{API_BASE}/models/{ref_id}/kpis", timeout=30)
    data = r.json()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total cost (dynamic)", f"{data['total_cost_dynamic']:.2f}")
    c2.metric("Total production (kWh)", f"{data['total_production_kwh']:.2f}")
    c3.metric("Total consumption (kWh)", f"{data['total_consumption_kwh']:.2f}")
    st.json(data)
