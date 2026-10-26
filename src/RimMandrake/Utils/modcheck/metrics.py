#!/usr/bin/env python3
"""modcheck.metrics -- the daily test-orchestration metrics file (MODCHECK_METRICS_BUILD_DAILY_WASTE; plan
design/RimMandrake/test_orchestration_two_machines_2026-10-25.md section 5).

    python3 src/RimMandrake/Utils/modcheck/cli.py metrics [--day YYYY-MM-DD] [--print]
    python3 src/RimMandrake/Utils/modcheck/metrics.py      (the same)

writes D:\\ClaudeWork\\rimmandrake\\testq\\metrics\\<day>.json (TESTQ_ROOT overrides the testq root; --out the folder).
The day is the owner's (America/Los_Angeles), so "a day" in an alarm is his day.

SOURCES (read only, except the miss lines below):
  modcheck run JSONs (runner.write_sheet: {mod, stamp, summary}) in Transient/modcheck, MODCHECK_GATE_HISTORY and,
    recursively, the testq root (results fetched from SteveDesktop carry their sheet JSON);
  testq records under the testq root: schema testq.job/1 and testq.result/1 (testq/schema.py).

PER CHAIN (one chain dict of one run; minutes = the sum of its phase_s hold/body/teardown -- shared setup and teardown
are per chain already, deploy and load are not in phase_s and are reported as `load_overhead_min`):
  waste         a chain the run marked offline (summary.offline_chains) that ran in the live slot; or a chain the
                known-good gate said would_skip (its recorded PASS still held) under purpose fix/guard;
  budgeted      would_skip under purpose sweep/sensitivity/flake/commission: the re-run was the point
                (the gate is advisory for those; plan section 3 "counted separately");
  useful        the gate had a complete manifest and no usable record (no record, a FAIL at the key, a newer
                non-pass record, an open miss): the run could change a decision;
  unclassified  no gate stamp (gate off, a run older than the gate), inputs unknown or the manifest unresolved --
                never counted as zero waste;
  skipped       not run (the gate reused the record): 0 minutes; its record's body time is `saved_min`.
  untimed       an executed chain with no phase_s (a run older than the chain timer): counted in its class with 0
                minutes and in `untimed_chains`, so an empty day of old runs does not read as "no work".
  WASTE = waste / (waste + budgeted + useful) minutes; unclassified share = unclassified / all executed minutes.
  targeted = purposes fix and guard; all-work = every purpose.

ALARMS (section 5):
  targeted_waste_6h   targeted WASTE above 20% over any 6 h window ending on a chain of the day, with at least 20
                      classified minutes in the window;
  all_waste_day       all-work WASTE above 25% for the day;
  unclassified_day    unclassified share above 30% for the day (the gate is blind: a manifest gap to fix);
  gate_miss           every miss (gate.audit_run: a would_skip chain whose fresh run FAILed or lost a PASS). A miss
                      found here in a run from another host is also appended to Transient/modcheck/gate_misses.jsonl
                      so this host's gate stops skipping that chain (gate.py clear-miss re-allows it).

ALSO: per-lane (host) busy minutes and utilisation, load overhead, minutes from request (the job id's UTC stamp) to
decision (the result's `finished`), gate counts and reuse hit rate.
"""
import argparse
import datetime
import json
import os
import re
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gate as G  # noqa: E402

DAY_TZ = "America/Los_Angeles"
TESTQ_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/testq"
TARGETED = G.GATED_PURPOSES
BUDGETED = G.ADVISORY_PURPOSES
THRESHOLDS = {"targeted_waste_6h": 0.20, "targeted_min_classified_min": 20.0, "all_waste_day": 0.25,
              "unclassified_day": 0.30, "window_h": 6}
CLASSES = ("waste", "budgeted", "useful", "unclassified")
STAMP = re.compile(r"^(\d{8}T\d{6}Z)$")
JOB_TS = re.compile(r"^J(\d{8}T\d{6}Z)-")


def _tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(DAY_TZ)
    except Exception:  # noqa: BLE001 - no tz database: say so in the file, fall back to UTC
        return datetime.timezone.utc


