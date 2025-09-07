from ai_chat_models import generate_review_summary, generate_reviews_analysis, generate_md_report, generate_models_analysis
from algorithms import filter_out_keys, process_input, convert_to_report_data, make_pdf
from ai_search_agent import search_and_summarize_model_reviews
from datetime import datetime
import json

def pipeline(month: str | int = "current", file_path: str | None = "./cache_data/LDV_places.jsonl", reuse_cache: bool = False, search_car_models: bool = False) -> None:
    # month can be "current" or an integer 1-12
    if month == "current": month = datetime.now().month
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Running pipeline for month: {month} (reuse_cache={reuse_cache})")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | Path: {file_path} | Search Car Models: {search_car_models}")

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
    
    
    #* Step 3(Optional): Add car model reviews
    generated_models_analysis = None
    if search_car_models:
        car_reviews = search_and_summarize_model_reviews()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | OPTIONAL STEP 3 - CAR REVIEWS:\n{car_reviews}")
        print('=' * 20)

        #* Step 4(Optional): Generate models analysis
        generated_models_analysis = generate_models_analysis(f"{car_reviews}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | STEP 4 - MODELS ANALYSIS:\n{json.loads(generated_models_analysis)}")
        print('=' * 20)

    #* Last step: Convert to report data and generate markdown
    month_name = datetime(1900, int(month), 1).strftime('%B')
    report_data = convert_to_report_data(
        client="LDV",
        loc="New South Wales, Australia",
        desc=f"Customer reviews analysis report for the month of {month_name}",
        report_title=f"LDV Dealerships{'' if not search_car_models else 'and Car Models'} Review {month_name} Report",
        processed_data=dealers_input,
        analysis_of_processed_data=f"For year {datetime.now().year}, {generated_models_analysis}"
    )

    generated_md_report = generate_md_report(f"{report_data}")
    make_pdf(month, generated_md_report)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | STEP 3 - MARKDOWN REPORT:\n{generated_md_report}")

if __name__ == "__main__":
    pipeline()