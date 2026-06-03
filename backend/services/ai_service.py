# services/ai_service.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
# TODO:
# Migrate to google.genai SDK in future version

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")
def format_schema(schema):

    formatted = ""

    for table, columns in schema.items():

        formatted += f"Table: {table}\n"

        formatted += "Columns:\n"

        for column in columns:

            formatted += f"- {column}\n"

        formatted += "\n"

    return formatted

def generate_sql_from_question(
    question: str,
    schema: dict
):
    schema_text = format_schema(schema)
    prompt = f"""
You are a PostgreSQL expert.

Schema:
{schema_text}

Question:
{question}

Rules:
1. Return ONLY SQL.
2. No markdown.
3. No explanation.
4. Use only tables and columns from the schema.
"""

    response = model.generate_content(prompt)

    sql = response.text.strip()

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql
def get_schema_dict(engine):

    from sqlalchemy import inspect

    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)

        schema[table] = [
            column["name"]
            for column in columns
        ]

    return schema