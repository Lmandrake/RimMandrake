## spec

GimmeSomeSlack visit 2 (2026-11-19 19:49 PST): `gravship_scene.py off --out …` ran `prove_gravship.py`'s staging, which
refused ("FAIL: at least one colonist aboard before launch") with `sys.exit(1)`. `SystemExit` is not an `Exception`, so
`main()`'s handler missed it, `rc` was unbound in `finally`, the run died on `UnboundLocalError` and wrote no row. Had
`rc` been set from the exit code, the staging refusal would have read FAIL/MOD. A staging refusal is "could not ask":
UNMEASURED/HARNESS.

Fix: `rc = None` before the try; `except SystemExit` writes UNMEASURED with "staging refused" in the detail and returns 2.

## verify

Acceptance test: `python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gravship_scene_exit.py` prints `PASS (5 cases)`.
On the old code it printed `staging refusal sys.exit(1): no row written (rc 'raised UnboundLocalError')` and exit 1
(watched 2026-11-19).

## criteria

- A staging refusal writes one UNMEASURED/HARNESS row that names the refusal.
- PASS, FAIL and UNMEASURED exits keep their rows.

## refs

file: src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py
file: src/RimMandrake/GimmeSomeSlack/northstar/selftest_gravship_scene_exit.py
