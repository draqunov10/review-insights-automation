from ai_chat_models import generate_review_summary, generate_reviews_analysis, generate_md_report
from algorithms import filter_out_keys, process_input, convert_to_report_data, make_pdf
from datetime import datetime
import json

def pipeline(month: str | int = "current", file_path: str | None = "./cache_data/LDV_places.jsonl", reuse_cache: bool = False) -> None:
    # month can be "current" or an integer 1-12
    if month == "current": month = datetime.now().month


    #* Step 1: Get dealer input and generate review summaries
    dealers_input = process_input(month, file_path, reuse_cache)
    for i, dealer in enumerate(dealers_input):
        generated_review_summary = generate_review_summary(f"{dealer['user_reviews_extended']}")
        dealers_input[i]["review_summary"] = generated_review_summary
        dealers_input[i] = filter_out_keys(dealers_input[i], ["user_reviews_extended"])        

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | STEP 1 - DEALERS INPUT:\n{dealers_input}")
    print('=' * 20)


    #* Step 2: Generate reviews analysis
    generated_analysis = generate_reviews_analysis(f"{dealers_input}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | STEP 2 - ANALYSIS:\n{json.loads(generated_analysis)}")
    print('=' * 20)


    #* Step 3: Convert to report data and generate markdown
    month_name = datetime(1900, int(month), 1).strftime('%B')
    report_data = convert_to_report_data(
        client="LDV",
        loc="New South Wales, Australia",
        desc=f"Customer reviews analysis report for the month of {month_name}",
        report_title=f"LDV Dealerships Review {month_name} Report",
        processed_data=dealers_input,
        analysis_of_processed_data=generated_analysis
    )

    generated_md_report = generate_md_report(f"{report_data}")
    make_pdf(month, generated_md_report)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | STEP 3 - MARKDOWN REPORT:\n{generated_md_report}")

if __name__ == "__main__":
    pipeline()