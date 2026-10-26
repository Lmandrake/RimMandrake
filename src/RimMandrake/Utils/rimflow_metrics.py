#!/usr/bin/env python3
"""rimflow_metrics — flow, wait and heat numbers derived from the rimflow ledger (offline, read-only).

MONITORING_CONCEPTS_DESIGN_HALF_DRAWN, design/RimMandrake/monitoring_concepts_2026-10-25.md §D. The first
slice of "what should Rimflow monitor": every number here is a pure function of the ledger (plus `git log`
for commit heat), computed by folding the ledger once through `model.replay(observe=)` so the verbs are
never re-interpreted here.

    python3 src/RimMandrake/Utils/rimflow_metrics.py                 # last 14 days, text
    python3 src/RimMandrake/Utils/rimflow_metrics.py --days 7 --json
    python3 src/RimMandrake/Utils/rimflow_metrics.py --no-git        # ledger only

Rules this follows (design §A): unmeasured is printed as `--`, never 0; every report says AS OF which
ledger stamp it looked; a count of zero is printed with the population it was taken from.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import model  # noqa: E402

DAY = 86400.0
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
# Subjects that name a mod without spelling it. Kept tiny and explicit; everything else must spell the
# mod's folder name. The unmapped share is reported, because the ledger has no `mod` field (§0).
ALIASES = {"FW": "FlowWorks", "HOSE": "FlowWorks", "FLOWWORKS": "FlowWorks"}


# ------------------------------------------------------------------ timelines
def timelines(events):
    """-> (world, {iid: [(epoch, state, needs, blocked, owner)]}) — one row per projected CHANGE."""
    tl = {}

    def observe(ev, world, ok):
        if not ok:
            return
        iid = ev.get("name") if ev.get("event") == "spawn" else ev.get("id")
        it = world.items.get(iid) if iid else None
        if it is None:
            return
        row = (model.epoch(ev["ts"]), it.state, it.needs, bool(it.blocked), it.owner)
        rows = tl.setdefault(iid, [])
        if not rows or rows[-1][1:] != row[1:]:
            rows.append(row)

    world = model.replay(events, observe=observe)
    return world, tl


def first_at(rows, pred):
    for r in rows:
        if pred(r):
            return r[0]
    return None


def spans(rows, pred, end):
    """-> [(start, stop_or_None)] of the stretches where pred(row) held; stop None = still holding."""
    out, start = [], None
    for r in rows:
        if pred(r) and start is None:
            start = r[0]
        elif not pred(r) and start is not None:
            out.append((start, r[0]))
            start = None
    if start is not None:
        out.append((start, None))
    return out


def q(vals, p):
    """Nearest-rank percentile; None for an empty population (printed `--`)."""
    if not vals:
        return None
    s = sorted(vals)
    k = max(0, min(len(s) - 1, int(round(p / 100.0 * len(s) + 0.5)) - 1))
    return s[k]


def days(sec):
    return None if sec is None else round(sec / DAY, 2)


def summary(secs):
    return {"n": len(secs), "median_d": days(q(secs, 50)), "p90_d": days(q(secs, 90)),
            "max_d": days(max(secs) if secs else None)}


# ------------------------------------------------------------------ mods
def mod_names(repo=REPO):
    out = {}
    for tier in TIERS:
        d = os.path.join(repo, "src", tier)
        if not os.path.isdir(d):
            continue
        for m in os.listdir(d):
            if os.path.isfile(os.path.join(d, m, "About", "About.xml")):
                out[m] = tier
    return out


def item_mod(iid, title, mods):
    """-> mod folder name or None. Id tokens first (alias or exact), then the mod's name in the title."""
    norm = {m.upper(): m for m in mods}
    for tok in iid.split("_"):
        if tok in ALIASES and ALIASES[tok] in mods:
            return ALIASES[tok]
        if len(tok) >= 4 and tok in norm:
            return norm[tok]
    flat = iid.replace("_", "")
    for up, m in sorted(norm.items(), key=lambda kv: -len(kv[0])):
        if len(up) >= 6 and up in flat:
            return m
    t = title or ""
    for m in sorted(mods, key=len, reverse=True):
        if len(m) >= 5 and re.search(r"\b%s\b" % re.escape(m), t):
            return m
    return None


