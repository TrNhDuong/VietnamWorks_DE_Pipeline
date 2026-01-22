from infra.postgre import read_table
from utilis.utilis import loader
from transform.transform import transform_gold, transform_delta
from load.load import load_data_to_warehouse
from logs.logger import setup_logger

logger = setup_logger(__name__)

def silver_to_warehouse():
    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    logger.info(" Starting ETL Process - Silver to Warehouse Phase")
    df_silver = read_table(schema='staging', table='job_company', connect_str=connect_str)

    logger.info("Transforming silver data to gold format")
    df_company_gold, df_job_gold = transform_gold(df_silver=df_silver)

    logger.info("Transforming gold data to delta format")
    df_company_delta, df_job_delta = transform_delta(
        df_company_gold=df_company_gold,
        df_job_gold=df_job_gold,
        connect_str=connect_str, 
        warehouse_schema="warehouse", 
        company_table="company", 
        job_table="job"
    )
    
    # Load to Warehouse
    logger.info("Loading delta data into warehouse")
    load_data_to_warehouse(
        df_delta_job=df_job_delta, 
        df_delta_company=df_company_delta, 
        connect_str=connect_str
    )
    
if __name__ == "__main__":
    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    logger.info(" Starting ETL Process - Silver to Warehouse Phase")
    df_silver = read_table(schema='staging', table='job_company', connect_str=connect_str)

    logger.info("Transforming silver data to gold format")
    df_company_gold, df_job_gold = transform_gold(df_silver=df_silver)

    logger.info("Transforming gold data to delta format")
    df_company_delta, df_job_delta = transform_delta(
        df_company_gold=df_company_gold,
        df_job_gold=df_job_gold,
        connect_str=connect_str, 
        warehouse_schema="warehouse", 
        company_table="company", 
        job_table="job"
    )
    
    # Load to Warehouse
    logger.info("Loading delta data into warehouse")
    load_data_to_warehouse(
        df_delta_job=df_job_delta, 
        df_delta_company=df_company_delta, 
        connect_str=connect_str
    )




