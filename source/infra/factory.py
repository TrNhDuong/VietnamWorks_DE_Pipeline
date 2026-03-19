from source.infra.azure_datalake import AzureDataLakeClient
from source.infra.postgres import PostgresClient

class Factory:
    @staticmethod
    def get_adls_client() -> AzureDataLakeClient:
        return AzureDataLakeClient()

    @staticmethod
    def get_postgres_client(connect_str: str) -> PostgresClient:
        return PostgresClient(connect_str=connect_str)