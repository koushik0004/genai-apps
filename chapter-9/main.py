from mem0 import Memory
from rich.console import Console
from lib import timer, client, api_key, base_url, TEXT_EMBEDDING_MODEL, GEMINI_GEMMA_MODEL, OPEN_ROUTER_MODEL


console = Console()

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": OPEN_ROUTER_MODEL,
            "api_key": api_key,                                                                                               
            "openai_base_url": base_url,
        }
    },

    "embedder": {
        "provider": "openai",
        "config": {
            "model": TEXT_EMBEDDING_MODEL,
            "api_key": api_key,                                                                                               
            "openai_base_url": base_url,                                                                                      
            "embedding_dims": 3072,  # matches text-embedding-3-large 
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": "6333"
        }
    },

    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "neo4j://localhost:7687",
            "username": "",
            "password": ""
        }
    }
}

memory = Memory.from_config(config)

def main():
    while True:
        user_input = input("🙅‍♂️ User > ")
        if user_input.lower() in ["exit", "quit"]:
            console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
            break

        relevent_data = memory.search(query=user_input, filters={"user_id": "genai"})
        data = {}
        if 'results' in relevent_data:
            for msg in relevent_data['results']:
                id = msg['id']
                message = msg['memory']
                data[id] = message # {'21e02547-fbc9-41f0-8bc9-8dd364843195' : 'Is from India'}

        SYSTEM_PROMPT = f"""
            You are a memory aware AI agent who has information of the user in below relavent data section

            Relevent Data (Format - id: message):
            {data}
        """

        response = client.chat.completions.create(
            model=OPEN_ROUTER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        print(response.choices[0].message.content)

        memory.add([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response.choices[0].message.content}
            ],
            user_id="genai"
        )

if __name__ == '__main__':
    main()