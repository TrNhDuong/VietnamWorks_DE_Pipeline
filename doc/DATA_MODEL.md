# Data Model Documentation

Tài liệu này mô tả chi tiết các mô hình dữ liệu (Data Models) trong hệ thống Data Warehouse.

## 1. Conceptual Model

Mô hình dữ liệu trong Warehouse tuân theo kiến trúc **Star Schema** đơn giản hóa, tập trung vào đối tượng chính là **Job** (Công việc).

```mermaid
erDiagram
    COMPANY ||--|{ JOB : "posts"}
    
    COMPANY {
        string company_id PK
        string company_name
        string company_url
        string processed_date
    }

    JOB {
        string job_id PK
        string job_title
        string company_id FK
        numeric salary_min
        numeric salary_max
        string job_level
        string job_description
        string job_requirements
        string benefits
        jsonb working_locations
        jsonb industries
        timestamp created_on
        timestamp expired_on
    }
```

## 2. Physical Data Model

### 2.1. Staging Area (Schema: `staging`)

Dữ liệu sau khi raw được load vào Staging. Đây vẫn là dạng dữ liệu phẳng (denormalized), gần với cấu trúc JSON ban đầu nhưng ở dạng bảng.

**Table: `job_company`**

| Column Name | Type | Description |
|---|---|---|
| `jobId` | TEXT | ID duy nhất của công việc từ nguồn. |
| `jobTitle` | TEXT | Tiêu đề công việc. |
| `companyId` | TEXT | ID của công ty. |
| `companyName` | TEXT | Tên công ty. |
| `salaryMin` | NUMERIC | Mức lương tối thiểu. |
| `salaryMax` | NUMERIC | Mức lương tối đa. |
| `createdOn` | TIMESTAMP | Thời gian tạo bài đăng. |
| `expiredOn` | TIMESTAMP | Thời gian hết hạn. |
| `working_locations` | JSONB | Danh sách địa điểm làm việc (JSON array). |
| `industries` | JSONB | Danh sách ngành nghề (JSON array). |
| ... | (các trường khác) | Các trường bổ trợ như `jobDescription`, `benefits`, `skills`. |

### 2.2. Warehouse Area (Schema: `warehouse`)

Dữ liệu được làm sạch, tách bảng và chuẩn hóa để phục vụ báo cáo.

**Table: `company` (Dimension)**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `company_id` | TEXT | PK | ID duy nhất của công ty. |
| `company_name` | TEXT | | Tên hiển thị của công ty. |
| `company_url` | TEXT | | Link đến trang công ty trên VietnamWorks. |
| `processed_date` | DATE | | Ngày dữ liệu được xử lý vào DW. |

**Table: `job` (Fact)**

| Column Name | Type | Key | Description |
|---|---|---|---|
| `job_id` | TEXT | PK | ID duy nhất của bài đăng tuyển dụng. |
| `job_title` | TEXT | | Tiêu đề công việc. |
| `company_id` | TEXT | FK | Reference sang bảng `company`. |
| `salary_min` | NUMERIC | | Lương tối thiểu. |
| `salary_max` | NUMERIC | | Lương tối đa. |
| `salary_currency`| TEXT | | Đơn vị tiền tệ (VND, USD). |
| `job_level` | TEXT | | Cấp bậc (Manager, Stack, etc.). |
| `working_locations`| JSONB | | Địa điểm làm việc (lưu dạng JSON để linh hoạt). |
| `industries` | JSONB | | Ngành nghề liên quan. |
| `created_on` | TIMESTAMP | | Ngày đăng. |
| `expired_on` | TIMESTAMP | | Ngày hết hạn. |

## 3. Data Dictionary Notes

- **`working_locations`**: Lưu trữ dưới dạng JSONB array. Ví dụ: `[{"city": "Ho Chi Minh", "district": "District 1"}]`. Việc này giúp truy vấn linh hoạt mà không cần bảng cầu nối quá phức tạp cho use-case hiện tại.
- **`salary`**: Được tách thành `salary_min` và `salary_max` để tiện cho việc query range. Nếu lương là "Thỏa thuận", giá trị có thể là NULL hoặc 0 tùy logic cleaning.
