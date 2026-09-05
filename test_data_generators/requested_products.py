import sqlite3
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect("shop_data.db")
cursor = conn.cursor()

# Random product names
products = [
    "Laptop", "Keyboard", "Mouse", "Monitor", "Printer",
    "Phone", "Tablet", "Speaker", "Camera", "Microphone",
    "Headphones", "Router", "USB Cable", "SSD", "Hard Drive",
    "Chair", "Desk", "Projector", "Smart Watch", "Power Bank"
]

# Generate 50 random rows
for _ in range(50):

    # Random product name
    product_name = random.choice(products)

    # Random date within last 365 days
    random_days = random.randint(0, 365)
    random_seconds = random.randint(0, 86400)

    random_date = datetime.now() - timedelta(
        days=random_days,
        seconds=random_seconds
    )

    # Format like: 2026-05-28 11:48:53
    created = random_date.strftime("%Y-%m-%d %H:%M:%S")

    # Insert into table
    cursor.execute("""
        INSERT INTO requested_products (name, created)
        VALUES (?, ?)
    """, (product_name, created))

# Save changes
conn.commit()

# Close connection
conn.close()

print("50 random products inserted successfully.")