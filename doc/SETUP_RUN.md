# Setup & Installation Guide

Hướng dẫn cài đặt và vận hành hệ thống **VietnamWorks Data Pipeline** trên môi trường Local.

## 1. Prerequisites (Yêu cầu)

Đảm bảo bạn đã cài đặt:
1. **Docker Desktop**: Công cụ chính để chạy hệ thống.
2. **Git**: Để clone source code.
3. **Azure Account**: Một tài khoản Azure có quyền truy cập vào Storage Account (Data Lake Gen2).

## 2. Configuration & Secrets

Vì hệ thống sử dụng **Azure Data Lake Gen2**, bạn cần cung cấp thông tin xác thực (Credentials) an toàn.

### Bước 1: Tạo file `.env`
Tạo một file `.env` tại thư mục gốc dự án (ngang hàng `docker-compose.yml`) và điền thông tin Azure của bạn:

```bash
# Azure Storage Config
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_CONTAINER_NAME=vietnamworks

# Authentication (Service Principal - Recommended)
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# Postgres Config (Optional Override)
# POSTGRES_USER=tnd
# POSTGRES_PASSWORD=tnd
```

### Bước 2: Build & Start System
```bash
docker-compose up -d --build
```

### Bước 3: Verify Services
- **Airflow UI**: [http://localhost:8081](http://localhost:8081) (User/Pass: `airflow`/`airflow`)
- **Azure Portal**: Kiểm tra Storage Account của bạn trên Azure để xem dữ liệu Raw.

## 3. Database Setup (Running Locally/Manually)

Nếu Database của bạn chưa có bảng (Run lần đầu), bạn cần khởi tạo schema `staging` và `warehouse`.

Có 2 cách để khởi tạo:

**Cách A: Dùng script Python có sẵn (Khuyên dùng)**
Nếu bạn có Python local:
```bash
pip install -r requirements.txt
python -m include.setup_db.create_tables
```

**Cách B: Dùng SQL Client**
Kết nối vào Postgres và chạy DDL thủ công cho schema `staging` và `warehouse`.

## 4. Run the Pipeline

### Option 1: Trigger via Airflow (Recommended)
1. Truy cập **Airflow UI**: [http://localhost:8081](http://localhost:8081).
2. Tìm DAG **`vietnamworks_etl_fixed`**.
3. Toggle button **ON** (Unpause).
4. Click nút **Play** (Trigger DAG) để chạy.

**Monitoring**:
- Click vào DAG để xem Graph View.
- Theo dõi màu xanh lá cây (Success) qua các bước `extract` -> `raw_to_silver` -> `dbt_run`.

### Option 2: Run via CLI (For Development)
Bạn có thể chạy từng module riêng lẻ nếu đã cài môi trường Python local.

```bash
# 1. Extract
python -m include.etl.extract_to_raw

# 2. Transform to Staging
python -m include.etl.raw_to_silver

# 3. dbt Run
cd dbt_vietnamwork
dbt run
```

## 5. Configuration (`include/config.yaml`)

Cấu hình hệ thống nằm tại `include/config.yaml`.
**Lưu ý**: Thông tin nhạy cảm (Credentials) nên để trong `.env`, không hardcode vào `config.yaml`.

- **API URL/Body**: Tham số request lấy job.
- **Postgres Creds**: Thông tin kết nối Database.

```yaml
posgres:
  host: localhost  # Đổi thành 'postgres' nếu chạy trong Docker container
  port: 5432
  user: tnd        # Cập nhật username của bạn
  password: tnd    # Cập nhật password của bạn
```

## 6. dotenv configuration file ./.env
```bash
    AZURE_STORAGE_ACCOUNT_NAME = 
    AZURE_CONTAINER_NAME = 
    POSTGRES_CONNECTION_STRING = 
    DBT_PASSWORD = 
```
