from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail
        super().__init__(detail)


class DuplicateError(Exception):
    """Raised when a write would violate a uniqueness rule."""

    def __init__(self, detail: str = "Resource already exists"):
        self.detail = detail
        super().__init__(detail)


class AppValidationError(Exception):
    """Raised for domain rules that Pydantic cannot express."""

    def __init__(self, detail: str = "Validation failed"):
        self.detail = detail
        super().__init__(detail)


def _error_body(error_type: str, message: str, status_code: int) -> dict:
    """One shape for every error this API returns."""
    return {
        "error": error_type,
        "message": message,
        "status_code": status_code,
    }


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=_error_body("NotFoundError", exc.detail, 404),
    )


async def duplicate_handler(request: Request, exc: DuplicateError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=_error_body("DuplicateError", exc.detail, 409),
    )


async def app_validation_handler(request: Request, exc: AppValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_body("AppValidationError", exc.detail, 422),
    )
