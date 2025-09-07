from markdown_pdf import MarkdownPdf, Section
from api_queries import fetch_reviews
from datetime import datetime
import json, subprocess, platform, os

# Turn multiple JSON lines into an array of dicts
def parse_json_lines(file_path: str) -> list[dict]:    
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    results.append(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Error parsing line: {e}")
    return results

# Scrape LDV places with reviews, or use cache if available
def scrape_LDV_places(file_path: str, reuse_cache: bool = False) -> list[dict]:
    if not file_path or file_path.strip() == "":
        raise ValueError("file_path must be a non-empty string.")
    
    if os.path.exists(file_path) and reuse_cache:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Using cached LDV places data.")
        return parse_json_lines(file_path)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Scraping LDV places with reviews...")
    # Check if file exists and rename it
    if os.path.exists(file_path):
        backup_suffix = f"_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        base, ext = os.path.splitext(file_path)
        new_path = f"{base}{backup_suffix}{ext}"
        os.rename(file_path, new_path)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Cache data already exists. Backed up {file_path} to {new_path}")

    command = ["./utils/google_maps_scraper", "-input", "./utils/gms_input.txt", "-results", file_path, "-json", "-extra-reviews", "-geo", "-31.5253323,148.6922628", "-zoom", "7"]

    #! Must have WSL Installed
    if platform.system() == "Windows": command =  ["cmd", "/c", "wsl"] + command
    
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Error occurred while scraping reviews: {result.stderr}")

    #* Fallback for null reviews
    ldv_places = parse_json_lines(file_path)
    updated_flag = False
    for place in ldv_places:
        if not place.get("user_reviews_extended"):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Re-attempting to scrape reviews for place: {place.get('title', 'Unknown')}")
            place["user_reviews_extended"] = scrape_reviews_with_serpapi(place.get("data_id"))
            if place["user_reviews_extended"]: updated_flag = True

    # If any place was updated, overwrite the file with new data
    if updated_flag:
        with open(file_path, "w", encoding="utf-8") as f:
            for place in ldv_places:
                f.write(json.dumps(place, ensure_ascii=False) + "\n")

    return ldv_places

# Using SerpAPI's Google Maps Reviews API as contingency if initial review scrape fails
def scrape_reviews_with_serpapi(data_id: str) -> list[dict]:
    reviews = fetch_reviews(data_id)
    if not reviews:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | No reviews found for {data_id} using SerpAPI.")

    # Renaming keys according to the original format of 'user_reviews_extended'
    # Original keys: "Name", "Rating", "Description", "When"
    # SerpAPI's equivalent keys: "user" (dict) -> "name", "rating", "snippet", "iso_date"
    return [{
        "Name": review.get("user", {}).get("name"),
        "Rating": review.get("rating"),
        "Description": review.get("snippet"),
        "When": review.get("iso_date"),
    } for review in reviews]

def check_places(places: list[dict]) -> None:
    if not places: raise ValueError("No places found.")
    [print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Missing user_reviews in place: {place.get('title', 'Unknown')}\nLink: {place.get('link', 'Unknown')}\n") for place in places if not place.get("user_reviews_extended")]

# Reduce the places by selecting only those who are dealerships
def filter_dealerships(places: list[dict]) -> list[dict]:
    def has_dealer(categories, place):
        if categories is None: raise KeyError(f"Missing 'categories' in place: {place}")
        return any("dealer" in cat.lower() for cat in categories)
    if not places: return []
    return [place for place in places if has_dealer(place.get("categories"), place)]

# Reduce the number of reviews by filtering selected month
def filter_reviews_by_month(reviews: list[dict], month: int | str) -> list[dict]:
    if not reviews: return []
    
    # Accept month as int or str, convert to int
    try: month_int = int(month)
    except Exception: raise ValueError(f"Month must be an integer from 1 to 12. Got {month}")
    if not (1 <= month_int <= 12): raise ValueError(f"Month must be in the range 1 to 12. Got {month}")

    filtered = []
    for review in reviews:
        review_date = review.get("When")
        if review_date:
            # Expect format 'YYYY-M-D' or 'YYYY-MM-DD', handle both
            # Skip invalid/problematic dates
            parts = review_date.split("-")
            if len(parts) < 2: continue
            try:
                review_month = int(parts[1])
                if review_month == month_int:
                    filtered.append(review)
            except Exception: continue
            
    return filtered

# Only take the necessary data, throw error if keys don't exist
def filter_keys(d: dict, keys: list[str]) -> dict:
    missing_keys = [key for key in keys if key not in d]
    if missing_keys: raise KeyError(f"Missing keys {missing_keys} in review: {d}")

    return {key: d[key] for key in keys}

# Remove certain keys from a dict
def filter_out_keys(d: dict, keys: list[str]) -> dict:
    return {key: d[key] for key in d if key not in keys}

# Return an array of dealerships json ready to feed by batch
def process_input(month: str | int, file_path: str, reuse_cache: bool) -> list[dict]:
    raw_ldv_places = scrape_LDV_places(file_path, reuse_cache)
    filtered_ldv_dealerships = filter_dealerships(raw_ldv_places)
    filtered_ldv_dealerships_keys = [filter_keys(dealership, [
        "title",
        "review_count",
        "review_rating",
        "reviews_per_rating",
        "user_reviews_extended"
    ]) for dealership in filtered_ldv_dealerships]

    for dealership in filtered_ldv_dealerships_keys: 
        dealership["user_reviews_extended"] = filter_reviews_by_month(dealership.get("user_reviews_extended"), month)
        dealership["user_reviews_extended"] = [
            filter_keys(review, [
            "Rating",
            "Description"
            ]) for review in dealership["user_reviews_extended"]
        ]
    
    return filtered_ldv_dealerships_keys

def convert_to_report_data(
    client: str,
    loc: str,
    desc: str,
    report_title: str,
    processed_data: list[dict],
    analysis_of_processed_data: dict,
    analysis_of_car_models: dict | None = None
) -> dict:
    report_data = {
        "client": client,
        "location": loc,
        "description": desc,
        "report_title": report_title,
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_of_rating_reviews": analysis_of_processed_data,
        "dealerships_with_reviews": processed_data
    }
    if analysis_of_car_models: report_data["analysis_of_car_models_reviews"] = analysis_of_car_models
    return report_data

def make_pdf(month: str | int, md: str) -> None:
    # Convert month number to month name
    try:
        month_int = int(month)
        month_name = datetime(1900, month_int, 1).strftime('%B').lower()
    except Exception: month_name = str(month)
    
    pdf = MarkdownPdf()
    pdf.add_section(Section(md, toc=False))
    pdf.save(f"./reports/{month_name}_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf")


# Test usage by running this
if __name__ == "__main__":
    scrape_LDV_places()