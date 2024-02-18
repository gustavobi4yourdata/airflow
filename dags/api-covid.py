import json
import os
import shutil
from datetime import datetime, timedelta

from airflow.decorators import dag, task

import requests
import logging

from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

S3_CONN_ID = "aws_default"
API = "https://qd28tcd6b5.execute-api.sa-east-1.amazonaws.com/prod/PortalMunicipio"

data_hora_atual = datetime.now()
file_data_hora = data_hora_atual.strftime("%Y_%m_%d")

default_args = {
    "owner": "Gustavo Souza",
    "retries": 1,
    "retry_delay": 0,
}

@dag(
    dag_id="api-covid",    
    schedule=None,
    start_date=datetime(2024,2,1),
    tags=['api', 'minio', 'taskflowAPI'],
    default_args=default_args,
    dagrun_timeout=timedelta(minutes=5),
    catchup=True  
)
def extrtact_api_covid():

    @task
    def extract_bitcoin_price(**kwargs):
        
        os.mkdir(f'/usr/local/airflow/include/dados_api/')
        response = requests.get(API)
        data = response.json()        
        print(data)

        # requests.get(API).json()
        json.dump(data, open(f'/usr/local/airflow/include/dados_api/covid_{file_data_hora}.json', 'x'))

    @task(multiple_outputs=True)
    def process_data():

        hook = S3Hook(aws_conn_id=S3_CONN_ID)
        files = os.listdir(f'/usr/local/airflow/include/dados_api')
        for file in files:
            hook.loadfile(
                filename=f'/usr/local/airflow/include/dados_api/{file}',
                key=f'covid/{file}',
                bucket_name='landing',
                replace=True
        )
        # return {file}

    @task(trigger_rule='all_done')
    def limpa_arquivos():
        shutil.rmtree(f'/usr/local/airflow/include/dados_api/', ignore_errors=True)

    extract_bitcoin_price() >> process_data() >>limpa_arquivos()

dag = extrtact_api_covid()