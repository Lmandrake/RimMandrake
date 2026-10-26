#!/usr/bin/env python3
"""How well do we use the testing rigs? Per machine, per owner-day, no LLM (TESTING_RIG_MONITOR_EFFICIENCY_IN_PULSE).

Owner, 2026-10-25: "periodically check statistics to see how efficient we're being at using that testing
apparatus ... make sure what it finds is of use. Monitor those statistics over time, and compare them to our own
local testing here ... part of the RimPulse display monitor as well."

Two machines, each read from what it already writes (nothing here asks a rig anything):
  steve     SteveDesktop, the remote runner: testq records (/mnt/d/ClaudeWork/rimmandrake/testq/{done,orphans,
            cancelled,running,pending}) + the RUNNER ledger shard (finding / verify events).
  archmagi  this machine's own live testing: modcheck sheets (<clone>/Transient/modcheck/<Mod>_<stamp>.json), the
            bridge call log (scratch/bridge_calls.jsonl + .1) for busy time, BENCH/FOUNDRY finding/verify events.

Per day (America/Los_Angeles, modcheck/metrics.py's day) and machine:
  UTILISATION  busy % / load+deploy % / run % of the window, idle minutes while a job waited, longest idle gap,
               jobs, rows run, rows per busy hour.
  QUALITY      verdict counts and shares (PASS/FAIL/UNMEASURED/NOT_RUN rows; INVALID attempts), failures split
               harness (INVALID attempts) vs mod (FAIL rows).
  USEFULNESS   findings filed, items closed after a passing run on that machine, regressions (a row whose last
               measured verdict was PASS now FAILs), wasted runs (INVALID / INTERRUPTED, nothing measured,
               refused, or an unchanged rerun: same mod + selector + deployed dll/defs as an earlier DONE run,
               for a purpose that is not budgeted re-running, testq GATE_BYPASS).
Every value is {"v": x, "m": "MEASURED"} or {"v": None, "m": "UNMEASURED", "why": ...}: a source that is missing,
unreadable or does not cover the window says so instead of reading 0. Each source carries a probe (files seen,
records parsed, records unreadable) so a zero can be told from blindness.

History: one record per (day, change) appended to /mnt/d/ClaudeWork/rimmandrake/testing_metrics/history.jsonl
(env RM_TESTING_HISTORY). It lives in agent storage, not the repo: a program reads it (RimPulse, the phone brief),
its inputs live in agent storage too, and an hourly timer must never commit into a clone two seats share. A day is
recomputed every hour until it is over; read_history + best_per_day pick, per day, the record with the most
coverage and then the latest.

Usage: testing_metrics.py [--days N] [--print] [--no-write]     (hourly: rm-pulse-testing.timer)
"""
import argparse
import datetime
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
sys.path.insert(0, UTILS)
import metrics as MX  # noqa: E402  modcheck/metrics.py: the owner-day, sheet loader, per-lane chain waste

SCHEMA = "rm.testing_metrics/1"
MARKS = ("MEASURED", "UNMEASURED")
TESTQ_ROOT = os.environ.get("RM_TESTQ_ROOT", MX.TESTQ_DEFAULT)
BRIDGE_LOG = os.environ.get("RM_BRIDGE_LOG", "/mnt/d/ClaudeWork/rimmandrake/scratch/bridge_calls.jsonl")
CLONES = ("/home/mandrake/rm/bench", "/home/mandrake/rm/foundry")
SHEET_DIRS = tuple(os.path.join(c, "Transient", "modcheck") for c in CLONES)
STEVE_SEATS = ("RUNNER",)
LOCAL_SEATS = ("BENCH", "FOUNDRY")
BUDGETED_RERUN = ("sweep", "sensitivity", "flake", "commission")    # testq schema GATE_BYPASS: re-running is the point
RAN = ("PASS", "FAIL", "UNMEASURED")                                # a row that executed (NOT_RUN / SKIP did not)
ROW_VERDICTS = ("PASS", "FAIL", "UNMEASURED", "NOT_RUN", "SKIP")
BRIDGE_MERGE_S = 120        # bridge calls closer than this are one busy stretch (a script's call cadence)
BLIND_BAD_SHARE = 0.10      # more than this share of unreadable records: the source is blind, not partial
INFO_KEYS = ("findings_by_type", "waste_why", "probe", "lane_waste_note")
PANEL_METRICS = ("busy_pct", "rows_per_hour", "findings", "waste_pct")


