import json
import os
import shutil
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


POSTGRES_CONN_ID = "DWDB"
S3_CONN_ID = "aws_default"
BCB_CONN_ID = "BCB"

data_hora_atual = datetime.now()
file_data_hora = data_hora_atual.strftime("%Y_%m_%d")

default_args = {
    "owner": "Gustavo Souza",
    "retries": 1,
    "retry_delay": 0,
}

@dag(
    dag_id="extract-informacoes-api-bcb",
    # schedule_interval='@daily',
    schedule=None,
    start_date=datetime(2024,2,1),
    tags=['api', 'minio', 'taskflowAPI'],
    default_args=default_args,
    catchup=True  
)

def extract_informacoes_api():

    init = EmptyOperator(task_id="init")
    finish = EmptyOperator(task_id="finish")

    @task
    def ler_api():
        hook = HttpHook(method='GET', http_conn_id=BCB_CONN_ID)        

        pagina = 1        
        os.mkdir(f'/usr/local/airflow/include/dados/')

        while pagina <= 25:
            response = hook.run(endpoint=f'informacoes_diarias?$top=1000&$skip={pagina}&$format=json')
                        
            if response.status_code != 200:
                raise Exception('Erro ao ler API')
            data = response.json()
            data = data['value']           
                        
            if len(data) == 0:
                break

            json.dump(data, open(f'/usr/local/airflow/include/dados/informacoes_{pagina}_{file_data_hora}.json', 'x'))
            pagina += 1

    @task
    def envia_s3():
        hook = S3Hook(aws_conn_id=S3_CONN_ID)
        files = os.listdir(f'/usr/local/airflow/include/dados')
        for file in files:
            print(f'Enviando arquivo {file} para o S3')
            hook.load_file(
                filename=f'/usr/local/airflow/include/dados/{file}',
                key=f'informacoes/{file}',
                bucket_name='landing',
                replace=True
        )

    @task(trigger_rule='all_done')
    def limpa_arquivos():
        shutil.rmtree(f'/usr/local/airflow/include/dados/', ignore_errors=True)

    init >> ler_api() >> envia_s3() >> limpa_arquivos() >> finish
    

dag = extract_informacoes_api()

