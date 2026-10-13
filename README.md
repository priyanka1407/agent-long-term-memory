# agent-memory-basics

A tiny, standard-library-only copy of the long-term memory design used in `genai-testgen-langflow`, built to learn and remember the techniques.

Run it:

```bash
python run_demo.py
```

## Files, in learning order

| File | Technique | One line |
| --- | --- | --- |
| `step0_short_vs_long_term.py` | Short-term vs long-term | A list in RAM forgets; a file on disk remembers |
| `step1_memory_store.py` | Long-term store + audit log | `state.json` = what I know, `audit_log.jsonl` = what happened |
| `step2_change_detection.py` | Identity + change detection | Have I seen it? (title, fuzzy >= 0.85) Has it changed? (hash, or >= 97% text AND same numbers) |
| `step3_stable_ids.py` | Stable IDs | Counters never reuse IDs; new cases inherit the most similar old case's ID (>= 0.75) |
| `step4_agent.py` | The agent loop | LOAD -> ASK -> ACT -> SAVE + LOG |
| `run_demo.py` | Three releases | NEW, CHANGED, UNCHANGED (0 LLM calls), REMOVED, reviewer edit kept |

## Remember it as a diary

1. **Open the diary** (load `state.json`)
2. **Do I know this face?** (identity: module + title, fuzzy)
3. **New haircut or new person?** (change: hash / similarity / numbers)
4. **Act**: NEW -> generate, CHANGED -> regenerate + inherit IDs, UNCHANGED -> reuse, REMOVED -> retire
5. **Write in the diary** (save state, append audit log)

Libraries: `json`, `pathlib`, `hashlib`, `difflib`, `re`, `datetime`, `copy` (all built in).
