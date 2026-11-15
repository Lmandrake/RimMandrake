#!/usr/bin/env python3
"""Offline check of the proof scene for sc_gas_shove_into_pit (design/concepts/ExplosiveKnockback/scenes.json): Stage 6
visit 1 (2026-11-15) read it UNMEASURED on every build, "unknown scene", because test_table.json named the entry
gas_into_pit and RM_KnockbackProof had no such case (RIMMANDRAKE_WRITE_GAS_INTO_PIT_SCENE_UNKNOWN_EVERY_BUILD). The scene
runs only in a game (its live command is in version/test_table.json); this proves what can be read without one:
  N  gas_into_pit and its control gas_into_pit_off are in SceneNames and reach a Build case
  G  the start assertions the scene names are INVALID guards: FlowWorks, the Cauldron's vent gas, its registration with
     the gas chain, an open pit (no cover), gas on the colonist's cell, the vent gas lit
  P  the geometry puts the first burst due west of the colonist: the colonist on the cloud's east edge (inside it), the
     cloud stopping short of the pit, the lit cell one cell due west and inside the cloud, within gasBurstRadius, and
     the one-cell shove's landing the pit's first cell
  C  the control unhooks the registration before lighting and the restore puts it back
  V  the verdict: main lane one launch of at most one cell with no impact, landed on the pit's first cell, one descent;
     control lane no burst, no launch, no descent, not in the pit
  T  test_table.json's sc_gas_shove_into_pit entry exists and its command runs both lanes

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_into_pit.py [--src DIR]
--src reads the mod's Source/ from DIR (laid out like this folder): the way it was watched red on acebabd5b6.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TABLE = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback", "version", "test_table.json")
fails = []


def check(code, ok, what):
    print("%s %s %s" % ("PASS" if ok else "FAIL", code, what))
    if not ok:
        fails.append(code)


def xy(text, pat):
    m = re.search(pat, text)
    return tuple(int(g) for g in m.groups()) if m else None


def main():
    root = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else HERE
    proof = open(os.path.join(root, "Source", "RM_KnockbackProof.cs"), encoding="utf-8").read()
    mod = open(os.path.join(root, "Source", "RM_KnockbackMod.cs"), encoding="utf-8").read()
    nm = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = set(re.findall(r'"([a-z0-9_]+)"', nm.group(1))) if nm else set()
    check("N0", len(names) > 20, "SceneNames parsed (%d names)" % len(names))
    check("N1", {"gas_into_pit", "gas_into_pit_off"} <= names, "gas_into_pit and gas_into_pit_off are in SceneNames")
    m = re.search(r'case "gas_into_pit":\s*case "gas_into_pit_off":(.*?)\n                case "', proof, re.S)
    body = m.group(1) if m else ""
    check("N2", bool(body), "one Build case takes both lanes")
    for code, guard in (("G1", '"FlowWorks not loaded"'), ("G2", "no vent gas"), ("G3", "not registered with the gas chain"),
                        ("G4", "could not dig an open pit"), ("G5", "holds no vent gas"), ("G6", "the vent gas did not light")):
        check(code, guard in body, "INVALID guard: %s" % guard.strip('"'))
    check("G7", "CoverAt(Map, O(s, 1, 0)) != null" in body, "the pit's first cell is asserted open (no cover)")

    pit = xy(body, r"Pit\(O\(s, (-?\d+), (-?\d+)\), (\d+), (\d+)\)")
    col = xy(body, r'Colonist\(s, "p", O\(s, (-?\d+), (-?\d+)\)\)')
    seed = xy(body, r'"SeedCloud"\)\.Invoke\(null, new object\[\] \{ Map, O\(s, (-?\d+), (-?\d+)\), (\d+), \d+ \}')
    lit = xy(body, r'"Ignite"\)\.Invoke\(vg, new object\[\] \{ O\(s, (-?\d+), (-?\d+)\), null \}')
    land = xy(body, r'\(IntVec3\)land\[0\]\["at"\] == O\(sc, (-?\d+), (-?\d+)\)')
    rad = re.search(r"public static float gasBurstRadius = ([0-9.]+)f;", mod)
    ok = all((pit, col, seed, lit, land, rad))
    check("P0", ok, "pit, colonist, cloud, lit cell, landing and gasBurstRadius all parsed")
    if ok:
        r_burst = float(rad.group(1))
        dist = lambda a, b: ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        in_pit = lambda c: pit[0] <= c[0] < pit[0] + pit[2] and pit[1] <= c[1] < pit[1] + pit[3]
        centre, r_cloud = (seed[0], seed[1]), seed[2]
        check("P1", dist(col, centre) <= r_cloud and not in_pit(col), "the colonist stands inside the cloud, off the pit")
        check("P2", centre[0] + r_cloud < pit[0], "the cloud stops short of the pit (no burst from its side)")
        check("P3", lit[1] == col[1] and lit[0] == col[0] - 1 and dist(lit, centre) <= r_cloud and dist(lit, col) <= r_burst,
              "the lit cell is one cell due west of the colonist, inside the cloud, within gasBurstRadius %.1f" % r_burst)
        shove = (2 * col[0] - lit[0], 2 * col[1] - lit[1])
        check("P4", land == shove and in_pit(shove) and shove[0] == pit[0],
              "the one-cell shove lands on the pit's first cell %s" % (shove,))
    off_at = body.find("RM_KnockbackCompat.VentGasRegistered = false")
    check("C1", "bool off = s.name == \"gas_into_pit_off\"" in body and 0 <= off_at < body.find('"Ignite"'),
          "the control unhooks the gas chain registration before lighting")
    check("C2", re.search(r"s\.restore = \(\) =>\s*\{\s*RM_KnockbackCompat\.VentGasRegistered = reg;", body) is not None
          and body.find("s.restore = ()") < off_at, "the restore, set before the unhook, puts the registration back")
    check("V1", "bursts == 0 && launch.Count == 0 && desc.Count == 0 && !inPit && cells == 0" in body,
          "control: no burst, no launch, no descent, not in the pit, not moved")
    check("V2", 'launch.Count == 1 && (int)launch[0]["planned"] <= 1 && Convert.ToSingle(launch[0]["impact"]) == 0f' in body
          and "landed && desc.Count == 1 && inPit" in body and "bursts >= 1 && shove && fell" in body,
          "main: one one-cell launch with no impact, landed on the pit's first cell, one descent")
    t = {}
    if os.path.exists(TABLE):
        t = json.load(open(TABLE, encoding="utf-8")).get("tests", {}).get("sc_gas_shove_into_pit", {})
    check("T1", t.get("entry_exists") is True and t.get("entry") == "gas_into_pit"
          and "--scenes gas_into_pit,gas_into_pit_off " in t.get("command", ""),
          "test_table.json: sc_gas_shove_into_pit entry exists, its command runs both lanes")
    print("%s %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
