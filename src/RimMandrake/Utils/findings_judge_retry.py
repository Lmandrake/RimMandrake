#!/usr/bin/env python3
"""findings_judge_retry.py - the daily findings judge retries ONCE after the account resets
(ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS). On 2026-11-04 it died at 15:20Z on the account (cost 0) and waited for a
hand rerun at ~22:20Z instead of the 24 h timer.

  findings_judge_retry.py decide <run.json> [--now EPOCH]
      prints `RETRY <seconds> <error>` and exits 0 when run.json is an account death (role_launch.account_death: the
      same classifier the role runs use), the seconds running to the reset its message names plus RETRY_MARGIN_S (or
      role_launch.RESUME_WAIT_S when it names none); prints `NO <why>` and exits 1 otherwise.

findings_judge.sh calls it only on a run that is not itself the retry (FINDINGS_JUDGE_RETRY unset), so one death
earns one retry: a transient `systemd-run --user --on-active` timer that runs the same script again.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rimflow"))
import role_launch as RL  # noqa: E402

RETRY_MARGIN_S = 120        # past the named reset, so the first call after it is not refused on the clock's edge


def decide(res, now):
    """Pure. -> ("RETRY", seconds, error) or ("NO", why)."""
    err = RL.account_death(res)
    if not err:
        return ("NO", "not an account death")
    reset = RL.limit_reset_at(str(res.get("result") or ""), now)
    due = (reset + RETRY_MARGIN_S) if reset is not None else now + RL.RESUME_WAIT_S
    return ("RETRY", max(60, int(due - now)), err)


def main(argv):
    if len(argv) < 2 or argv[0] != "decide":
        print(__doc__.strip().splitlines()[0])
        return 2
    now = float(argv[argv.index("--now") + 1]) if "--now" in argv else time.time()
    try:
        with open(argv[1], encoding="utf-8") as f:
            res = json.load(f)
    except (OSError, ValueError) as e:
        print("NO run.json unreadable: %s" % e)
        return 1
    out = decide(res if isinstance(res, dict) else {}, now)
    print(" ".join(str(x) for x in out))
    return 0 if out[0] == "RETRY" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
