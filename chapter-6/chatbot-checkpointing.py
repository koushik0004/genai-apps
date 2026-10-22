from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import add_messages, StateGraph, START, END
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console

from lib import timer, api_key, base_url, GEMINI_GEMMA_MODEL, OPEN_ROUTER_MODEL, OPEN_ROUTER_OSS_MODEL

console = Console()

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = init_chat_model(
    model_provider="openai", 
    model=OPEN_ROUTER_MODEL,
    api_key=api_key,                                                                                             
    base_url=base_url
)

def chatbot_agent(state: State):
    result = llm.invoke(state["messages"])
    return {"messages": [result]}

graph_builder = StateGraph(State)

# add node
graph_builder.add_node("chatbot_agent", chatbot_agent)

# add edges
graph_builder.add_edge(START, "chatbot_agent")
graph_builder.add_edge("chatbot_agent", END)

# Compile
# graph = graph_builder.compile()
def compile_for_checkpoining(checkpoitnig):
    return graph_builder.compile(checkpointer=checkpoitnig)


if __name__ == "__main__":
    DB_URI = "mongodb://localhost:27017"
    config = {
        "configurable": {
            "thread_id": "2"
        }
    }

    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = compile_for_checkpoining(checkpointer)

        user_query = input(" > ")

        _state = {
            "messages": [
                {"role": "user", "content": user_query}
            ]
        }

        with timer(description='Open Router API call'):
            # Call Graph or Invoke Graph
            output = graph.invoke(_state, config)
            structured_output = {
                "messages": [
                    {"role": msg.type, "content": msg.content}
                    for msg in output.get("messages", [])
                ]
            }
            # reset state
            # console.print(RichMarkdown(f" 🤖 {structured_output}"))
            console.print(RichMarkdown(f" 🤖 {structured_output['messages'][-1]['content']}"))


