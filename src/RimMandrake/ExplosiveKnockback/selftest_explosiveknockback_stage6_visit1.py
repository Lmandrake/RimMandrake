#!/usr/bin/env python3
"""Offline guards for the proof-scene faults Stage 6 visit 1 found live (2026-11-15,
design/concepts/ExplosiveKnockback/version/in_game/visit_1/SUMMARY.md). Each is a HARNESS fault: the mod behaved, the
scene read it wrong. Read from the C# source, since the scenes only run in a game:
  S1 spared_states reads each spared thing's cell a few ticks after the blast, not at the 300-tick verdict (a skipped
     animal wandered and a woken sleeper got up: "MOVED" with the right skip line and no launch)
  S2 spared_states starts the carry inside the blast's own scheduled action and is INVALID when the carrier is not carrying
     at the blast (an undrafted carrier with no job had dropped its pawn in the 60 ticks before it)
  A1 pawn_arc's walker starts one cell from the planned landing (three cells away it cannot arrive inside a ~25-tick flight)
  W1 the sweep's flyingGoods lane owns C (corpses): flyingGoods off skips corpses with flying_off
     (RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED), so C changing there is its own outcome, not drift
  W2 the sweep's gas-goods stack lies inside the seeded cloud (radius 1 at O(-5,-5)), so a burst always reaches it; two
     cells out it was reached on 13 of 18 lanes and the default lane's "still" read as drift on the rest

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage6_visit1.py [--src DIR]
--src reads the mod's Source/ from DIR (laid out like this folder): the way it was watched red on 545e930429.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(code, ok, what):
    print("%s %s %s" % ("PASS" if ok else "FAIL", code, what))
    if not ok:
        fails.append(code)


def case(src, name):
    """The text of `case "<name>":` up to the next top-level case label."""
    m = re.search(r'case "%s":(.*?)\n                case "' % re.escape(name), src, re.S)
    return m.group(1) if m else ""


def main():
    root = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else HERE
    src = os.path.join(root, "Source")
    proof = open(os.path.join(src, "RM_KnockbackProof.cs"), encoding="utf-8").read()
    three = open(os.path.join(src, "RM_KnockbackProof_StageThree.cs"), encoding="utf-8").read()
    sp = case(proof, "spared_states")
    check("S0", bool(sp), "spared_states case found")
    check("S1", "atBlast" in sp and re.search(r"stayed\s*=.*atBlast", sp) is not None,
          "spared_states compares each start with its cell read just after the blast (atBlast), not at the verdict")
    check("S2", re.search(r"ProofSchedule\.Add\(.*?TryStartCarry.*?Blast\(", sp, re.S) is not None
          and "carrier was not carrying" in sp,
          "spared_states starts the carry in the blast's scheduled action and is INVALID when the carrier is not carrying")
    pa = case(proof, "pawn_arc")
    check("A1", re.search(r'Colonist\(s, "w", O\(s, 4, 1\)', pa) is not None,
          "pawn_arc's walker starts one cell from the planned landing O(4,0)")
    fg = re.search(r'\["flyingGoods"\] = Lane\(([^\n]*)\),', three)
    check("W1", fg is not None and '"C"' in fg.group(1) and 'obs["C"].StartsWith("skip:flying_off")' in three,
          "the flyingGoods lane owns C and checks the corpse's flying_off skip")
    gg = re.search(r'Item\(s, "gg", "Steel", 10, O\(s, (-?\d+), (-?\d+)\)\)', three)
    seed = re.search(r'"SeedCloud"\)\.Invoke\(null, new object\[\] \{ map, O\(s, (-?\d+), (-?\d+)\), (\d+),', three)
    inside = bool(gg and seed) and max(abs(int(gg.group(1)) - int(seed.group(1))),
                                       abs(int(gg.group(2)) - int(seed.group(2)))) <= int(seed.group(3))
    check("W2", inside, "the sweep's gas-goods stack lies inside the seeded cloud")
    print("%s stage6 visit1 scenes: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
