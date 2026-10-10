from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """What the client sends."""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    category: Optional[str] = Field(default=None, max_length=50)
    is_pinned: bool = False


class NoteResponse(BaseModel):
    """What the server returns — includes the DB-assigned fields."""
    id: int
    title: str
    content: str
    category: Optional[str]
    is_pinned: bool
    created_at: datetime

    model_config = {"from_attributes": True}


NoteResponse.model_config = {
    "from_attributes": True,
    "json_schema_extra": {
        "example": {
            "id": 1,
            "title": "Buy groceries",
            "content": "Milk, eggs, bread",
            "category": "personal",
            "is_pinned": False,
            "created_at": "2026-10-10T14:20:00+00:00",
        }
    },
}
