# Google Cloud Storage
BUCKET_NAME = "case-ifood-landing-zone"
GCS_FOLDER = "raw/yellow_taxi"

# Google Cloud BigQuery
PROJECT_ID = "case-ifood-495822"
DATASET_ID = "nyc_taxi"
TABLE_NAME = "tb_yellow_tripdata_2023"

# Tabela de destino no BigQuery
TABLE_SCHEMA_PATH = "src/tables/tb_yellow_tripdata_2023.yaml"

# Fonte dos dados Yellow Taxi NYC
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
YEAR = "2023"
MONTHS = ["01", "02", "03", "04", "05"]

