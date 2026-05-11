import os
from urllib.parse import urlparse
import uuid
from datetime import datetime
from google.cloud.firestore import FieldFilter

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.schemas import Course
from app.services.html_generator import generar_html
from app.services.scorm import crear_scorm
from app.services.firebase import db, bucket
from app.services.storage import upload_file

router = APIRouter()

# Directorios locales (deben existir)
UPLOADS_DIR = "uploads"
DOCUMENTS_DIR = "documents"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# Extensiones permitidas
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt"}


# ===============================
# 🔐 AUTH (VALIDAR CÓDIGO)
# ===============================
@router.get("/auth/{code}")
def validate_code(code: str):
    doc = db.collection("codes").document(code).get()
    return {"valid": doc.exists}


# ===============================
# 🖼️ SUBIR IMAGEN
# ===============================
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {ext}. Usa: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOADS_DIR, unique_name)

    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"url": f"/uploads/{unique_name}"}
    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        raise HTTPException(status_code=500, detail="Error al subir la imagen")


# ===============================
# 📎 SUBIR DOCUMENTO
# ===============================
@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {ext}. Usa: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
        )

    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(DOCUMENTS_DIR, unique_name)

    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"url": f"/documents/{unique_name}"}
    except Exception as e:
        print(f"Error subiendo documento: {e}")
        raise HTTPException(status_code=500, detail="Error al subir el documento")


# ===============================
# 👀 PREVIEW
# ===============================
@router.post("/preview")
def preview_course(payload: dict):
    try:
        html = generar_html(payload)
        return {"html": html}
    except Exception as e:
        print(f"Error generando preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando preview: {str(e)}")


# ===============================
# 💾 GUARDAR CURSO (SIN EXPORTAR)
# ===============================
@router.post("/save")
def save_course(payload: dict):
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Falta el código de usuario")

    try:
        current_course_id = payload.get("currentCourseId")
        
        # Si ya existe un borrador, actualizar
        if current_course_id:
            doc_ref = db.collection("courses").document(current_course_id)
            doc_ref.update({
                "title": payload.get("title", "Sin título"),
                "pages": payload.get("pages", []),
                "updated_at": datetime.utcnow().isoformat()
            })
            print(f"📝 Borrador actualizado: {current_course_id}")
            return {"id": current_course_id}
        
        # Si no existe, crear nuevo borrador
        doc_ref = db.collection("courses").add({
            "code": code,
            "title": payload.get("title", "Sin título"),
            "pages": payload.get("pages", []),
            "url": None,
            "created_at": datetime.utcnow().isoformat()
        })

        print(f"✅ Nuevo borrador creado: {doc_ref[1].id}")
        return {"id": doc_ref[1].id}
    except Exception as e:
        print(f"Error guardando curso: {e}")
        raise HTTPException(status_code=500, detail=f"Error guardando: {str(e)}")


# ===============================
# ✏️ ACTUALIZAR CURSO EXISTENTE
# ===============================
@router.put("/{course_id}")
def update_course(course_id: str, payload: dict):
    doc_ref = db.collection("courses").document(course_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    try:
        doc_ref.update({
            "title": payload.get("title", "Sin título"),
            "pages": payload.get("pages", []),
            "updated_at": datetime.utcnow().isoformat()
        })
        return {"id": course_id, "status": "updated"}
    except Exception as e:
        print(f"Error actualizando curso: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando: {str(e)}")


# ===============================
# 🎯 CREAR CURSO + EXPORTAR SCORM
# ===============================
@router.post("/create")
def create_course(course: Course):

    data = course.dict()

    # 🔥 necesitas recibir course_id desde frontend
    course_id = data.get("id")

    if not course_id:
        raise HTTPException(status_code=400, detail="Falta course_id")

    doc_ref = db.collection("courses").document(course_id)

    # corregir rutas
    for page in data["pages"]:
        for block in page["blocks"]:
            if block["type"] == "image" and block.get("content"):
                if block["content"].startswith("/uploads/"):
                    block["content"] = block["content"][1:]

    html = generar_html(data)

    zip_path = crear_scorm(
        html,
        course.title,
        data["pages"],
        course_id
    )

    file_url = upload_file(
        zip_path,
        f"{course.title}.zip",
        course.code,
        course_id
    )

    # 🔥 ACTUALIZAR, NO CREAR
    doc_ref.update({
        "title": course.title,
        "pages": data["pages"],
        "url": file_url,
        "status": "completed",
        "updated_at": datetime.utcnow().isoformat()
    })

    return {
        "message": "SCORM actualizado",
        "file_url": file_url
    }



# ===============================
# 📜 HISTORIAL POR USUARIO
# ===============================
@router.get("/history/{code}")
def get_history(code: str):
    try:
        docs = db.collection("courses") \
            .where(filter=FieldFilter("code", "==", code)) \
            .stream()

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)

        return result
    except Exception as e:
        print(f"Error cargando historial: {e}")
        raise HTTPException(status_code=500, detail=f"Error cargando historial: {str(e)}")


# ===============================
# 🗑️ ELIMINAR CURSO
# ===============================
@router.delete("/{id}")
def delete_course(id: str):
    try:
        doc_ref = db.collection("courses").document(id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        data = doc.to_dict()
        file_url = data.get("url")

        # Eliminar archivo de Cloud Storage si existe
        if file_url:
            try:
                # Formato esperado:
                # https://storage.googleapis.com/BUCKET_NAME/path/to/file.zip
                parsed = urlparse(file_url)

                path_parts = parsed.path.lstrip("/").split("/", 1)
                blob_path = path_parts[1]

                blob = bucket.blob(blob_path)
                blob.delete()

                print(f"✅ Archivo eliminado de storage: {blob_path}")

            except Exception as e:
                print(f"⚠️ Error eliminando archivo de storage: {e}")

        # Eliminar documento de Firestore (siempre)
        doc_ref.delete()

        return {"status": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error eliminando curso: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando: {str(e)}")


# ===============================
# 📄 OBTENER CURSO POR ID
# ===============================
@router.get("/{course_id}")
def get_course(course_id: str):
    try:
        doc = db.collection("courses").document(course_id).get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        data = doc.to_dict()
        data["id"] = doc.id
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error obteniendo curso: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo curso: {str(e)}")