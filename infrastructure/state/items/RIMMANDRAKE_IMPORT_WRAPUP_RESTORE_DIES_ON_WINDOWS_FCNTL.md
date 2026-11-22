## spec
Pipeline defect found by Pyrelands in-game visit 4 (2026-11-22, game a release). `rimflow bridge release` runs
`python.exe src/RimMandrake/rimflow/wrapup.py restore` (cli `_restore_owed_settings`) before it frees a seat's own hold. Under
Windows python.exe the restore reaches `wrapup.check_clone` -> `import role_clones`, whose top-level `import fcntl` raises
ModuleNotFoundError (fcntl is Unix-only), so every such release printed "wrapup restore before release: Traceback ... (exit 1)"
and owed game settings were never put back. Fix: role_clones imports fcntl inside the one function that locks.

## verify
`python3 src/RimMandrake/rimflow/selftest_role_clones_no_fcntl.py` (hides fcntl as Windows does, imports role_clones,
calls is_role_clone): red on the parent (1 failed: ModuleNotFoundError), green on the fix (0 failed). Live:
`python.exe src/RimMandrake/rimflow/wrapup.py restore` printed "wrapup restore: 0 restored, 0 failed, 0 without a plan,
75 void" after the fix (the traceback before).

## criteria
- selftest_role_clones_no_fcntl.py 0 failed; red on the parent.
- python.exe wrapup.py restore ends with its tally, no traceback.

## Acceptance test
`python3 src/RimMandrake/rimflow/selftest_role_clones_no_fcntl.py` exits 0 with "0 failed" (1 check pair); watched red on
the parent (exit 1, "role_clones import raised without fcntl: ModuleNotFoundError").

## refs
file: src/RimMandrake/rimflow/role_clones.py
new: src/RimMandrake/rimflow/selftest_role_clones_no_fcntl.py
