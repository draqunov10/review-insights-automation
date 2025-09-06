from api_queries import fetch_dealerships, fetch_reviews_of
from models import dealership_model, report_model

from langchain.chains import LLMChain
from langchain_core.runnables import RunnableLambda
from langchain.prompts import PromptTemplate

# Wrap functions as RunnableLambda
scrape_dealerships = RunnableLambda(fetch_dealerships)
scrape_reviews = RunnableLambda(fetch_reviews_of)

prompt1 = PromptTemplate.from_template("{data}")
generate_summary = LLMChain(llm=dealership_model, prompt=prompt1, output_key="summary")

prompt2 = PromptTemplate.from_template("{summary}")
generate_report = LLMChain(llm=report_model, prompt=prompt2, output_key="insights")

def create_report():
    return (scrape_dealerships | scrape_reviews | generate_summary | generate_report)

# Example run
print(create_report())
