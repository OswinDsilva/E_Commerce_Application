from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..errors import ApiError


def require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"{field_name} is required", "BAD_REQUEST", 400)
    return value.strip()


def require_int(value: Any, field_name: str) -> int:
    if value is None or value == "":
        raise ApiError(f"{field_name} is required", "BAD_REQUEST", 400)

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"{field_name} must be an integer", "BAD_REQUEST", 400) from exc


def require_iso_date(value: Any, field_name: str) -> date:
    text = require_text(value, field_name)

    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ApiError(
            f"{field_name} must use YYYY-MM-DD format",
            "BAD_REQUEST",
            400,
        ) from exc


def get_next_id(connection: Any, table_name: str, id_column: str) -> int:
    query = f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name}"
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return int(row["next_id"])


def serialize_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def serialize_date(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    return value


def serialize_decimal(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value
