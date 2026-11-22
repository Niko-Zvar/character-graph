FROM python:3.12-slim

# uv — менеджер зависимостей, копируем готовый бинарник из официального образа
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Сначала ставим только зависимости: этот слой кэшируется, пока не меняется uv.lock
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

# Затем копируем код и ставим сам проект
COPY src ./src
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "character_graph.main:app", "--host", "0.0.0.0", "--port", "8000"]
