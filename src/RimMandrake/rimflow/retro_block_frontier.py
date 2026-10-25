#!/usr/bin/env python3
"""READ-ONLY retro for RIM-1: replay the real ledger and run the REAL frontier rule
(`priority.frontier_entry`) after every replay step.

    python3 src/RimMandrake/rimflow/retro_block_frontier.py [--json OUT]

Writes nothing to the ledger (never calls `append`, `check` or the CLI); `--json` writes
only the named file. For every block interval that names a blocker it records, from the
rule's own verdicts, when the item ENTERED the frontier, with which kind, whether it left
and how (a seat's unblock/re-block, the item ending, or the blocker regressing), and what
was true of the item at each step (blocked? offered by rank()?). A counterfactual pass asks
the same of each interval had it been typed `--until built` or `--until validated`, using
the first moment the blocker reached that lifecycle state (built_at, validated_at).
Counts are given per interval AND per distinct item. Design:
design/2026-10-25-rimflow-block-release.md.
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

REACHED = {"built": ("built", "validated", "done"), "validated": ("validated", "done"),
           "done": ("done",)}


def hours(a, b):
    return (model.epoch(b) - model.epoch(a)) / 3600.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()
    evs = model.read()
    live, done = {}, []          # dependent id -> interval
    violations = []              # (ts, item, what): the rule released or offered something

    def close(iid, ts, how):
        iv = live.pop(iid, None)
        if iv:
            if iv["in_since"]:
                iv["spans"].append((iv["in_since"], ts, iv["in_kind"], how))
                iv["in_since"] = None
            iv["end"], iv["how"] = ts, how
            done.append(iv)

    def observe(ev, w, ok):
        if not ok:
            return
        verb, iid, ts = ev.get("event"), ev.get("id"), ev.get("ts")
        if verb == "block":
            close(iid, ts, "reblock")
            if ev.get("on"):
                live[iid] = {"id": iid, "on": ev["on"], "start": ts, "until": ev.get("until"),
                             "first": {}, "dead_at": None, "spans": [], "in_since": None,
                             "in_kind": None, "first_in": None, "first_kind": None,
                             "worked": False, "worked_after_in": False}
        elif iid in live and not w.items[iid].blocked:
            close(iid, ts, verb)
        if iid in live and verb in ("claim", "start", "implemented"):
            live[iid]["worked"] = True
            if live[iid]["first_in"]:
                live[iid]["worked_after_in"] = True
        # the real rule, on every live interval this event could touch
        for d, iv in live.items():
            if iid not in (d, iv["on"]):
                continue
            it, b = w.items[d], w.items.get(iv["on"])
            if b is not None:
                for lv, sts in REACHED.items():
                    if b.state in sts and lv not in iv["first"]:
                        iv["first"][lv] = ts
                if b.state in priority.DEAD and not iv["dead_at"]:
                    iv["dead_at"] = ts
            e = priority.frontier_entry(w, it)
            if e and not iv["in_since"]:
                iv["in_since"], iv["in_kind"] = ts, e[0]
                if not iv["first_in"]:
                    iv["first_in"], iv["first_kind"] = ts, e[0]
            elif not e and iv["in_since"]:
                iv["spans"].append((iv["in_since"], ts, iv["in_kind"], "withdrawn:" + verb))
                iv["in_since"] = None
            if e:
                if not it.blocked:
                    violations.append((ts, d, "frontier entry not blocked"))
                if it in priority.rank(w, it.owner, None, {"now": model.epoch(ts),
                                                           "mode": "bench"}):
                    violations.append((ts, d, "frontier entry offered by rank()"))

    w = model.replay(evs, observe=observe)
    last = evs[-1]["ts"]
    for d in list(live):
        close(d, last, "still")

    rows = []
    for iv in done:
        lead = hours(iv["first_in"], iv["end"]) if iv["first_in"] else 0.0
        cf = {}
        for lv in ("built", "validated"):
            t = iv["first"].get(lv)
            if t and not iv["dead_at"] and model.epoch(t) < model.epoch(iv["end"]):
                t0 = max(model.epoch(t), model.epoch(iv["start"]))
                cf[lv] = round((model.epoch(iv["end"]) - t0) / 3600.0, 1)
        rows.append(dict(iv, lead_h=round(lead, 1), lead_raw=lead, cf=cf))

    def distinct(rs):
        return len({r["id"] for r in rs})

    entered = [r for r in rows if r["first_in"]]
    stale = [r for r in entered if r["lead_raw"] > 0]
    stale_1h = [r for r in stale if r["lead_raw"] > 1]
    big = sorted((r for r in stale if r["lead_raw"] > 170), key=lambda r: -r["lead_raw"])
    conf = [r for r in entered if r["first_kind"] == "confirm"]
    conf_how = collections.Counter(r["how"] for r in conf)
    withdrawn = [r for r in rows if any(s[3].startswith("withdrawn") for s in r["spans"])]
    worked = [r for r in rows if r["worked"]]
    worked_after = [r for r in rows if r["worked_after_in"]]
    cf_b = [r for r in rows if r["cf"].get("built", 0) > r["lead_h"] + 1]
    cf_v = [r for r in rows if r["cf"].get("validated", 0) > r["lead_h"] + 1]
    today = priority.block_frontier(w)
    today_built = [i for i in w.open_items() if i.blocked and i.blocked_on
                   and getattr(w.items.get(i.blocked_on), "state", None) in ("built", "validated")]
    diag = [(i.id, d) for i in w.open_items() for d in priority.block_diagnostics(w, i)]

    out = {
        "events": len(evs), "items": len(w.items), "replay_errors": len(w.errors),
        "on_intervals": len(rows), "on_items": distinct(rows),
        "entered_frontier": [len(entered), distinct(entered)],
        "outlived_blocker_end": [len(stale), distinct(stale)],
        "outlived_over_1h": [len(stale_1h), distinct(stale_1h)],
        "stale_over_170h": [(r["id"], r["on"], r["lead_h"], r["first_kind"], r["how"])
                            for r in big],
        "lead_days_over_170h": round(sum(r["lead_raw"] for r in big) / 24.0, 1),
        "confirm": [len(conf), distinct(conf)], "confirm_resolved_by": dict(conf_how),
        "confirm_rows": [(r["id"], r["on"], r["how"], r["end"]) for r in conf],
        "withdrawn_by_blocker_regression": [(r["id"], r["on"], r["spans"]) for r in withdrawn],
        "violations": violations[:20], "violation_count": len(violations),
        "worked_while_blocked": [len(worked), distinct(worked)],
        "worked_after_entering_frontier": [len(worked_after), distinct(worked_after)],
        "cf_until_built_earlier": [len(cf_b), distinct(cf_b)],
        "cf_until_validated_earlier": [len(cf_v), distinct(cf_v)],
        "frontier_today": [(f[0].id, f[1], f[2].id, f[2].state) for f in today],
        "open_blocked_on_built_or_validated_today": len(today_built),
        "diagnostics_today": diag,
    }
    p = lambda k: "%d intervals / %d items" % tuple(out[k])           # noqa: E731
    print("events %(events)d  items %(items)d  replay errors %(replay_errors)d" % out)
    print("block --on intervals: %d over %d items" % (out["on_intervals"], out["on_items"]))
    print("entered the frontier (real rule, every step): %s" % p("entered_frontier"))
    print("  of which still blocked after entering (seat had not lifted): %s; > 1 h: %s"
          % (p("outlived_blocker_end"), p("outlived_over_1h")))
    print("stale > 170 h after entering:")
    for r in big:
        print("  %-44s on %-40s %6.1f h  (%s; ended by %s)"
              % (r["id"][:44], r["on"][:40], r["lead_h"], r["first_kind"], r["how"]))
    print("  total lead: %.1f item-days" % out["lead_days_over_170h"])
    print("confirm (blocker dropped/superseded): %s; resolved by %s"
          % (p("confirm"), dict(conf_how)))
    print("withdrawn because the blocker regressed: %d" % len(withdrawn))
    print("rule violations (an entry unblocked or offered by rank(), any step): %d"
          % len(violations))
    print("claimed/started/implemented while blocked: %s; after entering the frontier: %s"
          % (p("worked_while_blocked"), p("worked_after_entering_frontier")))
    print("counterfactual --until built would surface earlier: %s; --until validated: %s"
          % (p("cf_until_built_earlier"), p("cf_until_validated_earlier")))
    print("frontier today: %d %s" % (len(today), dict(collections.Counter(f[1] for f in today))))
    print("open items blocked on a built/validated item today: %d" % len(today_built))
    print("read-time diagnostics today: %d" % len(diag))
    for d in diag[:10]:
        print("  %s: %s" % d)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
