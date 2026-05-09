import os
import json
import tempfile
import traceback

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage


print("🔥 Iniciando Firebase...")


# =========================
# OBTENER VARIABLE DE ENTORNO
# =========================

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise Exception("❌ FIREBASE_CREDENTIALS no encontrada")


# =========================
# PARSEAR JSON
# =========================

try:
    firebase_dict = json.loads(firebase_credentials)

    print("✅ JSON parseado correctamente")
    print(type(firebase_dict))

except Exception as e:
    print("❌ ERROR PARSEANDO JSON")
    traceback.print_exc()
    raise


# =========================
# CREAR ARCHIVO TEMPORAL
# =========================

try:

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".json"
    ) as temp_file:

        json.dump(firebase_dict, temp_file)

        temp_file_path = temp_file.name

    print("✅ Archivo temporal creado")
    print(temp_file_path)

except Exception:
    print("❌ ERROR CREANDO ARCHIVO TEMPORAL")
    traceback.print_exc()
    raise


# =========================
# INICIALIZAR FIREBASE
# =========================

try:

    if not firebase_admin._apps:

        cred = credentials.Certificate(temp_file_path)

        firebase_admin.initialize_app(
            cred,
            {
                "storageBucket": "proyecto-scorm.firebasestorage.app"
            }
        )

    print("✅ Firebase inicializado")

except Exception:
    print("❌ ERROR INICIALIZANDO FIREBASE")
    traceback.print_exc()
    raise


# =========================
# CLIENTES
# =========================

try:

    db = firestore.client()

    bucket = storage.bucket()

    print("✅ Firestore y Storage conectados")

except Exception:
    print("❌ ERROR CONECTANDO FIRESTORE/STORAGE")
    traceback.print_exc()
    raise