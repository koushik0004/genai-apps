import os
import sys
from rich.console import Console
from rich.markdown import Markdown as RichMarkdown

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", '..')))

# One-stop clean import
from lib import client, timer, OPEN_ROUTER_OSS_MODEL

console = Console()

SYSTEM_PROMPT = """
    You are a JavaScript AI export. 
    You solves query on javascript.
    make sure to response in a concise and clear manner (very brief).
    If user ask question not related to javascript, just tell them to ask javascript related questions only
"""

# if not api_key:
#     print("⚠️ OPENROUTER_API_KEY is not set or using placeholder value.")
#     print("Please set your real API key in the .env file in the root directory.")
#     exit(1)

while True:
    user_input = input("🙅‍♂️ User: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat. Goodbye!")
        break

    with timer("OpenRouter API call"):
        response = client.chat.completions.create(
            model=OPEN_ROUTER_OSS_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        print("\nResponse:")
        console.print(RichMarkdown(response.choices[0].message.content))