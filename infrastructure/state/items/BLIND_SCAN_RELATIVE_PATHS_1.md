## spec
`.claude/hooks/selftest_block_blind_scan.py` reported `a_relative_path_is_resolved_against_the_shell_cwd`
FAIL: `grep -c ThingDef defs/ThingDef.json` run with `cwd=DUMP` was allowed instead
of denied.

## root cause
`block_blind_scan.py`'s `_paths_in()` only substituted the cwd-joined absolute
path when `os.path.exists(joined)` was true:

    if cwd and not os.path.isabs(cand):
        joined = os.path.join(cwd, cand)
        if os.path.exists(joined):
            cand = joined

`measure.artifacts.classify()` is pure `fnmatch` pattern matching against
shapes like `*/DefDump/defs/*` — it does not need the file to exist. Gating
the join on existence meant: whenever the joined path did not exist (here,
because the live `DefDump/` folder no longer has a `defs/` subfolder at all —
it moved to `captures/<id>/` + `defs.sqlite` under `DUMP_PRODUCER_DATED_CAPTURES_1`,
so even the CORRECT layout wouldn't have existed relative to the selftest's
fixed `DUMP` constant), the relative token was left unresolved. A bare
`"defs/ThingDef.json"` matches no registry pattern (they all require a
`DefDump` prefix), so `classify()` returned `None` on both the joined and raw
forms and the scan sailed through — the exact evasion the test exists to close.

This is not narrow to the stale fixture: ANY classified-artifact-shaped
relative path fails to resolve whenever the joined path doesn't currently
exist on disk (a renamed/moved artifact, a slow or absent mount, a path named
before the file is created) — existence was never a valid precondition for
pattern classification.

## fix
Drop the `os.path.exists(joined)` gate; always join `cwd` for classification
when the token is not already absolute.

## verify
    python3 .claude/hooks/selftest_block_blind_scan.py
    17/17 passed   (was 16/17 before the fix, no other test's outcome changed)

## criteria
- [x] `a_relative_path_is_resolved_against_the_shell_cwd` passes.
- [x] All 16 previously-passing cases still pass (no new false refusals).
