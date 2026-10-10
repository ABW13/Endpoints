from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "",
    response_model=NoteResponse,
    status_code=201,
    summary="Create a note",
    responses={422: {"description": "Validation error - missing title or content"}},
)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Create a note. Data persists across server restarts."""
    db_note = Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get(
    "",
    response_model=list[NoteResponse],
    summary="List notes",
)
def list_notes(
    category: Optional[str] = Query(default=None, description="Exact category match"),
    is_pinned: Optional[bool] = Query(default=None, description="Filter by pinned status"),
    db: Session = Depends(get_db),
):
    """Return all notes, newest first, optionally filtered by category and pinned status."""
    query = db.query(Note)
    if category is not None:
        query = query.filter(Note.category == category)
    if is_pinned is not None:
        query = query.filter(Note.is_pinned == is_pinned)
    return query.order_by(Note.created_at.desc()).all()


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get one note",
    responses={404: {"description": "No note with that id"}},
)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Return a single note by id, or 404 if it does not exist."""
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return note


@router.delete(
    "/{note_id}",
    status_code=204,
    summary="Delete a note",
    responses={404: {"description": "No note with that id"}},
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note. Returns 204 with no body on success."""
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    db.delete(note)
    db.commit()
    return None