def _epoch_of_stamp(s):
    return datetime.datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()


def _epoch_of_iso(s):
    try:
        return datetime.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc).timestamp()
    except ValueError:
        return None


def day_bounds(day, tz=None):
    """(start, end) epoch seconds of the calendar `day` (a date) in the owner's time zone."""
    tz = tz or _tz()
    start = datetime.datetime(day.year, day.month, day.day, tzinfo=tz)
    nxt = day + datetime.timedelta(days=1)
    return start.timestamp(), datetime.datetime(nxt.year, nxt.month, nxt.day, tzinfo=tz).timestamp()


# ------------------------------------------------------------------------------------------------ loading
def _walk_json(root, skip=("metrics",)):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in skip and not x.startswith(".")]
        for f in files:
            if f.endswith(".json"):
                yield os.path.join(d, f)


def _load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def load_sources(sheet_dirs, testq_root):
    """({(mod, stamp): (path, run)}, [jobs], [results]) -- run = a modcheck sheet JSON."""
    runs, jobs, results = {}, [], []

    def take(p, d):
        if not isinstance(d, dict):
            return
        sch = d.get("schema")
        if sch == "testq.job/1":
            jobs.append(d)
        elif sch == "testq.result/1":
            results.append(d)
        elif isinstance(d.get("result"), dict) and d["result"].get("schema") == "testq.result/1":
            # testq's done/ (and cancelled/) record wraps the pair: {job: testq.job/1, result: testq.result/1, ...}
            take(p, d.get("job"))
            take(p, d["result"])
        elif isinstance(d.get("summary"), dict) and d.get("mod") and STAMP.match(str(d.get("stamp") or "")):
            runs.setdefault((d["mod"], d["stamp"]), (p, d))
    for sd in sheet_dirs:
        try:
            names = os.listdir(sd)
        except OSError:
            continue
        for n in names:
            if n.endswith(".json") and "_" in n:
                p = os.path.join(sd, n)
                take(p, _load(p))
    if testq_root and os.path.isdir(testq_root):
        for p in _walk_json(testq_root):
            take(p, _load(p))
    return runs, jobs, results


# ------------------------------------------------------------------------------------------------ classification
def chain_minutes(ch):
    ph = ch.get("phase_s") or {}
    return sum(float(v) for v in ph.values() if isinstance(v, (int, float))) / 60.0


def classify_chain(ch, purpose, offline):
    """(class, why) for one executed chain dict; class 'skipped' for a chain the gate reused."""
    g = ch.get("gate")
    if g and g.get("action") == G.SKIP:
        return "skipped", "reused %s" % ((g.get("record") or {}).get("file"))
    if ch.get("name") in offline:
        return "waste", "offline chain run in the live slot"
    if not g:
        return "unclassified", "no gate stamp"
    why = str(g.get("why") or "")
    if not g.get("key") or not g.get("inputs_known") or why.startswith("manifest"):
        return "unclassified", why[:120] or "manifest incomplete"
    if g.get("action") == G.WOULD:
        if purpose in BUDGETED:
            return "budgeted", "known good, purpose %s" % purpose
        return "waste", "known good at %s" % ((g.get("record") or {}).get("file"))
    return "useful", why[:120]


def chain_records(runs, host_default):
    """[{t, mod, run, chain, host, purpose, class, why, min, saved_min}] over every chain of every run; t is the
    chain's end (the run's sheet stamp minus the chains after it)."""
    out = []
    for (mod, stamp), (path, run) in sorted(runs.items()):
        s = run["summary"]
        end = _epoch_of_stamp(stamp)
        host = s.get("host") or host_default.get(os.path.dirname(os.path.abspath(path))) or "unknown"
        purpose = (s.get("gate") or {}).get("purpose") or "unknown"
        offline = set(s.get("offline_chains") or ())
        chains = s.get("chains") or []
        t = end
        recs = []
        for ch in reversed(chains):
            m = chain_minutes(ch)
            cls, why = classify_chain(ch, purpose, offline)
            g = ch.get("gate") or {}
            saved = float(((g.get("record") or {}).get("body_s")) or 0.0) / 60.0 if cls == "skipped" else 0.0
            recs.append({"t": t, "mod": mod, "run": os.path.basename(path), "chain": ch.get("name"), "host": host,
                         "purpose": purpose, "class": cls, "why": why, "min": 0.0 if cls == "skipped" else m,
                         "saved_min": saved, "action": g.get("action"),
                         "untimed": cls != "skipped" and not ch.get("phase_s")})
            t -= m * 60.0
        out += reversed(recs)
    return out


