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
    a = ap.parse_args(argv)
    fx = load()
    import list_dispatch as LD
    cfg = LD.load_cfg()
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
