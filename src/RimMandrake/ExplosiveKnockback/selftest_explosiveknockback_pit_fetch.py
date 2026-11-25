#!/usr/bin/env python3
"""Offline geometry guard for Explosive Knockback's sc_pit_fetch (RM_KnockbackProof.cs case "pit_goods_fetch").

RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT, live 2026-11-16 (minimal list, job log of the hauler): the hauler went
down the portable ladder and picked the stack up, then vanilla's Toils_Haul.CheckForGetOpportunityDuplicate (a same-def
stack within 8 cells, found by GenClosest.ClosestThingReachable, a region search FlowWorks' reach veto never sees) retargeted
the job at the CONTROL pit's stack 6 cells away. Its ladder is raised, the path errored (ErroredPather), the carried stack
was dropped on the ladder cell, and the same job repeated all day. Destroying the control stack, the stack and corpse were
fetched. And the corpse lay on the pit's edge row, where a hauler on the rim touches it without the ladder
(RIMMANDRAKE_MOVE_PIT_FETCH_CORPSE_OFF_RIM_TOUCHED_ABOVE). This test reads the scene's layout from the C# and checks:

  G1 the control stack is more than 8 cells from every cell the main lane's hauler stands on while carrying (main pit,
     ladder rim, stockpiles), so the lanes cannot interact through the duplicate pickup
  G2 neither the stack nor the corpse is on a cell 8-adjacent to undug ground: each is fetched only from inside the pit
  G3 the main ladder hangs from inside the main pit to undug ground; the control ladder likewise for the control pit
  G4 every cell the scene uses lies inside the scene's own prepared 15x15 (Prepare(s.o, 7)): scenes are 15 cells apart
  G5 the corpse is un-forbidden after the kill (live 2026-11-16: vanilla forbids a corpse dying outside the home area)
  G6 every haulable on the map that is not the scene's is forbidden for the scene and allowed again by its restore (visit 3,
     2026-11-16, SITE: after 53 scenes the hauler carried their corpses and steel into this scene's stockpiles, the stack
     merged into another and the corpse was moved off its cell; 2 FAIL of 2 on that map, 2 PASS of 2 on a fresh one)
  G7 the hauls are ORDERED (2026-11-25), and an ordered haul skips the free-will reach test, so before the orders the scene
     reads HaulAIUtility.PawnCanAutomaticallyHaulFast for the stack, the corpse and the control stack, and the verdict
     requires the first two true and the control false (fresh reader, 2026-11-25: a reach veto that wrongly shut the
     lowered-ladder pit would else pass, the ordered job walking the ladder anyway)

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_pit_fetch.py
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "RM_KnockbackProof.cs")
DUPE_RADIUS = 8.0       # Toils_Haul.CheckForGetOpportunityDuplicate: GenClosest.ClosestThingReachable(..., 8f, ...)
O = r"O\(s,\s*(-?\d+),\s*(-?\d+)\)"


def block(text):
    i = text.index('case "pit_goods_fetch":')
    return text[i:text.index("s.verdict = sc =>", i)]


def layout(b):
    """-> dict of the scene's cells, or raises ValueError naming what it could not read."""
    def one(pat, what):
        m = re.search(pat, b)
        if not m:
            raise ValueError("cannot read %s" % what)
        return tuple(int(v) for v in m.groups())
    pits = [tuple(int(v) for v in m) for m in re.findall(r"Pit\(" + O + r",\s*(\d+),\s*(\d+)\)", b)]
    if len(pits) != 2:
        raise ValueError("want 2 Pit(O(s,x,z),w,h) calls, read %d" % len(pits))
    cells = lambda p: {(p[0] + dx, p[1] + dz) for dx in range(p[2]) for dz in range(p[3])}  # noqa: E731
    lay = {
        "main": cells(pits[0]), "control": cells(pits[1]),
        "st": one(r'Item\(s, "st", "Steel", \d+, ' + O + r"\)", "the stack"),
        "cst": one(r'Item\(s, "cst", "Steel", \d+, ' + O + r"\)", "the control stack"),
        "dead": one(r'Colonist\(s, "dead", ' + O, "the corpse"),
        "lad": one(r"Thing lad = Ladder\(ld, " + O + r", " + O + r"\)", "the main ladder"),
        "ctl": one(r"Thing ctl = Ladder\(fixedLd, " + O + r", " + O + r"\)", "the control ladder"),
        "zones": [tuple(int(v) for v in m) for m in re.findall(r"z[ab]\.AddCell\(" + O + r"\)", b)],
        "hauler": one(r'Colonist\(s, "h", ' + O, "the hauler"),
        "corpse_allowed": bool(re.search(r"dead\.Kill\(null\);.{0,400}?dead\.Corpse\?\.SetForbidden\(false", b, re.S)),
        "free_will_reach": all(re.search(r'PawnCanAutomaticallyHaulFast\(h, s\.things\["%s"\], false\)' % k, b)
                               for k in ("st", "corpse", "cst"))
                           and 0 <= b.find("PawnCanAutomaticallyHaulFast") < b.find("TryTakeOrderedJob"),
        "foreign_forbidden": bool(re.search(r"ThingRequestGroup\.HaulableEver.{0,600}?SetForbidden\(true.{0,600}?s\.restore.{0,300}?"
                                            r"SetForbidden\(false", b, re.S)) and b.find("HaulableEver") < b.find("ProofSchedule"),
    }
    if len(lay["zones"]) != 2:
        raise ValueError("want 2 stockpile cells, read %d" % len(lay["zones"]))
    return lay