def history_path():
    return os.environ.get("RM_TESTING_HISTORY") or "/mnt/d/ClaudeWork/rimmandrake/testing_metrics/history.jsonl"


# ---------------------------------------------------------------- values
def M(v, note=None):
    d = {"v": v, "m": "MEASURED"}
    if note:
        d["note"] = note
    return d


def U(why):
    return {"v": None, "m": "UNMEASURED", "why": why}


def leaves(d):
    """Every measured/unmeasured value in a machine record (selftest: nothing may be a bare number)."""
    if isinstance(d, dict) and "m" in d:
        yield d
        return
    if isinstance(d, dict):
        for k, x in d.items():
            if k not in INFO_KEYS:
                yield from leaves(x)
    else:
        yield d


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def epoch(s):
    if s in (None, ""):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def pct(a, b):
    return round(100.0 * a / b, 1)


# ---------------------------------------------------------------- intervals
def union(spans, gap=0):
    out = []
    for s, e in sorted((s, e) for s, e in spans if e > s):
        if out and s - out[-1][1] <= gap:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def clip(spans, lo, hi):
    return [(max(s, lo), min(e, hi)) for s, e in spans if min(e, hi) > max(s, lo)]


def length(spans):
    return sum(e - s for s, e in spans)


def overlap(a, b):
    a, b = union(a), union(b)
    return sum(max(0, min(e1, e2) - max(s1, s2)) for s1, e1 in a for s2, e2 in b)


def gaps(spans, lo, hi):
    """The idle stretches of [lo, hi) not covered by spans."""
    out, cur = [], lo
    for s, e in union(clip(spans, lo, hi)):
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if hi > cur:
        out.append((cur, hi))
    return out


# ---------------------------------------------------------------- SteveDesktop: testq
def _attempt(job, res):
    job = job if isinstance(job, dict) else {}
    dep = ((res.get("deployed") or {}).get("mods") or {}).get(job.get("mod") or "") or {}
    ident = None
    if dep.get("dll_sha256") or dep.get("defs_sha256"):
        ident = (job.get("mod"), json.dumps(job.get("selector"), sort_keys=True), dep.get("dll_sha256"),
                 dep.get("defs_sha256"))
    return {"job": job.get("id") or res.get("job"), "attempt": res.get("attempt"), "mod": job.get("mod"),
            "purpose": job.get("purpose"), "submitted": epoch(job.get("submitted")), "started": epoch(res.get("started")),
            "finished": epoch(res.get("finished")), "outcome": res.get("outcome"), "cause": res.get("cause"),
            "phase_s": res.get("phase_s") or {}, "rows": [r for r in res.get("rows") or [] if isinstance(r, dict)],
            "ident": ident}


def load_testq(root=None):
    """Every testq record by state. Probe: files seen / records parsed / unreadable."""
    root = root or TESTQ_ROOT
    out = {"root": root, "attempts": [], "pending": [], "running": [], "submits": [],
           "probe": {"root": root, "files": 0, "records": 0, "bad": 0}}
    if not os.path.isdir(root):
        out["why"] = f"testq root {root} not found"
        return out
    pr = out["probe"]
    for state in ("done", "orphans", "cancelled", "running", "pending"):
        d = os.path.join(root, state)
        try:
            names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
        except OSError:
            continue
        for n in names:
            pr["files"] += 1
            try:
                with open(os.path.join(d, n), encoding="utf-8") as f:
                    rec = json.load(f)
            except (OSError, ValueError):
                pr["bad"] += 1
                continue
            if not isinstance(rec, dict):
                pr["bad"] += 1
                continue
            if rec.get("schema") == "testq.result/1":                       # orphan: a result with no job record
                out["attempts"].append(_attempt({"id": rec.get("job")}, rec))
            elif rec.get("schema") == "testq.job/1":                       # pending
                out["pending"].append(rec)
                out["submits"].append(epoch(rec.get("submitted")))
            elif isinstance(rec.get("job"), dict):                          # done / cancelled / running wrapper
                job = rec["job"]
                out["submits"].append(epoch(job.get("submitted")))
                if isinstance(rec.get("result"), dict):
                    out["attempts"].append(_attempt(job, rec["result"]))
                elif state == "running":
                    out["running"].append({"job": job, "sent": epoch(rec.get("sent")), "submitted": epoch(job.get("submitted"))})
            else:
                pr["bad"] += 1
                continue
            pr["records"] += 1
    if pr["records"] == 0 and pr["bad"] > 0 or pr["files"] and pr["bad"] / pr["files"] > BLIND_BAD_SHARE:
        out["why"] = f"testq blind: {pr['bad']} of {pr['files']} records unreadable"
    subs = [t for t in out["submits"] + [a["submitted"] or a["started"] for a in out["attempts"]] if t]
    out["commissioned"] = min(subs) if subs else None
    return out


