# RIMMANDRAKE_PIN_TMP_FILE_BASELINE_BEFORE_RENAME_NOT_AFTER

## spec
`scratch_reap.py` `sweep_tmp()`: for a regular file, eligibility is judged on `st2` but the signature queued for the
final check is `touched(os.lstat(pin))`, taken after the rename. A writer that modifies and closes the file between
those two calls makes its new timestamps the accepted baseline; if it exits before `_tmp_flush()` scans processes, the
modified file is deleted. Directories compare against their pre-rename signature and do not have this gap. Found by
Codex's full-file review 2026-11-18 (lane I); read in the source, not reproduced.

## verify
Acceptance test: a case in `src/RimMandrake/Utils/selftest_scratch_reap_tmp.py` that, through a hook between the eligibility
read and the post-rename lstat, rewrites an eligible /tmp fixture file; the sweep must restore (not delete) it.
Expected red on the base, green once the baseline is the pre-rename stat (or identity/content is checked across the
rename and the file restored on any doubt). Not yet written or watched failing.

## criteria
- A /tmp file changed during its rename is never deleted.
