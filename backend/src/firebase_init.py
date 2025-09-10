import firebase_admin 
from firebase_admin import credentials, firestore
import os


KEY_PATH = os.path.join(os.path.dirname(__file__), "campus-connect-firebase-admin.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)  # keep filename consistent
    firebase_admin.initialize_app(cred)

db = firestore.client()