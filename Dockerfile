FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

RUN poetry install --without dev --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
