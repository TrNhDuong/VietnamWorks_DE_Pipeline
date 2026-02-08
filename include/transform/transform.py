import pandas as pd
import json
from include.utilis.utilis import clean_html_text
# from include.infra.postgres import get_new_ids_by_temp_table
from datetime import date

def transform_silver(df_raw):
    # 1️⃣ Load JSONL
    df = df_raw.copy()

    # 2️⃣ Chọn cột quan trọng
    cols_to_keep = [
        "jobid","jobtitle", "joburl", "jobdescription", "jobrequirement", 
        "joblevel","joblevelvi",
        "salary","salarymin","salarymax","salarycurrency",
        "skills","benefits",
        "workinglocations","industriesv3",
        "createdon", "expiredon",
        "companyname", "companyurl", "companyid"
    ]
    valid_cols = [c for c in cols_to_keep if c in df.columns]

# 2. Kiểm tra tính toàn vẹn: Nếu danh sách rỗng -> Ném lỗi ngay lập tức
    if not valid_cols:
        # Tôi khuyến nghị in ra cả danh sách cột hiện có để dễ debug nhanh
        raise ValueError(
            f"Các cột hiện có trong dữ liệu: {list(df.columns)}"
        )

    # 3. Thực hiện filter
    df = df[valid_cols]

    # 2.1️⃣ Thêm ngày xử lý
    df["processed_date"] = date.today().isoformat()

    # 3️⃣ Clean HTML
    for col in ["jobdescription", "jobrequirement"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: clean_html_text(x) if isinstance(x, str) else x
            )

    # 4️⃣ Process workinglocations
    if "workinglocations" in df.columns:
        df["working_locations"] = df["workinglocations"].apply(
            lambda x: json.dumps(
                [loc.get("address") for loc in x if isinstance(loc, dict) and loc.get("address")],
                ensure_ascii=False
            ) if isinstance(x, list) else None
        )
        df = df.drop(columns=["workinglocations"])

    # 5️⃣ Process industriesV3
    if "industriesv3" in df.columns:
        df["industries"] = df["industriesv3"].apply(
            lambda x: json.dumps(
                [ind.get("industryV3NameVI") for ind in x if isinstance(ind, dict) and ind.get("industryV3NameVI")],
                ensure_ascii=False
            ) if isinstance(x, list) else None
        )
        df = df.drop(columns=["industriesv3"])

    # ⭐ 6️⃣ CHUẨN HOÁ TÊN CỘT → lowercase
    df.columns = df.columns.str.lower()

    for col in ["jobtitle", "jobdescription", "jobrequirement", "joblevel", "joblevelvi", "salarycurrency", "companyname"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # df = df[(df['salarymin'] >= 0) & (df['salarymax'] >= df['salarymin'])]


    return df


