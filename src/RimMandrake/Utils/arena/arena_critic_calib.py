#!/usr/bin/env python3
r"""arena_critic_calib.py — critic calibration: false-reject and miss rates on known-good and planted-defect candidates.

Item ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST (build order 10; design/RimMandrake/testpilot_merged_2026-10-29.md
§6.3 day 2, flaws O2/O6; architecture_switch_harness_2026-10-29.md §3.2 planted defects, §4.1 decision rule).

    python3 src/RimMandrake/Utils/arena/arena_critic_calib.py build-set [--pool POOL.json] [--write]
    python3 src/RimMandrake/Utils/arena/arena_critic_calib.py run --critic l4-opus|accept-all|reject-all|MOD:ATTR
                                                                  --run RUN_ID [--concurrency N] [--max N]
    python3 src/RimMandrake/Utils/arena/arena_critic_calib.py score --run RUN_ID [--json]

WHAT IS MEASURED. One critic ROUND (the first verdict a fresh critic gives a finished candidate):
  false-reject rate = rejects / valid verdicts on KNOWN-GOOD candidates
  miss rate         = accepts / valid verdicts on PLANTED-DEFECT candidates
each with a Wilson 95% interval and the Beta(1,1) posterior tail P(rate >= threshold). These are the simulator's
`crit_fr` and `1 - crit_s` (src/RimMandrake/Utils/sim/testpilot_sim.py), both defined per round.

THE SET (fixtures/critic_calib_set.json, built by `build-set` from arena_tasks.census()):
  planted  a census ESCAPED item's original fix, exactly as it shipped: base_sha -> fix_sha. A later caused_by rework
           fixed a defect in it, so the candidate carries a REAL defect that a v2 review already missed (§3.2 "a past
           Escaped fix with its defect re-introduced": here it was never removed). Each records its rework item(s).
           Only Escaped items whose rework is a defect against the item's OWN criteria are kept (vetted by hand, the
           PLANTED table below says why for each); review-only, tuning, ops and design-choice reworks are excluded.
           Grade `strong` (the rework names a plain bug in what the item claimed) or `medium` (a gap a careful
           reviewer of this item should have raised); the miss rate is reported for both and for strong only.
  good     tier A: every census CLEAN item (a verify pass, no rework within 7 days). tier B: a seeded draw of
           UNLABELLED items whose 7-day label window has ENDED with no rework candidate at all; nobody verified
           them, so a tier-B reject may be a true find and a tier-B accept may hide a defect: the tier-B
           rejection rate is reported as a NOMINAL rate, never as false reject (it bounds nothing).
  Census window 2026-09-15..2026-10-29 (wider than the replay pool's 10-12..10-27, which holds only 8 Escaped and
  9 Clean): the planted set needs the Escaped items; the replay pool is not touched or re-frozen by this.

BLINDING. The critic sees only: the item's prompt and criteria (arena task text), the diff base..head through
arena_judge.neutralise() (the judge's neutraliser: trailers, sessions, shas, paths, arm and model names redacted, a
leak refuses the candidate), and a tree of head materialised by arena_judge.materialise() (no .git). It never sees
the role, the label, the rework, the run order or another candidate. It is told nothing about calibration. Order
is shuffled per run. Each call runs in bubblewrap with a FRESH empty $HOME (a copy of the Claude credentials only:
no CLAUDE.md, no memory, no transcripts), tmpfs over /home/<user> (every clone, the mirror, ~/.claude), /mnt (D:,
C:, the arena root, the read-only mirror) and /var/tmp (the other candidates' trees); only its own work dir is
writable; /run is hidden and pid/ipc/uts are unshared. The critic therefore cannot read the later history that holds
the rework. The network is its own namespace with one allow-listed route to the model API (arena_critic_relay); that route is a stated residual. The item text is refused when it
names the candidate's rework item, its arena task id, its base/head sha or a role word (ROLE_WORDS); the
source item's own name is allowed (a builder sees it). The work base is masked so no call sees another's work dir. A plug-in critic runs in-process and is only as blind
as its own review() makes it. A run is bound to its critic fingerprint (name, model, class source, prompt, sandbox)
and its set; a resume with a different one is refused, and one process holds a run's lock at a time. score marks a
run made before fingerprinting UNVERIFIED in its provenance field.

THE L4 CRITIC (testpilot_merged §2.1 L4; harness §2.1 `trio` row). The trio arm's critic
(ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKS, FOUNDRY) was NOT on origin/main when this was built (2026-10-30 04:12Z),
so `l4-opus` is this module's own reading of L4: a fresh Opus context (`claude -p --model opus`, no session
persistence) that reviews code, plan and offline evidence together and RUNS THE ITEM'S OFFLINE TESTS ITSELF (tools
Bash/Read/Grep/Glob in the sandboxed tree). The trio critic plugs in through the Critic interface:
`--critic package.module:attr`, where attr is a Critic instance or a zero-argument factory; its review(CriticInput)
returns a CriticVerdict. Re-measure with it once it lands; until then the numbers are for L4-as-specified.

DECISION (reliability()). False reject is measured on tier A plus the tier-B goods of a seeded both-outcomes label draw; miss on the predeclared planted set. More than
MAX_INVALID_FRAC invalid is UNMEASURED. Each measure FAILS when its Wilson-95 LOWER bound reaches the threshold (any
n), or, with at least MIN_GOOD / MIN_BAD valid verdicts, when its point estimate does; it is UNMEASURED below that
count, PASSES when its upper bound is under the threshold, else INCONCLUSIVE. Any FAIL is UNRELIABLE; RELIABLE needs
both to PASS. A reject-side adjudication (score --adjudication) is a favourable sensitivity reading, never a verdict. FR_MAX = 0.25 is the owner-accepted line (testpilot_merged O6: "if the critic rejects a quarter of
good small items, the honest answer is C+sub plus a sampled blind review"). MISS_MAX = 0.5 is THIS BUILDER'S
choice (no document fixes one): a critic that passes half of the defects a review already missed adds less than a
sampled blind review. Forced failure: accept-all (miss 1.0) and reject-all (false reject 1.0) are each UNRELIABLE.

RESIDUAL (stated). The tree is TREE_PATHS + the changed areas, not the whole repo: a test that needs a path outside
it, the game, Windows or the network fails for the environment, and the critic is told so; every false reject is
listed with its reasons for a human to read. C# cannot be compiled in the sandbox (no Windows build), so C#
candidates are judged by reading. Results are written under the calibration dir and noted to the rimflow ledger;
the signed arena event log (arena_eventlog.py) admits only its own ENTRYPOINTS, which this module is not.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import dataclasses
import fcntl
import glob
import datetime as dt
import hashlib
import importlib
import inspect
import json
import math
import os
import random
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Protocol

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402
import arena_judge as J  # noqa: E402
import arena_critic_relay as RELAY  # noqa: E402
import arm_sandbox as AS  # noqa: E402

SET_PATH = HERE / "fixtures" / "critic_calib_set.json"
CENSUS_WINDOW = ("2026-09-15", "2026-10-29")
FR_MAX = 0.25          # owner-accepted (testpilot_merged O6)
MISS_MAX = 0.50        # builder's choice, provisional (see docstring)
MIN_GOOD, MIN_BAD = 10, 5
MAX_INVALID_FRAC = 0.2
Z95 = 1.959964
CALL_TIMEOUT = 470     # one critic round, wall seconds (a foreground invocation must end under 540 s)
INLINE_DIFF_MAX = 120_000   # chars of diff put in the prompt; longer goes to a file
TREE_BLOB_MAX = 1_000_000       # bytes; a larger blob is left out of the critic's tree
TREE_TOTAL_MAX = 400_000_000    # bytes in one critic tree
MIN_CALL_S = 90       # a call with less wall time left than this is not started
MAX_USD = 8.0          # per-call spend cap passed to claude (a runaway call becomes invalid, never a verdict)
TIER_B = {"python-util": 9, "csharp": 6, "xml-def-patch": 4, "tooling": 2}
TIER_B_SEED = "critic-calib-2026-10-30"
TIER_B_CUTOFF = "2026-10-30T00:00:00Z"   # label window must have ended by this fixed time (reproducible draw)

# Escaped items vetted by hand (builder, 2026-10-30): the rework must name a defect against the item's OWN criteria.
PLANTED = {
    "RP_CHILLFIREBAN_FIX_UNLIT_REFUELABLE_BURNS_FUEL": ("strong", "fuel-freeze also froze powered machines for free"),
    "RP_CHILLPRINTS_FIX_MACHINE_SHADOW_NO_DEPOSIT": ("strong", "capped deposit propagates via TryMakeFilth default"),
    "RP_DELEGATED_DIGEST_FIX_NEVER_WRITTEN": ("strong", "free text reaches the blind digest; backlog lost on failure"),
    "RP_DISPATCHER_GOLIVE_FIX_THREE_BLOCKERS_FOUND": ("strong", "stop() timeout skips the kill; force never SIGKILLs"),
    "RP_MODCHECK_DRIVERS_FIX_BUDGET_KILL_MIDCALL": ("strong", "driver still hard-killed mid call at its own timeout"),
    "RP_ENACT_KEYED_FIX_UNREVIEWED": ("medium", "installs a pick at a lane no def draws; raw raise on missing snapshot"),
    "RP_ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE": ("medium", "a compare-vetoed ACCEPT is stuck: nothing installs/refiles"),
    "RP_NORTHSTAR_BRIDGE_UTILIZATION_1": ("medium", "ad-hoc bridge scripts leave no log, metric reads 3.1%"),
    "RP_ARTEVAL_REGEN_ROWS_FIX_MISSING_TARGET": ("medium", "regen rows took CLI error text as the image prompt"),
}
EXCLUDED = {   # Escaped in the census, NOT a defect against the item's own criteria (why kept in code: auditable)
    "RP_ART_SHEET_REFTEX_FIX_UNREVIEWED": "rework is a further full-file review, not a named defect",
    "RP_DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE": "reworks are cap tuning and a seat/gate decision",
    "RP_EVIDENCE_SEALS_HARDEN_STRIPPED_LOOKS_DELETED": "rework is a cutover clone-sync operation",
    "RP_SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1": "rework is a recipe design choice",
    "RP_THIRST_ROWS_HARDEN_FALSE_PASS_ROUTES": "rework diagnoses a game behaviour the hardened row exposed",
}


# ---------------------------------------------------------------- statistics

def wilson(k: int, n: int, z: float = Z95) -> tuple:
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def beta_tail(k: int, n: int, thr: float, steps: int = 20000) -> float:
    """P(rate >= thr) under the Beta(1+k, 1+n-k) posterior (uniform prior), by Simpson's rule in log space."""
    a, b = k + 1.0, n - k + 1.0
    lnorm = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)

    def f(x):
        if x <= 0.0 or x >= 1.0:
            return 0.0 if (x <= 0 and a > 1) or (x >= 1 and b > 1) else math.exp(-lnorm)
        return math.exp((a - 1) * math.log(x) + (b - 1) * math.log(1 - x) - lnorm)

    def simpson(lo, hi):
        if hi <= lo:
            return 0.0
        h = (hi - lo) / steps
        s = f(lo) + f(hi)
        for i in range(1, steps):
            s += f(lo + i * h) * (4 if i % 2 else 2)
        return s * h / 3
    return min(1.0, max(0.0, simpson(thr, 1.0)))


