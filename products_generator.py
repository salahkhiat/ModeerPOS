import sqlite3
import random

# Connect to database
connection = sqlite3.connect("shop_data.db")
cursor = connection.cursor()

# Random product names
product_names = [
    "Laptop",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Phone",
    "Tablet",
    "Speaker",
    "Camera",
    "Printer",
    "Scanner",
    "Router",
    "Headphones",
    "Microphone",
    "SSD",
    "Hard Disk",
    "USB Cable",
    "Power Bank",
    "Smart Watch",
    "TV",
    "Projector"
]

# Generate 30 random products
for _ in range(30):

    barcode = random.randint(1000, 2000)

    name = f"{random.choice(product_names)} {random.randint(1, 999)}"

    purchase_price = round(
        random.uniform(20000.0, 50000.0), 2
    )

    sale_price = round(
        random.uniform(20000.0, 50000.0), 2
    )

    quantity = random.randint(1, 100)

    is_deleted = 0

    cursor.execute("""
        INSERT INTO products (
            barcode,
            name,
            purchase_price,
            sale_price,
            quantity,
            is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        barcode,
        name,
        purchase_price,
        sale_price,
        quantity,
        is_deleted
    ))

# Save changes
connection.commit()

# Close database
connection.close()

print("30 random products inserted successfully.")