"""STEP 0 - Short-term vs long-term memory.

Short-term memory: a Python list in RAM. Fast, but limited and gone when the program stops.
Long-term memory:  a file on disk. It survives restarts, so the next run can use it.

Run this file twice and compare what each kind of memory still knows.
"""
import json
from pathlib import Path

LONG_TERM_FILE = Path(__file__).parent / "memory" / "notes.json"
SHORT_TERM_LIMIT = 3          # like a context window: only the last few items fit


def remember_short_term(buffer: list, item: str) -> None:
    buffer.append(item)
    if len(buffer) > SHORT_TERM_LIMIT:
        buffer.pop(0)         # oldest item is forgotten (trimming)


def load_long_term() -> list:
    if LONG_TERM_FILE.exists():
        return json.loads(LONG_TERM_FILE.read_text(encoding="utf-8"))
    return []


def save_long_term(notes: list) -> None:
    LONG_TERM_FILE.parent.mkdir(exist_ok=True)
    LONG_TERM_FILE.write_text(json.dumps(notes, indent=2), encoding="utf-8")


if __name__ == "__main__":
    short_term: list = []                      # starts EMPTY every run
    long_term = load_long_term()               # starts with whatever was saved before

    print(f"At start  -> short-term: {short_term} | long-term has {len(long_term)} notes")

    for fact in ["user = Priya", "project = test-gen", "prefers pytest", "release = R2"]:
        remember_short_term(short_term, fact)
    long_term.append(f"run #{len(long_term) + 1}: generated tests for R2")
    save_long_term(long_term)

    print(f"At end    -> short-term: {short_term}   (oldest fact was trimmed)")
    print(f"             long-term : {long_term}")
    print("Run me again: short-term starts empty, long-term remembers every run.")
