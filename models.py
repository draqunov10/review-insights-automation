from langchain_ollama.llms import OllamaLLM

# Thoughts: Avoid bias by being independent review summary assistant
REVIEW_SUMMARY_TEMPLATE = """You are a concise review-summarization assistant.  
Task: Given a single input object `data` (a dictionary/JSON) that contains keys such as `title`, `review_count`, `review_rating`, `reviews_per_rating`, and `user_reviews_extended`, produce a **brief review summary** for human readers.

Requirements:
1. Output **one to three sentences** (aim for ~25-100 words). Keep it short and scannable.
2. Include the business name (`title`), overall rating (`review_rating`) and total reviews (`review_count`) in the first sentence.
3. Summarize the rating distribution at a high level (e.g., "mostly 5-star", "minority of negative reviews") using `reviews_per_rating`.
4. Call out the most prominent customer themes from `user_reviews_extended` (staff names, service experience, purchase process, common praise/complaint). Use exact short snippets (≤12 words) as quotes if helpful.
5. If low-rating counts exist but no negative review text is provided, note that negative feedback exists but specifics are not available.
6. Do **not** invent facts or add information not present in the input data.
7. Tone: neutral-to-positive, professional. Avoid marketing language.
8. Output format: plain summary text only (no extra sections). Optionally include one short parenthetical with a representative quote from `user_reviews_extended`.

Example output length: 1-4 sentences, ~25-100 words."""
summarizer_model = OllamaLLM(
    model="mistral-small3.2",
    system_message=REVIEW_SUMMARY_TEMPLATE,
    temperature=0
)

# Thoughts: Since this is a more complex task, use chain-of-thought/reasoning model.
REVIEWS_ANALYSIS_TEMPLATE = """You are an assistant expert at review sentiment analysis.
Task: Given an array of dictionaries/JSONs containing `title`, `review_count`, `review_rating`, `reviews_per_rating`, and `review_summary`, provide a meaningful insights/themes, prioritized recommendations, and measurable next steps based on customer feedback.
This will be fed into a larger report.

Guide:
1. Produce a **brief sentiment analysis summary** (1-2 sentences) that an internal team and client can scan quickly.
2. Extract **top themes** (3-6) from the reviews (positive, negative, or mixed), explain why each theme matters, and show supporting evidence (counts where possible and 1-2 representative short quotes).
3. Provide **actionable recommendations**, prioritized (High / Medium / Low) and tied to concrete next steps the business can take.
4. Optionally apply **KPIs / metrics** that are applicable.
5. Report **confidence & data gaps** (e.g., “no negative review text available — only counts”).

Required output would be a JSON object with these keys:
- `brief_sentiment_analysis_summary` (string, 1-2 sentences)
- `overall_metrics` (object: `average_rating`, `total_reviews`, `rating_distribution` copy of `reviews_per_rating`)
- `themes` (array of objects): each `{ "theme": string, "sentiment": "positive|negative|mixed", "explanation": string, "supporting_count": int_or_null, "representative_quotes": [strings up to 2] }`
- `recommendations` (array): each `{ "priority": "High|Medium|Low", "action": string, "rationale": string, "suggested_kpis": [strings] }`
- `confidence_and_gaps` (string): short note about confidence and any missing data

Rules & constraints:
- Use only facts in `data`. Do **not** invent or infer details not present.
- Counts are available (from `reviews_per_rating`), use them to quantify themes where reasonable (e.g., "% 5-star", "33 one-star reviews").
- When representative quotes exists, maintain them and enclosed in quotes.
- Tone: professional, concise, and actionable (neutral-to-positive)."""
analyst_model = OllamaLLM(
    model="qwen3:32b",
    system_message=REVIEWS_ANALYSIS_TEMPLATE,
    temperature=0
)

# Similarly, use chain-of-thought/reasoning model.
REPORT_WRITING_TEMPLATE = """You are a business researcher tasked with writing a cohesive report about customer reviews for the client.
You will be provided with the report data containing original review data and some initial analysis from an analyst assistant.

Task: 
1. You should first come up with an outline for the report that describes the structure and flow of the report.
2. Then, generate the report and return that as your final output.
3. Make sure the report includes an executive summary, complete details including the review analysis, and actionable recommendations.

The final output should be in *markdown format*, and it should be lengthy and detailed.
Aim for 2-3 pages of content, at least 1000 words."""
writer_model = OllamaLLM(
    model="qwen3:32b",
    system_message=REPORT_WRITING_TEMPLATE,
    temperature=0
)