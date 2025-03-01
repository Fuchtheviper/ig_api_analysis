import re
import yaml
import logging
import json

with open("config/config.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

# Function to Extract Insights
def extract_insights(items):
    # ✅ Debugging: Log raw data before parsing
    logging.info(f"Raw `items` before parsing: {repr(items)}")
    
    # ✅ Handle empty values before parsing
    if not items or items in ["null", "None", ""]:
        logging.error("Received empty or None value for `items`.")
        return []
    
    # ✅ If `items` is a string, convert it to a list
    if isinstance(items, str):
        try:
            # ✅ Ensure proper JSON format by replacing single quotes with double quotes
            if items.startswith("'") or items.startswith("[{"):
                items = items.replace("'", '"')
            items = json.loads(items)  # ✅ Convert JSON string to Python list
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error: {e}")
            return []  # ✅ Return an empty list to prevent failure

    # ✅ Ensure `items` is a list before proceeding
    if not isinstance(items, list):
        logging.error(f"Expected a list but got {type(items).__name__}")
        return []
    
    all_insights = []
    for item in items:
        try:
            if not isinstance(item, dict):
                logging.warning(f"Skipping item: Expected dict, got {type(item).__name__}")
                continue

            caption_text = item.get("caption", {}).get("text", "").lower()
            
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
    return all_insights