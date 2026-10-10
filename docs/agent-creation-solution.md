# ReAct Agent Loop Analysis & Fix

## Problem Overview

When executing [`chapter-3/main.py`](file:///Users/koushiksadhukhan/projects/genai-apps/chapter-3/main.py), the ReAct agent entered an infinite loop after invoking the `get_weather` tool. Instead of transitioning to the `Result` step after receiving the `Observe` output, it repeatedly issued the same `Action` step:

```text
🙅‍♂️ User > what is the current weather of Delhi?
🪜 Analyse: The user is requesting the current weather information for Delhi. 
🪜 Plan: I need to call the get_weather tool to retrieve the current weather for Delhi. 
🪓 Tool = get_weather and Input = Delhi
🪜 Observe: The current weather in Delhi, India is 25.7°C and Clear sky. 
🪓 Tool = get_weather and Input = Delhi
... (Repeated indefinitely)
```

---

## Root Cause Analysis

### 1. Missing `Action` Step in Conversation History (`messages`)
In the original implementation:
- The model generated an `Action` response: `{"step": "Action", "tool": "get_weather", "input": "Delhi"}`.
- The code executed the tool and appended the `Observe` message to `messages`.
- A `continue` statement immediately jumped to the next loop iteration, **skipping the line that appends `resp` (`Action`) to `messages`**.

As a result, the model's message history on the next iteration became:
- `User`: *"What is the weather of Delhi?"*
- `Assistant`: `{"step": "Observe", "content": "The current weather in Delhi..."}`

Because the model received an `Observe` step without seeing its preceding `Action` step, the LLM context became invalid. The model repeatedly re-sent the `Action` step in an attempt to satisfy the query.

### 2. Typo in Few-Shot Message Roles (`"assistance"`)
The initial few-shot conversation history in `messages` used `"role": "assistance"` instead of standard `"role": "assistant"`. Invalid role keys are ignored or mishandled by OpenAI-compatible backends, rendering few-shot context ineffective.

### 3. System Prompt Tool Name Mismatch
In `SYSTEM_PROMPT`, example calls referenced `"getWeather"`, whereas the Python dispatch map `AVAIABLE_TOOLS_MAP` was keyed on `'get_weather'`.

---

## Expected & Implemented File Changes

File: [`chapter-3/main.py`](file:///Users/koushiksadhukhan/projects/genai-apps/chapter-3/main.py)

### Change 1: Record Assistant Responses Before Step Evaluation

Move `messages.append({"role": "assistant", "content": json.dumps(resp)})` so that every assistant response (`Analyse`, `Plan`, `Action`, `Result`) is recorded in conversation history immediately upon receipt:

```python
    while True:
        response = client.chat.completions.create(
                    model=GEMINI_GEMMA_MODEL,
                    messages=messages
                )
        resp = json.loads(response.choices[0].message.content)
        # Record model response to message history FIRST
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
```

### Change 2: Correct Role Names in Few-Shot History

Update role values from `"assistance"` to `"assistant"`:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "What is the weather of Bengaluru?"},
    {"role": "assistant", "content": json.dumps({"step": "Analyse", "content": "The user is requesting..."})},
    {"role": "assistant", "content": json.dumps({"step": "Plan", "content": "I need to retrieve..."})},
    {"role": "assistant", "content": json.dumps({"step": "Action", "tool": "get_weather", "input": "Bengaluru"})},
    {"role": "assistant", "content": json.dumps({"step": "Observe", "content": "24 degrees Celsius and cloudy"})},
]
```

### Change 3: Align System Prompt Tool References

Update `SYSTEM_PROMPT` example references from `getWeather` to `get_weather`.
