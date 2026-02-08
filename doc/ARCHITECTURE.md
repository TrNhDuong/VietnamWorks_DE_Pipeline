# Architecture Design Document

## 1. High-Level Architecture

Hệ thống được thiết kế theo mô hình **Medallion Architecture**, đảm bảo tính toàn vẹn dữ liệu từ dạng thô (Raw) đến dạng sẵn sàng phân tích (Warehouse).

```mermaid
graph TD
    subgraph "Ingestion Layer"
        API[VietnamWorks API] -->|Extract| RAW[Azure Data Lake Gen2<br>(Raw Zone)<br>Container: vietnamworks]
    end

    subgraph "Processing Layer"
        RAW -->|Load & Transform| STAGING[Postgres DB<br>(Staging Schema)<br>Table: job_company]
    end

    subgraph "Transformation Layer (dbt)"
        STAGING -->|dbt run| WAREHOUSE[Postgres DB<br>(Warehouse Schema)<br>Tables: job, company]
    end

    subgraph "Orchestration (Airflow)"
        AF[Airflow DAG]
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
| **Orchestrator** | Apache Airflow 2.x | Lên lịch, quản lý dependency và thực thi các task ETL. |
| **Logic ETL** | Python (Pandas) | Xử lý dữ liệu ban đầu, transform JSON, cleaning. |
| **Transformation** | dbt (Data Build Tool) | Transform SQL, testing, và tạo lineage cho Data Warehouse. |
| **Storage (Raw)** | **Azure Data Lake Gen2** | Cloud Storage lưu trữ raw data (Parquet/JSONL). |
| **Database** | PostgreSQL | Chứa Staging và Warehouse layers. |
| **Infrastructure** | Docker Compose | Đóng gói toàn bộ môi trường. |

## 3. Data Flow Detail

Luồng dữ liệu được chia thành 3 giai đoạn chính:

### Stage 1: Ingestion (Extract)
- **Code**: `include/etl/extract_to_raw.py`
- **Source**: VietnamWorks REST API.
- **Destination**: Azure Data Lake Storage Gen2 (Container `vietnamworks`).
- **Format**: JSON Lines (`.jsonl`) hoặc Parquet.
- **Partition**: Theo ngày chạy (`run_date`).
- **Credential**: Sử dụng `DefaultAzureCredential` hoặc Access Key.

### Stage 2: Transform Raw to Staging (Silver)
- **Code**: `include/etl/raw_to_silver.py`
- **Input**: Files từ ADLS Gen2 (đọc qua `adlfs`).
- **Destination**: PostgreSQL schema `staging`.
- **Target Table**: `job_company` (Flat table).
- **Process**:
    - Đọc file từ ADLS Gen2.
    - Cleaning: Xử lý giá trị Null, convert typing.
    - Type Casting: Đảm bảo đúng kiểu dữ liệu (Timestamp, Numeric, JSONB).

### Stage 3: Staging to Warehouse (Gold via dbt)
- **Code**: `dbt_vietnamwork/`
- **Input**: Table `staging.job_company`.
- **Destination**: PostgreSQL schema `warehouse`.
- **Target Tables**:
    - `company`: Dimension table (SCD Type 1/2 tùy cấu hình).
    - `job`: Fact table.
- **Process**:
    - `dbt run`: Thực thi transformation SQL.
    - `dbt test`: Validate dữ liệu (unique, not_null, relationship).

## 4. Components Mapping

- **`dags/vietnamworks_etl_dag.py`**: Định nghĩa luồng chạy.
    - Task 1: `extract_task` (Python Operator).
    - Task 2: `raw_to_silver_task` (Python Operator).
    - Task 3: `dbt_run_task` (Bash Operator -> `dbt run`).

- **`include/`**: Chứa Core Logic (Logic này có thể chạy độc lập không cần Airflow).
