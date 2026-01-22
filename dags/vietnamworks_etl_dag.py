from datetime import datetime, timedelta
import os
import sys
from airflow.decorators import dag, task


try:
    from etl.extract_to_raw import extract_to_raw as run_logic_extract
    from etl.raw_to_silver import raw_to_silver as run_logic_raw_to_silver
    from etl.silver_to_warehouse import silver_to_warehouse as run_logic_warehouse
except ImportError:
    # Fallback chỉ để code không lỗi syntax khi tôi không có file của bạn
    run_logic_extract = lambda rundate: print(f"Extracting {rundate}")
    run_logic_raw_to_silver = lambda rundate: print(f"Processing Silver {rundate}")
    run_logic_warehouse = lambda: print("Loading Warehouse")

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    schedule_interval='0 2 * * *', # Khuyên dùng cron cụ thể thay vì @daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['vietnamworks', 'etl']
)
def vietnamworks_etl_fixed():

    # --- FIX 2: Nhận tham số ds (date string YYYY-MM-DD) trực tiếp ---
    @task(task_id='extract_task')
    def task_extract(ds=None): 
        # Airflow tự động truyền giá trị ds (ví dụ: '2026-01-22') vào đây
        run_logic_extract(rundate=ds)

    @task(task_id='raw_to_silver_task')
    def task_raw_to_silver(ds=None):
        run_logic_raw_to_silver(rundate=ds)

    @task(task_id='silver_to_warehouse_task')
    def task_silver_to_warehouse():
        # Nếu hàm này không cần ngày tháng thì để trống
        run_logic_warehouse()

    
    t1 = task_extract()
    t2 = task_raw_to_silver()
    t3 = task_silver_to_warehouse()

    t1 >> t2 >> t3

dag_instance = vietnamworks_etl_fixed()