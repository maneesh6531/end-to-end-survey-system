import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Add scripts folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from etl import extract_data, transform_data, load_processed_data

with DAG(
    dag_id='full_data_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract_to_s3_raw',
        python_callable=extract_data
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load = PythonOperator(
        task_id='load_to_s3_processed',
        python_callable=load_processed_data
    )

    #  Pipeline order
    extract >> transform >> load