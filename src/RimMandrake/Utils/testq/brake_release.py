#!/usr/bin/env python3
"""brake_release.py - Operations releases a filler brake that has a recorded non-fault cause. No LLM.

STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE. 2026-11-03: the filler braked on a hardware crash and a job cancelled for a BIOS
visit, ops_watch read steve.state=BRAKED with unowned_stall 0 because the steward was escalating, and nothing acted until
the owner asked. rm-ops-watch runs this on every full pass (ops_watch.steve_release).

A pass, reading the lane through testq.fill_plan and nothing else:
  none       no filler brake (the normal answer)
  wait       a brake, but the machine is down, quarantined or has no fresh companion yet: a canary could only fail
  escalate   a tail job has no recorded non-fault cause (testq.nonfault_cause), or the canary spent on this tail did not
             come back DONE: the steward's ladder has it, and steve.incident_unclaimed_min alarms if nobody claims it
  released   the brake's jobs all have a recorded cause: one canary job submitted, requested_by Operations.canary
  refused    the submit was refused: said here, tried again next pass, the steward's RELEASE_GRACE_S then escalates

One canary per tail: a job DONE with its canary on ends the brake (testq.lane_proven_after); anything else leaves the
same tail in place, so the spent record stops a loop. A new failure makes a new tail and earns a new look. The canary runs
one chain: the filler's own next pick, else the first chain of a tail job (a lane proof, so --retest-why).

Reading: QHOME/brake_release.json, rewritten every pass; the state, its reason and `canary` {job, tail, at, ts}.
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schema as S  # noqa: E402
import testq as T  # noqa: E402

BY = "Operations.canary"
RELEASE_GRACE_S = 1800      # two rm-ops-watch passes: past this a known brake is a plain fault, and the ladder runs
STATE = "brake_release.json"


def tail_ids(tails):
    return sorted(T.job_of(t)["id"] for t in tails if t)


def spent_on(tails):
    """The canary already sent for exactly this tail, or None."""
    c = (T.read_json(T.q(STATE)) or {}).get("canary") or {}
    return c if c.get("tail") == tail_ids(tails) else None


def causes_of(tails, now):
    wins = T.lane_windows(now)
    return {T.job_of(t)["id"]: T.nonfault_cause(t, wins) for t in tails}


def releasable(tails, now):
    """True while Operations still owes this brake its canary: every job has a recorded cause, none spent yet."""
    return bool(tails) and all(causes_of(tails, now).values()) and not spent_on(tails)


def canary_request(mod, tails, now):
    """-> (chains, purpose, row_items, retest_why) or None if nothing can be asked of the lane."""
    plan = T.fill_rank(mod, 1, now)
    if plan["verdict"] == "pick" and plan.get("pick"):
        pick = plan["pick"][:1]
        rows = {k: v for k, v in (plan.get("row_items") or {}).items() if k in pick}
        return pick, plan["purpose"], rows, None
    for t in reversed(tails):
        job = T.job_of(t)
        chains = (job.get("selector") or {}).get("chains") or []
        if job.get("mod") == mod and chains:
            return chains[:1], "guard", {}, "brake release canary: the lane proof after %s" % job["id"]
    return None


def submit(mod, req):
    """-> (rc, the last line cmd_submit printed)."""
    chains, purpose, rows, why = req
    r = subprocess.run(["git", "-C", T.REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        return 2, "no origin/main in %s: %s" % (T.REPO, r.stderr.strip()[-200:])
    a = argparse.Namespace(mod=mod, chains=",".join(chains), rows=None, item=None, full=False, purpose=purpose, by=BY,
                           sha=r.stdout.strip(), for_item=None, profile=None, priority=30, not_before=None,
                           supersedes=None, owner_gate=None, lane=T.STEVE, deploy=None, timeout=7200, no_canary=False,
                           no_validity=False, no_sha_check=True, retest_why=why,
                           row_item=["%s=%s" % kv for kv in sorted(rows.items())])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = T.cmd_submit(a)
    lines = out.getvalue().strip().splitlines()
    return rc, lines[-1] if lines else ""


def decide(now, mods):
    """-> the record of this pass, submitting when it says released."""
    T.ensure_dirs()
    down = (T.read_json(T.q("ssh_state.json")) or {}).get("down_since")
    if not T.brake_tail(T.filler_jobs()):
        return {"state": "none", "reason": "no filler brake"}
    plans = {m: T.fill_plan(m, 1, int(os.environ.get("TESTQ_FILL_CAP") or T.FILL_CAP_DEFAULT), T.FILL_DAY_S, now)
             for m in mods}
    braked = [m for m, p in plans.items() if p["verdict"] == "brake"]
    if not braked:      # a stop file, a pause, a job on the lane or the day's cap comes first: not ours to lift
        return {"state": "none", "reason": "; ".join("%s: %s" % (m, p["text"][:120]) for m, p in plans.items())}
    mod = braked[0]
    tails = plans[mod]["tail"]
    causes = causes_of(tails, now)
    rec = {"tail": tail_ids(tails), "causes": causes}
    if down or os.path.exists(T.q("quarantine.json")):
        return dict(rec, state="wait", reason="machine down since %s" % down if down else "quarantined")
    unknown = sorted(j for j, c in causes.items() if not c)
    if unknown:
        return dict(rec, state="escalate", reason="no recorded non-fault cause for %s" % ",".join(unknown))
    spent = spent_on(tails)
    if spent:
        return dict(rec, state="escalate", reason="canary %s spent on this tail and it did not end the brake" % spent.get("job"))
    hold = T.companion_hold()
    if hold:            # a canary now could only die the same death
        return dict(rec, state="wait", reason=hold)
    req = canary_request(mod, tails, now)
    if not req:
        return dict(rec, state="refused", reason="nothing to ask of %s: no pick and no chain on the tail" % mod)
    rc, line = submit(mod, req)
    try:
        job = json.loads(line).get("job") if rc == 0 else None
    except ValueError:
        job = None
    if not job:
        return dict(rec, state="refused", reason="submit exit %s: %s" % (rc, line[-200:]))
    T.log("brake release: %s on %s (%s): canary %s (%s %s)" % (rec["tail"], json.dumps(causes), mod, job, mod, req[0][0]))
    return dict(rec, state="released", reason="canary %s for %s" % (job, ",".join(rec["tail"])),
                canary={"job": job, "tail": rec["tail"], "at": now, "ts": S.utcnow()})


def release_pass(now=None, mods=None):
    now = time.time() if now is None else now
    prev = T.read_json(T.q(STATE)) or {}
    import coverage     # the filler's own list (wired_mods.json; TESTQ_FILL_MODS overrides)
    rec = decide(now, mods or coverage.fill_mods())
    rec.setdefault("canary", prev.get("canary"))
    rec.update(ts=S.utcnow(), epoch=now)
    S.dump(rec, T.q(STATE))
    return rec


def main():
    rec = release_pass()
    print("brake_release: %s: %s" % (rec["state"], rec["reason"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
