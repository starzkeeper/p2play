FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# For normal executing files inside tasks
WORKDIR /app/backend
ENV PYTHONPATH=/app/backend:/app/

# Configure poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Install dependencies
COPY .env ./
COPY backend/pyproject.toml ./

# Load sources (COPY command not copy directories, load only files inside)
COPY backend/backend ./backend

RUN poetry lock
RUN poetry install
