from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.data_collection import fetch_hashtag_data
from src.data_extraction import extract_insights
from src.data_loading import save_processed_to_mongo
from src.data_transformation import process_data_for_analysis
# Default arguments for DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    "instagram_etl_pipeline",
    default_args=default_args,
    catchup=False,  # ✅ Avoid unnecessary backfilling
    schedule_interval="@once",
)

# Task 1: Fetch Data from API
fetch_task = PythonOperator(
    task_id="fetch_data",
    python_callable=fetch_hashtag_data,
    dag=dag,
)

# Task 2: Extract Insights from Data
extract_task = PythonOperator(
    task_id="extract_insights",
    python_callable=extract_insights,
    op_kwargs={"file_path": "{{ ti.xcom_pull(task_ids='fetch_data') }}"},
    dag=dag,
)

# Task 3: Process Data Directly from Extracted Insights File
process_task = PythonOperator(
    task_id="process_data_for_analysis",
    python_callable=process_data_for_analysis,
    op_kwargs={"file_path": "{{ ti.xcom_pull(task_ids='extract_insights') }}"},  # ✅ Pass extracted file path
    dag=dag,
)

# ✅ Step 4: Save Processed Data to MongoDB
save_processed_task = PythonOperator(
    task_id="save_processed_to_mongo",
    python_callable=save_processed_to_mongo,
    op_kwargs={
        "file_path": "{{ ti.xcom_pull(task_ids='process_data_for_analysis') }}"},
    dag=dag,
)

fetch_task >> extract_task >> process_task >> save_processed_task