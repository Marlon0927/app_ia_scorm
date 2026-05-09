import os
import json
import firebase_admin

from firebase_admin import credentials, firestore, storage

db = None
bucket = None

try:
    # =========================
    # RENDER → variable entorno
    # =========================
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

    if firebase_credentials:
        print("✅ Usando credenciales desde variable entorno")

        cred_dict = json.loads(firebase_credentials)

        cred = credentials.Certificate(cred_dict)

    else:
        # =========================
        # LOCAL → archivo json
        # =========================
        print("✅ Usando archivo local de Firebase")

        cred = credentials.Certificate(
            "app/proyecto-scorm-firebase-adminsdk-fbsvc-2fc2d9fb11.json"
        )

    firebase_admin.initialize_app(cred, {
        "storageBucket": "proyecto-scorm.firebasestorage.app"
    })

    db = firestore.client()
    bucket = storage.bucket()

    print("✅ Firebase inicializado correctamente")

except Exception as e:
    print(f"❌ Error Firebase: {e}")
    
print("VARIABLE:", firebase_credentials)