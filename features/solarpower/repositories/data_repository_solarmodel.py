from datetime import datetime
import pandas as pd
from google.cloud import firestore
import pytz

from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
#TODO: first, add and update model to/in firestore
#TODO: think about which functions to add in state (update powerflow when setting new data, etc)

class DataRepositorySolarModel():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 
      self.collection = self.db.collection('solarmodel').document('solarmodel').collection('solarmodel')

  def add_model(self,model:SolarPowerModel):
      """
      Adds a model to the firestore database
      
      Args:
      model: SolarPowerModel
      
      Returns:
      reference_id: str
      """
      if model.get_reference_id() is None:
          return self.collection.add(model.to_dict())

      self.collection.document(model.get_reference_id()).set(model.to_dict())
      return model.get_reference_id()
  
  def update_model(self,model:SolarPowerModel,fields_to_update:dict=dict()):
      """
      Updates a model in the firestore database

      Args:

      model: SolarPowerModel
      fields_to_update: dict
      """
      
      if fields_to_update=={}:
          self.collection.document(model.get_reference_id()).set(model.to_dict())
      
      else:
        self.collection.document(model.get_reference_id()).update(fields_to_update)
      return None
  
  def get_model(self,reference_id:str):
      model=SolarPowerModel.from_snapshot(self.collection.document(reference_id).get()) #If using to_dict, the reference_id is not included and nested dictionaries are not converted to objects
      return model