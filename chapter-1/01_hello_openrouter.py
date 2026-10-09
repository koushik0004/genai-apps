import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lib import timer

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPEN_ROUTER_OSS_MODEL", "qwen/qwen3.7-flash")

    if not api_key or api_key == "your_openrouter_api_key_here":
        print("⚠️ OPENROUTER_API_KEY is not set or using placeholder value.")
        print("Please set your real API key in the .env file in the root directory.")
        return

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    with timer("OpenRouter API call"):
        print(f"Sending prompt to model '{model}' via OpenRouter...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a 1-sentence motivation for a AI developer."}
            ]
        )

        print("\nResponse:")
        print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
