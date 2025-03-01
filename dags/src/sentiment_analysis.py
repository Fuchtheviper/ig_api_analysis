import re
import yaml
import logging
import ollama
import time
import openai
from googletrans import Translator

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

# Function to Use OpenAI GPT for Sentiment Analysis
def get_sentiment_with_chatgpt(text):
    """
    Calls OpenAI API to classify sentiment as Positive, Negative, or Neutral.
    """
    openai.api_key = config["OPENAI_API_KEY"]
    if not text or text.strip() == "":
        return "Neutral"  # Default fallback
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a sentiment analysis assistant. Classify the sentiment of the given text."},
                {"role": "user", "content": f"Classify this Instagram caption into one of these categories: Positive, Negative, Neutral:\n\n{text}"}
            ],
            temperature=0.1  # Low temperature for deterministic response
        )
        sentiment_response = response.choices[0].message.content
        return extract_sentiment(sentiment_response)  # Ensure response is valid
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "Neutral"  # Default fallback

#Ensure Data quality from response
def extract_sentiment(text):
    # Define the list of sentiment words to look for.
    sentiments = ["Positive", "Negative", "Neutral"]
    
    # Convert the input text to lowercase for case-insensitive comparison.
    lower_text = text.lower()
    
    # Check each sentiment word.
    for sentiment in sentiments:
        if sentiment.lower() in lower_text:
            return sentiment  # Return the sentiment in its original form.
    
    # Return None if no sentiment word is found.
    return None