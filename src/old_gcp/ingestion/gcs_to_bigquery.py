# # from loguru import logger
# # import yaml
# # from src.config import BUCKET_NAME, DATASET_ID, GCS_FOLDER, YEAR, MONTHS, PROJECT_ID, TABLE_SCHEMA_PATH
# # from google.cloud import bigquery
# # from pathlib import Path


# # # Iniciando o cliente do Google Cloud BigQuery
# # client = bigquery.Client(project=PROJECT_ID)


# # def load_config(path: Path) -> dict:
# #     """"
# #     Função para carregar as configurações do YAML com o schema da tabela.
    
# #     Parâmetros
# #     ----------
# #     path: Path
# #         Caminho para o arquivo.

# #     Retornos
# #     --------
# #     dict
# #         Dicionário com as configurações da tabela.
# #     """

# #     with open(path, "r") as f:
# #         return yaml.safe_load(f)


# # def build_bq_schema(fields: list) -> list[bigquery.SchemaField]:
# #     """"
# #     Função para construir o schema do BigQuery a partir da configuração do YAML.
    
# #     Parâmetros
# #     ----------
# #     fields: list
# #         Lista de dicionários com as definições dos campos (nome, tipo, descrição, etc).
    
# #     Retornos
# #     --------
# #     list[bigquery.SchemaField]
# #         Lista de campos do schema do BigQuery.
# #     """

# #     schema = []
# #     for field in fields:
# #         schema.append(
# #             bigquery.SchemaField(
# #                 name=field["name"],
# #                 field_type=field["type"],
# #                 mode=field.get("mode", "NULLABLE"),
# #                 description=field.get("description", ""),
# #             )
# #         )
# #     return schema


# # config = load_config(TABLE_SCHEMA_PATH)
# # for field in config["schema"]:
# #     if field["name"] == "passenger_count":
# #         print(field)


# # def create_table(config: dict) -> str:
# #     """"
# #     Função para criar a tabela no BigQuery com base nas configurações do YAML.
    
# #     Parâmetros
# #     ----------
# #     config: dict
# #         Dicionário com as configurações da tabela (nome, schema, partição, cluster, descrição, etc).
        
# #     Retornos
# #     --------
# #     str
# #         ID da tabela criada.
# #     """

# #     table_id = f"{PROJECT_ID}.{DATASET_ID}.{config['table_name']}"

# #     schema = build_bq_schema(config["schema"])

# #     # Particionamento da tabela
# #     partitioning = bigquery.TimePartitioning(
# #         type_=bigquery.TimePartitioningType.DAY,
# #         field=config["partitioning_field"],
# #     )

# #     # Clusters da tabela
# #     clustering_fields = [f.strip() for f in config["clustering"].split(",")]

# #     table = bigquery.Table(table_id, schema=schema)
# #     table.description = config.get("table_description", "")
# #     table.time_partitioning = partitioning
# #     table.clustering_fields = clustering_fields

# #     # Cria a tabela (ignora se já existir)
# #     table = client.create_table(table, exists_ok=True)
# #     logger.info(f"Tabela {table_id} criada com sucesso.")

# #     return table_id


# # def load_parquet_data_into_bigquery_table(table_id: str, month: str) -> None:
# #     """"
# #     Função para carregar os dados do Parquet do Google Cloud Storage para a tabela do BigQuery.
    
# #     Parâmetros
# #     ----------
# #     table_id: str
# #         ID da tabela de destino no BigQuery.
# #     month: str
# #         Mês para o qual carregar os dados (formato: "MM").    
# #     """
    
# #     filename = f"yellow_tripdata_{YEAR}-{month}.parquet"
# #     gcs_uri = f"gs://{BUCKET_NAME}/{GCS_FOLDER}/{filename}"

# #     logger.info(f"[{month}/05] Carregando {filename} para o BigQuery...")

# #     # job_config = bigquery.LoadJobConfig(
# #     #     source_format=bigquery.SourceFormat.PARQUET,
# #     #     write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
# #     #     autodetect=False,  # usa o schema definido no YAML
# #     # )
# #     job_config = bigquery.LoadJobConfig(
# #         source_format=bigquery.SourceFormat.PARQUET,
# #         write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
# #         autodetect=True,
# #     )

# #     load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
# #     load_job.result()

# #     logger.info(f"[{month}/05] {filename} carregado com sucesso.")


# # if __name__ == "__main__":
# #     logger.info("Iniciando construção da tabela no BigQuery...")

# #     config = load_config(TABLE_SCHEMA_PATH)
# #     table_id = create_table(config)

# #     for month in MONTHS:
# #         load_parquet_data_into_bigquery_table(table_id, month)

# #     table = client.get_table(table_id)
# #     logger.info(f"Tabela {table.full_table_id} populada! Total de linhas: {table.num_rows:,}")




# # # import pandas as pd
# # # df1 = pd.read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet')
# # # df2 = pd.read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet')
# # # print('Jan:', df1['passenger_count'].dtype)
# # # print('Fev:', df2['passenger_count'].dtype)



# import pyarrow.parquet as pq
# for month in ['01', '02', '03', '04', '05']:
#     f = pq.read_schema(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-{month}.parquet')
#     print(f'Mês {month}:', f.field('passenger_count').type)


import pyarrow.parquet as pq
import gcsfs

fs = gcsfs.GCSFileSystem()
for month in ['01', '02', '03', '04', '05']:
    path = f'case-ifood-landing-zone/raw/yellow_taxi/yellow_tripdata_2023-{month}.parquet'
    schema = pq.read_schema(path, filesystem=fs)
    print(f'Mês {month}:', schema.field('passenger_count').type)
