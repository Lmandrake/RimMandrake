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


def live_rates(states, attempts):
    """Live store. Finish: done / ended. First-check fail: on unseeded work, so never a catch rate."""
    done = sum(s["status"] == "done" for s in states)
    ended = done + sum(s["status"] in ("held", "retired") for s in states)
    first = fails = weak = 0
    for rows in attempts:
        checks = [a for a in rows if a.get("end") in ("blind_fail", "proof_weak", "done")]
        if checks:
            first += 1
            fails += checks[0]["end"] == "blind_fail"
            weak += checks[0]["end"] == "proof_weak"
    return {"done": done, "ended": ended, "first_checks": first, "first_fails": fails, "first_weak": weak}


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
        miss = rule3(x["n"] - x["caught"] - x["weak"], x["n"], "misses")
        weak = ", %d more WEAK (held open, not caught)" % x["weak"] if x["weak"] else ""
        lines.append("| Marker catch, %s, %s | %s%s%s%s; %s |" % (cls, label, fmt(x["caught"], x["n"], x["ci"]), weak, miss, tail, tallies(x)))
    x = c["control"]
    lines.append("| Control false fail, %s | %s%s; %s |" % (label, fmt(x["false_fail"], x["n"], x["ci"]),
                                                            rule3(x["false_fail"], x["n"], "false fails"), tallies(x)))
    lines.append("| Control WEAK (kept open on a proof, no code rework asked), %s | %s |" % (label, fmt(x["weak"], x["n"], wilson(x["weak"], x["n"]))))
    lines.append("| Contaminated packets, repeat work, true stops, help value | %s |" % UNMEASURED)
    if live["first_checks"]:
        lines.append("| Live first-check FAIL rate (unseeded work, not a catch rate) | %d of %d |" % (
            live["first_fails"], live["first_checks"]))
        lines.append("| Live first-check WEAK rate | %d of %d |" % (live.get("first_weak", 0), live["first_checks"]))
    notes = []
    for name in ("lost", "contaminated", "removed_equivalent", "unread"):
        if c[name]:
            notes.append("%s: %s" % (name, ", ".join(c[name])))
    for item, why in c["control"]["reasons"].items():
        notes.append("control FAIL %s: %s" % (item, (why or "")))
    if frame:
        notes.append("Population: %s" % json.dumps({k: (len(v) if k == "dropped_at_delivery" else v) for k, v in frame.items()},
                                                   sort_keys=True))
    return "\n".join(lines) + "\n" + "".join("\n%s\n" % n for n in notes)


def report(store, private=None, set_name="E1", arm=None):
    private = Path(private or PRIVATE)
    res = private / ("results_" + arm if arm else "results")
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
    return c, render(c, live_rates(states, attempts), "accepted by Judge at " + set_name + (", arm " + arm if arm else ""), frame)


