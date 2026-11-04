#!/usr/bin/env python3
"""delivery_metrics.py - delivery, measurement availability and false closes, measured together.

Spec: design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, rank 6 ("Measure delivery, measurement availability,
and false closes together"); item CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY. Reads the Relentless store read-only and
the committed audit record infrastructure/state/close_audits.jsonl; writes only that record (`sample`, `audit`).

A metric whose source does not exist prints UNMEASURED with the reason, never 0 (owner 2026-11-03: inability to measure
is reported up). The unit is the ITEM: the store keeps no per-obligation record, so "obligations" are counted as items.

False closes are audited in two populations, never pooled: `random` (a seeded draw over every close, for an overall
estimate) and `narrow_weak` (targeted: every close whose deciding verdict was a WEAK the live narrow rule read as PASS,
relentless_wall.acted_weak, live since 2026-11-04T07:02Z, ede0dff499). Both are stratified by closure age at audit.

    python3 src/RimMandrake/rimflow/delivery_metrics.py [report] [--json]
    python3 src/RimMandrake/rimflow/delivery_metrics.py sample --random 8 --seed 20261104
    python3 src/RimMandrake/rimflow/delivery_metrics.py audit <SAMPLE> <ITEM> HOLDS|VIOLATED|UNMEASURED --by WHO \
        --how "what the auditor ran or read" --evidence "what it showed"
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import random
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import relentless_trust, relentless_wall          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
AUDITS = os.path.join(REPO, "infrastructure", "state", "close_audits.jsonl")
STORE = os.path.join(os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless", "store")
UNMEASURED = "UNMEASURED"

ACCEPTED = ("done", "closing")                       # closing: the supervisor accepted it, the ledger close is pending
WAITING = ("blocked", "held", "game")                # awaiting evidence, a repair, a dependency or the live game
UNRESOLVED = ("queued", "running", "candidate", "checking")
DROPPED = ("retired",)                                # excluded by the rules: never intake-accepted
# An attempt end that is a SUPPORTED attribution to the product. Everything else (a red blind check included: the spec,
# "red proof is not sufficient attribution to product") leaves the cause unattributed.
PRODUCT_ENDS = ("proof_found_defect", "game_fail")
VERDICT_OK = ("PASS", "WEAK", "FAIL")
AGES = ((1, "<1d"), (7, "1-7d"), (None, ">7d"))
VERDICTS = ("HOLDS", "VIOLATED", "UNMEASURED")


def short(item):
    """relentless.short: the hash in a unit name (rm-relentless-<kind>-<short>-g<gen>)."""
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def ep(s):
    if isinstance(s, (int, float)):
        return float(s)
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _jsonl(path, bad=None):
    """Rows of a JSONL file. A line that does not parse is skipped and, when `bad` is a dict, counted there under the
    path, so a corrupt record shows in source_coverage instead of reading as fewer events."""
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    if bad is not None:
                        bad[path] = bad.get(path, 0) + 1
    return out


# ---------------------------------------------------------------- the snapshot (the only reader of the store)

def load(store=STORE):
    """-> the snapshot compute() reads. Missing parts are None, so compute can say UNMEASURED and why."""
    snap = {"store": store, "enrols": None, "states": None, "attempts": None, "spend": None, "basis": None,
            "shadow": None, "acts": None, "unreadable": [], "no_attempts": [], "malformed": {}}
    if not os.path.isdir(store):
        return snap
    jp = os.path.join(store, "journal.jsonl")
    if os.path.exists(jp):
        enrols, acts = {}, []
        for e in _jsonl(jp, snap["malformed"]):
            if e.get("do") == "enrol" and e.get("item"):
                enrols.setdefault(e["item"], e["at"])
            for a in e.get("acts") or []:
                acts.append(a.get("do"))
        snap["enrols"], snap["acts"] = enrols, acts
    idir = os.path.join(store, "items")
    if os.path.isdir(idir):
        states, attempts = {}, {}
        for i in sorted(os.listdir(idir)):
            try:
                with open(os.path.join(idir, i, "state.json"), encoding="utf-8") as f:
                    states[i] = json.load(f)
            except (OSError, ValueError):
                snap["unreadable"].append(i)        # shown in source_coverage, never silently dropped
                continue
            ap = os.path.join(idir, i, "attempts.jsonl")
            if os.path.exists(ap):
                attempts[i] = _jsonl(ap, snap["malformed"])
            else:
                snap["no_attempts"].append(i)       # no record is not zero attempts
        snap["states"], snap["attempts"] = states, attempts
    files = sorted(glob.glob(os.path.join(store, "spend-*.json")))
    if files:
        spend, basis = {}, {}
        for p in files:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            for u, v in (d.get("runs") or {}).items():
                spend[u] = spend.get(u, 0) + v
            basis.update(d.get("basis") or {})
        snap["spend"], snap["basis"] = spend, basis
    sp = os.path.join(store, "shadow.jsonl")
    if os.path.exists(sp):
        snap["shadow"] = _jsonl(sp, snap["malformed"])
    return snap


def sensitivity_source(private=None, set_name="E1"):
    """-> relentless_trust.compute() over the seeded set, or None when the private seed set is absent."""
    private = private or str(relentless_trust.PRIVATE)
    kp = os.path.join(private, "keys", set_name + ".json")
    if not os.path.exists(kp):
        return None
    with open(kp, encoding="utf-8") as f:
        keys = json.load(f)
    results = []
    for k in keys:
        p = os.path.join(private, "results", k["item"] + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                results.append(json.load(f))
    reads = {}
    rp = os.path.join(private, "second_reads.json")
    if os.path.exists(rp):
        with open(rp, encoding="utf-8") as f:
            reads = {k: v["read"] for k, v in json.load(f).items()}
    return relentless_trust.compute(results, reads, keys)


# ---------------------------------------------------------------- the metrics (pure)

def um(why):
    return {"value": UNMEASURED, "why": why}


def ratio(k, n):
    ci = relentless_trust.wilson(k, n)
    return {"k": k, "n": n, "rate": round(k / n, 3) if n else None, "ci95": [round(ci[0], 3), round(ci[1], 3)] if ci else None}


def closes(states):
    """-> {item: (closed_at epoch, deciding verdict, reasons)} for every accepted item."""
    out = {}
    for i, st in (states or {}).items():
        if st.get("status") in ACCEPTED:
            ch = st.get("check") or {}
            out[i] = (st.get("done_at"), ch.get("verdict"), ch.get("reasons") or "")
    return out


def narrow_weak(states):
    """Closes whose deciding verdict was a WEAK the live rule read as PASS (relentless_wall.acted_weak)."""
    return sorted(i for i, (_, w, why) in closes(states).items()
                  if w == "WEAK" and relentless_wall.acted_weak(w, why) == "PASS")


def _units(spend, item):
    h = "-%s-g" % short(item)
    return {u: v for u, v in (spend or {}).items() if h in u}


def m_yield(snap):
    if snap["enrols"] is None or snap["states"] is None:
        return um("no journal enrol record or no item states in %s" % snap["store"])
    by = {}
    for i, at in snap["enrols"].items():
        c = by.setdefault(at[:10], {"intake": 0, "accepted": 0, "dropped": 0, "waiting": 0, "unresolved": 0, "unknown": 0})
        c["intake"] += 1
        s = (snap["states"].get(i) or {}).get("status")
        key = ("accepted" if s in ACCEPTED else "dropped" if s in DROPPED else "waiting" if s in WAITING
               else "unresolved" if s in UNRESOLVED else "unknown")
        c[key] += 1
    for c in by.values():
        c["yield"] = ratio(c["accepted"], c["intake"] - c["dropped"])
    return {"unit": "items (no per-obligation record exists)", "cohorts": dict(sorted(by.items()))}


def m_cost(snap):
    if snap["spend"] is None or snap["states"] is None:
        return um("no spend-*.json or no item states in %s" % snap["store"])
    groups = {"accepted": [], "unfinished": [], "dropped": []}
    role = {"work": 0, "check": 0, "stage": 0, "help": 0, "other": 0}
    mapped, unpriced, unpriced_acc = set(), 0, 0
    for i, st in snap["states"].items():
        mine = _units(snap["spend"], i)
        gens = {r["gen"] for r in (snap["attempts"] or {}).get(i, []) if r.get("start") is not None and "gen" in r}
        miss = sum("rm-relentless-work-%s-g%d" % (short(i), g) not in mine for g in gens)
        unpriced += miss                    # a started generation with no spend record: the totals are short by it
        unpriced_acc += bool(miss) and st.get("status") in ACCEPTED
        mapped.update(mine)
        s = st.get("status")
        groups["accepted" if s in ACCEPTED else "dropped" if s in DROPPED else "unfinished"].append(sum(mine.values()))
        for u, v in mine.items():
            k = u.split("-")[2] if u.startswith("rm-relentless-") else "other"
            role[k if k in role else "other"] += v
    acc = groups["accepted"]
    est = sum(v for u, v in snap["spend"].items() if u in mapped and (snap["basis"] or {}).get(u) == "estimated")
    return {"unit": "tokens", "accepted_items": len(acc), "accepted_spend": sum(acc),
            "per_accepted_item_own": round(sum(acc) / len(acc)) if acc else None,
            "per_accepted_item_all_in": round(sum(snap["spend"].values()) / len(acc)) if acc else None,
            "unfinished_spend": sum(groups["unfinished"]), "dropped_spend": sum(groups["dropped"]),
            "by_role": role, "unmapped_spend": sum(v for u, v in snap["spend"].items() if u not in mapped),
            "estimated_part": est, "unpriced_generations": unpriced, "accepted_items_with_unpriced_generations": unpriced_acc, "live_cost": UNMEASURED + ": live rounds keep no token or wall-clock spend record"}


def m_rebuild_waste(snap):
    """Product-worker spend on a generation launched after an end that was not a supported product attribution."""
    if snap["attempts"] is None or snap["spend"] is None:
        return um("no attempts or no spend record")
    waste, attributed, by_cause, unpriced = [0, 0], [0, 0], {}, 0
    for i, rows in snap["attempts"].items():
        last = None
        for r in rows:
            if r.get("end"):
                last = r
            elif r.get("start") is not None and r.get("gen", 1) > 1:
                cost = snap["spend"].get("rm-relentless-work-%s-g%d" % (short(i), r["gen"]))
                if cost is None:            # a generation with no spend record is unpriced, never free
                    unpriced += 1
                    cost = 0
                end = (last or {}).get("end") or "none"
                if end == "proof_weak" and ((last or {}).get("detail") or "").startswith("GAP:DIFF"):
                    end = "proof_weak:GAP:DIFF"
                prod = end in PRODUCT_ENDS or end == "proof_weak:GAP:DIFF"
                t = attributed if prod else waste
                t[0] += 1
                t[1] += cost
                if not prod:
                    c = by_cause.setdefault(end, [0, 0])
                    c[0] += 1
                    c[1] += cost
    return {"by_cause_columns": ["previous end", "rebuilds", "spend"], "product_ends": list(PRODUCT_ENDS) + ["proof_weak:GAP:DIFF"],
            "unattributed_rebuilds": waste[0], "unattributed_rebuild_spend": waste[1],
            "attributed_rebuilds": attributed[0], "attributed_rebuild_spend": attributed[1],
            "unpriced_rebuilds": unpriced,
            "by_cause": [[k, v[0], v[1]] for k, v in sorted(by_cause.items(), key=lambda kv: (-kv[1][1], kv[0]))]}


def m_availability(snap):
    if snap["shadow"] is None and snap["acts"] is None:
        return um("no verdict record (shadow.jsonl) and no journal")
    out = {}
    if snap["shadow"] is not None and snap["acts"] is not None:
        words = [r.get("word") for r in snap["shadow"]]
        ok = sum(w in VERDICT_OK for w in words)
        lost = snap["acts"].count("checker_lost") + snap["acts"].count("account_lost")
        out["checker"] = dict(ratio(ok, len(words) + lost), unmeasured=sum(w == "UNMEASURED" for w in words), lost=lost)
    else:
        out["checker"] = um("verdict record or journal missing")
    if snap["acts"] is not None:
        a = snap["acts"]
        good = a.count("game_implemented") + a.count("game_fail")
        bad = a.count("game_unmeasured") + a.count("game_refused") + a.count("game_stage_launch_failed")
        out["game"] = dict(ratio(good, good + bad), unmeasured=a.count("game_unmeasured"), refused=a.count("game_refused"),
                           launch_failed=a.count("game_stage_launch_failed"))
    else:
        out["game"] = um("no journal")
    if snap["attempts"] is not None:
        ends = [r.get("end") for rows in snap["attempts"].values() for r in rows if r.get("end")]
        # the worker's own proof run: a finish or a defect it found is a measurement. A checker outcome (proof_weak,
        # blind_fail) is the Marker's measurement and is counted once, under "checker", from the verdict record.
        fin = ends.count("finish") + ends.count("proof_found_defect")
        lost = ends.count("worker_lost") + ends.count("account_lost") + ends.count("proof_unrunnable")
        out["worker_proof"] = dict(ratio(fin, fin + lost), lost=lost)
    out["note"] = "an instrument failure is out of the accuracy denominators but its spend stays in cost and rebuild waste"
    return out


_NOISE = re.compile(r"[0-9a-f]{7,40}|\d+(\.\d+)?|/\S+")


def m_repeat_waste(snap):
    """An end repeating an earlier end of the same item (same class, same detail once shas, numbers and paths go)."""
    if snap["attempts"] is None:
        return um("no attempts record")
    n, spend, items, charged, unpriced = 0, 0, {}, set(), 0
    for i, rows in snap["attempts"].items():
        seen = set()
        for r in rows:
            if not r.get("end") or r["end"] in ("finish", "done", "unhold"):
                continue
            key = (r["end"], _NOISE.sub("#", r.get("detail") or ""))          # the whole detail: a shared prefix is not a repeat
            if key in seen:
                n += 1
                unit = "rm-relentless-work-%s-g%d" % (short(i), r.get("gen", 0))
                if unit not in charged:     # a generation's spend is charged once, however many repeats it ended
                    charged.add(unit)
                    if unit in (snap["spend"] or {}):
                        spend += snap["spend"][unit]
                    else:
                        unpriced += 1
                items[i] = items.get(i, 0) + 1
            seen.add(key)
    return {"repeats": n, "repeat_spend": spend if snap["spend"] is not None else UNMEASURED, "unpriced_repeat_gens": unpriced,
            "items": len(items), "worst": sorted(items.items(), key=lambda kv: -kv[1])[:5],
            "warrant": UNMEASURED + ": no retry-warrant record exists, so every repeat counts"}


def ons(row):
    """The blockers an attempt row names: `on` is one id or a list of them."""
    on = row.get("on")
    return [on] if isinstance(on, str) and on else [x for x in on if isinstance(x, str)] if isinstance(on, list) else []


def m_repair_leverage(snap):
    """Per blocker an item named (`on`): dependents blocked on it, restored after it closed, blocked on it again after.
    `repaired` means the blocker is a store item the supervisor accepted; a blocker outside the store never reads repaired."""
    if snap["attempts"] is None or snap["states"] is None:
        return um("no attempts or states")
    deps = {}
    for i, rows in snap["attempts"].items():
        for r in rows:
            for b in ons(r):
                deps.setdefault(b, []).append((i, ep(r["at"])))
    out = {}
    for b, lst in deps.items():
        bst = snap["states"].get(b) or {}
        fixed = bst.get("done_at") if bst.get("status") in ACCEPTED else None
        dep_items = sorted({i for i, _ in lst})
        restored = recur = 0
        for d in dep_items:
            if fixed is None or min(t for i, t in lst if i == d) >= fixed:
                continue                    # only a dependent blocked BEFORE the repair can be restored by it
            after = [r for r in snap["attempts"].get(d, []) if r.get("at") and ep(r["at"]) > fixed]
            restored += any(r.get("start") is not None or r.get("end") in ("finish", "done") for r in after)
            recur += any(b in ons(r) for r in after)
        out[b] = {"dependents": len(dep_items), "repaired": fixed is not None, "restored": restored, "recurred": recur}
    if not out:
        return um("no attempt names a blocker (`on`): there is nothing to count yet")
    rep = [v for v in out.values() if v["repaired"]]
    return {"blockers": len(out), "repaired": len(rep), "restored_per_repair": round(sum(v["restored"] for v in rep) / len(rep), 2)
            if rep else None, "recurred": sum(v["recurred"] for v in rep), "per_blocker": out}


def m_sensitivity(sens):
    if sens is None:
        return um("no seeded set (relentless_trust PRIVATE keys/E1.json) is readable here")
    cls = {c: {"caught": v["caught"], "n": v["n"], "ci95": v["ci"], "lost": v["lost"], "unrun": v["unrun"]}
           for c, v in sens["classes"].items()}
    ctl = sens["control"]
    return {"seeded_known_bad": cls, "false_rejection": {"false_fail": ctl["false_fail"], "n": ctl["n"], "ci95": ctl["ci"]},
            "unresolved_controls": ctl["lost"] + ctl["unrun"],
            "note": "seeded misses, kept apart from production escapes; finite controls are limited evidence"}


def m_debt(snap, now):
    if snap["states"] is None:
        return um("no item states")
    ages = []
    for i, st in snap["states"].items():
        if st.get("status") in WAITING:
            ts = [ep(r["at"]) for r in (snap["attempts"] or {}).get(i, []) if r.get("at")]
            ages.append(((now - max(ts)) / 86400.0 if ts else None, i, st["status"]))
    known = sorted(a for a, _, _ in ages if a is not None)
    return {"items": len(ages), "by_status": {s: sum(x[2] == s for x in ages) for s in WAITING},
            "median_age_days": round(statistics.median(known), 2) if known else None,
            "oldest": [(i, round(a, 1)) for a, i, _ in sorted((x for x in ages if x[0] is not None), reverse=True)[:5]],
            "priority": UNMEASURED + ": no business-priority field in the store"}


def age_bucket(days):
    for lim, name in AGES:
        if lim is None or days < lim:
            return name


def m_false_closes(audits):
    """Per sample and stratum, never pooled: drawn, audited, VIOLATED, HOLDS, UNMEASURED, by closure age at audit."""
    if not audits:
        return um("no audit has been drawn (%s)" % os.path.relpath(AUDITS, REPO))
    draws, verdicts, orphans = {}, {}, []
    for r in audits:
        if r["kind"] == "draw":
            draws[(r["sample"], r["stratum"], r["item"])] = r      # one item may sit in both populations
        elif r["kind"] == "audit":
            verdicts[(r["sample"], r["item"])] = r                 # the last audit of an item in a sample stands
    drawn = {(d["sample"], d["item"]) for d in draws.values()}
    orphans = sorted("%s/%s" % k for k in verdicts if k not in drawn)
    out = {"orphan_audits": orphans} if orphans else {}     # an audit whose draw is gone: the record is damaged
    for k, d in draws.items():
        s = out.setdefault(d["sample"], {}).setdefault(d["stratum"], {"drawn": 0, "audited": 0, "VIOLATED": 0, "HOLDS": 0,
                                                                       "UNMEASURED": 0, "by_age": {}, "violated": []})
        s["drawn"] += 1
        v = verdicts.get((d["sample"], d["item"]))
        if not v:
            continue
        s["audited"] += 1
        s[v["verdict"]] += 1
        if v["verdict"] == "VIOLATED":
            s["violated"].append(d["item"])
        b = s["by_age"].setdefault(age_bucket((ep(v["at"]) - ep(d["closed_at"])) / 86400.0) if d.get("closed_at") else "?",
                                   {"audited": 0, "VIOLATED": 0})
        b["audited"] += 1
        b["VIOLATED"] += v["verdict"] == "VIOLATED"
    for name, strata in out.items():
        if name == "orphan_audits":
            continue
        for s in strata.values():
            s["false_close_rate"] = ratio(s["VIOLATED"], s["VIOLATED"] + s["HOLDS"])
            s["unaudited"] = s["drawn"] - s["audited"]
    return out


def m_coverage(snap):
    """What the store let us read: an item with no state or no attempts record is named, so a count is never quietly
    short (its attempts are left out of rebuild and repeat waste, its state out of every status count)."""
    if snap["states"] is None:
        return um("no items directory in %s" % snap["store"])
    return {"states_read": len(snap["states"]), "unreadable_states": sorted(snap["unreadable"]),
            "no_attempts_record": len(snap["no_attempts"]), "no_attempts_items": sorted(snap["no_attempts"])[:20],
            "malformed_lines": {os.path.relpath(k, snap["store"]): v for k, v in sorted(snap.get("malformed", {}).items())}}


def compute(snap, audits, sens=None, now=None):
    now = now if now is not None else dt.datetime.now(dt.timezone.utc).timestamp()
    return {
        "at": iso(now),
        "source_coverage": m_coverage(snap),
        "accepted_delivery_yield": m_yield(snap),
        "end_to_end_cost": m_cost(snap),
        "rebuild_waste_before_attribution": m_rebuild_waste(snap),
        "instrument_availability": m_availability(snap),
        "repeat_waste": m_repeat_waste(snap),
        "attribution_reversal_rate": um("the supervisor keeps no attribution record to reverse "
                                        "(spec rank 1, the attribution transition, builds it)"),
        "diagnostic_time_to_attribution": um("no attribution record carries a time"),
        "repair_leverage": m_repair_leverage(snap),
        "validator_sensitivity": m_sensitivity(sens),
        "audited_false_closes": m_false_closes(audits),
        "unknown_validation_debt": m_debt(snap, now),
    }


# ---------------------------------------------------------------- the audit record (sample, audit)

def draw(snap, audits, n_random, seed, now, name=None):
    """-> rows for a new sample: every narrow-WEAK close no earlier sample targeted, and a seeded draw of n_random over every close
    (random; a narrow-WEAK close may land in both, it is counted in each population on its own)."""
    if snap["states"] is None:
        raise SystemExit("UNMEASURED: no item states in %s" % snap["store"])
    name = name or "S" + iso(now)[:10].replace("-", "")
    if any(r["sample"] == name for r in audits):
        raise SystemExit("sample %s exists; name another (--name)" % name)
    cl = closes(snap["states"])
    pool = sorted(cl)
    picks = random.Random(seed).sample(pool, min(n_random, len(pool)))
    pool_sha = hashlib.sha1("\n".join(pool).encode()).hexdigest()     # the draw is reproducible from seed + this pool
    rows = []
    done_before = {r["item"] for r in audits if r["kind"] == "draw" and r["stratum"] == "narrow_weak"}
    targeted = [i for i in narrow_weak(snap["states"]) if i not in done_before]     # a targeted close is audited once
    for stratum, items in (("narrow_weak", targeted), ("random", sorted(picks))):
        for i in items:
            st = snap["states"][i]
            c = st.get("contract") or {}
            rows.append({"kind": "draw", "sample": name, "stratum": stratum, "item": i, "at": iso(now), "seed": seed,
                         "population": len(pool), "population_sha1": pool_sha, "closed_at": iso(cl[i][0]) if cl[i][0] else None,
                         "sha": st.get("last_sha"), "verdict": cl[i][1], "proof": (c.get("proof") or "")[:600],
                         "reasons": cl[i][2][:300] if stratum == "narrow_weak" else None})
    return rows


STRATA = ("narrow_weak", "random")
NEEDS = {"draw": ("sample", "stratum", "item", "at"), "audit": ("sample", "item", "verdict", "by", "how", "evidence", "at")}


def damaged(rows, refs=True):
    """-> a reason per audit-record row that is not a well-formed draw or audit (a wrong verdict word, a missing field,
    an unparseable time) or, with refs, an audit whose draw is gone. A damaged record refuses writes and makes the report
    exit 2."""
    out = []
    for n, r in enumerate(rows, 1):
        need = NEEDS.get(r.get("kind")) if isinstance(r, dict) else None
        if need is None:
            out.append("row %d: kind is neither draw nor audit" % n)
            continue
        miss = [k for k in need if not r.get(k)]
        if miss:
            out.append("row %d: missing %s" % (n, ",".join(miss)))
        elif r["kind"] == "draw" and r["stratum"] not in STRATA:
            out.append("row %d: stratum %r" % (n, r["stratum"]))
        elif r["kind"] == "audit" and r["verdict"] not in VERDICTS:
            out.append("row %d: verdict %r" % (n, r["verdict"]))
        else:
            try:
                for k in ("at", "closed_at"):
                    if r.get(k):
                        ep(r[k])
            except (TypeError, ValueError):
                out.append("row %d: a time does not parse" % n)
    if not refs:
        return out
    drawn = {(r.get("sample"), r.get("item")) for r in rows if isinstance(r, dict) and r.get("kind") == "draw"}
    out += ["row %d: audit of %s/%s has no draw" % (n, r["sample"], r["item"]) for n, r in enumerate(rows, 1)
            if isinstance(r, dict) and r.get("kind") == "audit" and (r.get("sample"), r.get("item")) not in drawn]
    return out


def append(rows, path=AUDITS):
    if os.path.exists(path) and os.path.getsize(path):
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":                      # a record that lost its last newline: never glue onto it
                rows = [None] + list(rows)
    with open(path, "a", encoding="utf-8") as f:
        if rows and rows[0] is None:
            f.write("\n")
            rows = rows[1:]
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def audit_row(audits, sample, item, verdict, by, how, evidence, now):
    if verdict not in VERDICTS:
        raise SystemExit("verdict is one of %s" % ", ".join(VERDICTS))
    if not any(r["kind"] == "draw" and r["sample"] == sample and r["item"] == item for r in audits):
        raise SystemExit("%s is not drawn in sample %s" % (item, sample))
    if not (by and how and evidence):
        raise SystemExit("an audit names its auditor (--by), its method (--how) and what it showed (--evidence)")
    return {"kind": "audit", "sample": sample, "item": item, "verdict": verdict, "by": by, "how": how[:600],
            "evidence": evidence[:1200], "at": iso(now)}


# ---------------------------------------------------------------- report

def render(m):
    lines = ["# Delivery, measurement availability and false closes - %s" % m["at"], ""]
    for k, v in m.items():
        if k == "at":
            continue
        lines.append("## " + k.replace("_", " "))
        if isinstance(v, dict) and v.get("value") == UNMEASURED:
            lines.append("UNMEASURED - " + v["why"])
        else:
            lines.append("```")
            lines.append(json.dumps(v, indent=1, sort_keys=True))
            lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--audits", default=AUDITS)
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    s = sub.add_parser("sample")
    s.add_argument("--random", type=int, default=8)
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--name")
    a = sub.add_parser("audit")
    a.add_argument("sample")
    a.add_argument("item")
    a.add_argument("verdict")
    a.add_argument("--by", required=True)
    a.add_argument("--how", required=True)
    a.add_argument("--evidence", required=True)
    args = ap.parse_args(argv)
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    bad = {}
    audits = _jsonl(args.audits, bad)
    hurt = damaged(audits)
    if bad or hurt:
        sys.stderr.write("DAMAGED: %s: %d line(s) do not parse; %s - repair it before trusting a false-close rate\n"
                         % (args.audits, sum(bad.values()), "; ".join(hurt[:5]) or "no malformed row"))
        if not hurt:
            hurt = ["unparsed lines"]
        audits = [r for r in audits if not damaged([r], refs=False)]     # orphans stay: the report names them
        if args.cmd in ("sample", "audit"):
            return 2
    if args.cmd == "sample":
        rows = draw(load(args.store), audits, args.random, args.seed, now, args.name)
        append(rows, args.audits)
        for x in rows:
            print(x["sample"], x["stratum"], x["item"])
        return 0
    if args.cmd == "audit":
        append([audit_row(audits, args.sample, args.item, args.verdict.upper(), args.by, args.how, args.evidence, now)],
               args.audits)
        return 0
    m = compute(load(args.store), audits, sensitivity_source(), now)
    print(json.dumps(m, indent=1, sort_keys=True) if getattr(args, "json", False) else render(m))
    return 2 if bad or hurt else 0


if __name__ == "__main__":
    sys.exit(main())