def _ledger_day(ledger, seats, d0, d1, event):
    return [e for e in ledger if e.get("event") == event and e.get("seat") in seats
            and d0 <= (epoch(e.get("ts")) or -1) < d1]


def closed_after_pass(ledger, d0, d1, is_pass):
    """Items closed in [d0, d1) that had a passing run (is_pass(verify event)) BEFORE the close."""
    first = {}
    for e in ledger:
        if e.get("event") == "verify" and e.get("result") == "pass" and is_pass(e):
            t = epoch(e.get("ts"))
            if t is not None and (e.get("id") not in first or t < first[e["id"]]):
                first[e["id"]] = t
    n = set()
    for e in ledger:
        t = epoch(e.get("ts"))
        if e.get("event") == "close" and t is not None and d0 <= t < d1 and e.get("id") in first and first[e["id"]] < t:
            n.add(e["id"])
    return len(n)


def regressions(runs, d0, d1):
    """runs: [(t, mod, [(chain, row, verdict)])]. A row whose last MEASURED verdict (PASS/FAIL) was PASS and now
    FAILs, counted when the FAIL lands in [d0, d1). UNMEASURED between them neither breaks nor makes one."""
    last, n = {}, 0
    for t, mod, rows in sorted(runs, key=lambda r: r[0]):
        for ch, row, vd in rows:
            if vd not in ("PASS", "FAIL"):
                continue
            k = (mod, ch, row)
            if vd == "FAIL" and last.get(k) == "PASS" and d0 <= t < d1:
                n += 1
            last[k] = vd
    return n


def _verdicts(counts, attempts, invalid):
    rows = sum(counts[k] for k in ROW_VERDICTS)
    vc = {k: M(counts[k]) for k in ROW_VERDICTS}
    vc["INVALID"] = M(invalid)
    sh = {k: (M(pct(counts[k], rows)) if rows else U("no rows ran")) for k in ROW_VERDICTS}
    sh["INVALID"] = M(pct(invalid, attempts)) if attempts else U("no attempts")
    return vc, sh


def _unmeasured_machine(why):
    keys = ("window_h", "busy_pct", "load_pct", "run_pct", "idle_waiting_min", "max_idle_gap_min", "jobs",
            "rows_run", "rows_per_hour", "regressions", "findings", "closed_after_pass", "wasted", "waste_pct")
    d = {k: U(why) for k in keys}
    d["verdict_counts"] = {k: U(why) for k in ROW_VERDICTS + ("INVALID",)}
    d["verdicts"] = {k: U(why) for k in ROW_VERDICTS + ("INVALID",)}
    d["fail_split"] = {"harness": U(why), "mod": U(why)}
    d["findings_by_type"], d["waste_why"] = {}, {}
    return d


