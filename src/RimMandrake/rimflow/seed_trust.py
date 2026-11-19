"""seed_trust.py - the seeded-set trust numbers (Wilson interval, on-target, compute) delivery_metrics reads; moved
from relentless_trust.py.

Moved verbatim from rimflow/relentless_trust.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
from __future__ import annotations

import math
import os
import re
from pathlib import Path

CLASSES = ("all_red", "hunk_red", "hunk_green", "escaped")
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
    names = {p.replace("\\", "/").rsplit("/", 1)[-1] for p in ([r["path"]] if r.get("path") else (r.get("paths") or []))}
    why = (r.get("reasons") or "").replace("\\", "/")     # a Windows path in the reasons names the file too
    return any(n and re.search(r"(?<![\w.-])" + re.escape(n) + r"(?![\w-]|\.\w)", why) for n in names)


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
        elif r.get("verdict") not in ("PASS", "WEAK", "FAIL"):
            tally[cls]["lost"] += 1
            out["lost"].append(r["item"])
        else:
            rows.append(r)
    for cls in CLASSES:
        mine = [r for r in rows if r["cls"] == cls]
        caught = sum(r["verdict"] == "FAIL" for r in mine)
        weak = sum(r["verdict"] == "WEAK" for r in mine)
        target = sum(on_target(r) for r in mine if r["verdict"] == "FAIL")
        out["classes"][cls] = dict(tally[cls], caught=caught, weak=weak, n=len(mine), ci=wilson(caught, len(mine)),
                                   on_target=None if cls == "escaped" else target)
    ctl = [r for r in rows if r["cls"] == "control"]
    fails = [r for r in ctl if r["verdict"] == "FAIL"]
    weak = [r for r in ctl if r["verdict"] == "WEAK"]
    out["control"] = dict(tally["control"], false_fail=len(fails), n=len(ctl), ci=wilson(len(fails), len(ctl)),
                          weak=len(weak), weak_items=[r["item"] for r in weak],
                          items=[r["item"] for r in fails], reasons={r["item"]: r.get("reasons") for r in fails})
    return out
