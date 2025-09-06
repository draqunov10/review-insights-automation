from langchain_community.llms import ChatOllama


DEALERSHIP_SUMMARY_TEMPLATE: str = (
    "c"
    "c"
    "b"
    "a"
)
dealership_model = ChatOllama(
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
report_model = ChatOllama(
    model="qwen3:32b",
    system_message=REPORT_TEMPLATE,
    temperature=0
)
