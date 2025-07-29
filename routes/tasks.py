from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db.session import SessionLocal
from models.conversation import Conversation
from models.task import Task
from schemas.task import TaskRead, TaskCreate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.title)

    db_task.conversations = [
        Conversation(message="message 1"),
        Conversation(message="message 2"),
    ]

    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Task violates a DB constraint")

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating task")

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error while creating task")

@router.get("/", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
