#!/usr/bin/env python3
"""Read-only: is SteveDesktop's lane proven working again after a moment? Runs the steward's own recovery predicate,
testq.lane_proven_after (a stevedesktop job DONE with its canary on, finished after --after), against the queue the
environment names (TESTQ_QUEUE). Prints `PROVEN <job> <finished>` and exits 0, or `NOT PROVEN` and exits 1; a queue it
cannot read exits 2 with `UNMEASURED: <reason>`. A script form so a walled proof can run it (inline -c is never run).

    TESTQ_QUEUE=/mnt/d/ClaudeWork/rimmandrake/testq python3 src/RimMandrake/Utils/testq/lane_proven.py --after 2026-11-06T11:10:48Z
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import testq as T  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--after", required=True, help="UTC ISO time, e.g. 2026-11-06T11:10:48Z")
    a = ap.parse_args(argv)
    done = T.q("done")
    if not os.path.isdir(done):
        print("UNMEASURED: no queue done/ dir at %s" % done)
        return 2
    r = T.lane_proven_after([{"finished": a.after}])
    if not r:
        print("NOT PROVEN: no stevedesktop DONE+canary job finished after %s" % a.after)
        return 1
    res = r.get("result") or {}
    print("PROVEN %s %s" % (res.get("job") or T.job_of(r).get("id"), r.get("finished") or res.get("finished")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
