## spec
FlowWorks (Design Version 0.1.0). Rank 10 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` sections 5 and 9; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves.

**Measured (visit 9 rows.jsonl, `design/concepts/FlowWorks/version/in_game/visit_9/`):** three mod lists ran: the 13-mod `flowworks` tier (61 rows), `fw_gss_sitting` (16 mods; only sc_source_pays), and `evening_20261113` (23 mods; OL_OWNER_LOOK_READS and sc_walk). The two lone lists cost two restarts for sc_source_pays (324 s) and one for OL_OWNER_LOOK_READS (234 s): about 4 min saved if one list holds both: [guess ~40%]. Measured from the rows: the 23-mod evening list is a SUPERSET of both the 13-mod list (13 of 13 mods) and fw_gss_sitting (16 of 16). So a single list can contain every mod each check needs. NOT measured: that the 61 FlowWorks rows still pass on the 23-mod list (extra mods may interfere), and that sc_source_pays reads the same on it. The first step is one run of sc_source_pays on the evening list (a cold load; only on a full visit).
Files: `design/concepts/FlowWorks/version/test_table.json` (commands name the lists), `design/concepts/FlowWorks/version/in_game/visit_9/SUMMARY.md` line 11, the tier definitions in `src/RimMandrake/Utils/modset_builder.py`.

**Recommendation: Polish list** (about 4 min per visit, guess ~40%). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_SHARE_FLOWWORKS_LIST_BETWEEN_TWO_LONE_CHECKS.acceptance.sh`
- Counts distinct active_mods sets in the newest FlowWorks visit's rows; limit 2 (our own rule: the flowworks tier plus one shared list). WATCHED FAIL today (2026-11-24): `mod lists in the visit: 3 (limit 2, our own rule); rows per list [1, 2, 61]`, exit 1. `--selftest` prints SELFTEST OK (5 cases: three lists -> red; two lists in another order -> green; one list -> green; a row without active_mods -> could not look; empty -> could not look). Watched green.
- Turns green only after a visit after the change; until then it reads visit 9.

## criteria
- The acceptance script exits 0 on a visit that includes sc_source_pays and OL_OWNER_LOOK_READS, with every row still PASS where it passed before (or the item records which row the larger list changed).
