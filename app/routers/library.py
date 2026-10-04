from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query

from app.schemas.books import BookResponse, SortField

router = APIRouter(prefix="/books", tags=["library"])

book_catalog: list[dict] = [
    {"id": 1, "title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction",
     "rating": 4.6, "year": 1965, "available": True},
    {"id": 2, "title": "Neuromancer", "author": "William Gibson", "genre": "Science Fiction",
     "rating": 4.1, "year": 1984, "available": False},
    {"id": 3, "title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "genre": "Science Fiction",
     "rating": 4.4, "year": 1969, "available": True},
    {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classic",
     "rating": 4.5, "year": 1813, "available": True},
    {"id": 5, "title": "Emma", "author": "Jane Austen", "genre": "Classic",
     "rating": 4.2, "year": 1815, "available": False},
    {"id": 6, "title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy",
     "rating": 4.8, "year": 1937, "available": True},
    {"id": 7, "title": "The Fellowship of the Ring", "author": "J.R.R. Tolkien", "genre": "Fantasy",
     "rating": 4.9, "year": 1954, "available": True},
    {"id": 8, "title": "Mistborn", "author": "Brandon Sanderson", "genre": "Fantasy",
     "rating": 4.5, "year": 2006, "available": False},
    {"id": 9, "title": "The Name of the Wind", "author": "Patrick Rothfuss", "genre": "Fantasy",
     "rating": 4.3, "year": 2007, "available": True},
    {"id": 10, "title": "Gone Girl", "author": "Gillian Flynn", "genre": "Thriller",
     "rating": 4.0, "year": 2012, "available": True},
    {"id": 11, "title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Thriller",
     "rating": 4.2, "year": 2019, "available": False},
    {"id": 12, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "Non-fiction",
     "rating": 4.4, "year": 2011, "available": True},
]

authors_db: dict[int, dict] = {
    1: {"id": 1, "name": "Frank Herbert", "country": "USA"},
    2: {"id": 2, "name": "William Gibson", "country": "Canada"},
    3: {"id": 3, "name": "Ursula K. Le Guin", "country": "USA"},
    4: {"id": 4, "name": "Jane Austen", "country": "United Kingdom"},
    5: {"id": 5, "name": "J.R.R. Tolkien", "country": "United Kingdom"},
    6: {"id": 6, "name": "Brandon Sanderson", "country": "USA"},
    7: {"id": 7, "name": "Patrick Rothfuss", "country": "USA"},
    8: {"id": 8, "name": "Gillian Flynn", "country": "USA"},
    9: {"id": 9, "name": "Alex Michaelides", "country": "Cyprus"},
    10: {"id": 10, "name": "Yuval Noah Harari", "country": "Israel"},
}


@router.get("/authors/{author_id}/books", response_model=list[BookResponse],
            summary="List books by an author")
def list_books_by_author(author_id: int = Path(ge=1, description="Author directory id")):
    author = authors_db.get(author_id)
    if author is None:
        raise HTTPException(status_code=404,
                            detail=f"Author {author_id} not found in the directory")

    name = author["name"].casefold()
    matches = [b for b in book_catalog if b["author"].casefold() == name]
    if not matches:
        raise HTTPException(status_code=404,
                            detail=f"No books found for author {author['name']}")
    return matches


@router.get("/", response_model=list[BookResponse], summary="Search and filter books")
def search_books(
    genre: Optional[str] = Query(default=None, min_length=1, description="Case-insensitive genre match"),
    min_rating: float = Query(default=0.0, ge=0.0, le=5.0, description="Minimum rating, 0.0-5.0"),
    sort_by: Optional[SortField] = Query(default=None, description="Field to sort by"),
    limit: int = Query(default=10, ge=1, le=100, description="Max results, 1-100"),
):
    results = book_catalog

    if genre is not None:
        wanted = genre.casefold()
        results = [b for b in results if b["genre"].casefold() == wanted]

    results = [b for b in results if b["rating"] >= min_rating]

    if sort_by is not None:
        if sort_by in (SortField.rating, SortField.year):
            results = sorted(results, key=lambda b: b[sort_by.value], reverse=True)
        else:
            results = sorted(results, key=lambda b: str(b[sort_by.value]).casefold())

    return results[:limit]


@router.get("/{book_id}", response_model=BookResponse, summary="Get one book")
def get_library_book(book_id: int = Path(ge=1, description="Integer book id")):
    for book in book_catalog:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