def tally(recs):
    t = {c: 0.0 for c in CLASSES}
    t["saved"] = 0.0
    untimed = 0
    for r in recs:
        untimed += bool(r.get("untimed"))
        if r["class"] in t:
            t[r["class"]] += r["min"]
        t["saved"] += r["saved_min"]
    classified = t["waste"] + t["budgeted"] + t["useful"]
    executed = classified + t["unclassified"]
    return {"minutes": {k: round(v, 1) for k, v in t.items()}, "classified_min": round(classified, 1),
            "executed_min": round(executed, 1), "untimed_chains": untimed,
            "waste": round(t["waste"] / classified, 3) if classified else None,
            "unclassified_share": round(t["unclassified"] / executed, 3) if executed else None}


def worst_window(recs, start, end, hours=6, min_classified=20.0):
    """The highest targeted WASTE over a `hours` window ending on any targeted chain inside [start, end) that has
    at least `min_classified` classified minutes: {waste, end, classified_min} or None."""
    tg = sorted((r for r in recs if r["purpose"] in TARGETED), key=lambda r: r["t"])
    best = None
    for r in tg:
        if not (start <= r["t"] < end):
            continue
        win = [x for x in tg if r["t"] - hours * 3600 < x["t"] <= r["t"]]
        tl = tally(win)
        if tl["classified_min"] >= min_classified and tl["waste"] is not None:
            if best is None or tl["waste"] > best["waste"]:
                best = {"waste": tl["waste"], "end": _iso(r["t"]), "classified_min": tl["classified_min"]}
    return best


def _iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))], 1)


