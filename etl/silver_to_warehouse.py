from infra.postgre import read_table
from utilis.utilis import loader
from transform.transform import transform_gold, transform_delta
from load.load import load_data_to_warehouse
    
if __name__ == "__main__":
    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    df_silver = read_table(schema='staging', table='job_company', connect_str=connect_str)
    df_company_gold, df_job_gold = transform_gold(df_silver=df_silver)

    df_company_delta, df_job_delta = transform_delta(
        df_company_gold=df_company_gold,
        df_job_gold=df_job_gold,
        connect_str=connect_str, 
        warehouse_schema="warehouse", 
        company_table="company", 
        job_table="job"
    )
    
    # Load to Warehouse
    load_data_to_warehouse(
        df_delta_job=df_job_delta, 
        df_delta_company=df_company_delta, 
        connect_str=connect_str
    )




