#!/usr/bin/env python3
"""v3_vs_v2: is RimFlow v3 beating the tagged v2 baseline, and at what cost? (no AI, weekly)

The owner, 2026-10-27: "Please ensure that the RimFlow v3 will be able to actively determine if it's actually helping
vs. the baseline of the recently tagged Rimflow v2 (Bench + Foundry). We MUST prove that it's superior and at what
cost. After it's settled down and optimized of course. One of the v3 roles must own this regular assessment."
Item V3_VERSUS_V2_MEASURE_PROVE_IT_PAYS. Owner of the assessment: Operations (roles/operations.md); the quality half is
re-checked, token-blind, by the Auditor (roles/auditor.md).

What it does, for one week (7 days ending Monday 07:00 local):
  1. measures v3 on each baseline metric with the baseline's own definitions (design/RimMandrake/
     baseline_two_seat_system_2026-10-26.md §4 and its scripts): the ledger through rimflow_metrics.compute on the
     events before the week's end, the transcripts with the spend_census token formula, git for the process share;
  2. compares each to the v2 weeks named in the rule file (frozen v2 history, tag system-baseline-two-seat-2026-10-26)
     with a noise band from their week-to-week spread: BETTER / SAME / WORSE / UNMEASURED;
  3. applies the verdict rule that was written down BEFORE any v3 data (v3_vs_v2_rules.json, sha256 pinned below and
     in the selftest; a changed rule refuses to judge until the pin and an amendment entry say why);
  4. adds the simulator's counterfactual (what v2 would have done in this week's conditions), which counts only while
     its backtest on held-out real v2 weeks passes, and can only lower a verdict;
  5. writes D:\\ClaudeWork\\rimmandrake\\v3_vs_v2\\: weeks/<end>.json, history.jsonl, verdict.md (Operations: every
     figure, cost included) and quality_blind.md (the Auditor: quality metrics only, no token, account or cost word).

Operations reads verdict.md, checks it against the week file and sends it to the owner by its owner-only route.

Usage:
  v3_vs_v2.py baseline              # (re)measure the frozen v2 weeks -> v2_weeks.json
  v3_vs_v2.py run [--end 2026-11-30] [--no-counterfactual]
  v3_vs_v2.py rules                 # print the rule hash and whether it matches the pin
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "sim"))
import model  # noqa: E402
import rimflow_metrics  # noqa: E402
import spend_census as S  # noqa: E402

RULES_PATH = os.path.join(HERE, "v3_vs_v2_rules.json")
# The rule's pins, oldest first: (sha256 of v3_vs_v2_rules.json, date, reason, before any v3 data?). Changing the rule
# means appending a pin here AND an entry in the rule's "amendments" (date, reason, before_v3_data); the selftest
# checks both, so the rule cannot change silently. A pin with before_v3_data False is printed on every verdict.
RULE_PINS = [
    ("c2f177518417fb637d888c8695398ccf65fd35f30dcee75211bd6b7257cd17dd", "2026-10-27", "pre-registered with the program, before any v3 week existed", True),
    ("1f721889fc08f199da61151d54fe82be4f133ee58ab6fe0ae98a57bea7d58474", "2026-10-27", "owner by card: majority of measures (4 of 7 BETTER, no guard or veto primary WORSE)", True),
]
SIM = os.path.join(HERE, "sim", "rimflow_v3_sim.py")
DAY = 86400.0
WEEK_DAYS = 7


def out_dir():
    return os.environ.get("RM_V3V2_DIR", "/mnt/d/ClaudeWork/rimmandrake/v3_vs_v2")


def projects_dir():
    return os.environ.get("RM_V3V2_PROJECTS", S.PROJECTS)


# ---------------------------------------------------------------- the rule
def rules_sha(path=RULES_PATH):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_rules(path=RULES_PATH):
    return json.load(open(path, encoding="utf-8"))


def rules_status(path=RULES_PATH):
    """-> (ok, text). ok only when the file's hash is the last pin."""
    sha = rules_sha(path)
    pin = RULE_PINS[-1]
    if sha != pin[0]:
        return False, ("RULES CHANGED: v3_vs_v2_rules.json sha256 %s is not the pinned %s. Nothing is judged until a "
                       "new pin and an amendment entry (date, reason, before or after v3 data) say why." % (sha, pin[0]))
    late = [p for p in RULE_PINS if not p[3]]
    txt = "rule sha256 %s, pinned %s (%s)" % (sha[:12], pin[1], pin[2])
    if late:
        txt += "; AMENDED AFTER v3 DATA EXISTED on " + ", ".join(p[1] for p in late)
    return True, txt


