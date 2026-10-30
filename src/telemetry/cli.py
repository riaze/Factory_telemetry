"""CLI entry point for telemetry processing."""

import argparse

from collections import defaultdict

from pathlib import Path
import sys
from typing import Dict, List, Sequence

from telemetry.analytics import detect_anomalies
from telemetry.models import Reading
from telemetry.reader import read_readings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="telemetry", description="Factory Telemetry CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="Analyze telemetry log file")
    report_parser.add_argument("file", type=Path, help="Path to .jsonl file")
    report_parser.add_argument("--window", type=int, default=20, help="Window size for anomaly detection")
    report_parser.add_argument("--threshold", type=float, default=3.0, help="Standard deviation threshold")

    args = parser.parse_args(argv)

    if args.command == "report":
        file_path: Path = args.file
        if not file_path.is_file():
            sys.stderr.write(f"Error: File not found '{file_path}'\n")
            return 2

        # Group values by (machine, sensor) preserving insertion order of keys
        groups: Dict[tuple[str, str], List[float]] = defaultdict(list)
        for reading in read_readings(file_path):
            groups[(reading.machine, reading.sensor)].append(reading.value)

        # Output sorted by machine then sensor name
        for key in sorted(groups.keys()):
            values = groups[key]
            anomalies = detect_anomalies(values, window=args.window, threshold=args.threshold)
            machine, sensor = key
            print(f"{machine}/{sensor} readings={len(values)} anomalies={len(anomalies)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())