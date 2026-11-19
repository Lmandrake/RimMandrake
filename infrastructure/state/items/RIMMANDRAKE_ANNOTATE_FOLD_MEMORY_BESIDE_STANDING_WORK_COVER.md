## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_LET_FOLD_MEMORY_KEEP_THE_WORK_COVER, which this item replaces): a `memory` decision annotates a standing cover decision; it never replaces one. No separate key and no second file.
- `findings_fold.latest_decision`: walk the signature's decisions in time order. A `memory` made while a decision of a cover kind (`findings_fold_rules.json` `cover_kinds`: work, merge, route, item) stands leaves that decision as the one returned (same `as`, `into`, `ts`) and rides on it under `"memory"` (`{"into", "ts", "by", "why"}`, the newest). With none standing (no decision, `retire`, or after an `undo`) `memory` is the decision, as today.
- `undo` right after a memory annotation removes the annotation only; any other `undo` clears the decision, as today.
- The report line of a DECIDED signature that carries a note says so (`also in memory: <FILE:LINE>`).
- The decisions file's format does not change; no old line is rewritten.

## refs
file: src/RimMandrake/Utils/findings_fold.py

## criteria
- The acceptance test passes 21 of 21; selftest_findings_fold.py stays green; `findings_fold.py` over the real decisions file reports the same `covered_by` for every signature before and after.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/fold_memory_keeps_cover_accept.py` (21 checks; on 0dc24342c3 in a throwaway `git clone --shared`, watched: 10 red, 11 green). Covers memory after work, merge, route, a ledger spawn and a ledger item decision; two memories; memory alone; after retire; work after memory; a newer work; undo after a note, a second undo, undo after work, memory after an undone work, undo after a lone memory; another signature; no decision; the lane item.
