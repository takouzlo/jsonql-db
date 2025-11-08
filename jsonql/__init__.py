# jsonql/__init__.py
"""
JSONQL – A lightweight, file-based JSON database with SQL-like syntax.
"""

from .core import JSONQL
from .query import QueryEngine

def connect(db_path: str = "db") -> JSONQL:
    db = JSONQL(db_path)
    # Inject query method dynamically
    db.query = QueryEngine(db).query
    return db