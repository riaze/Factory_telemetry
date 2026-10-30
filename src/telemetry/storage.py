"""SQLite storage layer for telemetry readings."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
import sqlite3
from types import TracebackType

from telemetry.models import Reading


class ReadingRepo:
    """Context-managed SQLite repository. See TICKETS.md (T4)."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> ReadingRepo:
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _init_db(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    machine TEXT NOT NULL,
                    sensor TEXT NOT NULL,
                    value REAL NOT NULL,
                    ts TEXT NOT NULL,
                    PRIMARY KEY (machine, sensor, ts)
                );
                """
            )

    def add_many(self, readings: Iterable[Reading]) -> None:
        assert self._conn is not None
        records = [
            (r.machine, r.sensor, r.value, r.ts.isoformat()) for r in readings
        ]
        if not records:
            return

        with self._conn:
            self._conn.executemany(
                """
                INSERT INTO readings (machine, sensor, value, ts)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(machine, sensor, ts) DO NOTHING;
                """,
                records,
            )

    def count(self) -> int:
        assert self._conn is not None
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM readings;")
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    def latest(self, machine: str, sensor: str, n: int) -> list[Reading]:
        assert self._conn is not None
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT machine, sensor, value, ts
            FROM readings
            WHERE machine = ? AND sensor = ?
            ORDER BY ts DESC
            LIMIT ?;
            """,
            (machine, sensor, n),
        )
        rows = cursor.fetchall()
        return [
            Reading(
                machine=row[0],
                sensor=row[1],
                value=float(row[2]),
                ts=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]