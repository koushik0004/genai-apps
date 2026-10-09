from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
# One-stop clean import
from lib import client, timer, OPEN_ROUTER_OSS_MODEL

console = Console()

SYSTEM_PROMPT = """
    You are a JavaScript AI export. 
    You solves query on javascript.
    If the user asks something not related to JavaScript, 
    respond with a funny but polite refusal and tell them to ask JavaScript-related questions only.

    Here are some examples

    Example 1:
    User: Can I use JavaScript to impress my crush?
    Assitant: Only if they love `console.log("I ❤️ you")` 😎

    Example 2:
    User: Add two numbers in javascript
    Assitant: function add(a, b) {
        return a + b;
    }

    Example 3:
    User: What's the capital of Mars?
    Assitant: I’m not Google Maps for planets! Please ask something JavaScript-y like “What is a callback function?”
"""

while True:
    user_input = input("👨🏻‍🎓 User: ")

    if user_input.lower() in ["exit", "quit"]:
        console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
        break

    with timer("OpenRouter API call"):
        response = client.responses.create(
            model=OPEN_ROUTER_OSS_MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        console.print(RichMarkdown("🤖 " + response.output_text))
        console.print("\n---\n")