from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# TODO: Future improvement, fetching/scraping the models automatically possibly through https://www.ldvautomotive.com.au/
MODELS = [
    "LDV T60 MAX Ute",
    "LDV Terron 9 Ute",
    "LDV eT60 UTE",
    "LDV MY25 D90 SUV",
    "LDV MIFA People Mover",
    "LDV MIFA 9",
    "LDV Deliver 7",
    "LDV G10+ Van",
    "LDV eDeliver 7",
    "LDV Deliver 9 Large Van",
    "LDV Deliver 9 Cab Chassis",
    "LDV eDeliver 9",
    "LDV Deliver 9 Bus"
]

#* Uses Top 3 search
tool_belt = [TavilySearch(max_results=3)]
model = ChatOpenAI(
  model="gpt-oss:20b",
  api_key="ollama",
  base_url="http://localhost:11434/v1",
  temperature=0,
)
model = model.bind_tools(tool_belt)
tool_node = ToolNode(tool_belt)

class AgentState(TypedDict):
  messages: Annotated[list, add_messages]

def call_model(state):
  messages = state["messages"]
  response = model.invoke(messages)
  return {"messages" : [response]}

def should_continue(state):
  last_message = state["messages"][-1]

  if last_message.tool_calls:
    return "action"

  return END

uncompiled_graph = StateGraph(AgentState)
uncompiled_graph.add_node("agent", call_model)
uncompiled_graph.add_node("action", tool_node)
uncompiled_graph.set_entry_point("agent")
uncompiled_graph.add_conditional_edges("agent", should_continue)
uncompiled_graph.add_edge("action", "agent")

search_agent_graph = uncompiled_graph.compile()


# Finds reviews of the models in current year
def search_and_summarize_model_reviews(models: list[str] = MODELS) -> list[dict]:
  year = datetime.now().year
  results = []
  for model_name in models:
    prompt = f"Search in Tavily to find latest ({year}) review/s of {model_name} and summarize all the review/s into one.\nMake sure *whole output* is brief (3-5 sentences) and only in *1 paragraph*.\nMake sure to include the website/s name and date/s of the review.\nIf no review is found, say 'No review found'."
    input = {"messages": [HumanMessage(content=prompt)]}
    model_reviews = []
    result = search_agent_graph.invoke(input)
    msg = result["messages"][-1].text()  # Take only the last AIMessage

    print(f"MESSAGE: {msg}")

    if not msg or "no review found" in msg.lower():
      print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No review found for {model_name}")
      model_reviews = ["No review found"]
      continue

    model_reviews.append(msg)
    results.append({
      "model": model_name,
      "model_review": model_reviews
    })
  return results


# Example usage
if __name__ == "__main__":
  models = MODELS[:2]
  reviews = search_and_summarize_model_reviews(models)
  with open("reviews.txt", "w", encoding="utf-8") as f:
    import pprint
    f.write(pprint.pformat(reviews))
