FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml /app/
COPY src /app/src
COPY data /app/data
COPY eval /app/eval
COPY tests /app/tests
COPY README.md /app/README.md
COPY scripts /app/scripts

RUN pip install --no-cache-dir -e .

CMD ["/bin/sh", "/app/scripts/start.sh"]
