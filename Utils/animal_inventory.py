#!/usr/bin/env python3
"""
animal_inventory.py — dump every animal in the modded game to CSV.

VERSION 1.2  (2026-08-10)   Project: G:/My Drive/Personal/Rimworld/Utils/
Docs/manifest: Utils/README.md  ("animal_inventory.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

CHANGELOG
  1.2  load-set correctness. Mod/folder resolution moved to rimworld_loadset:
       honours LoadFolders.xml (incl. IfModActive / IfModNotActive) and scans
       ONLY the folders the game loads. v1.1 also scanned each mod's 1.5 and
       Common folders, so its CSVs contained animals that cannot spawn and
       missed conditional ones. Fixes the Core/DLC modName "?" bug at the same
       time (About name now falls back to the folder name).
  1.1  temperature group (comfy + insulation -> effective range, HEAT/COLD_HARDY);
       attacks + life stages split to their own CSVs; derived FAST_BREEDER and
       RENEWABLE_YIELD; pawnkind aggregation; ~112 columns.
  1.0  first cut: identity, core race fields, biome map, conflicts, patch watch.

FIXED IN 1.2: Core/DLC rows previously showed modName "?" (Ludeon About.xml has
no <name>). read_about() now falls back to the folder name. Measured field
coverage on the 562-mod stack is in Utils/README.md.

MAINTENANCE — adding a column
  1. simple <race> field -> append to RACE_SIMPLE as (csvColumn, "race/xpath")
  2. statBases entry     -> add to STAT_MAP as "StatDefName": "csvColumn"
  3. comp-derived        -> extend parse_comps()
  4. derived/computed    -> compute in scan_defs() after the comp block
  5. ALWAYS add the name to COLUMNS. DictWriter uses extrasaction="ignore", so a
     column missing from COLUMNS is silently dropped. This is the one easy mistake.

PERFORMANCE: run natively on Windows. Through the Cowork device bridge the mount
does ~210 files/sec and this touches tens of thousands of XML files (>10 min).
Natively it is seconds.

Offline. Reads the Defs on disk; the game does NOT need to be running, and this
touches no savegame. Run it on the Windows box for full filesystem speed.

WHY OFFLINE (and when you need the live bridge instead)
-------------------------------------------------------
For patching work the *file* matters more than the resolved value: you cannot
write a PatchOperation without knowing which mod and which xpath to target. A
live RimBridge dump gives you post-resolution values but hides their origin.
So: this is the authoring tool; a live dump is the verification tool.

What this CANNOT see (documented honestly, do not forget it):
  * PatchOperation results. Patches apply at load; this reads base XML.
    Mitigation: pass 3 scans Patches/ and reports every operation whose xpath
    touches an animal/biome, so you at least know where to look.
  * Full <ParentName> inheritance. Resolved one graph, best-effort; abstract
    parents in another mod may resolve differently in game.
  * Mod-vs-mod override winners for identical defNames (flagged, not resolved).
  * True shortHashes. Computed with RimWorld's StableStringHash, but the game
    resolves collisions across the whole loaded set per defType, so treat the
    value as a CANDIDATE until cross-checked against a live dump.

OUTPUTS
  animals.csv          one row per animal, ~90 columns (see COLUMN GROUPS)
  animal_attacks.csv   one row per attack tool (animals have several)
  animal_lifestages.csv one row per life stage (age thresholds, body scale)
  biome_animals.csv    every (biome, animal) pair, from BOTH directions
  conflicts.csv        duplicate (biome, animal) pairs — the CWAS crash class
  patch_watch.csv      PatchOperations touching animals/biomes

COLUMN GROUPS in animals.csv
  identity      defName label modName packageId workshopId loadOrder sourceFile
                shortHashCandidate abstractName parentName duplicateDefName
  temperament   wildness trainability petness intelligence nameOnTameChance
                nameOnNuzzleChance nuzzleMtbHours roamMtbDays playerCanChangeMaster
                trainableTags untrainableTags
  combat        predator maxPreyBodySize manhunterOnDamageChance
                manhunterOnTameFailChance canArriveManhunter combatPower
                attackCount attackBestPower attackBestDPS attackSummary
                armorSharp armorBlunt armorHeat moveSpeed deathActionWorker
  physiology    baseBodySize baseHealthScale baseHungerRate foodType lifeExpectancy
                fleshType bloodDef body mass carryingCapacity
                toxicResistance psychicSensitivity minimumHandlingSkill
  temperature   comfyTempMin comfyTempMax insulationCold insulationHeat
                effectiveTempMin effectiveTempMax tempRangeC tempSpan
                HEAT_HARDY (>=50C) COLD_HARDY (<=-40C)
  reproduction  gestationPeriodDays litterSizeMin/Max mateMtbHours hasGenders
                lifeStageCount ageAdultYears maxLittersPerYear annualOffspringMax
                FAST_BREEDER
  production    leatherDef leatherAmount meatAmount useMeatFrom milk* wool* egg*
                RENEWABLE_YIELD
  ecology       wildBiomes biomeCount wildGroupSizeMin/Max ecoSystemWeight
  performance   tickerType compCount comps modExtensions
  trade         tradeTags tradeability marketValue
  meta          pawnKinds description

USAGE
  python animal_inventory.py
  python animal_inventory.py --out D:\\Luke\\dev\\rimtools\\out
"""

