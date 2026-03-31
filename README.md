# 📊 Automated Survey Data Pipeline & Analytics Platform

An end-to-end data engineering project that collects survey data from a web application, processes it through an automated pipeline, and visualizes insights using Power BI.

---

## 🚀 Project Overview

This project demonstrates a modern data engineering workflow:

- Data is collected from a web-based survey application (HTML, CSS, JS, FastAPI)
- Stored in Supabase (PostgreSQL)
- Extracted and processed using Apache Airflow
- Stored in Amazon S3 (Data Lake)
- Queried using Amazon Athena
- Visualized in Power BI using ODBC connection

---

## 🏗️ Architecture
Frontend (HTML/CSS/JS + FastAPI)
↓
Supabase (PostgreSQL)
↓
Apache Airflow (ETL Pipeline)
↓
Amazon S3 (Raw + Processed Data)
↓
Amazon Athena (SQL Queries)
↓
Power BI (Dashboard)


---

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Orchestration**: Apache Airflow (Docker)
- **Cloud Storage**: Amazon S3
- **Query Engine**: Amazon Athena
- **Visualization**: Power BI (ODBC)
- **Languages**: Python (Pandas, SQLAlchemy, Boto3)

---

## ⚙️ Features

- Automated data ingestion using Airflow DAGs
- Multi-stage ETL pipeline (Extract, Transform, Load)
- Data cleaning and preprocessing using Pandas
- Storage of raw and processed data in S3
- SQL-based querying using Athena
- Interactive dashboards in Power BI
- Secure credential management using `.env`

---

## 📂 Project Structure
data_pipeline/
│
├── dags/ # Airflow DAG definitions
├── scripts/ # ETL scripts
├── docker-compose.yaml # Airflow setup
├── requirements.txt
├── .env # Environment variables (not committed)
└── README.md


---

## 🔄 Pipeline Workflow

1. **Extract**
   - Fetch data from Supabase using SQLAlchemy

2. **Transform**
   - Clean data using Pandas

3. **Load**
   - Store raw data in S3 (raw layer)
   - Store processed data in S3 (processed layer)

4. **Catalog**
   - AWS Glue Crawler automatically infers schema and updates the Data Catalog

5. **Query**
   - Amazon Athena queries data using Glue Data Catalog

6. **Visualize**
   - Power BI connects to Athena via ODBC
---

## 📊 Sample Use Cases

- Analyze average salary by profession
- Distribution of users across cities
- Age-based demographic analysis
- Survey trend insights

---

## 🔐 Security

- Credentials managed using `.env` file
- IAM users used for controlled AWS access
- Separation of ingestion and analytics roles

---

## 🚀 Future Enhancements

- Convert CSV to Parquet for optimized queries
- Implement incremental data loading
- Add partitioning for better performance
- Integrate Apache Spark for large-scale processing
- Automate Power BI refresh

---

## 🎯 Resume Impact

This project demonstrates:
- End-to-end data pipeline design
- Cloud data engineering (AWS)
- Workflow orchestration (Airflow)
- Data visualization (Power BI)
- Real-world system integration

---

## 👤 Author

**Maneesh Karlapudi**

- GitHub: https://github.com/maneesh6531
- LinkedIn: https://www.linkedin.com/in/maneeshkarlapudi

---

## ⭐ Acknowledgements

This project was built as part of hands-on learning in data engineering and cloud-based analytics systems.