def check(lay):
    faults = []
    main, ctl = lay["main"], lay["control"]
    rim, edge = lay["lad"][:2], lay["lad"][2:]
    carry = set(main) | {rim} | set(lay["zones"])
    near = min(math.hypot(c[0] - lay["cst"][0], c[1] - lay["cst"][1]) for c in carry)
    if near <= DUPE_RADIUS:
        faults.append("G1 the control stack is %.1f cells from the main lane's carry cells (duplicate pickup reaches %g)"
                      % (near, DUPE_RADIUS))
    for k in ("st", "dead"):
        c = lay[k]
        if c not in main:
            faults.append("G2 %s at %s is not on the main pit floor" % (k, c))
        elif any((c[0] + a, c[1] + b) not in main for a in (-1, 0, 1) for b in (-1, 0, 1)):
            faults.append("G2 %s at %s is touchable from undug ground" % (k, c))
    if lay["cst"] not in ctl:
        faults.append("G2 the control stack is not on the control pit floor")
    for name, (r0, e0), pit in (("main", (rim, edge), main), ("control", (lay["ctl"][:2], lay["ctl"][2:]), ctl)):
        if e0 not in pit or r0 in pit or abs(r0[0] - e0[0]) + abs(r0[1] - e0[1]) != 1:
            faults.append("G3 the %s ladder (rim %s, edge %s) does not hang from its pit to undug ground" % (name, r0, e0))
    used = set(main) | set(ctl) | {rim, lay["ctl"][:2], lay["hauler"]} | set(lay["zones"])
    out = sorted(c for c in used if max(abs(c[0]), abs(c[1])) > 7)
    if out:
        faults.append("G4 cells outside the scene's prepared 15x15: %s" % out[:6])
    if main & ctl:
        faults.append("G4 the two pits overlap")
    if not lay.get("corpse_allowed"):
        faults.append("G5 the corpse is left forbidden (vanilla forbids a corpse dying outside the home area): nobody hauls it")
    if not lay.get("foreign_forbidden"):
        faults.append("G6 the map's other haulables stay allowed: earlier scenes' corpses and steel crowd this scene's stockpiles")
    if not lay.get("free_will_reach"):
        faults.append("G7 the ordered hauls are not preceded by a free-will reach read of stack, corpse and control: a reach "
                      "veto that shuts the lowered-ladder pit would pass")
    if lay.get("verdict_reach") is False:
        faults.append("G7 the verdict does not require the free-will reach (autoHaulMain true, autoHaulControl false)")
    return faults


def main():
    text = open(SRC, encoding="utf-8").read()
    try:
        lay = layout(block(text))
        i = text.index('case "pit_goods_fetch":')
        v = text[text.index("s.verdict = sc =>", i):text.index("return null;", text.index("s.verdict = sc =>", i))]
        lay["verdict_reach"] = "autoHaulMain" in v and "autoHaulControl" in v
        faults = check(lay)
    except ValueError as e:
        faults = ["layout unreadable: %s" % e]
    for f in faults:
        print("FAIL", f)
    # planted faults: the visit-2 layout must go red on G1 and G2
    old = {"main": {(x, z) for x in (2, 3, 4) for z in (-1, 0, 1)}, "control": {(x, z) for x in (-5, -4, -3) for z in (-1, 0, 1)},
           "st": (3, 0), "cst": (-4, 0), "dead": (3, 1), "lad": (1, 0, 2, 0), "ctl": (-6, 0, -5, 0),
           "zones": [(0, 5), (2, 5)], "hauler": (0, 3), "corpse_allowed": True, "foreign_forbidden": True, "free_will_reach": True}
    got = check(old)
    planted = all(any(f.startswith(g) for f in got) for g in ("G1", "G2"))
    if not planted:
        print("FAIL planted visit-2 layout not caught on G1 and G2: %s" % got)
    ok = not faults and planted
    print("explosive knockback pit fetch geometry: %s (%d faults; visit-2 layout caught: %s)"
          % ("PASS" if ok else "FAIL", len(faults), planted))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