def rate(k: int, n: int, thr: float) -> dict:
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n) if n else None, "wilson95": [round(lo, 4), round(hi, 4)],
            "p_at_or_above_threshold": round(beta_tail(k, n, thr), 4) if n else None, "threshold": thr}


def verdict_of(results: list[dict], cids) -> dict:
    """The verdict record that counts per candidate: the first valid one; an invalid record never replaces a
    valid one (run() retries only invalid candidates, so a candidate has at most one valid verdict)."""
    out: dict[str, dict] = {}
    for r in results:
        if r.get("cid") not in cids:
            continue
        prev = out.get(r["cid"])
        if prev is None or (prev.get("verdict") not in J.VERDICTS and r.get("verdict") in J.VERDICTS):
            out[r["cid"]] = r
    return out


def tierb_sample(set_doc: dict, seed: str, n: int) -> list[str]:
    """The labelled tier-B draw: it depends on the seed alone, so it cannot have been chosen by outcome."""
    cids = [c["cid"] for c in set_doc["candidates"] if c.get("tier") == "B"]
    return sorted(cids, key=lambda c: hashlib.sha256((seed + c).encode()).hexdigest())[:n]


def tierb_labels(set_doc: dict, labels: dict | None = None) -> dict:
    """{cid: finding} of the shipped both-outcomes tier-B labels ({} on another set). Unlike a reject-side adjudication
    this covers accepts too, so a sampled good joins the false-reject denominator; a sampled true_defect or
    bad_candidate is simply not a labelled good. A label set that is not exactly the seeded draw is refused."""
    if labels is None:
        labels = json.loads(TIERB_LABELS_PATH.read_text())
    if labels.get("set_sha256") != set_doc.get("set_sha256"):
        return {}
    got = labels["labels"]
    if sorted(got) != sorted(tierb_sample(set_doc, labels["seed"], labels["n"])):
        raise A.ArenaError("tier-B labels are not the seeded draw: an unbiased sample cannot be edited")
    for cid, row in got.items():
        if row.get("finding") not in TIERB_FINDINGS or not row.get("evidence"):
            raise A.ArenaError("tier-B label %s: finding must be one of %s, with evidence" % (cid, TIERB_FINDINGS))
    return {cid: row["finding"] for cid, row in got.items()}


