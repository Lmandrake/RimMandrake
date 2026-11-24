#!/usr/bin/env python3
"""Stop hook, guard RESULT_BEFORE_EXIT (design/specs/2026-11-15-cheap-guards-at-every-door.md §3.1; item
RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED). A Designer stage-machine run that tries to end without a
result.json the stage machine accepts is told why and kept going, while its context is still loaded: 8 of 16 rejected
stage runs 2026-11-04..15 read "no result.json (a closing message is not a result)", each one a paid retry.

Active only when role_launch set RM_DESIGNER_DIR (the concept folder); otherwise exit 0, silent.
  RM_ROLE_UNIT           the run's unit: keys the block counter (else the hook input's session_id)
  RM_DESIGNER_CHECK_CMD  the check, the folder appended (default DEFAULT_CHECK); exit 0 = result.json acceptable
  RM_STOP_BLOCKS_DIR     where the per-unit counter lives (default: the temp dir, a role run's own TMPDIR)
A failing check blocks the stop at most MAX_BLOCKS times per unit, with the check's own words, would_pass and
smallest_fix; the next failing stop lets the run end (the launcher's close still rejects it). A check that cannot run
(exit 126/127, no interpreter, a timeout) blocks nothing, says "did not run" and, for the real check, raises the
incident signal GUARD_KIND. Tests: selftest_role_result_before_stop.py; acceptance:
src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py."""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CHECK = "python3 src/RimMandrake/rimflow/designer_stage.py check"
MAX_BLOCKS = 2
# budget: danger=a hung result check holds a role run open at its stop; never reached in the 14 days to 2026-11-24; no record of
# budget: its run
TIMEOUT_S = 45
GUARD_KIND = "guard:result_before_exit:did_not_run"


def counter_path(unit):
    d = os.environ.get("RM_STOP_BLOCKS_DIR") or tempfile.gettempdir()
    return os.path.join(d, "rm_result_before_stop.%s.count" % re.sub(r"[^A-Za-z0-9_.-]", "_", unit or "nounit"))


def blocks_so_far(path):
    try:
        with open(path, encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def run_check(argv):
    """-> (rc, output) or (None, why it did not run)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT_S, cwd=REPO, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "timed out after %d s" % TIMEOUT_S
    except OSError as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode in (126, 127):
        return None, "exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[:300])
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def alarm(why):
    """The real check could not run: one incident signal row, best effort (a failure to tell is printed, never raised)."""
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
        import incident
        with open(os.path.join(REPO, "src", "RimMandrake", "rimflow", "dispatcher_schedule.json"), encoding="utf-8") as f:
            incident.signal(json.load(f), GUARD_KIND, why, time.time())
    except Exception as e:  # noqa: BLE001
        print("result_before_exit: alarm not raised (%s: %s)" % (type(e).__name__, e), file=sys.stderr)


def main(stdin_text, env=None, raise_alarm=alarm):
    env = os.environ if env is None else env
    folder = env.get("RM_DESIGNER_DIR")
    if not folder:
        return 0
    try:
        hook_in = json.loads(stdin_text or "{}")
    except ValueError:
        hook_in = {}
    unit = env.get("RM_ROLE_UNIT") or (hook_in.get("session_id") if isinstance(hook_in, dict) else None)
    cmd = env.get("RM_DESIGNER_CHECK_CMD") or DEFAULT_CHECK
    argv = shlex.split(cmd) + [folder]
    rc, out = run_check(argv)
    if rc is None:
        why = "result_before_exit did not run (%s): %s; the run may end" % (" ".join(argv), out)
        print(why, file=sys.stderr)
        if not env.get("RM_DESIGNER_CHECK_CMD"):
            raise_alarm(why)
        return 0
    if rc == 0:
        return 0
    path = counter_path(unit)
    n = blocks_so_far(path)
    if n >= MAX_BLOCKS:
        print("result_before_exit: check still fails after %d blocks, letting the run end (the stage machine will "
              "reject it): %s" % (n, out[:500]), file=sys.stderr)
        return 0
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(n + 1))
    except OSError as e:     # no counter, no block: an unbounded loop is worse than a rejected run
        print("result_before_exit did not run (block counter %s: %s); the run may end" % (path, e), file=sys.stderr)
        return 0
    rerun = " ".join(shlex.quote(x) for x in argv)
    reason = ("RESULT BEFORE EXIT (stop %d of %d blocked): the stage machine will REJECT this run as it stands. "
              "Evidence, `%s` says:\n%s\n"
              "would_pass: that command prints \"result.json would be accepted\" and exits 0.\n"
              "smallest_fix: write or repair %s/result.json as your stage packet says (a closing message is not a "
              "result), rerun the command above, then end." % (n + 1, MAX_BLOCKS, rerun, out or "(no output)", folder))
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.stdin.read()))
