#!/usr/bin/env python3
"""brake_release.py - Operations releases a filler brake that has a recorded non-fault cause. No LLM.

STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE. 2026-11-03: the filler braked on a hardware crash and a job cancelled for a BIOS
visit, ops_watch read steve.state=BRAKED with unowned_stall 0 because the steward was escalating, and nothing acted until
the owner asked. ops_watch runs this on every filing pass that measures steve (ops_watch.steve_release_start;
since 2026-11-05 the metronome's sense phase, about every 13 min), started before the collectors so a 15 s beat fits it.

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
import copy
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
# budget: danger=a known brake that nobody releases; ends no work: the steward's ladder starts
RELEASE_GRACE_S = 1800      # two rm-ops-watch passes: past this a known brake is a plain fault, and the ladder runs
STATE = "brake_release.json"


def read_cache_path():
    """One cache per queue directory, so a selftest's temp queue never evicts the live one's."""
    import hashlib
    return os.environ.get("TESTQ_READ_CACHE") or "/tmp/rm_brake_release_reads_%s.json" % hashlib.sha1(
        os.path.abspath(T.q()).encode()).hexdigest()[:10]


@contextlib.contextmanager
def records_once():
    """A pass reads each queue file once (RIMMANDRAKE_SPEED_BRAKE_RELEASE_PASS_MISSES_ITS_BEAT): filler_jobs, brake_tail,
    lane_proven_after and fill_plan each re-read every record, 7 walks and 3,159 json reads over the D: mount, so a
    paused-lane pass took 11.9 s of its 15 s beat (2026-11-19; 145 s on 2026-11-13 before the lazy plan). The memo is
    keyed on the path, lives for this pass only, hands each caller its own parse, and is off while submit() writes.
    Under it, a local-disk cache (read_cache_path) keeps each file's text by (mtime, size): a stat is ~1 ms over D:, a read ~3 ms,
    and done/ only grows (1,032 records on 2026-11-19). A cache that cannot be read or written only costs the reads."""
    real, memo, cache = T.read_json, {}, read_cache_path()
    try:
        with open(cache, encoding="utf-8") as f:
            disk = json.load(f)
        if not isinstance(disk, dict):
            disk = {}
    except (OSError, ValueError):
        disk = {}
    seen, dirty = {}, [False]
    qdir = os.path.abspath(T.q())

    def text_of(key):
        if not key.startswith(qdir + os.sep):
            return None
        try:
            st = os.stat(key)
        except OSError:
            return None
        stamp = [st.st_mtime_ns, st.st_size]
        hit = disk.get(key)
        if isinstance(hit, list) and len(hit) == 3 and hit[:2] == stamp:
            seen[key] = hit
            return hit[2]
        try:
            with open(key, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return None
        seen[key] = stamp + [text]
        dirty[0] = True
        return text

    def once(path):
        key = os.path.abspath(path)
        if key not in memo:
            text = text_of(key)
            if text is None:
                memo[key] = ("real", real(path))
            else:
                try:
                    json.loads(text)
                    memo[key] = ("text", text)
                except ValueError:
                    memo[key] = ("real", None)
        kind, val = memo[key]
        return json.loads(val) if kind == "text" else copy.deepcopy(val)
    once.__wrapped_real__ = real
    T.read_json = once
    try:
        yield memo
    finally:
        T.read_json = real
        if dirty[0] or set(disk) - set(seen):
            try:
                tmp = cache + ".%d.tmp" % os.getpid()
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(seen, f)
                os.replace(tmp, cache)
            except OSError:
                pass


@contextlib.contextmanager
def live_reads():
    """Inside records_once: real reads again, for the submit that writes the queue."""
    memoized = T.read_json
    T.read_json = getattr(memoized, "__wrapped_real__", None) or memoized
    try:
        yield
    finally:
        T.read_json = memoized


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
                           supersedes=None, owner_gate=None, lane=T.STEVE, deploy=None, timeout=21600, no_canary=False,  # budget: danger=a hung run holds one game of the lane with no end; longest=2554s of 430 runs with this bound (testq done records, phase_s, 14 days to 2026-11-24); stays=a worker at an older commit refuses a job over 21600 s before it syncs; raise it when every lane's worker runs schema.py of 2026-11-24
                           no_validity=False, no_sha_check=True, retest_why=why,
                           row_item=["%s=%s" % kv for kv in sorted(rows.items())])
    out = io.StringIO()
    with contextlib.redirect_stdout(out), live_reads():
        rc = T.cmd_submit(a)
    lines = out.getvalue().strip().splitlines()
    return rc, lines[-1] if lines else ""


def decide(now, mods):
    """-> the record of this pass, submitting when it says released."""
    T.ensure_dirs()
    down = (T.read_json(T.q("ssh_state.json")) or {}).get("down_since")
    if not T.brake_tail(T.filler_jobs()):
        return {"state": "none", "reason": "no filler brake"}
    # Planned lazily (fill_plan reads every filler job: one per mod made a pass over 120 s, 2026-11-17). Only `held` is
    # mod-specific; every other verdict is the lane's, the same for every mod, so the first mod that is not held settles it.
    cap = int(os.environ.get("TESTQ_FILL_CAP") or T.FILL_CAP_DEFAULT)
    plans, unmeasured, mod = {}, {}, None
    for m in mods:
        try:
            p = T.fill_plan(m, 1, cap, now=now)
        except Exception as e:      # could not look: neither braked nor clear
            unmeasured[m] = "%s: %s" % (type(e).__name__, str(e)[:120])
            continue
        plans[m] = p
        if p["verdict"] == "brake":
            mod = m
            break
        if p["verdict"] != "held":
            break
    seen = set(plans) | set(unmeasured)
    looked = {"planned": sorted(plans), "unmeasured": unmeasured, "not_planned": [m for m in mods if m not in seen]}
    if mod is None:
        if not plans:   # nothing could be planned (or no mod was given): no answer, never "no brake"
            return dict(looked, state="unmeasured", reason="no mod could be planned: %s" % (
                "; ".join("%s: %s" % kv for kv in sorted(unmeasured.items())[:3]) or "the mod list is empty"))
        # a stop file, a pause, a job on the lane or the day's cap comes first: not ours to lift
        return dict(looked, state="none", reason="; ".join("%s: %s" % (m, p["text"][:120]) for m, p in plans.items()))
    tails = plans[mod]["tail"]
    causes = causes_of(tails, now)
    rec = dict(looked, tail=tail_ids(tails), causes=causes)
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
    with records_once():
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
