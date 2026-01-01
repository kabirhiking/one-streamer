"""
MinIO storage utilities.
"""
from minio import Minio
from minio.error import S3Error
import io
from typing import BinaryIO

from config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL
)


def ensure_bucket_exists():
    """Create bucket if it doesn't exist."""
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
    except S3Error as e:
        print(f"Error ensuring bucket exists: {e}")


def upload_file(object_name: str, file_data: BinaryIO, content_type: str = 'application/octet-stream'):
    """Upload file to MinIO."""
    try:
        ensure_bucket_exists()
        
        # Get file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Seek back to start
        
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
            file_data,
            file_size,
            content_type=content_type
        )
        
        return True
    except S3Error as e:
        print(f"Error uploading file: {e}")
        return False


def get_file_url(object_name: str, expires: int = 3600):
    """Get presigned URL for file."""
    try:
        url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
            expires=expires
        )
        return url
    except S3Error as e:
        print(f"Error getting file URL: {e}")
        return None


def delete_file(object_name: str):
    """Delete file from MinIO."""
    try:
        minio_client.remove_object(settings.MINIO_BUCKET_NAME, object_name)
        return True
    except S3Error as e:
        print(f"Error deleting file: {e}")
        return False


def list_files(prefix: str = ""):
    """List files in bucket with given prefix."""
    try:
        objects = minio_client.list_objects(
            settings.MINIO_BUCKET_NAME,
            prefix=prefix,
            recursive=True
        )
        return [obj.object_name for obj in objects]
    except S3Error as e:
        print(f"Error listing files: {e}")
        return []
