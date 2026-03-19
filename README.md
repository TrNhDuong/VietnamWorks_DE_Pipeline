# 🚀 VietnamWorks Data Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-2.x-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Azure](https://img.shields.io/badge/Azure_Data_Lake-007FFF?style=for-the-badge&logo=microsoftazure&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-1.x-FF694B?style=for-the-badge&logo=dbt&logoColor=white)

---

## Overview

**VietnamWorks Data Engineering Pipeline** là dự án mô phỏng một hệ thống **ETL/ELT production-grade** nhằm thu thập, xử lý và lưu trữ dữ liệu thị trường việc làm từ VietnamWorks API.

Dự án được thiết kế theo tư duy **Modern Data Engineering**, áp dụng:

*   **Medallion Architecture**: Raw → Silver → Warehouse
*   **Airflow** cho orchestration (Containerized)
*   **dbt** cho transformation layer
*   **Azure Data Lake Gen2** cho Data Lake storage (Raw Zone)

---

## Tech Stack

*   **Language**: Python 3.9+
*   **Orchestration**: Apache Airflow 2.x
*   **Transformation**: dbt (Data Build Tool)
*   **Database**: PostgreSQL (NeonDB or Local)
*   **Object Storage**: Azure Data Lake Storage Gen2 (ADLS)
*   **Containerization**: Docker & Docker Compose
*   **Libraries**: `pandas`, `psycopg`, `azure-storage-file-datalake`, `adlfs`

---

## Project Structure

```bash
VIETNAMWORK/
├── dags/
│   └── vietnamworks_etl_dag.py      # Airflow DAG definition
│
├── doc/                             # Project Documentation
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   └── SETUP_RUN.md
│
├── pipeline/                        # ETL Pipelines
│   ├── extract_to_raw.py            # API -> MinIO (Raw) or ADLS
│   └── raw_to_silver.py             # Raw -> Postgres (Staging)
│
├── source/                          # ETL Logic & Utilities
│   ├── cleaner/
│   │   └── df.py                    # Data cleaning logic
│   ├── infra/
│   │   ├── azure_datalake.py        # Azure integration (if used)
│   │   ├── postgres.py              # Postgres connection wrapper
│   │   └── factory.py
│   ├── load/
│   │   └── load.py                  # Loading utilities
│   ├── logs/
│   │   └── logger.py                # Custom logging
│   ├── setup_db/
│   │   └── create_tables.py         # Database initialization
│   ├── transform/
│   │   └── transform.py             # Transformation logic
│   ├── utilis/
│   │   └── utilis.py                # Config loader & helpers
│   └── config.yaml                  # System Configuration
│
├── dbt_vietnamwork/                 # dbt Project
│   ├── models/
│   │   ├── staging/
│   │   └── warehouse/
│   └── dbt_project.yml
│
├── docker-compose.yml               # Infrastructure definition
├── Dockerfile                       # Custom Airflow image
└── requirements.txt                 # Python dependencies
```

---

## Installation & Setup

Dự án được đóng gói hoàn toàn bằng Docker Compose để dễ dàng triển khai trên môi trường local.

**Xem hướng dẫn chi tiết tại:** [SETUP_RUN.md](doc/SETUP_RUN.md)

### Quick Start

1. **Clone repository:**
   ```bash
   git clone git@github.com:TrNhDuong/VietnamWorks_DE_Pipeline.git
   cd VietnamWork
   ```

2. **Cấu hình file .env**
   ```bash
   AZURE_STORAGE_ACCOUNT_NAME =
   AZURE_CONTAINER_NAME =
   AZURE_CONNECTION_STRING =
   POSTGRES_CONNECTION_STRING =
   DBT_PASSWORD =
   ```
   Chi tiết hướng dẫn cấu hình ở file `doc/SETUP_RUN.md`


3. **Khởi chạy hệ thống:**
   ```bash
   docker-compose up -d --build
   ```


4. **Truy cập:**
   - Airflow UI: [http://localhost:8081](http://localhost:8081)
