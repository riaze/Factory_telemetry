import asyncio
from typing import Any

import pytest

from telemetry.fetcher import fetch_all


def test_limit_failures_and_order() -> None:
    active = 0
    peak = 0

    async def fake(i: str) -> dict[str, Any]:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        if i == "bad":
            raise RuntimeError("boom")
        return {"id": i}

    ok, failed = asyncio.run(fetch_all(["a", "b", "bad", "c", "d"], fake, limit=2))
    assert peak == 2
    assert list(ok) == ["a", "b", "c", "d"]  # input order preserved
    assert ok["c"] == {"id": "c"}
    assert list(failed) == ["bad"]
    assert isinstance(failed["bad"], RuntimeError)


def test_empty_input() -> None:
    async def fake(i: str) -> dict[str, Any]:
        return {}

    assert asyncio.run(fetch_all([], fake, limit=3)) == ({}, {})


def test_invalid_limit() -> None:
    async def fake(i: str) -> dict[str, Any]:
        return {}

    with pytest.raises(ValueError):
        asyncio.run(fetch_all(["a"], fake, limit=0))
