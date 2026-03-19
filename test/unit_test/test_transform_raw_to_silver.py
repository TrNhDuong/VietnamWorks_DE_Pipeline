import sys
import os
import pandas as pd
import pytest
import json
from datetime import date

# Thêm thư mục gốc của project vào PYTHONPATH để Python nhận diện module "source"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from source.transform.transform import transform_silver

def test_transform_silver_valid_data():
    """Test function vói đầy đủ dữ liệu tiêu chuẩn (Happy path)"""
    data = {
        "JOBID": [1, 2],
        "JOBTitle": ["Data Engineer", "Software Engineer"],
        "jobURL": ["http://job1", "http://job2"],
        "jobDescription": ["<p>Work with data</p>", "<strong>Code apps</strong>"],
        "jobRequirement": ["<ul><li>SQL</li></ul>", "Java"],
        "jobLevel": ["Experienced", "Junior"],
        "jobLevelVI": ["Có kinh nghiệm", "Mới tốt nghiệp"],
        "salary": ["1000", "2000"],
        "salaryMin": [1000, 2000],
        "salaryMax": [2000, 3000],
        "salaryCurrency": ["USD", "VND"], 
        "skills": ["SQL, Python", "Java, C++"],
        "benefits": ["Insurance", "Free Lunch"],
        "workingLocations": [
            [{"address": "Hanoi, Vietnam"}],
            [{"address": "HCMC, Vietnam"}, {"address": "Da Nang, Vietnam"}]
        ],
        "industriesV3": [
            [{"industryV3NameVI": "IT - Phần mềm"}],
            "[{\"industryV3NameVI\": \"Kế toán\"}]" # Test string JSON parsing
        ],
        "createdOn": ["2023-01-01", "2023-01-02"],
        "expiredOn": ["2023-02-01", "2023-02-02"],
        "companyName": ["Company A", "Company B"],
        "companyUrl": ["http://compA", "http://compB"],
        "companyId": [101, 102],
        "junkColumn": ["junk1", "junk2"] # Cột dư thừa, sẽ bị drop
    }
    
    df_raw = pd.DataFrame(data)
    
    # Act
    df_transformed = transform_silver(df_raw)
    
    # Assert
    # 1. Kiểm tra tất cả cột đã được viết thường (lowercase)
    assert all(col.islower() for col in df_transformed.columns)
    
    # 2. Cột dư thừa phải bị xóa, cột chuẩn phải được giữ
    assert "junkcolumn" not in df_transformed.columns
    assert "jobtitle" in df_transformed.columns
    
    # 3. Đã thêm trường ngày xử lý processed_date
    assert "processed_date" in df_transformed.columns
    assert df_transformed["processed_date"].iloc[0] == date.today().isoformat()
    
    # 4. Kiểm tra trường workinglocations đã được chuyển thành working_locations (chứa danh sách dạng chuỗi json)
    assert "working_locations" in df_transformed.columns
    assert "workinglocations" not in df_transformed.columns
    loc1 = json.loads(df_transformed["working_locations"].iloc[0])
    assert loc1 == ["Hanoi, Vietnam"]
    
    loc2 = json.loads(df_transformed["working_locations"].iloc[1])
    assert loc2 == ["HCMC, Vietnam", "Da Nang, Vietnam"]
    
    # 5. Kiểm tra logic trường industriesv3 -> industries
    assert "industries" in df_transformed.columns
    assert "industriesv3" not in df_transformed.columns
    assert df_transformed["industries"].iloc[0] == ["IT - Phần mềm"]
    assert df_transformed["industries"].iloc[1] == ["Kế toán"]
    
    # 6. Kiểm tra các cột được yêu cầu lowercase values có đúng không
    assert df_transformed["jobtitle"].iloc[0] == "data engineer"
    assert df_transformed["joblevel"].iloc[0] == "experienced"

def test_transform_silver_empty_dataframe():
    """Test cảnh báo lỗi ValueError khi DataFrame không có cột nào hợp lệ """
    df_raw = pd.DataFrame({"random_col": [1, 2]})
    with pytest.raises(ValueError, match="Các cột hiện có trong dữ liệu"):
        transform_silver(df_raw)

def test_transform_silver_missing_optional_columns():
    """Test trường hợp thiếu vài cột không bắt buộc, hàm vẫn chạy đúng cho các cột còn lại"""
    data = {
        "jobid": [1],
        "jobtitle": ["Data Engineer"],
        # Cố tình thiếu industriesV3 và workingLocations
    }
    df_raw = pd.DataFrame(data)
    df_transformed = transform_silver(df_raw)
    
    assert "jobid" in df_transformed.columns
    assert "jobtitle" in df_transformed.columns
    assert "processed_date" in df_transformed.columns
    assert "industries" not in df_transformed.columns 
    assert "working_locations" not in df_transformed.columns 
