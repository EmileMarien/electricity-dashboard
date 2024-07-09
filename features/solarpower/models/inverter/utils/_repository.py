import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
#from inverter import Inverter

def from_snapshot(snapshot: DocumentSnapshot):
    data = snapshot.to_dict()
    return Inverter(**data, reference_id=snapshot.id)