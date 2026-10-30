import logging

import pytest

from telemetry.analytics import detect_anomalies
from telemetry.utils import timed

SERIES = [10, 11, 10, 11, 10, 11, 50, 10, 11]


def test_detects_spike() -> None:
    assert detect_anomalies(SERIES, window=5, threshold=3.0) == [6]


def test_accepts_generator() -> None:
    assert detect_anomalies((float(x) for x in SERIES), window=5, threshold=3.0) == [6]


def test_not_enough_data() -> None:
    assert detect_anomalies([1, 2, 3], window=5, threshold=3.0) == []


def test_constant_series_has_no_anomaly() -> None:
    assert detect_anomalies([5.0] * 20, window=5, threshold=3.0) == []


@pytest.mark.parametrize("window,threshold", [(1, 3.0), (0, 3.0), (5, 0.0), (5, -1.0)])
def test_invalid_params(window: int, threshold: float) -> None:
    with pytest.raises(ValueError):
        detect_anomalies(SERIES, window=window, threshold=threshold)


def test_timed_preserves_metadata_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    @timed
    def work(x: int) -> int:
        """doc"""
        return x * 2

    with caplog.at_level(logging.INFO):
        assert work(2) == 4
    assert work.__name__ == "work"
    assert work.__doc__ == "doc"
    assert any("work" in r.getMessage() for r in caplog.records)


def test_timed_logs_and_reraises_on_error(caplog: pytest.LogCaptureFixture) -> None:
    @timed
    def boom() -> None:
        raise RuntimeError("x")

    with caplog.at_level(logging.INFO), pytest.raises(RuntimeError):
        boom()
    assert any("boom" in r.getMessage() for r in caplog.records)
