import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["reports"])

# In-memory stores. A restart clears them, which is fine for this exercise -
# the point is the task scheduling, not durability.
reports_db: dict[str, dict] = {}
notification_log: list[dict] = []


class ReportRequest(BaseModel):
    report_type: str = "summary"
    rows: int = 1000


class NotificationRequest(BaseModel):
    recipient: str
    message: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_report(report_id: str, report_type: str, rows: int) -> None:
    """
    Simulated long-running report generation.

    This runs AFTER the response has been sent, so the client never waits
    for it. Because it is a sync function, FastAPI runs it in a threadpool,
    which keeps the event loop free for other requests.
    """
    report = reports_db.get(report_id)
    if report is None:
        return

    report["status"] = "processing"
    report["updated_at"] = _now()

    time.sleep(2)  # stand-in for real work

    report["status"] = "complete"
    report["result"] = {
        "report_type": report_type,
        "rows_processed": rows,
        "generated_at": _now(),
        "summary": f"{report_type} report covering {rows} rows",
    }
    report["updated_at"] = _now()


def send_notification(recipient: str, message: str) -> None:
    """Simulated notification delivery, also run in the background."""
    time.sleep(1)
    notification_log.append(
        {
            "recipient": recipient,
            "message": message,
            "sent_at": _now(),
        }
    )


@router.post("/", status_code=202, summary="Start report generation")
def create_report(payload: ReportRequest, background_tasks: BackgroundTasks):
    """
    Queue a report. Returns immediately with 202 Accepted - the report is
    not ready yet, only scheduled.
    """
    report_id = str(uuid.uuid4())
    reports_db[report_id] = {
        "report_id": report_id,
        "report_type": payload.report_type,
        "rows": payload.rows,
        "status": "pending",
        "result": None,
        "created_at": _now(),
        "updated_at": _now(),
    }

    # The task is registered now and executed after the response is returned.
    background_tasks.add_task(generate_report, report_id, payload.report_type, payload.rows)

    return {
        "report_id": report_id,
        "status": "pending",
        "message": "Report generation started. Poll GET /reports/{report_id} for status.",
    }


@router.get("/notifications/log", summary="Notification delivery log")
def get_notification_log():
    """Every notification the background task has delivered so far."""
    return {"count": len(notification_log), "notifications": notification_log}


@router.post("/notifications", status_code=202, summary="Send a notification")
def create_notification(payload: NotificationRequest, background_tasks: BackgroundTasks):
    """Queue a notification. Returns immediately; delivery happens after."""
    background_tasks.add_task(send_notification, payload.recipient, payload.message)
    return {
        "status": "queued",
        "recipient": payload.recipient,
        "message": "Notification queued for delivery.",
    }


@router.get("/{report_id}", summary="Check report status")
def get_report(report_id: str):
    """Current status of a report - poll this to watch progress."""
    report = reports_db.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return report
