# 🚀 VietnamWorks Data Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-2.x-017CEE?style=for-the-badge\&logo=apacheairflow\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge\&logo=postgresql\&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge\&logo=minio\&logoColor=white)

---

## 📖 Overview

**VietnamWorks Data Engineering Pipeline** là dự án mô phỏng một hệ thống **ETL/ELT production-grade** nhằm thu thập, xử lý và lưu trữ dữ liệu thị trường việc làm từ VietnamWorks API.

Dự án được thiết kế theo tư duy **Modern Data Engineering**, áp dụng:

* **Medallion Architecture**: Raw → Silver → Warehouse
* **Airflow** cho orchestration
* **Python CLI-based ETL** (chạy độc lập, không phụ thuộc Airflow runtime)
Mục tiêu không phải demo, mà là **thiết kế có thể scale và maintain**.

---

## 🛠 Tech Stack

* **Language**: Python 3.9+
* **Orchestration**: Apache Airflow
* **Data Processing**: dbt
* **Database**: PostgreSQL Neon Cloud
* **Object Storage**: MinIO (S3 compatible)
* **Core Libraries**:

  * `pandas`
  * `requests`
  * `psycopg`
  * `minio`
  * `pyyaml`

---

## 📂 Project Structure

```bash
VIETNAMWORK/
├── dags/
│   └── vietnamworks_etl_dag.py      # Airflow DAG (chỉ orchestration)
│
├── doc/                             # Documemt của hệ thống
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── SETUP_RUN.md
│   └── 
│
├── include/
│   ├── cleaner/
│   │   └── df.py                    # Data cleaning utilities
│   │
│   ├── etl/
│   │   ├── extract_to_raw.py        # Extract API → Raw (MinIO)
│   │   ├── raw_to_silver.py         # Transform Raw → Silver
│   │   ├── silver_to_warehouse.py   # Transform + Load → Warehouse
│   │   └── __init__.py
│   │
│   ├── infra/
│   │   ├── minio_client.py          # MinIO helpers
│   │   ├── postgre.py               # PostgreSQL helpers
│   │   └── __init__.py
│   │
│   ├── load/
│   │   └── load.py                  # Load logic
│   │
│   ├── logs/
│   │   ├── logger.py
│   │   └── etl.log
│   │
│   ├── setup_db/
│   │   └── create_tables.py         # Init schema & tables
│   │
│   ├── transform/
│   │   └── transform.py             # Shared transform logic
│   │
│   ├── utilis/
│   │   └── utilis.py                # Config loader, common helpers
│   │              
│   └── config.yaml                  # Config
├── logs/                            # Airflow / runtime logs
│
├── plugins/                         # Airflow plugins (nếu có)
│
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

### Design Notes

* **DAG chỉ orchestration**, không chứa business logic
* Mỗi file trong `etl/` có thể chạy độc lập qua CLI
* Logic dùng lại được tách sang `infra/`, `transform/`, `load/`, `cleaner/`

---

## ⚙️ Installation & Setup

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configuration

Cấu hình trong `config.yaml`:

```yaml
data:
  url: https://ms.vietnamworks.com/job-search/v1.0/search
  body: {"userId":0,"query":"","filter":[],"ranges":[],"order":[],
        "hitsPerPage":100,"page":0,
        "retrieveFields":["address","benefits","jobTitle","salaryMax",
                          "isSalaryVisible","jobLevelVI","isShowLogo",
                          "salaryMin","companyLogo","userId","jobLevel",
                          "jobLevelId","jobId","jobUrl","companyId","approvedOn",
                          "isAnonymous","alias","expiredOn","industries",
                          "industriesV3","workingLocations","services",
                          "companyName","salary","onlineOn","simpleServices",
                          "visibilityDisplay","isShowLogoInSearch","priorityOrder",
                          "skills","profilePublishedSiteMask","jobDescription",
                          "jobRequirement","prettySalary","requiredCoverLetter",
                          "languageSelectedVI","languageSelected","languageSelectedId",
                          "typeWorkingId","createdOn","isAdrLiteJob"],
        "summaryVersion":""
    }

minio:
  endpoint_url: http://minio:9000
  access_key: minioadmin
  secret_key: minioadmin
  bucket: vietnamwork

posgres:
  connect_str:
  staging:
    schema: staging
    table: job_company
  warehouse:
    schema: warehouse

  dbname: tnd
  user: tnd
  password: tnd
  host: localhost
  port: 5432
```

---