def steve_day(src, ledger, d0, d1, now):
    """SteveDesktop for the window [d0, d1) as seen at `now`."""
    if src.get("why"):
        out = _unmeasured_machine(src["why"])
    elif not src.get("commissioned") or src["commissioned"] >= min(d1, now):
        out = _unmeasured_machine("SteveDesktop not commissioned yet in this window (no testq job before it)")
    else:
        out = None
    if out is not None:
        out["probe"] = src.get("probe")
        return out
    lo, hi = max(d0, src["commissioned"]), min(d1, now)
    win = hi - lo
    atts = [a for a in src["attempts"] if a["started"] and a["finished"]]
    busy = [(a["started"], a["finished"]) for a in atts]
    busy += [(r["sent"], now) for r in src["running"] if r["sent"]]
    busy_in = union(clip(busy, lo, hi))
    today = [a for a in atts if lo <= a["finished"] < hi]
    load_s = sum(sum(float(v or 0) for k, v in a["phase_s"].items() if k != "run") for a in today)
    run_s = sum(float(a["phase_s"].get("run") or 0) for a in today)
    waits = [(a["submitted"], a["started"]) for a in atts if a["submitted"]]
    waits += [(r["submitted"], r["sent"] or now) for r in src["running"] if r["submitted"]]
    waits += [(epoch(p.get("submitted")), now) for p in src["pending"] if epoch(p.get("submitted"))]
    idle = gaps(busy_in, lo, hi)
    counts = Counter(r.get("verdict") for a in today for r in a["rows"])
    rows_run = sum(counts[k] for k in RAN)
    invalid = sum(1 for a in today if a["outcome"] == "INVALID")
    harness = sum(1 for a in today if a["outcome"] in ("INVALID", "INTERRUPTED"))
    vc, sh = _verdicts(counts, len(today), invalid)
    # waste, in time order so 'unchanged rerun' compares against what ran before
    seen, why = set(), Counter()
    for a in sorted(atts, key=lambda a: a["finished"]):
        measured = any(r.get("verdict") in ("PASS", "FAIL") for r in a["rows"])
        reason = None
        if a["outcome"] in ("INVALID", "INTERRUPTED"):
            reason = "invalid"
        elif a["outcome"] == "REFUSED":
            reason = "refused"
        elif not measured:
            reason = "all_unmeasured"
        elif a["ident"] in seen and a["purpose"] not in BUDGETED_RERUN:
            reason = "unchanged_rerun"
        if a["outcome"] == "DONE" and measured and a["ident"]:
            seen.add(a["ident"])
        if reason and a in today:
            why[reason] += 1
    wasted = sum(why.values())
    finds = _ledger_day(ledger, STEVE_SEATS, lo, hi, "finding")
    busy_s = length(busy_in)
    out = {
        "window_h": M(round(win / 3600, 2)),
        "busy_pct": M(pct(busy_s, win)),
        "load_pct": M(pct(load_s, win)),
        "run_pct": M(pct(run_s, win)),
        "idle_waiting_min": M(round(overlap(idle, clip(union(waits), lo, hi)) / 60, 1)),
        "max_idle_gap_min": M(round(max([e - s for s, e in idle] or [0]) / 60, 1)),
        "jobs": M(len(today)),
        "rows_run": M(rows_run),
        "rows_per_hour": M(round(rows_run / (busy_s / 3600), 1)) if busy_s else U("not busy in the window"),
        "verdict_counts": vc, "verdicts": sh,
        "fail_split": {"harness": M(harness), "mod": M(counts["FAIL"])},
        "regressions": M(regressions([(a["finished"], a["mod"], [(r.get("chain"), r.get("row"), r.get("verdict"))
                                                                  for r in a["rows"]]) for a in atts], lo, hi)),
        "findings": M(len(finds)),
        "findings_by_type": dict(Counter(e.get("type") or "?" for e in finds)),
        "closed_after_pass": M(closed_after_pass(ledger, lo, hi, lambda e: e.get("seat") in STEVE_SEATS)),
        "wasted": M(wasted),
        "waste_pct": M(pct(wasted, len(today))) if today else U("no attempts in the window"),
        "waste_why": dict(why),
        "probe": src["probe"],
    }
    return out


