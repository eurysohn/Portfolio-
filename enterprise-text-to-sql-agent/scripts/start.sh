#!/bin/sh
set -e

# Always initialize database on startup to ensure fresh data
echo "Initializing database..."
python -m text2sql_agent.cli init-db

exec uvicorn text2sql_agent.app:app --host 0.0.0.0 --port 8080
