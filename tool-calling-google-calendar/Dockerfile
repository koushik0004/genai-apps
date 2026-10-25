FROM python:3.12-slim

# Install uv from official binary image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Ensure Python output is unbuffered, set PYTHONPATH for root modules (like lib/), and set PATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH="/app" \
    PATH="/app/tool-calling-google-calendar/.venv/bin:$PATH"

# Copy project definition for uv lock and sync inside container
COPY tool-calling-google-calendar/pyproject.toml /app/tool-calling-google-calendar/

# Set working directory to the project directory where pyproject.toml lives
WORKDIR /app/tool-calling-google-calendar

# Generate lockfile and synchronize dependencies strictly inside Docker container
RUN uv lock && uv sync --no-install-project

# Copy entire codebase
COPY . /app

EXPOSE 5000

# Run Flask application using the project virtualenv
CMD ["uv", "run", "python", "app.py"]
