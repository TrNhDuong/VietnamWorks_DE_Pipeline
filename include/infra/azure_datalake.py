import os
import pandas as pd
import io 
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from include.logs.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger(__name__)

class AzureDataLakeClient:
    def __init__(self):
        # 1. Lấy Connection String trực tiếp từ môi trường
        self.connection_string = os.getenv("AZURE_CONNECTION_STRING")
        self.file_system_name = os.getenv("AZURE_CONTAINER_NAME", "vietnamworks")
        
        if not self.connection_string:
            logger.error("Missing AZURE_CONNECTION_STRING in .env file.")
            raise ValueError("AZURE_CONNECTION_STRING is not set.")

        logger.info(f"Initializing ADLS Gen2 Client via Connection String for container: {self.file_system_name}")
        
        try:
            # 2. Khởi tạo client chuẩn xác qua hàm from_connection_string
            self.service_client = DataLakeServiceClient.from_connection_string(self.connection_string)
            self.file_system_client = self.service_client.get_file_system_client(self.file_system_name)
        except Exception as e:
            logger.error(f"Failed to initialize ADLS Gen2 client: {e}")
            raise

    def close(self):
        """Đóng socket pool khi không dùng nữa"""
        self.service_client.close()

    def upload_dataframe(self, df: pd.DataFrame, remote_path: str, format='parquet'):
        """
        Upload DataFrame trực tiếp lên ADLS Gen2 (Không lưu file tạm)
        :param df: Pandas DataFrame
        :param remote_path: Đường dẫn trên Data Lake (VD: silver/jobs.parquet)
        :param format: 'parquet' (khuyên dùng) hoặc 'csv'
        """
        try:
            # 1. Tạo buffer trong RAM (IO Stream)
            output_buffer = io.BytesIO()

            # 2. Ghi DataFrame vào buffer (Serialize)
            if format == 'parquet':
                # Parquet nén tốt, giữ được schema (int là int, string là string)
                df.to_parquet(output_buffer, index=False)
            elif format == 'csv':
                # CSV chỉ dùng cho debug, không nên dùng cho pipeline chính
                df.to_csv(output_buffer, index=False, encoding='utf-8')
            else:
                logger.error(f"Unsupported format: {format}")
                raise ValueError("Format not supported. Use 'parquet' or 'csv'.")

            # 3. Đưa con trỏ về đầu buffer để chuẩn bị đọc
            data = output_buffer.getvalue()

            # 4. Upload byte stream lên Azure
            file_client = self.file_system_client.get_file_client(remote_path)
            file_client.upload_data(data, overwrite=True)
            
            logger.info(f"Uploaded DataFrame to {remote_path} ({len(data)/1024:.2f} KB)")

        except Exception as e:
            logger.error(f"Error uploading DataFrame: {e}")
            raise

    def get_dataframe(self, remote_path: str, format='parquet') -> pd.DataFrame:
        """
        Đọc trực tiếp từ Azure mà không cần tải buffer thủ công.
        Tận dụng tối đa khả năng Streaming và Predicate Pushdown của Parquet.
        """
        # Cấu trúc URL chuẩn của ADLS Gen2 cho Pandas
        # abfs://<container>/<folder>/<file>
        full_path = f"abfs://{self.file_system_name}/{remote_path}"
        
        # Truyền credential vào storage_options
        # adlfs sẽ tự dùng DefaultAzureCredential nếu không truyền key, 
        # nhưng truyền account_name là bắt buộc.
        storage_options = {
            "connection_string": self.connection_string
        }

        print(f"🔄 Streaming DataFrame from {full_path}...")

        try:
            if format == 'parquet':
                # Parquet thông minh: Nó chỉ tải phần Footer và Metadata trước,
                # Sau đó chỉ tải các cột cần thiết (Columnar Storage).
                # => Tiết kiệm RAM cực lớn.
                df = pd.read_parquet(full_path, storage_options=storage_options)
                
            elif format == 'csv':
                # CSV vẫn phải đọc tuần tự, nhưng adlfs quản lý buffer tốt hơn 
                # việc bạn readall()
                df = pd.read_csv(full_path, storage_options=storage_options)
                
            else:
                raise ValueError(f"Unsupported format: {format}")

            print(f"✅ Loaded {len(df)} rows.")
            return df

        except Exception as e:
            print(f"❌ Error reading dataframe: {e}")
            raise