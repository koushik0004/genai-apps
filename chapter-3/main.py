from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
from rich.json import JSON as RichJSON
import json
# One-stop clean import
from lib import client, get_current_weather, timer, OPEN_ROUTER_OSS_MODEL, OPEN_ROUTER_MODEL, GEMINI_GEMMA_MODEL

console = Console()

def get_weather(place="Bengaluru"):
    weather = get_current_weather(place, country_code="IN")
    return f"The current weather in {weather['city']} is {weather['temperature_c']}°C and {weather['condition']}."
    # return "The current weather in Bengaluru is 24°C and cloudy."

AVAIABLE_TOOLS_MAP = {
    'get_weather': get_weather,
    # 'conversionRate': conversionRate,
    # 'systemCommand': systemCommand
}
# SYSTEM_PROMPT = f"""
#     You are a helpful AI expert who solves user queries.

#     current time {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

#     Mumbai weather is 30°C and sunny.
#     Delhi weather is 40°C and sunny.
# """

SYSTEM_PROMPT = """
    You are a helpful AI expert who solves user queries step by step using strict reasoning and structured thinking.

    You must follow these fixed stages in every conversation:
    Analyse → Plan → Action → Observe → Result methodology for every task.

    Description of Each Step:
    1. Analyse - Analyze and interpret the user's query.
    2. Plan - Decide which available tool(s) should be used.
    3. Action - Call only one tool with relevant input.
    4. Observe - Wait for the output (observation) from the tool call.
    5. Result - Generate a final answer for the user based on observations.

    Rules
   - Never skip any step — You must go through each stage one by one in order.
   - Only one function call per `Action` step.
   - Never call a function before reaching the `Action` step.
   - You can only proceed to `analyze` after an actual output is observed.
   - You must handle unknown or unclear queries by stating you're unable to solve them with the available tools.
   - Do not answer the final user query until the `Result` step.
   - You must follow the output json format.

   Output JSON format:
   {
       "step": "string",
       "content": "string",
       "tool": "The name of the tool if step is Action",
       "input": "The input parameter for the tool",
       "output": "The final result if step is Result"
   }

   Available Tools:
   - "get_weather": Accepts the place name as input and return the current weather of that location

   Example:
   User: What is the weather of Delhi?
   Output: {"step": "Analyse", "content": "The user is interesetd in weather data of Delhi" }
   Output: {"step": "Plan", "content": "From the available tools I need to call the get_weather" }
   Output: {"step": "Action", "tool": "get_weather", "input": "Delhi" }
   Output: {"step": "Observe", "content": "32 degree celecious" }
   Output: {"step": "Result", "output": "Delhi weather is 32 C" }

"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    user_input = input("🙅‍♂️ User > ")
    if user_input.lower() in ["exit", "quit"]:
        console.print(f"[bold yellow]✓ Exiting.. [/bold yellow] Goodbye!")
        exit()

    messages.append({"role": "user", "content": user_input})
    
    while True:
        response = client.chat.completions.create(
                    model=GEMINI_GEMMA_MODEL,
                    messages=messages
                )
        resp = json.loads(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(resp)})

        if resp['step'] == 'Action':
            tool_name = resp['tool']
            tool_input = resp['input']
            print(f"🪓 Tool = {tool_name} and Input = {tool_input}")

            if tool_name in AVAIABLE_TOOLS_MAP:
                tool_resp = AVAIABLE_TOOLS_MAP[tool_name](tool_input)
                messages.append({"role": "assistant", "content": json.dumps({"step": "Observe", "content": tool_resp })})
                print(f"🪜 Observe: {tool_resp} ")
                continue

        if resp['step'] == 'Result':
            print(f"🤖 {resp['step']}: {resp['output']} ")
            break

        print(f"🪜 {resp['step']}: {resp['content']} ")

    # console.print(RichMarkdown(response.choices[0].message.content))
    
        
    
