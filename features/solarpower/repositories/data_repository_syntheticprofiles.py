import firebase_admin
from firebase_admin import credentials, firestore
#from google.cloud.firestore_v1.document import DocumentReference
#from google.cloud.firestore_v1.base_document import DocumentSnapshot

# Initialize Firebase Admin SDK
#cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
#firebase_admin.initialize_app(cred)

class DataRepositorySLP:
    def __init__(self):
        self.collection = firestore.client().collection('core').collection('SLP')
    
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