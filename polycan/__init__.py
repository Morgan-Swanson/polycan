import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.cloud.exceptions

# Use the application default credentials
cred = credentials.Certificate('secret.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
input_prompt = ""