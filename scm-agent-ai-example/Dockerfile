# Stage 1: Frontend Build
FROM node:20-slim as frontend-builder
WORKDIR /app/frontend-ts
COPY frontend-ts/package.json ./
RUN npm install
COPY frontend-ts/ ./
RUN npm run build

# Stage 2: Backend Build
FROM python:3.10-slim as backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final Stage
FROM python:3.10-slim
WORKDIR /app

# Copy python packages
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY . .

# Copy frontend build artifacts
COPY --from=frontend-builder /app/frontend-ts/dist ./frontend-ts/dist

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
