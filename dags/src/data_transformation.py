import re
import logging
import os
import json
import pandas as pd
from src.sentiment_analysis import extract_sentiment, get_sentiment_with_chatgpt
from src.topic_analysis import get_topic_with_deepseek

# Function to Clean Text (Remove URLs, Hashtags, Mentions)
def clean_text(text):
    if not text:
        return ""
    
    text = re.sub(r"http\S+|www.\S+", "", text)  # Remove URLs
    text = re.sub(r"#\w+", "", text)  # Remove hashtags
    text = re.sub(r"@\w+", "", text)  # Remove mentions
    return text.strip()

def clean_emoji_and_long_text(text):
    """
    Removes emojis from text and ensures the topic is not longer than 50 characters.
    Returns "Unknown" if text contains emojis or exceeds length limit.
    """
    if not isinstance(text, str):  # Handle non-string values (NaN, None)
        return "Unknown"

    # Define a regex pattern for detecting emojis
    emoji_regex = re.compile(
        r"[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
        r"\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF"
        r"\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
        r"\U00002702-\U000027B0]+", flags=re.UNICODE
    )

    # Check if text contains emojis
    if emoji_regex.search(text):
        return "Unknown"

    # Check if text exceeds length limit
    return text if len(text) <= 50 else "Unknown"
    
# Function to Process DataFrame for Sentiment & Topic Analysis
def process_data_for_analysis(file_path):
    """Reads extracted insights from file, processes data, and saves processed results to another temp file."""
    
    try:
        # ✅ Read extracted insights from JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            extracted_insights = json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        return None  # ✅ Ensure Airflow does not fail

    # ✅ Convert list to DataFrame for processing
    df = pd.DataFrame(extracted_insights)

    # ✅ Ensure required columns exist
    if "text" not in df.columns:
        logging.error("Column 'text' not found in DataFrame.")
        return None
    
    df["clean_text"] = df["text"].apply(clean_text)
    df["topic"] = df["clean_text"].apply(get_topic_with_deepseek)
    df["topic"] = df["topic"].apply(clean_emoji_and_long_text)
    df["sentiment"] = df["clean_text"].apply(get_sentiment_with_chatgpt)
    df["sentiment"] = df["sentiment"].apply(extract_sentiment)
    #df["topic"] = df["topic"].apply(translate_topic)
    
# ✅ Save Processed Data to a Temporary JSON File
    processed_file_path = "/opt/airflow/tmp/processed_data.json"  # ✅ File path for processed data
    os.makedirs(os.path.dirname(processed_file_path), exist_ok=True)

    try:
        with open(processed_file_path, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to write processed insights JSON file: {e}")
        return None

    return processed_file_path  # ✅ Return file path instead of large JSON