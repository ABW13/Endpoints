from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    """POST body - name and email required, the rest optional."""
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    major: Optional[str] = Field(default=None, max_length=120)
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)


class StudentUpdate(BaseModel):
    """PUT body - full replacement, so name and email are required."""
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    major: Optional[str] = Field(default=None, max_length=120)
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)


class StudentPatch(BaseModel):
    """PATCH body - every field optional; unset fields are left alone."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    major: Optional[str] = Field(default=None, max_length=120)
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    major: Optional[str]
    gpa: Optional[float]

    model_config = {"from_attributes": True}
