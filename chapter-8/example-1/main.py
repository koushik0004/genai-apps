from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console
from lib import timer, client, GEMINI_GEMMA_MODEL, OPEN_ROUTER_MODEL, OPEN_ROUTER_OSS_MODEL

console = Console()

class State(TypedDict):
    user_query: str
    email_content: str | None
    is_approved: bool
    result: str | None

SYSTEM_PROMPT = """
    You are an AI agent who generates email, and wait for the user conformation to send the email
"""

def email_generator(state: State) -> State:
    user_query = state['user_query']
    with timer(description="OpenRouter API call"):
        response = client.chat.completions.create(
            model=GEMINI_GEMMA_MODEL,
            messages=[
                {"role": "system", "content" : SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ]
        )
    # update email_content
    state["email_content"] = response.choices[0].message.content
    return state

def human_approval(state: State) -> State:
    print(f"Please review draft email \n \n {state['email_content']} \n")

    user_choice = input("Send email: Yes - y, No - n : ")
    if user_choice.lower() == 'y':
        state["is_approved"] = True
    else:
        state["result"] = "❌ Email not sent."
        state["is_approved"] = False
    return state

def route_tool(state: State) -> Literal["send_email", "__END__"]:
    is_approved = state["is_approved"]
    if is_approved == True:
        return "send_email"
    return "__END__"

def send_email(state: State) -> State:
    to_email = input("Enter Email Address: ")
    # TODO
    state["result"] = "✅ Email Sent Successfully."
    return state

graph_builder = StateGraph(State)

# Add Nodes
graph_builder.add_node("email_generator", email_generator)
graph_builder.add_node("human_approval", human_approval)
graph_builder.add_node("send_email", send_email)

# Add Edges
graph_builder.add_edge(START, "email_generator")
graph_builder.add_edge("email_generator", "human_approval")

graph_builder.add_conditional_edges("human_approval", route_tool, {"send_email": "send_email", "__END__": END})
graph_builder.add_edge("send_email", END)

# compiling the graph
graph = graph_builder.compile()

if __name__ == "__main__":
    user_query = input(" > ")
    
    _state = {
        "user_query": user_query,
        "email_content": None,
        "is_approved": False,
        "result": None
    }

    output = graph.invoke(_state)
    console.print(output["result"])