def git_heat(since_epoch, mods, repo=REPO):
    """-> {"commits": n, "mods": Counter(mod -> commits touching it), "design": Counter} or None (no git)."""
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since_epoch))
    try:
        out = subprocess.run(["git", "-C", repo, "log", "--since=" + since, "--no-merges",
                              "--name-only", "--format=@@%H"], capture_output=True, text=True,
                             timeout=120, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    commits, mc, dc, cur = 0, collections.Counter(), collections.Counter(), None
    ledger_only = 0
    touched_m, touched_d, paths = set(), set(), []

    def flush():
        nonlocal ledger_only
        if cur is None:
            return
        mc.update(touched_m)
        dc.update(touched_d)
        if paths and all(p.startswith("infrastructure/state/ledger/") for p in paths):
            ledger_only += 1

    for line in out.splitlines():
        if line.startswith("@@"):
            flush()
            cur, commits = line[2:], commits + 1
            touched_m, touched_d, paths = set(), set(), []
            continue
        p = line.strip()
        if not p:
            continue
        paths.append(p)
        parts = p.split("/")
        if len(parts) >= 3 and parts[0] == "src" and parts[1] in TIERS and parts[2] in mods:
            touched_m.add(parts[2])
        elif len(parts) >= 2 and parts[0] == "design":
            touched_d.add(parts[1] if len(parts) > 2 else "(top)")
    flush()
    return {"commits": commits, "ledger_only": ledger_only, "mods": mc, "design": dc}


# ------------------------------------------------------------------ the metrics
def compute(events, now=None, window_days=14, mods=None, heat=None):
    world, tl = timelines(events)
    now = now if now is not None else time.time()
    lo = now - window_days * DAY
    inw = [e for e in events if (model.epoch(e["ts"]) or 0) >= lo]
    items = world.items
    mods = mods if mods is not None else {}
    r = {"as_of_ledger": events[-1]["ts"] if events else None, "window_days": window_days,
         "events_total": len(events), "events_window": len(inw), "items_total": len(items)}

    # 1. flow
    flow = collections.Counter()
    for e in inw:
        if e["event"] in ("file", "spawn"):
            flow["filed"] += 1
    for iid, rows in tl.items():
        for (t, st, *_), prev in zip(rows[1:], rows[:-1]):
            if t >= lo and st != prev[1] and st in model.TERMINAL:
                flow[st] += 1
    r["flow"] = dict(flow, net=flow["filed"] - flow["done"] - flow["dropped"] - flow["superseded"])

    # 2-4. lead / cycle / ready-wait / acceptance, for items reaching done in window
    lead, cyc, qwait, accept, nostart, receipts = [], [], [], [], 0, 0
    lead_by_kind = collections.defaultdict(list)
    for iid, rows in tl.items():
        done = first_at(rows, lambda x: x[1] == "done")
        if done is None or done < lo:
            continue
        born = rows[0][0]
        lead.append(done - born)
        if done - born <= 300:
            receipts += 1
        lead_by_kind[items[iid].kind or "?"].append(done - born)
        d0 = first_at(rows, lambda x: x[1] == "doing")
        if d0 is not None and d0 <= done:
            cyc.append(done - d0)
            qwait.append(d0 - born)
        else:
            nostart += 1
        b0 = first_at(rows, lambda x: x[1] == "built")
        if b0 is not None and b0 <= done:
            accept.append(done - b0)
    r["lead"] = summary(lead)
    r["lead_by_kind"] = {k: summary(v) for k, v in sorted(lead_by_kind.items())}
    r["cycle"] = summary(cyc)
    r["queue_wait"] = summary(qwait)
    r["done_never_started"] = nostart
    r["done_within_5min_of_filing"] = receipts
    r["acceptance"] = summary(accept)

    # 5. WIP age (time in current state), open items
    wip = collections.defaultdict(list)
    for iid, it in items.items():
        if it.open and tl.get(iid):
            # age in state = now - first row of the trailing run in this state
            run = tl[iid]
            k = len(run) - 1
            while k > 0 and run[k - 1][1] == it.state:
                k -= 1
            wip[it.state].append(now - run[k][0])
    r["wip"] = {s: dict(summary(v), over_7d=sum(1 for x in v if x > 7 * DAY))
                for s, v in sorted(wip.items())}

    # 6. owner wait
    cur_wait, done_wait = [], []
    for iid, rows in tl.items():
        for a, b in spans(rows, lambda x: x[2] == "owner", now):
            if b is None:
                if items[iid].open:
                    cur_wait.append(now - a)
            elif b >= lo:
                done_wait.append(b - a)
    r["owner_wait_open"] = dict(summary(cur_wait), over_3d=sum(1 for x in cur_wait if x > 3 * DAY))
    r["owner_wait_resolved"] = summary(done_wait)

    # 7. verify backlog + 8. verify results
    vb, lv = [], collections.Counter()
    for it in items.values():
        if it.state in ("built", "validated"):
            if it.built_at:
                vb.append(now - model.epoch(it.built_at))
            for L in it.owed_levels():
                lv[L] += 1
    r["verify_backlog"] = dict(summary(vb), owed_levels=dict(sorted(lv.items())))
    vr = collections.Counter(e["result"] for e in inw if e["event"] == "verify")
    r["verify_results"] = dict(vr)

    # 9. rework: follow-ups filed in window whose cause is already closed
    fu, fu_closed = 0, 0
    filed_w = 0
    for e in inw:
        if e["event"] not in ("file", "spawn"):
            continue
        filed_w += 1
        cb = e.get("caused_by") or (e.get("from") if e["event"] == "spawn" else None)
        if cb:
            fu += 1
            if cb in items and items[cb].state == "done":
                fu_closed += 1
    r["rework"] = {"filed": filed_w, "with_cause": fu, "cause_already_done": fu_closed}

    # 10. leases
    lease = collections.Counter()
    takes = collections.Counter()
    for e in inw:
        if e["event"] == "lease":
            lease[e["action"]] += 1
            if e["action"] == "take":
                takes[e["id"]] += 1
    lapsed = sum(1 for it in items.values() if model.lease_status(it, now) == "lapsed" and it.open)
    r["leases"] = dict(lease, items_taken=len(takes), items_3plus_takes=sum(1 for v in takes.values() if v >= 3),
                       open_items_lapsed_now=lapsed,
                       top=[[k, v] for k, v in takes.most_common(3)])
    r["contested_claims_total"] = len(world.contested_claims)
    r["reclaims_window"] = sum(1 for e in inw if e["event"] == "reclaim")

    # 11. bounce: needs/reassign/retarget per item in window
    bounce = collections.Counter(e["id"] for e in inw if e["event"] in ("needs", "reassign", "retarget"))
    r["bounce"] = {"items": len(bounce), "items_3plus": sum(1 for v in bounce.values() if v >= 3),
                   "top": [[k, v] for k, v in bounce.most_common(3)]}

    # 12. blocked
    bl = [it for it in items.values() if it.open and it.blocked]
    on = collections.Counter(it.blocked_on for it in bl if it.blocked_on)
    bage = []
    for it in bl:
        sp = spans(tl.get(it.id, []), lambda x: x[3], now)
        if sp and sp[-1][1] is None:
            bage.append(now - sp[-1][0])
    r["blocked"] = dict(summary(bage), top_blockers=[[k, v] for k, v in on.most_common(3)])

    # 13. notes (thrash)
    notes = collections.Counter(e["id"] for e in inw if e["event"] == "note" and e.get("id"))
    r["notes"] = {"window": sum(notes.values()), "items": len(notes),
                  "top": [[k, v] for k, v in notes.most_common(3)]}

    # 14. seats
    seat_ev = collections.Counter(e["seat"] for e in inw)
    hours = collections.defaultdict(set)
    for e in inw:
        hours[e["seat"]].add(e["ts"][:13])
    r["seats"] = {s: {"events": n, "active_hours": len(hours[s]),
                      "last_seen_h": round((now - model.epoch(world.last_seen[s])) / 3600.0, 1)}
                  for s, n in seat_ev.most_common()}

    # 15. bridge hold
    hold = collections.Counter()
    longest = [0.0, None]
    taken = {}
    for e in inw:
        if e["event"] != "bridge":
            continue
        host = e.get("host") or "default"
        t = model.epoch(e["ts"])
        if e["state"] == "taken":
            taken.setdefault(host, (e["seat"], t))
        elif host in taken:
            s, t0 = taken.pop(host)
            hold[s] += t - t0
            if t - t0 > longest[0]:
                longest[:] = [t - t0, s]
    for host, (s, t0) in taken.items():
        hold[s] += now - t0
    r["bridge_hold_h"] = {s: round(v / 3600.0, 1) for s, v in hold.most_common()}
    r["bridge_longest_hold"] = [round(longest[0] / 3600.0, 1), longest[1]]

    # 16. provenance on items filed in window
    prov = collections.Counter()
    for e in inw:
        if e["event"] in ("file", "spawn"):
            prov["ownerSaid" if e.get("ownerSaid") else "byCard" if e.get("byCard") else
                 "perRuling" if e.get("perRuling") else "why" if e.get("why") else "none"] += 1
    r["provenance_filed"] = dict(prov)

    # 17. mod heat (ledger)
    lh, unm, seen = collections.Counter(), 0, set()
    for e in inw:
        iid = e.get("name") if e["event"] == "spawn" else e.get("id")
        if not iid or iid in seen or iid not in items:
            continue
        seen.add(iid)
        m = item_mod(iid, items[iid].title, mods)
        if m:
            lh[m] += 1
        else:
            unm += 1
    r["mod_heat_ledger"] = {"items_touched": len(seen), "unmapped": unm,
                            "top": [[k, v] for k, v in lh.most_common(8)]}
    subj = collections.Counter(i.split("_")[0] for i in seen)
    r["subjects_top"] = [[k, v] for k, v in subj.most_common(8)]

    # 18. mod heat (git)
    if heat is not None:
        r["mod_heat_git"] = {"commits": heat["commits"], "ledger_only": heat["ledger_only"],
                             "mods_touched": len(heat["mods"]),
                             "top": [[k, v] for k, v in heat["mods"].most_common(8)],
                             "design_top": [[k, v] for k, v in heat["design"].most_common(5)]}
        cold = sorted(m for m in mods if m not in heat["mods"])
        r["mod_heat_git"]["cold_mods"] = len(cold)

    # 19. instrument health
    r["instrument"] = {"replay_refusals": len(world.errors), "tolerated_fields": len(world.tolerated),
                       "events_without_tsn": sum(1 for e in events if "tsn" not in e)}
    return r


def fmt(v):
    return "--" if v is None else v


def render(r):
    out = ["rimflow metrics, window %sd, AS OF ledger %s (%s events, %s in window, %s items)"
           % (r["window_days"], r["as_of_ledger"], r["events_total"], r["events_window"], r["items_total"])]
    for k, v in r.items():
        if k in ("window_days", "as_of_ledger", "events_total", "events_window", "items_total"):
            continue
        out.append("%-22s %s" % (k, json.dumps(v, default=fmt)))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=float, default=14)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args(argv)
    events = model.read()
    now = time.time()
    mods = mod_names()
    heat = None if a.no_git else git_heat(now - a.days * DAY, mods)
    r = compute(events, now=now, window_days=a.days, mods=mods, heat=heat)
    r["mods_known"] = len(mods)
    print(json.dumps(r, indent=1, default=str) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
