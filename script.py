import sqlite3
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect("shop_data.db")  # change this
cursor = conn.cursor()

descriptions = [
    "Software debugging",
    "Hardware repair",
    "System setup",
    "Network configuration",
    "Data recovery",
    "Security check",
    "Performance optimization",
    "Backup service"
]

def random_datetime():
    now = datetime.now()
    random_days = random.randint(0, 15)
    random_seconds = random.randint(0, 86400)
    return (now - timedelta(days=random_days, seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

for _ in range(20):
    customer_id = 2  # ثابت
    category_id = random.randint(1, 3)
    description = random.choice(descriptions)

    default_price = round(random.uniform(80, 700), 2)
    paid_price = round(random.uniform(20, default_price), 2)

    created = random_datetime()

    cursor.execute("""
        INSERT INTO services 
        (customer_id, category_id, description, default_price, paid_price, created)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, category_id, description, default_price, paid_price, created))

conn.commit()
conn.close()

print("20 services inserted for customer_id = 2")