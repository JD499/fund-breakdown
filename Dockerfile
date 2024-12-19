FROM python:3.13.1-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .


RUN python -m venv .venv && \
    . .venv/bin/activate && \
    uv sync --frozen --no-cache


EXPOSE 8000


CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]