#!/usr/bin/env python3
"""streams.py — the Level 1 stream collector and the RimPulse Streams panel.

Design: design/RimMandrake/work_allocation_framework_2026-10-26.md §3 (measures), §4.1 (Level 1), §5 (when the
owner is the bottleneck), §7 (the panel). Items STREAM_METRICS_UNIFY_ONE_SERIES, MODCHECK_METRICS_RETIRE_INTO_HOURLY,
RIMPULSE_STREAMS_BUILD_VS_TIME.

    streams.py collect [--no-write] [--print]   one record -> streams/series.jsonl (the rm-pulse-streams timer, 15 min)
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
import html
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
import pulse_core as pc  # noqa: E402
import rimflow_metrics as RFM  # noqa: E402

MX = TM.MX
SCHEMA = "rm.streams/1"
DIR = Path(os.environ.get("RM_STREAMS_DIR", "/mnt/d/ClaudeWork/rimmandrake/streams"))
BENCH = Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))   # the data clone (the deploy is sparse)
FOUNDRY = Path("/home/mandrake/rm/foundry")
NIGHTLY = BENCH / "Transient" / "selftests_nightly.last"
ART_OUT = BENCH / "Transient" / "biome_ffar"
STALE_S = 45 * 60          # §7: no Level 1 record for 45 min greys the panel
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
def _art_events(clones=(BENCH, FOUNDRY)):
    """The art ledger, each seat's shard from its own clone (freshest there)."""
    out = []
    for c in clones:
        seat = "BENCH" if c == BENCH else "FOUNDRY"
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


def steward_escalated(st):
    """True when the steward's incident has reached him (an owner item is filed, §6.4 last rung)."""
    inc = st.get("incident") if isinstance(st.get("incident"), dict) else {}
    return bool(inc.get("owner_item") or st.get("escalated_to") == "owner" or st.get("escalation") == "owner")


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


def archmagi(now, br=None, snap=None, src=None):
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
    state, why = "UNKNOWN", "no pulse snapshot"
    snap = snap if snap is not None else _read_json(pc.STATE_DIR / "pulse_now.json")
    chip = next((c for c in (snap or {}).get("chips") or [] if c.get("label") == "rimworld"), None)
    if chip:
        title = str(chip.get("title") or "")
        up = " UP" in f" {title}"
        state, why = ("UP", title) if up else ("DOWN", title)
        if up and last and now - last <= 15 * 60:
            state = "DRIVING"
        if up and src and any((r["job"].get("lane") or "").lower() == "archmagi" for r in src.get("running") or []):
            state = "BATCH"
    return out, {"state": state, "why": why, "last_bridge_call": iso(last)}


def budget(now):
    import usage
    st = _read_json(pc.STATE_DIR / "usage.json") or {}
    p = usage.panel(st, usage.config(), now)
    rows = []
    for a in p["accounts"]:
        if a["role"] != "owned" or a["pct"] is None:
            continue
        left_d = max((a["resets_at"] or now) - now, 0) / DAY
        rows.append({"name": a["name"], "pct": a["pct"], "state": a["state"], "per_day_left": round((100 - a["pct"]) / left_d, 1)
                     if left_d >= 0.04 else None, "resets_in_d": round(left_d, 2), "asof": iso(a["measured_at"])})
    if not rows:
        return U("no account usage measured (usage.json empty or stale)")
    worst = max(rows, key=lambda r: r["pct"])
    return M(worst["pct"], TM.epoch(worst["asof"]), accounts=rows, unit="% of the week used (highest account)")


