from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console

from lib import client, timer, GEMINI_GEMMA_MODEL

console = Console()

class State(TypedDict):
    user_query: str
    result: str | None

SYSTEM_PROMPT = """
    You are a helpful AI expert who solves user queries. 
    Always answer very very briefly, Max one liner.
"""
def chatting_agent(state: State) -> State:
    console.print(RichMarkdown(f" 🙅‍♂️ User Query: {state['user_query']}"))
    user_query = state['user_query']
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    response = client.chat.completions.create(
                model=GEMINI_GEMMA_MODEL,
                messages=messages
            )
    result = response.choices[0].message.content
    return State(user_query=user_query, result=result)

graph_builder = StateGraph(State)

# Add Node
graph_builder.add_node("chatting_agent", chatting_agent)

# Add Edges
graph_builder.add_edge(START, "chatting_agent")
graph_builder.add_edge("chatting_agent", END)

#compile
graph = graph_builder.compile()

def main():
    while True:
        user_input = input("🙅‍♂️ User > ")
        if user_input.lower() in ["exit", "quit"]:
            console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
            break

        # _state = {
        #     "user_query": user_input,
        #     "result": None
        # }

        # output = graph.invoke(_state)
        # console.print(RichMarkdown(f" 🤖 Assistant >> {output['result']}"))

        with timer(description="OpenRouter API call / Langgraph"):
            initial_state = State(user_query=user_input, result=None)
            final_state = graph.invoke(initial_state)
            console.print(RichMarkdown(f" 🤖 Assistant >> {final_state['result']}"))

if __name__ == "__main__":
    main()