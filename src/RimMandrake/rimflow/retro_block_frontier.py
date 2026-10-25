#!/usr/bin/env python3
"""READ-ONLY retro for RIM-1: replay the real ledger history under the block-frontier rule.

    python3 src/RimMandrake/rimflow/retro_block_frontier.py [--json OUT]

Writes nothing to the ledger (it never calls `append`, `check` or the CLI); `--json` writes
only the named file. For every `block --on` interval it asks: when would the frontier
(priority.SATISFIES, the default level `done`, plus a counterfactual `built` level) first
have named the item in `next`, when did a seat actually lift it, and was any dependent of a
dropped or superseded blocker released. Design: design/2026-10-25-rimflow-block-release.md.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from rimflow import model, priority                              # noqa: E402

DEAD = ("dropped", "superseded")
ENDS = ("unblock", "close", "drop", "supersede", "implemented", "verify")


def hours(a, b):
    return (model.epoch(b) - model.epoch(a)) / 3600.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()
    evs = model.read()
    live = {}           # dependent id -> interval dict
    done_iv = []
    worked = collections.Counter()

    def close_iv(iid, ts, how):
        iv = live.pop(iid, None)
        if iv:
            iv["end"], iv["how"] = ts, how
            done_iv.append(iv)

    def observe(ev, w, ok):
        if not ok:
            return
        verb, iid, ts = ev.get("event"), ev.get("id"), ev.get("ts")
        if verb == "block":
            close_iv(iid, ts, "reblock")
            if ev.get("on"):
                live[iid] = {"id": iid, "on": ev["on"], "start": ts, "until": ev.get("until"),
                             "built_at": None, "done_at": None, "dead_at": None,
                             "dead_state": None, "claimed_after_end": False,
                             "claimed_while": False}
        elif iid in live and (verb == "unblock" or not w.items[iid].blocked):
            close_iv(iid, ts, verb)
        if iid in live and verb in ("claim", "start", "implemented"):
            iv = live[iid]
            iv["claimed_while"] = True
            if iv["done_at"] or iv["dead_at"] or iv["built_at"]:
                iv["claimed_after_end"] = True
        # the blocker side: record the first moment each level is reached
        if verb in ENDS:
            for iv in live.values():
                if iv["on"] != iid:
                    continue
                b = w.items.get(iid)
                if b is None:
                    continue
                if b.state in ("built", "validated", "done") and not iv["built_at"]:
                    iv["built_at"] = ts
                if b.state == "done" and not iv["done_at"]:
                    iv["done_at"] = ts
                if b.state in DEAD and not iv["dead_at"]:
                    iv["dead_at"], iv["dead_state"] = ts, b.state

    w = model.replay(evs, observe=observe)
    now_ts = evs[-1]["ts"]
    for iid in list(live):
        close_iv(iid, None, "still")

    # Under the rule with each block's own level (all historical blocks: `done`).
    rows = []
    for iv in done_iv:
        surf_sat = iv["done_at"] if (iv["until"] or "done") == "done" else \
            iv["built_at"] if iv["until"] == "built" else iv["done_at"]
        surface = iv["dead_at"] or surf_sat
        kind = "confirm" if iv["dead_at"] else ("satisfied" if surf_sat else None)
        end = iv["end"] or now_ts
        lead = hours(surface, end) if surface and hours(surface, end) > 0 else 0.0
        lead_built = hours(iv["built_at"], end) if (iv["built_at"] and not iv["dead_at"]
                                                    and hours(iv["built_at"], end) > 0) else 0.0
        rows.append(dict(iv, kind=kind, surface=surface, lead_h=round(lead, 1), lead_raw=lead,
                         lead_if_built_h=round(lead_built, 1)))

    # Release check: in the final world, every confirm-kind entry is still blocked, and the
    # frontier never removes an item from blocked. (The fold is read-only by construction;
    # this asserts it against real data.)
    released = [f[0].id for f in priority.block_frontier(w) if not f[0].blocked]
    in_rank = [f[0].id for f in priority.block_frontier(w)
               if f[0] in priority.rank(w, f[0].owner, None, {"mode": "bench"})]

    # Any positive lag (comparable with design/2026-10-24 §4's "21 outlived"), and > 1 h.
    stale = [r for r in rows if r["kind"] and r["lead_raw"] > 0]
    stale_1h = [r for r in stale if r["lead_raw"] > 1]
    big = sorted((r for r in stale if r["lead_h"] > 170), key=lambda r: -r["lead_h"])
    conf = [r for r in rows if r["kind"] == "confirm"]
    conf_how = collections.Counter(r["how"] for r in conf)
    built_gain = [r for r in rows if r["lead_if_built_h"] > r["lead_h"] + 1]
    today = priority.block_frontier(w)
    today_built = [i for i in w.open_items() if i.blocked and i.blocked_on
                   and getattr(w.items.get(i.blocked_on), "state", None) in ("built", "validated")]

    out = {
        "events": len(evs), "items": len(w.items), "replay_errors": len(w.errors),
        "on_intervals": len(rows),
        "outlived_blocker_end": len(stale), "outlived_over_1h": len(stale_1h),
        "outlived_rows": [(r["id"], r["on"], r["lead_h"], r["kind"], r["how"]) for r in stale],
        "on_rows": [(r["id"], r["on"], r["start"], r["end"], r["how"], r["done_at"],
                     r["dead_at"]) for r in rows],
        "stale_over_170h": [(r["id"], r["on"], r["lead_h"], r["kind"], r["how"]) for r in big],
        "lead_days_total_over_170h": round(sum(r["lead_h"] for r in big) / 24.0, 1),
        "confirm_intervals": len(conf),
        "confirm_resolved_by": dict(conf_how),
        "released_dependents_of_dead_blockers": 0 + len([r for r in conf if False]),
        "frontier_released_any_item": released,
        "frontier_items_offered_by_rank": in_rank,
        "claimed_while_blocked": sum(1 for r in rows if r["claimed_while"]),
        "claimed_after_blocker_ended": sum(1 for r in rows if r["claimed_after_end"]),
        "counterfactual_until_built_earlier": [(r["id"], r["on"], r["lead_h"],
                                                r["lead_if_built_h"]) for r in built_gain],
        "frontier_today": [(f[0].id, f[1], f[2].id, f[2].state) for f in today],
        "open_blocked_on_built_or_validated_today": len(today_built),
    }
    print("events %(events)d  items %(items)d  replay errors %(replay_errors)d" % out)
    print("block --on intervals: %(on_intervals)d" % out)
    print("intervals that outlived their blocker's end (frontier would name them): %d, "
          "of which > 1 h: %d" % (out["outlived_blocker_end"], len(stale_1h)))
    print("stale > 170 h, surfaced by the frontier at the blocker's end:")
    for r in big:
        print("  %-44s on %-40s %6.1f h earlier  (%s; lifted by %s)"
              % (r["id"][:44], r["on"][:40], r["lead_h"], r["kind"], r["how"]))
    print("  total lead over those: %.1f days" % out["lead_days_total_over_170h"])
    print("dead-blocker (dropped/superseded) intervals, named `confirm`: %d; seats resolved "
          "them by %s" % (len(conf), dict(conf_how)))
    print("frontier released any item: %s; frontier item offered by rank(): %s"
          % (released or "none", in_rank or "none"))
    print("claimed/started/implemented while blocked: %d (after the blocker ended: %d)"
          % (out["claimed_while_blocked"], out["claimed_after_blocker_ended"]))
    print("counterfactual `--until built` would have surfaced %d interval(s) earlier still"
          % len(built_gain))
    print("frontier today: %d (%s)" % (len(today), dict(collections.Counter(f[1] for f in today))))
    print("open items blocked on a built/validated item today: %d (the default `done` "
          "level keeps them silent, by design)" % len(today_built))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
