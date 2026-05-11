# Case Técnico Data Architect iFood
## NYC Yellow Taxi Trip Records 2023

Este repositório armazena o código com a transformação e análise dos dados de corridas de táxi em Nova York, de janeiro a maio de 2023, solicitado como parte do processo seletivo para a vaga de Engenheiro(a) de Dados Sênior no iFood.

## 1. Estrutura do Repositório

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

## 2. Tecnologias Utilizadas

- **Databricks Community Edition:** ambiente de execução
- **PySpark:** transformação e limpeza dos dados
- **SQL:** criação do ambiente, documentação da tabela e análises

## 3. Instruções de Execução

### Pré-requisitos

- Conta no [Databricks Community Edition](https://community.cloud.databricks.com)
- Repositório linkado ao GitHub via Git folder

### 1. Configurar o ambiente no Databricks

Execute os comandos abaixo no Databricks para criar o schema e os volumes necessários:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.nyc_taxi;
CREATE VOLUME IF NOT EXISTS workspace.nyc_taxi.landing_zone;
```

### 2. Upload dos arquivos para a Landing Zone

Faça o download dos arquivos parquet da fonte oficial [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) para o Volume criado anteriormente:

```
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet
```

### 3. Executar a pipeline

A pipeline pode ser executada de duas formas:

**Via Job:**
- Importe o arquivo `src/jobs/nyc_taxi_case_job.json`
- Execute o job `nyc_taxi_case`

**Via notebook:**
- Abra o arquivo `src/databricks_ingestion_data_nb`
- Clique em **Run all**
- Em seguida, abra o arquivo `src/validation` e clique em **Run all**

### 4. Consultar os dados

Após a execução, a tabela estará disponível para consulta:

```sql
SELECT * FROM workspace.nyc_taxi.yellow_trips;
```

## 4. Dados

| Campo                 | Tipo      | Descrição                      |
|-----------------------|-----------|--------------------------------|
| `vendor_id`             | bigint    | Código do fornecedor (1: Creative Mobile Technologies, 2: Curb Mobility, 6: Myle Technologies, 7: Helix). |
| `passenger_count`       | int       | Número de passageiros no veículo. |
| `total_amount`          | double    | Valor total cobrado pela corrida. |
| `tpep_pickup_datetime`  | timestamp | Data/hora de início da corrida.   |
| `tpep_dropoff_datetime` | timestamp | Data/hora de fim da corrida.      |

**Fonte:** [NYC Taxi & Limousine Commission - TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) \
**Dicionário:** [Data Dictionary – Yellow Taxi Trip Records](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf) \
**Período:** Janeiro a maio de 2023

## 5. Análises

**Obs.:** Considerando que os registros com as condições abaixo possam ser erros de preenchimento ou corridas canceladas, essas observações foram desconsiderados nestas análise, pois podem distorcer o resultado.
- `passenger_count` nulo ou igual a zero;
- `total_amount` menor ou igual a zero;
- `tpep_pickup_datetime` < `tpep_dropoff_datetime`;
- corridas com duração maior que 3 horas.

### Pergunta 1: Média de valor total por mês

| Mês     | Média (USD) |
|---------|-------------|
| 2023-01 | 27.46       |
| 2023-02 | 27.36       |
| 2023-03 | 28.28       |
| 2023-04 | 28.78       |
| 2023-05 | 29.46       |

A média de valor total por corrida apresenta tendência de crescimento ao longo dos meses, com aumento de aproximadamente 7.3% de janeiro a maio. Fevereiro foi o único mês com queda, possivelmente relacionada ao menor número de dias.

### Pergunta 2: Média de passageiros por hora no mês de maio

| Hora | Média de passageiros |
|------|----------------------|
|    0 |                 1.43 |
|    1 |                 1.44 |
|    2 |                 1.46 |
|    3 |                 1.45 |
|    4 |                 1.41 |
|    5 |                 1.28 |
|    6 |                 1.26 |
|    7 |                 1.28 |
|    8 |                 1.30 |
|    9 |                 1.31 |
|   10 |                 1.35 |
|   11 |                 1.36 |
|   12 |                 1.38 |
|   13 |                 1.39 |
|   14 |                 1.39 |
|   15 |                 1.40 |
|   16 |                 1.40 |
|   17 |                 1.39 |
|   18 |                 1.38 |
|   19 |                 1.39 |
|   20 |                 1.40 |
|   21 |                 1.42 |
|   22 |                 1.43 |
|   23 |                 1.42 |

A média de passageiros por hora se manteve entre **1.26 e 1.46**. Os horários de madrugada (0h às 3h) apresentaram maiores médias, sugerindo corridas em grupos maiores de pessoas. Nos horários da manhã (6h às 8h) a média caiu, o que pode indicar predominância de corridas individuais à trabalho.

## 6. Estratégias Abandonadas

**GCP (BigQuery + Cloud Storage):** A solução foi inicialmente desenvolvida utilizando **Google Cloud Storage** como landing zone e **BigQuery** como camada de consumo, com scripts Python para ingestão e transformação dos dados. Apesar de funcional, a abordagem foi substituída pelo Databricks por ser a tecnologia recomendada. Os scripts iniciais da solução GCP estão disponíveis na pasta `src/old_gcp/`.

**Pandas:** A biblioteca pandas foi considerada para a etapa de transformação dos dados por ser mais simples e familiar. No entanto, como se trata de uma grande quantidade de dados e o case exigia o uso de **PySpark** em algum momento, a transformação foi implementada com PySpark, que também se mostrou mais adequado para lidar com tipos inconsistentes dos dados (por ex: `passenger_count` variava entre `FLOAT` e `INT64` nos arquivos).