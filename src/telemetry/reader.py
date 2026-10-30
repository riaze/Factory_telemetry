"""Streaming file reader for telemetry data."""

import logging
from pathlib import Path
from typing import Callable, Iterator, Optional

from telemetry.models import InvalidReadingError, Reading, parse_reading

logger = logging.getLogger(__name__)


def read_readings(
    path: Path,
    on_error: Optional[Callable[[int, Exception], None]] = None,
) -> Iterator[Reading]:
    """Stream readings lazily from a file.

    Blank lines are skipped. Invalid lines invoke on_error or log a warning.
    """
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            try:
                yield parse_reading(stripped)
            except InvalidReadingError as exc:
                if on_error is not None:
                    on_error(line_no, exc)
                else:
                    logger.warning("Error parsing line %d in %s: %s", line_no, path, exc)