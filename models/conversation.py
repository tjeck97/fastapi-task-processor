from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    archived = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    task = relationship("Task", back_populates="conversations")