# ------------------------------------------------------------------------------------------------ the day
def compute(day, sheet_dirs=None, testq_root=None, now=None, record=True):
    """The metrics dict for `day` (a date). `record`: append misses found in other hosts' runs to SHEET_DIR."""
    sheet_dirs = sheet_dirs if sheet_dirs is not None else G.history_dirs()
    testq_root = testq_root if testq_root is not None else os.environ.get("TESTQ_ROOT", TESTQ_DEFAULT)
    start, end = day_bounds(day)
    now = now if now is not None else datetime.datetime.now(datetime.timezone.utc).timestamp()
    runs, jobs, results = load_sources(sheet_dirs, testq_root)
    me = socket.gethostname()
    host_default = {os.path.abspath(G.SHEET_DIR): me}
    lookback = start - THRESHOLDS["window_h"] * 3600
    near = {k: v for k, v in runs.items() if lookback <= _epoch_of_stamp(k[1]) < end + 86400}
    recs = [r for r in chain_records(near, host_default) if r["t"] < end]
    today = [r for r in recs if r["t"] >= start]
    targeted = [r for r in today if r["purpose"] in TARGETED]

    # misses: every would_skip chain of the day's runs against its record
    misses = []
    for (mod, stamp), (path, run) in sorted(near.items()):
        if not (start <= _epoch_of_stamp(stamp) < end):
            continue
        dirs = [os.path.dirname(os.path.abspath(path))] + [d for d in G.history_dirs() if d not in sheet_dirs] + \
            list(sheet_dirs)
        au = G.audit_run(run, dirs=dirs)
        misses += [{"mod": mod, "run": os.path.basename(path), "detail": m} for m in au["misses"]]
        if record and au["misses"] and os.path.abspath(os.path.dirname(path)) != os.path.abspath(G.SHEET_DIR):
            G.record_misses(mod, run["summary"], path, dirs=dirs, base=G.SHEET_DIR)

    # lanes: testq results give wall time and load overhead; local sheets no result names add their chain minutes
    linked = set()
    lanes = {}
    waits = []
    job_ts = {}
    for j in jobs:
        m = JOB_TS.match(str(j.get("id") or ""))
        if m:
            job_ts[j["id"]] = _epoch_of_stamp(m.group(1))
    last = {}
    for r in results:
        k = r.get("job")
        if k and (k not in last or str(r.get("finished")) > str(last[k].get("finished"))):
            last[k] = r
    for r in results:
        for a in r.get("artifacts") or []:
            linked.add(os.path.basename(str(a.get("path") or a.get("name") or "")))
        st, fi = _epoch_of_iso(r.get("started")), _epoch_of_iso(r.get("finished"))
        if st is None or fi is None:
            continue
        a, b = max(st, start), min(fi, end)
        lane = lanes.setdefault(r.get("host") or "unknown", {"busy_min": 0.0, "load_overhead_min": 0.0,
                                                             "attempts": 0, "invalid_attempts": 0})
        if b > a:
            lane["busy_min"] += (b - a) / 60.0
        if start <= fi < end:
            lane["attempts"] += 1
            lane["invalid_attempts"] += r.get("outcome") in ("INVALID", "INTERRUPTED")
            lane["load_overhead_min"] += sum(float(v) for k2, v in (r.get("phase_s") or {}).items()
                                             if k2 != "run" and isinstance(v, (int, float))) / 60.0
    for k, r in last.items():
        fi = _epoch_of_iso(r.get("finished"))
        m = JOB_TS.match(str(k))
        req = job_ts.get(k) or (_epoch_of_stamp(m.group(1)) if m else None)
        if fi is not None and req is not None and start <= fi < end and r.get("outcome") != "REFUSED":
            waits.append((fi - req) / 60.0)
    for r in today:
        if r["run"] in linked:
            continue
        lane = lanes.setdefault(r["host"], {"busy_min": 0.0, "load_overhead_min": 0.0, "attempts": 0,
                                            "invalid_attempts": 0})
        lane["busy_min"] += r["min"]
    span = max(1.0, (min(end, now) - start) / 60.0)
    for v in lanes.values():
        v["busy_min"] = round(v["busy_min"], 1)
        v["load_overhead_min"] = round(v["load_overhead_min"], 1)
        v["utilisation"] = round(min(1.0, v["busy_min"] / span), 3)

    acted = [r for r in today if r["action"] in (G.RUN, G.SKIP, G.WOULD)]
    skipped = [r for r in today if r["class"] == "skipped"]
    out = {
        "schema": "modcheck.metrics/1", "day": day.isoformat(), "tz": DAY_TZ if _tz() is not datetime.timezone.utc
        else "UTC", "generated": _iso(now), "host": me, "thresholds": THRESHOLDS,
        "runs": sorted({r["run"] for r in today}),
        "all_work": tally(today), "targeted": tally(targeted),
        "by_purpose": {p: tally([r for r in today if r["purpose"] == p]) for p in sorted({r["purpose"] for r in today})},
        "by_lane": {h: dict(tally([r for r in today if r["host"] == h]), **lanes.get(h, {}))
                    for h in sorted({r["host"] for r in today} | set(lanes))},
        "targeted_worst_6h": worst_window(recs, start, end, THRESHOLDS["window_h"],
                                          THRESHOLDS["targeted_min_classified_min"]),
        "request_to_decision_min": {"n": len(waits), "p50": _pct(waits, 0.5), "p90": _pct(waits, 0.9),
                                    "max": round(max(waits), 1) if waits else None},
        "gate": {"decided": len(acted), "skipped": len(skipped),
                 "would_skip": sum(1 for r in today if r["action"] == G.WOULD),
                 "reuse_hit_rate": round(len(skipped) / len(acted), 3) if acted else None,
                 "saved_min": round(sum(r["saved_min"] for r in today), 1),
                 "open_misses": ["%s/%s" % k for k in sorted(G.open_misses(G.history_dirs()))]},
        "gate_misses": misses,
        "unclassified_top": _top([r for r in today if r["class"] == "unclassified"]),
        "waste_top": _top([r for r in today if r["class"] == "waste"]),
    }
    out["alarms"] = alarms(out)
    return out


