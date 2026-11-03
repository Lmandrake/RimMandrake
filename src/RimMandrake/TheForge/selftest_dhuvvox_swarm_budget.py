#!/usr/bin/env python3
"""Dhuvvox swarm budget: does a Forge map ever hold enough dhuvvox to need swarm aggregation?

FORGE_DHUVVOX_SWARM_REMAINDER_1, open question 2 ("Swarm aggregation for performance: is there a
measured performance problem?"). This answers it offline with vanilla's own arithmetic, no game:

  RimWorld 1.6 WildAnimalSpawner (decompiled): DesiredTotalAnimalWeight = map.Area * density / 10000,
  each spawn picks a kind by commonality / wildGroupSize.Average and lands a whole group, and
  CurrentTotalAnimalWeight sums kindDef.ecoSystemWeight over unfactioned spawned pawns (a SEALED dhuvvox
  is still a spawned pawn, so it counts and is not respawned over). At a full ecosystem the expected
  count of kind k is therefore W * c_k / sum_j(c_j * e_j). GenStep_Animals fills to the same target.

On top of that resident population, entering the Rain phase erupts SwarmSize more (RM_GameCondition_ForgeCycle.cs,
EruptSwarm, once per Rain; ResealSwarm removes them at the Freeze). The peak awake count is therefore the
eruption plus the residents, taken here as the expected count plus one more full group (wildGroupSize max).

The roster is parsed as XML elements (BiomeDef RM_TheForge plus the Utinni patch rows), ecoSystemWeight
and wildGroupSize from each PawnKindDef (vanilla default 1.0 and 1 when unset). The dhuvvox has no
gestation and no egg layer, so births never add to the spawner's count; that is checked too.

Verdict: the peak on the largest vanilla map (325x325), roster at its thinnest (the RSW_ patch rows
absent), stays under SWARM_BUDGET awake pawns, the scale vanilla's own mass events (manhunter packs, infestations)
reach without any aggregation, so aggregation is not built. The awake
scuttle sound is capped by its SoundDef maxSimultaneous regardless of count. If a roster or weight
change pushes the estimate over the budget, this test goes red: that is the moment to revisit
aggregation, not before. A mutant (dhuvvox commonality x100) must go over the budget, proving the
instrument can fail.

    python3 src/RimMandrake/TheForge/selftest_dhuvvox_swarm_budget.py
"""
import glob
import re
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheForge_Biome.xml")
PATCH = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_TheForge.xml")
NATIVES = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_TheForgeNatives.xml")
SOUNDS = os.path.join(HERE, "Defs", "SoundDefs", "RM_ForgeVoices.xml")
CYCLE = os.path.join(HERE, "Source", "RM_GameCondition_ForgeCycle.cs")

SWARM_BUDGET = 100         # awake dhuvvox on one map before per-pawn ticking is worth aggregating
MAX_MAP_SIDE = 325         # largest vanilla map size option
SCUTTLE_VOICE_CAP = 8      # most simultaneous scuttle one-shots we accept

fails = []


def check(name, ok, msg):
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, msg))
    if not ok:
        fails.append(name)


def parse(path):
    return ET.parse(path).getroot()


def group_avg(text):
    if text is None or not text.strip():
        return 1.0
    t = text.strip()
    if "~" in t:
        a, b = t.split("~")
        return (float(a) + float(b)) / 2.0
    return float(t)


def group_max(text):
    if text is None or not text.strip():
        return 1
    return int(text.strip().split("~")[-1])


def kinds():
    out = {}
    for f in glob.glob(os.path.join(REPO, "src", "**", "*.xml"), recursive=True):
        try:
            root = parse(f)
        except ET.ParseError:
            continue
        for k in root.iter("PawnKindDef"):
            dn = k.findtext("defName")
            if dn:
                e = k.findtext("ecoSystemWeight")
                g = k.findtext("wildGroupSize")
                out.setdefault(dn, []).append((float(e) if e and e.strip() else 1.0, group_avg(g), group_max(g)))
    return out


