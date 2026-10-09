import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INDEX_PATH = Path("backend/metadata/vector_index.json")

EMBEDDING_MODEL = "text-embedding-3-small"


def load_vector_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "Vector index not found. "
            "Run backend/metadata/build_index.py first."
        )

    with open(
        INDEX_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def search_metadata(query: str, top_k: int = 3):
    index = load_vector_index()

    query_embedding = get_embedding(query)

    scored_tables = []

    for item in index:
        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        scored_tables.append({
            "score": similarity,
            "table": item["table"],
            "columns": item["columns"]
        })

    scored_tables.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected_tables = []

    for item in scored_tables[:top_k]:
        selected_tables.append({
            "table": item["table"],
            "columns": item["columns"],
            "similarity_score": round(
                item["score"],
                4
            )
        })

    return selected_tables


def format_metadata_for_prompt(metadata):
    parts = [
        "Database type: SQLite"
    ]

    for table in metadata:
        parts.append(
            f"\nTable: {table['table']}"
        )

        parts.append("Columns:")

        for column in table["columns"]:
            parts.append(
                f"- {column['name']} "
                f"{column['type']}"
            )

    return "\n".join(parts)