import argparse
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

# Shared load-set resolver. Lives beside this file so every offline tool in the
# project agrees on which folders the game actually reads.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimworld_loadset import build_load_set, def_dirs as loadset_def_dirs  # noqa: E402

# ---------------------------------------------------------------- defaults
D_CONFIG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
D_WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
D_LOCAL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
D_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

# NOTE: there is deliberately no VERSION_DIRS here any more. v1.1 used
# ("1.6", "1.5", "Common", "") which scanned 1.5 folders the game never loads
# and ignored LoadFolders.xml entirely, so conditional folders were mishandled
# in both directions. rimworld_loadset resolves this properly.

# Fast-breeder threshold: annual offspring above this trips the ranch guardrail.
# (Standing rule: never ranch a tamed breeding herd into a meat/leather/wool printer.)
FAST_BREEDER_ANNUAL = 12.0


# ---------------------------------------------------------------- helpers
def stable_string_hash(s):
    """RimWorld GenText.StableStringHash."""
    if s is None:
        return 0
    num = 23
    for ch in s:
        num = (num * 31 + ord(ch)) & 0xFFFFFFFF
    if num >= 0x80000000:
        num -= 0x100000000
    return num


def short_hash(defname):
    return (stable_string_hash(defname) % 65535) + 1 if defname else ""


def txt(node, path, default=""):
    if node is None:
        return default
    el = node.find(path)
    return el.text.strip() if el is not None and el.text else default


def fnum(s):
    try:
        return float(str(s).strip())
    except Exception:
        return None


def parse_xml(path):
    try:
        return ET.parse(path).getroot()
    except Exception:
        try:
            raw = open(path, encoding="utf-8", errors="replace").read()
            raw = re.sub(r"^\s*<\?xml[^>]*\?>", "", raw).strip()
            return ET.fromstring(raw)
        except Exception:
            return None


def def_dirs(mod, subdir):
    """Delegates to the shared resolver; see rimworld_loadset.def_dirs."""
    return loadset_def_dirs(mod, subdir)


def walk_xml(root_dir):
    for dp, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".xml"):
                yield os.path.join(dp, f)


# ---------------------------------------------------------------- mod list
def load_active_mods(config, workshop, local, data):
    """
    The real load set, in load order. See rimworld_loadset for why this is not
    just "walk the Workshop tree": version folders and LoadFolders.xml both make
    the on-disk file set a superset of what the game reads.
    """
    try:
        mods, missing, version = build_load_set(config, [workshop, local, data])
    except OSError as exc:
        sys.exit(str(exc))
    ndirs = sum(len(m["contentDirs"]) for m in mods)
    print(f"load set: version {version}, {len(mods)} active mods "
          f"-> {ndirs} content folders")
    return mods, missing


