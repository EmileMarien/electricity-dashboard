from datetime import datetime
import pandas as pd
import pytz
import firebase_admin
from firebase_admin import credentials, firestore
#from google.cloud.firestore_v1.document import DocumentReference
#from google.cloud.firestore_v1.base_document import DocumentSnapshot

# Initialize Firebase Admin SDK
#cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
#firebase_admin.initialize_app(cred)

class DataRepositorySLP:
    def __init__(self,firestore_reference:firestore.Client):
        self.db=firestore_reference 
        self.collection = self.db.collection('core').document('syntheticprofiles').collection('SLP')



    """
    def get_stream(self):
        return self.collection.stream()

    def get_users_stream(self):
        def map_user(snapshot):
            return 
            #return User.from_snapshot(snapshot)

        return map(map_user, self.collection.stream())
    """
    def add_SLP(self, SLP: pd.DataFrame):
        """
        Adds the synthetic load profile to Firestore under 'syntheticprofiles/SLP'
        
        :param SLP: pd.DataFrame containing the synthetic load profile with DateTimeindex and 'Load_SLP_kW' column
        :return: str indicating the number of new datapoints added to Firestore
        """
        #latest_timestamp= get_latest_belpex_timestamp_from_firestore(db)
        data_to_add = []
        # Define the timezone for the timestamps
        utc_plus_2 = pytz.timezone('Europe/Brussels')  # Adjust to the specific timezone name for UTC+2 if needed

        for index, row in SLP.iterrows():
            
            timestamp= index
            price_str = row['Load_SLP_kW']
            """
            
            # Parse timestamp (adjust according to your specific datetime format)
            timestamp_naive = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')

            # Localize the naive datetime object to UTC+2
            timestamp_utc_plus_2 = utc_plus_2.localize(timestamp_naive)

            # Convert to UTC
            timestamp_utc = timestamp_utc_plus_2.astimezone(pytz.utc)
            """
            # Prepare the data to add
            data = {
                'timestamp': timestamp,
                'value': float(price_str.replace(',', '.').strip().replace('€', ''))  # Assuming price needs to be stored as a float
            }
            data_to_add.append(data)

        # Update Firestore with new datapoints
        if data_to_add:
            self.collection.update({
                'datapoints': firestore.ArrayUnion(data_to_add)
            })

        return f"Added {len(data_to_add)} new datapoints to Firestore under 'prices/belpex'"

    def get_SLP(self):
        try:
            document_snapshot = self.collection.get()
            if document_snapshot.exists:
                return document_snapshot.to_dict()
            return None  # Return None if user with given ID doesn't exist
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None


"""
class DataRepositoryUser:
    def __init__(self):
        self.collection = firestore.client().collection('account')
    
    def get_stream(self):
        return self.collection.stream()

    def get_users_stream(self):
        def map_user(snapshot):
            return User.from_snapshot(snapshot)

        return map(map_user, self.collection.stream())

    async def get_user_by_id(self, user_id: str):
        try:
            document_snapshot = await self.collection.document(user_id).get()
            if document_snapshot.exists:
                return User.from_snapshot(document_snapshot)
            return None  # Return None if user with given ID doesn't exist
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    async def add_user(self, user: User):
        doc_ref = await self.collection.add(user.to_dict())
        return doc_ref

    async def add_user_with_id(self, user: User):
        print('Tried to add')
        await self.collection.document(user.reference_id).set(user.to_dict())

    async def update_user(self, user: User):
        await self.collection.document(user.reference_id).update(user.to_dict())

    async def delete_user(self, user: User):
        await self.collection.document(user.reference_id).delete()
"""