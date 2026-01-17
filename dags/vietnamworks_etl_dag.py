from datetime import datetime, timedelta
import os
import sys

from airflow.decorators import dag
from airflow.operators.bash import BashOperator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['vietnamworks', 'etl']
)
def vietnamworks_etl():

    extract = BashOperator(
        task_id='extract',
        bash_command='python -m etl.extract_to_raw --rundate {{ ds }}'
    )

    raw_to_silver = BashOperator(
        task_id='raw_to_silver',
        bash_command='python -m etl.raw_to_silver --rundate {{ ds }}'
    )

    silver_to_warehouse = BashOperator(
        task_id='silver_to_warehouse',
        bash_command='python -m etl.silver_to_warehouse --rundate {{ ds }}'
    )

    extract >> raw_to_silver >> silver_to_warehouse


dag = vietnamworks_etl()
