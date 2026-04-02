from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from datetime import timedelta
from io import BytesIO
import os
import time

app = FastAPI(title="NEXUS Printivo API Gateway")

# CORS — единственный источник правды (не Nginx)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

MINIO_URL = os.getenv("MINIO_URL", "minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "printivo")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "printivo")
BUCKET_NAME = "nexus-uploads"

client = Minio(
    MINIO_URL,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False
)

if not client.bucket_exists(BUCKET_NAME):
    client.make_bucket(BUCKET_NAME)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Принимает файл от браузера и кладёт в MinIO."""
    try:
        filename = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
        content = await file.read()
        size = len(content)

        client.put_object(
            BUCKET_NAME,
            filename,
            data=BytesIO(content),
            length=size,
            content_type=file.content_type or "application/octet-stream"
        )

        return {
            "status": "ok",
            "key": f"{BUCKET_NAME}/{filename}",
            "filename": filename,
            "size": size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "NEXUS Core Active"}
