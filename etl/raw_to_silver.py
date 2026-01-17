from argparse import ArgumentParser
from utilis.utilis import loader
from infra.minio_client import read_df
from transform.transform import transform_silver
from load.load import load_data_to_staging



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--rundate', required=True)
    args = parser.parse_args()

    minio_config = loader(config_path='config.yaml', type='minio')
    postgres_config = loader(config_path='config.yaml', type='posgres')
    connect_str = postgres_config['connect_str']

    rundate = args.rundate
    df_raw = read_df(
        minio_config=minio_config,
        bucket=minio_config['bucket'],
        object_path=f'raw/{rundate}.parquet'
    )
    
    df_silver = transform_silver(df_raw=df_raw)
    load_data_to_staging(df_silver=df_silver, connect_str=connect_str)


