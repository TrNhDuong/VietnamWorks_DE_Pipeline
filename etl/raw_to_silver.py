from argparse import ArgumentParser
from utilis.utilis import loader
from infra.minio_client import read_df
from transform.transform import transform_silver
from load.load import load_data_to_staging
from logs.logger import setup_logger

logger = setup_logger(__name__)

def raw_to_silver(rundate: str):
    logger.info("Starting ETL Process - Raw to Silver Phase")

    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    logger.info(f"Reading raw data from MinIO at rundate: {rundate}")
    df_raw = read_df(
        minio_config=minio_config,
        bucket=minio_config['bucket'],
        object_path=f'raw/{rundate}.parquet'
    )

    logger.info("Transforming raw data to silver format")  
    try:
        df_silver = transform_silver(df_raw=df_raw)
    except ValueError as e:
        logger.error(f"Collums not exists in data: {e}")
        raise e  

    logger.info("Loading silver data into staging database")
    load_data_to_staging(df_silver=df_silver, connect_str=connect_str)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--rundate', required=True)
    args = parser.parse_args()

    logger.info("Starting ETL Process - Raw to Silver Phase")

    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    rundate = args.rundate

    logger.info(f"Reading raw data from MinIO at rundate: {rundate}")
    df_raw = read_df(
        minio_config=minio_config,
        bucket=minio_config['bucket'],
        object_path=f'raw/{rundate}.parquet'
    )

    logger.info("Transforming raw data to silver format")    
    df_silver = transform_silver(df_raw=df_raw)

    logger.info("Loading silver data into staging database")
    load_data_to_staging(df_silver=df_silver, connect_str=connect_str)


