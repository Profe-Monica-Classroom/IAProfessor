from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator

from models.database import database_connection

FailureType = Literal["NO_INTERNET", "INTERMITTENT", "SLOW", "OTHER"]


class FailureReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    msisdn: StrictStr = Field(min_length=7, max_length=20)
    location: StrictStr = Field(min_length=2, max_length=120)
    network_type: Literal["4G", "5G"]
    failure_type: FailureType
    description: StrictStr = Field(min_length=10, max_length=1200)

    @field_validator("msisdn", "location", "description", mode="before")
    @classmethod
    def strip_text_fields(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class FailureReport(FailureReportRequest):
    report_id: StrictStr
    status: Literal["OPEN"]
    reported_at: StrictStr


class FailureReportListResponse(BaseModel):
    reports: list[FailureReport]


def initialize_failure_report_table() -> None:
    with database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS internet_failure_reports (
                report_id TEXT PRIMARY KEY,
                msisdn TEXT NOT NULL,
                location TEXT NOT NULL,
                network_type TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                reported_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_failure_reports_reported_at
            ON internet_failure_reports (reported_at DESC)
            """
        )


def create_failure_report(report: FailureReportRequest) -> FailureReport:
    values = report.model_dump()
    report_id = str(uuid4())
    reported_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = "OPEN"

    with database_connection() as connection:
        connection.execute(
            """
            INSERT INTO internet_failure_reports (
                report_id, msisdn, location, network_type, failure_type,
                description, status, reported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                values["msisdn"],
                values["location"],
                values["network_type"],
                values["failure_type"],
                values["description"],
                status,
                reported_at,
            ),
        )

    return FailureReport(
        **values,
        report_id=report_id,
        status=status,
        reported_at=reported_at,
    )


def list_recent_failure_reports(limit: int = 50) -> list[FailureReport]:
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT report_id, msisdn, location, network_type, failure_type,
                   description, status, reported_at
            FROM internet_failure_reports
            ORDER BY reported_at DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [FailureReport(**dict(row)) for row in rows]
