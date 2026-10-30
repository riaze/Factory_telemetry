import dataclasses
import json

import pytest

from telemetry.models import InvalidReadingError, Reading, parse_reading

BASE = {"machine": "M1", "sensor": "temp", "value": 71.2, "ts": "2026-01-01T10:00:00+00:00"}


def mk(**over: object) -> str:
    return json.dumps({**BASE, **over})


def test_parse_valid() -> None:
    r = parse_reading(mk())
    assert (r.machine, r.sensor, r.value) == ("M1", "temp", 71.2)
    assert r.ts.utcoffset() is not None


def test_int_value_becomes_float() -> None:
    r = parse_reading(mk(value=5))
    assert isinstance(r.value, float)


def test_reading_is_frozen() -> None:
    r = parse_reading(mk())
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.value = 1.0  # type: ignore[misc]


def test_invalid_reading_error_is_value_error() -> None:
    assert issubclass(InvalidReadingError, ValueError)


@pytest.mark.parametrize(
    "line",
    [
        "",
        "not json",
        "[]",
        '{"machine":"M1"}',
        mk(value="abc"),
        mk(value=True),
        mk(value=None),
        '{"machine":"M1","sensor":"t","value":NaN,"ts":"2026-01-01T10:00:00+00:00"}',
        mk(ts="yesterday"),
        mk(ts="2026-01-01T10:00:00"),  # naive datetime
        mk(machine=""),
        mk(sensor=""),
        mk(machine=12),
    ],
)
def test_invalid_lines_raise(line: str) -> None:
    with pytest.raises(InvalidReadingError):
        parse_reading(line)


def test_reading_equality() -> None:
    assert parse_reading(mk()) == parse_reading(mk())
    assert isinstance(parse_reading(mk()), Reading)
