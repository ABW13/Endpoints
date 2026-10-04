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