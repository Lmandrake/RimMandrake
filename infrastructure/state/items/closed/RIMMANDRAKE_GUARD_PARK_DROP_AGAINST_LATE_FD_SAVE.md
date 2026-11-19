## spec
Codex FULL-FILE review 2026-11-18 of `src/RimMandrake/Utils/seat_sync.py` (on the fix for
RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND; review copy
`D:\ClaudeWork\rimmandrake\lane4_publish_sync\park_codex.md`, point 3; Codex probed it in memory, not reproduced here):
`_drop_park_if_restored` compares the restored file with the parked copy, then `rmtree`s the park. A writer that held
the untracked file open before it was parked can write through that descriptor after the compare; the parked inode
then holds the only copy of that save, and `rmtree` deletes its last name. The working-tree file keeps upstream's bytes.
The dirty-file park already handles the same shape (`t_write_through_an_old_descriptor_keeps_the_park` in
selftest_publish.py); the fix probably follows it (keep the park when the parked inode changed since it was parked).

## verify
Acceptance test: none yet, not watched failing. The builder first writes a selftest_publish.py case: open a handle on
an untracked file identical to origin's copy, publish (the file is parked), write through the handle after the compare
(inject at `_drop_park_if_restored`), and assert the written bytes survive somewhere named in the output.

## criteria
- A save made through a descriptor opened before the park is never deleted by the park's cleanup.