def roster():
    base, density = {}, None
    for bd in parse(BIOME).iter("BiomeDef"):
        if bd.findtext("defName") == "RM_TheForge":
            density = float(bd.findtext("animalDensity"))
            base = {c.tag: float(c.text) for c in bd.find("wildAnimals")}
    patched = {}
    for v in parse(PATCH).iter("value"):
        for c in v:
            patched[c.tag] = float(c.text)
    return density, base, patched


def expected(rows, kd, density, side, target="RM_Dhuvvox"):
    w = side * side * density / 10000.0
    denom = sum(c * kd[k][0] for k, c in rows.items())
    return w * rows[target] / denom


def main():
    kd_all = kinds()
    density, base, patched = roster()
    check("roster parsed", density and len(base) >= 8 and "RM_Dhuvvox" in base,
          "density %s, %d base rows, %d patch rows" % (density, len(base), len(patched)))
    missing = [k for k in list(base) + list(patched) if k not in kd_all]
    dup = [k for k in list(base) + list(patched) if len(kd_all.get(k, [])) > 1]
    check("every roster kind resolves once", not missing and not dup, "missing %s, duplicated %s" % (missing, dup))
    if missing:
        return
    kd = {k: v[0] for k, v in kd_all.items()}
    e_d, g_d, gmax_d = kd["RM_Dhuvvox"]
    check("dhuvvox weights read", 0 < e_d < 1 and g_d > 1, "ecoSystemWeight %.2f, group avg %.1f" % (e_d, g_d))

    natives = parse(NATIVES)
    dh = next(t for t in natives.iter("ThingDef") if t.findtext("defName") == "RM_Dhuvvox")
    breeds = dh.find(".//gestationPeriodDays") is not None or any(
        (li.get("Class") or "").endswith("EggLayer") for li in dh.iter("li"))
    check("dhuvvox does not breed", not breeds, "births would bypass the spawner's weight cap")

    full = dict(base)
    full.update(patched)
    for label, rows in (("roster with RSW rows", full), ("roster without RSW rows", base)):
        for side in (250, MAX_MAP_SIDE):
            n = expected(rows, kd, density, side)
            print("     %s, %dx%d: expected dhuvvox %.2f (%.2f groups of ~%.0f)" % (label, side, side, n, n / g_d, g_d))
    src = open(CYCLE, encoding="utf-8").read()
    m_size = re.search(r"public const int SwarmSize = (\d+);", src)
    calls = len(re.findall(r"^\s*EruptSwarm\(map\);", src, re.M))
    check("eruption size read", m_size is not None and calls == 1,
          "SwarmSize %s, %d EruptSwarm call site(s) (one per Rain entry)" % (m_size.group(1) if m_size else None, calls))
    if m_size is None:
        return
    swarm = int(m_size.group(1))

    def peak(rows):
        return swarm + expected(rows, kd, density, MAX_MAP_SIDE) + gmax_d

    worst = peak(base)
    check("peak awake dhuvvox under budget", worst < SWARM_BUDGET,
          "eruption %d + residents (expected %.2f + one group of %d) = %.1f < %d on %dx%d: no swarm aggregation needed"
          % (swarm, worst - swarm - gmax_d, gmax_d, worst, SWARM_BUDGET, MAX_MAP_SIDE, MAX_MAP_SIDE))

    mutant = dict(base)
    mutant["RM_Dhuvvox"] *= 100
    m = peak(mutant)
    check("mutant x100 commonality goes over budget", m >= SWARM_BUDGET, "%.1f >= %d (the instrument can fail)" % (m, SWARM_BUDGET))

    sd = next((s for s in parse(SOUNDS).iter("SoundDef") if s.findtext("defName") == "RM_DhuvvoxScuttle"), None)
    cap = int(sd.findtext("maxSimultaneous") or 0) if sd is not None else 0
    check("scuttle voices capped", 0 < cap <= SCUTTLE_VOICE_CAP, "RM_DhuvvoxScuttle maxSimultaneous %d" % cap)


if __name__ == "__main__":
    main()
    print("RESULT: %s" % ("FAIL " + ", ".join(fails) if fails else "PASS"))
    sys.exit(1 if fails else 0)
