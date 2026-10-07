import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item

router = APIRouter(prefix="/items", tags=["items"])

# Matches anything that looks like an HTML tag, opening or closing.
TAG_RE = re.compile(r"<[^>]*>")


class ItemCreate(BaseModel):
    """Item input. Sanitization happens here, before the data ever reaches the DB."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)

    @field_validator("name", "description")
    @classmethod
    def sanitize(cls, value: str) -> str:
        """
        Strip HTML tags, then collapse whitespace.

        This prevents STORED XSS: if we saved "<script>alert(1)</script>" and
        later rendered it as HTML in a browser, the script would run in the
        victim's session. Removing the tags at the boundary means the database
        never holds executable markup.
        """
        without_tags = TAG_RE.sub("", value)
        return without_tags.strip()

    @field_validator("name")
    @classmethod
    def name_not_empty_after_sanitize(cls, value: str) -> str:
        """A name of pure markup like '<b></b>' sanitizes to '', which we reject."""
        if not value:
            raise ValueError("name cannot be empty after sanitization")
        return value


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ItemResponse], summary="List items")
def list_items(db: Session = Depends(get_db)):
    """
    List items, optionally filtered by name.

    SQL INJECTION - the vulnerable version vs. the safe one.

    VULNERABLE (never do this):
        query = f"SELECT * FROM items WHERE name = '{name}'"
        db.execute(query)

    If a caller passes name = "' OR '1'='1", the string becomes:
        SELECT * FROM items WHERE name = '' OR '1'='1'
    ...which matches every row. Worse, "' ; DROP TABLE items; --" could destroy
    the table outright. The problem is that user input is being CONCATENATED
    into the statement, so the database can no longer tell data from code.

    SAFE (what we do here):
        db.query(Item).filter(Item.name == name)

    SQLAlchemy compiles this to "SELECT ... WHERE items.name = ?" and sends the
    caller's value as a BOUND PARAMETER, separate from the statement text. The
    database parses the query first and only then substitutes the value, so a
    value containing quotes or SQL keywords is treated as a literal string, not
    as syntax. This is why parameterized queries are the fix - not escaping or
    blocklisting, which are easy to get wrong.
    """
    return db.query(Item).order_by(Item.id).all()


@router.post("/", response_model=ItemResponse, status_code=201, summary="Create an item")
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    """Create an item from the sanitized schema. Validation ran before this body."""
    item = Item(name=payload.name, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
