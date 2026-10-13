"""STEP 2 - The two questions memory answers for every requirement.

Q1 IDENTITY  "Have I seen this requirement before?"
             key = module + title; exact match, else fuzzy title match >= 0.85
Q2 CHANGE    "Has its content changed?"
             unchanged if the hash is equal, OR text >= 97% similar AND every number identical
"""
import hashlib
import re
from difflib import SequenceMatcher

TITLE_MATCH = 0.85     # "Transfer limit" vs "Transfer limits" is still the same requirement
CONTENT_SAME = 0.97    # tiny wording drift is ignored...
                       # ...but a changed number (10,000 -> 15,000) is ALWAYS a change


def norm(text: str) -> str:
    """Lowercase, punctuation to spaces: 'Transfer-Limit!' -> 'transfer limit'."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def identity_key(module: str, title: str) -> str:
    return f"{norm(module)}|{norm(title)}"


def content_hash(text: str) -> str:
    """A fingerprint of the content. Same text -> same hash."""
    return hashlib.sha256(norm(text).encode()).hexdigest()[:16]


def numbers(text: str) -> list[str]:
    """All numbers in the text: 'up to 10,000' -> ['10000']."""
    return sorted(re.findall(r"\d+(?:\.\d+)?", text.replace(",", "")))


def similarity(a: str, b: str) -> float:
    """0.0 = nothing alike, 1.0 = identical."""
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def find_known(registry: dict, module: str, title: str) -> dict | None:
    """Q1: return what memory knows about this requirement, or None if it is new."""
    key = identity_key(module, title)
    if key in registry and not registry[key].get("retired"):
        return registry[key]                                      # exact match
    best, best_score = None, 0.0
    for old_key, entry in registry.items():                       # fuzzy match, same module only
        old_module, old_title = old_key.split("|", 1)
        if old_module != norm(module) or entry.get("retired"):
            continue
        score = SequenceMatcher(None, old_title, norm(title)).ratio()
        if score > best_score:
            best, best_score = entry, score
    return best if best_score >= TITLE_MATCH else None


def is_unchanged(old_text: str, new_text: str) -> bool:
    """Q2."""
    if content_hash(old_text) == content_hash(new_text):
        return True
    return similarity(old_text, new_text) >= CONTENT_SAME and numbers(old_text) == numbers(new_text)


if __name__ == "__main__":
    print("Q1 IDENTITY: have I seen it?")
    registry = {identity_key("Payments", "Transfer limit"): {"req_id": "REQ-PAY-001"}}
    for title in ["Transfer limit", "Transfer limits", "OTP challenge"]:
        hit = find_known(registry, "Payments", title)
        print(f"  {title!r:18} title similarity {similarity('Transfer limit', title):.2f} "
              f"-> {hit['req_id'] if hit else 'NEW'}")

    print("\nQ2 CHANGE: has the content changed?")
    old = "Customer can transfer up to 10,000 per transaction."
    for new in [old,
                "Customers can transfer up to 10,000 per transaction.",
                "Customer can transfer up to 15,000 per transaction."]:
        verdict = "UNCHANGED" if is_unchanged(old, new) else "CHANGED"
        print(f"  {new!r:55} text {similarity(old, new):.2f}, numbers {numbers(new)} -> {verdict}")
