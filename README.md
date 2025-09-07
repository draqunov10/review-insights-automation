# Review Insights Automation

Automated pipeline for collecting, analyzing, and reporting on customer reviews for car dealerships, using Google Maps data and AI-powered summarization.

---

## Repository Structure

```
.env                      # Environment variables
.gitignore                # Git ignore rules
requirements.txt          # Python dependencies
ai_chat_models.py         # AI models for review summarization and report generation
algorithms.py             # Data processing and report formatting logic
api_queries.py            # (Reserved for API integrations)
report.py                 # Main pipeline orchestration
cache_data/               # Cached data (JSON, JSONL)
reports/                  # Generated PDF reports
utils/                    # Utilities and Google Maps Scraper
  ├─ gms_input.txt        # Input queries for scraper
  ├─ GMS_README.md        # Scraper documentation
  ├─ google_maps_scraper  # Scraper binary (Linux)
  ├─ google_maps_scraper.exe # Scraper binary (Windows)
  └─ webdata/             # Scraper database files
```

---

## Workflow Overview

1. **Data Collection**  
   Use [Google Maps Scraper](utils/GMS_README.md) to extract dealership reviews:
   - Configure queries in `utils/gms_input.txt`
   - Run the scraper to output JSON/JSONL files in `cache_data/`

2. **Data Processing**  
   - [`algorithms.py`](algorithms.py):  
     - Parse and filter dealership/review data
     - Prepare input for analysis and reporting

3. **AI-Powered Analysis & Reporting**  
   - [`ai_chat_models.py`](ai_chat_models.py):  
     - Summarize reviews
     - Generate sentiment analysis and actionable insights
     - Create detailed markdown reports

4. **Report Generation**  
   - [`report.py`](report.py):  
     - Orchestrates the pipeline
     - Outputs PDF reports to `reports/`

---

## Usage

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. Configure Environment

- Set up `.env` with required API keys (i.e. currently uses `GOOGLE_API_KEY` for Google AI model).

### 3. Run Google Maps Scraper

See [utils/GMS_README.md](utils/GMS_README.md) for command-line options and usage examples.

### 4. Generate Reports

```sh
python report.py
```
- Outputs PDF report in `reports/` directory.

---

## Key Files & Functions

- [`algorithms.process_input`](algorithms.py): Loads and filters dealership review data.
- [`ai_chat_models.generate_review_summary`](ai_chat_models.py): Summarizes reviews using AI.
- [`ai_chat_models.generate_reviews_analysis`](ai_chat_models.py): Produces sentiment analysis and recommendations.
- [`ai_chat_models.generate_md_report`](ai_chat_models.py): Generates markdown report.
- [`algorithms.make_pdf`](algorithms.py): Converts markdown to PDF.
- [`report.pipeline`](report.py): Main pipeline entry point.

---

## Notes

- Scraper binaries for Windows and Linux are included in `utils/`.
- Cached data and generated reports are not tracked by git (see [.gitignore](.gitignore)).
- For scraper details and advanced options, see [utils/GMS_README.md](utils/GMS_README.md).

---