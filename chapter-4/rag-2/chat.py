from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from rich.markdown import Markdown as RichMarkdown
from rich.console import Console

from lib import client, timer, api_key, base_url, GEMINI_GEMMA_MODEL
from lib.utility import TEXT_EMBEDDING_MODEL

console = Console()

# 2. Retrival
#     User input
user_input = input("User >> ")
#     Vecor Embadding
embeddings_model = OpenAIEmbeddings(
    model=TEXT_EMBEDDING_MODEL,
    api_key=api_key,
    base_url=base_url,
    check_embedding_ctx_length=False,
)
#     Retrive from vector DB
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="genai",
    embedding=embeddings_model
)

get_chunks = vector_db.similarity_search(
    query=user_input
)

def get_chunks_content():
    output = []
    no_of_chunks = len(get_chunks)

    for chunk_no in range(no_of_chunks):
        output.append({
            "page_number": get_chunks[chunk_no].metadata.get("page", "N/A"),
            "chunk_number": chunk_no + 1,
            "chunk_content": get_chunks[chunk_no].page_content
        })
    return output

# 3. Generate
    # User input and retrived chunks put it in LLM
SYSTEM_PROMPT = f"""
    You are an AI expert assistant. Your job is to answer user queries using ONLY the information provided in the "Context" section. 
    If a user asks a question that cannot be answered from the context, politely decline and explain that the information is not available.

    ---
    ### Context
    {get_chunks_content()}
    ---

    ### Rules
    1. Use only the provided context when answering.
    2. Keep answers concise, clear, and professional.
    3. If the answer exists in the context, include the **page number** where it was found.
    4. If the information is not in the context, respond politely:
    - Example: "I don't have information on this topic. Sorry!"
    5. Do not make up facts or provide external knowledge.

     ---

    ### Examples

    Example 1: 
    User: When was Python language created?
    Assistant: Python was released in 1991.  
    (Found in page no: 1)

    **Example 2**  
    User: Who is Salman Khan?  
    Assistant: I don’t have information on this topic. Sorry!
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_input}
]

with timer(description="OpenRouter API call"):
    response = client.chat.completions.create(
        model=GEMINI_GEMMA_MODEL,
        messages=messages
    )
    console.print(RichMarkdown(f" 🤖 Assistant >> {response.choices[0].message.content}"))
    