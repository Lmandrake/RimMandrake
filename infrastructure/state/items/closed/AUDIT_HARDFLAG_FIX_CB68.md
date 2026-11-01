## spec
The Auditor's no-AI pre-screen raised hard flag(s) on the close of `CLEARED_CALLS_VERIFY_TWELVE_UNCHECKED` (sha `none`):

- `sha_unresolvable`: the close's sha does not resolve in this clone (never published, or mistyped).

A hard flag is a defect found without a re-check (roles/auditor.md step 1). Correct the record: find the real published sha (or the evidence) and record it on `CLEARED_CALLS_VERIFY_TWELVE_UNCHECKED`.

## verify
Re-run `python3 src/RimMandrake/rimflow/audit_prescreen.py --days 7 --out <tmp>`: the item no longer carries these hard flags, or its corrected record is noted on it.

## notes
Filed by `src/RimMandrake/rimflow/audit_hardflag_file.py` (no AI) [hardflag CLEARED_CALLS_VERIFY_TWELVE_UNCHECKED@none].
