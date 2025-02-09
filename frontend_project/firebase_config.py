import firebase_admin
from firebase_admin import credentials, firestore, auth

# Path to your serviceAccountKey.json
cred = credentials.Certificate("serviceAccountKey.json")  # Adjust if in a subfolder
firebase_admin.initialize_app(cred)

# Firestore Database
db = firestore.client()
