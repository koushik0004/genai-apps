from mem0 import Memory
from neo4j import GraphDatabase
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
            "openai_base_url": base_url
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "memory_app",
            "embedding_model_dims": 3072, # <--- Explicitly match text-embedding-3-large
            "host": "localhost",
            "port": "6333"
        }
    },

    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "",
            "password": ""
        }
    }
}
neo4j_cfg = config["graph_store"]["config"]                                                                               
neo4j_driver = GraphDatabase.driver(                                                                                      
    neo4j_cfg["url"],                                                                                                     
    auth=(neo4j_cfg["username"], neo4j_cfg["password"]) if neo4j_cfg["username"] else None
)

memory = Memory.from_config(config)

def sync_to_neo4j(user_id: str, fact: str):
    with neo4j_driver.session() as session:
        session.run(
            """
            MERGE (u:User {id: $user_id})
            CREATE (m:Memory {text: $fact, created_at: datetime()})
            CREATE (u)-[:HAS_MEMORY]->(m)
            """,
            user_id=user_id, fact=fact
        )

def get_graph_memories(user_id: str, limit: int = 10):
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_MEMORY]->(m:Memory)
    RETURN m.text AS text, toString(m.created_at) AS created_at
    ORDER BY m.created_at DESC
    LIMIT $limit
    """
    with neo4j_driver.session() as session:
        results = session.run(query, user_id=user_id, limit=limit)
        return [record.data() for record in results]

def main():
    while True:
        user_input = input("🙅‍♂️ User > ")
        if user_input.lower() in ["exit", "quit"]:
            console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
            break

        # 1. Semantic Memory Search (Vector DB - Qdrant)
        relevent_data = memory.search(query=user_input, filters={"user_id": "genai"})
        vector_data = {}
        if 'results' in relevent_data:
            for msg in relevent_data['results']:
                id = msg['id']
                message = msg['memory']
                vector_data[id] = message # {'21e02547-fbc9-41f0-8bc9-8dd364843195' : 'Is from India'}

        # 2. Relational / Historical Memory (Graph DB - Neo4j)
        graph_data = get_graph_memories(user_id="genai")

        SYSTEM_PROMPT = f"""
            You are a memory aware AI agent who has access to both semantic and relational knowledge of the user.

            Vector Search Memories (from Qdrant):
            {vector_data}

            Graph Memory Timeline & Relationships (from Neo4j):
            {graph_data}
        """

        with timer(description="LLM generating text"):
            response = client.chat.completions.create(
                model=OPEN_ROUTER_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]
            )
            print(response.choices[0].message.content)

            added_memories = memory.add([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response.choices[0].message.content}
                ],
                user_id="genai"
            )
            if added_memories and "results" in added_memories:
                for item in added_memories["results"]:
                    fact = item.get("memory")
                    if fact:
                        sync_to_neo4j(user_id="genai", fact=fact)

if __name__ == '__main__':
    main()