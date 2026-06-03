# services/sql_service.py

def is_safe_query(sql: str):

    sql = sql.strip().upper()

    return (
        sql.startswith("SELECT")
        or sql.startswith("WITH")
    )