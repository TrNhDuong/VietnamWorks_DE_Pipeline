import boto3
from include.utilis.utilis import load_minio_config
from io import BytesIO
from botocore.exceptions import ClientError
from include.cleaner.df import df_manager
import pandas as pd
import os

_client = None

def create_minio_client(minio_config):
    return boto3.client(
        "s3",
        endpoint_url=minio_config["endpoint_url"],
        aws_access_key_id=minio_config["access_key"],
        aws_secret_access_key=minio_config["secret_key"],
        region_name=minio_config.get("region", "us-east-1"),
    )

def get_minio_client(minio_config):
    global _client
    if _client is None:
        _client = create_minio_client(minio_config=minio_config)
    return _client

def upload_df(s3, bucket: str, object_path: str, df: pd.DataFrame):
    # 1. Làm sạch & chuẩn hóa dữ liệu
    df = df_manager(df)
    
    # 2. Ghi dữ liệu vào RAM (Buffer)
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    
    # 3. Upload lên MinIO
    try:
        # SỬA LỖI: Dùng put_object thay vì upload_file
        s3.put_object(
            Bucket=bucket,
            Key=object_path,
            Body=parquet_buffer.getvalue() 
        )
        print(f"✅ Upload success: s3://{bucket}/{object_path}")
        
    except ClientError as e:
        # Log rõ ràng mã lỗi từ AWS/MinIO
        raise RuntimeError(
            f"Upload failed: bucket={bucket}, key={object_path}. Error: {e}"
        ) from e
    except Exception as e:
        # Bắt các lỗi khác (ví dụ lỗi parquet conversion)
        raise RuntimeError(f"Unexpected error during upload: {e}") from e
    finally:
        # Giải phóng bộ nhớ đệm
        parquet_buffer.close()


def upload_file(s3, bucket: str, object_path: str, file_path: str):
    """
    Upload một file từ ổ cứng local lên MinIO/S3.
    """
    
    # --- 1. Sanity Check: File có tồn tại không? ---
    # Đừng bao giờ tin tưởng input đường dẫn file một cách mù quáng.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Lỗi: Không tìm thấy file tại đường dẫn: {file_path}")
    
    # --- 2. Upload ---
    try:
        s3.upload_file(
            Filename=file_path,  # Chú ý: Chữ 'F' viết hoa, 'n' viết thường
            Bucket=bucket,       # Chú ý: Chữ 'B' viết hoa
            Key=object_path
        )
        print(f"✅ Upload success: Local '{file_path}' -> S3 's3://{bucket}/{object_path}'")
        return True

    except ClientError as e:
        # Bắt lỗi từ phía Server (MinIO/AWS) trả về (vd: 403 Forbidden, 404 Bucket Not Found)
        error_code = e.response['Error']['Code']
        raise RuntimeError(
            f"❌ S3 Upload Failed. Code: {error_code}. Bucket: {bucket}"
        ) from e
        
    except Exception as e:
        # Bắt các lỗi khác (vd: mất mạng, lỗi OS permission)
        raise RuntimeError(f"❌ Unexpected error uploading {file_path}: {e}") from e
    
import io
import pandas as pd
from botocore.exceptions import ClientError


def read_df(minio_config, bucket: str, object_path: str) -> pd.DataFrame:
    s3 = get_minio_client(minio_config=minio_config)

    try:
        response = s3.get_object(Bucket=bucket, Key=object_path)

        # 🔑 FIX: read bytes -> seekable buffer
        data = response["Body"].read()
        buffer = io.BytesIO(data)

        df = pd.read_parquet(buffer)

        print(f"✅ Read success: s3://{bucket}/{object_path}")
        return df

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        raise RuntimeError(
            f"❌ S3 Read Failed. Code: {error_code}. Bucket: {bucket}, Key: {object_path}"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"❌ Unexpected error reading s3://{bucket}/{object_path}: {e}"
        ) from e
