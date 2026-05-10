# Este script foi exportado do notebook Databricks e contém a pipeline de ingestão
# dos dados de corridas de táxi de Nova York (Yellow Taxi Trip Records - 2023).

# Para executar, importe o arquivo no Databricks e rode as células na ordem.
# O ambiente de execução esperado é o Databricks com Unity Catalog habilitado.

# Estrutura da pipeline:
# 1. Criação do schema e volumes no Unity Catalog
# 2. Leitura dos arquivos parquet da landing zone
# 3. Transformação e padronização dos tipos com PySpark
# 4. Salvamento como Delta Table na camada de consumo

# ---------------------------------------------------------------------------------------
# Databricks notebook source
# MAGIC %sql
# MAGIC -- Cria o schema (dataset) 
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.nyc_taxi

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Cria os volumes de armazenamento dos dados brutos e de consumo no schema
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.nyc_taxi.landing_zone;
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.nyc_taxi.consumption_zone;

# COMMAND ----------

# Os arquivos foram inseridos na landing zone manualmente
# Verifica os arquivos na landing zone
display(dbutils.fs.ls("/Volumes/workspace/nyc_taxi/landing_zone/"))

# COMMAND ----------

# Define os diretórios da landing zone e da consumption zone
LANDING_PATH = "/Volumes/workspace/nyc_taxi/landing_zone/"
CONSUMPTION_PATH = "/Volumes/workspace/nyc_taxi/consumption_zone/"

# COMMAND ----------

from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

# Lê os arquivos parquet da landing zone e define o schema explicitamente das colunas necessárias para que não haja inconsistências nos tipos dos campos

# Lê cada arquivo separadamente
dfs = []
for month in ["01", "02", "03", "04", "05"]:
    path = f"{LANDING_PATH}yellow_tripdata_2023-{month}.parquet"
    df = spark.read.parquet(path)

    # Renomeia Airport_fee para airport_fee se necessário
    if "Airport_fee" in df.columns:
        df = df.withColumnRenamed("Airport_fee", "airport_fee")

    # Seleciona e casteia as colunas obrigatórias com os tipos corretos
    df = df.select(
        col("VendorID").cast("long"),
        col("passenger_count").cast("integer"),
        col("total_amount").cast("double"),
        col("tpep_pickup_datetime").cast("timestamp"),
        col("tpep_dropoff_datetime").cast("timestamp"),
    )
    dfs.append(df)

# Une todos os meses em um único DataFrame
df_final = reduce(DataFrame.union, dfs)

print(f"Total de linhas: {df_final.count():,}")
df_final.printSchema()

# COMMAND ----------

# Salvando os dados em uma tabela delta no catálogo
# Salva os dados na camada de consumo como Delta Table
df_final.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.nyc_taxi.yellow_trips")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consultando a tabela para validacão
# MAGIC SELECT * FROM workspace.nyc_taxi.yellow_trips LIMIT 10