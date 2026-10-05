from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentPatch, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse, status_code=201, summary="Create a student")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.model_dump())
    db.add(db_student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"A student with email {student.email} already exists",
        )
    db.refresh(db_student)
    return db_student


@router.get("/", response_model=list[StudentResponse], summary="List students")
def list_students(
    major: Optional[str] = Query(default=None, description="Exact major match"),
    min_gpa: Optional[float] = Query(default=None, ge=0.0, le=4.0, description="Minimum GPA"),
    db: Session = Depends(get_db),
):
    query = db.query(Student)
    if major is not None:
        query = query.filter(Student.major == major)
    if min_gpa is not None:
        query = query.filter(Student.gpa >= min_gpa)
    return query.order_by(Student.id).all()


@router.get("/{student_id}", response_model=StudentResponse, summary="Get one student")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse, summary="Replace a student")
def replace_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    for field, value in payload.model_dump().items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"A student with email {payload.email} already exists",
        )
    db.refresh(student)
    return student


@router.patch("/{student_id}", response_model=StudentResponse, summary="Update a student")
def patch_student(student_id: int, payload: StudentPatch, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields provided to update")

    for field, value in changes.items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="That email is already in use")
    db.refresh(student)
    return student


@router.delete("/{student_id}", summary="Delete a student")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    db.delete(student)
    db.commit()
    return {"message": f"Student {student_id} deleted successfully"}
