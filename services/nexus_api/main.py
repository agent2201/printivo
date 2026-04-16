from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from datetime import timedelta
from io import BytesIO
import os
import time
import json
import asyncio
import datetime
import uuid
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image

app = FastAPI(title="NEXUS Printivo API Gateway")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# MinIO Setup
MINIO_URL  = os.getenv("MINIO_URL", "minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "printivo")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "printivo")
BUCKET_NAME = "nexus-uploads"

client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
if not client.bucket_exists(BUCKET_NAME):
    client.make_bucket(BUCKET_NAME)

# --- DATABASE SETUP ---
DB_URL = "postgresql://nexus_admin:nexus_password@nexus_postgres/nexus_core"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PrintJob(Base):
    __tablename__ = "print_jobs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, index=True, nullable=True)
    filename = Column(String)
    file_path = Column(String) # MinIO internal path
    customer = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    product = Column(String, nullable=True)
    status = Column(String, default="queued") # queued, printing, done, error
    width_cm = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

class RIINManager:
    def __init__(self):
        self.status = "offline"
        self.last_seen = 0

    def update_status(self):
        if time.time() - self.last_seen > 15:
            self.status = "offline"

riin = RIINManager()

class RegisterRequest(BaseModel):
    status: str
    riin_path: str
    version: str

class OrderCallback(BaseModel):
    order_id: str
    file_path: str
    customer: str
    quantity: int
    product: str

# ============ RIIN Endpoints (HTTP POLLING) ============

@app.post("/riin/register")
def riin_register(req: RegisterRequest):
    riin.status = req.status
    riin.last_seen = time.time()
    return {"status": "ok"}

@app.get("/riin/queue/next")
def riin_queue_next():
    riin.last_seen = time.time()
    riin.status = "online"
    
    db = SessionLocal()
    job = db.query(PrintJob).filter(PrintJob.status == "queued").order_by(PrintJob.created_at).first()
    if job:
        # Extract MinIO object key from file_path (remove bucket prefix)
        minio_key = job.file_path.replace(f"{BUCKET_NAME}/", "", 1) if job.file_path else job.filename
        url = client.presigned_get_object(BUCKET_NAME, minio_key, expires=timedelta(hours=1))
        res = {
            "id": job.id,
            "filename": job.filename,
            "url": url,
            "customer": job.customer,
            "order_id": job.order_id,
            "quantity": job.quantity
        }
        db.close()
        return res
    db.close()
    return {}

@app.post("/api/job/{job_id}/status/{new_status}")
def update_job_status(job_id: int, new_status: str):
    db = SessionLocal()
    job = db.query(PrintJob).filter(PrintJob.id == job_id).first()
    if job:
        job.status = new_status
        db.commit()
    db.close()
    return {"status": "ok", "new_status": new_status}

@app.get("/riin/status")
def riin_status():
    riin.update_status()
    db = SessionLocal()
    count = db.query(PrintJob).filter(PrintJob.status == "queued").count()
    db.close()
    return {"status": riin.status, "queue_size": count}

# ============ Business Logic ============
from fastapi import Form

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), quantity: int = Form(1)):
    db = SessionLocal()
    try:
        ts = int(time.time())
        content = await file.read()
        size = len(content)

        # 1. Create DB entry first to get the auto-increment ID
        new_job = PrintJob(
            filename=file.filename,
            status="queued",
            quantity=quantity
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job) # Now we have new_job.id

        # 2. Define Folder Name: YYYY-MM-DD_ID
        date_str = datetime.date.today().isoformat()
        job_folder = f"{date_str}_{new_job.id}"
        
        filename_ext = os.path.splitext(file.filename)[1].lower()
        original_name = f"original{filename_ext}"
        original_key = f"{job_folder}/{original_name}"

        # 3. Store original in MinIO
        client.put_object(
            BUCKET_NAME, original_key,
            data=BytesIO(content),
            length=size,
            content_type=file.content_type or "application/octet-stream"
        )

        # 4. Generate Thumbnail in the same folder
        thumb_key = f"{job_folder}/thumb.jpg"
        try:
            img = Image.open(BytesIO(content))
            img.thumbnail((300, 300))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=80)
            thumb_data = thumb_io.getvalue()
            
            client.put_object(
                BUCKET_NAME, thumb_key,
                data=BytesIO(thumb_data),
                length=len(thumb_data),
                content_type="image/jpeg"
            )
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
            thumb_key = None

        # 5. Update DB with final file path
        new_job.file_path = f"{BUCKET_NAME}/{original_key}"
        db.commit()

        return {
            "status": "ok",
            "key": f"{BUCKET_NAME}/{original_key}",
            "filename": file.filename,
            "thumb_key": f"{BUCKET_NAME}/{thumb_key}" if thumb_key else None,
            "job_id": new_job.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/order/callback")
async def order_callback(order: OrderCallback):
    print(f"[CALLBACK] === INCOMING ORDER CALLBACK ===")
    print(f"[CALLBACK] order_id={order.order_id}, customer={order.customer}, quantity={order.quantity}")
    print(f"[CALLBACK] file_path raw={order.file_path[:500]}")
    
    db = SessionLocal()
    
    # Parse file_path — it's JSON from WooCommerce cart metadata
    try:
        files = json.loads(order.file_path)
        print(f"[CALLBACK] Parsed {len(files)} file(s) from JSON")
    except (json.JSONDecodeError, TypeError):
        files = [{"key": order.file_path, "qty": order.quantity}]
        print(f"[CALLBACK] JSON parse failed, using raw file_path as key")
    
    updated_any = False
    for i, f in enumerate(files):
        if isinstance(f, dict):
            key = f.get("key", order.file_path)
            # Always use WooCommerce order quantity — it's what the customer chose
            file_qty = order.quantity
            print(f"[CALLBACK] File[{i}]: key={key}, using WC order.quantity={order.quantity}")
        else:
            key = str(f)
            file_qty = order.quantity
            print(f"[CALLBACK] File[{i}]: key={key} (plain string), qty={file_qty}")
        
        # Match by file_path (full MinIO key like 'nexus-uploads/2026-04-10_1/original.png')
        job = db.query(PrintJob).filter(PrintJob.file_path == key).first()
        if job:
            job.order_id = order.order_id
            job.customer = order.customer
            job.quantity = file_qty
            job.product = order.product
            
            if isinstance(f, dict):
                w = f.get('width')
                h = f.get('height')
                if w: job.width_cm = float(w)
                if h: job.height_cm = float(h)
                
            updated_any = True
            print(f"[CALLBACK] ✅ MATCHED job.id={job.id}, SET quantity={file_qty}, WxH={job.width_cm}x{job.height_cm}")
        else:
            print(f"[CALLBACK] ❌ NO MATCH for key={key}")
            # Try partial match as fallback
            all_jobs = db.query(PrintJob).filter(PrintJob.order_id == None).all()
            print(f"[CALLBACK]    Unmatched jobs in DB: {[(j.id, j.file_path) for j in all_jobs]}")

    db.commit()
    db.close()
    print(f"[CALLBACK] === DONE updated={updated_any} ===")
    return {"status": "ok", "updated": updated_any}

# ============ Dashboard API ============

from fastapi.responses import StreamingResponse

@app.get("/api/dashboard/image/{path:path}")
def stream_dashboard_image(path: str):
    """Streams image from MinIO. Handles intelligent fallbacks: thumb -> preview -> original."""
    folder = path.split('/')[0] if '/' in path else ""
    
    # Define search sequence for previews
    search_sequence = [path]
    if "thumb.jpg" in path:
        search_sequence.extend([f"{folder}/preview.jpg", f"{folder}/original.png", f"{folder}/original.jpg", f"{folder}/original.jpeg"])

    for candidate in search_sequence:
        try:
            response = client.get_object(BUCKET_NAME, candidate)
            # Efficiently detect content type
            ext = candidate.split('.')[-1].lower()
            content_type = "image/png" if ext == "png" else "image/jpeg"
            return StreamingResponse(response.stream(32*1024), media_type=content_type)
        except Exception:
            continue
            
    raise HTTPException(status_code=404, detail=f"Object not found in MinIO: {path}")

@app.get("/api/dashboard/jobs")
def get_dashboard_jobs():
    """Returns all jobs from Postgres with correct MinIO preview URLs. Supports two-way sync."""
    db = SessionLocal()
    
    # 1. Get all existing folders in MinIO
    try:
        existing_prefixes = set()
        for obj in client.list_objects(BUCKET_NAME, recursive=True):
            folder = obj.object_name.split('/')[0] if '/' in obj.object_name else obj.object_name
            existing_prefixes.add(folder)
    except Exception:
        existing_prefixes = set()

    # 2. Get current jobs from DB
    jobs = db.query(PrintJob).all()
    
    db_folders = set()
    sync_required = False

    # 3. Clean up orphans from DB
    for job in jobs:
        job_folder = None
        if job.file_path:
            parts = job.file_path.replace(f"{BUCKET_NAME}/", "", 1).split('/')
            if len(parts) >= 2:
                job_folder = parts[0]
                db_folders.add(job_folder)
        
        if job_folder and job_folder not in existing_prefixes:
            db.delete(job)
            sync_required = True

    # 4. Add missing MinIO folders to DB
    for folder in existing_prefixes:
        if folder not in db_folders:
            filename = f"recovered_{folder}.png"
            file_path = f"{BUCKET_NAME}/{folder}/original.png"
            new_job = PrintJob(
                filename=filename,
                file_path=file_path,
                status="queued"
            )
            db.add(new_job)
            sync_required = True

    if sync_required:
        db.commit()
        # Query again if we changed the DB
        jobs = db.query(PrintJob).order_by(PrintJob.created_at.desc()).limit(100).all()
    else:
        # Just sort existing and limit
        jobs.sort(key=lambda x: x.created_at.timestamp() if x.created_at else 0, reverse=True)
        jobs = jobs[:100]

    # 5. Build Final Payload
    result = []
    for job in jobs:
        job_folder = None
        if job.file_path:
            parts = job.file_path.replace(f"{BUCKET_NAME}/", "", 1).split('/')
            if len(parts) >= 2:
                job_folder = parts[0]
                
        preview_url = f"http://localhost:8000/api/dashboard/image/{job_folder}/thumb.jpg" if job_folder else ""
            
        result.append({
            "id": job.id,
            "order_id": job.order_id or "—",
            "filename": job.filename,
            "customer": job.customer or "No Customer Data",
            "quantity": job.quantity,
            "product": job.product or "—",
            "status": job.status,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S") if job.created_at else "",
            "preview_url": preview_url
        })
        
    db.close()
    return result

@app.get("/health")
def health():
    return {"status": "NEXUS Core Active", "riin": riin.status}
