import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage

db = None
bucket = None

try:
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

    if not firebase_credentials:
        raise Exception("FIREBASE_CREDENTIALS no encontrada")

    cred_dict = json.loads(firebase_credentials)

    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

    db = firestore.client()
    bucket = storage.bucket()

    print("✅ Firebase inicializado correctamente")

except Exception as e:
    print(f"❌ Error Firebase: {e}")