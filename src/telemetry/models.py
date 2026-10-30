"""T1 - Domain model and parsing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import math


class InvalidReadingError(ValueError):
    """Raised when a raw line cannot be turned into a valid Reading."""


@dataclass(frozen=True, slots=True)
class Reading:
    machine: str
    sensor: str
    value: float
    ts: datetime


def parse_reading(line: str) -> Reading:
    """Parse one JSON line into a Reading. See TICKETS.md (T1)."""
    try:
        data = json.loads(line)
        machine, sensor, value, ts_raw = data["machine"], data["sensor"], data["value"], data["ts"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        if isinstance(e, json.JSONDecodeError):
            msg = "invalid JSON format"
        elif isinstance(e, TypeError):
            msg = "JSON root must be an object (dictionary)"
        else:  # KeyError
            msg = f"missing field: {e}"
        raise InvalidReadingError(f"missing field: {e}") from e
    if not isinstance(machine, str) or not machine:
        raise InvalidReadingError("machine must be a non-empty string")
    if not isinstance(sensor, str) or not sensor:
        raise InvalidReadingError("sensor must be a non-empty string")
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidReadingError("value must be a number")
    if not math.isfinite(value):
        raise InvalidReadingError("value must be finite")
    if not isinstance(ts_raw, str):
        raise InvalidReadingError("ts must be a string")
    try:
        ts = datetime.fromisoformat(ts_raw)
    except ValueError as e:
        raise InvalidReadingError(f"invalid ts: {e}") from e
    if ts.utcoffset() is None:
        raise InvalidReadingError("ts must include a timezone")
    return Reading(machine, sensor, float(value), ts)            
