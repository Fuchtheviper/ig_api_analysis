from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.data_collection import fetch_hashtag_data
from src.data_extraction import extract_insights
from src.data_loading import save_raw_to_mongo, load_raw_data_from_mongo
from src.data_transformation import clean_text, clean_emoji_and_long_text, translate_topic, process_data_for_analysis
from src.sentiment_analysis import get_sentiment_with_chatgpt, extract_sentiment
from src.topic_analysis import get_topic_with_deepseek, batch_topic_analysis
from src.data_loading import save_sentiment_to_mongo, save_topic_to_mongo

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

# Task 3: Save Raw Data to MongoDB
save_raw_task = PythonOperator(
    task_id="save_raw_to_mongo",
    python_callable=save_raw_to_mongo,
    op_kwargs={"file_path": "{{ ti.xcom_pull(task_ids='extract_insights') }}"},
    dag=dag,
)

# Task 4: Load Raw Data from MongoDB
load_raw_task = PythonOperator(
    task_id="load_raw_data_from_mongo",
    python_callable=load_raw_data_from_mongo,
    dag=dag,
)

# Task 5: Clean Text Data
#clean_text_task = PythonOperator(
#    task_id="clean_text",
#    python_callable=clean_text,
#    dag=dag,
#)

# Task 6: Sentiment Analysis
#sentiment_task = PythonOperator(
#    task_id="get_sentiment_with_chatgpt",
#    python_callable=get_sentiment_with_chatgpt,
#    dag=dag,
#)

# Task 7: Extract Sentiment from Response
#extract_sentiment_task = PythonOperator(
#    task_id="extract_sentiment",
#    python_callable=extract_sentiment,
#    dag=dag,
#)

# Task 8: Topic Analysis
#topic_task = PythonOperator(
#    task_id="get_topic_with_deepseek",
#    python_callable=get_topic_with_deepseek,
#    dag=dag,
#)

# Task 9: Batch Topic Analysis
#batch_topic_task = PythonOperator(
#    task_id="batch_topic_analysis",
#    python_callable=batch_topic_analysis,
#    dag=dag,
#)

# Task 10: Clean Emoji & Long Text from Topic
#clean_topic_task = PythonOperator(
#    task_id="clean_emoji_and_long_text",
#    python_callable=clean_emoji_and_long_text,
#    dag=dag,
#)

# Task 11: Translate Non-English Topic to English
#translate_task = PythonOperator(
#    task_id="translate_topic",
#    python_callable=translate_topic,
#    dag=dag,
#)

# Task 12: Process Data for Final Analysis
process_task = PythonOperator(
    task_id="process_data_for_analysis",
    python_callable=process_data_for_analysis,
    op_kwargs={"df": "{{ ti.xcom_pull(task_ids='load_raw_data_from_mongo') }}"},
    dag=dag,
)

# Task 13: Store Sentiment Results in MongoDB
store_sentiment_task = PythonOperator(
    task_id="save_sentiment_to_mongo",
    python_callable=save_sentiment_to_mongo,
    op_kwargs={"df": "{{ ti.xcom_pull(task_ids='process_data_for_analysis') }}"},
    dag=dag,
)

# Task 14: Store Topic Results in MongoDB
store_topic_task = PythonOperator(
    task_id="save_topic_to_mongo",
    python_callable=save_topic_to_mongo,
    op_kwargs={"df": "{{ ti.xcom_pull(task_ids='process_data_for_analysis') }}"},
    dag=dag,
)

# DAG Task Dependencies
fetch_task >> extract_task >> save_raw_task >> load_raw_task >> process_task >> [store_sentiment_task, store_topic_task]