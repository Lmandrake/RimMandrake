#!/usr/bin/env python3
"""Static check T_CARRY_STATIC for Explosive Knockback 0.2.0, bar carried_thing_own_arc.

The bar: "When a blast throws a colonist who carries something, the carried thing leaves their hands at the blast and
flies on its own path, apart from the colonist ... A carried thing too heavy to fly drops where the colonist stood."
The kernel decides the carried thing's plan (KbPlanner.Carried, kernel case K_CARRY_OWN_PLAN). This file reads the game
side that the kernel cannot run, in RM_MapComponent_Knockback.cs and RM_ThingFlyer_Knockback.cs:

  C1  the pawn throw never flies with what it carries: every PawnFlyer.MakeFlyer call in the map component passes
      flyWithCarriedThing: false (0.1.0 passed true)
  C2  ThrowPawn empties the hands before the flyer: ThrowCarried is called after DropCarriedHose (bar hose_drops_at_takeoff
      keeps its order) and before MakeFlyer
  C3  ThrowCarried asks the kernel (KbPlanner.Carried, KbPlanner.CarriedRest), flies a ThrowGoods plan with
      LaunchFromHands, and otherwise drops the thing on the start cell (TryDropCarriedThing(start, ...))
  C4  LaunchFromHands moves the thing from the carrier's hands straight into the flyer (TryTransferToContainer from
      carryTracker.innerContainer, canMergeWithExistingStacks: false), never spawning or despawning it in between, so
      nothing is lost or doubled

Each line is also run against planted faults (the 0.1.0 call, the hose order swapped, the drop removed, a spawn in the
hand-off): each must turn its line red, or this file fails.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_carry_static.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(HERE, "Source", "RM_MapComponent_Knockback.cs")
FLY = os.path.join(HERE, "Source", "RM_ThingFlyer_Knockback.cs")


def body(src, signature):
    """The text of the method whose declaration contains `signature`, braces balanced; None when it is absent."""
    i = src.find(signature)
    if i < 0:
        return None
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
    return None


def code(text):
    """`text` with // comments removed, so a comment cannot satisfy or break a line."""
    return re.sub(r"//[^\n]*", "", text or "")


def checks(mc, fly):
    """-> [(id, ok, what it read)]"""
    out = []
    calls = re.findall(r"PawnFlyer\.MakeFlyer\(([^;]*)\);", code(mc))
    bad = [c for c in calls if not re.search(r"flyWithCarriedThing:\s*false", c)]
    out.append(("C1", bool(calls) and not bad, "%d MakeFlyer call(s), %d not passing flyWithCarriedThing: false" % (len(calls), len(bad))))
    tp = code(body(mc, "private bool ThrowPawn("))
    hose, carry, make = tp.find("DropCarriedHose("), tp.find("ThrowCarried("), tp.find("PawnFlyer.MakeFlyer(")
    out.append(("C2", tp != "" and 0 <= hose < carry < make,
                "in ThrowPawn: DropCarriedHose at %d, ThrowCarried at %d, MakeFlyer at %d (want hose < carried < flyer)" % (hose, carry, make)))
    tc = code(body(mc, "private string ThrowCarried("))
    need = ["KbPlanner.Carried(", "KbPlanner.CarriedRest(", "KbAct.ThrowGoods", "RM_ThingFlyer_Knockback.LaunchFromHands(",
            "TryDropCarriedThing(start"]
    miss = [n for n in need if n not in tc]
    out.append(("C3", tc != "" and not miss, "ThrowCarried %s; missing %s" % ("found" if tc else "ABSENT", miss or "nothing")))
    lf = code(body(fly, "public static RM_ThingFlyer_Knockback LaunchFromHands("))
    moves = re.search(r"carryTracker\?*\.innerContainer", lf) and re.search(r"TryTransferToContainer\(t, f\.innerContainer, [^)]*canMergeWithExistingStacks:\s*false\)", lf)
    spawns = [w for w in ("GenSpawn.Spawn(t", "t.DeSpawn(", "GenPlace.TryPlaceThing(t") if w in lf]
    out.append(("C4", lf != "" and bool(moves) and not spawns,
                "LaunchFromHands %s; hand-to-flyer transfer %s; spawn/despawn of the thing: %s"
                % ("found" if lf else "ABSENT", "found" if moves else "MISSING", spawns or "none")))
    return out


# planted faults: (name, file, old, new, the line it must turn red)
PLANTS = [
    ("the 0.1.0 call", "mc", "flyWithCarriedThing: false", "flyWithCarriedThing: true", "C1"),
    ("hose drop after the carried thing", "mc", "bool hose = RM_KnockbackCompat.DropCarriedHose(p);\n            string carried = ThrowCarried(r, p, f, start, ks);",
     "string carried = ThrowCarried(r, p, f, start, ks);\n            bool hose = RM_KnockbackCompat.DropCarriedHose(p);", "C2"),
    ("no drop when it does not fly", "mc", "dropped = p.carryTracker.TryDropCarriedThing(start, ThingPlaceMode.Near, out Thing _);", "dropped = false;", "C3"),
    ("a spawn in the hand-off", "fly", "f.Begin(start, map, res, dx, dz, kind, mass, explosionId, impactFactor, instigator, bounces, landingCap);\n            return f;\n        }\n\n        private void Begin",
     "GenSpawn.Spawn(t, start, map);\n            f.Begin(start, map, res, dx, dz, kind, mass, explosionId, impactFactor, instigator, bounces, landingCap);\n            return f;\n        }\n\n        private void Begin", "C4"),
]


def main():
    mc, fly = open(MC).read(), open(FLY).read()
    rows = checks(mc, fly)
    fails = 0
    for cid, ok, what in rows:
        fails += not ok
        print("%s %s: %s" % ("PASS" if ok else "FAIL", cid, what))
    caught = 0
    for name, which, old, new, want in PLANTS:
        src = {"mc": mc, "fly": fly}
        if src[which].count(old) != 1:
            print("FAIL plant %r: its text is not in the file once (the plant no longer fits the code)" % name)
            fails += 1
            continue
        src[which] = src[which].replace(old, new)
        red = {cid for cid, ok, _ in checks(src["mc"], src["fly"]) if not ok}
        if want in red:
            caught += 1
        else:
            fails += 1
            print("FAIL plant %r: %s stayed green" % (name, want))
    print("%s carry static: %d of %d lines failing, %d of %d planted faults caught (cases read: %d lines, %d plants; limit 0 failing)"
          % ("PASS" if fails == 0 else "FAIL", sum(1 for _c, ok, _w in rows if not ok), len(rows), caught, len(PLANTS), len(rows), len(PLANTS)))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
