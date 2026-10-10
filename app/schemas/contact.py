from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Category(str, Enum):
    """Allowed contact categories. Subclassing str makes it serialize as a plain string."""
    personal = "personal"
    work = "work"
    family = "family"


class ContactCreate(BaseModel):
    """Schema for creating a contact — every rule the client must satisfy."""

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str
    phone: Optional[str] = None
    category: Category

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value: str) -> str:
        """Custom validator: the value must contain an '@'."""
        if "@" not in value:
            raise ValueError("email must contain an '@' symbol")
        return value

    @field_validator("phone")
    @classmethod
    def phone_length_if_provided(cls, value: Optional[str]) -> Optional[str]:
        """Phone is optional, but when present it must be 10-15 characters."""
        if value is None:
            return value
        if not 10 <= len(value) <= 15:
            raise ValueError("phone must be between 10 and 15 characters")
        return value


class ContactUpdate(BaseModel):
    """Schema for updating a contact — every field optional."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = None
    phone: Optional[str] = None
    category: Optional[Category] = None

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if "@" not in value:
            raise ValueError("email must contain an '@' symbol")
        return value

    @field_validator("phone")
    @classmethod
    def phone_length_if_provided(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not 10 <= len(value) <= 15:
            raise ValueError("phone must be between 10 and 15 characters")
        return value


class ContactResponse(BaseModel):
    """Schema for returning a contact — adds the server-assigned fields."""

    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    category: Category
    created_at: str

# --- documentation example for the response model ---
ContactResponse.model_config = {
    "from_attributes": True,
    "json_schema_extra": {
        "example": {
            "id": 1,
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "phone": "5551234567",
            "category": "work",
            "created_at": "2026-10-10T14:20:00+00:00",
        }
    },
}
