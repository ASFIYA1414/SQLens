from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    college = Column(String)
    year = Column(Integer)

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True)
    host = Column(String)
    port = Column(Integer)
    database_name = Column(String)
    username = Column(String)
    password = Column(String)

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True)

    question = Column(String)

    generated_sql = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )