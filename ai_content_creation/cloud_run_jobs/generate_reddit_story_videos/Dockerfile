FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    ffmpeg \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi


COPY . .

EXPOSE 8080

ENTRYPOINT ["poetry", "run", "python", "main.py"]
CMD []