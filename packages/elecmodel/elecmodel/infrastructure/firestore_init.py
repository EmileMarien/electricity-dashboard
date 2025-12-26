from __future__ import annotations
import json
from google.oauth2 import service_account
import streamlit as st
import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials


def get_firestore_client() -> firestore.Client: #TODO: remove?
    """
    Creates a Firestore client.

    Supports two common setups:
    1) GOOGLE_APPLICATION_CREDENTIALS points to a service-account json file
    2) FIREBASE_SERVICE_ACCOUNT_JSON points to a service-account json file
    """
    # If firebase_admin is already initialized, we can just return firestore client
    try:
        firebase_admin.get_app()
    except ValueError:
        # Not initialized yet
        sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not sa_path:
            raise RuntimeError(
                "Missing credentials. Set GOOGLE_APPLICATION_CREDENTIALS (or FIREBASE_SERVICE_ACCOUNT_JSON) "
                "to the path of your service account JSON."
            )
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)

    return firestore.Client()

def load_key_OLD():
    try:
        key_dict = json.loads(st.secrets["textkey"])
        return key_dict
    except KeyError:
        st.error("Service account key not found in Streamlit secrets.")
        return None

def authenticate_to_firestore_OLD(key_dict): #TODO: remove?
    try:
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds, project="electricitydashboard")
        #st.success("Successfully authenticated to Firestore.")
        return db
    except Exception as e:
        st.error(f"Failed to authenticate to Firestore: {e}")
        return None
