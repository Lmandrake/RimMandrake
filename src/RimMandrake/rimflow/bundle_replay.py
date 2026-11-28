#!/usr/bin/env python3
"""bundle_replay.py: replay real ticket arrivals through the real bundling code with a fake clock. No model, no tokens.

Item RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY; page design/specs/2026-11-24-work-bundles/boundary.md
(the offline simulation of a-home-holds-until-five-or-the-hold-time); selftest selftest_bundle_hold.py.

    python3 src/RimMandrake/rimflow/bundle_replay.py                    the replay at list_dispatch.json's hold
    python3 src/RimMandrake/rimflow/bundle_replay.py --sweep            the median per hold, 0 to 24 h
    python3 src/RimMandrake/rimflow/bundle_replay.py --parent           the parent's form: no hold, no reader home

The arrivals are ARRIVALS: each ticket that a lane bundle took from 2026-11-23 to 27 (the Archmagi store, SteveDesktop's
markers included) and each fresh-reader ticket filed then; a ticket's arrival is its filing, or its first launch when it
was filed before. Each tick (TICK_S) the ready tickets become one launch row each; work_bundle.system_of gives each its
system, work_bundle.group makes the bundles, work_bundle.hold_systems holds the small ones, and a launched bundle holds
its system for the fixture's bundle_s (the median measured run). At most ROOM bundles run at once (list_dispatch.json
max_live 2 and SteveDesktop's 6). What it does not model: restarts, a run's own closes, the checks (each arrival is
ready), the onboarding route's old-ticket filter.

    python3 src/RimMandrake/rimflow/bundle_replay.py --live [--rule R] [--sweep] [--with-review] [--day D]
                                                                        the live routes (replay_live), each rule of RULES
    python3 src/RimMandrake/rimflow/bundle_replay.py --lane --day D     the live lane's own figures (ticks.jsonl)

replay_live models what replay does not: the Shape route (a ticket with no check is unseen until shape_grace_h, then a
Shape row that is never held), the onboarding route (old tickets of a pipeline: or machine: home in one run that reads no
hold), a filer that closes or claims its ticket first, and switches for the code review and game work pauses.
"""
import argparse
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ARRIVALS = os.path.join(REPO, "design", "specs", "2026-11-24-work-bundles", "arrivals_2026-11-23_to_27.json")
TICK_S = 600        # the lane's timer beat (rm-list-dispatch.timer, every 10 min)
ROOM = 8            # list_dispatch.json max_live 2 + hosts.SteveDesktop.max_live 6


