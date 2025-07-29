from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from db.session import SessionLocal
from models.conversation import Conversation
from schemas.conversation import ConversationRead

router = APIRouter(prefix="/conversations", tags=["Conversations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{task_id}", response_model=List[ConversationRead])
def list_conversations(task_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(Conversation).filter_by(task_id=task_id).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error retrieving conversations",
        )

@router.get("/", response_model=List[ConversationRead])
def get_all_conversations(db: Session = Depends(get_db)):
    try:
        return db.query(Conversation).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error retrieving conversations",
        )

@router.post("/{task_id}", response_model=ConversationRead)
def add_conversation(
    task_id: int,
    message: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    try:
        conv = Conversation(task_id=task_id, message=message)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task_id or conversation violates a DB constraint",
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error adding conversation",
        )
