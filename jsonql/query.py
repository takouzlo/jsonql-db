# jsonql/query.py
import re
from typing import Any, Dict, List, Union
from .core import JSONQL

class QueryEngine:
    def __init__(self, db: JSONQL):
        self.db = db

    def query(self, sql: str) -> Union[List[Dict], Dict[str, Any]]:
        sql_clean = sql.strip().rstrip(";").strip()
        if not sql_clean:
            return {"error": "Empty query"}

        upper = sql_clean.upper()
        if upper.startswith("SELECT"):
            return self._handle_select(sql_clean)
        elif upper.startswith("INSERT"):
            return self._handle_insert(sql_clean)
        elif upper.startswith("UPDATE"):
            return self._handle_update(sql_clean)
        elif upper.startswith("DELETE"):
            return self._handle_delete(sql_clean)
        else:
            return {"error": "Only SELECT, INSERT, UPDATE, DELETE are supported"}

    def _handle_select(self, sql: str) -> List[Dict]:
        match = re.match(r"SELECT\s+\*\s+FROM\s+(\w+)(?:\s+WHERE\s+(\w+)\s*=\s*['\"]?([^'\"\s]+)['\"]?)?", sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT. Use: SELECT * FROM table [WHERE key=value]")

        table = match.group(1)
        if not self.db.table_exists(table):
            return [{"error": f"Table '{table}' does not exist"}]

        if match.group(2):
            key = match.group(2)
            value = self._cast_value(match.group(3))
            return self.db.select(table, {key: value})
        else:
            return self.db.select(table)

    def _handle_insert(self, sql: str) -> Dict[str, Any]:
        match = re.search(
            r"INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)",
            sql, re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid INSERT. Example: INSERT INTO devices (name, room) VALUES ('Projo', 'A101')")

        table = match.group(1)
        columns = [c.strip() for c in match.group(2).split(",")]
        raw_values = [v.strip().strip("'\"") for v in match.group(3).split(",")]

        if len(columns) != len(raw_values):
            raise ValueError("Column count mismatch")

        record = {}
        for col, val in zip(columns, raw_values):
            record[col] = self._cast_value(val)

        record_id = self.db.insert(table, record)
        return {"status": "inserted", "id": record_id}

    def _handle_update(self, sql: str) -> Dict[str, Any]:
        # UPDATE table SET key=value WHERE id=1
        match = re.search(
            r"UPDATE\s+(\w+)\s+SET\s+(\w+)\s*=\s*['\"]?([^'\"\s]+)['\"]?\s+WHERE\s+(\w+)\s*=\s*['\"]?([^'\"\s]+)['\"]?",
            sql, re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid UPDATE. Example: UPDATE devices SET ip='192.168.1.10' WHERE id=1")

        table, set_key, set_val, where_key, where_val = match.groups()
        if not self.db.table_exists(table):
            return {"error": f"Table '{table}' does not exist"}

        where_val = self._cast_value(where_val)
        set_val = self._cast_value(set_val)

        # Trouver l'ID cible (on suppose WHERE sur un champ unique, souvent 'id')
        candidates = self.db.select(table, {where_key: where_val})
        if not candidates:
            return {"status": "no rows updated"}

        updated = 0
        for row in candidates:
            if self.db.update(table, row["id"], {set_key: set_val}):
                updated += 1
        return {"status": "updated", "rows": updated}

    def _handle_delete(self, sql: str) -> Dict[str, Any]:
        # DELETE FROM table WHERE id=1
        match = re.search(
            r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+(\w+)\s*=\s*['\"]?([^'\"\s]+)['\"]?",
            sql, re.IGNORECASE
        )
        if not match:
            raise ValueError("Invalid DELETE. Example: DELETE FROM devices WHERE id=1")

        table, where_key, where_val = match.groups()
        if not self.db.table_exists(table):
            return {"error": f"Table '{table}' does not exist"}

        where_val = self._cast_value(where_val)
        candidates = self.db.select(table, {where_key: where_val})
        if not candidates:
            return {"status": "no rows deleted"}

        deleted = 0
        for row in candidates:
            if self.db.delete(table, row["id"]):
                deleted += 1
        return {"status": "deleted", "rows": deleted}

    def _cast_value(self, value: str):
        if value.isdigit():
            return int(value)
        if value.replace(".", "").replace("-", "", 1).isdigit():
            return float(value)
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        return value