# ---------------------------------------------------------------- weeks
def week_end(day: str, rules) -> float:
    """local date 'YYYY-MM-DD' (a Monday) -> epoch of 07:00 local that day"""
    d = dt.datetime.strptime(day, "%Y-%m-%d").replace(hour=rules["week"]["end_local_hour"])
    return d.timestamp()   # naive -> local time


def last_week_end(now, rules) -> str:
    d = dt.datetime.fromtimestamp(now)
    h = rules["week"]["end_local_hour"]
    cand = d.replace(hour=h, minute=0, second=0, microsecond=0) - dt.timedelta(days=(d.weekday() - rules["week"]["end_weekday"]) % 7)
    if cand > d:
        cand -= dt.timedelta(days=7)
    return cand.strftime("%Y-%m-%d")


# ---------------------------------------------------------------- measures
def M(v, mark="MEASURED", why="", num=None, den=None):
    p = {"v": v, "mark": mark, "why": why}
    if den is not None:
        p["num"], p["den"] = num, den
    return p


def U(why):
    return {"v": None, "mark": "UNMEASURED", "why": why}


def ledger_week(events, lo, hi):
    """The ledger metrics for [lo, hi), as of hi (events at or after hi are not seen)."""
    ev = [e for e in events if (model.epoch(e.get("ts")) or 0) < hi]
    if not ev:
        return {k: U("no ledger event before the week's end") for k in
                ("done_wk", "filed_wk", "net_wk", "owner_wait_over_3d", "owner_resolve_med_d", "rework_share",
                 "close_no_level_share", "verify_backlog", "vfail_share", "doing_live_lease_share", "lapsed_open",
                 "contested_new_wk", "owner_filed_wk")}
    if model.epoch(ev[0]["ts"]) > lo - WEEK_DAYS * DAY:
        why = "the ledger starts %s, under a week before the window; its stocks are not filled" % ev[0]["ts"]
        return {k: U(why) for k in ("done_wk", "filed_wk", "net_wk", "owner_wait_over_3d", "owner_resolve_med_d",
                                    "rework_share", "close_no_level_share", "verify_backlog", "vfail_share",
                                    "doing_live_lease_share", "lapsed_open", "contested_new_wk", "owner_filed_wk")}
    r = rimflow_metrics.compute(ev, now=hi, window_days=(hi - lo) / DAY)
    out = {}
    fl = r["flow"]
    out["done_wk"] = M(fl.get("done", 0))
    out["filed_wk"] = M(fl.get("filed", 0))
    out["net_wk"] = M(fl.get("net", 0))
    out["owner_wait_over_3d"] = M(r["owner_wait_open"]["over_3d"])
    med = r["owner_wait_resolved"].get("median_d")
    out["owner_resolve_med_d"] = M(med) if med is not None else U("no owner wait resolved in the week")
    rw = r["rework"]
    out["rework_share"] = M(rw["cause_already_done"] / rw["filed"], num=rw["cause_already_done"], den=rw["filed"]) if rw["filed"] else U("nothing filed in the week")
    out["verify_backlog"] = M(r["verify_backlog"]["n"])
    vr = r["verify_results"]
    nv = sum(vr.values())
    out["vfail_share"] = M(vr.get("fail", 0) / nv, num=vr.get("fail", 0), den=nv) if nv else U("no verify result in the week")
    out["lapsed_open"] = M(r["leases"]["open_items_lapsed_now"])
    pv = r.get("provenance_filed", {})
    out["owner_filed_wk"] = M(pv.get("ownerSaid", 0) + pv.get("byCard", 0))
    # M8, as baseline ledger_measures.py: a close with no verify event carrying a level at or before it
    lvl = collections.defaultdict(list)
    closes = []
    lo_iso = dt.datetime.fromtimestamp(lo, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for e in ev:
        if e["event"] == "verify" and e.get("level"):
            lvl[e["id"]].append(e["ts"])
        elif e["event"] == "close" and e["ts"] >= lo_iso:
            closes.append(e)
    if closes:
        bad = sum(1 for e in closes if not any(t <= e["ts"] for t in lvl[e["id"]]))
        out["close_no_level_share"] = M(bad / len(closes), why="%d of %d closes" % (bad, len(closes)), num=bad, den=len(closes))
    else:
        out["close_no_level_share"] = U("no close in the week")
    # M9 as baseline doing_leases.py, and M10's contested claims added in the week
    w_hi = model.replay(ev)
    doing = [it for it in w_hi.items.values() if it.state == "doing"]
    live = sum(1 for it in doing if model.lease_status(it, hi) == "live")
    out["doing_live_lease_share"] = (M(live / len(doing), why="%d of %d doing items" % (live, len(doing)), num=live, den=len(doing))
                                     if doing else U("no doing item at the week's end"))
    w_lo = model.replay([e for e in ev if (model.epoch(e.get("ts")) or 0) < lo])
    out["contested_new_wk"] = M(len(w_hi.contested_claims) - len(w_lo.contested_claims))
    return out


def transcript_weeks(windows, rules, projects=None):
    """One pass over the transcripts for several [lo, hi) windows. Token arithmetic is spend_census.scan_file's
    (model weight x (input + 0.1 cache read + 1.25 5-min write + 2 1-h write + 5 output)), de-duplicated by message
    id across files; the selftest holds it equal to scan_file on the same transcript."""
    projects = projects or projects_dir()
    fams = set(rules["families"])
    big = rules["ctx_big"]
    rx = re.compile(rules["already_ruled_regex"], re.I)
    lo_min = min(lo for lo, _ in windows)
    acc = [collections.defaultdict(float) for _ in windows]
    helpers = [set() for _ in windows]
    hours = [set() for _ in windows]
    first_call = [None]
    seen = set()

    def which(t):
        return [i for i, (lo, hi) in enumerate(windows) if lo <= t < hi]

    for root, _dirs, files in os.walk(projects):
        rel = os.path.relpath(root, projects)
        if rel == ".":
            continue
        proj = rel.split(os.sep)[0]
        fam = S.family(proj)
        top = rel == proj
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            p = os.path.join(root, f)
            try:
                if os.path.getmtime(p) < lo_min:
                    continue
                fh = open(p, errors="replace")
            except OSError:
                continue
            sub = "/subagents/" in p
            with fh:
                for line in fh:
                    if '"usage"' in line:
                        try:
                            d = json.loads(line)
                        except Exception:
                            continue
                        if d.get("type") != "assistant" or d.get("isSidechain") and not sub:
                            continue
                        m = d.get("message") or {}
                        u, mid = m.get("usage"), m.get("id")
                        if not u or not d.get("timestamp") or mid in seen:
                            continue
                        seen.add(mid)
                        t = S.ts(d["timestamp"])
                        if first_call[0] is None or t < first_call[0]:
                            first_call[0] = t
                        ws = which(t)
                        if not ws:
                            continue
                        cc = u.get("cache_creation") or {}
                        c5, c1 = cc.get("ephemeral_5m_input_tokens"), cc.get("ephemeral_1h_input_tokens")
                        if c5 is None and c1 is None:
                            c5, c1 = u.get("cache_creation_input_tokens") or 0, 0
                        c5, c1 = c5 or 0, c1 or 0
                        cr = u.get("cache_read_input_tokens") or 0
                        it = u.get("input_tokens") or 0
                        ite = S.model_x(m.get("model")) * (it + 0.1 * cr + 1.25 * c5 + 2.0 * c1 + 5.0 * (u.get("output_tokens") or 0))
                        for i in ws:
                            a = acc[i]
                            a["all_ite"] += ite
                            if fam not in fams:
                                continue
                            a["ite"] += ite
                            if sub:
                                a["sub_ite"] += ite
                                helpers[i].add(p)
                                if it + cr + c5 + c1 > big:
                                    a["sub_ite_big"] += ite
                            else:
                                a["seat_ite"] += ite
                    elif top and fam in fams and '"origin"' in line and '"human"' in line:
                        try:
                            d = json.loads(line)
                        except Exception:
                            continue
                        if d.get("type") != "user" or (d.get("origin") or {}).get("kind") != "human" or not d.get("timestamp"):
                            continue
                        t = S.ts(d["timestamp"])
                        c = (d.get("message") or {}).get("content")
                        txt = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if isinstance(b, dict))
                        for i in which(t):
                            acc[i]["owner_msgs"] += 1
                            hours[i].add(int(t // 3600))
                            if rx.search(txt):
                                acc[i]["already_ruled"] += 1
    res = []
    for i, (lo, hi) in enumerate(windows):
        a = acc[i]
        if first_call[0] is None or first_call[0] > lo + DAY:
            why = "no transcript call before %s: the window starts before the transcripts do" % (
                time.strftime("%Y-%m-%d", time.localtime(lo + DAY)))
            res.append({k: U(why) for k in ("ite_wk", "all_ite_wk", "helpers_wk", "sub_ite_big_ctx_share",
                                             "seat_ite_share", "owner_msgs_wk", "owner_active_h_wk", "already_ruled_wk")})
            continue
        o = {}
        if a["ite"] <= 0:
            o.update({k: U("no BENCH or FOUNDRY call in the window (a blind instrument, never zero spend)")
                      for k in ("ite_wk", "helpers_wk", "sub_ite_big_ctx_share", "seat_ite_share")})
        else:
            o["ite_wk"] = M(a["ite"])
            o["helpers_wk"] = M(len(helpers[i]))
            o["seat_ite_share"] = M(a["seat_ite"] / a["ite"], num=a["seat_ite"], den=a["ite"])
            o["sub_ite_big_ctx_share"] = M(a["sub_ite_big"] / a["sub_ite"], num=a["sub_ite_big"], den=a["sub_ite"]) if a["sub_ite"] else U("no subagent call")
        o["all_ite_wk"] = M(a["all_ite"]) if a["all_ite"] > 0 else U("no call in the window")
        if a["owner_msgs"] <= 0:
            why = "no human-origin message in the window: the owner was away or the origin field is missing; not zero"
            o.update({k: U(why) for k in ("owner_msgs_wk", "owner_active_h_wk", "already_ruled_wk")})
        else:
            o["owner_msgs_wk"] = M(int(a["owner_msgs"]), "ESTIMATE", "proxy for his minutes")
            o["owner_active_h_wk"] = M(len(hours[i]), "ESTIMATE", "proxy for his minutes")
            o["already_ruled_wk"] = M(int(a["already_ruled"]))
        res.append(o)
    return res


def git_process_share(lo, hi, rules, repo=REPO):
    r = subprocess.run(["git", "-C", repo, "log", "--since=@%d" % int(lo), "--until=@%d" % int(hi), "--no-renames",
                        "--name-only", "--format=@@%ct"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return U("git log failed: " + r.stderr.strip()[-160:])
    rx = re.compile(rules["process_regex"])
    commits, cur = [], None
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            cur = [int(line[2:]), []]
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur[1].append(line.strip())
    cs = [fs for t, fs in commits if fs and lo <= t < hi]
    if not cs:
        return U("no commit with files in the window")
    p = sum(1 for fs in cs if all(rx.match(f) for f in fs))
    return M(p / len(cs), why="%d of %d commits" % (p, len(cs)), num=p, den=len(cs))


def measure_windows(wins, rules, events=None, projects=None, repo=REPO):
    """-> [{metric: point}] for each [lo, hi) window (a week, or a day of the tag week for the noise band)."""
    events = events if events is not None else model.read()
    tw = transcript_weeks(wins, rules, projects)
    out = []
    for (lo, hi), t in zip(wins, tw):
        w = ledger_week(events, lo, hi)
        w.update(t)
        w["process_share"] = git_process_share(lo, hi, rules, repo)
        ite, done = w.get("ite_wk", {}).get("v"), w.get("done_wk", {}).get("v")
        w["ite_per_done"] = (M(ite / done, num=ite, den=done) if ite and done
                             else U("token use or done unmeasured, or no item done"))
        out.append(w)
    return out


def measure_weeks(days, rules, events=None, projects=None, repo=REPO):
    """-> {day: {metric: point}} for the weeks ending on those Mondays."""
    wins = [(week_end(d, rules) - WEEK_DAYS * DAY, week_end(d, rules)) for d in days]
    return dict(zip(days, measure_windows(wins, rules, events, projects, repo)))


# ---------------------------------------------------------------- comparison
def _x(v, scale):
    return math.log1p(max(v, 0.0)) if scale == "log" else float(v)


def _boot(m, days, rules):
    """-> list of the metric's values on its scale: for count and ratio metrics, recomputed on weeks resampled from
    the tag week's 7 days; for a stock, the 7 end-of-day readings. None when too few days were measured."""
    k, kind, B = m["key"], m.get("kind"), rules["band"]
    pts = [d.get(k) or {} for d in days]
    if sum(1 for p in pts if p.get("v") is not None) < 5:
        return None
    n = len(pts)
    rng = __import__("random").Random(B["seed"])
    if kind == "stock":
        return [_x(p["v"], m["scale"]) for p in pts if p.get("v") is not None]
    if kind == "count":
        vals = [p.get("v") or 0 for p in pts]     # a day with no owner message is a quiet day, inside a measured week
        return [_x(sum(vals[rng.randrange(n)] for _ in range(n)), m["scale"]) for _ in range(B["resamples"])]
    if kind == "ratio":
        nd = [(p.get("num") or 0, p.get("den") or 0) for p in pts]
        out = []
        for _ in range(B["resamples"]):
            pick = [nd[rng.randrange(n)] for _ in range(n)]
            den = sum(x[1] for x in pick)
            if den:
                out.append(_x(sum(x[0] for x in pick) / den, m["scale"]))
        return out
    return None


def reference(v2, rules):
    """per metric: the tag week's value, its noise band from the tag week's own days, and the earlier v2 weeks"""
    H = rules["v2_history"]
    ref = {}
    for m in rules["metrics"]:
        k = m["key"]
        p = v2["weeks"].get(H["reference_week"], {}).get(k) or {}
        ctx = [(v2["weeks"].get(d, {}).get(k) or {}).get("v") for d in H["context_weeks"]]
        if p.get("v") is None:
            ref[k] = {"value": None, "x": None, "band": None, "context": ctx, "why": p.get("why", "not measured")}
            continue
        xs = _boot(m, v2.get("days") or [], rules) if m.get("kind") != "none" else None
        sd = statistics.pstdev(xs) if xs and len(xs) > 1 else None
        noise = rules["band"]["z"] * sd * math.sqrt(2) if sd is not None else 0.0
        ref[k] = {"value": p["v"], "x": _x(p["v"], m["scale"]), "sd": sd, "band": max(noise, m["floor"]),
                  "band_from": "floor" if noise < m["floor"] else "days", "context": ctx}
    return ref


def classify(m, point, ref):
    """-> BETTER / SAME / WORSE / UNMEASURED / NO_BASELINE (and the signed distance in bands)"""
    if not point or point.get("v") is None:
        return "UNMEASURED", None
    r = ref.get(m["key"]) or {}
    if r.get("x") is None:
        return "NO_BASELINE", None
    d = _x(point["v"], m["scale"]) - r["x"]
    z = d / r["band"] if r["band"] else 0.0
    if m.get("kill_above") is not None and point["v"] > m["kill_above"]:
        return "WORSE", z
    if abs(d) <= r["band"] or m["better"] == "none":
        return "SAME", z
    up = d > 0
    return ("BETTER" if up == (m["better"] == "higher") else "WORSE"), z


def judge_week(week, ref, rules, cf=None):
    per = {}
    for m in rules["metrics"]:
        c, z = classify(m, week.get(m["key"]), ref)
        per[m["key"]] = {"class": c, "bands": None if z is None else round(z, 2), "group": m["group"]}
    # the counterfactual can only take BETTER back, never give it
    cf_ok = bool(cf and cf.get("status") == "MEASURED")
    if cf_ok:
        for k, rng in cf["range"].items():
            if k in per and per[k]["class"] == "BETTER":
                m = next(x for x in rules["metrics"] if x["key"] == k)
                v = week[k]["v"]
                past = v > rng[1] if m["better"] == "higher" else v < rng[0]
                per[k]["cf"] = "past the v2 range" if past else "inside the v2 range"
                if not past:
                    per[k]["class_cf"] = "SAME"
    prim = [k for k, p in per.items() if p["group"] == "primary"]
    cls = {k: per[k].get("class_cf", per[k]["class"]) for k in per}
    measured = [k for k in prim if cls[k] in ("BETTER", "SAME", "WORSE")]
    better = [k for k in prim if cls[k] == "BETTER"]
    worse = [k for k in prim if cls[k] == "WORSE"]
    gworse = [k for k, p in per.items() if p["group"] == "guard" and cls[k] == "WORSE"]
    V = rules["verdict"]
    veto = [k for k in worse if k in V.get("superior_veto", [])]
    if len(measured) < V["min_primary_measured"] or cls.get("ite_wk") not in ("BETTER", "SAME", "WORSE"):
        verdict = "UNMEASURED"
    elif not gworse and not veto and len(better) >= V["superior_min_better"]:
        verdict = "SUPERIOR"      # majority of measures (owner by card 2026-10-27): a non-veto primary may be WORSE
    elif (len(worse) >= V["worse_min_worse"] and len(worse) >= len(better)) or (worse and not better):
        verdict = "WORSE"
    else:
        verdict = "NOT_SHOWN"
    cc = [cls.get("ite_wk"), cls.get("ite_per_done")]
    cost = "HIGHER" if "WORSE" in cc else "LOWER" if "BETTER" in cc else "SAME" if "SAME" in cc else "UNMEASURED"
    ite, rm = week.get("ite_wk", {}).get("v"), (ref.get("ite_wk") or {}).get("value")
    ratio = round(ite / rm, 3) if ite and rm else None
    return {"verdict": verdict, "cost": cost, "ite_ratio_to_v2": ratio, "per": per, "primary_measured": len(measured),
            "better": better, "worse": worse, "guard_worse": gworse, "counterfactual_used": cf_ok}


def standing(history, rules):
    S_ = rules["standing"]
    st = [h for h in history if h.get("settled") and h["verdict"] != "UNMEASURED"][-S_["weeks"]:]
    v = [h["verdict"] for h in st]
    if v.count("WORSE") >= S_["worse_min"]:
        s = "WORSE"
    elif v.count("SUPERIOR") >= S_["superior_min"] and "WORSE" not in v:
        s = "SUPERIOR"
    else:
        s = "NOT_SHOWN"
    ratios = [h["ite_ratio_to_v2"] for h in st if h.get("ite_ratio_to_v2")]
    return {"standing": s if len(st) >= S_["weeks"] else "PROVISIONAL", "rule_reading": s, "weeks": [h["end"] for h in st],
            "cost_ratio_median": round(statistics.median(ratios), 3) if ratios else None}


# ---------------------------------------------------------------- settled
def settled(lo, hi, rules, repo=REPO):
    """-> (settled, live, why). Checkable: git history of the v3 config files."""
    paths = rules["settled"]["config_paths"]
    r = subprocess.run(["git", "-C", repo, "log", "--format=%H %ct", "--until=@%d" % int(hi), "--"] + paths,
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return False, False, "git log failed: " + r.stderr.strip()[-160:]
    rows = [l.split() for l in r.stdout.splitlines() if l.strip()]
    if not rows:
        return False, False, "no commit to the v3 config before the week's end"
    sha, ct = rows[0][0], int(rows[0][1])
    sched = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (sha, paths[0])], capture_output=True, text=True, timeout=60)
    try:
        roles = [x["name"] for x in json.loads(sched.stdout).get("roles", []) if x.get("enabled")]
    except Exception:
        roles = []
    live = bool(roles) or not rules["settled"]["need_role_enabled"]
    quiet = (lo - ct) / DAY
    ok = live and quiet >= rules["settled"]["quiet_days"]
    why = "last v3 config commit %s at %s (%.1f d before the window); roles enabled then: %s" % (
        sha[:10], time.strftime("%Y-%m-%d %H:%M", time.localtime(ct)), quiet, ", ".join(roles) or "none")
    return ok, live, why


# ---------------------------------------------------------------- counterfactual
def counterfactual(day, week, v2, rules, timeout=480):
    """Run the simulator's counterfactual for this week; -> its result dict or an UNMEASURED one."""
    d = out_dir()
    inp = os.path.join(d, "cf_input_%s.json" % day)
    json.dump({"day": day, "week": week, "v2": v2, "reference_week": rules["v2_history"]["reference_week"],
               "rules": rules["counterfactual"]}, open(inp, "w"), default=str)
    dst = os.path.join(d, "counterfactual_%s.json" % day)
    try:
        r = subprocess.run([sys.executable, SIM, "counterfactual", "--input", inp, "--dst", dst],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "UNMEASURED", "why": "the simulator ran past %d s" % timeout}
    if r.returncode != 0 or not os.path.exists(dst):
        return {"status": "UNMEASURED", "why": "simulator exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:])}
    return json.load(open(dst))


# ---------------------------------------------------------------- output
def fmt(v, group=True):
    """group=False for the blind page: a grouped figure (45,000) is refused by contracts.blind.page_problem."""
    if v is None:
        return "-"
    if isinstance(v, float):
        return ("%.3f" % v) if abs(v) < 10 else ("{:,.0f}" if group else "{:.0f}").format(v)
    return ("{:,}" if group else "{}").format(v)


# The Auditor's page: quality metrics only, under labels that pass the blind type's word rules (contracts.blind_core:
# "week", "wk", "share" and "pct" are token words, so the page says "period" and "fraction"); the selftest holds
# contracts.blind.page_problem(page) is None.
BLIND_LABELS = {"done_wk": "items done", "owner_wait_over_3d": "owner waits open over 3 days",
                "already_ruled_wk": "owner messages saying already ruled", "rework_share": "rework fraction of items filed",
                "close_no_level_share": "closes with no verify level, fraction", "verify_backlog": "verify backlog",
                "process_share": "process-only commits, fraction", "doing_live_lease_share": "doing items with a live lease, fraction",
                "lapsed_open": "open items with a lapsed lease", "contested_new_wk": "new contested claims",
                "filed_wk": "items filed", "owner_resolve_med_d": "owner wait resolved, median days",
                "vfail_share": "verify fails, fraction", "owner_msgs_wk": "owner messages", "owner_active_h_wk": "owner active hours"}
BLIND_KEYS = tuple(BLIND_LABELS)


def _blind_text(t):
    return re.sub(r"(?i)\bweeks?\b", lambda m: "periods" if m.group(0).lower().endswith("s") else "period", t or "")


def render(rec, ref, rules, blind=False):
    j = rec["judge"]
    L = []
    if blind:
        L.append("# v3 vs v2, quality half, seven days ending %s 07:00 local (for the Auditor)" % rec["end"])
        L.append("")
        L.append("Quality metrics only. Re-check each one against the ledger yourself and write what you find on the "
                 "parent item; this page carries no resource figure on purpose.")
    else:
        L.append("# v3 vs v2, week ending %s 07:00 local (for Operations)" % rec["end"])
        L.append("")
        L.append("**Week: %s, cost %s (token use %s x the v2 tag week)%s.** Standing: **%s** (rule reading %s over %s)." % (
            j["verdict"], j["cost"], fmt(j["ite_ratio_to_v2"]), "" if rec["settled"] else ", PROVISIONAL (not settled)",
            rec["standing"]["standing"], rec["standing"]["rule_reading"], ", ".join(rec["standing"]["weeks"]) or "no settled week"))
        L.append("")
        L.append("- settled: %s; %s" % (rec["settled"], rec["settled_why"]))
        L.append("- %s" % rec["rules"])
        cf = rec.get("counterfactual") or {}
        L.append("- counterfactual: %s%s" % (cf.get("status", "not run"), (": " + cf["why"]) if cf.get("why") else ""))
    L.append("")
    L.append("| metric | group | v3 week | mark | v2 tag week | v2 earlier weeks | class | bands | counterfactual v2 range |"
             if not blind else "| metric | group | v3 | mark | v2 at the tag | v2 earlier | class | bands | counterfactual v2 range |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    cfr = (rec.get("counterfactual") or {}).get("range") or {}
    for m in rules["metrics"]:
        k = m["key"]
        if blind and k not in BLIND_KEYS:
            continue
        p = rec["week"].get(k) or {}
        r = ref.get(k) or {}
        pj = j["per"][k]
        cls = pj["class"] + (" -> " + pj["class_cf"] if pj.get("class_cf") else "")
        rng = cfr.get(k) if not blind or k in BLIND_KEYS else None
        g = not blind
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            BLIND_LABELS[k] if blind else k, m["group"], fmt(p.get("v"), g), p.get("mark", "-"), fmt(r.get("value"), g),
            ", ".join(fmt(c, g) for c in r.get("context") or []) or "-", cls,
            fmt(pj["bands"], g), "-" if not rng else "%s .. %s" % (fmt(rng[0], g), fmt(rng[1], g))))
    L.append("")
    un = [(k, (rec["week"].get(k) or {}).get("why")) for k in rec["week"]
          if (rec["week"].get(k) or {}).get("mark") == "UNMEASURED" and (not blind or k in BLIND_KEYS)]
    if un:
        L.append("Unmeasured (never zero): " + "; ".join(
            ("%s: %s" % (BLIND_LABELS[k], _blind_text(w))) if blind else ("%s: %s" % (k, w)) for k, w in un))
        L.append("")
    if not blind:
        L.append("Rule (pre-registered, %s): %s Standing: %s" % (rules["registered_utc"], rules["verdict"]["_why"],
                                                              rules["standing"]["_why"]))
    return "\n".join(L) + "\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


# ---------------------------------------------------------------- commands
def v2_path():
    return os.path.join(out_dir(), "v2_weeks.json")


def cmd_baseline(a, rules):
    """measure the tag week, the context weeks, and the tag week's 7 days (the noise band) -> v2_weeks.json"""
    H = rules["v2_history"]
    weeks = [H["reference_week"]] + list(H["context_weeks"])
    t0 = time.time()
    hi = week_end(H["reference_week"], rules)
    dwins = [(hi - (WEEK_DAYS - i) * DAY, hi - (WEEK_DAYS - i - 1) * DAY) for i in range(WEEK_DAYS)]
    wwins = [(week_end(d, rules) - WEEK_DAYS * DAY, week_end(d, rules)) for d in weeks]
    got = measure_windows(wwins + dwins, rules)
    v2 = {"rules_sha256": rules_sha(), "measured_utc": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
          "weeks": dict(zip(weeks, got[:len(weeks)])), "days": got[len(weeks):]}
    write(v2_path(), json.dumps(v2, indent=1))
    ref = reference(v2, rules)
    for m in rules["metrics"]:
        k = m["key"]
        r = ref[k]
        print("%-24s tag %12s  earlier %s  band %s (%s)" % (k, fmt(r["value"]), " ".join("%12s" % fmt(c) for c in r["context"]),
                                                          fmt(r["band"]), r.get("band_from", r.get("why"))))
    print("v2 weeks %s + 7 days -> %s (%.0f s)" % (", ".join(weeks), v2_path(), time.time() - t0))
    return 0


def cmd_run(a, rules):
    ok, rtxt = rules_status()
    if not ok:
        print(rtxt)
        write(os.path.join(out_dir(), "verdict.md"), "# v3 vs v2: NOT JUDGED\n\n" + rtxt + "\n")
        return 2
    if not os.path.exists(v2_path()):
        cmd_baseline(a, rules)
    v2 = json.load(open(v2_path()))
    if v2.get("rules_sha256") != rules_sha():
        print("v2_weeks.json was measured under another rule text; re-measuring")
        cmd_baseline(a, rules)
        v2 = json.load(open(v2_path()))
    ref = reference(v2, rules)
    day = a.end or last_week_end(time.time(), rules)
    hi = week_end(day, rules)
    lo = hi - WEEK_DAYS * DAY
    week = measure_weeks([day], rules)[day]
    st, live, why = settled(lo, hi, rules)
    cf = None if a.no_counterfactual else counterfactual(day, week, v2["weeks"], rules)
    j = judge_week(week, ref, rules, cf)
    if not live:
        j["verdict"] = "NOT_V3"
    hist_p = os.path.join(out_dir(), "history.jsonl")
    hist = [json.loads(l) for l in open(hist_p)] if os.path.exists(hist_p) else []
    hist = [h for h in hist if h["end"] != day]
    row = {"end": day, "settled": st, "live": live, "verdict": j["verdict"], "cost": j["cost"],
           "ite_ratio_to_v2": j["ite_ratio_to_v2"], "rules_sha256": rules_sha()}
    hist = sorted(hist + [row], key=lambda h: h["end"])
    rec = {"end": day, "window": [lo, hi], "settled": st, "live": live, "settled_why": why, "rules": rtxt,
           "week": week, "judge": j, "counterfactual": cf, "standing": standing(hist, rules)}
    write(os.path.join(out_dir(), "weeks", day + ".json"), json.dumps(rec, indent=1, default=str))
    write(hist_p, "".join(json.dumps(h) + "\n" for h in hist))
    write(os.path.join(out_dir(), "verdict.md"), render(rec, ref, rules))
    write(os.path.join(out_dir(), "quality_blind.md"), render(rec, ref, rules, blind=True))
    print("week %s: %s, cost %s (x%s), settled %s, standing %s -> %s" % (
        day, j["verdict"], j["cost"], fmt(j["ite_ratio_to_v2"]), st, rec["standing"]["standing"], out_dir()))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("baseline")
    r = sub.add_parser("run")
    r.add_argument("--end", help="the Monday the week ends on, local date (default: the last one passed)")
    r.add_argument("--no-counterfactual", action="store_true")
    sub.add_parser("rules")
    a = ap.parse_args(argv)
    rules = load_rules()
    if a.cmd == "rules":
        ok, txt = rules_status()
        print(txt)
        return 0 if ok else 2
    return {"baseline": cmd_baseline, "run": cmd_run}[a.cmd](a, rules)


if __name__ == "__main__":
    sys.exit(main())
