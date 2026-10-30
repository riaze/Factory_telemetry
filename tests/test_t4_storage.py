from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from telemetry.models import Reading
from telemetry.storage import ReadingRepo


def mk(i: int, machine: str = "M1") -> Reading:
    return Reading(machine, "temp", float(i), datetime(2026, 1, 1, 10, i, tzinfo=UTC))


def test_add_count_latest() -> None:
    with ReadingRepo(":memory:") as repo:
        repo.add_many(mk(i) for i in range(5))
        assert repo.count() == 5
        got = repo.latest("M1", "temp", 2)
        assert [r.value for r in got] == [4.0, 3.0]  # newest first
        assert got[0].ts.tzinfo is not None
        assert got[0] == mk(4)


def test_idempotent_insert() -> None:
    with ReadingRepo(":memory:") as repo:
        repo.add_many([mk(1), mk(2)])
        repo.add_many([mk(2), mk(3)])
        assert repo.count() == 3


def test_sql_injection_safe() -> None:
    evil = "x'; DROP TABLE readings; --"
    with ReadingRepo(":memory:") as repo:
        repo.add_many([mk(1, machine=evil)])
        assert repo.count() == 1
        assert len(repo.latest(evil, "temp", 5)) == 1


def test_persists_across_sessions(tmp_path: Path) -> None:
    db = str(tmp_path / "t.db")
    with ReadingRepo(db) as repo:
        repo.add_many([mk(1), mk(2)])
    with ReadingRepo(db) as repo:
        assert repo.count() == 2


def test_add_many_is_atomic() -> None:
    def gen() -> Iterator[Reading]:
        yield mk(1)
        raise RuntimeError("source failed")

    with ReadingRepo(":memory:") as repo:
        with pytest.raises(RuntimeError):
            repo.add_many(gen())
        assert repo.count() == 0