def _top(recs, n=8):
    by = {}
    for r in recs:
        k = (r["chain"], r["why"])
        by[k] = by.get(k, 0.0) + r["min"]
    return [{"chain": c, "why": w, "min": round(m, 1)} for (c, w), m in sorted(by.items(), key=lambda kv: -kv[1])[:n]]


def alarms(m):
    th = m["thresholds"]
    out = []
    w = m.get("targeted_worst_6h")
    if w and w["waste"] > th["targeted_waste_6h"]:
        out.append({"kind": "targeted_waste_6h", "value": w["waste"], "threshold": th["targeted_waste_6h"],
                    "detail": "6 h window ending %s, %.1f classified min" % (w["end"], w["classified_min"])})
    aw = m["all_work"]["waste"]
    if aw is not None and aw > th["all_waste_day"]:
        out.append({"kind": "all_waste_day", "value": aw, "threshold": th["all_waste_day"],
                    "detail": "%.1f of %.1f classified min" % (m["all_work"]["minutes"]["waste"],
                                                               m["all_work"]["classified_min"])})
    us = m["all_work"]["unclassified_share"]
    if us is not None and us > th["unclassified_day"]:
        out.append({"kind": "unclassified_day", "value": us, "threshold": th["unclassified_day"],
                    "detail": "%.1f of %.1f executed min: the gate cannot see these chains" % (
                        m["all_work"]["minutes"]["unclassified"], m["all_work"]["executed_min"])})
    for x in m["gate_misses"]:
        out.append({"kind": "gate_miss", "value": 1, "threshold": 0, "detail": "%s %s" % (x["run"], x["detail"])})
    return out


def write(m, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "%s.json" % m["day"])
    tmp = "%s.tmp.%d" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1, sort_keys=True)
    os.replace(tmp, p)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--day", default=None, help="YYYY-MM-DD in %s (default: today there)" % DAY_TZ)
    ap.add_argument("--out", default=None, help="folder (default <TESTQ_ROOT>/metrics)")
    ap.add_argument("--testq", default=None, help="testq root (default TESTQ_ROOT or %s)" % TESTQ_DEFAULT)
    ap.add_argument("--sheets", action="append", default=None, help="modcheck sheet folder (repeatable; default "
                                                                    "Transient/modcheck + MODCHECK_GATE_HISTORY)")
    ap.add_argument("--no-record", action="store_true", help="do not append misses found to gate_misses.jsonl")
    ap.add_argument("--print", action="store_true", help="print the JSON instead of the summary lines")
    a = ap.parse_args(argv)
    day = (datetime.date.fromisoformat(a.day) if a.day
           else datetime.datetime.now(_tz()).date())
    testq = a.testq or os.environ.get("TESTQ_ROOT", TESTQ_DEFAULT)
    m = compute(day, sheet_dirs=a.sheets, testq_root=testq, record=not a.no_record)
    p = write(m, a.out or os.path.join(testq, "metrics"))
    if a.print:
        print(json.dumps(m, indent=1, sort_keys=True))
        return 0
    aw, tg = m["all_work"], m["targeted"]

    def pc(x):
        return "-" if x is None else "%.0f%%" % (100 * x)
    print("%s  %s: %d runs, %.1f executed min; WASTE all %s targeted %s; unclassified %s; skipped %d (saved %.1f "
          "min); misses %d" % (p, m["day"], len(m["runs"]), aw["executed_min"], pc(aw["waste"]), pc(tg["waste"]),
                               pc(aw["unclassified_share"]), m["gate"]["skipped"], m["gate"]["saved_min"],
                               len(m["gate_misses"])))
    if aw["untimed_chains"]:
        print("  %d executed chains carry no phase_s (a run older than the chain timer): their minutes are unknown, "
              "not zero" % aw["untimed_chains"])
    for h, v in m["by_lane"].items():
        print("  lane %-16s busy %6.1f min  util %s  WASTE %s" % (h, v.get("busy_min", 0.0),
                                                               pc(v.get("utilisation")), pc(v.get("waste"))))
    for x in m["alarms"]:
        print("  ALARM %s %s (> %s): %s" % (x["kind"], x["value"], x["threshold"], x["detail"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
