
import pandas as pd
from google.cloud import firestore
#from solarpowermodel.solarpowermodel import SolarPowerModel

class DataRepositorySolarPower():
  def __init__(self,firestore_reference:firestore.Client):
      self.db=firestore_reference 

  

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

    #latest_timestamp= get_latest_belpex_timestamp_from_firestore(db)
    data_to_add = []
    # Define the timezone for the timestamps
    utc_plus_2 = pytz.timezone('Europe/Brussels')  # Adjust to the specific timezone name for UTC+2 if needed

    for index, row in belpex.iterrows():
        timestamp_str = row['DateTime']
        price_str = row['Price']

        # Parse timestamp (adjust according to your specific datetime format)
        timestamp_naive = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')

        # Localize the naive datetime object to UTC+2
        timestamp_utc_plus_2 = utc_plus_2.localize(timestamp_naive)

        # Convert to UTC
        timestamp_utc = timestamp_utc_plus_2.astimezone(pytz.utc)

        # Prepare the data to add
        data = {
            'timestamp': timestamp_utc,
            'value': float(price_str.replace(',', '.').strip().replace('€', ''))  # Assuming price needs to be stored as a float
        }
        data_to_add.append(data)

    # Update Firestore with new datapoints
    if data_to_add:
        prices_ref = db.collection('prices').document('belpex')
        prices_ref.update({
            'datapoints': firestore.ArrayUnion(data_to_add)
        })

    return f"Added {len(data_to_add)} new datapoints to Firestore under 'prices/belpex'"



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


