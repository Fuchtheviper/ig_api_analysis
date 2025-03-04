from pymongo import MongoClient
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

def save_processed_to_mongo(file_path):
    """
    Loads processed data from a JSON file and saves it to MongoDB.
    """
    try:
        # ✅ Read processed data from the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            processed_data = json.load(f)

        if not isinstance(processed_data, list):  # ✅ Ensure it's a list of posts
            logging.error(f"Expected list but got {type(processed_data).__name__}")
            return None

        logging.info(f"Loaded {len(processed_data)} processed records from file.")

        # ✅ Upsert data into MongoDB
        for doc in processed_data:
            doc.pop("_id", None)  # ✅ Remove `_id` to prevent conflicts
            filter_query = {"id": doc.get("id")}  # ✅ Ensure uniqueness
            update_query = {"$set": doc}
            collection.update_one(filter_query, update_query, upsert=True)

        logging.info("Processed data successfully upserted into MongoDB!")

    except BulkWriteError as bwe:
        logging.error("Bulk write error occurred during update operation.")
        logging.error(bwe.details)
        raise  # ✅ Raise for debugging

    except Exception as e:
        logging.error(f"Error saving to MongoDB: {str(e)}")
        raise  # ✅ Raise for debugging