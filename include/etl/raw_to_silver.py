from argparse import ArgumentParser
from include.utilis.utilis import loader
from include.transform.transform import transform_silver
from include.load.load import load_data_to_staging
from include.logs.logger import setup_logger
from include.infra.factory import Factory
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml')

load_dotenv()

logger = setup_logger(__name__)

def raw_to_silver(rundate: str):
    logger.info("Starting ETL Process - Raw to Silver Phase")

    connect_str = os.getenv('POSTGRES_CONNECTION_STRING')

    logger.info(f"Reading raw data from Azure at rundate: {rundate}")
    adls_client = Factory.get_adls_client()

    df_raw = adls_client.get_dataframe(
        remote_path=f'raw/{rundate}.parquet',
        format='parquet'
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

    adls_client = Factory.get_adls_client()

    connect_str = os.getenv('POSTGRES_CONNECTION_STRING')

    rundate = args.rundate

    logger.info(f"Reading raw data from Azure at rundate: {rundate}")
    df_raw = adls_client.get_dataframe(
        remote_path=f'raw/{rundate}.parquet',
        format='parquet'
    )

    logger.info("Transforming raw data to silver format")    
    df_silver = transform_silver(df_raw=df_raw)

    logger.info("Loading silver data into staging database")
    load_data_to_staging(df_silver=df_silver, connect_str=connect_str)