def score(set_doc: dict, results: list[dict], labels: dict | None = None) -> dict:
    """First valid verdict per candidate counts; a candidate with no valid verdict counts as invalid."""
    by = {c["cid"]: c for c in set_doc["candidates"]}
    latest = verdict_of(results, by)
    found = tierb_labels(set_doc, labels)
    cells = {"good": [], "good_A": [], "good_B": [], "good_labelled": [], "planted": [], "planted_strong": []}
    invalid = []
    false_rejects, misses = [], []
    for cid, c in by.items():
        r = latest.get(cid)
        if r is None or r["verdict"] not in J.VERDICTS:
            invalid.append(cid)
            continue
        if c["role"] == "good":
            bad = r["verdict"] == "reject"
            cells["good"].append(bad)
            cells["good_" + c["tier"]].append(bad)
            if c["tier"] == "A" or found.get(cid) == "good":
                cells["good_labelled"].append(bad)
            if bad:
                false_rejects.append({"cid": cid, "task": c["task"], "tier": c["tier"], "reasons": r.get("reasons")})
        else:
            bad = r["verdict"] == "accept"
            cells["planted"].append(bad)
            if c["grade"] == "strong":
                cells["planted_strong"].append(bad)
            if bad:
                misses.append({"cid": cid, "task": c["task"], "grade": c["grade"], "rework": c["rework_items"]})
    out = {"false_reject": rate(sum(cells["good_labelled"]), len(cells["good_labelled"]), FR_MAX),   # tier A + labelled
           "false_reject_tierA_only": rate(sum(cells["good_A"]), len(cells["good_A"]), FR_MAX),
           "tierb_labels": {f: sum(v == f for v in found.values()) for f in TIERB_FINDINGS},
           "reject_rate_tierB_unlabelled": rate(sum(cells["good_B"]), len(cells["good_B"]), FR_MAX),
           "reject_rate_all_good_nominal": rate(sum(cells["good"]), len(cells["good"]), FR_MAX),
           "miss": rate(sum(cells["planted"]), len(cells["planted"]), MISS_MAX),
           "miss_strong_only": rate(sum(cells["planted_strong"]), len(cells["planted_strong"]), MISS_MAX),
           "invalid": len(invalid), "invalid_cids": sorted(invalid), "candidates": len(by),
           "false_rejects": false_rejects, "misses": misses}
    out["reliability"] = reliability(out)
    return out


ADJ_PATH = HERE / "fixtures" / "critic_calib_adjudication.json"
TIERB_LABELS_PATH = HERE / "fixtures" / "critic_calib_tierb_labels.json"
TIERB_FINDINGS = ("good", "true_defect", "bad_candidate")
ADJ_FINDINGS = ("true_defect", "bad_candidate", "false_reject")


def adjudicate(set_doc: dict, adj: dict, results: list[dict]) -> dict:
    """Return a copy of set_doc corrected by a reject-side adjudication.

    true_defect: a 'good' candidate the critic rejected was really defective (later history proves it), so it
    becomes a planted candidate (grade 'found') and the reject counts as a catch. bad_candidate: the diff is not
    the item's work (wrong census commit, or the critic's tree could not show what the item delivered), so it
    leaves both denominators. false_reject: unchanged. Only rejected good candidates may be adjudicated. An
    adjudication that covers accepts too would be a different (unbiased) instrument; this one is biased toward
    the critic, and the caller must say so."""
    if adj.get("set_sha256") != set_doc["set_sha256"]:
        raise A.ArenaError("adjudication is for set %s, not %s" % (adj.get("set_sha256"), set_doc["set_sha256"]))
    by = {c["cid"]: c for c in set_doc["candidates"]}
    verdict = {cid: r.get("verdict") for cid, r in verdict_of(results, by).items()}
    out, drop = dict(set_doc), set()
    cands = {cid: dict(c) for cid, c in by.items()}
    for cid, a in adj["cids"].items():
        c = by.get(cid)
        if c is None or c["role"] != "good":
            raise A.ArenaError("adjudicated %s is not a good candidate in this set" % cid)
        if a.get("finding") not in ADJ_FINDINGS:
            raise A.ArenaError("adjudicated %s: finding %r not one of %s" % (cid, a.get("finding"), ADJ_FINDINGS))
        if verdict.get(cid) != "reject":
            raise A.ArenaError("adjudicated %s was not rejected in these results (reject-side adjudication only)"
                               % cid)
        if not a.get("evidence"):
            raise A.ArenaError("adjudicated %s has no evidence" % cid)
        if a["finding"] == "true_defect":
            cands[cid].update(role="planted", grade="found", defect=a["evidence"])
        elif a["finding"] == "bad_candidate":
            drop.add(cid)
    out["candidates"] = [cands[c["cid"]] for c in set_doc["candidates"] if c["cid"] not in drop]
    return out


def score_adjudicated(set_doc: dict, results: list[dict], adj: dict) -> dict:
    """A favourable SENSITIVITY reading, never a verdict: the true defects it adds to the planted side were selected
    because the critic caught them, so its intervals are not calibrated for the predeclared planted population."""
    s = score(adjudicate(set_doc, adj, results), results)
    n = {f: sum(1 for a in adj["cids"].values() if a["finding"] == f) for f in ADJ_FINDINGS}
    s["adjudication"] = dict(n, scope=adj.get("scope", ""), biased_toward_critic=True)
    s["reliability"] = {"verdict": "SENSITIVITY-ONLY", "why": "outcome-selected adjudication; the decision is the "
                        "raw score's. Under the same rule this reading would be: " + reliability(s)["why"]}
    return s


def _measure(m: dict, thr: float, need: int) -> tuple:
    if m["n"] and m["wilson95"][0] >= thr:
        return "FAIL", "lower bound %.3f >= %.2f (%d/%d)" % (m["wilson95"][0], thr, m["k"], m["n"])
    if m["n"] >= need and m["rate"] >= thr:
        return "FAIL", "point %.3f >= %.2f (%d/%d)" % (m["rate"], thr, m["k"], m["n"])
    if m["n"] < need:
        return "UNMEASURED", "%d valid (need %d)" % (m["n"], need)
    if m["wilson95"][1] < thr:
        return "PASS", "upper bound %.3f < %.2f" % (m["wilson95"][1], thr)
    return "INCONCLUSIVE", "point %.3f < %.2f but upper bound %.3f is not" % (m["rate"], thr, m["wilson95"][1])


def reliability(s: dict) -> dict:
    """False reject is measured on labelled goods (tier A, tier-B label draw): a tier-B rejection rate is neither a bound
    nor an estimate of it, because a defective unlabelled candidate moves numerator and denominator alike."""
    total = s["candidates"]
    if total and s["invalid"] / total > MAX_INVALID_FRAC:
        return {"verdict": "UNMEASURED", "why": "invalid %d of %d (> %.0f%%)" % (s["invalid"], total,
                                                                               100 * MAX_INVALID_FRAC)}
    parts = {"false_reject": _measure(s["false_reject"], FR_MAX, MIN_GOOD),
             "miss": _measure(s["miss"], MISS_MAX, MIN_BAD)}
    why = "; ".join("%s %s: %s" % (k, v[0], v[1]) for k, v in parts.items())
    st = {v[0] for v in parts.values()}
    verdict = ("UNRELIABLE" if "FAIL" in st else "UNMEASURED" if "UNMEASURED" in st
               else "RELIABLE" if st == {"PASS"} else "INCONCLUSIVE")
    return {"verdict": verdict, "why": why, "parts": {k: v[0] for k, v in parts.items()}}


