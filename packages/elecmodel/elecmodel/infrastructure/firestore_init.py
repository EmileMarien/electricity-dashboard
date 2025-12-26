from __future__ import annotations
import json
from google.oauth2 import service_account
import streamlit as st
import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials


import os, json, tempfile
import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore_client() -> firestore.Client:
    try:
        firebase_admin.get_app()
    except ValueError:
        sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        # NEW: allow JSON content directly
        sa_json_content = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON_CONTENT")

        if sa_json_content and not sa_path:
            # write to a temp file
            data = json.loads(sa_json_content)
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            json.dump(data, tmp)
            tmp.flush()
            sa_path = tmp.name

        if not sa_path:
            raise RuntimeError(
                "Missing credentials. Set GOOGLE_APPLICATION_CREDENTIALS (or FIREBASE_SERVICE_ACCOUNT_JSON) "
                "to a service account JSON file path, or set FIREBASE_SERVICE_ACCOUNT_JSON_CONTENT to the JSON text."
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
