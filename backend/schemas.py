from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    college: str
    year: int


class DatabaseConnectionCreate(BaseModel):
    host: str
    port: int
    database_name: str
    username: str
    password: str

class QueryRequest(BaseModel):
    question: str

class SQLRequest(BaseModel):
    sql: str
class ExecuteSQLRequest(BaseModel):
    host: str
    port: int
    database_name: str
    username: str
    password: str
    sql: str
class AskDatabaseRequest(BaseModel):
    host: str
    port: int
    database_name: str
    username: str
    password: str
    question: str