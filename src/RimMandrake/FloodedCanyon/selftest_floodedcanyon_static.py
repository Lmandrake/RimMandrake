#!/usr/bin/env python3
"""Offline selftest for FloodedCanyon's validation.static_checks (no game, no bridge).

static_checks() was reachable only from validation.py's __main__, so no suite run asserted it. This runs it
green on the shipped tree, then proves the tarruq-call component (CRACKEDLANDS_FIVE_BEATS_AUDIO_1) can go red:
call removed, call naming a SoundDef Core does not ship.
Run: python3 src/RimMandrake/FloodedCanyon/selftest_floodedcanyon_static.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


bad = V.static_checks()
check("shipped tree: static_checks green", not bad, "; ".join(bad))
xml = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_IrqitTarruq.xml"), encoding="utf-8").read()
check("shipped tarruq call green", V._tarruq_call_findings(xml) == [])
check("sanity: shipped XML carries the call", "<soundCall>Pawn_Muffalo_Call</soundCall>" in xml)
gone = xml.replace("<soundCall>Pawn_Muffalo_Call</soundCall>", "")
check("break: call removed -> red", any("no soundCall" in f for f in V._tarruq_call_findings(gone)))
if os.path.isdir(V.VANILLA_SOUNDDEF_DIR):
    typo = xml.replace("<soundCall>Pawn_Muffalo_Call</soundCall>", "<soundCall>Pawn_Tarruq_Call</soundCall>")
    check("break: non-Core SoundDef -> red", any("not a Core SoundDef" in f for f in V._tarruq_call_findings(typo)))
else:
    print("UNMEASURED  non-Core SoundDef break (no RimWorld install visible)")


# FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 A2: the flood driver writes FlowWorks fill only through the outcome contract,
# never the bool TrySetDriverFill (whose false conflates NotOwned with Refused).
import re  # noqa: E402

OLD_BOOL = re.compile(r"\bTrySetDriverFill\s*\(")


def bool_driver_calls(text):
    return [ln.strip() for ln in text.splitlines() if OLD_BOOL.search(ln) and not ln.strip().startswith("//")]


src_dir = os.path.join(HERE, "Source")
calls, outcome_calls = [], 0
for dp, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".cs") and "/obj/" not in dp.replace("\\", "/") + "/":
            t = open(os.path.join(dp, f), encoding="utf-8").read()
            calls += ["%s: %s" % (f, c) for c in bool_driver_calls(t)]
            outcome_calls += len(re.findall(r"\bTrySetDriverFillOutcome\s*\(", t))
check("contract: no bool TrySetDriverFill call in FloodedCanyon source", calls == [], "; ".join(calls))
check("sanity: the recede restores through TrySetDriverFillOutcome", outcome_calls >= 1, outcome_calls)
check("break: the old bool call -> red",
      bool_driver_calls("(k, prior) => excavation?.TrySetDriverFill(Cell(k), prior));") != [])
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
