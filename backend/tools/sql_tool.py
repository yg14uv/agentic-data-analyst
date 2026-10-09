import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/analytics.db")


def execute_sql(query: str):
    cleaned_query = query.strip()

    if not cleaned_query.lower().startswith("select"):
        return {
            "success": False,
            "error": "Only SELECT queries are allowed."
        }

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(cleaned_query)

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        return {
            "success": True,
            "columns": columns,
            "rows": rows
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "error": str(error)
        }

    finally:
        connection.close()