FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    ffmpeg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxfixes3 \
    libxkbcommon0 \
    libxshmfence1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libxss1 \
    libgdk-pixbuf-2.0-0 \
    fonts-liberation \
    fonts-unifont \
  && curl -sSL https://install.python-poetry.org | python3 - \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# download browsers only; don’t try to install OS deps
RUN playwright install chromium

COPY . .
EXPOSE 8080

ENTRYPOINT ["poetry", "run", "python", "main.py"]
CMD []
