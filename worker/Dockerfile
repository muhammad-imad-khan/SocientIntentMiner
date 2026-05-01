FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (worker imports from backend)
COPY backend/ /app/backend/
COPY worker/ /app/worker/

ENV PYTHONPATH=/app/backend

CMD ["python", "worker/worker.py"]
