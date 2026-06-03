from services.ai_service import generate_sql_from_question

schema = {
    "students": [
        "id",
        "name",
        "college",
        "year"
    ]
}

sql = generate_sql_from_question(
    "Show all students from ABC college",
    schema
)

print(sql)