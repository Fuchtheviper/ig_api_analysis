from openai import OpenAI
import yaml
import os
import time
import logging
import pandas as pd

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

# Function to Use DeepSeek for Topic Analysis
def get_topic_with_deepseek(text):
    """
    Calls DeepSeek API to classify text into a single-word topic.
    """
    # Use environment variable for API key
    api_key = config["DEEPSEEK_API_KEY"]
    if not api_key:
        raise ValueError("DeepSeek API key not found in environment variables")
    
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    if not text or text.strip() == "":
        return "Unknown"  # Default fallback for empty text
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a topic analysis assistant. Classify the topic of the given text. Return only Topic in English"},
                {"role": "user", "content": f"Analyze the given multi-language Instagram caption and classify it into only one English topic. The topic should be specific enough to provide meaningful insights but not overly niche. If multiple topics are highly related, consolidate them into a common broader category instead of listing them separately. Return only one word representing the topic in English. If the caption cannot be analyzed, return only the word Unknown (without quotes or additional explanation) example output = Travel, Festival :\n\n{text}"}
            ],
        )
        
        time.sleep(0.5)  # Avoid overloading the API with fast requests
        
        # Extract the topic from the response
        if response.choices and len(response.choices) > 0:
            logging.info(f"Topic :{response}")
            return response.choices[0].message.content.strip()
        else:
            return "Unknown"
    
    except Exception as e:
        print(f"Error calling DeepSeek: {e}")
        return "Unknown"  # Default fallback in case of errors
        
# Optimized Batch Topic Analysis
def batch_topic_analysis(df, batch_size=10):
    """Processes topic analysis in batches for efficiency."""

    # ✅ Ensure `df` is a valid Pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        logging.error(f"Expected DataFrame but got {type(df).__name__}")
        return df  # Return unchanged DataFrame
    
    if df.empty:
        logging.warning("DataFrame is empty. No topics to analyze.")
        return df

    num_batches = (len(df) // batch_size) + 1

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(df))

        # ✅ Only process non-empty slices
        if start_idx < end_idx:
            batch = df.loc[start_idx:end_idx, "clean_text"]
            if not batch.empty:
                df.loc[start_idx:end_idx, "topic"] = batch.apply(get_topic_with_deepseek)
                logging.info(f"Processed batch {i+1}/{num_batches}")
            else:
                logging.warning(f"Batch {i+1} is empty. Skipping.")

    return df