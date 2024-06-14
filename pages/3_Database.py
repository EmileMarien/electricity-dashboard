import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
import json

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
        db = firestore.Client(credentials=creds, project="ElectricityDashboard")
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

key_dict = load_key()
if key_dict:
    db = authenticate_to_firestore(key_dict)
    if db:
        fetch_document(db)