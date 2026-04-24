import zipfile
import os
import shutil
from app.services.firebase import bucket
import uuid


# =========================
# MANIFEST
# =========================
def generar_manifest(title="Curso", extra_files=None):

    files_xml = '      <file href="index.html"/>\n'

    if extra_files:
        for file in extra_files:
            files_xml += f'      <file href="{file}"/>\n'

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="course_{uuid.uuid4()}" version="1.0"
xmlns="http://www.imsglobal.org/xsd/imscp_v1p1">

  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>{title}</title>

      <item identifier="ITEM1" identifierref="RES1">
        <title>Inicio</title>
      </item>

    </organization>
  </organizations>

  <resources>
    <resource identifier="RES1" type="webcontent" href="index.html">
{files_xml}    </resource>
  </resources>

</manifest>
"""


# =========================
# CREAR SCORM
# =========================
def crear_scorm(html_content, title="curso", pages=None):

    base_path = "output/scorm_package"

    # limpiar carpeta
    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    os.makedirs(base_path, exist_ok=True)

    extra_files = []

    # =========================
    # HTML
    # =========================
    html_path = os.path.join(base_path, "index.html")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # =========================
    # CARPETAS
    # =========================
    uploads_dest = os.path.join(base_path, "uploads")
    docs_dest = os.path.join(base_path, "documents")

    os.makedirs(uploads_dest, exist_ok=True)
    os.makedirs(docs_dest, exist_ok=True)

    # =========================
    # PROCESAR BLOQUES
    # =========================
    if pages:
        for page in pages:
            for block in page.get("blocks", []):

                block_type = block.get("type")
                content = block.get("content")

                # ignorar bloques vacíos
                if not content:
                    continue

                # ===== IMÁGENES =====
                if block_type == "image":

                    img_path = content

                    if isinstance(img_path, str) and (
                        img_path.startswith("/uploads/") or img_path.startswith("uploads/")
                    ):
                        img_path = img_path.lstrip("/")

                        if os.path.isfile(img_path):
                            filename = os.path.basename(img_path)

                            shutil.copy2(
                                img_path,
                                os.path.join(uploads_dest, filename)
                            )

                            extra_files.append(f"uploads/{filename}")

                # ===== DOCUMENTOS =====
                if block_type == "document":

                    doc_path = content

                    if isinstance(doc_path, str) and (
                        doc_path.startswith("/documents/") or doc_path.startswith("documents/")
                    ):
                        doc_path = doc_path.lstrip("/")

                        if os.path.isfile(doc_path):
                            filename = os.path.basename(doc_path)

                            shutil.copy2(
                                doc_path,
                                os.path.join(docs_dest, filename)
                            )

                            extra_files.append(f"documents/{filename}")

    # =========================
    # MANIFEST
    # =========================
    manifest_path = os.path.join(base_path, "imsmanifest.xml")

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(generar_manifest(title, extra_files))

    # =========================
    # ZIP FINAL
    # =========================
    safe_title = title.replace(" ", "_")
    zip_path = f"output/{safe_title}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)

                zipf.write(
                    full_path,
                    os.path.relpath(full_path, base_path)
                )

    return zip_path


# =========================
# SUBIR A FIREBASE
# =========================
def upload_to_firebase(zip_path, filename, code):

    blob_name = f"{code}/{uuid.uuid4()}_{filename}"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(zip_path)

    blob.make_public()

    return blob.public_url