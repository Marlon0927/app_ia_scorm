import os
import json
import firebase_admin

from firebase_admin import credentials, firestore, storage

# ======================================
# RENDER -> variable de entorno
# LOCAL -> archivo json
# ======================================

firebase_json = os.getenv("FIREBASE_CREDENTIALS")

if firebase_json:

    # ===== PRODUCCIÓN / RENDER =====
    firebase_dict = json.loads(firebase_json)

    firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)

else:

    # ===== LOCAL =====
    cred = credentials.Certificate(
        "app/proyecto-scorm-firebase-adminsdk-fbsvc-2fc2d9fb11.json"
    )

# evitar inicialización duplicada
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

db = firestore.client()

bucket = storage.bucket()