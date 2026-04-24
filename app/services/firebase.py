import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate(
    "app/proyecto-scorm-firebase-adminsdk-fbsvc-2fc2d9fb11.json"
    )

firebase_admin.initialize_app(cred, {
    "storageBucket": "proyecto-scorm.firebasestorage.app"
})

db = firestore.client()
bucket = storage.bucket()