from pymongo import MongoClient, UpdateOne, errors
import logging
from pymongo.errors import BulkWriteError
import yaml
import pandas as pd
import json

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

MONGO_URI = config["MONGO_URI"]
DB_NAME = config["DB_NAME"]
COLLECTION_NAME = config["COLLECTION_NAME"]

# Save Data to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_raw_to_mongo(file_path):
    """
    Loads extracted insights from a JSON file and saves them to MongoDB.
    """
    try:
        # ✅ Read extracted insights from the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            all_insights = json.load(f)  # ✅ Convert JSON string into a Python dictionary

        if not isinstance(all_insights, list):  # ✅ Ensure it's a list of posts
            logging.error(f"Expected list but got {type(all_insights).__name__}")
            return None

        logging.info(f"Loaded {len(all_insights)} insights from file.")

        # ✅ Upsert data into MongoDB
        for doc in all_insights:
            doc.pop("_id", None)  # Remove `_id` to prevent conflicts
            filter_query = {"id": doc.get("id")}  # Ensure uniqueness
            update_query = {"$set": doc}
            collection.update_one(filter_query, update_query, upsert=True)

        logging.info("All new data upserted into MongoDB!")

    except BulkWriteError as bwe:
        logging.error("Bulk write error occurred during update operation.")
        logging.error(bwe.details)
        raise  # Raise for debugging

    except Exception as e:
        logging.error(f"Error saving to MongoDB: {str(e)}")
        raise  # Raise for debugging


# Function to load data from mongoDB
def load_raw_data_from_mongo():
    # Load Data from MongoDB
    data = list(collection.find({}, {"text": 1}))
    df = pd.DataFrame(data).drop(columns=["_id"], errors="ignore")
    return df

# Function to Save Sentiment Analysis Results
def save_sentiment_to_mongo(df):
    """
    Saves sentiment analysis results to MongoDB without using `bulk_write()`.
    """
    try:
        for _, row in df.iterrows():
            filter_query = {"text": row["text"]}
            update_query = {"$set": {"sentiment": row["sentiment"]}}
            collection.update_one(filter_query, update_query, upsert=True)

        logging.info("Sentiment Analysis Results Saved to MongoDB.")

    except BulkWriteError as bwe:
        logging.error("Bulk write error occurred during update operation.")
        logging.error(bwe.details)
        raise  # Raise error for visibility

    except Exception as e:
        logging.error(f"Error saving sentiment to MongoDB: {str(e)}")
        raise  # Raise error to prevent silent failures

# Function to Save Topic Analysis Results
def save_topic_to_mongo(df):
    """
    Saves topic analysis results to MongoDB without using `bulk_write()`, using `update_one()` for each record.
    """
    try:
        for _, row in df.iterrows():
            filter_query = {"text": row["text"]}
            update_query = {"$set": {"topic": row["topic"]}}
            collection.update_one(filter_query, update_query, upsert=True)

        logging.info("Topic Analysis Results Saved to MongoDB.")

    except BulkWriteError as bwe:
        logging.error("Bulk write error occurred during update operation.")
        logging.error(bwe.details)
        raise  # Raise error for visibility

    except Exception as e:
        logging.error(f"Error saving topic to MongoDB: {str(e)}")
        raise  # Raise error to prevent silent failures