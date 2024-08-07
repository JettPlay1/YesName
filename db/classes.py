from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String, ForeignKeyConstraint

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    task_id = Column(Integer)
    subtask_id = Column(Integer)
    completed_tasks = Column(String)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String)
    score = Column(Integer)
    flag = Column(String)


class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    task_id = Column(Integer)
    flag = Column(String)