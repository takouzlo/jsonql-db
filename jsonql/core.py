# jsonql/core.py
import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class JSONQL:
    def __init__(self, db_path: Union[str, Path] = "db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}

    def _get_lock(self, table: str) -> threading.Lock:
        if table not in self._locks:
            self._locks[table] = threading.Lock()
        return self._locks[table]

    def _table_file(self, table: str) -> Path:
        return self.db_path / f"{table}.json"

    def _load_table(self, table: str) -> List[Dict[str, Any]]:
        file = self._table_file(table)
        if not file.exists():
            return []
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_table(self, table: str, data: List[Dict[str, Any]]) -> None:
        file = self._table_file(table)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_table(self, table: str) -> None:
        """Creates an empty table if it doesn't exist."""
        if not self._table_file(table).exists():
            self._save_table(table, [])

    def drop_table(self, table: str) -> None:
        """Deletes a table (file)."""
        file = self._table_file(table)
        if file.exists():
            file.unlink()

    def insert(self, table: str, record: Dict[str, Any]) -> int:
        """Inserts a record and returns its auto-generated ID."""
        self.create_table(table)
        with self._get_lock(table):
            data = self._load_table(table)
            new_id = max((r.get("id", 0) for r in data), default=0) + 1
            record = {**record, "id": new_id}
            data.append(record)
            self._save_table(table, data)
            return new_id

    def select(self, table: str, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Selects records. WHERE is a dict of exact key-value matches."""
        data = self._load_table(table)
        if where is None:
            return data
        return [
            row for row in data
            if all(row.get(k) == v for k, v in where.items())
        ]

    def update(self, table: str, record_id: int, updates: Dict[str, Any]) -> bool:
        """Updates a record by ID. Returns True if found and updated."""
        updates.pop("id", None)  # Never allow ID change
        with self._get_lock(table):
            data = self._load_table(table)
            for row in data:
                if row.get("id") == record_id:
                    row.update(updates)
                    self._save_table(table, data)
                    return True
            return False

    def delete(self, table: str, record_id: int) -> bool:
        """Deletes a record by ID. Returns True if deleted."""
        with self._get_lock(table):
            data = self._load_table(table)
            original_len = len(data)
            data = [row for row in data if row.get("id") != record_id]
            if len(data) != original_len:
                self._save_table(table, data)
                return True
            return False
        
    def drop_database(self) -> None:
        """Supprime TOUT le dossier de la base de données et son contenu."""
        import shutil
        if self.db_path.exists():
            shutil.rmtree(self.db_path)
        # Réinitialise l'état
        self.db_path.mkdir(exist_ok=True)
        self._locks.clear()

    def table_exists(self, table: str) -> bool:
        return self._table_file(table).exists()

    def list_tables(self) -> List[str]:
        return sorted(f.stem for f in self.db_path.glob("*.json"))