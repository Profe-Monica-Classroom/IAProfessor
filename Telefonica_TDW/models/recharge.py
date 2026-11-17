from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictStr, field_validator

from models.database import database_connection

VALID_AMOUNTS = (50.0, 100.0, 200.0, 500.0)


class RechargeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    msisdn: StrictStr
    amount: float
    network_type: Literal["4G", "5G"]
    location: StrictStr
    transaction_id: StrictStr

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value: object) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Amount must be a number.")
        if value not in VALID_AMOUNTS:
            raise ValueError("Amount is not supported.")
        return float(value)


class RechargeRecord(RechargeRequest):
    timestamp: str


class RechargeListResponse(BaseModel):
    recharges: list[RechargeRecord]


class NetworkStatus(BaseModel):
    status: Literal["OPERATIONAL", "DEGRADED"]
    details: StrictStr


class CustomerStatusResponse(BaseModel):
    msisdn: StrictStr
    latest_recharge: RechargeRecord
    network_status: NetworkStatus


def initialize_database() -> None:
    with database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS recharges (
                transaction_id TEXT PRIMARY KEY,
                msisdn TEXT NOT NULL,
                amount REAL NOT NULL,
                network_type TEXT NOT NULL,
                location TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_recharges_msisdn_timestamp
            ON recharges (msisdn, timestamp DESC)
            """
        )


def create_recharge(recharge: RechargeRequest) -> RechargeRecord:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    values = recharge.model_dump()
    with database_connection() as connection:
        connection.execute(
            """
            INSERT INTO recharges (
                transaction_id, msisdn, amount, network_type, location, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                values["transaction_id"],
                values["msisdn"],
                values["amount"],
                values["network_type"],
                values["location"],
                timestamp,
            ),
        )
    return RechargeRecord(**values, timestamp=timestamp)


def list_recharges() -> list[RechargeRecord]:
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT msisdn, amount, network_type, location, transaction_id, timestamp
            FROM recharges
            ORDER BY timestamp, transaction_id
            """
        ).fetchall()
    return [RechargeRecord(**dict(row)) for row in rows]


def get_latest_recharge_by_msisdn(msisdn: str) -> RechargeRecord | None:
    with database_connection() as connection:
        row = connection.execute(
            """
            SELECT msisdn, amount, network_type, location, transaction_id, timestamp
            FROM recharges
            WHERE msisdn = ?
            ORDER BY timestamp DESC, rowid DESC
            LIMIT 1
            """,
            (msisdn,),
        ).fetchone()
    return RechargeRecord(**dict(row)) if row is not None else None
