import re
import yaml
import logging
import json
import os

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

# Function to Extract Insights
def extract_insights(file_path):
    """Reads hashtag data from file and extracts insights."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_items = json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        return None  # Return None if file reading fails

    all_insights = []
    for item in all_items:
        try:
            caption_text = item.get("caption", {}).get("text", "").lower()
            logging.info(f"Caption Length {len(caption_text)} characters")
            
            # Extract hashtags from text using regex
            hashtags = re.findall(r"#(\w+)", caption_text)

            # Extract additional details
            post_id = item.get("id", None)
            comment_count = item.get("comment_count", 0)
            feed_type = item.get("feed_type", "")
            is_video = item.get("is_video", False)
            like_count = item.get("like_count", 0)
            media_name = item.get("media_name", "")
            product_type = item.get("product_type", "")
            video_duration = item.get("video_duration", 0.0)

            # Check for mentions of the hashtag in text or hashtags
            all_insights.append({
                "text": caption_text,
                "hashtags": hashtags,
                "id": post_id,
                "comment_count": comment_count,
                "feed_type": feed_type,
                "is_video": is_video,
                "like_count": like_count,
                "media_name": media_name,
                "product_type": product_type,
                "video_duration": video_duration,
            })
        except Exception as e:
            logging.error(f"Error in extracting insights: {str(e)}")
    logging.info(f"Post insight amount {len(all_insights)} post")

    # ✅ Save Extracted Insights to a JSON File
    temp_file = "/opt/airflow/tmp/extracted_insights.json"  # ✅ File path for saving extracted data
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(all_insights, f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to write extracted insights JSON file: {e}")
        return None

    return temp_file  # ✅ Return file path instead of large JSON