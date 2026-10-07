import uuid
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import settings


def _client():
    return boto3.client("s3", region_name=settings.aws_region)


def bucket_configured() -> bool:
    return bool(settings.s3_bucket_name.strip())


def build_object_key(filename: str) -> str:
    safe = filename.replace("\\", "/").split("/")[-1] or "file"
    return f"uploads/{uuid.uuid4().hex}_{safe}"


def upload_fileobj(fileobj: BinaryIO, key: str, content_type: str | None) -> None:
    if content_type:
        _client().upload_fileobj(
            fileobj,
            settings.s3_bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
        )
    else:
        _client().upload_fileobj(fileobj, settings.s3_bucket_name, key)


def download_fileobj(key: str, fileobj: BinaryIO) -> None:
    _client().download_fileobj(settings.s3_bucket_name, key, fileobj)


def delete_object(key: str) -> None:
    _client().delete_object(Bucket=settings.s3_bucket_name, Key=key)


def head_object(key: str) -> dict | None:
    try:
        return _client().head_object(Bucket=settings.s3_bucket_name, Key=key)
    except ClientError:
        return None
