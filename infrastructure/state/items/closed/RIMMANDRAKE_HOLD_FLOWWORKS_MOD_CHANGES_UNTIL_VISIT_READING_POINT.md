## spec
FlowWorks (Design Version 0.1.0). Rank 1 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` sections 5 and 9; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness and visit-order change only: no mod bar moves.

**Measured (visit 9, 2026-11-23, `design/concepts/FlowWorks/version/in_game/visit_9/rows.jsonl`):** the visit ran on three builds (209d57476d 17 rows, bc7dd578fd 15 rows, f4971d58fa 32 rows). The mod's source moved at 14:54 and 15:16 (commits 6447d14771, f4971d58fa) while the visit ran. 26 PASS rows of builds A and B, 2,541 s, were run again on build C. The other 6 early rows found scene faults and are not waste. The relation program reads a C# change as touching every check, so a rerun-only-touched rule has nothing to select by today. [measured]
**That the change could have waited for the visit's end:** [guess ~70%].

**Which does the analysis support?** The RULE: hold every mod change (a C# or def change that moves the deployed sha) until the visit's reading point, i.e. after the rows of the current build are read; record a mid-visit change only when a row shows a MOD FAILURE that blocks later rows. Small build (a line in the visit brief and a stop in the visit driver). The TOOL (the relation program reading C# by member, so a change reruns only the checks it touches) is rated medium by the study and gains nothing until built. So: the rule now; the tool is a later ticket, not filed here. The study did not measure how often a visit finds a MOD FAILURE that forces a mid-visit change; that is UNMEASURED and decides how often the rule's exception fires.

Files: `design/concepts/FlowWorks/version/in_game/visit_9/rows.jsonl` (the record), `design/concepts/FlowWorks/version/in_game/visit_9/SUMMARY.md`, `design/concepts/FlowWorks/version/test_table.json` (key `bars`), the visit driver scripts beside the rows, and the relation program that "reads a C# change as touching every check" (the study did not name its file; the fixer finds it).

**Recommendation: current Design Version** (no version bump: nothing in the mod changes; every later visit gains up to 42 min). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_HOLD_FLOWWORKS_MOD_CHANGES_UNTIL_VISIT_READING_POINT.acceptance.sh`
- Reads the newest FlowWorks visit's rows.jsonl and counts PASS rows whose mod_sha is not the check's last sha. Limit 0 (our own rule). Exit 0 pass, 1 fail, 2 could not look.
- WATCHED FAIL today (2026-11-24): `rows read 64; superseded PASS rows 26 (limit 0, our own rule); wasted seconds 2541`, exit 1. The 26 and 2,541 s match the study.
- Its planted faults: `--selftest` prints SELFTEST OK (5 cases: superseded rows -> red; one build -> green; a FAIL fixed by a later build -> green, not waste; empty visit -> could not look; unreadable record -> could not look). Watched green 2026-11-24.
- Kinds covered: empty visit, visit with one build (no costly act), unreadable record. Not covered: the exception case (a mid-visit change forced by a MOD FAILURE leaves superseded PASS rows of untouched checks; the limit reads that as a fail until the relation program can say which checks were touched). That gap is stated, not hidden.
- It passes once a visit after this change (visit 10 or later) lands with 0 superseded PASS rows. Until a new visit lands it keeps reading visit 9 and stays red.

## criteria
- The visit brief or driver holds a mod change until the reading point (path of the rule recorded on the item at close).
- The newest FlowWorks visit's rows show 0 superseded PASS rows, or the item records the MOD FAILURE that forced a change and the checks the change touched.
