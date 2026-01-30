# Architecture Design Document

## 1. High-Level Architecture

Hệ thống được thiết kế theo mô hình **Medallion Architecture** (Multihop Architecture), đảm bảo tính toàn vẹn dữ liệu từ dạng thô (Raw) đến dạng sẵn sàng phân tích (Warehouse). Dữ liệu được thu thập từ API VietnamWorks, lưu trữ raw, làm sạch, và cuối cùng được mô hình hóa cho mục đích phân tích.

```mermaid
graph TD
    subgraph "Ingestion Layer"
        API[VietnamWorks API] -->|Extract| RAW[MinIO<br>(Raw Zone)<br>Bucket: vietnamwork]
    end

    subgraph "Processing Layer"
        RAW -->|Load & Transform| STAGING[Postgres DB<br>(Staging Schema)<br>Table: job_company]
    end

    subgraph "Transformation Layer (dbt)"
        STAGING -->|dbt run| WAREHOUSE[Postgres DB<br>(Warehouse Schema)<br>Tables: job, company]
    end

    subgraph "Orchestration"
        AF[Airflow] -->|Trigger| RAW
        AF -->|Trigger| STAGING
        AF -->|Trigger| WAREHOUSE
    end

    classDef storage fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef db fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef logic fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    
    class RAW storage;
    class STAGING,WAREHOUSE db;
    class AF logic;
```

## 2. Technology Stack

| Component | Technology | Role |
|-----------|------------|------|
| **Orchestrator** | Apache Airflow (via Docker) | Lên lịch, quản lý dependency và thực thi các task ETL. |
| **Logic ETL** | Python (Pandas) | Xử lý dữ liệu, transform JSON, cleaning. |
| **Transformation** | dbt (Data Build Tool) | Transform SQL, testing, và lineage cho Data Warehouse. |
| **Storage (Raw)** | MinIO | Object Storage tương thích S3, lưu trữ raw data (JSONL/Parquet). |
| **Storage (DW)** | PostgreSQL (NeonDB) | Database chính chứa Staging và Warehouse layers. |
| **Container** | Docker & Docker Compose | Đóng gói và triển khai toàn bộ môi trường local. |

## 3. Data Flow Detail

Luồng dữ liệu được chia thành 3 giai đoạn chính (Stages):

### Stage 1: Ingestion (Extract)
- **Source**: VietnamWorks REST API (`https://ms.vietnamworks.com/job-search/v1.0/search`).
- **Destination**: MinIO Bucket `vietnamwork`.
- **Format**: JSON Lines (`.jsonl`) hoặc Parquet.
- **Partition**: Theo ngày chạy (`run_date`).
- **Mục tiêu**: Lưu trữ lịch sử dữ liệu thô, cho phép replay lại ETL mà không cần gọi lại API bên thứ 3.

### Stage 2: Transform Raw to Silver (Staging)
- **Input**: Files từ MinIO.
- **Destination**: PostgreSQL schema `staging`.
- **Target Table**: `job_company` (Bảng phẳng chứa tất cả thông tin gộp).
- **Process**:
    - Đọc file từ MinIO.
    - Làm sạch (Cleaning): Xử lý null, convert types.
    - Flattening: Duỗi phẳng các cấu trúc nested đơn giản.
    - Type Casting: Đảm bảo đúng kiểu dữ liệu (Timestamp, Numeric).

### Stage 3: Silver to Gold (Warehouse via dbt)
- **Input**: Table `staging.job_company`.
- **Destination**: PostgreSQL schema `warehouse`.
- **Target Tables**:
    - `company`: Dimension table chứa thông tin công ty.
    - `job`: Fact table chứa thông tin chi tiết công việc.
- **Process**: Sử dụng **dbt** để thực hiện SQL transformations.
    - Deduplication: Loại bỏ bản ghi trùng lặp.
    - Normalization: Tách bảng Job và Company.
    - Validation: `dbt test` (unique, not_null).

## 4. Project Structure Mapping

- **`dags/`**: Chứa định nghĩa pipeline Airflow (`vietnamworks_etl_dag.py`).
- **`include/`**: Chứa source code Python cho các logic ETL.
    - `etl/`: Logic chính cho Extract, Transform, Load.
    - `cleaner/`, `utilis/`: Các hàm utility hỗ trợ.
    - `config.yaml`: Cấu hình chung của hệ thống.
- **`dbt_vietnamwork/`**: Project dbt chứa models và tests.
    - `models/staging/`: Source definitions.
    - `models/warehouse/`: Final models (`job.sql`, `company.sql`).
- **`docker-compose.yml`**: Định nghĩa services (Airflow, MinIO, Postgres, Redis).
