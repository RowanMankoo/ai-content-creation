FROM python:3.10-slim

WORKDIR /app

# system deps + Playwright libraries
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
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libxss1 \
    fonts-liberation \
  && curl -sSL https://install.python-poetry.org | python3 - \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi
RUN playwright install --with-deps

COPY . .

EXPOSE 8080

ENTRYPOINT ["poetry", "run", "python", "main.py"]
CMD []