import logging
import time
import requests
import yaml
import sys
import json

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
    hashtags = HASHTAGS
    all_items = []
    for hashtag in hashtags:
        try:
            response = requests.get(INSTAGRAM_API_URL, headers=HEADERS, params={"hashtag": hashtag})
            response.raise_for_status()
            data = response.json().get("data", {}).get("items", [])
            if isinstance(data, dict):
                data = list(data.values())

            # ✅ Ensure `data` is a list before extending `all_items`
            if isinstance(data, list):
                all_items.extend(data)
            else:
                logging.error(f"Unexpected data type for hashtag {hashtag}: {type(data).__name__}")
        except requests.RequestException as e:
            logging.error(f"Error fetching {hashtag}: {e}")
    logging.info(f"Fetched {len(all_items)} items")
    return json.dumps(all_items)