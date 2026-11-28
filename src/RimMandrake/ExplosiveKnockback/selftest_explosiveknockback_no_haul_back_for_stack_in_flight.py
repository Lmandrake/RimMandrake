#!/usr/bin/env python3
"""Static check for Explosive Knockback 0.2.0, promise "a thrown colonist is not sent back to a stack that is still in
flight", leaf pawn_flight_arc ("goes back to work when the stun ends") with bar carried_thing_own_arc.

The owner's card of 2026-11-27 9:51 PM PST (item RIMMANDRAKE_REVERT_KNOCKBACK_HAUL_WALKBACK_HE_LIKES_THE_SCATTER),
"Leave it for hauling": a blast scatters work. The thrown colonist takes its next job by priority, and the stack waits
for any hauler, as in the passed 0.2.0. Commit 11fffbf13b had made the colonist wait for its stack to land and then
gave the haul back (AwaitingStack, StackLanded); this file keeps that code out.

Scope: 0.2.0's ResumeHaul stays. It still gives the haul back when the stack is already on the map at the landing (a
stack too heavy to fly, dropped on the start cell) or still in the hands. That is the passed behaviour, not the walk-back.

This file reads the game side, in RM_PawnFlyerPatches.cs, RM_ThingFlyer_Knockback.cs and RM_KnockbackProof.cs:

  N1  ResumeHaul keeps no haul waiting for a stack in its knockback flyer (no flyer test, no AwaitingStack, no
      resume_wait line)
  N2  no thrown stack gives a haul back when it comes down: RM_ThingFlyer_Knockback calls no StackLanded, and
      RM_PawnFlyerPatches defines none
  N3  the sc_pawn_arc verdict does not depend on the haul: its Result condition names neither `resumed` (the mod's
      resume line) nor `rehaul` (the colonist took the same stack again), so a colonist that walks away gets the same
      verdict
  N4  the sc_pawn_arc verdict still decides "goes back to work when the stun ends": its Result condition names `working`,
      a current job read after the stun ends

Each line is also run against a planted fault (the walk-back part put back); each must turn its line red, or this file
fails.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_no_haul_back_for_stack_in_flight.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(HERE, "Source", "RM_PawnFlyerPatches.cs")
FLY = os.path.join(HERE, "Source", "RM_ThingFlyer_Knockback.cs")
PROOF = os.path.join(HERE, "Source", "RM_KnockbackProof.cs")


def body(src, signature):
    """The text of the method or block whose declaration contains `signature`, braces balanced; "" when absent."""
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
    return ""


def code(text):
    """`text` with // comments removed, so a comment cannot satisfy or break a line."""
    return re.sub(r"//[^\n]*", "", text or "")


def verdict_condition(proof):
    """The first argument of the Result(sc, ...) call in the sc_pawn_arc verdict; "" when absent."""
    i = proof.find('case "pawn_arc":')
    if i < 0:
        return ""
    arc = code(proof[i:proof.find('case "pit_goods_fetch":', i)])
    v = arc.find("s.verdict")
    m = re.search(r"Result\(sc,\s*([^,]*),", arc[v:]) if v >= 0 else None
    return m.group(1) if m else ""


def checks(pf, fly, proof):
    """-> [(id, ok, what it read)]"""
    out = []
    rh = code(body(pf, "private static void ResumeHaul("))
    flyer = re.search(r"ParentHolder\s+is\s+RM_ThingFlyer_Knockback", rh) is not None
    waits = "AwaitingStack" in rh or '"resume_wait"' in rh
    out.append(("N1", rh != "" and not flyer and not waits,
                "ResumeHaul found %s, flyer test %s, a wait %s" % (rh != "", flyer, waits)))
    calls = "StackLanded(" in code(fly)
    defines = re.search(r"\bvoid\s+StackLanded\s*\(", code(pf)) is not None
    out.append(("N2", not calls and not defines, "flyer calls StackLanded %s, patches define StackLanded %s" % (calls, defines)))
    cond = verdict_condition(proof)
    names = sorted(w for w in ("resumed", "rehaul") if re.search(r"\b%s\b" % w, cond))
    out.append(("N3", cond != "" and not names, "verdict condition %r names %s" % (cond.strip()[:120], names or "no haul")))
    out.append(("N4", re.search(r"\bworking\b", cond) is not None, "verdict condition names working: %s"
                % (re.search(r"\bworking\b", cond) is not None)))
    return out


PLANTS = [
    ("N1", PF, lambda s: s.replace("            if (haul == null)\n",
                                   "            if (haul == null && stack != null && stack.ParentHolder is RM_ThingFlyer_Knockback) { return; }\n"
                                   "            if (haul == null)\n", 1)),
    ("N2", FLY, lambda s: s.replace("            Destroy();\n        }", "            RM_Patch_PawnFlyer_KnockbackLanding.StackLanded(inner, landed);\n"
                                    "            Destroy();\n        }", 1)),
    ("N3", PROOF, lambda s: s.replace("stun && working &&", "stun && working && rehaul &&", 1)),
    ("N4", PROOF, lambda s: s.replace("stun && working &&", "stun &&", 1)),
]


def main():
    src = {k: open(k, encoding="utf-8").read() for k in (PF, FLY, PROOF)}
    rows = checks(src[PF], src[FLY], src[PROOF])
    bad = 0
    for cid, ok, what in rows:
        print("%s  %s  %s" % ("PASS" if ok else "FAIL", cid, what))
        bad += 0 if ok else 1
    for cid, path, plant in PLANTS:
        planted = dict(src)
        planted[path] = plant(src[path])
        if planted[path] == src[path]:
            print("PLANT %s  NOT APPLIED (the text it changes is absent)" % cid)
            bad += 1
            continue
        red = [r for r in checks(planted[PF], planted[FLY], planted[PROOF]) if r[0] == cid and not r[1]]
        print("PLANT %s  %s" % (cid, "caught" if red else "NOT CAUGHT"))
        bad += 0 if red else 1
    print("VERDICT %s (%d lines and %d plants)" % ("PASS" if bad == 0 else "FAIL", len(rows), len(PLANTS)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
