## spec

`maturation_dispatch.py void <unit>` writes the void line, then rewrites each touched mod's `stage.json` and lands it
with `./publish`. When the rewritten `stage.json` equals HEAD, `./publish` refuses "nothing to publish" (exit 1). The
verb then printed `VOID WRITTEN, NOT LANDED ... land these by hand` and exited 1, although the void stood and nothing
needed landing. Seen 2026-11-23 on the void of rm-detached-bench-rimmandrake-autobuild-gimmesomeslack-fou-1795431592.
That collapses "nothing to land" into "landing failed".

Fix: `run_void.landable(root, paths)` keeps only paths that differ from HEAD or are untracked (all paths when git
cannot look). `_void` prints `nothing to land (equal to HEAD): ...` for the rest and lands only what changed.

## verify

`python3 src/RimMandrake/rimflow/selftest_run_void.py` prints 0 FAIL.

## criteria

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_run_void.py` (113 checks, 0 FAIL). Seen red before the fix
(109 checks, 1 FAIL: `run_void.landable exists`), and red on a planted mutant that returns every path.
