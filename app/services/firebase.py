import os
import json
import tempfile
import firebase_admin

from firebase_admin import credentials, firestore, storage

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise Exception("FIREBASE_CREDENTIALS no encontrada")

# Convertir string -> dict
firebase_dict = json.loads(firebase_credentials)

# Crear archivo temporal
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
    json.dump(firebase_dict, temp_file)
    temp_file_path = temp_file.name

# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(temp_file_path)

    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

db = firestore.client()
bucket = storage.bucket()

print("✅ Firebase inicializado correctamente")