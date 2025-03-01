from pymongo import MongoClient, UpdateOne, errors
import logging
from pymongo.errors import BulkWriteError
import yaml
import pandas as pd

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

MONGO_URI = config["MONGO_URI"]
DB_NAME = config["DB_NAME"]
COLLECTION_NAME = config["COLLECTION_NAME"]

# Save Data to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_raw_to_mongo(all_insights):
    """
    Saves raw data to MongoDB without using `bulk_write()`, using `update_one()` for each record.
    """
    try:
        all_data = [post for insights in all_insights.values() for post in insights]

        for doc in all_data:
            doc.pop("_id", None)  # Remove `_id` to prevent conflicts

        logging.info(f"Attempting to insert {len(all_data)} documents into MongoDB.")

        for doc in all_data:
            filter_query = {"id": doc["id"]}  # Ensure uniqueness based on 'id'
            update_query = {"$set": doc}
            collection.update_one(filter_query, update_query, upsert=True)

        logging.info("All new data upserted into MongoDB!")

    except BulkWriteError as bwe:
        logging.error("Bulk write error occurred during update operation.")
        logging.error(bwe.details)
        raise  # Ensure the error is raised for debugging

    except Exception as e:
        logging.error(f"Error saving to MongoDB: {str(e)}")
        raise  # Raise error for visibility


# Function to load data from mongoDB
def load_raw_data_from_mongo():
    # Load Data from MongoDB
    data = list(collection.find({}, {"text": 1}))
    df = pd.DataFrame(data)
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