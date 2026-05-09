import os
import json
import firebase_admin

from firebase_admin import credentials, firestore, storage

# =========================================
# FIREBASE LOCAL O RENDER
# =========================================

if not firebase_admin._apps:

    firebase_json = os.getenv("FIREBASE_CREDENTIALS")

    # ===== RENDER =====
    if firebase_json:

        cred_dict = json.loads(firebase_json)

        cred = credentials.Certificate(cred_dict)

    # ===== LOCAL =====
    else:

        cred = credentials.Certificate(
            "app/proyecto-scorm-firebase-adminsdk-fbsvc-2fc2d9fb11.json"
        )

    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

db = firestore.client()
bucket = storage.bucket()