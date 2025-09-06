from langchain_ollama.llms import OllamaLLM

DEALERSHIP_SUMMARY_TEMPLATE: str = (
    "c"
    "c"
    "b"
    "a"
)
dealership_model = OllamaLLM(
    model="mistral-small3.2",
    system_message=DEALERSHIP_SUMMARY_TEMPLATE,
    temperature=0
)



REPORT_TEMPLATE: str = (
    "c"
    "c"
    "b"
    "a"
)
report_model = OllamaLLM(
    model="qwen3:32b",
    system_message=REPORT_TEMPLATE,
    temperature=0
)

if __name__ == "__main__":
    print(DEALERSHIP_SUMMARY_TEMPLATE)