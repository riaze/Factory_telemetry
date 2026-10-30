"""Analytics and anomaly detection routines."""

from collections import deque
import statistics
from typing import Iterable, List

from telemetry.utils import timed


@timed
def detect_anomalies(
    values: Iterable[float],
    window: int,
    threshold: float,
) -> List[int]:
    """Detect indices of anomalous values using a moving population stddev window.

    Window memory complexity is bound to O(window).
    """
    if window < 2:
        raise ValueError("Window size must be at least 2")
    if threshold <= 0:
        raise ValueError("Threshold must be strictly positive")

    anomalies: List[int] = []
    window_buf: deque[float] = deque(maxlen=window)

    for idx, value in enumerate(values):
        if len(window_buf) == window:
            mean = statistics.fmean(window_buf)
            stddev = statistics.pstdev(window_buf, mu=mean)

            if stddev > 0.0:
                score = abs(value - mean) / stddev
                if score > threshold:
                    anomalies.append(idx)

        window_buf.append(value)

    return anomalies