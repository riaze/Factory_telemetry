# factory-telemetry

industrial sensor ingestion in pure Python. Tickets are in `TICKETS.md`.

## Setup
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest            # all tests fail at the start — that is expected
bash scripts/check.sh   # ruff + mypy --strict + pytest with coverage >= 90%
```

