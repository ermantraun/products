FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend backend

ENV DATABASE_URL=sqlite:///./test.db

CMD ["uvicorn", "backend.api.v1.main:app", "--host", "0.0.0.0", "--port", "8000"]