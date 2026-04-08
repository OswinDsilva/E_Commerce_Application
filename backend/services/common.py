from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pymysql.err import MySQLError

from ..errors import ApiError

DB_ERROR_PREFIX = "APP_ERROR"


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


def _drain_result_sets(cursor: Any) -> None:
    nextset = getattr(cursor, "nextset", None)
    if not callable(nextset):
        return

    while cursor.nextset():
        continue


def _parse_db_api_error(exc: MySQLError) -> ApiError | None:
    message = ""
    if getattr(exc, "args", None):
        message = str(exc.args[-1])
    else:
        message = str(exc)

    prefix = f"{DB_ERROR_PREFIX}|"
    if not message.startswith(prefix):
        return None

    try:
        _, code, status_code, detail = message.split("|", 3)
        return ApiError(detail, code, int(status_code))
    except (TypeError, ValueError):
        return None


def raise_api_error_from_db(exc: MySQLError) -> None:
    parsed = _parse_db_api_error(exc)
    if parsed is not None:
        raise parsed from exc
    raise exc


def call_procedure(
    connection: Any,
    statement: str,
    params: tuple[Any, ...] = (),
    *,
    fetch: str = "none",
) -> Any:
    try:
        with connection.cursor() as cursor:
            cursor.execute(statement, params)

            result: Any = None

            def _fetch_current() -> Any:
                if fetch == "one":
                    return cursor.fetchone()
                if fetch == "all":
                    return cursor.fetchall()
                return None

            current = _fetch_current()
            if current not in (None, []):
                result = current

            nextset = getattr(cursor, "nextset", None)
            if callable(nextset):
                while cursor.nextset():
                    current = _fetch_current()
                    if current not in (None, []):
                        result = current

            return result
    except MySQLError as exc:
        raise_api_error_from_db(exc)


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
