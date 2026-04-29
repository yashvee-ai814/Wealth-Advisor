FROM python:3.12-slim

WORKDIR /app

# Install uv — the fast Python package manager
RUN pip install uv

# Copy dependency definition and application code
COPY pyproject.toml .
COPY app/ ./app/

# Install all dependencies declared in pyproject.toml
RUN uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
