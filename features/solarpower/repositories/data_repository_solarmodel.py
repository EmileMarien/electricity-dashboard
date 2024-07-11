from datetime import datetime
import pandas as pd
from google.cloud import firestore
import pytz
#TODO: first, add and update model to/in firestore
#TODO: think about which functions to add in state (update powerflow when setting new data, etc)

class DataRepositorySolarModel():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 