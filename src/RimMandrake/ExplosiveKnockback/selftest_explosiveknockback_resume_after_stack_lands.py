#!/usr/bin/env python3
"""Static check T_RESUME_AFTER_STACK_LANDS for Explosive Knockback 0.2.0, leaf pawn_flight_arc ("goes back to work when
the stun ends") with bar carried_thing_own_arc (the carried stack flies on its own path).

The fault (RIMMANDRAKE_SORT_KNOCKBACK_LANE_FAILS_ARCHBIG_PASSES_SAME_CHECKS, 2026-11-27): a colonist thrown mid-haul
lands about 7 ticks before the stack it carried, because the stack flies further on its own flyer. At the pawn's landing
ResumeHaul found the stack neither held nor spawned and wrote `resume_skip reason=stack_gone`, so the haul came back only
by free will. In 4 of 4 SteveDesktop lane runs and in ArchBig's visit 2 run, the journal read stack_gone; the scene
passed only where free will re-took the stack (origin 57,12 and 42,12) and failed 3 of 3 at origin 27,12.

This file reads the game side, in RM_PawnFlyerPatches.cs, RM_ThingFlyer_Knockback.cs and RM_KnockbackProof.cs:

  R1  ResumeHaul waits for a stack that is still in its knockback flyer: it remembers the pawn and the job against the
      stack (AwaitingStack) and journals resume_wait, before it would journal resume_skip
  R2  RM_ThingFlyer_Knockback.Land tells the hook when the stack comes down (StackLanded(inner, landed)), after
      PlaceLanding
  R3  a stack destroyed in flight also tells the hook (StackLanded(inner, null)), so no wait is left behind
  R4  StackLanded takes the wait out, puts the remembered job back (Hauling[...]) and calls ResumeHaul when the landed
      thing is the stack itself
  R5  the sc_pawn_arc verdict requires the mod's own `resume` journal line for the colonist (started true), so a
      free-will haul can no longer pass the row

Each line is also run against a planted fault (each part removed); each must turn its line red, or this file fails.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_resume_after_stack_lands.py
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


def checks(pf, fly, proof):
    """-> [(id, ok, what it read)]"""
    out = []
    rh = code(body(pf, "private static void ResumeHaul("))
    wait, skip = rh.find("AwaitingStack["), rh.find('"resume_skip"')
    flyer = re.search(r"ParentHolder\s+is\s+RM_ThingFlyer_Knockback", rh) is not None
    out.append(("R1", rh != "" and flyer and wait >= 0 and '"resume_wait"' in rh and (skip < 0 or wait < skip),
                "ResumeHaul: flyer test %s, AwaitingStack write at %d, resume_skip at %d" % (flyer, wait, skip)))
    land = code(body(fly, "private void Land(Thing inner, Map map)"))
    place, hook = land.find("PlaceLanding("), land.find("StackLanded(inner, landed)")
    out.append(("R2", land != "" and 0 <= place < hook, "Land: PlaceLanding at %d, StackLanded(inner, landed) at %d" % (place, hook)))
    leg = code(body(fly, "private void LegEnd(Thing inner)"))
    out.append(("R3", "StackLanded(inner, null)" in leg, "LegEnd's destroyed-in-flight path calls StackLanded(inner, null): %s"
                % ("StackLanded(inner, null)" in leg)))
    sl = code(body(pf, "internal static void StackLanded("))
    ok4 = sl != "" and "AwaitingStack.Remove(" in sl and re.search(r"Hauling\[[^\]]+\]\s*=", sl) is not None \
        and "ResumeHaul(" in sl and re.search(r"landed\s*==\s*inner", sl) is not None
    out.append(("R4", ok4, "StackLanded: %s" % ("removes the wait, restores the job, resumes on landed == inner" if ok4 else
                                                 "absent or incomplete (%d chars)" % len(sl))))
    i = proof.find('case "pawn_arc":')
    arc = code(proof[i:proof.find('case "pit_goods_fetch":', i)]) if i >= 0 else ""
    ver = arc[arc.find("s.verdict"):] if "s.verdict" in arc else ""
    ok5 = re.search(r'ForThing\(sc,\s*"resume",\s*p\)', ver) is not None and "started" in ver \
        and re.search(r"Result\(sc,[^;]*\bresumed\b", ver) is not None
    out.append(("R5", ok5, "sc_pawn_arc verdict requires the mod's resume line: %s" % ok5))
    return out


PLANTS = [
    ("R1", PF, lambda s: s.replace('"resume_wait"', '"resume_skip_wait"')),
    ("R1", PF, lambda s: re.sub(r"ParentHolder\s+is\s+RM_ThingFlyer_Knockback", "ParentHolder is Pawn", s)),
    ("R2", FLY, lambda s: s.replace("StackLanded(inner, landed)", "StackLandedNot(inner, landed)")),
    ("R3", FLY, lambda s: s.replace("StackLanded(inner, null)", "StackLandedNot(inner, null)")),
    ("R4", PF, lambda s: s.replace("AwaitingStack.Remove(", "AwaitingStack.ContainsKey(")),
    ("R5", PROOF, lambda s: s.replace('ForThing(sc, "resume", p)', 'ForThing(sc, "resume_wait", p)')),
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
    print("VERDICT %s (%d of %d lines and %d plants)" % ("PASS" if bad == 0 else "FAIL", len(rows), len(rows), len(PLANTS)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
