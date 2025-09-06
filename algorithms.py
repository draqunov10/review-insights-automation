from markdown_pdf import MarkdownPdf
from datetime import datetime
import tempfile
import json
import os

# Turn multiple JSON lines into an array of dicts
def parse_json_lines(file_path: str = "./cache_data/LDV_places.jsonl") -> list[dict]:
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
def process_input(month: str | int) -> list[dict]:
    raw_ldv_places = parse_json_lines()
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
    analysis_of_processed_data: dict
) -> dict:
    return {
        "client": client,
        "location": loc,
        "description": desc,
        "report_title": report_title,
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_of_reviews": analysis_of_processed_data,
        "dealerships_with_reviews": processed_data,
    }

def make_pdf(md: str) -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as tmp_md:
        tmp_md.write(md)
        tmp_md_path = tmp_md.name
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_pdf = f"report-{date_str}.pdf"
    
    pdf = MarkdownPdf()
    pdf.add_markdown(tmp_md_path)
    pdf.save(output_pdf)
    
    os.remove(tmp_md_path)


# Test usage by running this
if __name__ == "__main__":
    for filtered_dealership in process_input(8):
        print(filtered_dealership)
        print(f"{'=' * 20}\n")