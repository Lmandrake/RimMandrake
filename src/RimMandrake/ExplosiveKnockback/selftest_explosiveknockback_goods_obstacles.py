#!/usr/bin/env python3
"""Offline check of sc_goods_obstacles (design/concepts/ExplosiveKnockback/scenes.json; dl_goods_obstacles in record.json:
a flying good treats a closed door as a wall and rebounds keeping about 70 percent, passes over sandbags, and stops on
the last cell before deep water). Stage 6 visit 1 read it UNMEASURED: the entry goods_obstacles was named by
version/test_table.json but absent from RM_KnockbackProof.SceneNames (RIMMANDRAKE_WRITE_GOODS_OBSTACLES_SCENE_NAMED_NEVER_BUILT,
2026-11-15). The scene runs only in a game (its live command is in the table, UNRUN); this proves what can be read without one:
  N  goods_obstacles and its control lane goods_obstacles_control are in SceneNames, Build sends both to GoodsObstacles,
     and the csproj compiles the file that holds it
  G  the builder stages the three lanes (a closed door between walls, a sandbag line, deep water), asserts each start
     from the kernel plan (INVALID otherwise), runs the thing trace with a test row before the blasts, and judges the
     rebound against the keep percent, the door closed after, and zero despawn-spawn pairs
  R  the builder sets s.restore before it changes a setting
  T  version/test_table.json lists sc_goods_obstacles with entry_exists true and a command that runs both lanes

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_goods_obstacles.py [--src DIR]
--src reads the mod's files from DIR (laid out like this folder) instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TABLE = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback", "version", "test_table.json")
LANES = ("goods_obstacles", "goods_obstacles_control")
FILE = "RM_KnockbackProof_GoodsObstacles.cs"

fails = []


def check(code, ok, what):
    print(("PASS " if ok else "FAIL ") + code + " " + what)
    if not ok:
        fails.append(code + " " + what)


def rd(root, *p):
    path = os.path.join(root, *p)
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def main():
    root = HERE
    if "--src" in sys.argv:
        root = sys.argv[sys.argv.index("--src") + 1]
    proof = rd(root, "Source", "RM_KnockbackProof.cs")
    own = rd(root, "Source", FILE)
    csproj = rd(root, "Source", "RimMandrake_ExplosiveKnockback.csproj")
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    for lane in LANES:
        check("N1", lane in names, "%s is in RM_KnockbackProof.SceneNames" % lane)
        # the case may arm the scene first (its restore and pokes sit there, in the file whose Stage catch and Verdict run
        # restores: blind cycle 3, RIMMANDRAKE_RESTORE_KNOCKBACK_PROOF_POKES_LEAKED_AFTER_CLOSE); nothing else may sit between
        check("N2", re.search(r'case "%s":(\s*case "\w+":)*(\s*//[^\n]*|\s*s\.restore = FlightRestore\(s\);|'
                              r'\s*RimMandrakeExplosiveKnockbackSettings\.\w+ = \w+;)*\s*return GoodsObstacles\(s\);' % lane, proof) is not None,
              "Build sends %s to GoodsObstacles" % lane)
    check("N3", ('Include="%s"' % FILE) in csproj, "the csproj compiles " + FILE)
    check("N4", own.startswith("#if RM_PROOFS") and own.rstrip().endswith("#endif"), FILE + " is proof-build only")

    b = re.search(r"private static string GoodsObstacles\(Scene s\)(.*?)(?=\n        (?:private|internal|public) static |\Z)", own, re.S)
    body = b.group(1) if b else ""
    check("G0", bool(body), "GoodsObstacles(Scene s) exists")
    for needle, what in [
        ('"Door"', "lane D builds a door"), ('"Wall"', "lane D's door stands between walls"),
        ('"Sandbags"', "lane S builds a sandbag line"), ("TerrainDefOf.WaterDeep", "lane W lays deep water"),
        ('EndsWith("_control")', "the control lane leaves the obstacles out"),
        ("RM_KnockbackMath.Resolve(", "each start is asserted from the kernel plan"),
        ("KbStop.Door", "lane D's plan must stop at the door"), ("KbStop.Water", "lane W's plan must stop at the water"),
        ("KbStop.Distance", "the control's plan must run its full distance"),
        ("ReboundCells(", "the rebound is judged against the kernel's rebound cells"),
        ("goodsReboundKeepPercent", "the rebound reads the keep percent"),
        ('"item_rebound"', "the rebound is read from the journal"), ('"Door"', "the rebound names the door"),
        (".Open", "the door is read closed after"),
        ("TraceGoods(", "the thing trace runs"), ("traceRows0", "the trace takes a test row before the blasts"),
        ("_hops", "despawn-spawn pairs are counted"), ("_hidden", "unspawned, carrier-less samples are counted"),
        ("_inWater", "a stack in deep water is counted"), ("Fogged(", "lane W's stack must be visible"),
        ('return "lane ', "a failed start assertion returns its reason (Stage reads it INVALID)"), ("600", "the trace runs at most 600 ticks"),
    ]:
        check("G1", needle in body or needle in own, what + " (" + needle + ")")
    check("G2", len(re.findall(r"Blast\(O\(s, 0, ", body)) == 1 and "LaneZ" in body,
          "one grenade per lane, each at its own lane origin")
    # the arming lives in Build's goods_obstacles case (blind cycle 3): there the restore comes first and pokes both
    # settings the scene needs; GoodsObstacles itself pokes no setting at all (a poke there has no restore beside it)
    cm = re.search(r'case "goods_obstacles":\s*case "goods_obstacles_control":(.*?)return GoodsObstacles\(s\);', proof, re.S)
    arm = cm.group(1) if cm else ""
    r = arm.find("s.restore = FlightRestore(s)")
    pokes = [arm.find("RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;"), arm.find("RimMandrakeExplosiveKnockbackSettings.goodsRebound = true;")]
    check("R1", r >= 0 and all(p > r for p in pokes), "s.restore = FlightRestore(s) comes before the flyingGoods and goodsRebound pokes in Build's case")
    check("R2", re.search(r"RimMandrakeExplosiveKnockbackSettings\.\w+\s*(=(?!=)|\+=|-=)", body) is None,
          "GoodsObstacles itself writes no setting")

    try:
        t = json.load(open(TABLE, encoding="utf-8"))
        tests = t.get("tests", t)
        row = tests.get("sc_goods_obstacles", {}) if isinstance(tests, dict) else {}
    except (OSError, ValueError):
        row = {}
    check("T1", row.get("entry_exists") is True, "test_table sc_goods_obstacles entry_exists true")
    cmd = row.get("command", "")
    check("T2", all(l in cmd for l in LANES) and "--ticks 600" in cmd, "its command runs both lanes for 600 ticks")

    print("%s: %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
