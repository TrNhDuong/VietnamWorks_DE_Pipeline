import pandas as pd
from include.infra.factory import Factory


def load_data_to_staging(df_silver: pd.DataFrame, connect_str: str):
    postgres_client = Factory.get_postgres_client(connect_str=connect_str)
    postgres_client.load_data(schema='staging', table='job_company', df=df_silver)

 