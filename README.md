# Case Técnico Data Architect iFood
## NYC Yellow Taxi Trip Records 2023

Pipeline de ingestão, transformação e análise dos dados de corridas de táxi em Nova York (janeiro a maio de 2023), desenvolvida como parte do processo seletivo para a vaga de Engenheiro de Dados no iFood.

## 1. Arquitetura

```
NYC TLC (fonte)
      ↓
Databricks: Landing Zone (Volume: workspace.nyc_taxi.landing_zone)
      ↓
Databricks PySpark: Transformação e limpeza
      ↓
Delta Table (workspace.nyc_taxi.yellow_trips)
      ↓
SQL: Análises
```

## 2. Estrutura do Repositório

```
case-ifood/
├── src/
│   ├── jobs/
│   │   └── nyc_taxi_case_job.json           # Definição do Job no Databricks
│   ├── old_gcp/                             # Pasta com a definição inicial do projeto
│   ├── databricks_ingestion_data_nb.ipynb   # Notebook de ingestão e transformação
│   ├── databricks_ingestion_data_script.py  # Script exportado do notebook
│   └── validation.py                        # Validações da tabela
├── analysis/
│   └── analysis.ipynb                       # Notebook com as análises e respostas
├── README.md
└── requirements.txt
```

## 3. Tecnologias Utilizadas

- **Databricks Community Edition:** ambiente de execução
- **PySpark:** transformação e limpeza dos dados
- **SQL:** análises e consultas

## 4. Instruções de Execução

### Pré-requisitos

- Conta no [Databricks Community Edition](https://community.cloud.databricks.com)
- Repositório linkado ao GitHub via Git folder

### 1. Configurar o ambiente no Databricks

Execute os comandos abaixo em uma célula SQL no Databricks para criar o schema e os volumes:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.nyc_taxi;
CREATE VOLUME IF NOT EXISTS workspace.nyc_taxi.landing_zone;
```

### 2. Upload dos arquivos para a Landing Zone

Faça o download dos arquivos parquet da fonte oficial [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page):

```
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet
```

Em seguida, faça o upload dos arquivos para o Volume criado anteriormente via **Catalog → workspace → nyc_taxi → landing_zone → Upload to this volume**.

### 3. Executar a pipeline

A pipeline pode ser executada de duas formas:

**Via Job:**
- Importe o arquivo `src/jobs/nyc_taxi_case_job.json` no Databricks
- Execute o job `nyc_taxi_case`: ele roda a ingestão dos dados e a validação em sequência

**Via notebook:**
- Abra o arquivo `src/databricks_ingestion_data_nb` no Databricks
- Clique em **Run all**
- Em seguida, abra o arquivo `src/validation` e clique em **Run all**

### 4. Consultar os dados

Após a execução, a tabela estará disponível para consulta via SQL:

```sql
SELECT * FROM workspace.nyc_taxi.yellow_trips;
```

## 5. Dados

| Campo                 | Tipo      | Descrição                      |
|-----------------------|-----------|--------------------------------|
| vendor_id             | bigint    | Código do fornecedor (1: Creative Mobile Technologies, 2: Curb Mobility, 6: Myle Technologies, 7: Helix) |
| passenger_count       | int       | Número de passageiros no veículo |
| total_amount          | double    | Valor total cobrado pela corrida |
| tpep_pickup_datetime  | timestamp | Data/hora de início da corrida   |
| tpep_dropoff_datetime | timestamp | Data/hora de fim da corrida      |

**Fonte:** [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)  
**Período:** Janeiro a maio de 2023  
**Total de registros:** Aproximadamente 16 milhões de corridas

## 6. Análises

### Pergunta 1: Média de valor total por mês

| Mês     | Média (USD) |
|---------|-------------|
| 2023-01 | 27.02       |
| 2023-02 | 26.90       |
| 2023-03 | 27.80       |
| 2023-04 | 28.27       |
| 2023-05 | 28.98       |

A média de valor total por corrida apresenta tendência de crescimento ao longo dos meses, com aumento de aproximadamente 7.6% de janeiro a maio. Fevereiro foi o único mês com queda, possivelmente relacionada ao menor número de dias.

### Pergunta 2: Média de passageiros por hora no mês de maio

| Hora | Média de passageiros |
|------|----------------------|
|   0 |                  1.41 |
|   1 |                  1.42 |
|   2 |                  1.44 |
|   3 |                  1.44 |
|   4 |                  1.39 |
|   5 |                  1.27 |
|   6 |                  1.24 |
|   7 |                  1.25 |
|   8 |                  1.27 |
|   9 |                  1.28 |
|  10 |                  1.32 |
|  11 |                  1.33 |
|  12 |                  1.35 |
|  13 |                  1.36 |
|  14 |                  1.36 |
|  15 |                  1.37 |
|  16 |                  1.37 |
|  17 |                  1.37 |
|  18 |                  1.36 |
|  19 |                  1.37 |
|  20 |                  1.38 |
|  21 |                   1.4 |
|  22 |                  1.41 |
|  23 |                  1.41 |

A média de passageiros por hora mantém-se estável entre **1.24 e 1.44 passageiros por corrida**. Os horários de madrugada (0h às 3h) apresentam as maiores médias, sugerindo corridas de grupos. Nos horários de rush (6h às 8h) a média cai, indicando predominância de corridas individuais.

## 7. Decisões Técnicas

- **Databricks Community Edition** foi escolhido por ser gratuito, já recomendado no enunciado e ter PySpark e Delta Lake nativos
- **PySpark** foi utilizado na etapa de transformação para padronizar tipos inconsistentes entre os arquivos mensais (ex: `passenger_count` variava entre `FLOAT` e `INT64`)

## 8. Estratégias Abandonadas

**GCP (BigQuery + Cloud Storage):** A solução foi inicialmente desenvolvida utilizando **Google Cloud Storage** como landing zone e **BigQuery** como camada de consumo, com scripts Python para ingestão e transformação dos dados. Apesar de funcional, a abordagem foi substituída pelo Databricks por ser a tecnologia recomendada no enunciado e por centralizar toda a pipeline em um único ambiente.

Os scripts da solução GCP estão disponíveis na pasta `src/old_gcp/` para referência.

**Pandas:** A biblioteca pandas foi considerada para a etapa de transformação dos dados por ser mais simples e familiar. No entanto, como é uma grande quantidade de dados e o case exigia o uso de **PySpark** em algum momento, a transformação foi implementada com PySpark, que também se mostrou mais adequado para lidar com as inconsistências de tipos entre os arquivos mensais.