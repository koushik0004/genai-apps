import os
import time
from openai import OpenAI
from contextlib import contextmanager
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables relative to this file's location (root directory)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

# 2. Extract environment variables
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.getenv("OPENROUTER_API_KEY")

# 3. Extract Model Names from .env
MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "google/gemini-2.5-flash")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen/qwen3.7-flash")
OPEN_ROUTER_MODEL = os.getenv("OPEN_ROUTER_MODEL", "openai/gpt-4o-mini")
OPEN_ROUTER_OSS_MODEL = os.getenv("OPEN_ROUTER_OSS_MODEL", "openai/gpt-oss-120b")
OPENAI_NANO_MODEL = os.getenv("OPENAI_NANO_MODEL", "openai/gpt-4.1-nano")
ANTHROPIC_HAIKU_MODEL = os.getenv("ANTHROPIC_HAIKU_MODEL", "anthropic/claude-haiku-5.5:batch")
MISTRAL_NEMO_MODEL = os.getenv("MISTRAL_NEMO_MODEL", "mistralai/mistral-nemo")
DEEPSEEK_V4_FLASH_MODEL = os.getenv("DEEPSEEK_V4_FLASH_MODEL", "deepseek/deepseek-v4-flash-0731")

# 4. Instantiate shared client
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

console = Console()

@contextmanager
def timer(description="Code block"):
    # Start the spinner loader with custom styling/spinner type
    with console.status(f"[bold green]{description}...[/bold green]", spinner="dots"):
        start = time.perf_counter()
        try:
            yield
        finally:
            end = time.perf_counter()
            console.print(f"[bold blue]✓ {description}[/bold blue] Elapsed time: [bold yellow]{end - start:.4f}[/bold yellow] seconds")