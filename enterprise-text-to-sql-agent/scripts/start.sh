#!/bin/sh
set -e

if [ ! -f "data/app.db" ]; then
  python -m text2sql_agent.cli init-db
fi

exec uvicorn text2sql_agent.app:app --host 0.0.0.0 --port 8080
