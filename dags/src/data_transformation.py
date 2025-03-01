import re
import yaml
import logging
import ollama
import time
import openai
import pandas as pd
from googletrans import Translator
from src.sentiment_analysis import extract_sentiment

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

# Function to Translate Non-English Topics
def translate_topic(text):
    """
    Translates topic to English only if detected language is not English.
    """
    translator = Translator()
    try:
        if not isinstance(text, str) or text.strip() == "":
            return "Unknown"  # ✅ Ensure non-empty string is returned
        
        detected_lang = translator.detect(text).lang
        if detected_lang == "en":
            return text  # Skip translation if already in English
        
        translated_text = translator.translate(text, dest="en").text
        return translated_text if translated_text else "Unknown"  # ✅ Handle empty translations

    except Exception as e:
        logging.error(f"Translation Error: {e}")
        return "Translation Error"  # ✅ Ensure fallback value is a string
    
# Function to Process DataFrame for Sentiment & Topic Analysis
def process_data_for_analysis(df):
    """
    Cleans text, extracts sentiment, and classifies topics for analysis.
    """
    df["clean_text"] = df["text"].apply(clean_text)
    df["sentiment"] = df["sentiment"].apply(extract_sentiment)
    df["topic"] = df["topic"].apply(clean_emoji_and_long_text)
    #df["topic"] = df["topic"].apply(translate_topic)
    
    return df  # Return transformed DataFrame