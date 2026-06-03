from fastapi.middleware.cors import CORSMiddleware
from schemas import StudentCreate, DatabaseConnectionCreate, QueryRequest, SQLRequest, ExecuteSQLRequest, AskDatabaseRequest
from models import (
    Student,
    DatabaseConnection,
    QueryHistory
)
from fastapi import HTTPException
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect
from services.ai_service import generate_sql_from_question

from database import get_db
from services.sql_service import is_safe_query
from services.ai_service import (
    generate_sql_from_question,
    get_schema_dict
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    new_student = Student(
        name=student.name,
        college=student.college,
        year=student.year
    )

    db.add(new_student)
    db.commit()

    return {"message": "Student added to PostgreSQL"}


@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()

    return students
@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: StudentCreate,
    db: Session = Depends(get_db)
):
    
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.name = updated_student.name
    student.college = updated_student.college
    student.year = updated_student.year

    db.commit()

    return {
        "message": "Student updated successfully"
    }
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }
@app.post("/database-connections")
def create_database_connection(
    connection: DatabaseConnectionCreate,
    db: Session = Depends(get_db)
):

    new_connection = DatabaseConnection(
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        username=connection.username,
        password=connection.password
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    return {
        "message": "Connection saved successfully",
        "id": new_connection.id
    }
@app.post("/test-connection")
def test_connection(connection: DatabaseConnectionCreate):

    try:

        database_url = (
            f"postgresql://{connection.username}:"
            f"{connection.password}@"
            f"{connection.host}:"
            f"{connection.port}/"
            f"{connection.database_name}"
        )

        engine = create_engine(database_url)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "Database connection successful"
        }

    except Exception as e:

        return {
            "status": "failed",
            "message": str(e)
        }
@app.post("/schema")
def get_schema(connection: DatabaseConnectionCreate):

    try:

        database_url = (
            f"postgresql://{connection.username}:"
            f"{connection.password}@"
            f"{connection.host}:"
            f"{connection.port}/"
            f"{connection.database_name}"
        )

        engine = create_engine(database_url)

        inspector = inspect(engine)

        schema = {}

        for table in inspector.get_table_names():

            columns = inspector.get_columns(table)

            schema[table] = [
                column["name"]
                for column in columns
            ]

        return schema

    except Exception as e:

        return {
            "status": "failed",
            "message": str(e)
        }
@app.post("/generate-sql")
def generate_sql(request: QueryRequest):

    schema = {
        "students": [
            "id",
            "name",
            "college",
            "year"
        ]
    }

    sql = generate_sql_from_question(
        request.question,
        schema
    )

    return {
        "question": request.question,
        "sql": sql
    }
@app.post("/validate-sql")
def validate_sql(request: SQLRequest):

    return {
        "safe": is_safe_query(request.sql)
    }
@app.post("/execute-sql")
def execute_sql(request: ExecuteSQLRequest):

    if not is_safe_query(request.sql):

        return {
            "status": "failed",
            "message": "Unsafe SQL query detected"
        }

    try:

        database_url = (
            f"postgresql://{request.username}:"
            f"{request.password}@"
            f"{request.host}:"
            f"{request.port}/"
            f"{request.database_name}"
        )

        engine = create_engine(database_url)

        with engine.connect() as conn:

            result = conn.execute(
                text(request.sql)
            )

            rows = [
                dict(row._mapping)
                for row in result
            ]

        return {
            "status": "success",
            "rows": rows
        }

    except Exception as e:

        return {
            "status": "failed",
            "message": str(e)
        }
@app.post("/ask-database")
def ask_database(
    request: AskDatabaseRequest,
    db: Session = Depends(get_db)
):

    try:

        database_url = (
            f"postgresql://{request.username}:"
            f"{request.password}@"
            f"{request.host}:"
            f"{request.port}/"
            f"{request.database_name}"
        )

        engine = create_engine(database_url)

        schema = get_schema_dict(engine)

        sql = generate_sql_from_question(
            request.question,
            schema
        )

        # Check if SQL is safe
        if not is_safe_query(sql):

            history = QueryHistory(
                question=request.question,
                generated_sql=sql,
                status="blocked"
            )

            db.add(history)
            db.commit()

            return {
                "status": "failed",
                "message": "Unsafe SQL generated",
                "sql": sql
            }

        # Execute safe query
        with engine.connect() as conn:

            result = conn.execute(
                text(sql)
            )

            rows = [
                dict(row._mapping)
                for row in result
            ]

        # Save successful query
        history = QueryHistory(
            question=request.question,
            generated_sql=sql,
            status="success"
        )

        db.add(history)
        db.commit()

        return {
            "status": "success",
            "question": request.question,
            "sql": sql,
            "rows": rows
        }

    except Exception as e:

        history = QueryHistory(
            question=request.question,
            generated_sql=sql if 'sql' in locals() else "",
            status="error"
        )

        db.add(history)
        db.commit()

        error_message = str(e)

        if "does not exist" in error_message:

            user_message = (
                "The requested table or column does not exist."
            )

        elif "password authentication failed" in error_message:

            user_message = (
                "Invalid database username or password."
            )

        elif "connection refused" in error_message:

            user_message = (
                "Could not connect to the database server."
            )

        elif (
            "database" in error_message
            and "does not exist" in error_message
        ):

            user_message = (
                "The specified database does not exist."
            )

        else:

            user_message = (
                "An unexpected error occurred."
            )

        return {
            "status": "failed",
            "message": user_message,
            "technical_error": error_message
        }
@app.get("/query-history")
def get_query_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    history = db.query(
        QueryHistory
    ).order_by(
        QueryHistory.id.desc()
    ).limit(limit).all()

    return history