from pydantic import BaseModel


class ConversationBase(BaseModel):
    message: str


class ConversationCreate(ConversationBase):
    task_id: int


class ConversationRead(ConversationBase):
    id: int
    archived: bool
    task_id: int

    class Config:
        from_attributes = True
