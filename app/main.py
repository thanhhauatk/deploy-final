import io
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, s3_service
from app.config import settings
from app.database import get_db, init_db
from app.schemas import FileRecordRead, HealthRead, ItemCreate, ItemRead, ItemUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health", response_model=HealthRead)
def health(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    return HealthRead(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
        s3_configured=s3_service.bucket_configured(),
    )


@app.get("/items", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).order_by(models.Item.id.desc()).all()


@app.post("/items", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    row = models.Item(name=payload.name, description=payload.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Item, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@app.patch("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.Item, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.name is not None:
        row.name = payload.name
    if payload.description is not None:
        row.description = payload.description
    db.commit()
    db.refresh(row)
    return row


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Item, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(row)
    db.commit()


@app.post("/files/upload", response_model=FileRecordRead, status_code=201)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not s3_service.bucket_configured():
        raise HTTPException(status_code=503, detail="S3 bucket not configured")
    key = s3_service.build_object_key(file.filename or "file")
    content = await file.read()
    buffer = io.BytesIO(content)
    s3_service.upload_fileobj(buffer, key, file.content_type)
    record = models.FileRecord(
        object_key=key,
        original_name=file.filename or "file",
        content_type=file.content_type,
        size_bytes=len(content),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/files", response_model=list[FileRecordRead])
def list_files(db: Session = Depends(get_db)):
    return db.query(models.FileRecord).order_by(models.FileRecord.id.desc()).all()


@app.get("/files/{record_id}/download")
def download_file(record_id: int, db: Session = Depends(get_db)):
    if not s3_service.bucket_configured():
        raise HTTPException(status_code=503, detail="S3 bucket not configured")
    record = db.get(models.FileRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    buffer = io.BytesIO()
    s3_service.download_fileobj(record.object_key, buffer)
    buffer.seek(0)
    media = record.content_type or "application/octet-stream"
    headers = {"Content-Disposition": f'attachment; filename="{record.original_name}"'}
    return StreamingResponse(buffer, media_type=media, headers=headers)


@app.delete("/files/{record_id}", status_code=204)
def delete_file(record_id: int, db: Session = Depends(get_db)):
    if not s3_service.bucket_configured():
        raise HTTPException(status_code=503, detail="S3 bucket not configured")
    record = db.get(models.FileRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    s3_service.delete_object(record.object_key)
    db.delete(record)
    db.commit()
