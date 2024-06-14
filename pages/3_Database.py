import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
import json

# Load the service account key from Streamlit secrets
try:
    key_dict = json.loads(st.secrets["textkey"])
except KeyError:
    st.error("Service account key not found in Streamlit secrets.")
    st.stop()

# Authenticate to Firestore with the JSON account key
try:
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="electricity-dashboard")
    st.success("Successfully authenticated to Firestore.")
except Exception as e:
    st.error(f"Failed to authenticate to Firestore: {e}")
    st.stop()

# Example Firestore query
try:
    doc_ref = db.collection("your-collection").document("your-document-id")
    doc = doc_ref.get()
    if doc.exists:
        st.write("Document data:", doc.to_dict())
    else:
        st.write("No such document!")
except Exception as e:
    st.error(f"Failed to fetch document: {e}")

st.write("Hello World")