from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AppValidationError, DuplicateError, NotFoundError
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentPatch, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201,
    summary="Create a student",
    responses={
        409: {"description": "A student with that email already exists"},
        422: {"description": "Validation error - bad email format or GPA out of range"},
    },
)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a student record with a unique email and a GPA between 0.0 and 4.0."""
    db_student = Student(**student.model_dump())
    db.add(db_student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateError(f"A student with email {student.email} already exists")
    db.refresh(db_student)
    return db_student


@router.get("/", response_model=list[StudentResponse], summary="List students")
def list_students(
    major: Optional[str] = Query(default=None, description="Exact major match"),
    min_gpa: Optional[float] = Query(default=None, ge=0.0, le=4.0, description="Minimum GPA"),
    db: Session = Depends(get_db),
):
    """Return all students, optionally filtered by major and minimum GPA."""
    query = db.query(Student)
    if major is not None:
        query = query.filter(Student.major == major)
    if min_gpa is not None:
        query = query.filter(Student.gpa >= min_gpa)
    return query.order_by(Student.id).all()


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get one student",
    responses={404: {"description": "No student with that id"}},
)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Return a single student by id, or 404 if none exists."""
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError(f"Student {student_id} not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse, summary="Replace a student")
def replace_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    """Full replacement - every field is overwritten from the request body."""
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError(f"Student {student_id} not found")

    for field, value in payload.model_dump().items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateError(f"A student with email {payload.email} already exists")
    db.refresh(student)
    return student


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update a student",
    responses={
        404: {"description": "No student with that id"},
        409: {"description": "That email is already in use by another student"},
        422: {"description": "Validation error, or an empty request body"},
    },
)
def patch_student(student_id: int, payload: StudentPatch, db: Session = Depends(get_db)):
    """Partially update a student - only the fields you send are changed."""
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError(f"Student {student_id} not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise AppValidationError("No fields provided to update")

    for field, value in changes.items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateError("That email is already in use")
    db.refresh(student)
    return student


@router.delete("/{student_id}", summary="Delete a student")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student record, or 404 if the id is unknown."""
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError(f"Student {student_id} not found")
    db.delete(student)
    db.commit()
    return {"message": f"Student {student_id} deleted successfully"}
