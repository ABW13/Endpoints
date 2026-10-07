import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.models import item, note, student  # noqa: F401 - register tables with Base
from app.routers import contacts, items, library, notes, recipes, reports, students

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="A properly structured FastAPI application",
    version="0.1.0",
)

# --- CORS -------------------------------------------------------------------
# Explicit origins, never "*". With allow_credentials=True a wildcard is
# rejected by browsers anyway, and being specific means only these front ends
# may read responses in a user's browser.
ALLOWED_ORIGINS = [
    "[localhost](http://localhost:3000)",
    "[127.0.0.1](http://127.0.0.1:3000)",
    "[localhost](http://localhost:5173)",
    "[127.0.0.1](http://127.0.0.1:5173)",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    # Only the verbs this API actually exposes - not "*".
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Rate limiting ----------------------------------------------------------
# Simple in-memory sliding window: IP -> timestamps of recent requests.
# Note this is per-process; behind multiple workers each would keep its own
# count, so a real deployment needs Redis or similar shared storage.
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
request_log: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = request_log[client_ip]
    # Drop anything older than the window.
    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_REQUESTS:
        retry_after = int(RATE_LIMIT_WINDOW_SECONDS - (now - timestamps[0])) + 1
        return JSONResponse(
            status_code=429,
            content={
                "error": "RateLimitExceeded",
                "message": f"Too many requests. Limit is {RATE_LIMIT_REQUESTS} per minute.",
                "status_code": 429,
            },
            headers={"Retry-After": str(retry_after)},
        )

    timestamps.append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT_REQUESTS - len(timestamps))
    return response


# --- Routers ----------------------------------------------------------------
app.include_router(recipes.router)
app.include_router(contacts.router)
app.include_router(library.router)
app.include_router(notes.router)
app.include_router(students.router)
app.include_router(reports.router)
app.include_router(items.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}
