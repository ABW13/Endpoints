from fastapi import APIRouter, HTTPException
from app.schemas.book import BookCreate, BookResponse

router = APIRouter(prefix="/books", tags=["Books"])

books_db: list[dict] = []
next_id: int = 1


@router.get("/", response_model=list[BookResponse])
def list_books():
    return books_db


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db.append(new_book)
    next_id += 1
    return new_book