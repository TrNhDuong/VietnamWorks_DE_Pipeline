import pandas as pd
import requests
import datetime
import argparse
from utilis.utilis import loader
from infra.minio_client import get_minio_client, upload_df


def extract(url, body):
    page = 0
    records = []
    while True:
        payload = body.copy()
        payload["page"] = page

        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json().get("data", [])
        if not data:
            break

        for record in data:
            records.append(record)
        page += 1
        break
    return records

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rundate', required=True)
    args = parser.parse_args()
    
    print("🚀 Starting ETL Process - Extract Phase")
    data_config = loader(config_path='config.yaml', type='data')
    minio_config = loader(config_path='config.yaml', type='minio')

    url = data_config['url']
    body = data_config['body']
    bucket = minio_config['bucket']
    s3 = get_minio_client(minio_config=minio_config)
    print("🔗 Extracting data from source API")
    raw_data = extract(url=url, body=body)
    raw_df = pd.DataFrame(raw_data)
    print(raw_df.head())
    rundate = parser.parse_args().rundate
    
    print(f"📦 Uploading raw data to MinIO at rundate: {rundate}")
    # upload_df(s3=s3, bucket=bucket, object_path=f'raw/{rundate}.parquet', df=raw_df)
    