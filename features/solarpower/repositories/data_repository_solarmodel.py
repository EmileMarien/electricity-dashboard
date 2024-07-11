from datetime import datetime
import pandas as pd
from google.cloud import firestore
import pytz

from solarpowermodel.solarpowermodel import SolarPowerModel
#TODO: first, add and update model to/in firestore
#TODO: think about which functions to add in state (update powerflow when setting new data, etc)

class DataRepositorySolarModel():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 
      self.collection = self.db.collection('solarmodel').document('solarmodel').collection('solarmodel')

  def add_model(self,model:SolarPowerModel):
      model_dict=model.__dict__
      self.collection.document(model.get_reference_id()).set(model_dict)
  
  def get_model(self,reference_id:str):
      model_dict=self.collection.document(reference_id).get().to_dict()
      model=SolarPowerModel()
      model.__dict__=model_dict
      return model