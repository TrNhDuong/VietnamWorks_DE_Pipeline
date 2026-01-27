import pandas as pd
from include.infra.postgre import load_data


def load_data_to_staging(df_silver: pd.DataFrame, connect_str: str):
    load_data(schema='staging', table='job_company', df=df_silver, connect_str=connect_str)

def load_data_to_warehouse(df_delta_job: pd.DataFrame, df_delta_company: pd.DataFrame, connect_str):
    load_data(schema='warehouse', table='job', df=df_delta_job, connect_str=connect_str)
    load_data(schema='warehouse', table='company', df=df_delta_company, connect_str=connect_str)
 