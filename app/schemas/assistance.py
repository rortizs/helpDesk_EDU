from pydantic import BaseModel, Field


class AssistanceIn(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    category: str = "General"


class AssistanceSuggestionOut(BaseModel):
    topic: str
    hint: str


class AssistanceOut(BaseModel):
    matched: bool
    suggestions: list[AssistanceSuggestionOut]
    disclaimer: str