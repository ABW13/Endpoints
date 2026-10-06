from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.exceptions import (
    AppValidationError,
    DuplicateError,
    NotFoundError,
    app_validation_handler,
    duplicate_handler,
    not_found_handler,
)
from app.models import note, student  # imported so create_all sees both tables
from app.routers import contacts, library, notes, recipes, students

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="A properly structured FastAPI application",
    version="0.1.0",
)

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(DuplicateError, duplicate_handler)
app.add_exception_handler(AppValidationError, app_validation_handler)

app.include_router(recipes.router)
app.include_router(contacts.router)
app.include_router(library.router)
app.include_router(notes.router)
app.include_router(students.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}
