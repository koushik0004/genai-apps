from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from lib import base_url, api_key, timer, OPEN_ROUTER_MODEL, GEMINI_GEMMA_MODEL, TEXT_EMBEDDING_MODEL
from lib.utility import timer


# Initialize the loader
# Ingestion
file_path = "chapter-4/rag-2/python.pdf"
def load_pdf(file_path) -> list[Document]: 
    reader = PdfReader(file_path)
    return [
        Document(
            page_content=page.extract_text() or "", 
            metadata={"source": file_path, "page": reader.metadata['page_number'] if 'page_number' in reader.metadata else i + 1}
        )
        for i, page in enumerate(reader.pages)
    ]
docs = load_pdf(file_path)
print(docs[0])

#     Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=500,
    add_start_index=True,
)
splitted_docs = text_splitter.split_documents(docs)

# Vector Embaddings
embeddings_model = OpenAIEmbeddings(
    model=TEXT_EMBEDDING_MODEL,
    api_key=api_key,
    base_url=base_url,
    check_embedding_ctx_length=False,
)

with timer("Ingestion"):
    # Store In Vector DB (Qdrant DB) - "splited_docs" convert to vectore embadding using "embeddings_model"
    vectore_store = QdrantVectorStore.from_documents(
        url="http://localhost:6333",
        collection_name="genai",
        embedding=embeddings_model,
        documents=splitted_docs
    )
    print("Ingestion is completed")