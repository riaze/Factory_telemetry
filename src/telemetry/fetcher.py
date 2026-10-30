"""Bounded concurrency fetcher module."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


async def fetch_all(
    ids: Iterable[str],
    fetch: Callable[[str], Awaitable[T]],
    limit: int,
) -> tuple[dict[str, T], dict[str, Exception]]:
    """Concurrently fetch resources with bounded concurrency.

    Returns a tuple of (ok_dict, failed_dict). Both dictionaries preserve
    the original input order of the IDs.
    """
    if limit < 1:
        raise ValueError("Concurrency limit must be at least 1")

    id_list = list(ids)
    if not id_list:
        return {}, {}

    semaphore = asyncio.Semaphore(limit)

    async def _worker(item_id: str) -> tuple[str, T | Exception, bool]:
        async with semaphore:
            try:
                res = await fetch(item_id)
                return (item_id, res, True)
            except Exception as exc:
                return (item_id, exc, False)

    tasks = [_worker(item_id) for item_id in id_list]
    raw_results = await asyncio.gather(*tasks)

    ok: dict[str, T] = {}
    failed: dict[str, Exception] = {}

    # Since Python dicts preserve insertion order, iterating over id_list 
    # or processing gather results in input order preserves sequence.
    results_map = {item_id: (res, success) for item_id, res, success in raw_results}

    for item_id in id_list:
        if item_id in results_map:
            res, success = results_map[item_id]
            if success:
                ok[item_id] = res  # type: ignore[assignment]
            else:
                failed[item_id] = res  # type: ignore[assignment]

    return ok, failed