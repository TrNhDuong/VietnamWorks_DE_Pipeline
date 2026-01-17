import pandas as pd
import json
from utilis.utilis import clean_html_text
from infra.postgre import get_new_ids_by_temp_table
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
    df = df[[c for c in cols_to_keep if c in df.columns]]

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

    return df



def transform_gold(df_silver: pd.DataFrame):
    company_rows = []
    job_rows = []

    for _, raw in df_silver.iterrows():
        company_rows.append({
            "company_id": raw["companyid"],
            "company_name": raw["companyname"].lower() if isinstance(raw["companyname"], str) else raw["companyname"],
            "company_url": raw["companyurl"],  # giữ nguyên
            "processed_date": raw["processed_date"]
        })

        job_rows.append({
            "job_id": raw["jobid"],
            "job_title": raw["jobtitle"].lower() if isinstance(raw["jobtitle"], str) else raw["jobtitle"],
            "job_url": raw["joburl"],
            "description": raw["jobdescription"].lower() if isinstance(raw["jobdescription"], str) else raw["jobdescription"],
            "requirement": raw["jobrequirement"].lower() if isinstance(raw["jobrequirement"], str) else raw["jobrequirement"],
            "job_level": raw["joblevel"].lower() if isinstance(raw["joblevel"], str) else raw["joblevel"],
            "job_level_vi": raw["joblevelvi"].lower() if isinstance(raw["joblevelvi"], str) else raw["joblevelvi"],
            "salary_min": raw["salarymin"],
            "salary_max": raw["salarymax"],
            "salary_currency": raw["salarycurrency"].lower() if isinstance(raw["salarycurrency"], str) else raw["salarycurrency"],
            "working_locations": raw.get("working_locations"),
            "industries": raw.get("industries"),
            "created_on": raw["createdon"],
            "expired_on": raw["expiredon"],
            "company_id": raw["companyid"],
            "processed_date": raw["processed_date"]
        })

    df_company = (
        pd.DataFrame(company_rows)
        .drop_duplicates(subset=["company_id"])
    )

    df_job = (
        pd.DataFrame(job_rows)
        .drop_duplicates(subset=["job_id"])
    )

    return df_company, df_job



def transform_delta(df_company_gold: pd.DataFrame, df_job_gold: pd.DataFrame, connect_str: str,
                    warehouse_schema: str, company_table: str , job_table: str):
    
    # ===== COMPANY DELTA =====
    company_ids_to_check = df_company_gold["company_id"].unique().tolist()
    new_company_ids = get_new_ids_by_temp_table(connect_str=connect_str, warehouse_schema=warehouse_schema, table=company_table, id_col="company_id", id_list=company_ids_to_check)
    df_company_delta = df_company_gold[df_company_gold["company_id"].astype(str).isin(new_company_ids)]

    # ===== JOB DELTA =====
    job_ids_to_check = df_job_gold["job_id"].unique().tolist()
    new_job_ids = get_new_ids_by_temp_table(connect_str=connect_str, warehouse_schema=warehouse_schema, table=job_table, id_col="job_id", id_list=job_ids_to_check)
    df_job_delta = df_job_gold[df_job_gold["job_id"].astype(str).isin(new_job_ids)]
    df_job_delta = df_job_delta.drop_duplicates(subset=["job_id"])

    return df_company_delta, df_job_delta