# ---------------------------------------------------------------- the set

def _cid(seed: str, task: str) -> str:
    return "c" + hashlib.sha256((seed + "\0" + task).encode()).hexdigest()[:10]


def hidden_code(repo: Path, base: str, head: str, area: list) -> list:
    """In-area changed files the neutraliser strips as bookkeeping (.claude/, AGENTS.md, ...): when one is CODE the
    critic would judge a change it cannot see, so the candidate is not judgeable blind."""
    with J.SafeRepo(Path(repo)) as g:
        names = J._z(g.git("diff", *J.DIFF_SAFE, "--name-only", "-z", base, head, "--"))
    return [x for x in names if J.in_area(x, area) and J.is_arm_bookkeeping(x)
            and x.endswith((".py", ".cs", ".sh", ".xml", ".json", ".js", ".ts", ".ps1"))]


def build_set(pool: list, cutoff: str = TIER_B_CUTOFF, repo: Path | None = None) -> dict:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    by = {t["id"]: (t, h) for t, h in pool}
    cands = []

    def entry(t, h, role, **kw):
        e = {"cid": _cid(TIER_B_SEED, t["id"]), "role": role, "task": t["id"], "source_item": t["source_item"],
             "kind": t["kind"], "size": t["size"], "base": t["base_sha"], "head": h["fix_sha"], "area": t["area"],
             "prompt": t["prompt"], "criteria": t["criteria"]}
        e.update(kw)
        return e
    escaped = sorted(i for i, (t, h) in by.items() if h["label"] == "Escaped")
    unvetted = [i for i in escaped if i not in PLANTED and i not in EXCLUDED]
    if unvetted:
        raise A.ArenaError("Escaped items not vetted (add to PLANTED or EXCLUDED): %s" % ", ".join(unvetted))
    for i in sorted(PLANTED):
        if i not in by:
            raise A.ArenaError("vetted planted item %s is not in the census pool: the census changed" % i)
        t, h = by[i]
        if h["label"] != "Escaped":
            raise A.ArenaError("vetted planted item %s is no longer Escaped (%s)" % (i, h["label"]))
        grade, why = PLANTED[i]
        cands.append(entry(t, h, "planted", grade=grade, defect=why,
                           rework_items=[r["item"] for r in h["reworks"]],
                           rework_fix_shas=[r.get("fix_sha") for r in h["reworks"]]))
    for i, (t, h) in sorted(by.items()):
        if h["label"] == "Clean":
            cands.append(entry(t, h, "good", tier="A"))
    elig = {}
    for i, (t, h) in sorted(by.items()):
        if (h["label"] is None and not h.get("rework_candidates") and not h.get("label_pending")
                and h.get("label_window_ends", "9") < cutoff):
            elig.setdefault(t["kind"], []).append(i)
    rng = random.Random(TIER_B_SEED)
    hidden_out = {}
    rests: dict[str, list] = {}
    for kind, n in sorted(TIER_B.items()):
        ids = elig.get(kind, [])
        if len(ids) < n:
            raise A.ArenaError("tier B needs %d %s items, the census has %d eligible" % (n, kind, len(ids)))
        drawn = rng.sample(ids, n)
        rest = rests[kind] = [i for i in ids if i not in drawn]
        for k, i in enumerate(drawn):          # a hidden change is replaced by the next seeded draw, the rest stay
            while repo is not None and hidden_code(repo, by[i][0]["base_sha"], by[i][1]["fix_sha"], by[i][0]["area"]):
                hidden_out[i] = hidden_code(repo, by[i][0]["base_sha"], by[i][1]["fix_sha"], by[i][0]["area"])
                if not rest:                   # stratum spent: spill to the largest stratum already drawn
                    rest = max(rests.values(), key=len)
                    if not rest:
                        raise A.ArenaError("tier B ran out of items the neutraliser does not hide")
                i = rest.pop(rng.randrange(len(rest)))
            drawn[k] = i
        for i in sorted(drawn):
            t, h = by[i]
            cands.append(entry(t, h, "good", tier="B"))
    for c in cands:
        if c.get("tier") != "B" and repo is not None and hidden_code(repo, c["base"], c["head"], c["area"]):
            raise A.ArenaError("%s: the neutraliser hides part of the change (%s); vet it out by hand"
                               % (c["task"], hidden_code(repo, c["base"], c["head"], c["area"])))
    doc = {"item": "ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST", "built": now, "census_window": list(CENSUS_WINDOW),
           "tier_b_seed": TIER_B_SEED, "tier_b_cutoff": cutoff, "tier_b_replaced_hidden": hidden_out, "excluded_escaped": EXCLUDED,
           "counts": {"planted": sum(c["role"] == "planted" for c in cands),
                      "planted_strong": sum(c.get("grade") == "strong" for c in cands),
                      "good_A": sum(c.get("tier") == "A" for c in cands),
                      "good_B": sum(c.get("tier") == "B" for c in cands)},
           "candidates": cands}
    doc["set_sha256"] = hashlib.sha256(json.dumps(cands, sort_keys=True).encode()).hexdigest()
    return doc


def load_set(path: Path = SET_PATH) -> dict:
    doc = json.loads(Path(path).read_text())
    h = hashlib.sha256(json.dumps(doc["candidates"], sort_keys=True).encode()).hexdigest()
    if h != doc["set_sha256"]:
        raise A.ArenaError("calibration set %s changed since it was built (hash mismatch)" % path)
    return doc


# ---------------------------------------------------------------- the critic interface

@dataclasses.dataclass
class CriticInput:
    cid: str                 # opaque; says nothing about role
    prompt: str              # the item's spec (plan)
    criteria: str
    diff: str                # neutralised (arena_judge.neutralise)
    tree: Path | None        # head materialised (arena_judge.materialise); None for stand-in critics
    work: Path | None        # the call's own writable dir (tree lives under it)


@dataclasses.dataclass
class CriticVerdict:
    verdict: str             # accept | reject | invalid
    reasons: list
    meta: dict


class Critic(Protocol):
    name: str
    needs_tree: bool

    def review(self, c: CriticInput) -> CriticVerdict: ...


class AcceptAll:
    name, needs_tree = "accept-all", False

    def review(self, c):
        return CriticVerdict("accept", ["stand-in: accepts everything"], {})


class RejectAll:
    name, needs_tree = "reject-all", False

    def review(self, c):
        return CriticVerdict("reject", ["stand-in: rejects everything"], {})


