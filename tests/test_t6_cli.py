import json
from pathlib import Path

import pytest

from telemetry.cli import main


def rows(machine: str, values: list[float]) -> list[str]:
    return [
        json.dumps(
            {
                "machine": machine,
                "sensor": "temp",
                "value": v,
                "ts": f"2026-01-01T10:{i:02d}:00+00:00",
            }
        )
        for i, v in enumerate(values)
    ]


def test_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = tmp_path / "d.jsonl"
    lines = rows("M1", [10, 11, 10, 11, 10, 11, 50, 10, 11]) + ["garbage"] + rows("M2", [5.0] * 9)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    code = main(["report", str(p), "--window", "5", "--threshold", "3"])
    out = capsys.readouterr().out.strip().splitlines()
    assert code == 0
    assert out == [
        "M1/temp readings=9 anomalies=1",
        "M2/temp readings=9 anomalies=0",
    ]


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["report", str(tmp_path / "nope.jsonl")])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.err.strip() != ""
    assert captured.out == ""


def test_defaults_are_usable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = tmp_path / "d.jsonl"
    p.write_text("\n".join(rows("M1", [1.0] * 30)) + "\n", encoding="utf-8")
    assert main(["report", str(p)]) == 0
    assert "M1/temp readings=30 anomalies=0" in capsys.readouterr().out