def _load_results(private, keys, name):
    d = private / name
    out = []
    for k in keys:
        p = d / (k["item"] + ".json")
        if p.exists():
            out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def _median(xs):
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    return xs[len(xs) // 2] if xs else None


def compare(base, arm, second_reads=None, keys=None, arm_print=None):
    """Step 3 (design §13): the same set run twice, `base` unwalled (step 0) and `arm` behind the wall. Pure.
    Per class, each side's own counted rate under the counting rules; then the cases with a counted verdict on BOTH sides,
    paired, so a flip is the same case read two ways. Contamination is split: a real read (counted out under the rules)
    against `unscanned`, which is a harness fault, not a read."""
    c0, c1 = compute(base, second_reads, keys), compute(arm, second_reads, keys)
    ok0 = {r["item"]: r for r in base if r["item"] not in c0["contaminated"] + c0["lost"] and r.get("verdict")}
    ok1 = {r["item"]: r for r in arm if r["item"] not in c1["contaminated"] + c1["lost"] and r.get("verdict")}
    removed = set(c0["removed_equivalent"])
    pairs, flips = {}, []
    for k in keys if keys is not None else base:
        i = k["item"]
        if i in removed or i not in ok0 or i not in ok1:
            continue
        a, b = ok0[i]["verdict"], ok1[i]["verdict"]
        pairs.setdefault(k["cls"], {}).setdefault("%s>%s" % (a, b), 0)
        pairs[k["cls"]]["%s>%s" % (a, b)] += 1
        if a != b:
            flips.append((i, k["cls"], a, b))

    def contam(rs):
        real = [r["item"] for r in rs if r.get("contaminated") and r["contaminated"] != ["unscanned"]]
        uns = [r["item"] for r in rs if r.get("contaminated") == ["unscanned"]]
        return real, uns

    return {"base": c0, "arm": c1, "pairs": pairs, "flips": sorted(flips),
            "contam_base": contam(base), "contam_arm": contam(arm),
            "walled_arm": sum(bool(r.get("walled")) for r in arm), "walled_base": sum(bool(r.get("walled")) for r in base),
            "runs": (len(base), len(arm)),
            "secs": (_median(r.get("secs") for r in base), _median(r.get("secs") for r in arm)),
            # a walled run's token count reads 0: the counter cannot see into the box, so 0 is no measurement
            "tokens": (_median(r.get("tokens") or None for r in base), _median(r.get("tokens") or None for r in arm)),
            # a result carries its KEY's fingerprint (the Marker the set was picked under); an arm's own Marker is in arm.json
            "fingerprints": (sorted({r.get("fingerprint", "")[:12] for r in base}), [arm_print[:12]] if arm_print else
                             sorted({r.get("fingerprint", "")[:12] for r in arm}))}


def render_compare(x, arm_name):
    def side(c, cls):
        if cls == "control":
            y = c["control"]
            return "false fail %s, WEAK %d" % (fmt(y["false_fail"], y["n"], y["ci"]), y["weak"])
        y = c["classes"][cls]
        return "%s, WEAK %d" % (fmt(y["caught"], y["n"], y["ci"]), y["weak"])
    lines = ["| Class | Step 0, unwalled | Arm %s, walled | Paired (same case, both counted) |" % arm_name, "|---|---|---|---|"]
    for cls in CLASSES + ("control",):
        p = x["pairs"].get(cls, {})
        lines.append("| %s | %s | %s | %s |" % (cls, side(x["base"], cls), side(x["arm"], cls),
                                               ", ".join("%s %d" % kv for kv in sorted(p.items())) or "none"))
    (r0, u0), (r1, u1) = x["contam_base"], x["contam_arm"]
    lines += ["", "| Measure | Step 0 | Arm %s |" % arm_name, "|---|---|---|",
              "| Runs with a result | %d | %d |" % x["runs"],
              "| Runs behind the wall | %d | %d |" % (x["walled_base"], x["walled_arm"]),
              "| Contaminated: a real read of the books or a seat clone | %d | %d |" % (len(r0), len(r1)),
              "| Contaminated: unscanned (harness fault, not a read) | %d | %d |" % (len(u0), len(u1)),
              "| Lost (no verdict) | %d | %d |" % (len(x["base"]["lost"]), len(x["arm"]["lost"])),
              "| Median seconds to verdict | %s | %s |" % tuple("%.0f" % s if s is not None else UNMEASURED for s in x["secs"]),
              "| Median tokens | %s | %s |" % tuple(str(t) if t is not None else UNMEASURED for t in x["tokens"]),
              "| Marker fingerprint | %s | %s |" % tuple(", ".join(f) or UNMEASURED for f in x["fingerprints"])]
    notes = ["flip %s (%s): %s -> %s" % f for f in x["flips"]]
    if r1:
        notes.append("arm real reads: " + ", ".join(r1))
    return "\n".join(lines) + "\n" + "".join("\n%s\n" % n for n in notes)


def compare_report(private=None, set_name="E1", arm="S03"):
    private = Path(private or PRIVATE)
    keys = json.loads((private / "keys" / (set_name + ".json")).read_text(encoding="utf-8"))
    reads = {}
    p = private / "second_reads.json"
    if p.exists():
        reads = {k: v["read"] for k, v in json.loads(p.read_text(encoding="utf-8")).items()}
    ap = private / ("results_" + arm) / "arm.json"
    arm_print = json.loads(ap.read_text(encoding="utf-8")).get("fingerprint") if ap.exists() else None
    x = compare(_load_results(private, keys, "results"), _load_results(private, keys, "results_" + arm), reads, keys, arm_print)
    return x, render_compare(x, arm)
