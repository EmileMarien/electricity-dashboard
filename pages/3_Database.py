import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
import json
# Hide Streamlit's default menu and footer using custom CSS
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def load_key():
    try:
        key_dict = json.loads(st.secrets["textkey"])
        return key_dict
    except KeyError:
        st.error("Service account key not found in Streamlit secrets.")
        return None

def authenticate_to_firestore(key_dict):
    try:
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds, project="electricitydashboard")
        st.success("Successfully authenticated to Firestore.")
        return db
    except Exception as e:
        st.error(f"Failed to authenticate to Firestore: {e}")
        return None

def fetch_document(db):
    try:
        doc_ref = db.collection("meters").document("meter_test")
        doc = doc_ref.get()
        if doc.exists:
            st.write("Document data:", doc.to_dict())
        else:
            st.write("No such document!")
    except Exception as e:
        st.error(f"Failed to fetch document: {e}")


def add_meter(db, meter_id, location, status):
    try:
        meter_data = {
            "meter_id": meter_id,
            "location": location,
            "status": status
        }
        db.collection("meters").document(meter_id).set(meter_data)
        st.success(f"Meter {meter_id} added successfully!")
    except Exception as e:
        st.error(f"Failed to add meter: {e}")

def show_meters(db):
    st.subheader("Existing Meters")
    meters_ref = db.collection('meters')
    meters = meters_ref.get()
    
    # Prepare data for the table
    table_data = [["Meter ID", "Meter Name", "Location", "Status"]]  # Adding headers
    for meter in meters:
        meter_data = meter.to_dict()
        meter_name = meter_data.get('name', '')
        location = meter_data.get('location', '')
        status = meter_data.get('status', '')
        meter_id = meter_data.get('meter_id', '')
        
        table_data.append([meter_id, meter_name, location, status])
    
    # Display the table
    if len(table_data) > 1:  # Check if there are meters (excluding headers)
        st.table(table_data)
    else:
        st.write("No meters found.")

key_dict = load_key()
if key_dict:
    db = authenticate_to_firestore(key_dict)

if db:
    st.header("Fetch a Document")
    fetch_document(db)
    
    st.header("Existing Meters")
    show_meters(db)
    st.header("Add a Meter")
    with st.form("add_meter_form"):
        meter_id = st.text_input("Meter ID")
        location = st.text_input("Location")
        status = st.selectbox("Status", ["Active", "Inactive"])
        submitted = st.form_submit_button("Add Meter")

        if submitted:
            if meter_id and location and status:
                add_meter(db, meter_id, location, status)
            else:
                st.error("Please fill in all fields")