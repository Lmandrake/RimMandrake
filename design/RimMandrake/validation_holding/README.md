# Validation holding store

Where an owner-reported look defect waits until the validation ladder is built. Nothing here is a test, a gate or a
ladder stage; nothing here is wired into one.

## The ruling

Owner, 2026-11-12 ~9:35 PM PST (phone typos fixed, meaning unchanged; on item
`RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS` as an `--owner-said` note):

> "Make it a rule to store these items until our validation ladder is fully defined and regenerated. Then we will ingest them properly where and how they belong."

It answers his 9:20 PM PST question whether each defect is being recorded for future testing, and replaces the earlier
rule that a defect closes only with a named check.

## How an entry is added

Every defect he reports in a look is appended here when reported, at the end of the look (the Conductor's Workshop rule).
One file per look or sitting, `owner_look_defects_<date>.md`, one table row per statement. Each row must stand alone for a
reader months from now:
- his words verbatim, with the local (Pacific) date and time;
- the save or capture that shows it (a full path; say if it is not in the repo);
- the build he saw (commit sha or DLL hash; say `not recorded` rather than guess);
- the item that fixed it, if any;
- what a check would assert, and the candidate kind: offline selftest, fast in-game state read, or look only;
- whether a proof hook is needed (and its item), and what tests it today;
- never invent a missing cell: write `not recorded`.

## How an entry leaves

Only when the ladder is fully defined and regenerated: each entry is ingested where and how it belongs (a stage line
item, a matrix cell, a selftest, or a look-only criterion), and its row is removed from the file here (the file is
deleted when empty). Until then nothing from here is placed into the ladder, a gate, the nightly sweep or a close check.
Ingest item: `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED`.

## Contents

| file | what |
|---|---|
| `owner_look_defects_2026-11-12.md` | 48 statements (56 rows) from the 2026-11-12 under-liquid pit looks |
| `owner_look_defects_2026-11-12_explosive_knockback.md` | 2 statements from his Explosive Knockback gap rulings, 2026-11-12 4:05 PM PST |
| `src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py` (+ `selftest_owner_look_regressions.py`) | built early, awaiting ingest: in-game state reads for the rows above; wired into nothing. Its selftest runs only because the nightly sweep discovers every `selftest*.py`, so it does not rot |
| `src/RimMandrake/Utils/selftest_screenshot_mode_restored.py` | built early, awaiting ingest: harness guard for the "cannot select or screenshot" defect |
| enforcement `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` | held, blocked on the ladder |
