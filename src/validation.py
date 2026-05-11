# Databricks notebook source
# Este script contém as validações da tabela yellow_trips após a ingestão dos dados.

import logging
from datetime import date
from pyspark.sql import functions as f

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

TABLE_NAME = "workspace.nyc_taxi.yellow_trips"
EXPECTED_COLUMNS = [
    "vendor_id",
    "passenger_count",
    "total_amount",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df_nyc_taxi_data = spark.table(TABLE_NAME)

#  1. Valida se a tabela não está vazia
assert not df_nyc_taxi_data.isEmpty(), "A tabela yellow_trips está vazia!"

# 2. Valida se todas as colunas obrigatórias estão presentes
missing_columns = [col for col in EXPECTED_COLUMNS if col not in df_nyc_taxi_data.columns]
assert not missing_columns, f"Colunas ausentes: {missing_columns}"

# 3. Valida os tipos das colunas
expected_types = {
    "vendor_id": "bigint",
    "passenger_count": "int",
    "total_amount": "double",
    "tpep_pickup_datetime": "timestamp",
    "tpep_dropoff_datetime": "timestamp",
}
actual_types = {field.name: field.dataType.simpleString() for field in df_nyc_taxi_data.schema.fields}
for col, expected in expected_types.items():
    assert actual_types[col] == expected, f"Tipo incorreto para {col}: esperado {expected}, encontrado {actual_types[col]}"

# 4. Valida se há valores nulos
columns = [
    "vendor_id",
    "total_amount",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]
for col in columns:
    null_count = df_nyc_taxi_data.filter(f.col(col).isNull()).count()
    assert null_count == 0, f"Coluna {col} possui {null_count:,} valores nulos."

# 5. Valida se as datas estão dentro do período esperado
min_date, max_date = df_nyc_taxi_data.agg(
    f.min("tpep_pickup_datetime"),
    f.max("tpep_pickup_datetime")
).first()

assert min_date.date() >= date(2023, 1, 1), f"Data mínima fora do período esperado: {min_date}"
assert max_date.date() <= date(2023, 5, 31), f"Data máxima fora do período esperado: {max_date}"

logger.info("Todas as validações passaram com sucesso!")
