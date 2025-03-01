import ollama
import time
import logging
import pandas as pd

# Function to Use DeepSeek for Topic Analysis
def get_topic_with_deepseek(text):
    """
    Calls DeepSeek API to classify text into a single-word topic.
    """
    if not text or text.strip() == "":
        return "Unknown"  # Default fallback for empty text
    try:
        response = ollama.chat(
            model="deepseek-v2:16b",
            messages=[
                {"role": "system", "content": "You are a topic analysis assistant. Classify the topic of the given text."},
                {"role": "user", "content": f"Analyze the given multi-language Instagram caption and classify it into only one English topic. The topic should be specific enough to provide meaningful insights but not overly niche. If multiple topics are highly related, consolidate them into a common broader category instead of listing them separately. Return only one word representing the topic in English. If the caption cannot be analyzed, return only the word Unknown (without quotes or additional explanation).:\n\n{text}"}
            ],
            options={"temperature": 0}
        )
        time.sleep(0.5)  # Avoid overloading Ollama with fast requests
        return response["message"]["content"] if "message" in response else "Unknown"
    
    except Exception as e:
        print(f"Error calling DeepSeek: {e}")
        return "Unknown"  # Default fallback in case of errors
        
# Optimized Batch Topic Analysis
def batch_topic_analysis(df, batch_size=10):
    """Processes topic analysis in batches for efficiency."""
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