import pandas as pd
from sqlalchemy import create_engine
import boto3
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv("/opt/airflow/.env")
def upload_supabase_to_s3():
    print("🚀 Starting job...")

    db_url = os.getenv("SUPABASE_DB_URL")
    print("DB URL loaded:", db_url is not None)

    engine = create_engine(db_url)

    print("📥 Reading from database...")
    df = pd.read_sql("SELECT * FROM entries", engine)

    print("Rows fetched:", len(df))

    file_name = "data.csv"
    df.to_csv(file_name, index=False)
    print("💾 CSV saved")

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    print("☁️ Uploading to S3...")
    print("BUCKET:", os.getenv("BUCKET_NAME"))
    s3.upload_file(file_name, os.getenv("BUCKET_NAME"), "raw/data.csv")

    print("✅ Uploaded to S3")

