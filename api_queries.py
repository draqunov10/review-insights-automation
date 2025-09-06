import requests

def fetch_dealerships():
    res = requests.get(f"http://localhost:5000/data?query={{}}")
    return res.json()["result"]

def fetch_reviews_of(dealership):
    from langchain_community.utilities import SerpAPIWrapper
    serp = SerpAPIWrapper()
    return serp.run(dealership)