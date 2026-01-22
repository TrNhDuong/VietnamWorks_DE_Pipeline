import pandas as pd
import requests
import datetime
import argparse
from utilis.utilis import loader
from infra.minio_client import get_minio_client, upload_df
from logs.logger import setup_logger

logger = setup_logger(__name__)

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
    data_config = loader(config_path='config.yaml', type='data')
    minio_config = loader(config_path='config.yaml', type='minio')

    url = data_config['url']
    body = data_config['body']
    bucket = minio_config['bucket']
    s3 = get_minio_client(minio_config=minio_config)

    logger.info("Extracting data from source API")
    raw_data = extract(url=url, body=body)
    raw_df = pd.DataFrame(raw_data)

    logger.info(f"Uploading raw data to MinIO at rundate: {rundate}")
    upload_df(s3=s3, bucket=bucket, object_path=f'raw/{rundate}.parquet', df=raw_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rundate', required=True)
    args = parser.parse_args()
    
    logger.info("Starting ETL Process - Extract Phase")
    data_config = loader(config_path='config.yaml', type='data')
    minio_config = loader(config_path='config.yaml', type='minio')

    url = data_config['url']
    body = data_config['body']
    bucket = minio_config['bucket']
    s3 = get_minio_client(minio_config=minio_config)

    logger.info("Extracting data from source API")
    raw_data = extract(url=url, body=body)
    raw_df = pd.DataFrame(raw_data)
    rundate = parser.parse_args().rundate

    logger.info(f"Uploading raw data to MinIO at rundate: {rundate}")
    upload_df(s3=s3, bucket=bucket, object_path=f'raw/{rundate}.parquet', df=raw_df)
    