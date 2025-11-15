# Adaptive Learning Coach - Day 1

This repo implements Day 1 infra:
- Structured JSON logging (src/observability/logging_setup.py)
- Simple SQLite Memory Bank (src/tools/persistence.py)
- Smoke test to verify persistence and logging (src/smoke_test.py)

Run:
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. python src/smoke_test.py
