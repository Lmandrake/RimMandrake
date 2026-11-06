#!/usr/bin/env python3
"""selftest_natives_drink_own_water.py — every Baroque Biome native drinks its own environmental water
(NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME).

Owner, 2026-11-01: "Yes, natives should drink their own environmental water. That's a ruling for all Baroque Biomes,
period, including this one." First instance: RM_Noohm and RM_Shulla standing in the Scald's boil accrued RM_Dehydration
(SCALD_NATIVES_THIRST_PROBE_PARCHED_LAKESIDE): the Scald terrains name RM_Liquid_BoilingWater, a row with no
thirstQuality (use class Never), so RM_ThirstUtility.DrinkLiquidAt returned null for everyone, natives included.

Two halves, both offline:
  A. SOURCE (the thirst code is Verse-bound; the C# SelfTest cannot run it): the production .cs, comments masked, lets a
     native animal find, keep and drink a terrain marked nativeWater, and no one else. Undo mutants must each go RED.
  B. AUDIT over every RM_/RSW_/RUT_ BiomeDef: each Water terrain the biome paints (its def's terrains, plus Water terrains
     named after it) resolves to a liquid its natives may drink: a row the Q12 native rule already allows (any use class
     but Never), or a terrain the patches mark nativeWater. NOT_WATER is the explicit list of Water-tagged terrains that
     are not water at all. Writes Tools/native_water_audit.md; a BLOCKED row fails. The probe mutant (forget the
     nativeWater marks) must turn the Scald BLOCKED, or the audit is blind.

    python3 src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
THIRST = HERE / "Source" / "Thirst"
UTIL = THIRST / "RM_ThirstUtility.cs"
JOBS = THIRST / "RM_ThirstJobs.cs"
LIQ = HERE / "Source" / "LiquidTypes" / "LiquidDef.cs"
REPORT = HERE / "Tools" / "native_water_audit.md"
sys.path.insert(0, str(HERE / "Tools"))
import selftest_water_terrains_name_liquid as W  # noqa: E402  (terrain loader, Water-tag inheritance)

# Water-tagged for pathing or freezing, not a body anything drinks: the ruling does not reach them.
NOT_WATER = {
    "RM_DeepSand": "deep sand; Water-tagged for wading only (DEEP_SAND_FIX_READS_AS_FRESHWATER)",
    "RM_SolidPropane": "frozen propane, a solid",
}


def mask_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def body(src: str, sig: str) -> str:
    at = src.find(sig)
    if at < 0:
        return ""
    open_ = src.find("{", at)
    depth = 0
    for k in range(open_, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[open_:k + 1]
    return ""


def flat(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def source_faults(util: str, jobs: str, liq: str) -> list[str]:
    f = []
    ext = body(liq, "class RM_DrinkableTerrainExtension")
    if "public bool nativeWater;" not in ext:
        f.append("RM_DrinkableTerrainExtension has no nativeWater field")
    native = flat(body(util, "public static bool NativeHere("))
    if "!pawn.RaceProps.Humanlike" not in native or "CommonalityOfAnimal(pawn.kindDef) > 0f" not in native:
        f.append("NativeHere no longer means a non-humanlike on the map biome's roster")
    home = flat(body(util, "public static bool HomeWater("))
    if "ext.nativeWater" not in home or "NativeHere(pawn)" not in home:
        f.append("HomeWater does not require both the nativeWater mark and NativeHere")
    at = flat(body(util, "public static LiquidDef DrinkLiquidAt(TerrainDef terrain, Pawn pawn)"))
    if "!HomeWater(pawn, terrain)" not in at:
        f.append("DrinkLiquidAt(terrain, pawn) widens past HomeWater")
    find = flat(body(util, "public static bool TryFindDrinkCell(Pawn pawn, float level, out IntVec3 cell, out LiquidDef liquid, out RM_DrinkUse use"))
    if "bool home = !only.HasValue && HomeWater(pawn, t);" not in find:
        f.append("TryFindDrinkCell does not compute home water (or widens the salt break's search)")
    if "!(home || MayDrink(pawn, l, level, only))" not in find:
        f.append("TryFindDrinkCell does not let home water past MayDrink")
    if "RM_DrinkUse u = home && UseOf(l) == RM_DrinkUse.Never ? RM_DrinkUse.LastResort : UseOf(l);" not in find:
        f.append("TryFindDrinkCell lets home water of use class Never rank as Never (or above potable water)")
    if "home ? DrinkLiquidAt(t, pawn) : DrinkLiquidAt(t)" not in find:
        f.append("TryFindDrinkCell does not read the native's liquid at home water")
    drv = flat(body(jobs, "class JobDriver_RM_DrinkFromTerrain"))
    if drv.count("DrinkLiquidAt(Map.terrainGrid.TerrainAt(job.targetA.Cell), pawn)") != 1:
        f.append("the drink job's FailOn drops a native at home water (no pawn passed)")
    if drv.count("DrinkLiquidAt(Map.terrainGrid.TerrainAt(c), pawn)") != 1:
        f.append("the drink job's finish toil drinks nothing at home water (no pawn passed)")
    drink = flat(body(util, "public static void Drink("))
    if "if (!pawn.RaceProps.Humanlike && UseOf(liquid) != RM_DrinkUse.Potable) { return; }" not in drink:
        f.append("Drink no longer spares an animal the effects of non-potable water")
    return f


def check_source() -> list[str]:
    util, jobs, liq = (mask_comments(p.read_text(encoding="utf-8")) for p in (UTIL, JOBS, LIQ))
    faults = source_faults(util, jobs, liq)
    mutants = {
        "no field": (util, jobs, liq.replace("public bool nativeWater;", "")),
        "mark not required": (util.replace("&& ext.nativeWater ", ""), jobs, liq),
        "not native": (util.replace("&& ext.liquid != null && NativeHere(pawn)", "&& ext.liquid != null"), jobs, liq),
        "MayDrink kept": (util.replace("!(home || MayDrink(pawn, l, level, only))", "!MayDrink(pawn, l, level, only)"), jobs, liq),
        "salt break widened": (util.replace("bool home = !only.HasValue && HomeWater", "bool home = HomeWater"), jobs, liq),
        "rank lost": (util.replace("RM_DrinkUse u = home && UseOf(l) == RM_DrinkUse.Never ? RM_DrinkUse.LastResort : UseOf(l);", "RM_DrinkUse u = UseOf(l);"), jobs, liq),
        "driver FailOn": (util, jobs.replace("TerrainAt(job.targetA.Cell), pawn)", "TerrainAt(job.targetA.Cell))"), liq),
        "driver finish": (util, jobs.replace("TerrainAt(c), pawn)", "TerrainAt(c))"), liq),
    }
    for name, m in mutants.items():
        if m == (util, jobs, liq):
            faults.append(f"mutant '{name}' did not apply (the check reads text that is gone)")
        elif not source_faults(*m):
            faults.append(f"mutant '{name}' stayed green: the check cannot fail")
    return faults


def load_world():
    terrains, _ = W.load()
    water = {n for n, d in terrains.items() if W.is_water(d, terrains)}
    rows, t2l, marks = {}, {}, set()
    for f in W._globs("Defs"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag.endswith("LiquidDef") and d.findtext("defName"):
                n = d.findtext("defName").strip()
                rows[n] = d
                for k in ("shallow", "deep", "chestDeep"):
                    v = (d.findtext(f"terrainSuite/{k}") or "").strip()
                    if v:
                        t2l[v] = n
    ext = {}
    for f in W._globs("Patches"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for op in root.iter("match"):
            m = re.search(r'TerrainDef\[defName="([^"]+)"\]', op.findtext("xpath") or "")
            for li in op.iter("li"):
                if m and li.get("Class", "").endswith("RM_DrinkableTerrainExtension"):
                    ext[m.group(1)] = (li.findtext("liquid") or "").strip()
                    if (li.findtext("nativeWater") or "").strip().lower() == "true":
                        marks.add(m.group(1))
    for n, d in terrains.items():
        for li in d.findall("modExtensions/li"):
            if li.get("Class", "").endswith("RM_DrinkableTerrainExtension"):
                ext[n] = (li.findtext("liquid") or "").strip()
                if (li.findtext("nativeWater") or "").strip().lower() == "true":
                    marks.add(n)
    biomes = {}
    for f in sorted(W._globs("Defs")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            b = (d.findtext("defName") or "").strip()
            if d.tag != "BiomeDef" or not re.match(r"^(RM|RSW|RUT)_", b):
                continue
            wa = d.find("wildAnimals")
            biomes[b] = (f, d, 0 if wa is None else len(list(wa)))
    return terrains, water, rows, t2l, ext, marks, biomes


def liquid_of(t, rows, t2l, ext, water):
    """RM_ThirstUtility.DrinkLiquidAt's order: the registry row (suite), then the terrain adapter, then fresh water only
    for an unadopted water terrain that is not an ocean (vanilla oceans read salt through the registry suite); else
    nothing (None)."""
    lq = t2l.get(t) or ext.get(t)
    if lq:
        return lq
    is_water = t in water or re.match(r"^(Water|Lake|River|Marsh)", t)
    return "RM_Liquid_FreshWater" if is_water and "Ocean" not in t else None


def use_of(row):
    if row is None:
        return "Never"
    u = (row.findtext("useClass") or "").strip()
    if u:
        return u
    q = (row.findtext("thirstQuality") or "").strip()
    return {"": "Never", "Potable": "Potable", "Distilled": "Potable", "Fouled": "BreakOnly"}.get(q, "LastResort")


def audit(marks_override=None):
    terrains, water, rows, t2l, ext, marks, biomes = load_world()
    if marks_override is not None:
        marks = marks_override
    lines, blocked = [], []
    for b, (f, d, roster) in sorted(biomes.items()):
        stem = re.sub(r"^(RM|RSW|RUT)_(The)?", "", b)
        cands = {t.text.strip() for t in d.iter() if t.tag in ("terrain", "terrainDef") and t.text}
        cands |= {n for n in water if len(stem) >= 4 and stem in n}
        for t in sorted(cands):
            if t not in water and not re.match(r"^(Water|Lake|River|Ocean|Marsh)", t):
                continue
            liq = liquid_of(t, rows, t2l, ext, water)
            row = rows.get(liq)
            use = use_of(row)
            drink = row is not None and bool((row.findtext("thirstQuality") or "").strip())  # C#: no quality, no drink
            if t in NOT_WATER:
                v = "not water: " + NOT_WATER[t]
            elif not drink and t in marks:
                v = "drinks (home water, nativeWater)"
            elif not drink:
                v = "BLOCKED"
            elif use == "Potable":
                v = "drinks (potable for everyone)"
            elif use != "Never":
                v = f"drinks (Q12 native rule, {use})"
            elif t in marks:
                v = "drinks (home water, nativeWater)"
            else:
                v = "BLOCKED"
            if v == "BLOCKED":
                if roster:
                    blocked.append(f"{b}: {t} -> {liq}")
                else:
                    v = "BLOCKED (no roster in def; a patch-added cast would hit it)"
                    blocked.append(f"{b}: {t} -> {liq} (patch roster)")
            lines.append(f"| {b} | {roster} | {t} | {liq} | {use} | {v} |")
    return lines, blocked, biomes


def main() -> int:
    faults = check_source()
    lines, blocked, biomes = audit()
    # sanity probes: the instrument must see the known Baroque water
    if len(biomes) < 40:
        faults.append(f"instrument blind: only {len(biomes)} of our BiomeDefs seen")
    scald = [l for l in lines if l.startswith("| RM_TheScald |") and "RM_Liquid_BoilingWater" in l]
    if len(scald) < 6:
        faults.append(f"instrument blind: {len(scald)} Scald boil terrains seen, want 6")
    if not any("RM_GreySea" in l and "RM_Liquid_Brine" in l for l in lines):
        faults.append("instrument blind: the Grey Sea's brine not seen")
    _, probe_blocked, _ = audit(marks_override=set())
    if not any(x.startswith("RM_TheScald:") for x in probe_blocked):
        faults.append("probe mutant (no nativeWater marks) left the Scald drinkable: the audit cannot fail")
    faults += ["BLOCKED " + x for x in blocked]
    REPORT.write_text(
        "# Natives drink their own water: every-biome audit\n\n"
        "Generated by `src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py` "
        "(NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME). Owner, 2026-11-01: *\"Yes, natives should drink their own "
        "environmental water. That's a ruling for all Baroque Biomes, period, including this one.\"*\n\n"
        "Each row is a Water terrain the biome paints (its BiomeDef's terrains, or a Water terrain named after it). "
        "`roster` counts the def's own `<wildAnimals>`; RUT twins get their cast by patch. Biomes with no water row "
        "rely on map-generated rivers and lakes, which are fresh water for everyone.\n\n"
        "| biome | roster | terrain | liquid | use class | a native |\n|---|---|---|---|---|---|\n"
        + "\n".join(lines) + "\n", encoding="utf-8")
    if faults:
        print(f"FAIL {len(faults)}:")
        for x in faults:
            print("  ", x)
        return 1
    print(f"PASS source + 8 mutants red; {len(biomes)} biomes, {len(lines)} water rows, 0 blocked; report {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
