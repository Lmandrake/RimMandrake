#!/usr/bin/env python3
"""streams.py — the Level 1 stream collector (its RimPulse Streams panel went 2026-11-18 with the dashboard).

Design: design/RimMandrake/work_allocation_framework_2026-10-26.md §3 (measures), §4.1 (Level 1), §5 (when the
owner is the bottleneck), §7 (the panel). Items STREAM_METRICS_UNIFY_ONE_SERIES, MODCHECK_METRICS_RETIRE_INTO_HOURLY,
RIMPULSE_STREAMS_BUILD_VS_TIME.

    streams.py collect [--no-write] [--print]   one record -> streams/series.jsonl (the rm-streams-collect timer, 15 min)
    streams.py backfill --days 7                 hourly records for past hours, ledger + testq measures only
    streams.py show                              the latest record, as text

One record per run holds every §3 measure as MEASURED (with its value and AS OF time) or UNMEASURED (with the reason),
never a 0 standing in for "could not see". It folds rimflow_metrics.py (ledger flow), testing_metrics.py (SteveDesktop
lane; that collector's own history is still written by the same timer) and modcheck/metrics.py (the WASTE split
whose daily file was never scheduled: item 2 retires that file into this series). The badges and the "where you're
needed" lists are computed HERE, so the panel only draws what the record says (§7: "the panel computes nothing").

A rule never fires on an UNMEASURED input (§4.1): such a row's badge is "build the instrument", never a call on him.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck"), os.path.join(UTILS, "art")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import testing_metrics as TM  # noqa: E402  (imports modcheck/metrics.py as MX)
import ops_ledger as pc  # noqa: E402
import rimflow_metrics as RFM  # noqa: E402

MX = TM.MX
SCHEMA = "rm.streams/1"
DIR = Path(os.environ.get("RM_STREAMS_DIR", "/mnt/d/ClaudeWork/rimmandrake/streams"))
BENCH = Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))   # the data clone (the deploy is sparse)
NIGHTLY = BENCH / "Transient" / "selftests_nightly.last"
ART_OUT = BENCH / "Transient" / "biome_ffar"

STEWARD_STALE_S = 5 * 60   # §6.1: steward.json older than this is STALE_HEARTBEAT, so G1 cannot be read from it
DAY = 86400.0
HOUR = 3600.0
FILLER = "BENCH.filler"    # testq.py: a filler job's requested_by
STEVE_LANES = (None, "stevedesktop")
WINDOWS = {"G2": 2 * HOUR, "G3": 6 * HOUR, "G6": DAY, "P3": 7 * DAY, "A2": DAY, "A3": DAY, "A5": 7 * DAY}
NO_REBUILD = "not reconstructable for a past hour"


# ---------------------------------------------------------------------------------------------- value marks
def iso(t):
    return TM.iso(t) if t else None


def M(v, asof, **x):
    """A measured value. `asof`: when the thing it reads was last true (a file's mtime, the ledger's last event)."""
    out = {"v": v, "m": "MEASURED", "asof": iso(asof) if isinstance(asof, (int, float)) else asof}
    if x:
        out["x"] = x
    return out


def U(why, **x):
    out = {"v": None, "m": "UNMEASURED", "why": why}
    if x:
        out["x"] = x
    return out


def guard(fn, ids, *a):
    """Run one instrument group; a crash makes its measures UNMEASURED with the error, never kills the record."""
    try:
        return fn(*a)
    except Exception as e:  # noqa: BLE001 - one blind instrument must not blank the other five streams
        why = f"{fn.__name__} crashed: {type(e).__name__}: {str(e)[:160]}"
        return {k: U(why) for k in ids}


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def _read_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _days(t, now):
    return round((now - t) / DAY, 2) if t else None


# ---------------------------------------------------------------------------------------------- ledger (D, V, P, W)
def ledger_measures(events, now, world=None, tl=None):
    """D1-D4, V0, P1-P4, W1 from the rimflow ledger as it stood at `now` (events already cut at `now`)."""
    asof = RFM.model.epoch(events[-1]["ts"]) if events else None
    r = RFM.compute(events, now=now, window_days=1, mods={}, heat=None)
    if world is None:
        world, tl = RFM.timelines(events)
    out = {}
    ow = r.get("owner_wait_open") or {}
    out["D1"] = M(ow.get("over_3d"), asof, n=ow.get("n"), median_d=ow.get("median_d"), oldest_d=ow.get("max_d"),
                  unit="waits over 3 d")
    rs = r.get("owner_wait_resolved") or {}
    if not rs.get("n"):
        out["D2"] = U("reads 0 resolved in the last day: a suspect zero (resolutions made without a `needs` change "
                      "are missed); probe owed, OWNER_WAIT_RESOLVED_PROBE_ZERO_READING")
    else:
        out["D2"] = M(round(rs["p90_d"] * 24, 1) if rs.get("p90_d") is not None else None, asof, n=rs["n"],
                      p50_h=round((rs.get("median_d") or 0) * 24, 1), unit="h p90")
    items = world.items
    design_open = [i for i, it in items.items() if it.open and (it.kind or "").lower() == "design"
                   and str(it.target or "").lower() == "v1"]
    des = (r.get("lead_by_kind") or {}).get("design") or {}
    waiting_design = sum(1 for i in design_open if items[i].needs == "owner")
    out["D3"] = M(len(design_open), asof, closes_1d=des.get("n", 0), waiting_on_you=waiting_design, unit="open v1 design")
    bl = r.get("blocked") or {}
    top = (bl.get("top_blockers") or [[None, 0]])[0]
    bit = items.get(top[0]) if top[0] else None
    out["D4"] = M(top[1], asof, blocker=top[0], blocked=bl.get("n"), needs_you=bool(bit and bit.open and bit.needs == "owner"),
                  unit="held by the top blocker")
    vb = r.get("verify_backlog") or {}
    out["V0"] = M(vb.get("n"), asof, median_d=vb.get("median_d"), owed=vb.get("owed_levels"), unit="built, not verified")
    out["P1"] = M((r.get("cycle") or {}).get("n"), asof, unit="closed after start, 1 d",
                  bookkeeping=(r.get("done_never_started") or {}).get("n") if isinstance(r.get("done_never_started"), dict)
                  else r.get("done_never_started"))
    wip = (r.get("wip") or {}).get("doing") or {}
    out["P2"] = M((r.get("leases") or {}).get("open_items_lapsed_now"), asof, doing=wip.get("n"),
                  doing_over_7d=wip.get("over_7d"), unit="lapsed leases")
    lo = now - WINDOWS["P3"]
    to_owner = started = 0
    for rows in tl.values():
        for prev, row in zip(rows[:-1], rows[1:]):
            if row[0] < lo or row[0] > now:
                continue
            if row[2] == "owner" and prev[2] != "owner":
                to_owner += 1
            if row[1] == "doing" and prev[1] != "doing":
                started += 1
    out["P3"] = (M(round(100.0 * to_owner / started, 1), asof, to_owner=to_owner, started=started, unit="per 100 started, 7 d")
                 if started else U("no item started in the last 7 d"))
    rw = r.get("rework") or {}
    out["P4"] = M(rw.get("cause_already_done"), asof, filed=rw.get("filed"), unit="filed against closed work, 1 d",
                  share_pct=TM.pct(rw.get("cause_already_done") or 0, rw.get("filed") or 0))
    walks = sorted(i for i, it in items.items() if it.open and it.needs == "owner" and not it.blocked
                   and re.search(pc._WALK_RE, f"{it.title or ''}", re.I))
    out["W1"] = M(len(walks), asof, items=walks[:12], unit="walks owed",
                  note="title match for walk / in-game words: a weak instrument")
    out["W2"] = U("no record of a staged walk exists; OWNER_WALK_MEASURE_STAGED_AND_DONE")
    out["W3"] = U("no ledger event marks a walk (ranBy holds only BENCH and FOUNDRY); OWNER_WALK_MEASURE_STAGED_AND_DONE")
    out["W4"] = U("walk findings are not joined to the criteria ledger yet; OWNER_WALK_MEASURE_STAGED_AND_DONE")
    return out


def asks_now(events, now):
    """Open asks of him right now (Pulse's own ask list): remote = rule/look/provide, in person = hands + walk."""
    rem, inp = [], []
    for iid, a in pc.owner_rulings(events).items():
        if a.get("answered"):
            continue
        row = {"id": iid, "label": pc.ask_label(iid, a.get("reason") or ""), "class": a["class"],
               "age_d": _days(a.get("t"), now), "link": f"/item/{iid}"}
        (inp if a["class"] in ("hands", "walk") else rem).append(row)
    key = lambda r: -(r["age_d"] or 0)  # noqa: E731
    return sorted(rem, key=key), sorted(inp, key=key)

# ---------------------------------------------------------------------------------------------- offline (O)
_TEST_LINE = re.compile(r"^(FAIL|CRASH|UNMEASURED)\s+[\d.]+s\s+(\S+)")
_SUMMARY = re.compile(r"^PASS (\d+)/(\d+)\s+FAIL (\d+)/\d+\s+UNMEASURED (\d+)/\d+\s+CRASH (\d+)/\d+")


def nightly(path=None):
    """Transient/selftests_nightly.last -> {verdict, pass, total, fail, crash, unmeasured, reds: [paths], at}."""
    path = Path(path or NIGHTLY)
    at = _mtime(path)
    if at is None:
        return {"why": f"{path} not found"}
    out = {"at": at, "reds": [], "verdict": None}
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = _TEST_LINE.match(ln)
            if m and m.group(1) in ("FAIL", "CRASH"):
                out["reds"].append(m.group(2))
            m = _SUMMARY.match(ln)
            if m:
                out.update(passed=int(m.group(1)), total=int(m.group(2)), fail=int(m.group(3)),
                           unmeasured=int(m.group(4)), crash=int(m.group(5)))
            if ln.startswith("RESULT:"):
                out["verdict"] = ln.split()[1] if len(ln.split()) > 1 else None
    if out.get("total") is None or not out["verdict"]:
        out["why"] = f"{path}: no summary or RESULT line (a run in progress or a changed format)"
    return out


def offline_measures(events, world, now, ny=None, crs=None, mx=None):
    ny = ny if ny is not None else nightly()
    out = {}
    if ny.get("why"):
        out["O1"] = out["O2"] = U(ny["why"])
    else:
        reds = ny["fail"] + ny["crash"]
        out["O1"] = M(reds, ny["at"], verdict=ny["verdict"], passed=ny["passed"], total=ny["total"], fail=ny["fail"],
                      crash=ny["crash"], unmeasured=ny["unmeasured"], unit="FAIL + CRASH")
        text = {}
        for e in events:
            iid = e.get("id")
            it = world.items.get(iid) if iid else None
            if it is not None and it.open:
                text.setdefault(iid, [iid, it.title or ""]).append(str(e.get("reason") or e.get("text") or e.get("note") or ""))
        blob = "\n".join(" ".join(v) for v in text.values()).lower()
        unowned = [p for p in ny["reds"] if os.path.basename(p).lower().replace(".py", "") not in blob]
        out["O2"] = M(len(unowned), ny["at"], tests=unowned[:30], of=len(ny["reds"]), unit="reds no open item names",
                      note="an open item names the test when its file name (no .py) is in its id, title or event text")
    crs = crs if crs is not None else code_review_dirty()
    out["O3"] = crs
    mx = mx if mx is not None else modcheck_today(now)
    out["O4"] = mx.get("O4") or U("modcheck metrics unavailable")
    return out


def code_review_dirty():
    try:
        p = subprocess.run([sys.executable, str(BENCH / "src/RimMandrake/Utils/code_review_status.py"), "list"],
                           cwd=str(BENCH), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return U(f"code_review_status.py list failed: {e}")
    m = re.search(r"TALLY\s+CLEAN (\d+)\s+DIRTY (\d+)", p.stdout or "")
    if not m:
        return U("code_review_status.py list printed no TALLY line")
    return M(int(m.group(2)), time.time(), clean=int(m.group(1)), unit="DIRTY files",
             note="recorded entries only; files never entered are not counted")


def modcheck_today(now):
    """Item 2: the modcheck WASTE split for his day so far, folded into this series (the daily file is retired).
    record=False: the deploy's SHEET_DIR is empty, and this collector never writes gate misses."""
    day = datetime.datetime.fromtimestamp(now, MX._tz()).date()
    m = MX.compute(day, TM.SHEET_DIRS, TM.TESTQ_ROOT, now, record=False)
    aw = m.get("all_work") or {}
    off = sum(w["min"] for w in m.get("waste_top") or [] if w.get("why") == "offline chain run in the live slot")
    ex = aw.get("executed_min") or 0
    fold = {"day": m.get("day"), "all_work": aw, "targeted": m.get("targeted"), "targeted_worst_6h": m.get("targeted_worst_6h"),
            "by_lane": {h: {k: v.get(k) for k in ("waste", "executed_min", "classified_min", "busy_min", "util")}
                        for h, v in (m.get("by_lane") or {}).items()},
            "alarms": m.get("alarms"), "waste_top": m.get("waste_top"), "gate": {k: (m.get("gate") or {}).get(k) for k in
                                                                                ("decided", "skipped", "saved_min")}}
    o4 = (M(round(100.0 * off / ex, 1), now, offline_min=round(off, 1), executed_min=round(ex, 1), unit="% of live minutes")
          if ex >= 1 else U(f"only {ex:.1f} classified live minutes today (testq chains carry no gate stamp yet)"))
    return {"fold": fold, "O4": o4}


# ---------------------------------------------------------------------------------------------- art (A)
def _art_events(clones=(BENCH,)):
    """The art ledger, each seat's shard from its own clone (freshest there)."""
    out = []
    for c in clones:
        seat = "BENCH"
        p = c / "infrastructure/state/art/events" / f"{seat}.jsonl"
        try:
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    try:
                        e = json.loads(ln)
                    except ValueError:
                        continue
                    t = TM.epoch(e.get("ts") or e.get("at"))
                    if t is None and e.get("date"):
                        t = TM.epoch(e["date"] + "T12:00:00+00:00")
                    if t is not None and isinstance(e, dict):
                        out.append((t, e.get("type"), e.get("by")))
        except OSError:
            continue
    return out


def art_rates(now, evs=None):
    evs = evs if evs is not None else _art_events()
    if not evs:
        return {k: U("art ledger not readable") for k in ("A2", "A3", "A5")}
    asof = max(t for t, *_ in evs if t <= now) if any(t <= now for t, *_ in evs) else None

    def n(kind, win, by=None):
        return sum(1 for t, ty, b in evs if ty == kind and now - win <= t <= now and (by is None or b == by))
    v1, v7 = n("variant", DAY), n("variant", 7 * DAY)
    out = {"A2": M(v1, asof, d7=v7, unit="variants, 1 d"),
           "A3": M(n("ruling", DAY, "owner"), asof, d7=n("ruling", 7 * DAY, "owner"), unit="your rulings, 1 d")}
    bad = n("purge", 7 * DAY) + n("rejected", 7 * DAY)
    out["A5"] = M(TM.pct(bad, v7), asof, purged_rejected=bad, variants=v7, unit="% purged or rejected, 7 d") if v7 else \
        U("no variants in the last 7 d")
    return out


def art_queue(now):
    """A1: the rows awaiting his pick (art.py review awaiting-pick), read from the BENCH clone's sheets."""
    os.environ.setdefault("ART_LEDGER_DIR", str(BENCH / "infrastructure/state/art"))
    import review_queue as RQ
    q = RQ.awaiting(out=ART_OUT, ledger=True)
    dates = []
    for base, k in (q.get("per_sheet") or {}).items():
        m = re.search(r"_(\d{4}-\d{2}-\d{2})$", base)
        if k and m:
            dates.append((m.group(1), base))
    oldest = min(dates) if dates else None
    od = _days(TM.epoch(oldest[0] + "T00:00:00+00:00"), now) if oldest else None
    rows = len(q.get("rows") or [])
    top = sorted(((k, b) for b, k in (q.get("per_sheet") or {}).items() if k), reverse=True)[:5]
    return {"A1": M(rows, now, sheets=len(q.get("per_sheet") or {}), open_sheets=q.get("sheets"),
                    top_sheets=[{"sheet": b, "rows": k} for k, b in top],
                    oldest_sheet=oldest[1] if oldest else None, oldest_d=od, unit="rows awaiting your pick"),
            "A4": U("no join of agent verdicts to your rulings; ART_OVERRIDE_MEASURE_AGENT_VS_OWNER")}


# ---------------------------------------------------------------------------------------------- live (G)
def _spans(atts, running, lo, hi, now, keep=lambda a: True):
    sp = [(a["started"], a["finished"]) for a in atts if a["started"] and a["finished"] and keep(a)]
    sp += [(r["sent"], now) for r in running if r.get("sent") and keep({"requested_by": r["job"].get("requested_by")})]
    return TM.union(TM.clip(sp, lo, hi))


def steward_now(now, root=None):
    """testq/steward.json (§6.2), if the steward exists and is writing."""
    p = os.path.join(root or TM.TESTQ_ROOT, "steward.json")
    d, t = _read_json(p), _mtime(p)
    if not isinstance(d, dict):
        return None, "steward not built yet (no testq/steward.json); STEVE_STEWARD_BUILD_NO_LLM_OWNER"
    if now - (t or 0) > STEWARD_STALE_S:
        return None, f"steward.json is {round((now - t) / 60)} min old: STALE_HEARTBEAT, its counts cannot be read"
    return dict(d, _mtime=t), None


def steward_unowned_min(st):
    """Unowned minutes from steward.json: top-level unowned_min / unowned_minutes (§6.2's words), or the open
    incident's unowned_s (what the steward writes); no open incident and no fault means 0 unowned."""
    for k in ("unowned_min", "unowned_minutes"):
        if isinstance(st.get(k), (int, float)):
            return st[k]
    inc = st.get("incident")
    if isinstance(inc, dict) and isinstance(inc.get("unowned_s"), (int, float)):
        return round(inc["unowned_s"] / 60, 1)
    if st.get("fault") is False:
        return 0
    return None


def steve_state(src, now):
    lv = TM.steve_live(src, now)
    st, why = steward_now(now, src.get("root"))
    if st and st.get("state"):
        return st["state"], "steward: " + _short(st.get("reason") or "no reason given", 200)
    if not lv["ok"]:
        return "UNKNOWN", src.get("why")
    if lv["ssh_down_since"]:
        return "DOWN", f"ssh down since {iso(lv['ssh_down_since'])}"
    if lv["paused"]:
        return "PAUSED", str((lv["paused"] or {}).get("outcome") or "paused")
    if lv["running"]:
        return "RUNNING", "a job is running"
    return ("IDLE_WAITING" if lv["pending"] else "IDLE"), f"{lv['pending']} pending"


def live_measures(src, ledger, now, harness_mods=None):
    """G1-G8 from testq records as they stood at `now`."""
    out = {}
    if src.get("why") or not src.get("commissioned") or src["commissioned"] >= now:
        why = src.get("why") or "SteveDesktop not commissioned yet (no testq job before this time)"
        return {k: U(why) for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")}
    asof = max([a["finished"] for a in src["attempts"] if a["finished"]] or [src["commissioned"]])
    atts = [a for a in src["attempts"] if a.get("lane") in STEVE_LANES and a["finished"] and a["finished"] <= now]
    running = [r for r in src["running"] if (r["job"].get("lane") in STEVE_LANES)]
    st, why = steward_now(now, src.get("root"))
    if st is not None:
        um = steward_unowned_min(st)
        out["G1"] = M(um, st["_mtime"], state=st.get("state"), since=st.get("since"), fault=st.get("fault"),
                      unit="min unowned idle") if isinstance(um, (int, float)) else \
            U("steward.json carries no unowned minutes (unowned_min, unowned_minutes or incident.unowned_s)")
    else:
        lv = TM.steve_live(src, now)
        idle = round((now - lv["idle_since"]) / 60) if lv["idle_since"] and not lv["running"] else 0
        out["G1"] = U(why, idle_min=idle, note="idle minutes, not unowned minutes: the steward decides ownership")
    lo = max(now - WINDOWS["G2"], src["commissioned"])
    win = now - lo
    tot = TM.length(_spans(atts, running, lo, now, now))
    use = TM.length(_spans(atts, running, lo, now, now, keep=lambda a: a.get("requested_by") != FILLER))
    out["G2"] = M(TM.pct(tot, win), now, useful_pct=TM.pct(use, win), filler_pct=TM.pct(tot - use, win),
                  window_h=round(win / HOUR, 2), unit="% busy, 2 h") if win > 600 else U("lane commissioned under 10 min ago")
    six = [a for a in atts if now - WINDOWS["G3"] <= a["finished"] <= now]
    out["G3"] = M(TM.pct(sum(1 for a in six if a["outcome"] == "INVALID"), len(six)), asof, attempts=len(six),
                  unit="% INVALID, 6 h") if six else U("no attempt finished in the last 6 h")
    last = {}
    for a in sorted(atts, key=lambda a: a["finished"]):
        if a["outcome"] == "DONE":
            last[a["sel"]] = a
    gaps = Counter(r.get("verdict") for a in last.values() for r in a["rows"] if r.get("verdict") in ("UNMEASURED", "NOT_RUN"))
    out["G4"] = M(sum(gaps.values()), asof, unmeasured=gaps["UNMEASURED"], not_run=gaps["NOT_RUN"], selections=len(last),
                  unit="gap rows at the latest DONE run per selection",
                  note="latest run per (mod, selector), not per identity; items owing a live level not joined yet")
    wired = sorted({a["mod"] for a in atts if a["outcome"] == "DONE" and a["mod"] and now - a["finished"] <= 14 * DAY})
    hm = harness_mods if harness_mods is not None else count_harness_mods()
    out["G5"] = M(len(wired), asof, of=hm, mods=wired, unit="mods testq ran (DONE) in 14 d",
                  note="proxy for 'chains testq can select': no per-mod bad_selection probe yet; of = mods with a validation.py")
    d = TM.steve_day(src, ledger, now - WINDOWS["G6"], now, now)
    bh = (d["busy_pct"]["v"] or 0) / 100.0 * (d["window_h"]["v"] or 0) if d.get("busy_pct", {}).get("v") is not None else 0
    if bh >= 0.5:
        f, c = d["findings"]["v"] or 0, d["closed_after_pass"]["v"] or 0
        out["G6"] = M(round((f + c) / bh, 2), asof, findings=f, closes=c, busy_h=round(bh, 2), unit="per busy hour, 24 h")
    else:
        out["G6"] = U("under 30 busy minutes in the last 24 h")
    out["G7"] = M(d["waste_pct"]["v"], asof, why=d.get("waste_why"), unit="% wasted attempts, 24 h") \
        if d.get("waste_pct", {}).get("m") == "MEASURED" else U((d.get("waste_pct") or {}).get("why") or "no attempts")
    out["G8"] = U("no allocator yet measures useful-queue demand over capacity; SLOT_ALLOCATOR_BUILD_RULES_FILE")
    return out


def count_harness_mods():
    return len({os.path.dirname(p) for p in glob.glob(str(BENCH / "src/*/*/validation.py"))})


def archmagi(now, br=None, game=None, src=None):
    """G9 bridge busy over 24 h, and Archmagi's state now: DOWN / UP / DRIVING (an agent called the bridge in the
    last 15 min) / BATCH (a testq Archmagi-lane job is running)."""
    br = br if br is not None else TM.load_bridge()
    out = {}
    if br.get("why"):
        out["G9"] = U(br["why"])
        last = None
    else:
        lo = max(now - DAY, br.get("coverage_start") or now - DAY)
        sp = TM.union(TM.clip(br["spans"], lo, now))
        last = max([e for s, e in br["spans"] if e <= now] or [0]) or None
        out["G9"] = M(TM.pct(TM.length(sp), now - lo), last, window_h=round((now - lo) / HOUR, 1),
                      longest_idle_min=round(max([e - s for s, e in TM.gaps(sp, lo, now)] or [0]) / 60, 1),
                      unit="% bridge held, 24 h", note="'game UP and undriven while bridge items are ready' is not measured")
    state, why, as_of = game_reading(game if game is not None else probe_game(), last, now, src)
    return out, {"state": state, "why": why, "last_bridge_call": iso(last), "as_of": as_of}


def probe_game():
    """The live game reading: rimflow.probe.measure() (process and bridge port), never a file a daemon wrote once."""
    rf = os.path.join(os.path.dirname(UTILS), "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import probe
    return probe.measure()


def game_reading(g, last=None, now=None, src=None):
    """probe reading -> (state, why, as_of). A probe that could not look is UNKNOWN with its evidence, never DOWN."""
    as_of = iso(g["at"]) if g.get("at") else None
    why = str(g.get("evidence") or "no evidence")
    state = g.get("implies")
    if state not in ("UP", "DOWN", "LOADING"):
        return "UNKNOWN", why, as_of
    if state == "UP":
        if last and now and now - last <= 15 * 60:
            state = "DRIVING"
        if src and any((r["job"].get("lane") or "").lower() == "archmagi" for r in src.get("running") or []):
            state = "BATCH"
    return state, why, as_of


def budget(now, acc=None):
    """The lowest week LEFT among the accounts account_usage measured, with the reading's time."""
    if acc is None:
        import account_usage
        acc = account_usage.read_now(now)["accounts"]
    rows = [{"name": n, "pct_left": a.get("week_pct_left"), "hours_to_reset": a.get("hours_to_week_reset"), "asof": a.get("measured_at"),
             "stale": bool(a.get("stale"))} for n, a in sorted(acc.items())]
    known = [r for r in rows if r["pct_left"] is not None and r["asof"]]
    if not known:
        return U("no account has a week reading (account_usage latest.json absent or all unmeasured)")
    worst = min(known, key=lambda r: r["pct_left"])
    return M(worst["pct_left"], TM.epoch(worst["asof"]), accounts=rows, unit="% of the week LEFT (lowest account)")

# ---------------------------------------------------------------------------------------------- badges + needs
STREAMS = (   # key, title, lead measure, how the lead reads, good band (lo, hi) or None
    ("art", "Art", "A1", "rows awaiting your pick", (0, 30)),
    ("design", "Design + you", "D1", "waits over 3 d", (0, 0)),
    ("dev", "Development", "V0", "built, not verified", None),
    ("offline", "Offline validation", "O1", "nightly FAIL + CRASH", (0, 0)),
    ("live", "Live validation (SteveDesktop)", "G2", "% busy, 2 h", (70, 100)),
    ("walk", "Your live walk", "W1", "walks owed", None),
)

NAMES = {"A1": "Pick queue", "A2": "Generation rate", "A3": "Your ruling rate", "A4": "Override rate", "A5": "Purge share",
         "D1": "Waiting on you", "D2": "Answer latency", "D3": "Design in flight", "D4": "Blocker fan-in",
         "V0": "Built, not verified", "P1": "Real throughput", "P2": "Stale work in progress", "P3": "Clarification rate",
         "P4": "Rework", "O1": "Nightly verdict", "O2": "Unowned reds", "O3": "Dirty backlog", "O4": "Offline-in-live share",
         "G1": "Unowned idle", "G2": "Useful busy", "G3": "Harness health", "G4": "Evidence gaps", "G5": "Coverage",
         "G6": "Yield", "G7": "WASTE", "G8": "Two-machine test", "G9": "Archmagi agent use", "W1": "Walks owed",
         "W2": "Walk readiness", "W3": "Last walk age", "W4": "Walk yield", "B": "Token budget"}


def _v(m, key=None):
    if not m or m.get("m") != "MEASURED":
        return None
    return m.get("v") if key is None else (m.get("x") or {}).get(key)


def needs_and_badges(ms, rem, inp, steve, now):
    """§5: the remote and in-person signals, and each stream's whose-move badge. No rule fires on UNMEASURED."""
    remote, person = [], []
    a1 = ms.get("A1")
    if _v(a1) is not None and (_v(a1) > 30 or (_v(a1, "oldest_d") or 0) > 7):
        remote.append({"signal": "Pick queue", "text": f"{_v(a1)} art rows wait on your pick; oldest sheet "
                       f"{_v(a1, 'oldest_d'):.0f} d ({_v(a1, 'oldest_sheet')})", "rule": "A1 above 30 rows or a sheet older than 7 d",
                       "items": [{"id": t["sheet"], "label": f"{t['sheet']}: {t['rows']} rows"} for t in _v(a1, "top_sheets") or []]})
    d1 = ms.get("D1")
    if _v(d1):
        remote.append({"signal": "Waiting on you", "text": f"{_v(d1)} items wait on you over 3 d (of {_v(d1, 'n')}); "
                       f"oldest {_v(d1, 'oldest_d'):.0f} d", "rule": "D1 any item over 3 d",
                       "items": [r for r in rem if (r["age_d"] or 0) > 3][:8]})
    d4 = ms.get("D4")
    if _v(d4) is not None and _v(d4) >= 5 and _v(d4, "needs_you"):
        remote.append({"signal": "Blocker fan-in", "text": f"{_v(d4, 'blocker')} holds {_v(d4)} items and needs you",
                       "rule": "a blocker holding 5 or more that needs you", "items": [{"id": _v(d4, "blocker"),
                       "label": _v(d4, "blocker"), "link": f"/item/{_v(d4, 'blocker')}"}]})
    g1 = ms.get("G1")
    st = (steve or {}).get("steward") or {}
    # no "Steward escalation" remote signal: the steward's T+120 rung tells Operations, never him
    # (STEWARD_RUNG_FIX_ASKS_THE_WRONG_GROWNUP); an unreachable host is the in-person row below
    if steve.get("state") == "DOWN" and steve.get("down_min", 0) >= 30:
        person.append({"signal": "Machine unreachable", "text": f"SteveDesktop not answering ssh for {steve['down_min']} min",
                       "rule": "SteveDesktop or Archmagi not answering for 30 min"})
    hands = [r for r in inp if r["class"] == "hands"]
    if hands:
        person.append({"signal": "A login or a physical action", "text": f"{len(hands)} hands-on job"
                       f"{'s' if len(hands) != 1 else ''} at home", "rule": "a chore only your hands can do", "items": hands[:8]})
    w1 = ms.get("W1")
    walk_note = None
    if _v(w1):
        walk_note = (f"{_v(w1)} walk{'s' if _v(w1) != 1 else ''} owed; none can be called ready: staging (W2) is not "
                     "measured, so no walk is put to you yet")
    badges = {}
    badges["art"] = "YOU (remote)" if any(r["signal"] == "Pick queue" for r in remote) else "agents"
    badges["design"] = "YOU (remote)" if any(r["signal"] in ("Waiting on you", "Blocker fan-in") for r in remote) else "agents"
    badges["dev"] = "agents"
    badges["offline"] = "agents"
    if any(r["signal"] == "Machine unreachable" for r in person):
        badges["live"] = "YOU (in person)"
    elif st and (st.get("fault") or (_v(g1) or 0) > 0):
        badges["live"] = "steward"   # a fault the steward is working (§6.4 rungs before him)
    else:
        badges["live"] = "agents"
    badges["walk"] = "agents"
    for k, lead in ((s[0], s[2]) for s in STREAMS):
        if (ms.get(lead) or {}).get("m") != "MEASURED" and not badges[k].startswith("YOU"):
            badges[k] = "build the instrument"
    return {"remote": remote, "in_person": person, "walk_note": walk_note}, badges


def brief_line(ms, steve, arch):
    a1, d1 = _v(ms.get("A1")), _v(ms.get("D1"))
    you = ", ".join(x for x in (f"{a1} picks" if a1 is not None else "picks ?",
                                f"{d1} waits over 3 d" if d1 is not None else "waits ?") if x)
    return f"you: {you}; Steve {steve.get('state', '?')}; Archmagi {arch.get('state', '?')}"


# ---------------------------------------------------------------------------------------------- collect
def pacing(now, write=True):
    """The 15-min re-check (ACCOUNT_USAGE_WIRE_PULSE_TILE_ALLOCATOR): run slot_allocator, write allocation.json (the spawn
    hook reads it), and return the Pacing tile's record: mode, N per seat, why, and every account's % left against its
    time to reset. A crash returns UNMEASURED with the reason; it never draws as 0 helpers."""
    try:
        import slot_allocator as SA
        rules = SA.load_rules()
        dec = SA.publish(now, rules) if write else SA.compute(now, rules)  # compute+write under one lock
        inp = dec.get("inputs") or {}
        accs = []
        for name, a in sorted(((SA.meter_now(now) or {}).get("accounts") or {}).items()):
            sp = {"account": name, "pct_left": a.get("week_pct_left"), "pct_used": a.get("week_pct_used"),
                  "hours_to_reset": a.get("hours_to_week_reset"), "resets_at": a.get("week_resets_at")}
            _cap, rule = SA.lent_allowance(sp, rules, now)
            accs.append({"name": name, "pct_left": a.get("week_pct_left"), "hours_to_reset": a.get("hours_to_week_reset"),
                         "source": a.get("source") if not a.get("stale") else "STALE", "burn": name == inp.get("account"),
                         "rule": rule or None})
        return {"at": dec["at"], "mode": dec["mode"], "token_mode": dec["token_mode"], "queue_mode": dec["queue_mode"],
                "presence": dec["presence"], "seats": dec["seats"], "n_total": dec["n_total"], "why": dec["why"],
                "running": inp.get("helpers_running"), "overage": dec.get("overage"), "accounts": accs}
    except Exception as e:  # noqa: BLE001
        return {"m": "UNMEASURED", "why": f"slot_allocator crashed: {type(e).__name__}: {e}"}


def collect(now=None, events=None):
    t0 = time.time()
    now = now if now is not None else time.time()
    events = events if events is not None else pc.read_ledger()
    world, tl = RFM.timelines(events)
    ms = {}
    ms.update(guard(ledger_measures, ("D1", "D2", "D3", "D4", "V0", "P1", "P2", "P3", "P4", "W1", "W2", "W3", "W4"),
                    events, now, world, tl))
    rem, inp = guard(asks_now, (), events, now) if True else ([], [])
    if isinstance(rem, dict):
        rem, inp = [], []
    mx = guard(modcheck_today, ("O4",), now)
    if "fold" not in mx:
        mx = {"O4": mx.get("O4"), "fold": None}
    ms.update(guard(offline_measures, ("O1", "O2", "O3", "O4"), events, world, now, None, None, mx))
    ms.update(guard(art_queue, ("A1", "A4"), now))
    ms.update(guard(art_rates, ("A2", "A3", "A5"), now))
    src = TM.load_testq()
    ms.update(guard(live_measures, ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"), src, events, now))
    try:
        g9, arch = archmagi(now, src=src)
    except Exception as e:  # noqa: BLE001
        g9, arch = {"G9": U(f"archmagi crashed: {e}")}, {"state": "UNKNOWN", "why": str(e)}
    ms.update(g9)
    ms["B"] = guard(lambda n: {"B": budget(n)}, ("B",), now)["B"]
    s_state, s_why = steve_state(src, now)
    lv = TM.steve_live(src, now)
    stw, _ = steward_now(now, src.get("root"))
    steve = {"state": s_state, "why": s_why, "steward": {k: v for k, v in (stw or {}).items() if not k.startswith("_")},
             "down_min": round((now - lv["ssh_down_since"]) / 60) if lv.get("ssh_down_since") else 0,
             "busy_last_15": TM.pct(TM.length(_spans(src["attempts"], src["running"], now - 900, now, now)), 900)
             if not src.get("why") else None}
    needed, badges = needs_and_badges(ms, rem, inp, steve, now)
    needed["asks"] = {"remote": len(rem), "hands": sum(1 for r in inp if r["class"] == "hands"),
                      "walk": sum(1 for r in inp if r["class"] == "walk")}
    alloc = _read_json(DIR / "allocation.json")
    rec = {"schema": SCHEMA, "at": iso(now), "t": now, "measures": ms, "badges": badges, "needed": needed,
           "steve": steve, "archmagi": arch, "modcheck": mx.get("fold"),
           "slots": alloc.get("slots") if isinstance(alloc, dict) else None,
           "brief": brief_line(ms, steve, arch), "pacing": pacing(now), "run_s": None}
    rec["run_s"] = round(time.time() - t0, 1)
    return rec


def series_path():
    return DIR / "series.jsonl"


def append(rec, path=None):
    path = Path(path or series_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), default=str) + "\n")


def _tail_lines(path, since):
    """Lines of the file from roughly where `since` begins: the series only grows (~1.3 MB a day), and the panel
    reads 7 days of it on every request, so it reads backwards in doubling blocks instead of the whole history."""
    with open(path, "rb") as f:
        size = f.seek(0, 2)
        block = 2 << 20 if since is not None else size   # no cut = the whole history (backfill rewrites it all)
        while True:
            start = max(0, size - block)
            f.seek(start)
            data = f.read()
            lines = data.split(b"\n")
            if start > 0:
                lines = lines[1:]   # a partial first line
            first = next((ln for ln in lines if ln.strip()), None)
            t0 = None
            if first:
                m = re.search(rb'"t":([0-9.]+)', first)
                t0 = float(m.group(1)) if m else None
            if start == 0 or (t0 is not None and t0 < since):
                return [ln.decode("utf-8", "replace") for ln in lines]
            block *= 2


def read_series(path=None, since=None):
    path = Path(path or series_path())
    out = []
    try:
        lines = _tail_lines(path, since)
    except OSError:
        return out
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("schema") == SCHEMA and isinstance(r.get("t"), (int, float)) \
                and (since is None or r["t"] >= since):
            out.append(r)
    return sorted(out, key=lambda r: r["t"])


def backfill(days=7, step_h=1.0, path=None, events=None, src=None, now=None):
    """Hourly past records from the ledger and testq only (A1, O1, the asks and the states cannot be rebuilt for a
    past hour: they read files that only hold the present). Each is marked backfill and skipped where a real or
    backfilled record already covers that hour."""
    now = now if now is not None else time.time()
    events = events if events is not None else pc.read_ledger()
    src = src if src is not None else TM.load_testq()
    old = read_series(path)
    have = {int(r["t"] // HOUR) for r in old}
    new = []
    ep = [RFM.model.epoch(e["ts"]) or 0 for e in events]
    art = _art_events()
    hm = count_harness_mods()
    br = TM.load_bridge()
    n = 0
    t = (now // HOUR) * HOUR - HOUR + 3599
    stamps = []
    while t > now - days * DAY:
        if int(t // HOUR) not in have:
            stamps.append(t)
        t -= step_h * HOUR
    for t in sorted(stamps):
        cut = [e for e, x in zip(events, ep) if x <= t]
        sub = dict(src, attempts=[a for a in src["attempts"] if a["finished"] and a["finished"] <= t],
                   running=[], pending=[])
        ms = {k: U(NO_REBUILD) for k in ("A1", "A4", "O1", "O2", "O3", "O4", "B")}
        ms.update(guard(ledger_measures, ("D1", "D2", "D3", "D4", "V0", "P1", "P2", "P3", "P4", "W1", "W2", "W3", "W4"), cut, t))
        ms.update(guard(art_rates, ("A2", "A3", "A5"), t, art))
        ms.update(guard(live_measures, ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"), sub, cut, t, hm))
        ms["G1"] = U(NO_REBUILD)
        g9, _ = archmagi(t, br, game={"implies": None, "evidence": "backfill: no game reading for that hour", "at": t})
        ms.update(g9)
        drove = br.get("spans") and TM.length(TM.clip(br["spans"], t - HOUR, t)) > 0
        busy = TM.length(_spans(sub["attempts"], [], t - HOUR, t, t)) if sub["attempts"] else 0
        rec = {"schema": SCHEMA, "at": iso(t), "t": t, "backfill": True, "measures": ms, "badges": {}, "needed": None,
               "steve": {"state": None if not src.get("commissioned") or t < src["commissioned"]
                         else "RUNNING" if busy >= 0.5 * HOUR else "IDLE", "why": "backfill: busy share of the hour",
                         "busy_last_15": None, "busy_hour_pct": TM.pct(busy, HOUR)},
               "archmagi": {"state": "DRIVING" if drove else "UNKNOWN",
                            "why": "backfill: a bridge call in this hour" if drove else "backfill: up/down " + NO_REBUILD},
               "brief": None}
        new.append(rec)
        n += 1
    if new:   # rewrite in time order: read_series reads the tail and trusts the file to be sorted
        path = Path(path or series_path())
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for r in sorted(old + new, key=lambda r: r["t"]):
                f.write(json.dumps(r, separators=(",", ":"), default=str) + "\n")
        os.replace(tmp, path)
    return n


def _short(s, n=96):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


# ---------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("collect")
    c.add_argument("--no-write", action="store_true")
    c.add_argument("--print", action="store_true")
    b = sub.add_parser("backfill")
    b.add_argument("--days", type=float, default=7)
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        rec = collect()
        if not a.no_write:
            append(rec)
        if a.print:
            print(json.dumps(rec, indent=1, default=str))
        print(f"streams: {rec['brief']}  ({rec['run_s']} s; "
              f"{sum(1 for m in rec['measures'].values() if m.get('m') == 'MEASURED')} measured, "
              f"{sum(1 for m in rec['measures'].values() if m.get('m') != 'MEASURED')} unmeasured)", flush=True)
        return 0
    if a.cmd == "backfill":
        print(f"streams: backfilled {backfill(a.days)} hourly records")
        return 0
    if a.cmd == "show":
        s = read_series()
        if not s:
            print("no series yet")
            return 1
        r = [x for x in s if not x.get("backfill")][-1:] or s[-1:]
        r = r[0]
        print(f"AS OF {r['at']}: {r.get('brief')}")
        for k, m in r["measures"].items():
            print(f"  {k:3} {NAMES.get(k, k):24} " + (f"{m['v']}  {(m.get('x') or {}).get('unit', '')}" if m.get("m") == "MEASURED"
                                                    else f"UNMEASURED: {m.get('why')}"))
        return 0
    ap.print_help()
    return 2

if __name__ == "__main__":
    sys.exit(main())
