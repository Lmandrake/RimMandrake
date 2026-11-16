#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_BACKFILL_SLACK_LEDGER_SHADOW_BESIDE_FLOWWORKS and
RIMMANDRAKE_BACKFILL_FLOWWORKS_LEDGER_SHADOW_BESIDE_SLACK, one mod each, run in parallel (plan
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 3). Written by the filing seat; the builder does not edit
it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/modledger_backfill_accept.py GimmeSomeSlack      # PASS 7/7 when built
    python3 src/RimMandrake/rimflow/acceptance/modledger_backfill_accept.py FlowWorks

THE CONTRACT, per mod named: its mod ledger exists (design/concepts/<Mod>/ledger/) with events; every BACKFILL event
cites a file that exists (evidence[0], a path optionally followed by #locator or :line); a version.open event names its
Design Version; the reduced stage equals version/stage_record.json's `stage` when that file exists; the reduced bar
count equals version/VERSION.json's bars_total when that exists; `modledger.py lint --mod <Mod>` is clean against
origin/main (views current, nothing hand-edited); the packet is within packet_budget_tokens and ends with "## Left out".
Shadow mode: nothing here checks or allows a redirect; that is the cutover item's.
Exit 0 with "PASS n/n" only when every check of every mod passes. ExplosiveKnockback, backfilled by the filing item,
passes it (the sanity probe that the instrument can see).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import modledger as M                                            # noqa: E402

ROOT = M.REPO_ROOT
res = []


def check(name, ok, detail=""):
    res.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))


def _load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


for mod in sys.argv[1:] or ["GimmeSomeSlack", "FlowWorks"]:
    evs = M.read(ROOT, mod)
    check("%s: the mod ledger holds events" % mod, len(evs) > 0, len(evs))
    bf = [e for e in evs if e.get("writer") == "BACKFILL"]
    # evidence refs are typed since the entry standard (path:<repo path>); the old untyped form still reads
    ref0 = lambda e: re.sub(r"^path:", "", e["evidence"][0])  # noqa: E731
    bad = [e.get("subject") for e in bf if not e.get("evidence") or not os.path.exists(
        os.path.join(ROOT, re.split(r"[#]", ref0(e))[0].rsplit(":", 1)[0]
                     if re.search(r":\d+$", ref0(e).split("#")[0]) else ref0(e).split("#")[0]))]
    check("%s: every BACKFILL event cites an existing old file" % mod, bool(bf) and not bad, bad[:5])
    st = M.reduce(evs)
    check("%s: a version.open names the Design Version" % mod,
          any(e.get("kind") == "version.open" for e in evs) and bool(st["version"]), st["version"])
    sr = _load(os.path.join(ROOT, "design", "concepts", mod, "version", "stage_record.json"))
    if sr is not None:
        check("%s: the ledger's stage equals the stage record's" % mod, st["stage"] == sr.get("stage"),
              (st["stage"], sr.get("stage")))
    vj = _load(os.path.join(ROOT, "design", "concepts", mod, "version", "VERSION.json"))
    if vj is not None and vj.get("bars_total") is not None:
        check("%s: the ledger's bars equal VERSION.json bars_total" % mod, len(st["bars"]) == vj["bars_total"],
              (len(st["bars"]), vj["bars_total"]))
    findings, notes = M.lint(ROOT, mod, base="origin/main")
    check("%s: modledger lint is clean against origin/main" % mod, evs != [] and findings == [], findings[:5])
    txt, info = M.packet(ROOT, mod)
    check("%s: the packet is within budget and says what it left out" % mod,
          evs != [] and not info["over_budget"] and "## Left out" in txt, (info["tokens"], info["budget"]))
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
