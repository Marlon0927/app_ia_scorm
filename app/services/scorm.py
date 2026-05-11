import zipfile
import os
import shutil
from app.services.firebase import bucket
import uuid
import urllib.request
from urllib.parse import urlparse
import re


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


def descargar_archivo(url, dest_path):
    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")
        return False


# =========================
# CREAR SCORM
# =========================
def crear_scorm(html_content, title="curso", pages=None, course_id=None):

    base_path = "output/scorm_package"

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    os.makedirs(base_path, exist_ok=True)

    extra_files = []
    url_mapping = {}

    print(f"\n🔍 === PROCESANDO BLOQUES ===\n")

    if pages:
        for page in pages:
            for block in page.get("blocks", []):

                block_type = block.get("type")
                content = block.get("content")

                if not content:
                    continue

                print(f"📌 {block_type}: {content[:60]}...")

                # ===== IMÁGENES =====
                if block_type == "image":
                    
                    # URL HTTPS (Cloud Storage o externa)
                    if isinstance(content, str) and content.startswith("https://"):
                        try:
                            parsed_url = urlparse(content)
                            filename = os.path.basename(parsed_url.path) or f"image_{uuid.uuid4().hex[:8]}.jpg"
                            
                            uploads_dest = os.path.join(base_path, "uploads")
                            os.makedirs(uploads_dest, exist_ok=True)
                            
                            file_path = os.path.join(uploads_dest, filename)
                            
                            if descargar_archivo(content, file_path):
                                local_path = f"uploads/{filename}"
                                extra_files.append(local_path)
                                url_mapping[content] = local_path
                                print(f"  ✅ Imagen HTTPS descargada: {filename}")
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                    
                    # RUTA LOCAL /uploads/ o uploads/
                    elif isinstance(content, str) and "uploads" in content:
                        try:
                            # Limpiar la ruta
                            local_file = content.lstrip("/").strip()
                            
                            print(f"  🔎 Buscando: {local_file}")
                            
                            if os.path.isfile(local_file):
                                filename = os.path.basename(local_file)
                                uploads_dest = os.path.join(base_path, "uploads")
                                os.makedirs(uploads_dest, exist_ok=True)
                                
                                dest_file = os.path.join(uploads_dest, filename)
                                shutil.copy2(local_file, dest_file)
                                
                                local_path = f"uploads/{filename}"
                                extra_files.append(local_path)
                                
                                # Guardar el mapeo con TODAS las variantes posibles
                                url_mapping[content] = local_path
                                url_mapping[f"/{content}"] = local_path
                                url_mapping[content.lstrip("/")] = local_path
                                
                                print(f"  ✅ Imagen local copiada: {filename}")
                            else:
                                print(f"  ❌ NO ENCONTRADO: {local_file}")
                        except Exception as e:
                            print(f"  ❌ Error: {e}")

                # ===== DOCUMENTOS =====
                if block_type == "document":
                    
                    # URL HTTPS
                    if isinstance(content, str) and content.startswith("https://"):
                        try:
                            parsed_url = urlparse(content)
                            filename = os.path.basename(parsed_url.path) or f"doc_{uuid.uuid4().hex[:8]}.pdf"
                            
                            docs_dest = os.path.join(base_path, "documents")
                            os.makedirs(docs_dest, exist_ok=True)
                            
                            file_path = os.path.join(docs_dest, filename)
                            
                            if descargar_archivo(content, file_path):
                                local_path = f"documents/{filename}"
                                extra_files.append(local_path)
                                url_mapping[content] = local_path
                                print(f"  ✅ Doc HTTPS descargado: {filename}")
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                    
                    # RUTA LOCAL
                    elif isinstance(content, str) and "documents" in content:
                        try:
                            local_file = content.lstrip("/").strip()
                            
                            print(f"  🔎 Buscando: {local_file}")
                            
                            if os.path.isfile(local_file):
                                filename = os.path.basename(local_file)
                                docs_dest = os.path.join(base_path, "documents")
                                os.makedirs(docs_dest, exist_ok=True)
                                
                                dest_file = os.path.join(docs_dest, filename)
                                shutil.copy2(local_file, dest_file)
                                
                                local_path = f"documents/{filename}"
                                extra_files.append(local_path)
                                
                                # Guardar mapeo con variantes
                                url_mapping[content] = local_path
                                url_mapping[f"/{content}"] = local_path
                                url_mapping[content.lstrip("/")] = local_path
                                
                                print(f"  ✅ Doc local copiado: {filename}")
                            else:
                                print(f"  ❌ NO ENCONTRADO: {local_file}")
                        except Exception as e:
                            print(f"  ❌ Error: {e}")

    print(f"\n📋 MAPEO FINAL ({len(url_mapping)} mappings):")
    for k, v in list(url_mapping.items())[:10]:
        print(f"  '{k}' → '{v}'")

    print(f"\n🔄 Reemplazando en HTML...")
    replaced_count = 0
    for url_original, ruta_local in url_mapping.items():
        count = html_content.count(url_original)
        if count > 0:
            html_content = html_content.replace(url_original, ruta_local)
            replaced_count += count
            print(f"  ✅ {count}x '{url_original}' → '{ruta_local}'")

    print(f"  Total reemplazados: {replaced_count}")

    # Guardar HTML
    html_path = os.path.join(base_path, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Manifest
    manifest_path = os.path.join(base_path, "imsmanifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(generar_manifest(title, extra_files))

    # ZIP
    zip_path = f"output/{course_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, base_path)
                zipf.write(full_path, arcname)

    print(f"\n✅ SCORM generado: {zip_path}")
    print(f"📦 Archivos: {extra_files}")
    return zip_path


def upload_to_firebase(zip_path, filename, code):
    blob_name = f"{code}/{uuid.uuid4()}_{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(zip_path)
    blob.make_public()
    return blob.public_url