def steve_live(src, now):
    """What the RimPulse red rule needs right now: idle since, jobs waiting, SSH down since, paused lane."""
    root = src.get("root") or TESTQ_ROOT
    ends = [a["finished"] for a in src.get("attempts") or [] if a["finished"]]
    idle_since = None if src.get("running") else (max(ends) if ends else None)

    def rd(name):
        try:
            with open(os.path.join(root, name), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None
    ssh = rd("ssh_state.json") or {}
    return {"idle_since": idle_since, "pending": len(src.get("pending") or []), "running": len(src.get("running") or []),
            "ssh_down_since": epoch(ssh.get("down_since")), "paused": rd("paused.json"), "ok": not src.get("why")}


# ---------------------------------------------------------------- Archmagi: bridge log + local modcheck sheets
def load_bridge(path=None):
    """Bridge call spans from the live log and its one rotation. coverage_start = the oldest line still on disk."""
    path = path or BRIDGE_LOG
    pr = {"files": 0, "records": 0, "bad": 0}
    starts, spans, first = {}, [], None
    for p in (path + ".1", path):
        try:
            f = open(p, encoding="utf-8", errors="replace")
        except OSError:
            continue
        pr["files"] += 1
        with f:
            for line in f:
                try:
                    r = json.loads(line)
                    t = epoch(r.get("t"))
                except (ValueError, AttributeError):
                    pr["bad"] += 1
                    continue
                if t is None:
                    pr["bad"] += 1
                    continue
                pr["records"] += 1
                first = t if first is None else min(first, t)
                if r.get("ev") == "start":
                    starts[r.get("cid")] = t
                elif r.get("ev") == "end" and r.get("cid") in starts:
                    spans.append((starts.pop(r["cid"]), t))
    out = {"probe": pr, "spans": union(spans, gap=BRIDGE_MERGE_S), "coverage_start": first}
    if pr["files"] == 0:
        out["why"] = f"bridge call log {path} not found"
    elif pr["records"] == 0:
        out["why"] = f"bridge call log blind: {pr['bad']} unreadable lines, none parsed"
    return out


def load_sheets(dirs=None):
    """Local modcheck sheets via modcheck/metrics.py's loader -> [(t, mod, rows, refused)] + probe."""
    dirs = dirs or SHEET_DIRS
    files = 0
    for d in dirs:
        try:
            files += sum(1 for n in os.listdir(d) if n.endswith(".json") and "_" in n)
        except OSError:
            pass
    runs, _, _ = MX.load_sources(list(dirs), None)
    out = []
    for (mod, st), (_, d) in runs.items():
        rows = [(ch.get("name"), c.get("name"), c.get("verdict")) for ch in (d.get("summary") or {}).get("chains") or []
                if isinstance(ch, dict) for c in ch.get("components") or [] if isinstance(c, dict)]
        out.append((MX._epoch_of_stamp(st), mod, rows, (d.get("summary") or {}).get("refused") or ""))
    res = {"runs": out, "probe": {"dirs": list(dirs), "files": files, "records": len(out)}}
    if files and not out:
        res["why"] = f"modcheck sheets blind: {files} files, none parsed"
    return res


def archmagi_day(sheets, br, ledger, d0, d1, now):
    hi = min(d1, now)
    if sheets.get("why"):
        return dict(_unmeasured_machine(sheets["why"]), probe={"sheets": sheets.get("probe"), "bridge": br.get("probe")})
    runs = sheets["runs"]
    today = [r for r in runs if d0 <= r[0] < hi]
    counts = Counter(vd for r in today for _, _, vd in r[2])
    rows_run = sum(counts[k] for k in RAN)
    vc, sh = _verdicts(counts, len(today), 0)
    vc["INVALID"] = sh["INVALID"] = U("local sheets record no INVALID attempts")
    why = Counter()
    for r in today:
        if r[3]:
            why["refused"] += 1
        elif not any(vd in ("PASS", "FAIL") for _, _, vd in r[2]):
            why["all_unmeasured"] += 1
    wasted = sum(why.values())
    finds = _ledger_day(ledger, LOCAL_SEATS, d0, hi, "finding")
    out = _unmeasured_machine("")
    out.update({
        "jobs": M(len(today)), "rows_run": M(rows_run), "verdict_counts": vc, "verdicts": sh,
        "fail_split": {"harness": U("local sheets do not record INVALID attempts"), "mod": M(counts["FAIL"])},
        "regressions": M(regressions([(r[0], r[1], r[2]) for r in runs], d0, hi)),
        "findings": M(len(finds), note="BENCH/FOUNDRY ledger finding events (modcheck record); an item filed by hand "
                                         "from a local run is not counted"),
        "findings_by_type": dict(Counter(e.get("type") or "?" for e in finds)),
        "closed_after_pass": M(closed_after_pass(
            ledger, d0, hi, lambda e: e.get("seat") in LOCAL_SEATS and "offline" not in str(e.get("config") or ""))),
        "wasted": M(wasted),
        "waste_pct": (M(pct(wasted, len(today)), note="unchanged_rerun UNMEASURED: local sheets carry no source identity")
                      if today else U("no local modcheck runs in the window")),
        "waste_why": dict(why),
        "load_pct": U("local runs record no attest/deploy/load phase timings"),
        "run_pct": U("local runs record no run phase timings"),
        "idle_waiting_min": U("there is no local job queue to wait in"),
        "probe": {"sheets": sheets["probe"], "bridge": br.get("probe")},
    })
    cov = br.get("coverage_start")
    if br.get("why") or cov is None or cov >= hi:
        why_b = br.get("why") or "the bridge call log does not reach back to this window"
        for k in ("window_h", "busy_pct", "max_idle_gap_min"):
            out[k] = U(why_b)
        out["rows_per_hour"] = U(why_b)
        return out
    lo = max(d0, cov)
    busy = union(clip(br["spans"], lo, hi))
    busy_s, win = length(busy), hi - lo
    note = None if lo == d0 else f"bridge log covers from {iso(lo)} only"
    out["window_h"] = M(round(win / 3600, 2), note=note)
    out["busy_pct"] = M(pct(busy_s, win), note="bridge-active time (calls merged across gaps <= %d s)" % BRIDGE_MERGE_S)
    out["max_idle_gap_min"] = M(round(max([e - s for s, e in gaps(busy, lo, hi)] or [0]) / 60, 1))
    out["rows_per_hour"] = (M(round(rows_run / (busy_s / 3600), 1)) if busy_s and rows_run
                            else U("no local rows ran" if busy_s else "bridge idle all window"))
    return out


# ---------------------------------------------------------------- one day's record + history
def day_record(day, now, src, sheets, br, ledger):
    d0, d1 = MX.day_bounds(day)
    steve = steve_day(src, ledger, d0, d1, now)
    try:      # modcheck/metrics.py's own per-lane chain-minute waste, attached rather than recomputed
        lane = (MX.compute(day, sheet_dirs=list(SHEET_DIRS), testq_root=src.get("root"), now=now, record=False)
                .get("by_lane") or {}).get("stevedesktop")
        steve["lane_waste_note"] = lane.get("waste") if isinstance(lane, dict) else None
    except Exception as ex:  # noqa: BLE001 - an attachment; never let it blank the record
        steve["lane_waste_note"] = f"metrics.compute failed: {type(ex).__name__}: {ex}"
    return {"schema": SCHEMA, "day": day.isoformat(), "generated": iso(now),
            "coverage": round(max(0.0, min(1.0, (min(d1, now) - d0) / (d1 - d0))), 4),
            "machines": {"steve": steve, "archmagi": archmagi_day(sheets, br, ledger, d0, d1, now)}}


def read_history(path=None):
    out = []
    try:
        with open(path or history_path(), encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict) and r.get("day"):
                    out.append(r)
    except OSError:
        pass
    return out


def best_per_day(recs):
    best = {}
    for r in recs:      # file order is append order: a later equal-coverage record wins
        b = best.get(r["day"])
        if b is None or (r.get("coverage") or 0) >= (b.get("coverage") or 0):
            best[r["day"]] = r
    return best


def _same(a, b):
    strip = lambda r: {k: v for k, v in r.items() if k not in ("generated", "coverage")}  # noqa: E731
    return json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)


