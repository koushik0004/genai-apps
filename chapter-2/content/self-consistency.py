from collections import Counter
import random

from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
import json
# One-stop clean import
from lib import client, timer, OPEN_ROUTER_OSS_MODEL, OPEN_ROUTER_MODEL, OPENAI_NANO_MODEL, MISTRAL_NEMO_MODEL
from lib.utility import DEEPSEEK_V4_FLASH_MODEL, QWEN_MODEL

console = Console()

SYSTEM_PROMPT = """
    Give me one word answer to the question asked by user.
"""

user_input = input("👨🏻‍🎓 User: ")

if user_input.lower() in ["exit", "quit"]:
    console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
    exit()

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_input},
]

_last_model = None

def get_model_choice():
    global _last_model
    models = [
        QWEN_MODEL,
        OPEN_ROUTER_MODEL,
        OPEN_ROUTER_OSS_MODEL,
        OPENAI_NANO_MODEL,
        MISTRAL_NEMO_MODEL,
        DEEPSEEK_V4_FLASH_MODEL
    ]
    available_models = [m for m in models if m != _last_model]
    chosen_model = random.choice(available_models)
    _last_model = chosen_model
    return chosen_model

def response_with_model(model):
    response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.8,
            )
    return response.choices[0].message.content

def findFrequency(answers):
    counter = Counter(answers)
    with timer("Stat - Frequency of answers"):
        print("Final Answer = ", counter.most_common(1)[0])

answers = []
for llm_calling in range(10):
    model_choice = get_model_choice()
    with timer(f"OpenRouter API call with {model_choice}"):
        answer = response_with_model(model_choice)
        answers.append(answer)
        console.print(RichMarkdown(f"🤖 {user_input}: {answer}"))
        console.print("\n---\n")

findFrequency(answers)