L4_PROMPT = """You are the blind critic gate for one work item in a software project (a suite of RimWorld mods and
the Python tooling around them). A builder has finished the item. You are a fresh reviewer: you did not build it
and you are not told who did.

Review the code, the plan and the offline evidence TOGETHER, then give one verdict.
- The plan: the item's spec and acceptance criteria, below.
- The code: the diff below. Identities in it are redacted (<ARM>, <MODEL>, <SHA>, <REPO>, <TRAILER>); that is
  normal and is not a defect.
- The offline evidence: produce it yourself. Your current directory is the working tree AFTER the change (only the
  tooling packages under src/RimMandrake/Utils and src/RimMandrake/rimflow plus the changed areas; there is no .git).
  Run the item's offline tests: for Python, the selftests the change adds or touches and any others that exercise
  the changed code (`python3 path/to/selftest_x.py` from the tree root). There is no game, no Windows and no
  network here, so a C# change cannot be compiled: judge it by reading. A test that fails only because a path
  outside this tree, the game, Windows or the network is missing is an environment limit, not a defect; say so.

Accept when the change delivers the item's criteria and you found no defect that matters.
Reject when you find a concrete defect: a test fails because of the change, a criterion is not met, or a bug that
would make the item wrong in use. Do not reject for style, taste, or wishes beyond the item's scope. When you
reject, name each defect specifically (file, behaviour, why it breaks the criteria).

End your answer with exactly one JSON object and nothing after it:
{{"verdict": "accept" or "reject", "reasons": ["..."]}}

=== ITEM SPEC (plan) ===
{prompt}

=== ACCEPTANCE CRITERIA ===
{criteria}

=== DIFF (neutralised) ===
{diff}
"""


def sandbox_argv(argv: list, work: Path, cwd: Path, model_route: bool = True) -> list:
    """bwrap: read-only root, fresh /tmp, own pid/ipc/uts/net namespaces; tmpfs over /home (clones, mirror, ~/.claude),
    /mnt (D:, C:, the arena root), /var/tmp (the other candidates) and /run (host service sockets); the claude binary
    and THIS call's work dir bound back. Nothing else is writable. The network namespace holds only lo: the model API
    is reached through arena_critic_relay's allow-listed socket (model_route=False: no way out at all), so loopback
    services, the Windows host and the rest of the internet are gone. arm_sandbox's seccomp program refuses AF_VSOCK
    (no namespace covers it) and io_uring."""
    bw = shutil.which("bwrap")
    if not bw:
        raise J.JudgeUnavailable("bwrap not found: the critic never runs unsandboxed")
    home = Path(os.path.realpath(Path.home()))
    out = [bw, "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp",
           "--tmpfs", "/home", "--tmpfs", "/mnt", "--tmpfs", "/var/tmp", "--tmpfs", "/run"]
    if not str(home).startswith("/home/"):
        out += ["--tmpfs", str(home)]
    masked = ("/home/", "/mnt/", "/var/tmp/", "/tmp/", str(home) + "/")
    for what, p in (("repo", A.REPO), ("arena root", A.arena_root())):
        if not (os.path.realpath(p) + "/").startswith(masked):
            raise J.JudgeUnavailable("the %s %s is outside every masked directory: the critic could read it" % (what, p))
    out += ["--tmpfs", str(work_base())]          # the other candidates' work dirs, wherever ARENA_CRITIC_WORK points
    try:
        AS._prereq()
        rel = RELAY.relay(work_base()) if model_route else None
        bpf = AS._bpf_file()
    except (RELAY.RelayRefused, AS.SandboxRefused, OSError) as e:
        raise J.JudgeUnavailable("critic network refused: %s" % e)
    for p in (str(home / ".local" / "bin"), str(home / ".local" / "share" / "claude")):
        if os.path.exists(p):
            out += ["--ro-bind", p, p]
    if rel:
        out += ["--ro-bind", rel.path, rel.path]
    out += ["--bind", str(work), str(work), "--unshare-net", "--unshare-pid", "--unshare-ipc", "--unshare-uts",
            "--new-session", "--die-with-parent", "--seccomp", "3", "--chdir", str(cwd), "--"]
    if rel:
        out += ["/usr/bin/python3", "-I", "-c", RELAY.BRIDGE, rel.path]
    return ["/bin/sh", "-c", 'exec 3<"$1" && /bin/rm -f "$1" && shift && exec "$@"', "sh", bpf] + out + list(argv)


