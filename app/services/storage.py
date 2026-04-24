from app.services.firebase import bucket
import uuid

def upload_file(file_path, filename, code):
    blob_name = f"{code}/{uuid.uuid4()}_{filename}"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    # hacerlo público
    blob.make_public()

    return blob.public_url