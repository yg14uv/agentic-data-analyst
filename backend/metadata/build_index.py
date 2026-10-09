import json
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = Path("backend/data/analytics.db")

INDEX_PATH = Path("backend/metadata/vector_index.json")

EMBEDDING_MODEL = "text-embedding-3-small"


def get_metadata_catalog():
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

        table_names = [row[0] for row in cursor.fetchall()]

        catalog = []

        for table_name in table_names:
            cursor.execute(
                f"PRAGMA table_info({table_name})"
            )

            columns = cursor.fetchall()

            column_metadata = []

            for column in columns:
                column_metadata.append({
                    "name": column[1],
                    "type": column[2]
                })

            catalog.append({
                "table": table_name,
                "columns": column_metadata
            })

        return catalog

    finally:
        connection.close()


def build_metadata_text(table):
    column_text = ", ".join(
        f"{column['name']} ({column['type']})"
        for column in table["columns"]
    )

    return (
        f"Table name: {table['table']}. "
        f"Columns: {column_text}. "
        f"This table may be used to answer analytics "
        f"questions related to these fields."
    )


def get_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


def build_vector_index():
    catalog = get_metadata_catalog()

    index = []

    for table in catalog:
        metadata_text = build_metadata_text(table)

        embedding = get_embedding(metadata_text)

        index.append({
            "table": table["table"],
            "columns": table["columns"],
            "metadata_text": metadata_text,
            "embedding": embedding
        })

        print(
            f"Embedded metadata for table: "
            f"{table['table']}"
        )

    with open(
        INDEX_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            index,
            file
        )

    print(
        f"Vector index saved to: {INDEX_PATH}"
    )


if __name__ == "__main__":
    build_vector_index()