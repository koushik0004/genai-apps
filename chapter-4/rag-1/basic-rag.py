from pypdf import PdfReader
from rich.console import Console
from lib import client, timer, GEMINI_GEMMA_MODEL

pdf_path = "chapter-4/rag-1/sample_python.pdf"
console = Console()

def read_pdf(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    output = []
    for page in range(number_of_pages):
        output.append({
            "page_number": page+1,
            "page_content": reader.pages[page].extract_text()
        })
    return output

SYSTEM_PROMPT = f"""
    You are an AI expert assistant. Your job is to answer user queries using ONLY the information provided in the "Context" section. 
    If a user asks a question that cannot be answered from the context, politely decline and explain that the information is not available.

    ---
    ### Context
    {read_pdf(pdf_path)}
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
]

if __name__ == "__main__":
    # pdf_content = read_pdf(pdf_path)
    # print(f"Extracted content from {pdf_path}:")
    # for page in pdf_content:
    #     print(f"Page {page['page_number'] + 1}:")
    #     print(page['page_content'])
    #     print("\n---\n")
    while True:
        user_input = input("🙅‍♂️ User > ")
        if user_input.lower() in ["exit", "quit"]:
            console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
            exit()

        messages.append({"role": "user", "content": user_input})
        with timer(description="OpenRouter API call"):
            response = client.chat.completions.create(
                        model=GEMINI_GEMMA_MODEL,
                        messages=messages
            )
            extracted_content = response.choices[0].message.content
            console.print(f"🤖 Assistant: {extracted_content}")
            messages.append({"role": "assistant", "content": extracted_content})
                