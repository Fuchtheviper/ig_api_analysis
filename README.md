# 📷 Instagram ETL Data Pipeline
🚀 **An end-to-end data pipeline for extracting, analyzing, and storing Instagram hashtag data using Airflow, MongoDB, and DeepSeek API.**

## 📌 Project Overview
This project automates **data extraction, sentiment analysis, and topic classification** from Instagram hashtags. It is **built on Airflow** and **designed for scalability** using **Docker & MongoDB**.

### 🎯 Key Features
✅ **Fully Automated Workflow** → Uses **Airflow** to schedule & process Instagram data.  
✅ **Efficient Storage Handling** → Uses **temporary JSON storage** to optimize data transfer.  
✅ **Sentiment Analysis** → Uses **OpenAI GPT API** to classify posts as **Positive, Neutral, or Negative**.  
✅ **Topic Classification** → Uses **DeepSeek API** to categorize post topics dynamically.  
✅ **Scalable & Modular** → Can be expanded to **analyze multiple social media sources**.

## 📌 How It Works

This pipeline follows the **ETL (Extract, Transform, Load) workflow**:

1️⃣ **Extract**: Fetches Instagram hashtag data from the API.  
2️⃣ **Transform**: Cleans data, analyzes sentiment, and classifies topics.  
3️⃣ **Load**: Saves processed data to MongoDB for further analysis.

## Setup & Installation
Remark : Install Airflow, MongoDB and Docker on your own
Install Dependencies
- pip install -r requirements.txt
Start the Infrastructure (Airflow & MongoDB)
- docker-compose up -d --build

## Access Airflow UI
- URL: http://localhost:8080
- Username: admin
- Password: "Check in airflow-tainer volumn in docker"

## Run the DAG
- Go to DAGs → instagram_etl_pipeline
- Click "Trigger DAG"
- Monitor DAG execution

## Verify Processed Data in MongoDB
Option 1 Using Mongo Shell
- docker exec -it mongodb-container mongosh
- use instagram_data
- db.posts.find().pretty()

Option 2 Using MongoDB Compass
- Connect to MongoDB  URI: mongodb://localhost:27017/
- View the posts collection