def load(path=ARRIVALS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _day(t):
    import datetime
    from zoneinfo import ZoneInfo
    return datetime.datetime.fromtimestamp(t, ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")


def replay(fx, hold_s, full_n=5, reader_home=True, urgent_rule=True, room=ROOM, tick_s=TICK_S, extra=()):
    """-> {"bundles": [{system, members, at, waits}], "urgent": [(id, waited_s)], ...}. fx: the fixture; extra: more
    arrivals (a test plants one). reader_home False: the parent's form, a reader ticket keyed on its own id."""
    import work_bundle as WB
    arr = sorted(list(fx["arrivals"]) + list(extra), key=lambda a: (a["filed"], a["id"]))
    by_id = {a["id"]: a for a in arr}
    items = {a["id"]: {"id": a["id"], "title": a["title"], "home": {"home": a["home"]} if a.get("home") else None,
                       "caused_by": a.get("caused_by")} for a in arr}
    for a in arr:       # the parent's home, as the ledger held it
        if a.get("caused_by") and a["caused_by"] not in items:
            items[a["caused_by"]] = {"id": a["caused_by"], "title": "", "home": {"home": a["parent_home"]}
                                     if a.get("parent_home") else None, "caused_by": None}
    reading = lambda it: {"mod": None}      # noqa: E731 - the fixture holds lane tickets only (no mod's work)

    def system(i):
        if reader_home:
            return WB.system_of(items[i], reading, items)
        import list_home as LH
        keep = LH.reader_home
        LH.reader_home = lambda it: None
        try:
            return WB.system_of(items[i], reading, items)
        finally:
            LH.reader_home = keep
    systems = {i: system(i) for i in by_id}
    urgent = {i: WB.urgent_why(i, None, {}) for i in by_id} if urgent_rule else {}
    urgent.update({a["id"]: a["urgent"] for a in extra if a.get("urgent") and urgent_rule})
    urgent = {i: w for i, w in urgent.items() if w}
    t = arr[0]["filed"] - arr[0]["filed"] % tick_s
    end = arr[-1]["filed"] + 2 * 86400
    k, ready, live, out, urg, held_s = 0, {}, {}, [], [], {}
    while t <= end and (k < len(arr) or ready):
        while k < len(arr) and arr[k]["filed"] <= t:
            ready[arr[k]["id"]] = arr[k]["filed"]
            k += 1
        for s in [s for s, e in live.items() if e <= t]:
            live.pop(s)
        free = room - len(live)
        rows = []
        for i in sorted(ready, key=lambda i: (0 if i in urgent else 1, ready[i], i)):
            s = systems[i]
            if s in live:
                continue
            got = any(r["decision"] == "launch" and systems[r["item"]] == s for r in rows)
            rows.append({"item": i, "decision": "launch" if got or free > 0 else "slots_full"})
            if not got and free > 0:
                free -= 1
        rows, _l = WB.group(rows, [r["item"] for r in rows if r["decision"] == "launch"], systems, dict.fromkeys(live, "WB"))
        since = dict(ready)     # a wait counts from the first ready tick, a wait under a live bundle included
        held = WB.hold_systems(rows, since, urgent, t, hold_s, full_n)
        for i in ready:
            if systems[i] in held:
                held_s[i] = held_s.get(i, 0) + tick_s     # this tick it waits for the hold, not for room
        for r in rows:
            b = r.get("bundle")
            if not b or b["system"] in held:
                continue
            mem = b["members"]
            out.append({"system": b["system"], "members": mem, "at": t, "waits": [t - since[m] for m in mem]})
            urg += [(m, t - ready[m]) for m in mem if m in urgent]
            for m in mem:
                ready.pop(m, None)
            live[b["system"]] = t + fx["bundle_s"]
        t += tick_s
    return {"bundles": out, "urgent": urg, "systems": systems, "held_s": held_s}


# ---- the live routes (item RIMMANDRAKE_BUNDLE_SHAPE_ROWS_BY_HOME_HOLD_HELD_NOTHING) -------------------------------------
# The replay above makes each arrival ready at its filing and holds every bundle. The live lane does not: a ticket with
# no check is unseen until shape_grace_h after its filing, then it is a Shape run that is never held; an old ticket of a
# pipeline: or machine: home starts in that home's onboarding run, which reads no hold; an old ticket of a cause: or
# item: home starts only as a Shape run of its own. replay_live models those routes over LIVE_ARRIVALS, which
# build_live made from the ledger (each ticket filed 2026-11-23 to 27 PST, with the times of its check, route, claim,
# home and close) and the lane's own records (which tickets a lane launch took).

LIVE_ARRIVALS = os.path.join(REPO, "design", "specs", "2026-11-24-work-bundles", "arrivals_live_2026-11-23_to_27.json")
GRACE_S = 24 * 3600     # list_dispatch.json shape_grace_h, as it read 2026-11-23 to 27
FILER_S = 600           # a claim or close this soon after the ticket is ready is its filer's own work: the lane tick is
                        # every 10 min, so no lane launch claims a ticket sooner
RULES = {
    # the code of 2026-11-27 (ed14a18611): Shape rows never held, each alone outside an on home; onboarding reads no hold;
    # an item: bundle is held too
    "live": dict(shape_group=False, hold_routes=False, hold_item=True, cause_onboard=False),
    # an item: home never gains company: it is not held (the hold only delays it)
    "no_item_hold": dict(shape_group=False, hold_routes=False, hold_item=False, cause_onboard=False),
    # the Shape rows of one home (any but item:) in one tick start as one run, and the hold applies to them and to an
    # onboarding run
    "shape_by_home": dict(shape_group=True, hold_routes=True, hold_item=False, cause_onboard=False),
    # shape_by_home, and a cause: home onboards its old tickets like a pipeline: home
    "shape_by_home_cause": dict(shape_group=True, hold_routes=True, hold_item=False, cause_onboard=True),
    # Shape rows grouped by home, no hold on them (the hold stays on the check route only)
    "shape_by_home_nohold": dict(shape_group=True, hold_routes=False, hold_item=False, cause_onboard=False),
}


def _lane_dir():
    import doorbell     # the dispatcher state root, as list_dispatch.sdir and work_bundle.store_dir read it
    return doorbell.state_dir()


def build_live(out=LIVE_ARRIVALS, root=REPO, lane_dir=None, t0="2026-11-23T08:00:00Z", t1="2026-11-28T08:00:00Z"):
    """Write LIVE_ARRIVALS from the ledger of `root` and the lane's records (ticks.jsonl and the bundle store of the
    dispatcher state). Run once; the file is frozen. -> the count written."""
    import glob
    import list_effect as LE
    import list_shape as LS
    import mod_work as MW
    import model as LM
    import work_bundle as WB
    T0, T1 = LM.epoch(t0), LM.epoch(t1)
    facts, home_at = {}, {}
    closed = ("done", "dropped", "superseded")

    def obs(ev, w, ok):
        iid = ev.get("id")
        if not ok or not iid or iid not in w.items:
            return
        it = w.items[iid]
        ts = LM.epoch(ev["ts"]) if ev.get("ts") else None
        if iid not in home_at and WB._home(it):
            home_at[iid] = ts
        f = facts.get(iid)
        if f is None:
            c = LM.epoch(it.created_at) if it.created_at else None
            if c is None or not (T0 <= c < T1):
                return
            f = facts[iid] = {"id": iid, "filed": c, "window": not ev.get("role_unit"), "check_at": None,
                              "route_at": None, "claim_at": None, "closed_at": None}
        sf = LS.facts(it)
        if f["claim_at"] is None and ev.get("event") in ("claim", "start", "lease"):
            f["claim_at"] = ts
        if f["check_at"] is None and LS._text(sf.get("effect")):
            f["check_at"] = ts
        if f["route_at"] is None and (sf.get("route") or LS.shaped(sf.get("parts"))["shaped"]):
            f["route_at"] = ts
        if it.state in closed and f["closed_at"] is None:
            f["closed_at"] = ts
        elif it.state not in closed:
            f["closed_at"] = None
    w = LE._world(observe=obs)
    lane_dir = lane_dir or _lane_dir()
    taken = set()
    with open(os.path.join(lane_dir, "list_dispatch", "ticks.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            taken.update(x["item"] for x in (json.loads(ln).get("launched") or []))
    for p in glob.glob(os.path.join(lane_dir, "work_bundle", "bundles", "*.json")):
        with open(p, encoding="utf-8") as fh:
            b = json.load(fh)
        if b.get("pipeline") == "workshop":
            taken.update(b.get("members") or [])
    mods = MW.mods()
    out_rows = []
    for iid, f in facts.items():
        it = w.items[iid]
        r = MW.reading(it, mods, LM.ITEMS)
        p = it.caused_by
        f.update(title=it.title, home=WB._home(it), home_at=home_at.get(iid), caused_by=p,
                 parent_home=WB._home(w.items[p]) if p in w.items else None, parent_home_at=home_at.get(p),
                 mod=(r.get("mod") if isinstance(r, dict) else None), lane_taken=iid in taken, old=False)
        out_rows.append(f)
    have = {f["id"] for f in out_rows}
    for a in load()["arrivals"]:     # the old tickets that lane bundles took in those days (filed before T0)
        if a["id"] not in have and a.get("onboard"):
            out_rows.append({"id": a["id"], "filed": a["filed"], "window": None, "check_at": None, "route_at": None,
                             "claim_at": None, "closed_at": None, "title": a["title"], "home": a.get("home"),
                             "home_at": 0, "caused_by": a.get("caused_by"), "parent_home": a.get("parent_home"),
                             "parent_home_at": 0, "mod": None, "lane_taken": True, "old": True})
    out_rows.sort(key=lambda f: (f["filed"], f["id"]))
    import subprocess
    head = subprocess.run(["git", "-C", root, "rev-parse", "--short=10", "HEAD"], capture_output=True, text=True,
                          timeout=60).stdout.strip() or "UNMEASURED"     # hang guard: rev-parse runs in under 1 s
    doc = ("The arrivals of the ticket lane for bundle_replay.replay_live: each ticket filed %s to %s (the ledger at %s), "
           "with the times of its first check, route, claim and close, its home and its parent's home with the time "
           "each was first set, its mod (mod_work), whether a lane launch took it (ticks.jsonl, the bundle store), and "
           "whether a window filed it (no role_unit); lane: the live lane's own figures of each day without the code "
           "review tickets (live_lane); plus each old ticket of arrivals_2026-11-23_to_27.json that an "
           "onboarding run took (old, filed: its first launch). Made by bundle_replay.py build-live for item "
           "RIMMANDRAKE_BUNDLE_SHAPE_ROWS_BY_HOME_HOLD_HELD_NOTHING; frozen." % (t0, t1, head))
    with open(out, "w", encoding="utf-8") as fh:
        lane = {d: live_lane(d, lane_dir) for d in ("2026-11-25", "2026-11-26", "2026-11-27")}
        json.dump({"_doc": doc, "bundle_s": load()["bundle_s"], "arrivals": out_rows, "lane": lane}, fh, indent=0,
                  sort_keys=True)
        fh.write("\n")
    return len(out_rows)


def review_rx():
    import re
    import list_dispatch as LD
    pats = ((LD.load_cfg().get("code_review_pause") or {}).get("id_patterns")) or []
    rx = [re.compile(p) for p in pats]
    return lambda i: any(r.match(i) for r in rx)


def live_route(a, grace_s=GRACE_S, shape_from=None):
    """-> (route, ready time) or (None, why) for one live arrival: "old" (an onboarding member at its first launch),
    "check" (a check attached before Shape was due: a lane launch row from then), "shape" (no check at shape_grace_h:
    a Shape row from then). A ticket that its filer claimed or closed first, or that was routed first, never reaches the
    lane, unless a lane launch took it."""
    if a.get("old"):
        return "old", a["filed"]
    due = a["filed"] + grace_s
    ck = a.get("check_at")
    if ck is not None and ck < due:
        route, t = "check", max(a["filed"], ck)
    elif shape_from is not None and a["filed"] < shape_from:
        return None, "filed before shape_from and never checked"
    else:
        route, t = "shape", due
    if not a.get("lane_taken"):
        for k in ("claim_at", "closed_at", "route_at"):
            v = a.get(k)
            if v is not None and v <= t + FILER_S:
                return None, "its %s came first" % k
    return route, t


def replay_live(fx, hold_s, full_n=5, rule="live", review=False, game=False, room=ROOM, tick_s=TICK_S, extra=(),
                grace_s=GRACE_S, urgent_rule=True, rules=None):
    """-> {"bundles": [{system, members, at, waits, route}], "urgent", "systems", "held_s", "routes"} over the live
    arrivals `fx` (LIVE_ARRIVALS form) under one rule of RULES (or `rules`, a dict of its four switches). review False
    leaves out the code review tickets (the pause of 2026-11-27); game False leaves out game: homes (the game work
    pause) and every arrival is lane work only (a mod: arrival is the Maturation Pipeline's). extra: more arrivals (a
    test plants them; a key "urgent" marks one)."""
    import work_bundle as WB
    R = dict(RULES[rule] if rules is None else rules)
    is_rev = review_rx()
    arr = sorted(list(fx["arrivals"]) + list(extra), key=lambda a: (a["filed"], a["id"]))
    routes, ready_at = {}, {}
    for a in arr:
        if a.get("mod") or (not review and is_rev(a["id"])):
            continue
        r, t = live_route(a, grace_s)
        if r:
            routes[a["id"]], ready_at[a["id"]] = r, t
    by_id = {a["id"]: a for a in arr}

    def system(i, at):
        a = by_id[i]
        it = {"id": i, "title": a.get("title") or "",
              "home": {"home": a["home"]} if a.get("home") and (a.get("home_at") or 0) <= at else None,
              "caused_by": a.get("caused_by")}
        items = {}
        if a.get("caused_by"):
            ph = a.get("parent_home") if (a.get("parent_home_at") or 0) <= at else None
            items[a["caused_by"]] = {"id": a["caused_by"], "title": "", "home": {"home": ph} if ph else None}
        return WB.system_of(it, lambda x: {"mod": None}, items)
    systems = {i: system(i, ready_at[i]) for i in routes}
    if not game:
        for i in [i for i, s in systems.items() if str(s).startswith("game:")]:
            routes.pop(i), ready_at.pop(i), systems.pop(i)
    urgent = {i: WB.urgent_why(i, None, {}) for i in routes} if urgent_rule else {}
    urgent.update({a["id"]: a["urgent"] for a in extra if a.get("urgent") and urgent_rule})
    urgent = {i: w for i, w in urgent.items() if w}
    order = sorted(routes, key=lambda i: (ready_at[i], i))
    if not order:
        return {"bundles": [], "urgent": [], "systems": systems, "held_s": {}, "routes": routes}
    t = ready_at[order[0]] - ready_at[order[0]] % tick_s
    end = ready_at[order[-1]] + 2 * 86400
    k, pend, live, out, urg, held_s = 0, {}, {}, [], [], {}
    on_classes = {"pipeline", "machine"} | ({"cause"} if R["cause_onboard"] else set())
    while t <= end and (k < len(order) or pend):
        while k < len(order) and ready_at[order[k]] <= t:
            pend[order[k]] = ready_at[order[k]]
            k += 1
        for i in [i for i in pend if not by_id[i].get("lane_taken") and by_id[i].get("closed_at") is not None
                  and by_id[i]["closed_at"] <= t]:
            pend.pop(i)     # its filer or another run closed it first
        for s in [s for s, e in live.items() if e <= t]:
            live.pop(s)
        # the candidate runs of this tick, one per (system, kind), before the room. kind: "check" (launch rows, grouped
        # and held), "onboard" (the home's old and Shape tickets; under the live rule a check lead of the home that
        # starts takes them, and a held lead leaves them to start alone), "shape" (Shape rows of one home grouped), or
        # "solo:<id>" (a Shape run of its own)
        cands = {}
        for i in sorted(pend, key=lambda i: (0 if i in urgent else 1, pend[i], i)):
            s, r = systems[i], routes[i]
            cls = str(s).partition(":")[0]
            if s in live:
                continue
            if r == "check":
                kind = "check"
            elif cls in on_classes:
                kind = "check" if R["hold_routes"] else "onboard"     # one bundle of the home, held as one
            elif r == "shape" and R["shape_group"] and cls != "item":
                kind = "shape"
            elif r == "shape":
                kind = "solo:" + i
            else:
                continue                   # an old ticket of a home that no onboarding run takes: it never starts
            c = cands.setdefault((s, kind), {"system": s, "members": [], "routes": set()})
            c["members"].append(i)
            c["routes"].add(r)
        free = room - len(live)
        started = {}

        def first(kv):
            return (0 if any(m in urgent for m in kv[1]["members"]) else 1, kv[0][1] == "onboard",
                    min(pend[m] for m in kv[1]["members"]), kv[0])
        for (s, kind), c in sorted(cands.items(), key=first):
            if kind.startswith("solo:"):
                held_ok = False
            elif kind == "check" and c["routes"] == {"check"}:
                held_ok = True
            else:
                held_ok = R["hold_routes"]
            if str(s).startswith("item:") and not R["hold_item"]:
                held_ok = False
            if kind == "onboard" and s in started:      # the home's check lead started: it takes them, no room
                b = started[s]
                b["members"] += c["members"]
                b["waits"] += [t - pend[m] for m in c["members"]]
                urg += [(m, t - ready_at[m]) for m in c["members"] if m in urgent]
                for m in c["members"]:
                    pend.pop(m, None)
                continue
            row = {"item": c["members"][0], "decision": "launch", "bundle": {"system": s, "members": c["members"]}}
            if held_ok and WB.hold_systems([row], pend, urgent, t, hold_s, full_n).get(s):
                for m in c["members"]:
                    held_s[m] = held_s.get(m, 0) + tick_s     # this tick it waits for the hold, not for room
                continue
            if free <= 0:
                continue
            free -= 1
            route = ("check" if "check" in c["routes"] else "onboard" if kind in ("onboard", "check") else "shape")
            b = {"system": s, "members": list(c["members"]), "at": t, "route": route,
                 "waits": [t - pend[m] for m in c["members"]]}
            out.append(b)
            started.setdefault(s, b)
            urg += [(m, t - ready_at[m]) for m in c["members"] if m in urgent]
            for m in c["members"]:
                pend.pop(m, None)
            if not kind.startswith("solo:"):
                live[s] = t + fx["bundle_s"]
        t += tick_s
    return {"bundles": out, "urgent": urg, "systems": systems, "held_s": held_s, "routes": routes}


def live_lane(day, lane_dir=None, review=False):
    """-> the live lane's own figures of one day: each launch of ticks.jsonl is one run, and its members are those of
    the lane bundle record that it led (else 1). review False leaves out the launches that a code review ticket led."""
    import glob
    lane_dir = lane_dir or _lane_dir()
    is_rev = review_rx()
    lead = {}
    for p in glob.glob(os.path.join(lane_dir, "work_bundle", "bundles", "*.json")):
        with open(p, encoding="utf-8") as fh:
            b = json.load(fh)
        if b.get("pipeline") == "workshop":
            lead.setdefault(b.get("lead"), []).append(b)
    out = []
    with open(os.path.join(lane_dir, "list_dispatch", "ticks.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            t = json.loads(ln)
            for x in t.get("launched") or []:
                if not review and is_rev(x["item"]):
                    continue
                c = [b for b in lead.get(x["item"], []) if abs((b.get("at") or 0) - t["at"]) < 1200]
                out.append({"system": c[0]["system"] if c else None, "members": c[0]["members"] if c else [x["item"]],
                            "at": t["at"], "waits": []})
    return day_figures({"bundles": out}, day)


def day_figures(res, day):
    b = [x for x in res["bundles"] if _day(x["at"]) == day]
    sizes = [len(x["members"]) for x in b]
    return {"day": day, "bundles": len(b), "median": statistics.median(sizes) if sizes else None,
            "singles": sum(1 for n in sizes if n == 1), "largest": max(sizes) if sizes else None,
            "longest_wait_h": round(max([w for x in b for w in x["waits"]] or [0]) / 3600.0, 2)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--parent", action="store_true")
    ap.add_argument("--day", default="2026-11-27")
    ap.add_argument("--live", action="store_true", help="the live routes over LIVE_ARRIVALS (replay_live)")
    ap.add_argument("--rule", default=None, help="one rule of RULES (default: each); with --live")
    ap.add_argument("--with-review", action="store_true", help="with --live: keep the code review tickets")
    ap.add_argument("--lane", action="store_true", help="the live lane's own figures of --day (ticks.jsonl)")
    ap.add_argument("--build-live", action="store_true", help="write LIVE_ARRIVALS from the ledger (once; frozen)")
    a = ap.parse_args(argv)
    import list_dispatch as LD
    cfg = LD.load_cfg()
    if a.build_live:
        print("wrote %d arrivals to %s" % (build_live(), LIVE_ARRIVALS))
        return 0
    if a.lane:
        print("live lane:", live_lane(a.day, review=a.with_review))
        return 0
    if a.live:
        fxl = load(LIVE_ARRIVALS)
        hold_s = float(cfg.get("bundle_hold_h") or 0) * 3600
        n = cfg.get("bundle_full_n", 5)
        for rule in ([a.rule] if a.rule else list(RULES)):
            for h in ((0, 3600, 7200, 4 * 3600, 6 * 3600, 8 * 3600, 12 * 3600) if a.sweep else (hold_s,)):
                res = replay_live(fxl, h, n, rule=rule, review=a.with_review)
                print("%-22s hold %4.1f h: %s; longest hold wait %.2f h" % (
                    rule, h / 3600.0, day_figures(res, a.day), max(res["held_s"].values() or [0]) / 3600.0))
        return 0
    fx = load()
    if a.sweep:
        for h in (0, 1, 2, 3, 4, 6, 8, 12, 16, 24):
            print("hold %2d h: %s" % (h, day_figures(replay(fx, h * 3600, cfg.get("bundle_full_n", 5)), a.day)))
        return 0
    if a.parent:
        res = replay(fx, 0, reader_home=False, urgent_rule=False)
    else:
        res = replay(fx, float(cfg.get("bundle_hold_h") or 0) * 3600, cfg.get("bundle_full_n", 5))
    print(day_figures(res, a.day))
    print("urgent tickets: %d, each started after %s s" % (len(res["urgent"]), [w for _i, w in res["urgent"]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
