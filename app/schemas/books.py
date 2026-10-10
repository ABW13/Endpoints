from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SortField(str, Enum):
    """Allowed sort keys. Subclassing str keeps it serializing as a plain string."""
    title = "title"
    author = "author"
    rating = "rating"
    year = "year"


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    rating: float
    year: int
    available: bool

BookResponse.model_config = {
    "from_attributes": True,
    "json_schema_extra": {
        "example": {
            "id": 1,
            "title": "Dune",
            "author": "Frank Herbert",
            "genre": "Science Fiction",
            "rating": 4.6,
            "year": 1965,
            "available": True,
        }
    },
}
