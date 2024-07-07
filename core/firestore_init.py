import json
from google.oauth2 import service_account
import streamlit as st
from google.cloud import firestore

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