class L4OpusCritic:
    """L4 as specified: a fresh Opus context per round that runs the offline tests itself (tools in the sandbox)."""
    name, needs_tree = "l4-opus", True

    def __init__(self, model: str | None = None, timeout: int = CALL_TIMEOUT, max_usd: float = MAX_USD,
                 exe: list | None = None, persist_sessions: bool = False):
        self.model = model or os.environ.get("ARENA_CRITIC_MODEL", "opus")
        # True (trio's arena critic): the session transcript is kept in work/home/.claude/projects, where
        # helper_capture copies it for the spend meter before trio deletes the work dir
        self.persist_sessions = bool(persist_sessions)
        self.timeout, self.max_usd = timeout, max_usd
        self.deadline: float | None = None       # set by run(): no call outlives the invocation's wall budget
        self.exe = exe or [shutil.which("claude") or "claude"]

    def review(self, c: CriticInput) -> CriticVerdict:
        home = c.work / "home"
        (home / ".claude").mkdir(parents=True, exist_ok=True)
        cred = Path.home() / ".claude" / ".credentials.json"
        if cred.exists():
            shutil.copy2(cred, home / ".claude" / ".credentials.json")
        diff = c.diff
        if len(diff) > INLINE_DIFF_MAX:          # too big to inline: the critic reads it from its work dir
            (c.work / "change.diff").write_text(diff)
            diff = ("(%d lines, too long to inline: it is in the file ../change.diff relative to your current "
                    "directory; read it in parts)" % diff.count("\n"))
        prompt = L4_PROMPT.format(prompt=c.prompt.strip(), criteria=c.criteria.strip(), diff=diff)
        argv = self.exe + ["-p", "--model", self.model, "--output-format", "json",
                           "--tools", "Bash,Read,Grep,Glob", "--dangerously-skip-permissions", "--strict-mcp-config",
                           "--disable-slash-commands"] + ([] if self.persist_sessions else ["--no-session-persistence"]) + [
                           "--max-budget-usd", str(self.max_usd)]
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin:" + str(Path.home() / ".local" / "bin"), "HOME": str(home),
               "LANG": "C.UTF-8", "USER": os.environ.get("USER", "u"), "TERM": "dumb",
               "RM_GPT_CALL_LOG": str(c.work / "gpt") + "/"}   # a GPT call it makes lands where helper_capture reads
        (c.work / "gpt").mkdir(exist_ok=True)
        for k, v in os.environ.items():            # proxy / CA settings only; never ARENA_*, RM_*, or a session id
            if k in ("SSL_CERT_FILE", "SSL_CERT_DIR", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "https_proxy",
                     "http_proxy", "no_proxy"):
                env[k] = v
        t0 = time.time()
        timeout = self.timeout
        if self.deadline is not None:
            timeout = min(timeout, self.deadline - t0)
            if timeout < MIN_CALL_S:
                return CriticVerdict("invalid", ["skipped: the invocation's wall budget is spent"], {"skipped": True})
        proc = subprocess.Popen(sandbox_argv(argv, c.work, c.tree), cwd="/", stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
        try:
            out, err = proc.communicate(prompt.encode("utf-8"), timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = proc.communicate()
            rc = 124
        meta = {"rc": rc, "wall_s": round(time.time() - t0, 1), "model_arg": self.model}
        if rc == 124 and timeout < self.timeout:
            meta["budget_cut"] = True            # cut by the invocation budget, not the critic's own limit: retried
        try:
            d = json.loads(out.decode("utf-8", "replace"))
        except ValueError:
            meta["stderr_tail"] = err.decode("utf-8", "replace")[-400:]
            return CriticVerdict("invalid", ["no JSON envelope from claude (rc %d)" % rc], meta)
        mu = d.get("modelUsage") or {}
        meta.update({"cost_usd": d.get("total_cost_usd"), "turns": d.get("num_turns"), "is_error": d.get("is_error"),
                     "models": sorted(mu), "tokens": sum(int(v.get(k) or 0) for v in mu.values() for k in
                                                         ("inputTokens", "outputTokens", "cacheReadInputTokens",
                                                          "cacheCreationInputTokens"))})
        if rc != 0 or d.get("is_error"):
            return CriticVerdict("invalid", ["claude error: %s" % str(d.get("result"))[:300]], meta)
        ans = J.parse_answer(d.get("result") or "", ())
        meta["answer_tail"] = (d.get("result") or "")[-1500:]
        return CriticVerdict(ans["verdict"], ans.get("reasons") or [ans.get("why")], meta)


def critic_fingerprint(critic: Critic) -> str:
    """What a run is bound to: the critic's name, its class source, its instance configuration (model, timeout,
    budget...), the resolved executable, the L4 prompt, the sandbox code and what it is shown (prepare, the tree). A resumed run whose critic differs in
    any of these is refused. The model is the REQUESTED alias; the resolved version is in each result's meta.
    Contract for a plug-in: everything that changes its reviews must be a scalar instance attribute or in its class
    source (containers are treated as run state and ignored)."""
    exe = getattr(critic, "exe", None)
    exe_id = os.path.realpath(shutil.which(exe[0]) or exe[0]) + "\0" + "\0".join(exe[1:]) if exe else ""
    scalar = (str, int, float, bool, type(None))
    config = sorted((k, repr(v)) for k, v in vars(critic).items()     # configuration, not mutable run state
                    if k not in ("deadline", "exe") and isinstance(v, scalar)) if hasattr(critic, "__dict__") else []
    parts = [critic.name, getattr(critic, "model", "") or "", str(getattr(critic, "max_usd", "")), L4_PROMPT,
             inspect.getsource(sandbox_argv), inspect.getsource(prepare), inspect.getsource(critic_tree_files),
             inspect.getsource(unchanged_assets), inspect.getsource(asset_roots), inspect.getsource(RELAY), exe_id,
             repr(config)]
    try:
        parts.append(inspect.getsource(type(critic)))
    except (OSError, TypeError):
        parts.append(repr(type(critic)))
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()


def load_critic(spec: str) -> Critic:
    """A plug-in critic (package.module:attr) runs IN this process: it is only as blind and as sandboxed as its own
    review() makes it (L4OpusCritic sandboxes itself; a plug-in must do the same before its numbers count)."""
    if spec == "accept-all":
        return AcceptAll()
    if spec == "reject-all":
        return RejectAll()
    if spec == "l4-opus":
        return L4OpusCritic()
    mod, _, attr = spec.partition(":")
    if not mod or not attr:
        raise SystemExit("--critic must be l4-opus, accept-all, reject-all or package.module:attr")
    obj = getattr(importlib.import_module(mod), attr)
    obj = obj() if inspect.isclass(obj) or (callable(obj) and not hasattr(obj, "review")) else obj
    for k in ("name", "needs_tree", "review"):
        if not hasattr(obj, k):
            raise SystemExit("critic %s has no %r: it does not implement the Critic interface" % (spec, k))
    return obj


# ---------------------------------------------------------------- running

def calib_root() -> Path:
    return A.arena_root() / "calibration" / "critic"


def work_base() -> Path:
    return Path(os.environ.get("ARENA_CRITIC_WORK", "/var/tmp/rm_critic_calib"))


def text_area(repo: Path, c: dict) -> tuple:
    """The judge's neutraliser refuses a binary change outright (it cannot be judged blind). For the critic a binary
    (a compiled DLL beside its C# source, a texture) carries nothing a reviewer reads, so the diff is narrowed to the
    candidate's changed TEXT files inside its area, and the binaries are listed by (scrubbed) name only."""
    with J.SafeRepo(Path(repo)) as g:
        out = g.git("diff", *J.DIFF_SAFE, "--numstat", "-z", c["base"], c["head"], "--")
    text, binaries = [], []
    for rec in out.split(b"\0"):
        if not rec:
            continue
        add, dele, path = rec.decode("utf-8", "surrogateescape").split("\t", 2)
        if not J.in_area(path, c["area"]) or J.is_arm_bookkeeping(path):
            continue
        (binaries if (add, dele) == ("-", "-") else text).append(path)
    return sorted(text), sorted(binaries)


SIBLING_ROOTS = ("src/RimMandrake", "src")   # where a changed selftest's other mods live (mods/TheSump, ../RimStarWars)
SIBLING_TEXT = (".xml", ".cs", ".py", ".json", ".txt", ".md", ".csv")
SIBLING_DIR_MAX = 30_000_000   # bytes of one referenced sibling directory (RimStarWars is far bigger: text only, to this)


def referenced_sibling_dirs(repo: Path, head: str, changed: list) -> set:
    """Directories a changed text file names by quoted path component ("TheSump", "RimStarWars") that sit under
    SIBLING_ROOTS. A selftest reads its neighbours' defs and sources; without them it crashes on FileNotFoundError and
    the tester rejects a sound change for a gap in its own sandbox (TESTER_PROMPT_TUNE_REJECTS_MOST_GOOD_WORK)."""
    names = {}
    with J.SafeRepo(Path(repo)) as g:
        for root in SIBLING_ROOTS:
            out = g.git("ls-tree", "-d", "--name-only", "-z", head, root + "/")
            for rec in out.split(b"\0"):
                if rec:
                    d = rec.decode("utf-8", "surrogateescape")
                    if d != "src/RimMandrake":
                        names.setdefault(d.rsplit("/", 1)[-1], d)
        found = set()
        for path in changed:
            if not path.endswith(SIBLING_TEXT):
                continue
            try:
                body = g.git("show", "%s:%s" % (head, path)).decode("utf-8", "replace")
            except Exception:
                continue
            for n in names:
                if n not in found and re.search(r"""["'/\\]%s["'/\\]""" % re.escape(n), body):
                    found.add(n)
    return {names[n] for n in found}


def critic_tree_files(repo: Path, head: str, changed: list) -> list:
    """The files the critic's tree holds: the tooling packages (TREE_PATHS) and the directory of each changed text
    file, minus blobs over TREE_BLOB_MAX and anything under Transient/ or deployed/ (savegames, meshes: gigabytes
    no reviewer reads). The changed files themselves are always kept. Capped at TREE_TOTAL_MAX bytes."""
    dirs = set(J.TREE_PATHS) | {str(Path(p).parent) for p in changed if str(Path(p).parent) not in ("", ".")}
    sib = referenced_sibling_dirs(repo, head, changed)
    dirs |= sib
    sib_used = {d: 0 for d in sib}
    with J.SafeRepo(Path(repo)) as g:
        out = g.git("ls-tree", "-r", "-l", "-z", "--full-tree", head, "--", *sorted(dirs))
    keep, total = set(changed), 0
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, _, name = rec.partition(b"\t")
        mode, typ, _sha, size = meta.decode().split()
        path = name.decode("utf-8", "surrogateescape")
        if typ != "blob" or path in keep or path.startswith(("Transient/", "deployed/")):
            continue
        if size == "-" or int(size) > TREE_BLOB_MAX or total + int(size) > TREE_TOTAL_MAX:
            continue
        sd = next((d for d in sib if path.startswith(d + "/")), None)
        if sd is not None and not any(path.startswith(t + "/") for t in J.TREE_PATHS):
            near = any(path.startswith(str(Path(p).parent) + "/") for p in changed)
            if not near:
                if not path.endswith(SIBLING_TEXT) or sib_used[sd] + int(size) > SIBLING_DIR_MAX:
                    continue
                sib_used[sd] += int(size)
        keep.add(path)
        total += int(size)
    return sorted(keep)


ASSET_LIST = "unchanged_assets.txt"     # in the work dir, beside the tree: the critic greps it instead of trusting `ls`


def asset_roots(changed: list) -> list:
    """The mod of each changed file (src/<tier>/<mod>), or its directory outside src/: where a change's unchanged art,
    sounds and other defs live."""
    roots = set()
    for p in changed:
        parts = Path(p).parts
        roots.add("/".join(parts[:3]) if parts[0] == "src" and len(parts) >= 4 else str(Path(p).parent))
    return sorted(r for r in roots if r not in ("", "."))


def unchanged_assets(repo: Path, head: str, changed: list, tree_paths: list) -> list:
    """Every path at head under asset_roots(changed) that the critic's tree left out: names only, never blobs. Without
    them the critic reads an absent texture directory as missing art (GELATINOUSSLIME, CONTAGION on l4-main)."""
    roots = asset_roots(changed)
    if not roots:
        return []
    with J.SafeRepo(Path(repo)) as g:
        out = g.git("ls-tree", "-r", "-z", "--name-only", "--full-tree", head, "--", *roots)
    held = set(tree_paths)
    names = (n.decode("utf-8", "surrogateescape") for n in out.split(b"\0") if n)
    return sorted(n for n in names if n not in held and not n.startswith(("Transient/", "deployed/")))


# Words that would tell the critic a candidate's role if they were in the item text (none in the shipped set).
ROLE_WORDS = re.compile(r"(?i)\b(?:planted|calibrat\w*|escaped|rework(?:ed)?|reopened)\b")


def prepare(c: dict, critic: Critic, repo: Path = A.REPO) -> CriticInput:
    """Neutralised diff always (a leak refuses); a tree only for a critic that runs tests."""
    spec = c["prompt"] + "\n" + c["criteria"]
    # The arena task id and the shas are harness identity; the source item's own name is not (a builder sees it).
    ids = list(c.get("rework_items") or []) + [c.get("task")] + \
        [c[k][:10] for k in ("base", "head") if len(c.get(k) or "") >= 10]
    told = [w for w in ids if w and w in spec] + ROLE_WORDS.findall(spec)
    if told:
        raise J.JudgeError("the item text itself tells the critic the outcome: %s" % told[:3])
    text, binaries = text_area(repo, c)
    area = [glob.escape(p) for p in text]
    if not area:
        raise J.JudgeError("no text file changed in the area: nothing a critic can read")
    n = J.neutralise(repo, c["base"], c["head"], area)
    if not n.text.strip():
        raise J.JudgeError("empty neutralised diff")
    diff = n.text
    if binaries:
        names = [J.scrub(b)[0] for b in binaries]
        diff += ("\n=== BINARY FILES CHANGED (content not shown; a compiled DLL is built from the source above) "
                 "===\n" + "\n".join(names) + "\n")
        leaks = J.find_leaks(diff, clone=Path(repo), shas=(c["base"], c["head"]))
        if leaks:
            raise J.NeutraliserLeak("binary file names identify the arm: " + "; ".join(leaks[:5]))
    work = tree = None
    if critic.needs_tree:
        work = work_base() / secrets.token_hex(8)
        work.mkdir(parents=True, mode=0o700)
        paths = critic_tree_files(repo, c["head"], text)
        tree = J.materialise(repo, c["head"], [], work / "tree", tree_paths=paths)
        rest = [J.scrub(n)[0] for n in unchanged_assets(repo, c["head"], text, paths)]
        if rest:
            leaks = J.find_leaks("\n".join(rest), clone=Path(repo), shas=(c["base"], c["head"]))
            if leaks:
                raise J.NeutraliserLeak("unchanged file names identify the arm: " + "; ".join(leaks[:5]))
            (work / ASSET_LIST).write_text("\n".join(rest) + "\n", "utf-8", "surrogateescape")
            diff = ("=== FILES NOT IN YOUR TREE (they exist at this head) ===\nYour tree leaves out %d unchanged files "
                    "of the changed mods: textures, sounds and other binaries, and text it does not need. An absent "
                    "file is not a missing file: before you call anything missing, grep ../%s relative to your current "
                    "directory (one path per line).\n\n" % (len(rest), ASSET_LIST)) + diff
    return CriticInput(cid=c["cid"], prompt=c["prompt"], criteria=c["criteria"], diff=diff, tree=tree, work=work)


def run_one(c: dict, critic: Critic, repo: Path = A.REPO) -> dict:
    rec = {"cid": c["cid"], "critic": critic.name, "ts": dt.datetime.now(dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")}
    ci = None
    try:
        ci = prepare(c, critic, repo)
        v = critic.review(ci)
        rec.update(verdict=v.verdict if v.verdict in J.VERDICTS else "invalid", reasons=v.reasons, meta=v.meta)
    except Exception as e:                       # noqa: BLE001 -- a failed preparation or call is invalid, never a verdict
        rec.update(verdict="invalid", reasons=["%s: %s" % (type(e).__name__, str(e)[:300])], meta={})
    finally:
        if ci is not None and ci.work is not None:
            shutil.rmtree(ci.work, ignore_errors=True)
    return rec


def read_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def run(set_doc: dict, critic: Critic, run_id: str, concurrency: int = 8, max_n: int | None = None,
        attempts: int = 2, root: Path | None = None, repo: Path = A.REPO, budget_s: float | None = None) -> dict:
    """Resumable: a candidate with a valid verdict in this run is skipped; an invalid one is retried until it has
    `attempts` records. Order is shuffled per run (seeded by the run id), never by role."""
    d = (root or calib_root()) / run_id
    d.mkdir(parents=True, exist_ok=True)
    with open(d / ".lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SystemExit("run %s is being run by another process; refusing to interleave" % run_id)
        return _run_locked(d, set_doc, critic, run_id, concurrency, max_n, attempts, repo, budget_s)


def _run_locked(d, set_doc, critic, run_id, concurrency, max_n, attempts, repo, budget_s) -> dict:
    res_path = d / "results.jsonl"
    meta_path = d / "run.json"
    fp = critic_fingerprint(critic)
    if not meta_path.exists():
        meta_path.write_text(json.dumps({"run": run_id, "critic": critic.name, "critic_fingerprint": fp,
                                         "set_sha256": set_doc["set_sha256"],
                                         "started": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    prev = json.loads(meta_path.read_text())
    if (prev["critic"] != critic.name or prev.get("critic_fingerprint") != fp
            or prev["set_sha256"] != set_doc["set_sha256"]):
        raise SystemExit("run %s was started with critic %s (fingerprint %s) on set %s; refusing to mix"
                         % (run_id, prev["critic"], str(prev.get("critic_fingerprint"))[:12],
                            prev["set_sha256"][:12]))
    done = read_results(res_path)
    tries: dict[str, int] = {}
    ok = set()
    for r in done:
        if not (r.get("meta") or {}).get("budget_cut"):
            tries[r["cid"]] = tries.get(r["cid"], 0) + 1
        if r["verdict"] in J.VERDICTS:
            ok.add(r["cid"])
    todo = [c for c in set_doc["candidates"] if c["cid"] not in ok and tries.get(c["cid"], 0) < attempts]
    random.Random(run_id).shuffle(todo)
    if max_n is not None:
        todo = todo[:max_n]
    if budget_s is not None and hasattr(critic, "deadline"):
        critic.deadline = time.time() + budget_s
    with cf.ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
        futs = [ex.submit(run_one, c, critic, repo) for c in todo]
        for f in cf.as_completed(futs):
            rec = f.result()
            if rec.get("meta", {}).get("skipped"):
                continue                         # not attempted: never counts as a try
            with open(res_path, "a") as fh:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    allres = read_results(res_path)
    left = [c["cid"] for c in set_doc["candidates"] if c["cid"] not in {r["cid"] for r in allres
                                                                          if r["verdict"] in J.VERDICTS}]
    return {"run": run_id, "ran": len(todo), "results": str(res_path), "without_valid_verdict": len(left)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-set")
    b.add_argument("--pool", help="cached census pool JSON ([[task, hidden], ...]); default: run the census")
    b.add_argument("--write", action="store_true", help="write fixtures/critic_calib_set.json")
    r = sub.add_parser("run")
    r.add_argument("--critic", required=True)
    r.add_argument("--run", required=True)
    r.add_argument("--concurrency", type=int, default=8)
    r.add_argument("--max", type=int)
    r.add_argument("--budget", type=float, default=480.0, help="wall seconds for this invocation (calls are cut)")
    s = sub.add_parser("score")
    s.add_argument("--run", required=True)
    s.add_argument("--json", action="store_true")
    s.add_argument("--adjudication", help="also score with a reject-side adjudication JSON (e.g. %s)" % ADJ_PATH)
    a = ap.parse_args(argv)
    if a.cmd == "build-set":
        if a.pool:
            pool = [(t, h) for t, h in json.loads(Path(a.pool).read_text())]
        else:
            pool, _ = A.census(window=CENSUS_WINDOW)
        doc = build_set(pool, repo=A.REPO)
        print(json.dumps({"counts": doc["counts"], "set_sha256": doc["set_sha256"]}))
        if a.write:
            SET_PATH.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
            print("wrote", SET_PATH)
        return 0
    doc = load_set()
    if a.cmd == "run":
        print(json.dumps(run(doc, load_critic(a.critic), a.run, a.concurrency, a.max, budget_s=a.budget)))
        return 0
    meta = json.loads((calib_root() / a.run / "run.json").read_text())
    if meta.get("set_sha256") != doc["set_sha256"]:
        raise SystemExit("run %s was made on set %s, not the shipped set %s: its verdicts cannot be scored here"
                         % (a.run, str(meta.get("set_sha256"))[:12], doc["set_sha256"][:12]))
    res = read_results(calib_root() / a.run / "results.jsonl")
    sc = score(doc, res)
    sc["critic"], sc["critic_fingerprint"] = meta.get("critic"), meta.get("critic_fingerprint")
    sc["provenance"] = ("fingerprinted" if meta.get("critic_fingerprint") else
                        "UNVERIFIED: legacy run.json without a critic fingerprint; re-run under fingerprinting to "
                        "make this verdict decision-grade")
    sc["run"] = a.run
    sc["set_sha256"] = doc["set_sha256"]
    if a.adjudication:
        adj = json.loads(Path(a.adjudication).read_text())
        if adj.get("run") != a.run:
            raise SystemExit("adjudication %s is for run %s, not %s" % (a.adjudication, adj.get("run"), a.run))
        sc["adjudicated"] = score_adjudicated(doc, res, adj)
    (calib_root() / a.run / "score.json").write_text(json.dumps(sc, indent=1) + "\n")
    if a.json:
        print(json.dumps(sc, indent=1))
        return 0
    for label, block in (("RAW (the decision)", sc), ("ADJUDICATED (reject side only, sensitivity, not a verdict)",
                                       sc.get("adjudicated"))):
        if block is None:
            continue
        print("==", label)
        for k in ("false_reject", "reject_rate_tierB_unlabelled", "reject_rate_all_good_nominal", "miss",
                  "miss_strong_only"):
            v = block[k]
            print("%-32s %s/%s = %s  95%% [%s, %s]  P(>=%.2f)=%s" % (k, v["k"], v["n"], None if v["rate"] is None
                  else round(v["rate"], 3), v["wilson95"][0], v["wilson95"][1], v["threshold"],
                  v["p_at_or_above_threshold"]))
        print("invalid %d of %d; reliability %s (%s)" % (block["invalid"], block["candidates"],
                                                          block["reliability"]["verdict"],
                                                          block["reliability"]["why"]))
    print("provenance:", sc["provenance"])
    print("score:", calib_root() / a.run / "score.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
