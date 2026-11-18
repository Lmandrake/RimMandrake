## spec
Measured 2026-11-18 (the sync run): on-disk mod selftests that no command or file in `design/concepts/<Mod>/version/test_table.json` names — Pyrelands 5 of 23, GimmeSomeSlack 13 of 37, FlowWorks 139 of 187 (Graffiti 0 of 10; EK is RIMMANDRAKE_REGISTER_EK_SELFTESTS_THIRTEEN_NO_TABLE_ENTRY_SAW). Many FlowWorks ones are probably old proof, art or live-driver helpers, not mod tests. For each: register it as an entry supporting the bar it checks, or list it in a top-level `unlisted_suites` map with a one-line why (retired, live driver, pipeline machinery). Never make a new entry a bar DECIDER here: that is the Designer's call. Then `maturation.py certificate <Mod> --run` per mod. Pre-existing: not caused by the 2026-11-17/18 landings. Stronger follow-up worth weighing: the certificate itself refuses an unaccounted suite (same class as RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED).

## verify
`python3 design/specs/2026-11-18-unlisted-mod-selftests/check_unlisted.py` — pass: rc 0, every mod line '0 unaccounted'. Watched failing 2026-11-18 on cdd427e8eb: rc 1 (5, 13, 139). Unreadable table: rc 2, never 0.

## criteria
Each of the three mods: 0 unaccounted; certificate --run OK.
