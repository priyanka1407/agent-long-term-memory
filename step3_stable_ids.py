"""STEP 3 - Stable IDs, so the same thing keeps the same name across releases.

Requirement IDs  REQ-<MOD>-<nnn>   next number comes from a counter in memory; never reused.
Test-case IDs    TC-<req_id>-<nn>  a regenerated case INHERITS the ID of the most similar old
                                   case (same type, similarity >= 0.75), so the same JIRA issue
                                   is updated instead of a duplicate being created.
"""
from step2_change_detection import similarity

TC_MATCH = 0.75


def module_code(module: str) -> str:
    """'Payments' -> 'PAY'."""
    return ("".join(ch for ch in module if ch.isalnum()).upper() + "XXX")[:3]


def next_req_id(state: dict, module: str) -> str:
    code = module_code(module)
    state["counters"][code] = state["counters"].get(code, 0) + 1
    return f"REQ-{code}-{state['counters'][code]:03d}"


def assign_case_ids(state: dict, req_id: str, new_cases: list[dict], old_cases: dict) -> tuple[list[dict], list[str]]:
    """Give new cases IDs. Returns (cases with tc_id, old IDs that are now obsolete)."""
    # every (new, old) pair of the same type, best match first
    pairs = sorted(
        ((similarity(new["title"], old["title"]), i, old_id)
         for i, new in enumerate(new_cases)
         for old_id, old in old_cases.items() if new["type"] == old["type"]),
        reverse=True)

    inherited, taken = {}, set()
    for score, i, old_id in pairs:
        if score < TC_MATCH:
            break
        if i not in inherited and old_id not in taken:
            inherited[i] = old_id
            taken.add(old_id)

    last = state["tc_counters"].get(req_id, 0)
    for i, case in enumerate(new_cases):
        if i in inherited:
            case["tc_id"] = inherited[i]                   # same ID as before
        else:
            last += 1
            case["tc_id"] = f"TC-{req_id}-{last:02d}"      # brand-new ID
        case["req_id"] = req_id
    state["tc_counters"][req_id] = last

    obsolete = [old_id for old_id in old_cases if old_id not in taken]
    return new_cases, obsolete
