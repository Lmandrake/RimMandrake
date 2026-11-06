#!/usr/bin/env python3
"""evidence_metrics.py - a record of how Relentless is doing, kept as EVIDENCE, never as targets.

Item METRICS_RECORD_BUILD_EVIDENCE_NOT_TARGETS; spec design/RimMandrake/relentless_improvement_loop_2026-11-03.md
§Metrics are evidence, not targets. Owner, 2026-11-03: "track whatever metrics you'd like. We're not chasing metrics,
we're just keeping a record of them as evidence." So nothing here carries a goal, threshold, alarm or pass/fail: it
counts and records. A metric whose source is missing says UNMEASURED and why, never 0.

The four records, all read-only from their sources:
  stays_done            each ledger `close`, once 7 days old: did it stay done? It did NOT when, in the 7 days after,
                        the item was reopened (a later start / claim / implemented, a `verify` fail marked afterClose,
                        a `live` broken) or work was filed against it (a `file` caused_by it, a `spawn` from it).
                        Younger closes are `pending`, never counted. Split offline / online by the item's `needs`
                        when it closed (offline = needs offline; anything else is online; never set = unknown).
                        The unit is the CLOSE: an item closed, reopened and closed again is two closes.
  cost_per_stayed_done  for the closes that stayed done: tokens (Relentless store spend units for the item; items the
                        belt never ran have none: counted as unpriced, never as 0), worker hours (the sum of the
                        item's Relentless generations, start to end) and elapsed hours (the ledger's first
                        start/claim to the close).
  jams_by_class         the belt journal's jam alarms (jam_classes.json kinds), each named by its jam class; jams no
                        class names are `unnamed`. Last 7 days and all time.
  escapes_by_tag        every close that did not stay done (any time after it, up to the item's next close), by its
                        plain tag from ESCAPE_TAGS (rows {"item", "tag"}; ESCAPE_RECORD_BUILD_PLAIN_TAGS writes them).
                        An escape with no tag counts as `(untagged)`, with the signal that made it an escape.

    python3 src/RimMandrake/rimflow/evidence_metrics.py [report] [--json]
    python3 src/RimMandrake/rimflow/evidence_metrics.py record      # append today's reading to RECORD
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import delivery_metrics, jam_classes          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LEDGER = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
RECORD = os.path.join(REPO, "infrastructure", "state", "evidence_metrics.jsonl")
ESCAPE_TAGS = os.path.join(REPO, "infrastructure", "state", "escape_tags.jsonl")
STORE = delivery_metrics.STORE
UNMEASURED = "UNMEASURED"
WINDOW_DAYS = 7
NOTE = "evidence, not a target: nothing here is a goal or a threshold (owner 2026-11-03)"
REOPENING = ("start", "claim", "implemented")


def ep(s):
    return jam_classes.epoch(s)


def um(why):
    return {"value": UNMEASURED, "why": why}


def ledger_events(ledger=LEDGER):
    """-> every ledger event in (ts, tsn) order, or None when the directory is missing (not zero events)."""
    if not os.path.isdir(ledger):
        return None
    out = []
    for p in sorted(glob.glob(os.path.join(ledger, "*.jsonl"))):
        out.extend(e for e in delivery_metrics._jsonl(p) if e.get("ts"))
    out.sort(key=lambda e: (str(e["ts"]), e.get("tsn") or 0))
    return out


def signal(e, item):
    """-> the kind of 'did not stay done' signal this event is about `item`, or None."""
    k = e.get("event")
    if e.get("id") == item:
        if k in REOPENING:
            return "reopened"
        if k == "verify" and e.get("result") == "fail" and e.get("afterClose"):
            return "failed_after_close"
        if k == "live" and e.get("result") == "broken":
            return "broke_live"
    if k == "file" and e.get("caused_by") == item:
        return "work_filed_against_it"
    if k == "spawn" and item in (e.get("from"), e.get("caused_by")):
        return "work_filed_against_it"
    return None


def closes(events):
    """-> [{item, t, needs, first_start, signals: [(t, kind)] up to the item's next close}] in ledger order."""
    needs, first, out, open_close = {}, {}, [], {}
    for e in events:
        t = ep(e["ts"])
        if t is None:
            continue
        i, k = e.get("id"), e.get("event")
        if k == "file" and i and e.get("needs"):
            needs[i] = e["needs"]
        elif k == "needs" and i and e.get("to"):
            needs[i] = e["to"]
        elif k == "implemented" and i and e.get("needs"):
            needs[i] = e["needs"]
        if k in ("start", "claim") and i and i not in first:
            first[i] = t
        # signals go to every open close they name
        for cand in {x for x in (i, e.get("caused_by"), e.get("from")) if isinstance(x, str)}:
            c = open_close.get(cand)
            if c is not None and t > c["t"]:
                s = signal(e, cand)
                if s:
                    c["signals"].append((t, s))
        if k == "close" and i:
            c = {"item": i, "t": t, "needs": needs.get(i), "first_start": first.get(i), "signals": []}
            out.append(c)
            open_close[i] = c
            first.pop(i, None)        # elapsed time of a reclose runs from the reopening start
    return out


def lane(needs):
    return "unknown" if not needs else "offline" if needs == "offline" else "online"


def stays_done(cl, now, window=WINDOW_DAYS):
    w = window * 86400
    lanes = {x: {"stayed": 0, "did_not": 0, "pending": 0} for x in ("offline", "online", "unknown")}
    why, cohorts, stayed = {}, {}, []
    for c in cl:
        ln = lanes[lane(c["needs"])]
        if now - c["t"] < w:
            ln["pending"] += 1
            continue
        early = [s for t, s in c["signals"] if t - c["t"] <= w]
        week = dt.datetime.fromtimestamp(c["t"], dt.timezone.utc).strftime("%G-W%V")
        co = cohorts.setdefault(week, {"stayed": 0, "did_not": 0})
        if early:
            ln["did_not"] += 1
            co["did_not"] += 1
            for s in set(early):
                why[s] = why.get(s, 0) + 1
        else:
            ln["stayed"] += 1
            co["stayed"] += 1
            stayed.append(c)
    for v in list(lanes.values()) + list(cohorts.values()):
        n = v["stayed"] + v["did_not"]
        v["share_stayed"] = round(v["stayed"] / n, 3) if n else None
    return {"unit": "closes (a reclose is a second close)", "window_days": window, "by_lane": lanes,
            "did_not_because": dict(sorted(why.items())), "by_close_week": dict(sorted(cohorts.items()))}, stayed


def worker_hours(rows):
    """-> hours summed over the item's Relentless generations (start row to its end row), or None with no pair."""
    starts, total, seen = {}, 0.0, False
    for r in rows or []:
        t = ep(r.get("at"))
        if t is None:
            continue
        if r.get("start") is not None:
            starts[r.get("gen")] = t
        elif r.get("end") and r.get("gen") in starts:
            total += t - starts.pop(r["gen"])
            seen = True
    return round(total / 3600, 2) if seen else None


def med(xs):
    return round(statistics.median(xs), 2) if xs else None


def cost(stayed, snap):
    if not stayed:
        return {"stayed_done_closes": 0, "note": "no close has stayed done yet: nothing to cost"}
    spend, attempts = snap.get("spend"), snap.get("attempts")
    out = {}
    for name, group in (("all", stayed), ("offline", [c for c in stayed if lane(c["needs"]) == "offline"]),
                        ("online", [c for c in stayed if lane(c["needs"]) == "online"])):
        toks, wh, eh, unpriced = [], [], [], 0
        for c in group:
            units = delivery_metrics._units(spend, c["item"]) if spend is not None else {}
            if units:
                toks.append(sum(units.values()))
            else:
                unpriced += 1
            h = worker_hours((attempts or {}).get(c["item"]))
            if h is not None:
                wh.append(h)
            if c["first_start"] is not None:
                eh.append(round((c["t"] - c["first_start"]) / 3600, 2))
        states = snap.get("states") or {}
        out[name] = {"closes": len(group), "belt_ran": sum(c["item"] in states for c in group),
                     "tokens": ({"priced": len(toks), "unpriced": unpriced, "total": sum(toks), "median": med(toks)}
                                if spend is not None else um("no spend-*.json in %s" % snap.get("store"))),
                     "worker_hours": ({"measured": len(wh), "total": round(sum(wh), 2), "median": med(wh)}
                                      if attempts is not None else um("no item attempts in %s" % snap.get("store"))),
                     "elapsed_hours": {"measured": len(eh), "median": med(eh)}}
    out["note"] = ("tokens and worker hours exist only for items the Relentless belt ran (belt_ran: unpriced closes "
                   "are the rest) and are the item's whole spend to date, so a reclosed item carries all its generations; elapsed "
                   "hours run from the ledger's first start/claim to the close")
    return out


def jams(reg, journal, now):
    names = {c["id"]: c.get("plain") for c in reg["classes"]}
    out = {}
    for label, since in (("last_%dd" % WINDOW_DAYS, now - WINDOW_DAYS * 86400), ("all_time", 0)):
        rows, why = jam_rows_safe(journal, set(reg["kinds"]), since)
        if rows is None:
            return um(why)
        by = {}
        for r in rows:
            cid = jam_classes.classify(reg, r["why"]) or "unnamed"
            by[cid] = by.get(cid, 0) + 1
        out[label] = {"jams": len(rows), "by_class": dict(sorted(by.items(), key=lambda kv: -kv[1]))}
    out["plain"] = {k: v for k, v in names.items() if any(k in out[w]["by_class"] for w in out)}
    return out


def jam_rows_safe(journal, kinds, since):
    if not journal or not os.path.exists(str(journal)):
        return None, "no belt journal at %s" % journal
    return jam_classes.jam_rows(journal, kinds, since)


def escape_tags(path=ESCAPE_TAGS):
    """-> {item: tag} (the newest row per item wins), or None when no tag record exists yet."""
    if not os.path.exists(path):
        return None
    tags = {}
    for r in delivery_metrics._jsonl(path):
        if r.get("item") and r.get("tag"):
            tags[r["item"]] = r["tag"]
    return tags


def escapes(cl, tags):
    by_tag, untagged = {}, {}
    n = 0
    for c in cl:
        if not c["signals"]:
            continue
        n += 1
        tag = (tags or {}).get(c["item"])
        if tag:
            by_tag[tag] = by_tag.get(tag, 0) + 1
        else:
            s = c["signals"][0][1]
            untagged[s] = untagged.get(s, 0) + 1
    out = {"escapes": n, "by_tag": dict(sorted(by_tag.items(), key=lambda kv: -kv[1])),
           "untagged_by_signal": dict(sorted(untagged.items()))}
    if tags is None:
        out["tags"] = um("no tag record at %s yet (ESCAPE_RECORD_BUILD_PLAIN_TAGS writes it): every escape is "
                         "untagged" % os.path.relpath(ESCAPE_TAGS, REPO))
    return out


def compute(events, snap, reg, journal, tags, now):
    m = {"note": NOTE, "at": dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if events is None:
        m["stays_done"] = m["cost_per_stayed_done"] = m["escapes_by_tag"] = um("no ledger at %s" % LEDGER)
    else:
        cl = closes(events)
        m["stays_done"], stayed = stays_done(cl, now)
        m["cost_per_stayed_done"] = cost(stayed, snap)
        m["escapes_by_tag"] = escapes(cl, tags)
    m["jams_by_class"] = jams(reg, journal, now)
    return m


def render(m):
    out = ["Relentless evidence record, %s - %s" % (m["at"], m["note"])]
    for k in ("stays_done", "cost_per_stayed_done", "jams_by_class", "escapes_by_tag"):
        out.append("%s: %s" % (k, json.dumps(m[k], sort_keys=True)))
    return "\n".join(out)


def journal_path():
    try:
        return jam_classes.default_journal()
    except SystemExit:
        return None             # jams_by_class then says UNMEASURED: no belt journal configured


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", default="report", choices=("report", "record"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--journal")
    ap.add_argument("--record", default=RECORD)
    a = ap.parse_args(argv)
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    m = compute(ledger_events(a.ledger), delivery_metrics.load(a.store, a.ledger), jam_classes.load(),
                a.journal or journal_path(), escape_tags(), now)
    if a.cmd == "record":
        with open(a.record, "a", encoding="utf-8") as f:
            f.write(json.dumps(m, sort_keys=True) + "\n")
        print("evidence_metrics: recorded %s to %s" % (m["at"], os.path.relpath(a.record, REPO)))
        return 0
    print(json.dumps(m, indent=1, sort_keys=True) if a.json else render(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
