from typing_extensions import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console

from lib import client, timer, GEMINI_GEMMA_MODEL, OPENAI_NANO_MODEL, OPEN_ROUTER_OSS_MODEL

console = Console()

class QueryIdentifier(BaseModel):
    is_coding_query: bool

class ValidateCode(BaseModel):
    is_valid_code: bool

class State(TypedDict):
    user_query: str
    is_coding_query: bool
    is_valid_code: bool
    result: str | None

def query_identifer_agent(state: State) -> State:
    console.print(RichMarkdown(" ⚠️ Called query identifier agents"))
    console.print(RichMarkdown(f" 🙅‍♂️ User Query: {state['user_query']}"))
    user_query = state['user_query']
    messages = [
        {"role": "system", "content": "You are a helpful AI expert who identifies if the user query is coding related or not. If it is coding related, also identify if the code is valid or not."},
        {"role": "user", "content": user_query}
    ]

    response = client.chat.completions.parse(
        model=OPENAI_NANO_MODEL,
        messages=messages,
        response_format=QueryIdentifier
    )
    result = response.choices[0].message.content
    is_coding_query = response.choices[0].message.parsed.is_coding_query
    console.print(RichMarkdown(f" ⚠️ Query Identifier Agent Result: {result}"))

    return State(user_query=user_query, is_coding_query=is_coding_query, result=result)

def route_query_agent(state: State) -> Literal["code", "general"]:
    console.print(RichMarkdown(" ⚠️ Called route query agent"))
    console.print(RichMarkdown(f" 🙅‍♂️ User Query: {state['user_query']}"))
    is_coding_query = state['is_coding_query']

    return "code" if is_coding_query else "general"

def coding_agent(state: State) -> State:
    console.print(RichMarkdown(" ⚠️ Called coding agent"))
    SYSTEM_PROMPT = """
        You are a coding AI Agent, You solves user's query related to coding.
        - make sure to have answer briefly, i.e. not much coding examples
    """
    user_query = state["user_query"]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    response = client.chat.completions.create(
        model=OPEN_ROUTER_OSS_MODEL,
        messages=messages
    )
    result = response.choices[0].message.content
    console.print(RichMarkdown(f" ⚠️ Coding Agent Result: {result}"))
    return State(user_query=user_query, is_coding_query=True, is_valid_code=state["is_valid_code"], result=result)

def general_query_agent(state: State) -> State:
    console.print(RichMarkdown(" ⚠️ Called general query agent"))
    console.print(RichMarkdown(f" 🙅‍♂️ User Query: {state['user_query']}"))
    messages = [
        {"role": "system", "content": "You are a helpful AI expert who able to answer general queries"},
        {"role": "user", "content": state['user_query']}
    ]
    response = client.chat.completions.create(
        model=GEMINI_GEMMA_MODEL,
        messages=messages
    )
    result = response.choices[0].message.content
    console.print(RichMarkdown(f" ⚠️ General Query Agent Result: {result}"))
    return State(user_query=state['user_query'], is_coding_query=False, is_valid_code=state["is_valid_code"], result=result)

def validate_agent(state: State) -> State:
    console.print(RichMarkdown(" ⚠️ Called validate code agent"))
    user_query = state['user_query']
    code = state["result"]
    SYSTEM_PROMPT = f"""
        You are a coding AI agent, who validate below 'code' based on 'query'
        
        query: {user_query}
        code: {code}
    """
    response = client.chat.completions.parse(
        model=OPEN_ROUTER_OSS_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        response_format=ValidateCode
    )
    result = response.choices[0].message.content
    is_valid_code = response.choices[0].message.parsed.is_valid_code
    return State(user_query=state['user_query'], is_coding_query=False, is_valid_code=is_valid_code, result=result)

def route_validate_agent(state: State) -> Literal["coding_agent", "__END__"]:
    print(" ⚠️ call route_validate_agent")
    is_valid_code = state["is_valid_code"]
    return "__END__" if is_valid_code else "code"


graph_builder = StateGraph(State)

# add Node
graph_builder.add_node("query_identifer_agent", query_identifer_agent)
graph_builder.add_node("route_query_agent", route_query_agent)
graph_builder.add_node("coding_agent", coding_agent)
graph_builder.add_node("general_query_agent", general_query_agent)
graph_builder.add_node("validate_agent", validate_agent)
graph_builder.add_node("route_validate_agent", route_validate_agent)

graph_builder.add_edge(START, "query_identifer_agent")
graph_builder.add_conditional_edges("query_identifer_agent", route_query_agent, {"code": "coding_agent", "general": "general_query_agent"})
graph_builder.add_edge("general_query_agent", END)

graph_builder.add_edge("coding_agent", "validate_agent")
graph_builder.add_conditional_edges("validate_agent", route_validate_agent, {"code": "coding_agent", "__END__": END})

# Compile
graph = graph_builder.compile()

if __name__ == "__main__":
    while True:
        user_input = input("🙅‍♂️ User > ")
        if user_input.lower() in ["exit", "quit"]:
            console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
            break

        with timer(description="OpenRouter API call / Langgraph"):
            initial_state = State(user_query=user_input, is_coding_query=False, is_valid_code=True, result=None)
            # final_state = graph.invoke(initial_state)
            # console.print(RichMarkdown(f" 🤖 Assistant >> {final_state['result']}"))
            # Stream
            events = graph.stream(initial_state)
            for event in events:
                console.print(RichMarkdown(event))