import numpy as np
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console
from lib import timer, api_key, base_url, get_current_weather, GEMINI_GEMMA_MODEL, OPEN_ROUTER_MODEL, OPEN_ROUTER_OSS_MODEL

console = Console()

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_weather(place="Bengaluru", country_code="IN"):
    """
        Accepts the place name as input and return the current weather of that location
        Args:
            place: the city name mostly
            country_code: another parameter the country code here. default country code is IN, but we can pass city from other country
    """
    weather = get_current_weather(place, country_code)
    return f"The current weather in {weather['city']} is {weather['temperature_c']}°C and {weather['condition']}."

@tool
def get_average_value(arr=[])-> float:
    """
        Accepts an array of values int / float i.e. numeric values only, and it will calculate the mean using numpy array.
        finally it will return the float value with 2 decimal places
        Args:
            arr: the list of numeric values
    """
    try:
        nparr = np.asarray(arr, dtype=float)
    except (TypeError, ValueError) as e:
        raise ValueError("Input must contain numeric values") from e

    if nparr.size == 0:
        raise ValueError("Cannot calculate mean of an empty array")
    return round(float(np.mean(nparr)), 2)


# List of tools   
tool_list = [get_weather, get_average_value]

llm = init_chat_model(
    model_provider="openai", 
    model=OPEN_ROUTER_MODEL,
    api_key=api_key,                                                                                             
    base_url=base_url
)
llm_with_tool = llm.bind_tools(tools=tool_list)

def chatbot_agent(state: State):
    result = llm_with_tool.invoke(state["messages"])
    return {"messages": [result]}

graph_builder = StateGraph(State)
tool_node = ToolNode(tools=tool_list)

# add node
graph_builder.add_node("chatbot_agent", chatbot_agent)
graph_builder.add_node("tools", tool_node)

# add edges
graph_builder.add_edge(START, "chatbot_agent")
graph_builder.add_conditional_edges("chatbot_agent", tools_condition)

# not required here, as `tools_condition` going to handle it automatically
# graph_builder.add_edge("chatbot_agent", END)

graph_builder.add_edge("tools", "chatbot_agent")

graph = graph_builder.compile()

if __name__ == "__main__":
    user_query = input(" > ")
    
    _state = {
        "messages": [
            {"role": "user", "content": user_query}
        ]
    }
    with timer(description='Open Router API call'):
        # Call Graph or Invoke Graph
        # output = graph.invoke(_state)
        # structured_output = {
        #     "messages": [
        #         {"role": msg.type, "content": msg.content}
        #         for msg in output.get("messages", [])
        #     ]
        # }
        # # reset state
        # # console.print(RichMarkdown(f" 🤖 {structured_output}"))
        # console.print(RichMarkdown(f" 🤖 {structured_output['messages'][-1]['content']}"))

        # # pretty print with streams
        events = graph.stream(_state, stream_mode="values")
        for event in events:
            event['messages'][-1].pretty_print()