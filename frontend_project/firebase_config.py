import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Firestore Database
db = firestore.client()
