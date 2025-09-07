from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

# Using SerpAPI's Google Maps Reviews API
def fetch_reviews(place_id: str):
    params = {
        "engine": "google_maps_reviews",
        "place_id": place_id,
        "api_key": os.getenv("SERP_API_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("reviews", [])

# Example usage
if __name__ == "__main__":
    place_id = "0x6b9c0f1d986269cd:0x1001f7bfaaba10b2"
    reviews = fetch_reviews(place_id)
    for review in reviews:
        print(f"Review by {review['author_name']}: {review['text']}")