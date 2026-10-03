from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.contact import Category, ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])

contacts_db: list[dict] = []
next_id: int = 1


@router.post("/", response_model=ContactResponse, status_code=201, summary="Create a contact")
def create_contact(contact: ContactCreate):
    """Create a contact. Validation happens before this function runs."""
    global next_id
    new_contact = {
        "id": next_id,
        **contact.model_dump(mode="json"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    contacts_db.append(new_contact)
    next_id += 1
    return new_contact


@router.get("/", response_model=list[ContactResponse], summary="List contacts")
def list_contacts(category: Optional[Category] = Query(default=None, description="Filter by category")):
    """List every contact, optionally narrowed by category."""
    if category is None:
        return contacts_db
    return [c for c in contacts_db if c["category"] == category.value]


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get one contact")
def get_contact(contact_id: int):
    for contact in contacts_db:
        if contact["id"] == contact_id:
            return contact
    raise HTTPException(status_code=404, detail=f"Contact {contact_id} not found")


@router.patch("/{contact_id}", response_model=ContactResponse, summary="Update a contact")
def update_contact(contact_id: int, updates: ContactUpdate):
    """Partial update — only the fields the client actually sent are changed."""
    # exclude_unset=True drops anything the client omitted, so a PATCH that
    # sends just {"phone": "..."} cannot blank out first_name with a default.
    changes = updates.model_dump(exclude_unset=True, mode="json")
    if not changes:
        raise HTTPException(status_code=422, detail="No fields provided to update")

    for contact in contacts_db:
        if contact["id"] == contact_id:
            contact.update(changes)
            return contact
    raise HTTPException(status_code=404, detail=f"Contact {contact_id} not found")