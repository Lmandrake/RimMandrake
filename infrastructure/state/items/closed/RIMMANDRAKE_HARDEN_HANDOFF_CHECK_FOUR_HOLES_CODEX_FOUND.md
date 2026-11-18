## spec
Codex's full-file review of src/RimMandrake/Utils/handoff.py (2026-11-18, evidence D:\ClaudeWork\rimmandrake\lane_c\codex_review_e4.txt) found four pre-existing holes in the handoff gate, each confirmed by reading the code at acadffc5b7:
1. Half-done gate discharged by any mention: `gates()` drops an open `doing` item when its id appears ANYWHERE in the handoff (`i not in text`), including the auto-listed "Filed and still open" section or inside a longer id. It should require the exact id on a half-done pointer holding `NEXT:`.
2. A failed `git status` reads as a clean tree: `sh()` ignores the return code, so empty stdout from a failing git writes "Working tree clean." Failure must be UNMEASURED and refuse readiness.
3. `--since` moves `since_sha` but `gates()`/`build()` still get `prev_ts`, so items started between the requested commit and the previous handoff escape accountability (Codex's read; not yet reproduced).
4. Same-minute rerun overwrites: the skeleton name is minute-precision (`%Y%m%d%H%M`) and opened with "w", so a second write-mode run in the same minute replaces a filled handoff with a fresh skeleton.

## verify
Acceptance test: none written yet (LEFT for the builder: the filing run is Lane C, which had three more tickets queued). The builder writes it FIRST under src/RimMandrake/Utils/selftest_handoff.py or rimflow/acceptance/, one case per hole, and watches it fail on acadffc5b7 before fixing.

## criteria
- A1: each of the four holes has a case red on acadffc5b7 and green after.
- A2: selftest_handoff.py and owed_pointers_accept.py stay green.
