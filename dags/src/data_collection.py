import logging
import time
import requests
import yaml
import sys
import json
import os

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

INSTAGRAM_API_URL = config["INSTAGRAM_API_URL"]
HEADERS = {
    "x-rapidapi-key": config["RAPIDAPI_KEY"],
    "x-rapidapi-host": config["RAPIDAPI_HOST"],
}
HASHTAGS = config["HASHTAGS"]

# Function to Fetch Data for Hashtags
def fetch_hashtag_data():
    """Fetches Instagram hashtag data and saves it as a JSON file to avoid XCom truncation."""
    all_items = []
    
    try:
        for hashtag in HASHTAGS:
            response = requests.get(INSTAGRAM_API_URL, headers=HEADERS, params={"hashtag": hashtag})
            response.raise_for_status()

            # ✅ Log raw response size
            response_text = response.text
            logging.info(f"Raw API Response Length for {hashtag}: {len(response_text)} characters")

            # ✅ Ensure response is valid JSON
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON Decode Error for {hashtag}: {e}")
                continue  # Skip this hashtag if the response is invalid

            data = response_json.get("data", {}).get("items", [])

            # ✅ Ensure `data` is correctly formatted
            if isinstance(data, dict):
                data = list(data.values())

            if isinstance(data, list):
                all_items.extend(data)
            else:
                logging.error(f"Unexpected data type for hashtag {hashtag}: {type(data).__name__}")

    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None  # ✅ Ensure Airflow handles None gracefully

    # ✅ Save Data to a Temporary JSON File
    temp_file = "/opt/airflow/tmp/fetch_data.json"  # Adjust the path if needed
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False)  # ✅ Preserve Unicode characters
    except Exception as e:
        logging.error(f"Failed to write JSON file: {e}")
        return None

    return temp_file  # ✅ Return file path instead of JSON string