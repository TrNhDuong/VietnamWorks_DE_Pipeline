# DESIGN.md

VietnamWorks Data Engineering Pipeline

---

## 1. Mục tiêu thiết kế

Dự án này mô phỏng một **ETL pipeline theo hướng production-grade**, tập trung vào:

* Tư duy **Data Engineering thực tế**, không phải demo
* Khả năng **maintain, re-run, debug**
* Tách biệt rõ **orchestration – business logic – infrastructure**
* Phù hợp với quy mô nhỏ nhưng **có thể mở rộng**

Đối tượng hướng tới: **intern / fresher Data Engineer**, nhưng tư duy thiết kế tiệm cận junior.

---

## 2. Tổng quan kiến trúc

Pipeline áp dụng **Medallion Architecture**:

```
Raw (Object Storage) 
   → Silver (Cleaned / Normalized Tables) 
      → Warehouse (Analytics-ready Tables)
```

Nguồn dữ liệu: VietnamWorks API
Công cụ orchestration: Apache Airflow
Lưu trữ file: MinIO (S3-compatible)
Data Warehouse: PostgreSQL

---

## 3. Data Flow chi tiết

### 3.1 Extract → Raw

* Gọi VietnamWorks API theo `rundate`
* Lưu toàn bộ response gốc (JSON) vào MinIO
* Không transform, không validate business logic ở bước này

**Mục tiêu:**

* Giữ nguyên dữ liệu gốc để:

  * reprocess
  * audit
  * debug khi upstream thay đổi

---

### 3.2 Raw → Silver

* Đọc JSON từ MinIO
* Thực hiện:

  * cleaning
  * normalize field
  * split entity (job, company, location, skill, …)
* Áp dụng các rule cơ bản:

  * drop record thiếu key chính
  * chuẩn hóa kiểu dữ liệu

**Mục tiêu:**

* Tách dữ liệu theo domain
* Chuẩn bị cho việc load vào database

---

### 3.3 Silver → Warehouse

* Thực hiện **delta-based loading**
* Kiểm tra record đã tồn tại hay chưa
* Upsert theo business key (`job_id`, `company_id`)
* Gắn `processed_date`

**Mục tiêu:**

* Idempotent theo `rundate`
* Có thể chạy lại pipeline mà không gây duplicate

---

## 4. Vì sao dùng Medallion Architecture?

* **Raw**: bảo toàn dữ liệu gốc, không phụ thuộc logic hiện tại
* **Silver**: xử lý nghiệp vụ, dễ debug, dễ test
* **Warehouse**: phục vụ analytics, reporting, downstream systems

Cách làm này phổ biến trong hệ thống data thực tế vì:

* giảm coupling
* tăng khả năng mở rộng
* dễ rollback và reprocess

---

## 5. Orchestration vs Business Logic

### Nguyên tắc:

* **Airflow chỉ dùng để orchestration**
* Không chứa:

  * transform logic
  * SQL phức tạp
  * data processing

### Lý do:

* ETL script có thể:

  * chạy độc lập bằng CLI
  * test riêng
  * debug không cần Airflow
* Giảm phụ thuộc runtime của Airflow
* Dễ migrate sang công cụ orchestration khác nếu cần

---

## 6. CLI-based ETL Design

Mỗi bước ETL:

* Có thể chạy bằng:

  ```
  python -m etl.<module> --rundate YYYY-MM-DD
  ```
* Nhận `rundate` làm input chính

**Lợi ích:**

* Debug nhanh
* Re-run selective
* Dễ tích hợp với scheduler khác ngoài Airflow

---

## 7. Idempotency & Reprocessing

Pipeline được thiết kế **idempotent theo `rundate`**:

* Chạy lại cùng `rundate`:

  * không tạo duplicate
  * không phá dữ liệu cũ
* Dữ liệu Raw được lưu theo partition ngày
* Warehouse sử dụng upsert theo business key

Điều này cho phép:

* backfill
* reprocess khi logic thay đổi
* xử lý lỗi upstream

---

## 8. Data Handoff Strategy

Không sử dụng:

* XCom cho data lớn
* Truyền DataFrame giữa tasks

Thay vào đó:

* File-based handoff (MinIO)
* DB-based handoff (PostgreSQL)

**Lý do:**

* Tránh bottleneck Airflow metadata DB
* Phù hợp best practice trong data engineering

---

## 9. Logging & Observability (định hướng)

Pipeline được thiết kế để dễ mở rộng logging:

* Log theo module
* Log rõ:

  * start / end step
  * record count
  * error + traceback
* Có thể tích hợp alerting sau này

Mục tiêu: **debug được khi pipeline fail**, không “chạy mù”.

---

## 10. Trade-offs & Giới hạn hiện tại

### Chấp nhận:

* Không dùng Spark / Kafka
* Không triển khai streaming
* Data quality check ở mức cơ bản

### Lý do:

* Phù hợp scope intern / fresher
* Tập trung vào nền tảng tư duy
* Tránh over-engineering

---

## 11. Hướng mở rộng trong tương lai

* Data quality framework
* Metadata & audit tables
* Incremental watermark rõ ràng hơn
* Monitoring & alerting
* CI/CD cho pipeline

---

## 12. Kết luận

Dự án này không nhằm phô trương công nghệ, mà tập trung vào:

* **đúng tư duy**
* **đúng kiến trúc**
* **đúng cách làm việc của Data Engineer**

Thiết kế ưu tiên:

> Maintainability > Scalability (ở giai đoạn đầu) > Fancy technology

Đây là nền tảng để phát triển thành pipeline production thực thụ trong tương lai.
