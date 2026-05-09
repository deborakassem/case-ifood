import requests
from config import BUCKET_NAME, GCS_FOLDER, BASE_URL, YEAR, MONTHS
from google.cloud import storage

# Configurações do Google Cloud Storage
BUCKET_NAME = "case-ifood-landing-zone"
GCS_FOLDER = "raw/yellow_taxi"
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
MONTHS = ["01", "02", "03", "04", "05"]
YEAR = "2023"

# Iniciando o cliente do Google Cloud Storage
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)


def download_and_upload_data_to_gcs(month: str) -> None:
    """"
    Função que faz o download dos dados do Yellow Taxi para um mês específico e os envia para o Google Cloud Storage.
    
    Parâmetros
    ----------
    month: str
        O mês para o qual baixar os dados (formato: "MM").        
    """

    filename = f"yellow_tripdata_{YEAR}-{month}.parquet"
    url = f"{BASE_URL}/{filename}"
    destination = f"{GCS_FOLDER}/{filename}"

    print(f"[{month}/05] Baixando {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    print(f"[{month}/05] Fazendo upload para gs://{BUCKET_NAME}/{destination}...")
    blob = bucket.blob(destination)
    blob.upload_from_file(response.raw, content_type="application/octet-stream")

    print(f"[{month}/05] {filename} salvo com sucesso!\n")


if __name__ == "__main__":
    print(f"Iniciando ingestão dos dados Yellow Taxi NYC {YEAR} para os meses {', '.join(MONTHS)}\n")
    for month in MONTHS:
        download_and_upload_data_to_gcs(month)
    print("Ingestão dos dados concluída.")