FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Instalar dependências do sistema
# ADICIONADO: tesseract-ocr e tesseract-ocr-por
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# Instala PyTorch CPU-only primeiro
# Depois sincroniza o resto das dependências
RUN uv pip install --system torch --index-url https://download.pytorch.org/whl/cpu && \
    uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "litestar", "--app", "src.app:app", "run", "--host", "0.0.0.0", "--port", "8000"]