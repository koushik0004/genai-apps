from langgraph.checkpoint.mongodb import MongoDBSaver
from util import (checkpoint_with_graph, mongo_uri, thread_id)
from langgraph.types import Command
from lib import timer

def human_support():
    DB_URI = mongo_uri()
    config = thread_id()
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = checkpoint_with_graph(checkpointer)

        graph_state = graph.get_state(config)
        last_message = graph_state.values["messages"][-1]
        # last_message.pretty_print()

        user_question = None

        # Another way of getting message
        # if graph_state.tasks and graph_state.tasks[0].interrupts:
        #     user_question = graph_state.tasks[0].interrupts[0].value.get('query')


        if getattr(last_message, 'tool_calls', None):
            for tool_call in last_message.tool_calls:
                if tool_call.get('name') == 'human_assistance':
                    user_question = tool_call.get('args', {}).get('query')
                    break

        print("User's Query: ", user_question)
        answer = input("Human Support: ")
        human_command = Command(resume={"data": answer})
        with timer(description='Open Router API call'):
            events = graph.stream(human_command, config, stream_mode="values")
            for event in events:
                    event['messages'][-1].pretty_print()

if __name__ == "__main__":
    human_support()