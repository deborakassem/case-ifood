import requests
from src.old_gcp.config import BUCKET_NAME, GCS_FOLDER, BASE_URL, YEAR, MONTHS
from google.cloud import storage
from loguru import logger


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

    logger.info(f"[{month}/05] Baixando {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    logger.info(f"[{month}/05] Fazendo upload para gs://{BUCKET_NAME}/{destination}...")
    blob = bucket.blob(destination)
    blob.upload_from_file(response.raw, content_type="application/octet-stream")

    logger.info(f"[{month}/05] {filename} salvo com sucesso!")


if __name__ == "__main__":
    logger.info(f"Iniciando ingestão dos dados Yellow Taxi NYC {YEAR} para os meses {', '.join(MONTHS)}")
    for month in MONTHS:
        download_and_upload_data_to_gcs(month)
    logger.info("Ingestão dos dados concluída.")