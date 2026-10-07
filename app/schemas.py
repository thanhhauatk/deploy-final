from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class FileRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    object_key: str
    original_name: str
    content_type: str | None
    size_bytes: int
    created_at: datetime


class HealthRead(BaseModel):
    status: str
    database: str
    s3_configured: bool
