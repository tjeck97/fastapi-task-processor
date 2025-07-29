from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from db.base import Base
import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)


    conversations = relationship("Conversation", back_populates="task", cascade="all, delete")
