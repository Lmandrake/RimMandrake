#!/usr/bin/env python3
"""env_verify_check.py -- did `modcheck run <Mod>` record a real verdict for the mod as it stands now? Read-only.

    python3 src/RimMandrake/Utils/modcheck/env_verify_check.py Armoury

For MODCHECK_DONOR_ENVIRONMENTS_1's live clauses ("the suite produces a real verify event on a list that loaded
clean"); the load half is live_def_check.py / live_log_check.py on the same line. Reads
infrastructure/state/modcheck_status.json, the registry `status.record_run` writes once per run.

Exit 0: the mod's entry carries the mod's CURRENT hash, a verdict that came from running chains (GREEN, RED,
DRAFT-CHECKLIST, PENDING-OWNER-REVIEW; RED counts, it is a real verdict), and a timestamp after the last commit to the
mod's modcheck_env.py (so it ran on the composed environment). 1: the run was REFUSED. 2 (UNMEASURED): no entry, a
stale hash, or an entry older than the environment.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runner  # noqa: E402
import status  # noqa: E402

PASS, FAIL, UNMEASURED = 0, 1, 2
REAL = {"GREEN", "RED", "DRAFT-CHECKLIST", "PENDING-OWNER-REVIEW"}


def env_commit_time(mod_dir):
    env = os.path.join(mod_dir, "modcheck_env.py")
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", env], cwd=runner.ROOT,
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return int(out) if out else None


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return UNMEASURED
    mod = argv[0]
    mod_dir = runner.find_mod_dir(mod)
    entry = status.load().get(mod)
    if not entry:
        print("UNMEASURED %s: no modcheck_status entry" % mod)
        return UNMEASURED
    now_hash = status.mod_hash(mod_dir)
    if entry.get("hash") != now_hash:
        print("UNMEASURED %s: entry hash %s is not the mod's current %s" % (mod, entry.get("hash"), now_hash))
        return UNMEASURED
    since = env_commit_time(mod_dir)
    if since is None or (entry.get("ts") or 0) <= since:
        print("UNMEASURED %s: entry (ts %s) does not postdate modcheck_env.py's commit (%s)" % (mod, entry.get("ts"), since))
        return UNMEASURED
    if entry.get("status") not in REAL:
        print("FAIL %s: run %s recorded %s (%s)" % (mod, entry.get("run_id"), entry.get("status"), entry.get("refused")))
        return FAIL
    print("PASS %s: run %s recorded %s at the current hash" % (mod, entry.get("run_id"), entry.get("status")))
    return PASS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
