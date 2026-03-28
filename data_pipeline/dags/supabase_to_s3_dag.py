import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 🔥 Add scripts folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Now import your function
from etl import upload_supabase_to_s3

with DAG(
    dag_id='supabase_to_s3_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@hourly',
    catchup=False
) as dag:

    task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_supabase_to_s3
    )