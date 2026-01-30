# Setup & Installation Guide

Hướng dẫn cài đặt và chạy dự án **VietnamWorks Data Pipeline** trên môi trường local.

## Prerequisites (Yêu cầu)

Trước khi bắt đầu, hãy đảm bảo bạn đã cài đặt các công cụ sau:
1. **Docker Desktop**: Để chạy container.
2. **Git**: Để clone source code.
3. **Python 3.9+** (Optional): Nếu muốn chạy script lẻ bên ngoài Docker.

## Installation Steps (Cài đặt)

### 1. Clone Repository
```bash
git clone git@github.com:TrNhDuong/VietnamWorks_DE_Pipeline.git
cd VietnamWork
```

### 2. Cấu hình Environment
Kiểm tra file `include/config.yaml`. Đây là nơi chứa các cấu hình quan trọng:
- **API URL**: Endpoint lấy dữ liệu.
- **MinIO**: User/Password mặc định (`minioadmin`/`minioadmin`).
- **Postgres**: Connection string đến Database (NeonDB hoặc Local).

### 3. Khởi chạy với Docker Compose
Sử dụng Docker Compose để dựng toàn bộ stack (Airflow, MinIO, Postgres, Redis).

```bash
docker-compose up -d --build
```
*Lệnh này sẽ build image Custom Airflow và pull các images cần thiết.*

### 4. Kiểm tra trang thái các dịch vụ
Sau khi chạy xong, truy cập các đường dẫn sau:
- **Airflow UI**: [http://localhost:8081](http://localhost:8081) (User: `airflow`, Pass: `airflow`)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001) (User: `minioadmin`, Pass: `minioadmin`)

## Database Initialization (Khởi tạo DB)

Nếu chạy lần đầu, bạn cần khởi tạo các bảng trong Database (Staging & Warehouse schema).
Đoạn script tạo bảng nằm tại `include/setup_db/create_tables.py`. Bạn có thể chạy nó thủ công hoặc thêm vào Airflow DAG nếu cần.

Để chạy thủ công (Yêu cầu Python local đã cài thư viện trong `requirements.txt`):
```bash
# Cài thư viện
pip install -r requirements.txt

# Run script
python -m include.setup_db.create_tables
```
*Lưu ý: Nếu sử dụng NeonDB Cloud, đảm bảo bạn đã update connection string trong `include/config.yaml` chính xác.*

## How to Run the Pipeline (Vận hành)

1. **Truy cập Airflow UI**: Login vào [http://localhost:8081](http://localhost:8081).
2. **Kích hoạt DAG**: Tìm DAG có tên `vietnamworks_etl_fixed` và gạt nút Trigger.
3. **Trigger DAG**: Bấm nút **Trigger DAG** (nút Play) để chạy ngay lập tức.
4. **Monitoring**:
    - Theo dõi các task `extract`, `transform`, `load` chuyển sang màu xanh lá cây (Success).
    - Checks Logs nếu có lỗi (Click vào task -> Logs).

## dbt Integration

Project dbt nằm trong thư mục `dbt_vietnamwork`. Airflow sẽ tự động trigger lệnh `dbt run` thông qua `BashOperator`.
Nếu muốn chạy dbt thủ công local:
```bash
cd dbt_vietnamwork
dbt run --vars "{'run_date': '2025-01-01'}" .
```
