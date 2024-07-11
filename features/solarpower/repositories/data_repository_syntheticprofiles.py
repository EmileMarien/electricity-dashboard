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
        """
        data_to_add = []

        for index, row in SLP.iterrows():
            if index.minute == 0:  # Only add data for full hours
                timestamp = index
                # Prepare the data to add
                data = {
                    'DateTime': timestamp,
                    'Load_kW': row['Load_kW']
                }
                data_to_add.append(data)
                """
        # Only add data for full hours
        assert SLP is not None, "SLP is empty"
        #self.collection.document('SLP_2022').set(SLP.to_dict())
        self.collection.document('SLP_2022').set({'datapoints': 123})
        return None
        
        """
        # Update Firestore with new datapoints in chunks
        if data_to_add:
            chunk_size = 10000  # Maximum number of elements per chunk
            for i in range(0, len(data_to_add), chunk_size):
                chunk = data_to_add[i:i + chunk_size]
                # Reference a specific document, e.g., 'SLP_2022_chunk_{i // chunk_size}'
                doc_ref = self.collection.document(f'SLP_2022') 
                doc_ref.set({
                    'datapoints': firestore.ArrayUnion(chunk)
                }, merge=True)
        """


        return f"Added {len(data_to_add)} new datapoints to Firestore under 'syntheticprofiles/SLP'"


    def get_SLP(self):
        """
        Retrieves the synthetic load profile from Firestore under 'syntheticprofiles/SLP'
        
        :return: pd.DataFrame containing the synthetic load profile with DateTimeindex and 'Load_SLP_kW' column
        """
        slp_dict = self.collection.document('SLP').get().to_dict()
        return pd.DataFrame.from_dict(slp_dict)
        """
        # Reference the document
        doc_ref = self.collection.document('SLP_2022')
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict().get('datapoints', [])
            # Create a DataFrame from the data
            df = pd.DataFrame(data)
            # Ensure that the 'timestamp' is the index and it is in DateTime format
            if 'timestamp' in df.columns:
                df['DateTime'] = pd.to_datetime(df['timestamp'])
                df.set_index('DateTime', inplace=True)
            return df
        else:
            return ValueError(f"Document '{doc_ref.id}' does not exist in Firestore")"""


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