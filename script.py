import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "shop_data.db"

pieces = [
    "Laptop screen", "Keyboard", "Motherboard", "Battery",
    "Cooling fan", "RAM module", "SSD drive", "Power supply",
    "Graphics card", "USB port", "Touchpad", "Speaker",
    "WiFi card", "Camera module", "Charging port"
]

statuses = ["in_shop", "installed", "returned"]

def random_date():
    start = datetime(2025, 1, 1)
    end = datetime(2026, 5, 1)
    delta = end - start

    random_seconds = random.randint(0, int(delta.total_seconds()))
    date = start + timedelta(seconds=random_seconds)

    return date.strftime("%Y-%m-%d %H:%M:%S")

def generate_rows(n=25):
    rows = []
    for _ in range(n):
        supplier_id = random.choice([1, 2])
        piece = random.choice(pieces)
        price = round(random.uniform(10, 500), 2)
        status = random.choice(statuses)
        created = random_date()

        rows.append((supplier_id, piece, price, status, created))
    
    return rows

def insert_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    rows = generate_rows(25)

    cursor.executemany("""
        INSERT INTO pieces_transactions
        (supplier_id, piece, price, status, created)
        VALUES (?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

    print(f"{len(rows)} rows inserted successfully!")

if __name__ == "__main__":
    insert_data()