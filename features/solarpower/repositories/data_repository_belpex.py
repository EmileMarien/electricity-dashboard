
from datetime import datetime
import pandas as pd
from google.cloud import firestore
import pytz
#from solarpowermodel.solarpowermodel import SolarPowerModel

class DataRepositoryBelpex():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 
      self.collection=self.db.collection('prices')
  

  @staticmethod
  def add_belpex_to_firestore(self, belpex:pd.DataFrame):
    """
    Adds the BELPEX prices to Firestore for the specified meter_id.

    Args:
        belpex (pd.DataFrame): DataFrame containing BELPEX prices.
        meter_id (str): The ID of the meter to add the prices to.
        db: Firestore client instance.

    Returns:
        str: A message indicating the number of data points added.
    """

    #latest_DateTime= get_latest_belpex_DateTime_from_firestore(db)
    data_to_add = []
    # Define the timezone for the DateTimes
    utc_plus_2 = pytz.timezone('Europe/Brussels')  # Adjust to the specific timezone name for UTC+2 if needed

    for index, row in belpex.iterrows():
        DateTime_str = row['DateTime']
        price_str = row['Price']

        # Parse DateTime (adjust according to your specific datetime format)
        DateTime_naive = datetime.strptime(DateTime_str, '%d/%m/%Y %H:%M:%S')

        # Localize the naive datetime object to UTC+2
        DateTime_utc_plus_2 = utc_plus_2.localize(DateTime_naive)

        # Convert to UTC
        DateTime_utc = DateTime_utc_plus_2.astimezone(pytz.utc)

        # Prepare the data to add
        data = {
            'DateTime': DateTime_utc,
            'Belpex': float(price_str.replace(',', '.').strip().replace('€', ''))  # Assuming price needs to be stored as a float
        }
        data_to_add.append(data)

    # Update Firestore with new datapoints
    if data_to_add:
        prices_ref = self.collection.document('belpex')
        prices_ref.update({
            'datapoints': firestore.ArrayUnion(data_to_add)
        })

    return f"Added {len(data_to_add)} new datapoints to Firestore under 'prices/belpex'"

  def get_belpex(self):
      """
      Retrieves the synthetic load profile from Firestore under 'syntheticprofiles/SLP'
      
      :return: pd.DataFrame containing the synthetic load profile with DateTimeindex and 'Load_SLP_kW' column
      """
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


