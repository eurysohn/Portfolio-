import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy import create_engine, inspect


@dataclass
class TableSchema:
    name: str
    columns: Dict[str, str]


@dataclass
class SchemaSnapshot:
    tables: List[TableSchema]
    schema_hash: str


class SchemaCache:
    def __init__(self, cache_path: str = ".cache/schema.json") -> None:
        self.cache_path = cache_path
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    def load(self) -> Optional[SchemaSnapshot]:
        if not os.path.exists(self.cache_path):
            return None
        with open(self.cache_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        tables = [
            TableSchema(name=table["name"], columns=table["columns"])
            for table in payload["tables"]
        ]
        return SchemaSnapshot(tables=tables, schema_hash=payload["schema_hash"])

    def save(self, snapshot: SchemaSnapshot) -> None:
        payload = {
            "tables": [
                {"name": table.name, "columns": table.columns} for table in snapshot.tables
            ],
            "schema_hash": snapshot.schema_hash,
        }
        with open(self.cache_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)


def _compute_hash(tables: List[TableSchema]) -> str:
    raw = json.dumps(
        [{"name": table.name, "columns": table.columns} for table in tables],
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def introspect_schema(db_url: str, cache: Optional[SchemaCache] = None) -> SchemaSnapshot:
    if cache:
        cached = cache.load()
        if cached:
            return cached
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables: List[TableSchema] = []
    for table_name in sorted(inspector.get_table_names()):
        columns = {
            column["name"]: str(column["type"])
            for column in inspector.get_columns(table_name)
        }
        tables.append(TableSchema(name=table_name, columns=columns))
    snapshot = SchemaSnapshot(tables=tables, schema_hash=_compute_hash(tables))
    if cache:
        cache.save(snapshot)
    return snapshot


def schema_as_dict(snapshot: SchemaSnapshot) -> Dict[str, Dict[str, str]]:
    return {table.name: table.columns for table in snapshot.tables}
