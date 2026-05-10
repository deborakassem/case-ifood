# Databricks notebook source

# Este script foi exportado do notebook Databricks e contém a pipeline de ingestão
# dos dados de corridas de táxi de Nova York (Yellow Taxi Trip Records - 2023).

# Para executar, importe o arquivo no Databricks e rode as células na ordem.
# O ambiente de execução esperado é o Databricks com Unity Catalog habilitado.

# Estrutura da pipeline:
# 1. Criação do schema e volumes no Unity Catalog
# 2. Leitura dos arquivos parquet da landing zone
# 3. Transformação e padronização dos tipos com PySpark
# 4. Salvamento como Delta Table na camada de consumo

# ------------------------------------------------------------------------------------

# MAGIC %sql
# MAGIC -- Cria o schema (dataset)
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.nyc_taxi

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Cria os volumes de armazenamento dos dados brutos
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.nyc_taxi.landing_zone;

# COMMAND ----------

# Os arquivos foram inseridos na landing zone manualmente
# Verifica os arquivos na landing zone
display(dbutils.fs.ls("/Volumes/workspace/nyc_taxi/landing_zone/"))

# COMMAND ----------

from pyspark.sql import functions as f
from pyspark.sql import types as t

# Lê os arquivos parquet da landing zone e define o schema explicitamente das colunas necessárias para que não haja inconsistências nos tipos dos campos

LANDING_PATH = "/Volumes/workspace/nyc_taxi/landing_zone/"

df_final = None

for month in ["01", "02", "03", "04", "05"]:
    path = f"{LANDING_PATH}yellow_tripdata_2023-{month}.parquet"
    df = spark.read.parquet(path)
    df = df.select(
        f.col("VendorID").cast(t.LongType()).alias("vendor_id"),
        f.col("passenger_count").cast(t.IntegerType()),
        f.col("total_amount").cast(t.DoubleType()),
        f.col("tpep_pickup_datetime").cast(t.TimestampType()),
        f.col("tpep_dropoff_datetime").cast(t.TimestampType()),
    )

    if df_final is None:
        df_final = df
    else:
        df_final = df_final.union(df)
    
df_final = df_final.filter(
    (f.col("tpep_pickup_datetime") >= "2023-01-01") &
    (f.col("tpep_pickup_datetime") <= "2023-05-31")
)

print(f"Total de linhas: {df_final.count():,}")
df_final.printSchema()

# COMMAND ----------

# Salva os arquivos como Delta Table no catálogo
df_final.write.format("delta").mode("overwrite").saveAsTable("workspace.nyc_taxi.yellow_trips")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consultando a tabela para validacão
# MAGIC SELECT
# MAGIC   *
# MAGIC FROM
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Adiciona descrição da tabela
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC SET TBLPROPERTIES
# MAGIC   ('comment' = 'Tabela com dados de corridas de táxi em Nova York para o ano de 2023.');
# MAGIC
# MAGIC -- Adiciona descrição das colunas
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC ALTER COLUMN
# MAGIC   vendor_id
# MAGIC   COMMENT 'Código do fornecedor (1: Creative Mobile Technologies, 2: Curb Mobility, 6: Myle Technologies, 7: Helix).';
# MAGIC
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC ALTER COLUMN
# MAGIC   passenger_count
# MAGIC   COMMENT 'Número de passageiros no veículo.';
# MAGIC
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC ALTER COLUMN
# MAGIC   total_amount
# MAGIC   COMMENT 'Valor total cobrado do passageiro.';
# MAGIC
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC ALTER COLUMN
# MAGIC   tpep_pickup_datetime
# MAGIC   COMMENT 'Data e hora em que o taxímetro foi acionado.';
# MAGIC
# MAGIC ALTER TABLE
# MAGIC   workspace.nyc_taxi.yellow_trips
# MAGIC ALTER COLUMN
# MAGIC   tpep_dropoff_datetime
# MAGIC   COMMENT 'Data e hora em que o taxímetro foi desligado.';