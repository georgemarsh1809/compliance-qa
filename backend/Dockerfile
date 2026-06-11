# backend/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install deps
COPY requirements.txt .
RUN pip install uv --no-cache-dir
RUN uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
