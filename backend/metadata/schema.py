import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/analytics.db")


def get_database_schema():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """)

        tables = [row[0] for row in cursor.fetchall()]

        schema_parts = [
            "Database type: SQLite"
        ]

        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema_parts.append(f"\nTable: {table_name}")
            schema_parts.append("Columns:")

            for column in columns:
                column_name = column[1]
                column_type = column[2]

                schema_parts.append(
                    f"- {column_name} {column_type}"
                )

        return "\n".join(schema_parts)

    finally:
        connection.close()