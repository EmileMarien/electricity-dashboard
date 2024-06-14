import streamlit as st
from google.cloud import firestore

# Authenticate to Firestore with the JSON account key.
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="electricity-dashboard")

# Create a reference to the Google post.
doc_ref = db.collection("meters").document("meter_test")

# Then get the data at that reference.
doc = doc_ref.get()

# Let's see what we got!
#st.write("The id is: ", doc.id)
#st.write("The contents are: ", doc.to_dict())
st.write("Hello World")