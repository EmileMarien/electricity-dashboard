import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from solarpowermodel import SolarPowerModel

def from_snapshot(snapshot: DocumentSnapshot):
    """
    Convert a Firestore snapshot to a SolarPowerModel object
    
    :param snapshot: Firestore snapshot
    :return: SolarPowerModel object
    """
    data = snapshot.to_dict()
    return SolarPowerModel(**data, reference_id=snapshot.id)