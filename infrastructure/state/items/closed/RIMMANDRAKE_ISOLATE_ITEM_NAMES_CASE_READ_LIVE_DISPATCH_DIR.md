## spec

`selftest_maturation_dispatch.py`'s `item_names_main` (run by the default suite, so at the pipeline door) calls
`MD.add_ingame(".", "X", ...)`, which calls `rerun_result` -> `rerun_dir()` -> `sdir()`. The section never sets
`RM_MATURATION_DISPATCH_DIR`, so `sdir()` falls back to `doorbell.state_dir()` — the REAL Dispatch state,
`/mnt/d/ClaudeWork/rimmandrake/dispatcher/maturation` on Archmagi, where it creates `cert_rerun/` and reads
`cert_rerun/X.json`. On a machine without that path (a Mac: read-only `/mnt`; a container) `os.makedirs` raises
OSError and the whole selftest CRASHES (reported by a remote builder 2026-11-17 as "CRASH, uncaught OSError";
reproduced on Archmagi 2026-11-18 by making `/mnt` read as absent in-process:
`FileNotFoundError ... '/mnt/d/ClaudeWork/rimmandrake/dispatcher/maturation'`, traceback through
`item_names_main` line 1790). A selftest that reads live state reads green or red by the machine, not the code.

Fix: the section runs on a throwaway `RM_MATURATION_DISPATCH_DIR` and restores the old value. Found by
RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH.

## verify

python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --item-names

## acceptance

Acceptance test: `python3 /mnt/d/ClaudeWork/rimmandrake/conductor/door_20261118/macview.py /mnt,/proc
src/RimMandrake/rimflow/selftest_maturation_dispatch.py --item-names` (macview makes the named prefixes read as
absent in-process) must exit 0 with `ALL PASS`; watched failing on base 952788a7ce (CRASH, FileNotFoundError on the
dispatcher state dir). Pass count: the section's own checks, 0 failed. Also the plain run stays green.

## criteria

- A1: the section reads no live Dispatch state on any machine; on one without /mnt it runs, not crashes.

## closed

Fixed 22dfc868b5 (2026-11-18): the section runs on a throwaway RM_MATURATION_DISPATCH_DIR. macview (/mnt,/proc absent) ALL PASS; plain ALL PASS.
