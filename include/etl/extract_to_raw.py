import pandas as pd
import requests
import os
import argparse
from include.utilis.utilis import loader
from include.logs.logger import setup_logger
from include.infra.factory import Factory

logger = setup_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml')

def extract(url, body):
    page = 0
    records = []
    while True:
        payload = body.copy()
        payload["page"] = page

        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
        except ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise e

        try:
            data = resp.json().get("data", [])
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise e

        if not data:
            break

        for record in data:
            records.append(record)
        page += 1
        break
    return records

def extract_to_raw(rundate: str):
    logger.info(f"Loading config from: {CONFIG_PATH}")
    
    # Thêm check tồn tại file để debug
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"CRITICAL: Không tìm thấy file config tại {CONFIG_PATH}")
    
    data_config = loader(config_path=CONFIG_PATH, type='data')
    url = data_config['url']
    body = data_config['body']

    logger.info("Extracting data from source API")
    raw_data = extract(url=url, body=body)
    raw_df = pd.DataFrame(raw_data)

    logger.info(f"Uploading raw data to Azure at rundate: {rundate}")
    adls_client = Factory.get_adls_client()
    adls_client.upload_dataframe(
        df=raw_df,
        remote_path=f'raw/{rundate}.parquet',
        format='parquet'
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rundate', required=True)
    args = parser.parse_args()
    
    logger.info("Starting ETL Process - Extract Phase")
    data_config = loader(config_path=CONFIG_PATH, type='data')
    
    url = data_config['url']
    body = data_config['body']

    logger.info("Extracting data from source API")
    raw_data = extract(url=url, body=body)
    raw_df = pd.DataFrame(raw_data)
    rundate = parser.parse_args().rundate

    logger.info(f"Uploading raw data to Azure at rundate: {rundate}")

    adls_client = Factory.get_adls_client()
    adls_client.upload_dataframe(
        df=raw_df,
        remote_path=f'raw/{rundate}.parquet',
        format='parquet'
    )
    