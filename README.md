# factory-telemetry

industrial sensor ingestion in pure Python. Tickets are in `TICKETS.md`.

## Setup
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest            # all tests fail at the start — that is expected
bash scripts/check.sh   # ruff + mypy --strict + pytest with coverage >= 90%
```

## Validation workflow with me
1. Finish one ticket, run `scripts/check.sh` until green.
2. Send me the code of the files you changed (paste it, or the `git diff`).
3. I review against `REVIEW_RUBRIC.md` and answer: **Accepted** or **Rework** with exact issues.
4. Only move on when the ticket is Accepted.

## Done = "I can say I'm a Python dev"
All 6 tickets Accepted + repo on GitHub with green CI. See the end of `REVIEW_RUBRIC.md` for the interview
questions you must be able to answer about your own code.
