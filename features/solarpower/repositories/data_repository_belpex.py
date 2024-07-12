
from datetime import datetime
import pandas as pd
from google.cloud import firestore
import pytz
#from solarpowermodel.solarpowermodel import SolarPowerModel

class DataRepositoryBelpex():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 
      self.collection=self.db.collection('prices')
  


  def update(self, belpex:pd.DataFrame):
    data_to_add = {}

    for index, row in belpex.iterrows():
        if index.minute == 0:  # Only add data for full hours
            # Convert the timestamp to a string
            timestamp = index.strftime('%Y-%m-%d %H:%M:%S %Z')
            # Prepare the data to add
            data_to_add[timestamp] = row['Belpex']
    self.collection.document('belpex').set(data_to_add)

  def get_belpex(self):
    belpex_dict = self.collection.document('belpex').get().to_dict()
    return pd.DataFrame.from_dict(belpex_dict)
  
  """
  def get_belpex(self):
      
      Retrieves the synthetic load profile from Firestore under 'syntheticprofiles/SLP'
      
      :return: pd.DataFrame containing the synthetic load profile with DateTimeindex and 'Load_SLP_kW' column
      
      # Reference the document
      doc_ref = self.collection.document('belpex')
      doc = doc_ref.get()

      if doc.exists:
          data = doc.to_dict().get('datapoints', [])
          # Create a DataFrame from the data
          df = pd.DataFrame(data)
          # Ensure that the 'DateTime' is the index and it is in DateTime format
          if 'DateTime' in df.columns:
              df['DateTime'] = pd.to_datetime(df['DateTime'])
              df.set_index('DateTime', inplace=True)
          return df
      else:
          return ValueError(f"Document '{doc_ref.id}' does not exist in Firestore")
"""
"""
  final CollectionReference collection =
      FirebaseFirestore.instance.collection('unitType');

  Stream<QuerySnapshot> getStream() {
    return collection.snapshots();
  }

  Future<DocumentReference> addUnitType(UnitType unitType) {
    return collection.add(unitType.toJson());
  }

  updateUnitType(UnitType unitType) async {
    await collection.doc(unitType.referenceId).update(unitType.toJson());
  }

  deleteUnitType(UnitType unitType) async {
    await collection.doc(unitType.referenceId).delete();
  }

}
"""


