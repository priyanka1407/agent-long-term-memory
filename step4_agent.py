"""STEP 4 - The agent loop: LOAD memory -> ASK the two questions -> ACT -> SAVE + LOG.

For each requirement in a release:
  NEW        -> call the LLM, give it the next free ID
  CHANGED    -> call the LLM, new cases inherit old IDs, reviewer edits are dropped (back to review)
  UNCHANGED  -> reuse old cases and reviewer edits from memory, NO LLM call
  REMOVED    -> mark its cases obsolete, retire the ID forever
"""
import step1_memory_store as memory
from step2_change_detection import content_hash, find_known, identity_key, is_unchanged, numbers
from step3_stable_ids import assign_case_ids, next_req_id

llm_calls = 0


def fake_llm_generate(req: dict) -> list[dict]:
    """Stands in for the real LLM: boundary tests from each number in the requirement."""
    global llm_calls
    llm_calls += 1
    cases = []
    for n in numbers(req["text"]):
        limit = float(n)
        cases.append({"type": "positive", "title": f"{req['title']}: {limit:.2f} (at the limit)"})
        cases.append({"type": "negative", "title": f"{req['title']}: {limit + 0.01:.2f} (just over)"})
    if not cases:
        cases.append({"type": "positive", "title": f"{req['title']}: happy path"})
    return cases


def process_release(name: str, requirements: list[dict]) -> None:
    global llm_calls
    llm_calls = 0
    state = memory.load()                                             # 1. LOAD
    decisions, seen, new_registry = {}, set(), {}

    for req in requirements:
        known = find_known(state["registry"], req["module"], req["title"])   # 2a. Q1 identity
        if known is None:
            req_id, status = next_req_id(state, req["module"]), "NEW"
        else:
            req_id = known["req_id"]
            status = "UNCHANGED" if is_unchanged(known["text"], req["text"]) else "CHANGED"  # 2b. Q2
        seen.add(req_id)

        old_cases = {tc: c for tc, c in state["test_cases"].items() if c["req_id"] == req_id}
        if status != "UNCHANGED":                                     # 3. ACT
            cases, obsolete = assign_case_ids(state, req_id, fake_llm_generate(req), old_cases)
            for tc in old_cases:
                del state["test_cases"][tc]
            for case in cases:
                state["test_cases"][case["tc_id"]] = case
                if state["overrides"].pop(case["tc_id"], None):       # old edit no longer valid
                    print(f"    reviewer edit on {case['tc_id']} dropped -> back to review")
            for tc in obsolete:
                state["obsolete"][tc] = f"{name}: no longer generated"
        # UNCHANGED: nothing to do, the old cases and overrides simply stay in memory

        new_registry[identity_key(req["module"], req["title"])] = {
            "req_id": req_id, "hash": content_hash(req["text"]), "text": req["text"]}
        decisions[req_id] = status

    for key, entry in state["registry"].items():                     # REMOVED requirements
        if entry["req_id"] in seen:
            continue
        if not entry.get("retired"):
            decisions[entry["req_id"]] = "REMOVED"
            for tc in [tc for tc, c in state["test_cases"].items() if c["req_id"] == entry["req_id"]]:
                del state["test_cases"][tc]
                state["overrides"].pop(tc, None)
                state["obsolete"][tc] = f"{name}: requirement removed"
        new_registry[key] = {**entry, "retired": True}                # keep it so the ID is never reused
    state["registry"] = new_registry

    memory.save(state)                                                # 4. SAVE
    memory.log_event("release_processed", release=name, decisions=decisions, llm_calls=llm_calls)  # + LOG

    print(f"\n=== {name} ===  LLM calls: {llm_calls}")
    for req_id, status in decisions.items():
        print(f"  {req_id}: {status}")
    show_suite(state)


def reviewer_edit(tc_id: str, new_title: str, reviewer: str) -> None:
    """A human edits a test case (e.g. in JIRA). Stored separately so it is never overwritten."""
    state = memory.load()
    state["overrides"][tc_id] = {**state["test_cases"][tc_id], "title": new_title, "edited_by": reviewer}
    memory.save(state)
    memory.log_event("reviewer_edit", tc_id=tc_id, reviewer=reviewer)
    print(f"\n  {reviewer} edited {tc_id}")


def show_suite(state: dict) -> None:
    """The live suite = generated cases, with reviewer edits on top."""
    for tc_id in sorted(state["test_cases"]):
        case = state["overrides"].get(tc_id, state["test_cases"][tc_id])
        mark = f"  [edited by {case['edited_by']}]" if "edited_by" in case else ""
        print(f"    {tc_id}  {case['title']}{mark}")
    if state["obsolete"]:
        print(f"    obsolete: {sorted(state['obsolete'])}")
