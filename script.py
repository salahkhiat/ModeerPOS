import sqlite3
import random
from datetime import datetime, timedelta

# Connect to your database
conn = sqlite3.connect("shop_data.db")  # change this
cursor = conn.cursor()

descriptions = [
    "Repair service",
    "Installation",
    "Maintenance",
    "Consultation",
    "Upgrade",
    "Cleaning service",
    "Technical support",
    "Inspection"
]

def random_datetime():
    now = datetime.now()
    random_days = random.randint(0, 30)
    random_seconds = random.randint(0, 86400)
    return (now - timedelta(days=random_days, seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

for _ in range(20):
    customer_id = random.randint(1, 5)
    category_id = random.randint(1, 3)
    description = random.choice(descriptions)
    
    default_price = round(random.uniform(50, 500), 2)
    
    # paid_price can be <= default_price or equal
    paid_price = round(random.uniform(0, default_price), 2)
    
    created = random_datetime()

    cursor.execute("""
        INSERT INTO services 
        (customer_id, category_id, description, default_price, paid_price, created)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, category_id, description, default_price, paid_price, created))

# Commit and close
conn.commit()
conn.close()

print("20 random services inserted successfully.")