FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app

COPY . .

RUN uv sync

CMD ["uv", "run", "ovh-dns-sync.py"]