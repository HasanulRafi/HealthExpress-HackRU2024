import firebase_admin
from firebase_admin import firestore

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
db = firestore.client()

users_ref = db.collection("users")
docs = users_ref.stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
    
def send_data_to_firebase(data):
    doc_ref = db.collection("users").document(data["phone_number"])
    doc_ref.set(data)

    





