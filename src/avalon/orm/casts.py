"""Attribute casting — Laravel `$casts` parity."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any

_TRUE = {"1", "true", "t", "yes", "on"}


class CastError(ValueError):
    """Raised when a value cannot be cast to the declared type."""


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    text = str(value)
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise CastError(f"Cannot cast {value!r} to datetime") from exc


def cast_value(value: Any, cast: Any) -> Any:
    """Cast a raw database value into its declared Python type."""
    if value is None:
        return None

    if isinstance(cast, type) and issubclass(cast, Enum):
        return cast(value)

    name = str(cast)
    base, _, parameter = name.partition(":")
    base = base.strip().lower()

    if base in {"int", "integer"}:
        return int(value)
    if base in {"float", "double", "real"}:
        return float(value)
    if base in {"str", "string"}:
        return str(value)
    if base in {"bool", "boolean"}:
        if isinstance(value, str):
            return value.strip().lower() in _TRUE
        return bool(value)
    if base == "decimal":
        quantized = Decimal(str(value))
        if parameter:
            exponent = Decimal(1).scaleb(-int(parameter))
            return quantized.quantize(exponent)
        return quantized
    if base in {"json", "array", "dict", "object", "collection"}:
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError) as exc:
            raise CastError(f"Cannot cast {value!r} to {base}") from exc
    if base == "datetime":
        return _parse_datetime(value)
    if base == "date":
        parsed = _parse_datetime(value)
        return parsed.date() if parsed else None
    if base == "time":
        if isinstance(value, time):
            return value
        return time.fromisoformat(str(value))
    if base == "timestamp":
        parsed = _parse_datetime(value)
        return int(parsed.timestamp()) if parsed else None
    return value


def uncast_value(value: Any, cast: Any) -> Any:
    """Convert a cast Python value back into something the driver accepts."""
    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    name = str(cast)
    base, _, _parameter = name.partition(":")
    base = base.strip().lower()

    if base in {"json", "array", "dict", "object", "collection"}:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value
    if base == "decimal":
        return str(value)
    if base in {"bool", "boolean"}:
        return bool(value)
    return value


def serialize_value(value: Any) -> Any:
    """Make a cast value JSON-safe for `to_dict()` / responses."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    return value
