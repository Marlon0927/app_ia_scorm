from app.services.firebase import bucket
import uuid

def upload_file(file_path, filename, code, course_id):
    # 🔥 MISMO ARCHIVO SIEMPRE
    blob_name = f"{code}/{course_id}.zip"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    blob.make_public()

    return blob.public_url