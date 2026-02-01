import sqlite3

from text2sql_agent.schema import SchemaCache, introspect_schema


def test_schema_cache_saved(tmp_path):
    db_path = tmp_path / "app.db"
    cache_path = tmp_path / "schema.json"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE demo (id INTEGER)")
    snapshot = introspect_schema(f"sqlite:///{db_path}", SchemaCache(str(cache_path)))
    assert snapshot.schema_hash
    loaded = SchemaCache(str(cache_path)).load()
    assert loaded is not None
    assert loaded.schema_hash == snapshot.schema_hash
