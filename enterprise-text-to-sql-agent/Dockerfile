FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml /app/
COPY src /app/src
COPY data /app/data
COPY eval /app/eval
COPY tests /app/tests
COPY README.md /app/README.md

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "text2sql_agent.cli", "ask", "order fill rate last 30 days"]
