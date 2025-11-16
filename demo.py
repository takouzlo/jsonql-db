# jsonql/demo.py
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
    print("Inserted device with ID:", dev_id)

    # Select all
    print("\nAll devices:")
    for dev in db.select("devices"):
        print(dev)

    # SQL-like query
    print("\nQuery result (SQL-like):")
    result = db.query("SELECT * FROM devices WHERE room = 'A101'")
    print(jsonql.json.dumps(result, indent=2))

if __name__ == "__main__":
    main()