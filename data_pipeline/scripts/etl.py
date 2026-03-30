import pandas as pd
from sqlalchemy import create_engine
import boto3
import os
from dotenv import load_dotenv
import time

load_dotenv("/opt/airflow/.env")

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")
)

bucket = os.getenv("BUCKET_NAME")


# STEP 1: EXTRACT
def extract_data():
    print("Extract step started")

    engine = create_engine(os.getenv("SUPABASE_DB_URL"))
    df = pd.read_sql("SELECT * FROM entries", engine)

    file_name = "/tmp/raw_data.csv"
    df.to_csv(file_name, index=False)

    s3.upload_file(file_name, bucket, "raw/data.csv")

    print("Raw data uploaded")
    time.sleep(5)


# STEP 2: TRANSFORM
def transform_data():
    print("Transform step started")

    obj = s3.get_object(Bucket=bucket, Key="raw/data.csv")
    df = pd.read_csv(obj['Body'])

    # Basic cleaning
    df = df.dropna()
    df['salary'] = df['salary'].astype(float)

    file_name = "/tmp/processed_data.csv"
    df.to_csv(file_name, index=False)

    print("Data transformed")
    time.sleep(5)


# STEP 3: LOAD
def load_processed_data():
    print("Load step started")

    file_name = "/tmp/processed_data.csv"

    s3.upload_file(file_name, bucket, "processed/data.csv")

    print("Processed data uploaded")