# ---------------------------------------------------------------- extraction
RACE_SIMPLE = [
    # (csv column, xpath under the ThingDef)
    ("wildness", "race/wildness"), ("trainability", "race/trainability"),
    ("petness", "race/petness"), ("intelligence", "race/intelligence"),
    ("nameOnTameChance", "race/nameOnTameChance"),
    ("nameOnNuzzleChance", "race/nameOnNuzzleChance"),
    ("nuzzleMtbHours", "race/nuzzleMtbHours"), ("roamMtbDays", "race/roamMtbDays"),
    ("playerCanChangeMaster", "race/playerCanChangeMaster"),
    ("predator", "race/predator"), ("maxPreyBodySize", "race/maxPreyBodySize"),
    ("manhunterOnDamageChance", "race/manhunterOnDamageChance"),
    ("manhunterOnTameFailChance", "race/manhunterOnTameFailChance"),
    ("deathActionWorker", "race/deathActionWorkerClass"),
    ("baseBodySize", "race/baseBodySize"), ("baseHealthScale", "race/baseHealthScale"),
    ("baseHungerRate", "race/baseHungerRate"), ("foodType", "race/foodType"),
    ("lifeExpectancy", "race/lifeExpectancy"), ("fleshType", "race/fleshType"),
    ("bloodDef", "race/bloodDef"), ("body", "race/body"),
    ("gestationPeriodDays", "race/gestationPeriodDays"),
    ("mateMtbHours", "race/mateMtbHours"), ("hasGenders", "race/hasGenders"),
    ("herdAnimal", "race/herdAnimal"), ("packAnimal", "race/packAnimal"),
    ("leatherDef", "race/leatherDef"), ("useMeatFrom", "race/useMeatFrom"),
    ("meatLabel", "race/meatLabel"), ("needsRest", "race/needsRest"),
    ("doesntMove", "race/doesntMove"), ("canBecomeShambler", "race/canBecomeShambler"),
    ("nameGenerator", "race/nameGenerator"),
    ("thinkTreeMain", "race/thinkTreeMain"),
]

STAT_MAP = {
    "MoveSpeed": "moveSpeed", "MarketValue": "marketValue", "Mass": "mass",
    "ArmorRating_Sharp": "armorSharp", "ArmorRating_Blunt": "armorBlunt",
    "ArmorRating_Heat": "armorHeat", "ComfyTemperatureMin": "comfyTempMin",
    "ComfyTemperatureMax": "comfyTempMax", "LeatherAmount": "leatherAmount",
    "MeatAmount": "meatAmount", "CarryingCapacity": "carryingCapacity",
    "ToxicResistance": "toxicResistance", "ToxicEnvironmentResistance": "toxicEnvResistance",
    "PsychicSensitivity": "psychicSensitivity", "FilthRate": "filthRate",
    "MinimumHandlingSkill": "minimumHandlingSkill", "AnimalsLearningFactor": "animalsLearningFactor",
    "Insulation_Cold": "insulationCold", "Insulation_Heat": "insulationHeat",
}


def parse_tools(node):
    """Combat behaviour: every attack tool, plus aggregates."""
    tools = []
    for t in node.findall("tools/li"):
        caps = [c.text.strip() for c in t.findall("capacities/li") if c.text]
        power = fnum(txt(t, "power"))
        cd = fnum(txt(t, "cooldownTime"))
        tools.append({
            "label": txt(t, "label"), "capacities": ";".join(caps),
            "power": txt(t, "power"), "cooldownTime": txt(t, "cooldownTime"),
            "armorPenetration": txt(t, "armorPenetration"),
            "linkedBodyPartsGroup": txt(t, "linkedBodyPartsGroup"),
            "chanceFactor": txt(t, "chanceFactor"),
            "dps": round(power / cd, 2) if power and cd else "",
        })
    best_p = max([fnum(t["power"]) or 0 for t in tools], default=0)
    best_d = max([t["dps"] or 0 for t in tools], default=0)
    summary = "; ".join(
        f"{t['label'] or t['capacities']}({t['power']}p/{t['cooldownTime']}s)" for t in tools)
    return tools, {
        "attackCount": len(tools),
        "attackBestPower": best_p or "",
        "attackBestDPS": best_d or "",
        "attackSummary": summary[:300],
    }