# ---------------------------------------------------------------------------------------------- badges + needs
STREAMS = (   # key, title, lead measure, how the lead reads, good band (lo, hi) or None
    ("art", "Art", "A1", "rows awaiting your pick", (0, 30)),
    ("design", "Design + you", "D1", "waits over 3 d", (0, 0)),
    ("dev", "Development", "V0", "built, not verified", None),
    ("offline", "Offline validation", "O1", "nightly FAIL + CRASH", (0, 0)),
    ("live", "Live validation (SteveDesktop)", "G2", "% busy, 2 h", (70, 100)),
    ("walk", "Your live walk", "W1", "walks owed", None),
)
STREAM_MEASURES = {"art": ("A1", "A2", "A3", "A4", "A5"), "design": ("D1", "D2", "D3", "D4"),
                   "dev": ("V0", "P1", "P2", "P3", "P4"), "offline": ("O1", "O2", "O3", "O4"),
                   "live": ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"), "walk": ("W1", "W2", "W3", "W4")}
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
    if st and steward_escalated(st):
        oi = ((st.get("incident") or {}).get("owner_item")) if isinstance(st.get("incident"), dict) else None
        remote.append({"signal": "Steward escalation", "text": f"SteveDesktop {st.get('state')}: no seat claimed it. "
                       f"{_short(st.get('reason') or '', 160)}", "rule": "T+120 min with no seat claiming the steward's item",
                       "items": [{"id": oi, "label": oi, "link": f"/item/{oi}"}] if oi else []})
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
        dec = SA.compute(now, rules)
        if write:
            SA.write(dec)
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
        g9, _ = archmagi(t, br, snap={"chips": []})
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


# ---------------------------------------------------------------------------------------------- the panel (§7)
# The panel draws what the records say; it computes no measure. Its only arithmetic is bucketing to hours.
HOURS = 168
ALARM = {"A1": 100, "D1": 10}
STEVE_COLOR = {"RUNNING": "var(--mustard)", "BUSY": "var(--mustard)", "IDLE": "#4a4036", "IDLE_WAITING": "#6d5a2e",
               "IDLE_EMPTY": "#4a4036", "EXHAUSTED": "#4a4036", "PAUSED": "var(--dim)", "DOWN": "var(--red)",
               # §6.1 fault states: the unowned clock runs, so they draw red
               "BRAKED": "var(--red)", "QUARANTINE": "var(--red)", "STALE_HEARTBEAT": "var(--red)"}
ARCH_COLOR = {"DRIVING": "var(--mustard)", "BATCH": "var(--lk)", "UP": "#4a4036", "DOWN": "var(--red)"}
BADGE_CLASS = {"agents": "ag", "steward": "sw", "YOU (remote)": "you", "YOU (in person)": "you",
               "build the instrument": "bi"}


def hourly(series, now, hours=HOURS):
    """The last record of each hour over the last `hours` hours: [record or None] oldest first."""
    top = int(now // HOUR)
    slots = [None] * hours
    for r in series:
        i = hours - 1 - (top - int(r["t"] // HOUR))
        if 0 <= i < hours and (slots[i] is None or r["t"] >= slots[i]["t"]):
            slots[i] = r
    return slots


def latest_live(series):
    real = [r for r in series if not r.get("backfill")]
    return real[-1] if real else None


def stale(series, now):
    r = latest_live(series)
    return r is None or now - r["t"] > STALE_S


def spark(slots, key, band, w=336, h=44):
    """Inline SVG: the value per hour as a line, broken where the hour is UNMEASURED (hollow ticks on the floor)
    or unrecorded (nothing); the good band shaded; the alarm line dashed."""
    vals = [((r or {}).get("measures") or {}).get(key) for r in slots]
    nums = [m["v"] for m in vals if m and m.get("m") == "MEASURED" and isinstance(m.get("v"), (int, float))]
    hi = max(nums + [band[1] if band else 0, ALARM.get(key, 0), 1])
    hi = 100 if band == (70, 100) else hi * 1.08
    n = len(slots)
    X = lambda i: round(i * w / max(n - 1, 1), 1)  # noqa: E731
    Y = lambda v: round(h - 3 - (h - 6) * (v / hi), 1)  # noqa: E731
    parts = [f"<svg class='sp' viewBox='0 0 {w} {h}' preserveAspectRatio='none' role='img'>"]
    if band:
        y1, y0 = Y(band[1]), Y(band[0])
        parts.append(f"<rect x='0' y='{min(y1, y0) - 1}' width='{w}' height='{max(abs(y0 - y1), 2)}' class='band'/>")
    if key in ALARM:
        parts.append(f"<line x1='0' x2='{w}' y1='{Y(ALARM[key])}' y2='{Y(ALARM[key])}' class='alarm'/>")
    for d in range(1, 7):   # day ticks
        parts.append(f"<line x1='{X(n - 1 - 24 * d)}' x2='{X(n - 1 - 24 * d)}' y1='0' y2='{h}' class='tick'/>")
    run, last = [], None
    for i, m in enumerate(vals):
        if m and m.get("m") == "MEASURED" and isinstance(m.get("v"), (int, float)):
            run.append(f"{X(i)},{Y(m['v'])}")
            last = (X(i), Y(m["v"]))
            continue
        if m and m.get("m") == "UNMEASURED":
            parts.append(f"<rect x='{X(i) - 0.6}' y='{h - 4}' width='1.6' height='3' class='hollow'/>")
        if run:
            parts.append(f"<polyline points='{' '.join(run)}' class='ln'/>" if len(run) > 1 else
                         f"<circle cx='{run[0].split(',')[0]}' cy='{run[0].split(',')[1]}' r='1.6' class='dot'/>")
            run = []
    if run:
        parts.append(f"<polyline points='{' '.join(run)}' class='ln'/>" if len(run) > 1 else "")
    if last:
        parts.append(f"<circle cx='{last[0]}' cy='{last[1]}' r='2.4' class='dot'/>")
    parts.append("</svg>")
    return "".join(parts)


def state_band(slots, part, colors, w=336, h=12):
    n = len(slots)
    bw = w / n
    out = [f"<svg class='bd' viewBox='0 0 {w} {h}' preserveAspectRatio='none'>"]
    for i, r in enumerate(slots):
        st = ((r or {}).get(part) or {}).get("state")
        x = round(i * bw, 2)
        if st in colors:
            out.append(f"<rect x='{x}' y='0' width='{round(bw + .2, 2)}' height='{h}' fill='{colors[st]}'><title>"
                       f"{html.escape(str(st))} {html.escape(str((r or {}).get('at')))}</title></rect>")
        else:   # no record, or a state nobody can read for that hour: hollow, never a colour
            out.append(f"<rect x='{x + .3}' y='{h - 2}' width='{round(max(bw - .6, .4), 2)}' height='1.2' class='hollow'/>")
    for d in range(1, 7):
        out.append(f"<line x1='{round(w - 24 * d * bw, 1)}' x2='{round(w - 24 * d * bw, 1)}' y1='0' y2='{h}' class='tick'/>")
    out.append("</svg>")
    return "".join(out)


def _fmt(v):
    if isinstance(v, float):
        return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:,.0f}"
    return f"{v:,}" if isinstance(v, int) else html.escape(str(v))


def _asof(m, now):
    a = TM.epoch(m.get("asof")) if m and m.get("asof") else None
    if a is None:
        return ""
    s = now - a
    ago = f"{int(s // 60)} min" if s < 5400 else (f"{s / 3600:.0f} h" if s < 2 * DAY else f"{s / DAY:.0f} d")
    return f"AS OF {datetime.datetime.fromtimestamp(a, MX._tz()).strftime('%a %H:%M')} ({ago} ago)"


def cell(key, m, now, lead=False):
    e = html.escape
    name = NAMES.get(key, key)
    if not m or m.get("m") != "MEASURED" or m.get("v") is None:
        why = (m or {}).get("why") or "no record"
        return (f"<div class='c un{' lead' if lead else ''}' title='{e(why)}'><span class='k'>{key}</span> {e(name)}"
                f"<span class='v'>UNMEASURED</span><span class='why'>{e(why)}</span></div>")
    x = m.get("x") or {}
    return (f"<div class='c{' lead' if lead else ''}'><span class='k'>{key}</span> {e(name)}<span class='v'>{_fmt(m['v'])}"
            f"<small> {e(str(x.get('unit', '')))}</small></span><span class='why'>{_asof(m, now)}</span></div>")


def _items(rows):
    e = html.escape
    out = []
    for r in rows or []:
        age = f" <span class='st'>{r['age_d']:.0f} d</span>" if r.get("age_d") is not None else ""
        lab = e(_short(r.get("label") or r["id"]))
        out.append(f"<li><a href='{e(r['link'])}'>{lab}</a>{age}</li>" if r.get("link") else f"<li>{lab}{age}</li>")
    return "<ul class='its'>" + "".join(out) + "</ul>" if out else ""


def _short(s, n=96):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


CSS2 = """
main.wide{max-width:min(1100px,100vw)}
.stale main>*:not(.hb){opacity:.42;filter:grayscale(1)}
.brief{font-size:16px;margin:10px 0 4px}.brief b{color:var(--mustard)}
.strip{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.strip a,.strip span{flex:1 1 96px;background:#241e19;border-radius:8px;
 padding:8px 10px;text-decoration:none;color:var(--ink)}.strip b{display:block;font-size:24px}.strip small{color:var(--dim);font-size:12px}
.need{display:grid;grid-template-columns:1fr;gap:10px}@media(min-width:760px){.need{grid-template-columns:1fr 1fr}
 .rows{display:grid;grid-template-columns:1fr 1fr;gap:0 22px}}
.need section{background:#211b17;border-radius:8px;padding:8px 12px}.need h3{color:var(--mustard)}
.sig{padding:6px 0;border-bottom:1px solid #2c251f}.sig .r{color:var(--faint);font-size:12px}
.its li{padding:3px 0;border:0;font-size:13.5px}
.row{padding:12px 0;border-bottom:1px solid #2c251f}.row h3{display:flex;justify-content:space-between;align-items:center;margin:0 0 4px;
 color:var(--ink);font-size:14.5px}
.bdg{font-size:11.5px;border-radius:10px;padding:1px 8px;white-space:nowrap;font-weight:600}.bdg.ag{background:#2f2822;color:var(--dim)}
.bdg.sw{background:#23323a;color:#bcd9e6}.bdg.you{background:var(--mustard);color:#191512}.bdg.bi{border:1px dashed var(--faint);color:var(--faint)}
.sp{width:100%;height:44px;display:block;background:#1f1a16;border-radius:4px}.band{fill:#3d4a2c;opacity:.75}
.ln{fill:none;stroke:var(--mustard);stroke-width:1.6;vector-effect:non-scaling-stroke}.dot{fill:var(--mustard)}
.alarm{stroke:var(--red);stroke-dasharray:3 3;stroke-width:1;vector-effect:non-scaling-stroke}
.tick{stroke:#2e2721;stroke-width:1;vector-effect:non-scaling-stroke}.hollow{fill:none;stroke:var(--faint);stroke-width:.8;vector-effect:non-scaling-stroke}
.ax{display:flex;justify-content:space-between;color:var(--faint);font-size:11px}
.c{font-size:13px;padding:3px 0;display:grid;grid-template-columns:auto 1fr;column-gap:6px}.c .k{color:var(--faint);font-size:11px;padding-top:2px}
.c .v{grid-column:2;font-weight:600}.c .v small{color:var(--dim);font-weight:400}.c .why{grid-column:2;color:var(--faint);font-size:11.5px}
.c.lead .v{font-size:22px}.c.un .v{font-weight:600;color:var(--faint);border:1px dashed var(--faint);border-radius:4px;padding:0 5px;
 justify-self:start;font-size:12px}.c.lead.un .v{font-size:13px}
details summary{cursor:pointer;color:var(--dim);font-size:12.5px;margin-top:4px}
.bd{width:100%;height:14px;display:block;background:#1f1a16;border-radius:3px}.key{font-size:11.5px;color:var(--dim)}
.key i{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 3px 0 8px;vertical-align:-1px}
.hollowbox{border:1px dashed var(--faint);border-radius:6px;padding:10px;color:var(--faint);font-size:13px}
"""


def render(series, now, base=""):
    """The Streams page (§7). `series`: read_series() records, oldest first."""
    from brief import CSS
    e = html.escape
    slots = hourly(series, now)
    r = latest_live(series)
    is_stale = stale(series, now)
    head = (f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,"
            f"initial-scale=1'><meta http-equiv='refresh' content='300'><title>RimPulse streams</title><style>{CSS}{CSS2}"
            f"</style></head><body{' class=stale' if is_stale else ''}><main class='wide'>")
    out = [head]
    if r is None:
        out.append("<div class='hb red'>No stream record yet: the rm-pulse-streams timer has not run "
                   "(<code>systemctl --user status rm-pulse-streams.timer</code>).</div></main></body></html>")
        return "".join(out)
    age = (now - r["t"]) / 60
    out.append(f"<div class='hb{' red' if is_stale else ''}'>Streams · AS OF {e(_hm(r['t']))} "
               f"({age:.0f} min ago){' · STALE: no record for 45 min, every value below is old' if is_stale else ''}"
               f" · <a href='{base}/brief'>brief</a></div>")
    out.append(f"<div class='brief'>{e(r.get('brief') or '')}</div>")
    ms = r.get("measures") or {}
    nd = r.get("needed") or {}
    a1, d1 = ms.get("A1") or {}, ms.get("D1") or {}
    # your queue strip
    def tile(m, label, sub):
        if m.get("m") != "MEASURED":
            return f"<span title='{e(m.get('why') or '')}'><b class='un'>?</b><small>{label}: UNMEASURED</small></span>"
        return f"<a href='#needed'><b>{_fmt(m['v'])}</b><small>{label}{sub}</small></a>"
    ax = a1.get("x") or {}
    dx = d1.get("x") or {}
    asks = nd.get("asks") or {}
    out.append("<div class='strip'>" + tile(a1, "art rows to pick", f" · oldest sheet {_fmt(ax.get('oldest_d') or 0)} d")
               + tile(d1, "waits over 3 d", f" of {_fmt(dx.get('n'))} · oldest {_fmt(dx.get('oldest_d') or 0)} d")
               + f"<a href='#needed'><b>{_fmt(asks.get('hands', 0))}</b><small>hands-on jobs at home</small></a></div>")
    # where you're needed
    out.append("<h2 id='needed'>Where you're needed</h2><div class='need'>")
    for title, key in (("Remote: decisions", "remote"), ("In person", "in_person")):
        sigs = nd.get(key) or []
        body = "".join(f"<div class='sig'><b>{e(s['signal'])}</b>: {e(s['text'])}<div class='r'>rule: {e(s['rule'])}</div>"
                       f"{_items(s.get('items'))}</div>" for s in sigs)
        if key == "in_person" and nd.get("walk_note"):
            body += f"<div class='sig r'>{e(nd['walk_note'])}</div>"
        out.append(f"<section><h3>{title}</h3>{body or '<div class=none>nothing is waiting on you here</div>'}</section>")
    out.append("</div>")
    # six stream rows
    out.append("<h2>Streams, last 7 days</h2><div class='rows'>")
    badges = r.get("badges") or {}
    for key, title, lead, _desc, band in STREAMS:
        b = badges.get(key, "agents")
        out.append(f"<div class='row'><h3>{e(title)}<span class='bdg {BADGE_CLASS.get(b, 'ag')}'>{e(b)}</span></h3>")
        out.append(cell(lead, ms.get(lead), now, lead=True))
        if key == "live":
            out.append(cell("G1", ms.get("G1"), now))
        out.append(spark(slots, lead, band))
        out.append(f"<div class='ax'><span>7 d ago</span>{_delta(slots, lead)}<span>{'band ' + str(band[0]) + '-' + str(band[1]) if band else 'no target band'}"
                   f"{' · alarm ' + str(ALARM[lead]) if lead in ALARM else ''}{' · ticks = unmeasured hours' if _has_un(slots, lead) else ''}"
                   f"</span><span>now</span></div>")
        rest = [k for k in STREAM_MEASURES[key] if k != lead and not (key == "live" and k == "G1")]
        nun = sum(1 for k in rest if (ms.get(k) or {}).get("m") != "MEASURED")
        out.append(f"<details><summary>{len(rest)} more measures ({nun} unmeasured)</summary>"
                   + "".join(cell(k, ms.get(k), now) for k in rest) + "</details></div>")
    out.append("</div>")
    # machines
    out.append("<h2>SteveDesktop, by hour</h2>" + state_band(slots, "steve", STEVE_COLOR)
               + "<div class='ax'><span>7 d ago</span><span>now</span></div>"
               + _key(dict(STEVE_COLOR, FAULT=STEVE_COLOR["BRAKED"]), ("RUNNING", "IDLE_WAITING", "IDLE", "PAUSED", "FAULT"))
               + f"<div class='m'>now: <b>{e(str((r.get('steve') or {}).get('state')))}</b> · {e(str((r.get('steve') or {}).get('why') or ''))}"
               + ("" if (r.get("steve") or {}).get("steward") else " · steward not built: unowned idle cannot be coloured yet")
               + "</div>")
    out.append("<h2>Archmagi, by hour</h2>" + state_band(slots, "archmagi", ARCH_COLOR)
               + "<div class='ax'><span>7 d ago</span><span>now</span></div>"
               + _key(ARCH_COLOR, ("DRIVING", "BATCH", "UP", "DOWN"))
               + f"<div class='m'>now: <b>{e(str((r.get('archmagi') or {}).get('state')))}</b> · "
                 f"{e(str((r.get('archmagi') or {}).get('why') or ''))} · hollow = not recorded (game up/down is not "
                 "rebuilt for hours before the collector ran)</div>")
    out.append(pacing_tile(r.get("pacing"), now))
    out.append("<h2>Builder slots</h2>")
    if not any(x.get("slots") for x in slots if x):
        out.append("<div class='hollowbox'>No per-stream split recorded: the allocator sets helpers per seat (Pacing, "
                   "above); splitting them across the six streams is not built. Drawn hollow, not as zero slots.</div>")
    else:
        out.append(slots_chart(slots))
    bm = ms.get("B") or {}
    if bm.get("m") == "MEASURED":
        acc = " · ".join(f"{e(a['name'])} {a['pct']:.0f}% used ({_fmt(a['per_day_left'])}%/day left until reset)"
                         if a.get("per_day_left") is not None else f"{e(a['name'])} {a['pct']:.0f}%"
                         for a in (bm.get("x") or {}).get("accounts") or [])
        out.append(f"<h2>Token budget</h2><div class='m'>{acc} · {_asof(bm, now)}</div>")
    else:
        out.append(f"<h2>Token budget</h2>{cell('B', bm, now)}")
    mc = r.get("modcheck") or {}
    if mc:
        aw = mc.get("all_work") or {}
        out.append(f"<div class='foot'>modcheck today ({e(str(mc.get('day')))}): {_fmt(aw.get('executed_min') or 0)} live min "
                   f"classified, waste {_fmt(round(100 * (aw.get('waste') or 0), 1))}% · alarms "
                   f"{e(', '.join(map(str, mc.get('alarms') or [])) or 'none')}</div>")
    out.append(f"<div class='foot'>One record every 15 min from streams.py (design/RimMandrake/work_allocation_framework_2026-10-26.md §3, §7). "
               f"UNMEASURED never draws as 0. {sum(1 for x in series if x.get('backfill'))} hours before the collector started are "
               "rebuilt from the ledger and testq (marked backfill); A1, O1, O3 and the budget hold only the present, so "
               "they start when the collector does.</div></main></body></html>")
    return "".join(out)


def pacing_tile(pc_, now):
    """Pacing: the allocator's mode and N per seat, why, and each account's % left against the share of its week left."""
    e = html.escape
    out = ["<h2>Pacing</h2>"]
    if not isinstance(pc_, dict) or pc_.get("m") == "UNMEASURED" or not pc_.get("seats"):
        why = (pc_ or {}).get("why") if isinstance(pc_, dict) else "this record predates the allocator wiring"
        return out[0] + f"<div class='hollowbox'>No pacing recorded: {e(str(why))}. Drawn hollow, not as zero helpers.</div>"
    run = pc_.get("running") or {}
    seats = " · ".join(f"{e(k)} <b>{v}</b>" + (f" ({run[k]} running)" if k in run else "") for k, v in pc_["seats"].items())
    out.append(f"<div class='m'><b>{e(pc_.get('mode') or '')}</b> {e(pc_.get('queue_mode') or '')} "
               f"{e(pc_.get('presence') or '')} · {seats} · total {pc_.get('n_total')} · as of {e(str(pc_.get('at')))}</div>")
    out.append(f"<div class='m'>why: {e(pc_.get('why') or '')}</div>")
    ov = pc_.get("overage")
    if isinstance(ov, dict):
        owed = float(ov.get("owed_h") or 0)
        if owed > 0:
            out.append(f"<div class='m'>overage owed: <b>{owed:.1f} helper-h</b> · payback: {e(str(ov.get('plan') or ''))}</div>")
        else:
            out.append("<div class='m'>overage owed: <b>0 helper-h</b> · no payback due</div>")
    rows = []
    for a in pc_.get("accounts") or []:
        tag = " · seats burn this" if a.get("burn") else ""
        rule = f" · {e(a['rule'])}" if a.get("rule") else ""
        if a.get("pct_left") is None or a.get("hours_to_reset") is None or a.get("source") not in ("MEASURED", "ESTIMATE"):
            rows.append(f"<div class='m'>{e(a['name'])}: <b class='un'>?</b> {e(str(a.get('source') or 'UNMEASURED'))}{tag}{rule}</div>")
            continue
        wk = max(0.0, min(100.0, 100 * a["hours_to_reset"] / 168))
        left = max(0.0, min(100.0, float(a["pct_left"])))
        col = "#8fae6b" if left >= wk else ("#e0aa3e" if left >= 0.5 * wk else "#c9524a")
        bar = (f"<svg class='sp' viewBox='0 0 200 14' preserveAspectRatio='none' style='height:14px'>"
               f"<rect x='0' y='1' width='{2 * left:.1f}' height='8' fill='{col}'/>"
               f"<rect x='{2 * wk:.1f}' y='0' width='1.5' height='14' fill='var(--faint)'/></svg>")
        est = " (ESTIMATE)" if a.get("source") == "ESTIMATE" else ""
        rows.append(f"<div class='m'>{e(a['name'])}: {left:.0f}% left · {a['hours_to_reset']:.0f} h to reset "
                    f"({wk:.0f}% of the week){est}{tag}{rule}{bar}</div>")
    out.append("".join(rows))
    out.append("<div class='foot'>Bar = % of the week left; tick = share of the week's time left before that account resets "
               "(bar left of the tick: burning faster than the week). Re-checked every 15 min by slot_allocator.py "
               "(src/RimMandrake/Utils/slot_rules.json); the spawn hook refuses a helper over a seat's N. Only his word "
               "overrides: <code>slot_allocator.py set --seat S --n N --owner-said \"...\"</code>.</div>")
    return "".join(out)


def _delta(slots, key, hours=72):
    """The change over the last 3 days, from the hourly buckets (a slow series's line looks flat at full scale)."""
    vals = [(i, ((r or {}).get("measures") or {}).get(key) or {}) for i, r in enumerate(slots)]
    vals = [(i, m["v"]) for i, m in vals if m.get("m") == "MEASURED" and isinstance(m.get("v"), (int, float))]
    if len(vals) < 2 or vals[-1][0] - vals[0][0] < hours // 2:
        return ""
    then = next((v for i, v in vals if i >= len(slots) - 1 - hours), vals[0][1])
    d = vals[-1][1] - then
    return f"<span>{'+' if d > 0 else ''}{_fmt(round(d, 1))} in 3 d</span>"


def _has_un(slots, key):
    return any((((r or {}).get("measures") or {}).get(key) or {}).get("m") == "UNMEASURED" for r in slots)


def _key(colors, order):
    return "<div class='key'>" + "".join(f"<i style='background:{colors[k]}'></i>{k.lower().replace('_', ' ')}" for k in order) + \
        "<i class='hk' style='border:1px dashed var(--faint)'></i>not recorded</div>"


def slots_chart(slots, w=336, h=40):
    keys = [s[0] for s in STREAMS]
    cols = dict(zip(keys, ("#e0aa3e", "#c9824a", "#8fae6b", "#6f9fb8", "#b48ad1", "#d0c27a")))
    n = len(slots)
    bw = w / n
    out = [f"<svg class='sp' viewBox='0 0 {w} {h}' preserveAspectRatio='none'>"]
    for i, r in enumerate(slots):
        al = (r or {}).get("slots") or {}
        tot = sum(v for v in al.values() if isinstance(v, (int, float))) or 0
        y = h
        for k in keys:
            v = al.get(k) or 0
            if v and tot:
                hh = (h - 2) * v / max(tot, 4)
                y -= hh
                out.append(f"<rect x='{round(i * bw, 2)}' y='{round(y, 2)}' width='{round(bw + .2, 2)}' height='{round(hh, 2)}' "
                           f"fill='{cols[k]}'/>")
    out.append("</svg>")
    return "".join(out) + "<div class='key'>" + "".join(f"<i style='background:{cols[k]}'></i>{k}" for k in keys) + "</div>"


def _hm(t):
    return datetime.datetime.fromtimestamp(t, MX._tz()).strftime("%a %H:%M")


def page(path, now=None):
    """/streams and /streams.json, served by brief.page on loopback 8765 and the tailnet listener."""
    now = now if now is not None else time.time()
    series = read_series(since=now - (HOURS + 1) * HOUR)
    if path.endswith(".json"):
        r = latest_live(series)
        return 200, "application/json", json.dumps({"latest": r, "stale": stale(series, now), "records_7d": len(series)},
                                                   default=str).encode()
    return 200, "text/html; charset=utf-8", render(series, now).encode()


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
    rn = sub.add_parser("render", help="write the panel HTML to a file (screenshots, review)")
    rn.add_argument("out")
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
    if a.cmd == "render":
        Path(a.out).write_text(page("/streams")[2].decode(), encoding="utf-8")
        print(a.out)
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
