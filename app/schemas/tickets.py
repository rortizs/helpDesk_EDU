from pydantic import BaseModel, Field


class TicketIn(BaseModel):
    title: str = Field(min_length=3)
    description: str
    category: str = "General"
    priority: str = "Medium"


class StatusIn(BaseModel):
    status: str


class AssignIn(BaseModel):
    assignee_id: int


class CommentIn(BaseModel):
    body: str = Field(min_length=1)