def parse_comps(node):
    """Production comps: milk, wool, eggs, explosive. Feeds the ranch guardrail."""
    out = {"compCount": 0, "comps": "", "milkDef": "", "milkIntervalDays": "",
           "milkAmount": "", "woolDef": "", "shearIntervalDays": "", "woolAmount": "",
           "eggFertilizedDef": "", "eggUnfertilizedDef": "", "eggLayIntervalDays": "",
           "eggCountRange": "", "explosiveRadius": ""}
    names = []
    for c in node.findall("comps/li"):
        cls = c.get("Class", "") or txt(c, "compClass")
        if cls:
            names.append(cls.split(".")[-1])
        short = cls.split(".")[-1]
        if short == "CompProperties_Milkable":
            out["milkDef"] = txt(c, "milkDef")
            out["milkIntervalDays"] = txt(c, "milkIntervalDays")
            out["milkAmount"] = txt(c, "milkAmount")
        elif short == "CompProperties_Shearable":
            out["woolDef"] = txt(c, "woolDef")
            out["shearIntervalDays"] = txt(c, "shearIntervalDays")
            out["woolAmount"] = txt(c, "woolAmount")
        elif short == "CompProperties_EggLayer":
            out["eggFertilizedDef"] = txt(c, "eggFertilizedDef")
            out["eggUnfertilizedDef"] = txt(c, "eggUnfertilizedDef")
            out["eggLayIntervalDays"] = txt(c, "eggLayIntervalDays")
            out["eggCountRange"] = txt(c, "eggCountRange")
        elif short == "CompProperties_Explosive":
            out["explosiveRadius"] = txt(c, "explosiveRadius")
    out["compCount"] = len(names)
    out["comps"] = ";".join(names)[:250]
    return out


def parse_litter(node):
    """litterSizeCurve points look like <li>(1,0)</li> ... return min/max size."""
    pts = []
    for li in node.findall("race/litterSizeCurve/points/li"):
        s = (li.text or "").strip().strip("()")
        parts = [p.strip() for p in s.split(",")]
        if len(parts) == 2:
            x, y = fnum(parts[0]), fnum(parts[1])
            if x is not None and y is not None and y > 0:
                pts.append(x)
    if not pts:
        return "", ""
    return min(pts), max(pts)


def parse_lifestages(node):
    rows = []
    for i, li in enumerate(node.findall("race/lifeStageAges/li")):
        rows.append({"index": i, "def": txt(li, "def"), "minAge": txt(li, "minAge"),
                     "soundWounded": txt(li, "soundWounded")})
    adult = ""
    for r in rows:
        if "Adult" in (r["def"] or ""):
            adult = r["minAge"]
            break
    return rows, len(rows), adult


