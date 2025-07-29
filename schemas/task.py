from pydantic import BaseModel
from models.task import TaskStatus

class TaskBase(BaseModel):
    title: str

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    status: TaskStatus

    class Config:
        from_attributes = True
