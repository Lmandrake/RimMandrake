#!/usr/bin/env python3
"""Stop hook, the filing gate's last door (item RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW; page
design/specs/2026-11-24-filing-gate/boundary.md; gate src/RimMandrake/rimflow/filing_gate.py). A helper run whose filing
of work was refused, and that has not resolved the refusal, is kept going while its context is still loaded: the
refusal told it to do the work, and a run that ends there drops the finding on the floor.

Active only in a run with a unit (RM_ROLE_UNIT); otherwise exit 0, silent.
  RM_DISPATCHER_STATE  the state folder that holds filing_refusals/<unit>.jsonl (default doorbell.DEFAULT_STATE)
  RM_STOP_BLOCKS_DIR   where the per-unit counter lives (default: the temp dir, a role run's own TMPDIR)
It blocks at most MAX_BLOCKS times per unit; the next stop lets the run end and says so on stderr (the run-end text of
detached_helper.finish still names each refusal). A record that cannot be read blocks nothing and says "could not look".
Always exit 0; a block is {"decision": "block", "reason": ...} on stdout. Tests: selftest_filing_refusal_before_stop.py.
"""
import json
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
MAX_BLOCKS = 2     # the same bound as role_result_before_stop.py: an unbounded loop is worse than an unresolved refusal


def counter_path(unit):
    d = os.environ.get("RM_STOP_BLOCKS_DIR") or tempfile.gettempdir()
    return os.path.join(d, "rm_filing_refusal_before_stop.%s.count" % re.sub(r"[^A-Za-z0-9_.-]", "_", unit or "nounit"))


def blocks_so_far(path):
    try:
        with open(path, encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def main(stdin_text, env=None):
    env = os.environ if env is None else env
    unit = (env.get("RM_ROLE_UNIT") or "").strip()
    if not unit:
        return 0
    try:
        import doorbell
        import filing_gate
        state = env.get("RM_DISPATCHER_STATE") or doorbell.DEFAULT_STATE
        left, why = filing_gate.read_refusals(unit, state)
    except Exception as e:  # noqa: BLE001 - the hook never stops a run on its own fault
        left, why = None, "%s: %s" % (type(e).__name__, e)
    if left is None:
        print("filing_refusal_before_stop: could not look (%s); the run may end" % why, file=sys.stderr)
        return 0
    if not left:
        return 0
    path = counter_path(unit)
    n = blocks_so_far(path)
    if n >= MAX_BLOCKS:
        print("filing_refusal_before_stop: %d refusal(s) still not resolved after %d blocks, letting the run end (the "
              "run-end text names each): %s" % (len(left), n, ", ".join(r["id"] for r in left)), file=sys.stderr)
        return 0
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(n + 1))
    except OSError as e:     # no counter, no block: an unbounded loop is worse than an unresolved refusal
        print("filing_refusal_before_stop did not run (block counter %s: %s); the run may end" % (path, e),
              file=sys.stderr)
        return 0
    lines = ["FILING REFUSED AND NOT RESOLVED (stop %d of %d blocked). This run's filing of work was refused, and the "
             "refusal stands:" % (n + 1, MAX_BLOCKS)]
    lines += ["  %s: %s" % (r["id"], r.get("title") or "") for r in left]
    lines += ["Resolve each, in one of three ways (rimflow file or spawn, with the same id):",
              "  did      do the work now, test first, land it, then: --did-it <sha> (a commit on origin/main)",
              '  filed    the run cannot do it now: file again with --not-now "<class>: <evidence>"',
              '  dropped  it is not worth the touch (CLAUDE.md test 1): --not-worth-it "<why>"']
    print(json.dumps({"decision": "block", "reason": "\n".join(lines)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.stdin.read()))
