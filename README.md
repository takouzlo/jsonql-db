# JSONQL-DB — Your Lightweight JSON Database

> **SQLite, but with human-readable JSON files.**  
> Zero setup. Zero server. Just pure Python and transparency.

[![PyPI](https://img.shields.io/pypi/v/jsonql-db.svg)](https://pypi.org/project/jsonql-db/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/jsonql-db)](https://pypi.org/project/jsonql-db/)

## ✨ Why JSONQL-DB?

| Feature          | SQLite        | JSONQL-DB               |
|------------------|---------------|-------------------------|
| **Storage**      | Binary        | **Human-readable JSON** |
| **Setup**        | Install       | **Zero install** (pure Python) |
| **Transparency** | Opaque        | **Everything is a file** |
| **Ideal for**    | Heavy apps    | **Prototypes, AV tools, edge devices, indie devs** |

✅ No server • ✅ Thread-safe • ✅ SQL-like queries • ✅ < 300 lines core

> ⚠️ **Not related to** [`json-ql`](https://pypi.org/project/json-ql/) or [`jsonql.js.org`](https://jsonql.js.org) — those are **JSON query utilities**, not databases.

---

## 🚀 Install


pip install jsonql-db


For the GUI browser (Flet-based):

pip install "jsonql-db[browser]"

Quick Start

    import jsonql

    # Connect (creates folder if needed)
    db = jsonql.connect("my_app_data")

    # Insert
    db.insert("devices", {"name": "Projector", "room": "A101", "ip": "192.168.1.10"})

    # Query
    devices = db.select("devices", {"room": "A101"})
    print(devices)

    # SQL-like
    result = db.query("SELECT * FROM devices WHERE room = 'A101'")
    print(result)


🖥️ GUI Browser
Launch the built-in browser:

python -m jsonql.browser

![JSONQL Browser](https://raw.githubusercontent.com/tonpseudo/jsonql-db/main/jqlFlet.png)


🧠 Philosophy
“If it’s not human-readable, it’s not transparent.”
JSONQL-DB is for developers who value simplicity, portability, and control. 

Perfect for:

- Audiovisual integrators (Crestron, QSC, Extron)
- IoT edge logging
- Local Flet/PyQt apps
- Teaching database basics


📜 License
MIT — see LICENSE

# demo.py
import jsonql

def main():
    db = jsonql.connect("demo_db")
    
    # Insert
    dev_id = db.insert("devices", {
        "name": "Epson L710U",
        "type": "projector",
        "room": "A101",
        "ip": "192.168.10.50"
    })
    print(f"✅ Inserted device ID: {dev_id}")

    # Select
    devices = db.select("devices", {"room": "A101"})
    print("🔍 Devices in A101:", devices)

    # SQL Query
    result = db.query("SELECT * FROM devices WHERE type = 'projector'")
    print("💻 SQL Result:", result)

if __name__ == "__main__":
    main()