# ---------------------------------------------------------------- scan
def scan_defs(mods):
    animals, pawnkinds, biomes = {}, defaultdict(list), {}
    attacks, lifestages = [], []
    dupnames = defaultdict(list)

    for m in mods:
        for d in def_dirs(m, "Defs"):
            for path in walk_xml(d):
                root = parse_xml(path)
                if root is None or root.tag != "Defs":
                    continue
                rel = os.path.relpath(path, m["folder"])
                for node in root:
                    dn = txt(node, "defName")

                    if node.tag == "ThingDef" and node.find("race") is not None:
                        key = dn or f"<abstract:{node.get('Name','')}>"
                        r = {
                            "defName": dn, "abstractName": node.get("Name", ""),
                            "parentName": node.get("ParentName", ""),
                            "label": txt(node, "label"),
                            "description": re.sub(r"\s+", " ", txt(node, "description"))[:400],
                            "modName": m["name"], "packageId": m["packageId"],
                            "workshopId": m["workshopId"], "loadOrder": m["order"],
                            "sourceFile": rel, "shortHashCandidate": short_hash(dn),
                            "tickerType": txt(node, "tickerType"),
                            "tradeability": txt(node, "tradeability"),
                            "tradeTags": ";".join(
                                x.text.strip() for x in node.findall("tradeTags/li") if x.text),
                            "modExtensions": ";".join(
                                (x.get("Class", "") or "").split(".")[-1]
                                for x in node.findall("modExtensions/li"))[:150],
                        }
                        for col, xp in RACE_SIMPLE:
                            r[col] = txt(node, xp)

                        for sb in node.findall("statBases/*"):
                            col = STAT_MAP.get(sb.tag)
                            if col:
                                r[col] = (sb.text or "").strip()

                        wb = node.find("race/wildBiomes")
                        r["wildBiomes"] = ";".join(
                            f"{c.tag}={(c.text or '').strip()}" for c in wb) if wb is not None else ""

                        r["trainableTags"] = ";".join(
                            x.text.strip() for x in node.findall("race/trainableTags/li") if x.text)
                        r["untrainableTags"] = ";".join(
                            x.text.strip() for x in node.findall("race/untrainableTags/li") if x.text)

                        tools, agg = parse_tools(node)
                        r.update(agg)
                        for t in tools:
                            attacks.append(dict(t, defName=dn, modName=m["name"]))

                        r.update(parse_comps(node))
                        r["litterSizeMin"], r["litterSizeMax"] = parse_litter(node)
                        ls, n_ls, adult = parse_lifestages(node)
                        r["lifeStageCount"], r["ageAdultYears"] = n_ls, adult
                        for x in ls:
                            lifestages.append(dict(x, defName=dn, modName=m["name"]))

                        # ---- derived: reproduction pressure -----------------
                        gest = fnum(r.get("gestationPeriodDays"))
                        lmax = fnum(r.get("litterSizeMax")) or 1.0
                        if gest and gest > 0:
                            lpy = 365.0 / gest
                            r["maxLittersPerYear"] = round(lpy, 2)
                            r["annualOffspringMax"] = round(lpy * lmax, 1)
                            r["FAST_BREEDER"] = ("YES" if lpy * lmax >= FAST_BREEDER_ANNUAL else "")
                        else:
                            r["maxLittersPerYear"] = r["annualOffspringMax"] = r["FAST_BREEDER"] = ""

                        # ---- derived: renewable yield (ranch guardrail) -----
                        yields = []
                        if r["milkDef"]:
                            yields.append(f"milk/{r['milkIntervalDays']}d")
                        if r["woolDef"]:
                            yields.append(f"wool/{r['shearIntervalDays']}d")
                        if r["eggUnfertilizedDef"] or r["eggFertilizedDef"]:
                            yields.append(f"egg/{r['eggLayIntervalDays']}d")
                        r["RENEWABLE_YIELD"] = ";".join(yields)

                        # ---- derived: temperature tolerance ------------------
                        # Effective survivable range = comfy range widened by any
                        # insulation stat the def declares. Load-bearing for the
                        # desert world: who actually survives extreme heat.
                        tmin, tmax = fnum(r.get("comfyTempMin")), fnum(r.get("comfyTempMax"))
                        icold, iheat = fnum(r.get("insulationCold")), fnum(r.get("insulationHeat"))
                        emin = (tmin - icold) if (tmin is not None and icold is not None) else tmin
                        emax = (tmax + iheat) if (tmax is not None and iheat is not None) else tmax
                        r["effectiveTempMin"] = round(emin, 1) if emin is not None else ""
                        r["effectiveTempMax"] = round(emax, 1) if emax is not None else ""
                        r["tempRangeC"] = (f"{emin:g}..{emax:g}"
                                           if emin is not None and emax is not None else "")
                        r["tempSpan"] = (round(emax - emin, 1)
                                         if emin is not None and emax is not None else "")
                        r["HEAT_HARDY"] = ("YES" if emax is not None and emax >= 50 else "")
                        r["COLD_HARDY"] = ("YES" if emin is not None and emin <= -40 else "")

                        if dn:
                            dupnames[("ThingDef", dn)].append(m["name"])
                        animals[key] = r

                    elif node.tag == "PawnKindDef":
                        pawnkinds[txt(node, "race")].append({
                            "defName": dn, "combatPower": txt(node, "combatPower"),
                            "ecoSystemWeight": txt(node, "ecoSystemWeight"),
                            "wildGroupSizeMin": txt(node, "wildGroupSize/min"),
                            "wildGroupSizeMax": txt(node, "wildGroupSize/max"),
                            "canArriveManhunter": txt(node, "canArriveManhunter"),
                            "shortHashCandidate": short_hash(dn), "mod": m["name"],
                        })
                        if dn:
                            dupnames[("PawnKindDef", dn)].append(m["name"])

                    elif node.tag == "BiomeDef" and dn:
                        biomes[dn] = {
                            "mod": m["name"], "packageId": m["packageId"], "file": rel,
                            "label": txt(node, "label"),
                            "wildAnimals": [(rec.tag, (rec.text or "").strip())
                                            for rec in node.findall("wildAnimals/*")],
                        }
                        dupnames[("BiomeDef", dn)].append(m["name"])
    return animals, pawnkinds, biomes, attacks, lifestages, dupnames


PATCH_KEYS = ("wildAnimals", "wildBiomes", "PawnKindDef", "race/", "BiomeDef",
              "tools/", "statBases", "comps/")