def append_if_changed(path, rec):
    prev = [r for r in read_history(path) if r.get("day") == rec["day"]]
    if prev and _same(prev[-1], rec):
        return False
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return True


def read_ledger():
    sys.path.insert(0, HERE)
    import pulse_core as pc
    return pc.read_ledger()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=int, default=2, help="owner-days to (re)compute, ending today (backfill: 7)")
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    now = datetime.datetime.now().timestamp()
    today = datetime.datetime.now(MX._tz()).date()
    src, sheets, br, ledger = load_testq(), load_sheets(), load_bridge(), read_ledger()
    path = history_path()
    if not read_history(path):
        a.days = max(a.days, 7)       # first run: backfill the sparkline week
    for i in range(a.days - 1, -1, -1):
        day = today - datetime.timedelta(days=i)
        rec = day_record(day, now, src, sheets, br, ledger)
        wrote = False if a.no_write else append_if_changed(path, rec)
        s, ar = rec["machines"]["steve"], rec["machines"]["archmagi"]
        show = lambda m, k: ("%s" % m[k]["v"]) if m[k]["m"] == "MEASURED" else "UNM"  # noqa: E731
        print(f"{rec['day']} {'appended' if wrote else 'unchanged'}  steve busy {show(s, 'busy_pct')}% "
              f"rows/h {show(s, 'rows_per_hour')} findings {show(s, 'findings')} waste {show(s, 'waste_pct')}%  |  "
              f"archmagi busy {show(ar, 'busy_pct')}% rows/h {show(ar, 'rows_per_hour')} "
              f"findings {show(ar, 'findings')} waste {show(ar, 'waste_pct')}%")
        if a.print:
            print(json.dumps(rec, indent=1, sort_keys=True))
    print(f"probes: testq {src['probe']} | sheets {sheets['probe']['records']}/{sheets['probe']['files']} | "
          f"bridge {br['probe']} | ledger {len(ledger)} events -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
