import os
import json
import firebase_admin

from firebase_admin import credentials, firestore, storage

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise ValueError("FIREBASE_CREDENTIALS no existe")

try:
    cred_dict = json.loads(firebase_credentials)

    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

    print("Firebase inicializado correctamente")

except Exception as e:
    print("ERROR FIREBASE:")
    print(e)
    raise e

db = firestore.client()
bucket = storage.bucket()