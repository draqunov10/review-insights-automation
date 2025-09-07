from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os, re

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Thoughts: Avoid bias by being independent review summary assistant
REVIEW_SUMMARY_TEMPLATE = """You are a concise review-summarization assistant.  
Task: Given a list of json reviews produce a **brief review summary** for human readers.

Requirements:
1. No fluff, answer the question directly.
2. Output **one to four sentences** (aim for ~25-125 words). Keep it short.
3. Be specific on the strengths, weaknesses, and recommendations if there are any.
4. Be specific on the car models if there are mentioned.
5. Call out the most prominent customer themes (staff names, service experience, purchase process, common praise/complaint). Use exact short snippets (≤12 words) as quotes if helpful.
6. If low-rating counts exist but no negative review text is provided, note that negative feedback exists but specifics are not available.
7. If you are given an empty list, note that no reviews are available for summary.
8. Do **not** invent facts or add information not present in the input data.
9. Tone: neutral-to-positive, professional. Avoid marketing language.
10. Output format: one paragraph plain summary text only (no extra sections). Optionally include one short parenthetical with a representative quote.

Example output length: 1-4 sentences, ~25-100 words."""

# Thoughts: Since this is a more complex task, use chain-of-thought/reasoning model.
REVIEWS_ANALYSIS_TEMPLATE = """You are an assistant expert at review sentiment analysis.
Task: Given an array of dictionaries/JSONs containing `title`, `review_count`, `review_rating`, `reviews_per_rating`, and `review_summary`, provide a meaningful insights/themes, prioritized recommendations, and measurable next steps based on customer feedback.
This will be fed into a larger report.

Guide:
1. Produce a **sentiment analysis summary** (1-2 sentences) that an internal team and client can scan quickly.
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
- Pure JSON output starting with a left curly bracket { and ends with a right curly bracket }
- Use only facts in `data`. Do **not** invent or infer details not present.
- Counts are available (from `reviews_per_rating`), use them to quantify themes where reasonable (e.g., "% 5-star", "33 one-star reviews").
- When representative quotes exists, maintain them and enclosed in quotes.
- Tone: professional, concise, and actionable (neutral-to-positive)."""

# Slightly modified to cater to car model reviews
MODELS_ANALYSIS_TEMPLATE = """You are an assistant expert at review sentiment analysis for car models.
Task: Given an array of dictionaries/JSONs useful data, provide a meaningful insights/themes, prioritized recommendations, and measurable next steps based on customer feedback.
This will be fed into a larger report.

Guide:
1. Produce a **sentiment analysis summary** (1-2 sentences) that an internal team and client can scan quickly.
2. Extract **top themes** (3-6) from the reviews (positive, negative, or mixed), explain why each theme matters, and show supporting evidence (counts where possible and 1 representative short quote).
3. Provide **actionable recommendations**, prioritized (High / Medium / Low) and tied to concrete next steps the business can take.
5. Report **confidence & data gaps** (e.g., “no negative review text available — only counts”).

Required output would be a JSON object with these keys:
- `brief_sentiment_analysis_summary` (string, 1-2 sentences)
- `themes` (array of objects): each `{ "theme": string, "sentiment": "positive|negative|mixed", "explanation": string, "representative_quotes": [strings up to 1] }`
- `recommendations` (array): each `{ "priority": "High|Medium|Low", "action": string, "rationale": string, "suggested_kpis": [strings] }`
- `confidence_and_gaps` (string): short note about confidence and any missing data

Rules & constraints:
- Pure JSON output starting with a left curly bracket { and ends with a right curly bracket }
- Use only facts in `data`. Do **not** invent or infer details not present.
- Include the website name and date of the review.
- When representative quotes exists, maintain them and enclosed in quotes.
- Tone: professional, concise, and actionable (neutral-to-positive)."""

# Similarly, use chain-of-thought/reasoning model.
REPORT_WRITING_TEMPLATE = """You are a business researcher tasked with writing a cohesive report about customer reviews for the client.
You will be provided with the report data containing original review data and some analysis from an analyst assistant.

Task: 
1. You should first come up with an outline for the report that describes the structure and flow of the report.
2. Then, generate the report and return that as your final output.
3. Make sure the report includes an executive summary, complete details including the review analysis, and actionable recommendations.

The final output should be in *markdown format*, and it should be lengthy and detailed.
Aim for 2-4 pages of content, at least 1000 words."""


# Helper function to parse out thoughts for chain-of-thoughts model
def parse_reasoning_output(output: str) -> dict:
    thoughts_pattern = r"<think>(.*?)</think>"
    thoughts_match = re.search(thoughts_pattern, output, re.DOTALL)
    thoughts = thoughts_match.group(1).strip() if thoughts_match else ""
    # Remove thoughts section from content
    content = re.sub(thoughts_pattern, "", output, flags=re.DOTALL).strip()
    return {
        "thoughts": thoughts,
        "content": content
    }


def generate_review_summary(user_prompt: str) -> str:
    return ChatOllama(
        model="qwen2.5:32b",
        temperature=0,
        num_ctx=1024
    ).invoke([
        SystemMessage(content=REVIEW_SUMMARY_TEMPLATE),
        HumanMessage(content=user_prompt)
    ]).text()

def generate_reviews_analysis(user_prompt: str) -> str:
    response = ChatOllama(
        model="qwen2.5:32b",
        temperature=0,
        num_ctx=4096
    ).invoke([
        SystemMessage(content=REVIEWS_ANALYSIS_TEMPLATE),
        HumanMessage(content=user_prompt)
    ]).text()

    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match: response = match.group(0)
    else: raise ValueError("Failed to extract JSON from dealers_input")
    return response

def generate_models_analysis(user_prompt: str) -> str:
    response = ChatOllama(
        model="qwen2.5:32b",
        temperature=0,
        num_ctx=4096
    ).invoke([
        SystemMessage(content=MODELS_ANALYSIS_TEMPLATE),
        HumanMessage(content=user_prompt)
    ]).text()

    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match: response = match.group(0)
    else: raise ValueError("Failed to extract JSON from models_analysis")
    return response

def generate_md_report(user_prompt: str) -> str:
    return ChatOllama(
        model="qwen2.5:32b",
        temperature=0,
        num_ctx=16384
    ).invoke([
        SystemMessage(content=REPORT_WRITING_TEMPLATE),
        HumanMessage(content=user_prompt)
    ]).text()

model_google = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0
)

# Test usage here
if __name__ == "__main__":
    # print(ChatGoogleGenerativeAI(model="gemini-2.0-flash").invoke("Who is jose rizal?"))
    print(ChatOllama(model="mistral-nemo:latest").invoke("Who is jose rizal?"))