def scan_patches(mods):
    rows = []
    for m in mods:
        for d in def_dirs(m, "Patches"):
            for path in walk_xml(d):
                try:
                    raw = open(path, encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                for xp in re.findall(r"<xpath>(.*?)</xpath>", raw, re.S):
                    xp = re.sub(r"\s+", " ", xp).strip()
                    if any(k in xp for k in PATCH_KEYS):
                        rows.append({"mod": m["name"], "packageId": m["packageId"],
                                     "file": os.path.relpath(path, m["folder"]),
                                     "xpath": xp[:400]})
    return rows


# ---------------------------------------------------------------- output
COLUMNS = (
    ["defName", "label", "modName", "packageId", "workshopId", "loadOrder", "sourceFile",
     "shortHashCandidate", "abstractName", "parentName", "duplicateDefName"]
    + ["wildness", "trainability", "petness", "intelligence", "nameOnTameChance",
       "nameOnNuzzleChance", "nuzzleMtbHours", "roamMtbDays", "playerCanChangeMaster",
       "trainableTags", "untrainableTags"]
    + ["predator", "maxPreyBodySize", "manhunterOnDamageChance", "manhunterOnTameFailChance",
       "canArriveManhunter", "combatPower", "attackCount", "attackBestPower",
       "attackBestDPS", "attackSummary", "armorSharp", "armorBlunt", "armorHeat",
       "moveSpeed", "deathActionWorker", "explosiveRadius"]
    + ["baseBodySize", "baseHealthScale", "baseHungerRate", "foodType", "lifeExpectancy",
       "fleshType", "bloodDef", "body", "mass", "carryingCapacity",
       "comfyTempMin", "comfyTempMax", "insulationCold", "insulationHeat",
       "effectiveTempMin", "effectiveTempMax", "tempRangeC", "tempSpan",
       "HEAT_HARDY", "COLD_HARDY", "toxicResistance", "toxicEnvResistance", "psychicSensitivity",
       "minimumHandlingSkill", "animalsLearningFactor", "filthRate", "needsRest", "doesntMove"]
    + ["hasGenders", "gestationPeriodDays", "litterSizeMin", "litterSizeMax", "mateMtbHours",
       "lifeStageCount", "ageAdultYears", "maxLittersPerYear", "annualOffspringMax",
       "FAST_BREEDER"]
    + ["leatherDef", "leatherAmount", "meatAmount", "meatLabel", "useMeatFrom",
       "milkDef", "milkIntervalDays", "milkAmount", "woolDef", "shearIntervalDays",
       "woolAmount", "eggFertilizedDef", "eggUnfertilizedDef", "eggLayIntervalDays",
       "eggCountRange", "RENEWABLE_YIELD"]
    + ["wildBiomes", "biomeCount", "herdAnimal", "packAnimal", "wildGroupSizeMin",
       "wildGroupSizeMax", "ecoSystemWeight", "canBecomeShambler"]
    + ["tickerType", "compCount", "comps", "modExtensions", "thinkTreeMain", "nameGenerator"]
    + ["tradeTags", "tradeability", "marketValue", "pawnKinds", "pawnKindHashes", "description"]
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--workshop", default=D_WORKSHOP)
    ap.add_argument("--local", default=D_LOCAL)
    ap.add_argument("--data", default=D_DATA)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    mods, missing = load_active_mods(a.config, a.workshop, a.local, a.data)
    print(f"active mods resolved: {len(mods)}   unresolved packageIds: {len(missing)}")
    for x in missing[:10]:
        print("   ! no folder for:", x)

    animals, pawnkinds, biomes, attacks, lifestages, dupnames = scan_defs(mods)
    patches = scan_patches(mods)
    print(f"animals: {len(animals)}   biomes: {len(biomes)}   "
          f"attacks: {len(attacks)}   animal/biome patches: {len(patches)}")

    # bidirectional biome x animal
    pairs = defaultdict(list)
    for bdn, b in biomes.items():
        for adn, com in b["wildAnimals"]:
            pairs[(bdn, adn)].append({"direction": "biome.wildAnimals", "commonality": com,
                                      "mod": b["mod"], "file": b["file"]})
    for r in animals.values():
        if not r.get("wildBiomes"):
            continue
        for chunk in r["wildBiomes"].split(";"):
            if "=" in chunk:
                bdn, com = chunk.split("=", 1)
                pairs[(bdn, r["defName"])].append(
                    {"direction": "animal.wildBiomes", "commonality": com,
                     "mod": r["modName"], "file": r["sourceFile"]})

    biome_count = defaultdict(int)
    for (bdn, adn) in pairs:
        biome_count[adn] += 1

    def w_csv(name, cols, rows):
        with open(os.path.join(a.out, name), "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            wr.writeheader()
            wr.writerows(rows)

    out_rows = []
    for key, r in sorted(animals.items(), key=lambda x: (x[1]["modName"], x[0])):
        pks = pawnkinds.get(r["defName"], [])
        r["pawnKinds"] = ";".join(p["defName"] for p in pks)
        r["pawnKindHashes"] = ";".join(str(p["shortHashCandidate"]) for p in pks)
        r["combatPower"] = ";".join(p["combatPower"] for p in pks if p["combatPower"])
        r["ecoSystemWeight"] = ";".join(p["ecoSystemWeight"] for p in pks if p["ecoSystemWeight"])
        r["wildGroupSizeMin"] = ";".join(p["wildGroupSizeMin"] for p in pks if p["wildGroupSizeMin"])
        r["wildGroupSizeMax"] = ";".join(p["wildGroupSizeMax"] for p in pks if p["wildGroupSizeMax"])
        r["canArriveManhunter"] = ";".join(p["canArriveManhunter"] for p in pks if p["canArriveManhunter"])
        r["biomeCount"] = biome_count.get(r["defName"], 0)
        owners = set(dupnames.get(("ThingDef", r["defName"]), []))
        r["duplicateDefName"] = " | ".join(sorted(owners)) if len(owners) > 1 else ""
        out_rows.append(r)

    w_csv("animals.csv", COLUMNS, out_rows)
    w_csv("animal_attacks.csv",
          ["defName", "modName", "label", "capacities", "power", "cooldownTime", "dps",
           "armorPenetration", "linkedBodyPartsGroup", "chanceFactor"], attacks)
    w_csv("animal_lifestages.csv",
          ["defName", "modName", "index", "def", "minAge", "soundWounded"], lifestages)
    w_csv("patch_watch.csv", ["mod", "packageId", "file", "xpath"], patches)

    with open(os.path.join(a.out, "biome_animals.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["biome", "animal", "sources", "direction", "commonality", "mod", "file"])
        for (bdn, adn), srcs in sorted(pairs.items()):
            for s in srcs:
                wr.writerow([bdn, adn, len(srcs), s["direction"], s["commonality"], s["mod"], s["file"]])

    conflicts = {k: v for k, v in pairs.items() if len(v) > 1}
    with open(os.path.join(a.out, "conflicts.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["biome", "animal", "timesRegistered", "sources"])
        for (bdn, adn), srcs in sorted(conflicts.items()):
            wr.writerow([bdn, adn, len(srcs),
                         " || ".join(f"{s['mod']} [{s['direction']}] {s['file']}" for s in srcs)])

    fast = [r for r in out_rows if r.get("FAST_BREEDER") == "YES"]
    print(f"\nDUPLICATE (biome, animal) PAIRS: {len(conflicts)}   <- the CWAS crash class")
    for (bdn, adn), srcs in list(sorted(conflicts.items()))[:15]:
        print(f"   {bdn:26s} {adn:24s} x{len(srcs)}  " +
              " || ".join(f"{s['mod']}[{s['direction']}]" for s in srcs))
    print(f"\nFAST BREEDERS (>= {FAST_BREEDER_ANNUAL}/yr): {len(fast)}")
    for r in sorted(fast, key=lambda x: -(fnum(x['annualOffspringMax']) or 0))[:15]:
        print(f"   {r['defName']:26s} {r['annualOffspringMax']:>6}/yr  "
              f"gest={r['gestationPeriodDays']:>6}  {r['RENEWABLE_YIELD']:20s} {r['modName']}")
    heat = [r for r in out_rows if r.get("HEAT_HARDY") == "YES"]
    print(f"\nHEAT-HARDY animals (effective max >= 50C): {len(heat)}  <- desert-world candidates")
    for r in sorted(heat, key=lambda x: -(fnum(x["effectiveTempMax"]) or 0))[:15]:
        print(f"   {r['defName']:26s} {r['tempRangeC']:>16s}  {r['modName']}")
    print(f"\nwrote 6 CSVs to {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
