import sqlite3
import random
from datetime import datetime, timedelta

# Connect to DB
conn = sqlite3.connect("shop_data.db")
cursor = conn.cursor()

notes = [
    "Payment received",
    "Partial settlement",
    "Invoice correction",
    "Monthly supply",
    "Urgent order",
    "Advance payment",
    "Credit adjustment",
    "Stock replenishment",
    "Refund",
    "Discount applied"
]

def random_datetime(start, end):
    """Generate random datetime between two datetimes"""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

start_date = datetime(2026, 1, 1, 0, 0, 0)
end_date = datetime(2026, 5, 11, 23, 59, 59)

for _ in range(50):

    supplier_id = random.choice([1, 2])
    note = random.choice(notes)
    amount = round(random.uniform(2000.0, 50000.0), 2)
    tx_type = random.choice(["deposit", "debt"])
    created = random_datetime(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO suppliers_transactions (
            supplier_id,
            note,
            amount,
            type,
            created
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        supplier_id,
        note,
        amount,
        tx_type,
        created
    ))

conn.commit()
conn.close()

print("50 supplier transactions inserted successfully.")