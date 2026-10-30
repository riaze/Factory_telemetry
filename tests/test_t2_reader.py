import inspect
import json
from pathlib import Path

import pytest

from telemetry.models import InvalidReadingError
from telemetry.reader import read_readings


def line(i: int) -> str:
    return json.dumps(
        {"machine": "M1", "sensor": "temp", "value": i, "ts": f"2026-01-01T10:{i:02d}:00+00:00"}
    )


def test_lazy_and_skips_bad_lines(tmp_path: Path) -> None:
    p = tmp_path / "a.jsonl"
    p.write_text("\n".join([line(1), "garbage", "", line(2)]) + "\n", encoding="utf-8")
    errors: list[tuple[int, type]] = []
    gen = read_readings(p, on_error=lambda n, e: errors.append((n, type(e))))
    assert inspect.isgenerator(gen)
    assert errors == []  # nothing consumed yet
    out = list(gen)
    assert [r.value for r in out] == [1.0, 2.0]
    assert errors == [(2, InvalidReadingError)]  # 1-based line number, blank line is not an error


def test_no_callback_does_not_crash(tmp_path: Path) -> None:
    p = tmp_path / "a.jsonl"
    p.write_text(line(1) + "\nbad\n", encoding="utf-8")
    assert len(list(read_readings(p))) == 1


def test_missing_file_raises_on_iteration(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        list(read_readings(tmp_path / "nope.jsonl"))


def test_handles_large_file_lazily(tmp_path: Path) -> None:
    p = tmp_path / "big.jsonl"
    p.write_text("\n".join(line(i % 60) for i in range(20000)) + "\n", encoding="utf-8")
    first = next(read_readings(p))
    assert first.value == 0.0
