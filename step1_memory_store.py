"""STEP 1 - The long-term memory store.

Two files, like an agent's notebook and diary:
  memory/state.json        -> what the agent KNOWS now (overwritten each run)
  memory/audit_log.jsonl   -> what HAPPENED, one line per event (only ever appended)
"""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "memory"
STATE_FILE = MEMORY_DIR / "state.json"
AUDIT_FILE = MEMORY_DIR / "audit_log.jsonl"

EMPTY_STATE = {
    "registry": {},      # identity key -> {req_id, hash, text}   who each requirement is
    "counters": {},      # module code  -> last requirement number  ids are never reused
    "test_cases": {},    # tc_id        -> test case                what we produced last time
    "tc_counters": {},   # req_id       -> last test-case number
    "overrides": {},     # tc_id        -> reviewer-edited case     human feedback wins
    "obsolete": {},      # tc_id        -> reason                   retired test cases
}


def load() -> dict:
    """Read memory from disk. First run ever -> empty memory."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return copy.deepcopy(EMPTY_STATE)


def save(state: dict) -> None:
    """Write memory to disk so the next run can use it."""
    MEMORY_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def log_event(event: str, **details) -> None:
    """Append one line to the diary. Never edited, never deleted: an audit trail."""
    MEMORY_DIR.mkdir(exist_ok=True)
    row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **details}
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def reset() -> None:
    """Forget everything (used by the demo so it always starts clean)."""
    STATE_FILE.unlink(missing_ok=True)
    AUDIT_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    state = load()
    state["counters"]["DEMO"] = state["counters"].get("DEMO", 0) + 1
    save(state)
    log_event("demo_run", run=state["counters"]["DEMO"])
    print(f"This file has run {state['counters']['DEMO']} time(s); the count lives in {STATE_FILE.name}")
