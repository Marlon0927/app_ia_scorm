import os
import json
import firebase_admin

from firebase_admin import credentials, firestore, storage

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise ValueError("FIREBASE_CREDENTIALS no encontrada")

firebase_dict = json.loads(firebase_credentials)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    "storageBucket": "proyecto-scorm.firebasestorage.app"
})

db = firestore.client()
bucket = storage.bucket()