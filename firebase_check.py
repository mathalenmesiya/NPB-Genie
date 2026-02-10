import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client(database_id="tickets")
    print("Firebase Admin SDK initialized.")
    
    # Try to list collections as a test
    print("Attempting to list collections in 'tickets' database...")
    collections = db.collections()
    print("Successfully connected to (default). Collections found:", [c.id for c in collections])

except Exception as e:
    print(f"Error: {e}")
