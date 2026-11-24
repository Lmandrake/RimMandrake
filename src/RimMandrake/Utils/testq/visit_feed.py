#!/usr/bin/env python3
"""visit_feed.py - an open in-game visit's testq checks go to the SteveDesktop lane ahead of filler
(RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER; page design/specs/2026-11-22-steve-idle-takeable/boundary.md;
tests src/RimMandrake/Utils/selftest_steve_visit_feed.py).

The failure (measured 2026-11-22): the lane ran filler for 5.5 h, and 10.5 h by 03:30Z, while 28 Pyrelands and 6
FlowWorks checks of open in-game visits carried a testq block. Nothing sent them: the filler ranks evidence gaps per
wired mod and never reads a visit.

`step()` runs at the start of every testq tick (testq.cmd_tick, before admission, so its job is admitted in the same
tick). It reads the dispatch tick's `ingame_testq` block (maturation_dispatch.ingame_testq: per in-game mod, the visit,
its opening and the checks it runs that carry a testq block, less those with a row in the visit's folder), and queues
ONE job on the SteveDesktop lane for the visit that waits: its waiting chains, requested by BENCH.visit at priority 40
(the filler's is 20), so the next admission takes it and fill_plan reads the lane busy while it waits. Work done
elsewhere drains a check when each of its chains ran DONE for the mod since the visit opened with a PASS or FAIL row
(ops_watch.c_steve_takeable counts any DONE run; a DONE run that read only UNMEASURED rows drains nothing here). Nothing is queued when the lane is stopped or paused, a visit job is already pending or running, the
mod is held (the reading's flag, and `testq.py submit`'s own hold refusal), the visit is blocked or its exit is met, or
a chain waits on the owner's gate. A reading that could not be read sends nothing and says why (state `unmeasured`).

    testq.py visit-feed [--dry]     the same step by hand; --dry says what it would queue
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

BY = "BENCH.visit"
PRIORITY = 40               # above the filler's 20; under a hand commission's 50 (testq.py submit's default priority)
# The dispatch tick writes its reading every 60 s; one older than this is a dead step (the same line as
# ops_watch.MATURATION_READING_MAX_AGE_S), and a check read from it may have run already.
READING_MAX_AGE_S = 1800
# A chain whose jobs failed by their own fault (failure_class: BAD REQUEST, the same job is refused again) this many
# times since the visit opened is not sent again: sending it every tick spins the lane (the filler brake's evidence: two
# filler jobs in a row not DONE; 20 h of lane lost 2026-10-25). It is named in the step's `spent` until the visit reopens.
FAILS_TO_STOP = 2
# A run that held the lane and whose outcome is not the chain's own (killed, INVALID, no verdict read, or nobody can
# class it) spends nothing (RIMMANDRAKE_SHARE_ONE_FAILURE_CLASSIFIER_EVERY_COUNTER_ROLLED_ITS_OWN): the chain waits
# BOUNCE_BACKOFF_S, doubled for each such run in a row, this long at most, and is named in `faults`.
FAULT_BACKOFF_MAX_S = 7200
# A run the lane refused before the chain ran (REFUSED for a cause in testq.ARCH_BOUNCE - deploy, load, the guard's
# hold - or SYNC, the runner's pull) measured nothing about the chain and is not one of those failures: live 2026-11-23,
# four FlowWorks visit jobs refused LOAD on Steve2 (its game was up) spent six chains, and the feed read `quiet` for six
# hours with the checks never run. A chain just refused so waits this long before it is sent again, so the feed does not
# resend into the same refusal every tick: longer than the 1-4 min one refusal cycle took on Steve2 that day (done
# records), under the 30 min line of the lane's idle alarm (ops_watch_rules.json steve.idle_with_takeable_min).
LANE_REFUSALS = {"SYNC"}       # with testq.ARCH_BOUNCE
BOUNCE_BACKOFF_S = 600


def _T():
    import testq
    return testq


def _failure_class():
    rf = os.path.join(HERE, "..", "..", "rimflow")
    if rf not in sys.path:
        sys.path.append(rf)
    import failure_class
    return failure_class


def _parse(ts):
    """ISO time -> epoch, or None. A visit's opening carries its offset ('2026-11-22T08:54:05-08:00'); testq's own
    stamps end in Z. schema.parse_ts reads only the Z form, and with it the live visits read as no opening at all."""
    if isinstance(ts, (int, float)) and not isinstance(ts, bool):
        return float(ts)
    import datetime
    try:
        return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError, OverflowError):
        return None


LIVE_QUEUE = "/mnt/d/ClaudeWork/rimmandrake/testq"     # testq.QHOME's default


def foreign_queue():
    """-> why this queue may not read the live dispatch reading, or None. A queue other than the live one (a selftest's
    temp TESTQ_QUEUE) reads only a dispatch reading named for it (RM_MATURATION_DISPATCH_DIR): selftest_testq.py's tick
    on a temp queue read the live reading and queued a live Pyrelands visit job into its fixture."""
    qh = os.environ.get("TESTQ_QUEUE")
    if qh and os.path.realpath(qh) != os.path.realpath(LIVE_QUEUE) and not os.environ.get("RM_MATURATION_DISPATCH_DIR"):
        return "the queue %s is not the live one and names no dispatch reading (RM_MATURATION_DISPATCH_DIR)" % qh
    return None


def reading(now):
    """-> (the ingame_testq block, None), or (None, why it could not be read)."""
    why = foreign_queue()
    if why:
        return None, why
    rf = os.path.join(HERE, "..", "..", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    try:
        import maturation_dispatch as MD
        p = os.path.join(MD.sdir(), "reading.json")
    except Exception as e:  # noqa: BLE001 - no reading place: could not look
        return None, "the dispatch reading's folder is unknown (%s: %s)" % (type(e).__name__, e)
    rd = _T().read_json(p)
    if not isinstance(rd, dict):
        return None, "the dispatch reading %s is missing or unreadable" % p
    at = rd.get("at")
    at = at if isinstance(at, (int, float)) else _parse(at)
    if at is None or now - at > READING_MAX_AGE_S or at > now + 300:
        return None, "the dispatch reading %s is %s old (the dispatch step is not ticking)" % (
            p, "of unknown age" if at is None else "%d min" % ((now - at) / 60))
    blk = rd.get("ingame_testq")
    if not isinstance(blk, dict):
        return None, "no ingame_testq block in %s (%s)" % (p, rd.get("ingame_testq_error") or "not written")
    return blk, None


def _chains(j):
    s = j.get("selector") if isinstance(j.get("selector"), dict) else {}
    return [c for c in s.get("chains") or [] if isinstance(c, str)]


def _measured(res):
    """-> the chains of a DONE result that read a verdict (a row PASS or FAIL). A DONE job whose rows for a chain were
    all UNMEASURED or NOT_RUN measured nothing of it: 5 Pyrelands jobs of 2026-11-19..23 came back DONE with every row
    UNMEASURED SITE (no site save on SteveDesktop), and counting them as run would drain the visit's checks unmeasured.
    A result with no rows at all (an older or hand-made record) counts every chain of its job as run."""
    rows = res.get("rows")
    if not isinstance(rows, list) or not rows:
        return set(_chains(res.get("job") if isinstance(res.get("job"), dict) else {})) | {"*"}
    return {r.get("chain") for r in rows if isinstance(r, dict) and r.get("verdict") in ("PASS", "FAIL")}


def waiting(now, blk, recs=None):
    """-> ({mod: {"opened", "visit", "checks": {check: [chains]}}}, {mod: {chain: failures}}, {mod: {chain: seconds}},
    {mod: {chain: {word: n}}}) for the visits whose checks still wait for a lane run; the second map names the chains not
    sent again (FAILS_TO_STOP), the third the chains held back that many seconds (BOUNCE_BACKOFF_S, doubled per fault in
    a row), the fourth the outcomes that did not count against a waiting chain (failure_class), by word."""
    T = _T()
    FC = _failure_class()
    out, unread = {}, {}
    for mod, e in sorted(blk.items()):
        if not isinstance(e, dict) or e.get("error") or e.get("hold_unreadable") or e.get("held") \
                or e.get("blocked") or e.get("owed") == "exit met":
            continue
        t0 = _parse(e.get("opened"))
        ch = {k: [c for c in v if isinstance(c, str)] for k, v in (e.get("checks") or {}).items() if isinstance(v, list)}
        ch = {k: v for k, v in ch.items() if v}
        if t0 is None and ch:
            unread[mod] = "visit opening %r unreadable" % e.get("opened")
        if t0 is None or not ch:
            continue
        out[mod] = {"opened": t0, "visit": e.get("visit"), "checks": ch}
    if not out:
        return {}, ({"unread": unread} if unread else {}), {}, {}
    gated = {}
    for j in T.records("pending"):
        if j.get("owner_gate") and j.get("mod") in out:
            gated.setdefault(j["mod"], set()).update(_chains(j))
    ran, runs, bounced = {}, {}, {}
    lane = set(getattr(T, "ARCH_BOUNCE", ())) | LANE_REFUSALS
    for rec in T.records("done") if recs is None else recs:
        j, res = T.job_of(rec), rec.get("result") or {}
        m = j.get("mod")
        if m not in out or rec.get("cancelled"):
            continue
        fin = _parse(rec.get("finished") or res.get("finished"))
        if fin is None or fin < out[m]["opened"]:
            continue
        if res.get("outcome") == "REFUSED" and res.get("cause") in lane:
            for c in _chains(j):        # the lane's refusal, not the chain's failure (LANE_REFUSALS)
                bounced.setdefault(m, {})[c] = max(bounced.get(m, {}).get(c, 0), fin)
            continue
        measured = _measured(res) if res.get("outcome") == "DONE" else set()
        for c in _chains(j):
            if c in measured or "*" in measured:
                ran.setdefault(m, set()).add(c)
            else:
                runs.setdefault((m, c), []).append((fin, FC.of_testq(rec, c)))
    fails, faults, held = {}, {}, {}
    for (m, c), rs in runs.items():
        n, left = FC.count(r for _, r in rs)
        if n:
            fails.setdefault(m, {})[c] = n
        if left and c not in ran.get(m, set()):
            faults.setdefault(m, {})[c] = left
        rs.sort(key=lambda x: x[0])
        row = 0
        while row < len(rs) and not rs[-1 - row][1].counts:
            row += 1
        if row:     # the faults in a row at the end: each doubles the wait
            held.setdefault(m, {})[c] = rs[-1][0] + min(FAULT_BACKOFF_MAX_S, BOUNCE_BACKOFF_S * 2 ** min(row - 1, 20))
    spent, backoff = {}, {}
    for m in list(out):
        keep = {}
        for k, v in out[m]["checks"].items():
            if set(v) <= ran.get(m, set()) or set(v) & gated.get(m, set()):
                continue
            left = [c for c in v if c not in ran.get(m, set())]
            dead = [c for c in left if fails.get(m, {}).get(c, 0) >= FAILS_TO_STOP]
            if dead:
                spent.setdefault(m, {}).update({c: fails[m][c] for c in dead})
            left = [c for c in left if c not in dead]
            due = {c: max(bounced.get(m, {}).get(c, 0) + BOUNCE_BACKOFF_S, held.get(m, {}).get(c, 0)) for c in left}
            wait = {c: int(t - now) for c, t in due.items() if t > now}
            if wait:
                backoff.setdefault(m, {}).update(wait)
            left = [c for c in left if c not in wait]
            if left:
                keep[k] = left
        if keep:
            out[m]["checks"] = keep
        else:
            del out[m]
    if unread:
        spent["unread"] = unread
    return out, spent, backoff, faults


def _order(w, recs):
    """The earliest-opened visit first; after that, the mod whose last visit job was submitted longest ago."""
    T = _T()
    last = {}
    for st in ("done", "cancelled"):
        for rec in (recs if st == "done" and recs is not None else T.records(st)):
            j = T.job_of(rec)
            if j.get("requested_by") == BY and j.get("mod") in w:
                last[j["mod"]] = max(last.get(j["mod"], 0), _parse(j.get("submitted")) or 0)
    return sorted(w, key=lambda m: (last.get(m, 0), w[m]["opened"], m))


def in_flight(T):
    """-> (the visit job that makes the feed busy, or None; the mods whose visit job is in flight). Busy while a visit job
    is pending, or while as many run as there are live Steve games (T.steve_lanes(): Steve2 too when switched on); a
    free second game takes a visit job of another mod (design/specs/2026-11-23-steve-two-games-lane/boundary.md)."""
    pend = [j for j in T.records("pending") if j.get("requested_by") == BY]
    run = [T.job_of(r) for r in T.records("running") if T.job_of(r).get("requested_by") == BY]
    lanes = T.steve_lanes() if hasattr(T, "steve_lanes") else [T.STEVE]
    busy = pend[0] if pend else (run[0] if len(run) >= len(lanes) else None)
    return busy, sorted({j.get("mod") for j in run})


def step(now=None, n=None, dry=False):
    """One tick's feed step -> a record: state `queued` (job), `busy`, `stopped`, `quiet` (nothing waits), `backoff`
    (what waits was refused by the lane just now), `refused`
    (every waiting mod refused at submit, each named) or `unmeasured` (why)."""
    T = _T()
    now = time.time() if now is None else now
    n = int(os.environ.get("TESTQ_FILL_CHAINS", "4")) if n is None else n     # the filler's chains per job
    T.ensure_dirs()
    if os.path.exists(T.q("fill.stop")):
        return {"state": "stopped", "why": "%s exists" % T.q("fill.stop")}
    if T.paused():
        return {"state": "stopped", "why": "the lane is paused"}
    busy, inflight = in_flight(T)
    if busy:
        return {"state": "busy", "job": busy.get("id"), "mod": busy.get("mod")}
    blk, why = reading(now)
    if blk is None:
        return {"state": "unmeasured", "why": why}
    recs = T.records("done")
    w, spent, backoff, faults = waiting(now, blk, recs)
    if not w:
        if spent.get("unread"):
            return {"state": "unmeasured", "why": "nothing readable waits, but not read: %s" % spent["unread"]}
        if backoff:     # {mod: {chain: seconds left}}: refused (LANE_REFUSALS) or at fault just now; never `quiet`
            return {"state": "backoff", "backoff": backoff, "spent": spent, "faults": faults}
        return {"state": "quiet", "spent": spent}
    r = subprocess.run(["git", "-C", T.REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        return {"state": "unmeasured", "why": "no origin/main in %s: %s" % (T.REPO, r.stderr.strip()[-200:])}
    sha = r.stdout.strip()
    refused = {}
    for mod in _order(w, recs):
        if mod in inflight:     # its job runs on the other game: never a second job for one mod
            continue
        e = w[mod]
        chains = []
        for k in sorted(e["checks"]):
            for c in e["checks"][k]:
                if c not in chains:
                    chains.append(c)
        pick = chains[:n]
        if dry:
            return {"state": "would_queue", "mod": mod, "chains": pick, "visit": e["visit"], "spent": spent,
                    "backoff": backoff, "faults": faults,
                    "waiting": {m: len(v["checks"]) for m, v in w.items()}}
        rc, text = _submit(T, mod, pick, sha, e)
        gone = T.unknown_chains(text) if rc != 0 else set()
        if rc != 0 and gone & set(pick):        # a chain modcheck no longer declares: drop it, once
            pick = [c for c in chains if c not in gone][:n]
            rc, text = _submit(T, mod, pick, sha, e) if pick else (2, text)
        if rc == 0:
            try:
                job = json.loads(text.strip().splitlines()[-1]).get("job")
            except (ValueError, IndexError, AttributeError):
                job = None
            T.log("visit feed: %s visit %s %s -> %s" % (mod, e["visit"], ",".join(pick), job))
            return {"state": "queued", "job": job, "mod": mod, "chains": pick, "visit": e["visit"], "spent": spent,
                    "backoff": backoff, "faults": faults,
                    "waiting": {m: len(v["checks"]) for m, v in w.items()}}
        refused[mod] = text.strip()[-300:]
    T.log("visit feed: every waiting mod refused: %s" % json.dumps(refused)[:400])
    return {"state": "refused", "refused": refused, "spent": spent}


def _submit(T, mod, chains, sha, e):
    """testq.py submit for MOD's waiting CHAINS -> (exit code, its printed text)."""
    import contextlib
    import io
    sub = argparse.Namespace(
        mod=mod, chains=",".join(chains), rows=None, item=None, full=False, purpose="commission", by=BY, sha=sha,
        for_item=None, profile=None, proofs=None, priority=PRIORITY, not_before=None, supersedes=None,
        owner_gate=None, lane="stevedesktop", gate=None, deploy=None, timeout=7200, no_canary=False,
        no_validity=False, situational=False, no_sha_check=False, row_item=[],
        retest_why="in-game visit %s of %s (opened %s) owes these checks; sent by the visit feed "
                   "(RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER)" % (
                       e["visit"], mod, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(e["opened"]))))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = T.cmd_submit(sub)
    return rc, buf.getvalue()


def cmd_visit_feed(a):
    out = step(dry=a.dry)
    print(json.dumps(out, sort_keys=True))
    return 0 if out.get("state") != "unmeasured" else 2
