from pydantic import BaseModel


class BookCreate(BaseModel):
    """Schema for creating a new book."""
    title: str
    author: str
    year: int


class BookResponse(BaseModel):
    """Schema for returning a book."""
    id: int
    title: str
    author: str
    year: int