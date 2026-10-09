import sqlite3
from pathlib import Path

db_path = Path("backend/data/analytics.db")

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    order_id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    product TEXT NOT NULL,
    country TEXT NOT NULL,
    revenue REAL NOT NULL
)
""")

sample_data = [
    (1, "2026-09-03", "Laptop", "Canada", 1200.00),
    (2, "2026-09-08", "Monitor", "Canada", 450.00),
    (3, "2026-09-12", "Laptop", "United States", 1350.00),
    (4, "2026-09-18", "Keyboard", "Canada", 120.00),
    (5, "2026-09-25", "Monitor", "United States", 500.00),
]

cursor.executemany("""
INSERT OR REPLACE INTO sales (
    order_id,
    order_date,
    product,
    country,
    revenue
)
VALUES (?, ?, ?, ?, ?)
""", sample_data)

connection.commit()
connection.close()

print(f"Database created and sample data inserted at: {db_path}")