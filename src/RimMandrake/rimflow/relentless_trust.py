#!/usr/bin/env python3
"""relentless_trust.py - TRUST.md, computed. Rules: design/RimMandrake/relentless_counting_rules_2026-11-01.md.

Reads seed results and the live store, writes nothing to either. `compute` is pure so the rules can be tested on planted
results. A measure with no source prints UNMEASURED, never 0.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

CLASSES = ("all_red", "hunk_red", "hunk_green", "escaped")
UNMEASURED = "UNMEASURED"
PRIVATE = Path(os.environ.get("RM_SEEDS_PRIVATE", "/mnt/d/ClaudeWork/rimmandrake/relentless_agent/seeds"))


def wilson(k, n, z=1.96):
    """The 95% interval of k/n."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, mid - half), min(1.0, mid + half)


def on_target(r):
    """Reasons name the reverted file, whole. Only a mechanical reading: it is not a proof the Marker saw the fault."""
    names = {os.path.basename(p) for p in ([r["path"]] if r.get("path") else (r.get("paths") or []))}
    return bool(names & {os.path.basename(x) for x in re.findall(r"[\w./\\-]+\.py\b", r.get("reasons") or "")})


def compute(results, second_reads=None, keys=None):
    """results: one dict per run case. second_reads: {item: "observable"|"equivalent"}, read blind for every hunk_green
    case before any verdict. keys: the set's cases, so that a case with no result is counted as unrun, never as absent."""
    second_reads = second_reads or {}
    keys = keys if keys is not None else results
    removed = {k["item"] for k in keys if second_reads.get(k["item"]) == "equivalent"}
    seen = {r["item"]: r for r in results}
    out = {"classes": {}, "lost": [], "contaminated": [], "removed_equivalent": sorted(removed),
           "unread": [k["item"] for k in keys if k["cls"] == "hunk_green" and k["item"] not in second_reads]}
    rows = []
    tally = {c: {"planned": 0, "unrun": 0, "lost": 0, "contaminated": 0, "removed": 0} for c in CLASSES + ("control",)}
    for k in keys:
        cls, r = k["cls"], seen.get(k["item"])
        tally[cls]["planned"] += 1
        if k["item"] in removed:
            tally[cls]["removed"] += 1
        elif r is None:
            tally[cls]["unrun"] += 1
        elif r.get("contaminated"):
            tally[cls]["contaminated"] += 1
            out["contaminated"].append(r["item"])
        elif r.get("verdict") not in ("PASS", "FAIL"):
            tally[cls]["lost"] += 1
            out["lost"].append(r["item"])
        else:
            rows.append(r)
    for cls in CLASSES:
        mine = [r for r in rows if r["cls"] == cls]
        caught = sum(r["verdict"] == "FAIL" for r in mine)
        target = sum(on_target(r) for r in mine if r["verdict"] == "FAIL")
        out["classes"][cls] = dict(tally[cls], caught=caught, n=len(mine), ci=wilson(caught, len(mine)),
                                   on_target=None if cls == "escaped" else target)
    ctl = [r for r in rows if r["cls"] == "control"]
    fails = [r for r in ctl if r["verdict"] == "FAIL"]
    out["control"] = dict(tally["control"], false_fail=len(fails), n=len(ctl), ci=wilson(len(fails), len(ctl)),
                          items=[r["item"] for r in fails], reasons={r["item"]: r.get("reasons") for r in fails})
    return out


def live_rates(states, attempts):
    """Live store. Finish: done / ended. First-check fail: on unseeded work, so never a catch rate."""
    done = sum(s["status"] == "done" for s in states)
    ended = done + sum(s["status"] in ("held", "retired") for s in states)
    first = fails = 0
    for rows in attempts:
        checks = [a for a in rows if a.get("end") in ("blind_fail", "done")]
        if checks:
            first += 1
            fails += checks[0]["end"] == "blind_fail"
    return {"done": done, "ended": ended, "first_checks": first, "first_fails": fails}


def fmt(k, n, ci):
    if not n:
        return UNMEASURED
    return "%d of %d (95%% %.0f-%.0f%%)" % (k, n, 100 * ci[0], 100 * ci[1])


def rule3(k, n, what):
    """With none of the event seen, the rule of three bounds the event. Apart from Wilson, and labelled."""
    return ", %s at most %.0f%% (rule of three)" % (what, 100 * min(1.0, 3.0 / n)) if n and k == 0 else ""


def tallies(x):
    return "planned %d, unrun %d, lost %d, contaminated %d, removed %d" % (
        x["planned"], x["unrun"], x["lost"], x["contaminated"], x["removed"])


def render(c, live, label, frame=None):
    lines = ["| Measure | Now |", "|---|---|"]
    if live["ended"]:
        lines.append("| Finish rate, aided or not (`unaided` needs intake) | %d of %d ended items |" % (live["done"], live["ended"]))
    else:
        lines.append("| Finish rate | %s |" % UNMEASURED)
    lines.append("| Escaped defects | %s |" % UNMEASURED)
    for cls in CLASSES:
        x = c["classes"][cls]
        tail = "" if x["on_target"] is None or not x["n"] else ", %d named the file" % x["on_target"]
        miss = rule3(x["n"] - x["caught"], x["n"], "misses")
        lines.append("| Marker catch, %s, %s | %s%s%s; %s |" % (cls, label, fmt(x["caught"], x["n"], x["ci"]), miss, tail, tallies(x)))
    x = c["control"]
    lines.append("| Control false fail, %s | %s%s; %s |" % (label, fmt(x["false_fail"], x["n"], x["ci"]),
                                                            rule3(x["false_fail"], x["n"], "false fails"), tallies(x)))
    lines.append("| Contaminated packets, repeat work, true stops, help value | %s |" % UNMEASURED)
    if live["first_checks"]:
        lines.append("| Live first-check FAIL rate (unseeded work, not a catch rate) | %d of %d |" % (
            live["first_fails"], live["first_checks"]))
    notes = []
    for name in ("lost", "contaminated", "removed_equivalent", "unread"):
        if c[name]:
            notes.append("%s: %s" % (name, ", ".join(c[name])))
    for item, why in c["control"]["reasons"].items():
        notes.append("control FAIL %s: %s" % (item, (why or "")[:300]))
    if frame:
        notes.append("Population: %s" % json.dumps({k: (len(v) if k == "dropped_at_delivery" else v) for k, v in frame.items()},
                                                   sort_keys=True))
    return "\n".join(lines) + "\n" + "".join("\n%s\n" % n for n in notes)


def report(store, private=None, set_name="E1"):
    private = Path(private or PRIVATE)
    res = private / "results"
    kp = private / "keys" / (set_name + ".json")
    keys = json.loads(kp.read_text(encoding="utf-8")) if kp.exists() else []
    fp = private / "keys" / (set_name + ".frame.json")
    frame = json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else None
    results = []
    for k in keys:
        p = res / (k["item"] + ".json")
        if p.exists():
            results.append(json.loads(p.read_text(encoding="utf-8")))
    reads = {}
    p = private / "second_reads.json"
    if p.exists():
        reads = {k: v["read"] for k, v in json.loads(p.read_text(encoding="utf-8")).items()}
    states = store.states()
    attempts = []
    for s in states:
        f = Path(store.item_dir(s["item"]), "attempts.jsonl")
        if f.exists():
            attempts.append([json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()])
    c = compute(results, reads, keys)
    return c, render(c, live_rates(states, attempts), "accepted by Judge at " + set_name, frame)
