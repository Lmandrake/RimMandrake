#!/usr/bin/env python3
"""
animal_inventory.py — dump every animal in the modded game to CSV.

VERSION 1.5  (2026-08-10)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Docs/manifest: src/RimMandrake/Utils/README.md  ("animal_inventory.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

CHANGELOG
  1.5  LAYERED. This tool is now a PROJECTION over def_inventory.py (layer 1)
       and owns no scanning or inheritance machinery of its own. Deleted:
       load_active_mods(), the two-pass scan_defs() index, resolve_inherit(),
       _merge_into(), _overwrite(), _is_list_node(), INHERIT_MAX_DEPTH,
       _INHERIT_ATTRS, parse_xml(), walk_xml(), def_dirs() and the D_* path
       defaults — every one of those was a duplicate of layer 1, which was
       itself generalised out of this file's v1.4. What remains is the part
       that is actually about ANIMALS: which ThingDefs count as one, which
       fields become which columns, the derived columns, the PawnKind/Biome
       aggregation, and the CSVs.
       BEHAVIOUR-NEUTRAL by construction and by test: all six CSVs are
       byte-identical to v1.4's on the 562-mod stack (1,243 / 3,614 / 3,345 /
       4,618 / 3 / 1,897 rows). Nothing about the row set, the column set or
       any value changed. If you are looking for a semantic change, there
       isn't one — see 1.4 and 1.3 for the last two.
       One thing worth knowing: layer 1's Name index is GLOBAL across def
       types (RimWorld's XmlInheritance runs on the raw node graph before
       anything knows what a "ThingDef" is), whereas v1.4 indexed ThingDefs
       only. Measured on this stack: 2,575 global Names vs 1,269 ThingDef
       Names, ZERO cross-type Name collisions, and zero animals whose chain,
       depth or unresolvedParent changes. Layer 1 is the more correct rule and
       here it happens to be indistinguishable — but on a different mod set it
       could legitimately resolve a parent this tool used to give up on.
  1.4  dead xpaths. Four columns read fields RimWorld 1.6 no longer uses, so
       they reported near-0% coverage and were misread as "poor inheritance".
       Measured over 1,248 race-bearing ThingDefs in the resolved load set:
       wildness moved to a StatDef (race/wildness 1 def -> statBases/Wildness
       1054); deathActionWorker became a Class ATTRIBUTE on <race><deathAction>
       (race/deathActionWorkerClass 0 defs); nameOnNuzzleChance no longer
       exists anywhere (column removed); Insulation_Cold/Heat are apparel-only
       stats that no animal carries, so effectiveTemp* == comfyTemp* always.
       See the DEAD XPATHS note above STAT_MAP. This is independent of 1.3:
       inheritance was never the reason these were empty.
  1.3  <ParentName> inheritance is now actually RESOLVED. v1.2 recorded
       parentName/abstractName as columns and then read every field off the
       def's OWN element, so the majority of animals reported blank for fields
       their abstract base supplies -- wildness 48%, comfyTempMax 44%,
       nuzzleMtbHours 33%. The scan is now two-pass: pass A indexes every
       ThingDef that carries a Name attribute (including abstract bases with no
       <race>, e.g. BasePawn) plus every ThingDef with a <race>; pass B walks
       each animal's ParentName chain and merges with RimWorld's own
       XmlInheritance semantics. Derived columns (FAST_BREEDER,
       RENEWABLE_YIELD, effectiveTemp*, tempRangeC/Span, HEAT/COLD_HARDY,
       maxLittersPerYear, annualOffspringMax) are computed AFTER the merge --
       computing them before it was the other half of the v1.2 bug. New
       columns: inheritDepth, inheritChain, inheritedFields, unresolvedParent.
       (The scan and the resolver described here are now layer 1's; see 1.5.)
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

WHERE THE WORK HAPPENS (the three layers)
=========================================
  layer 1  def_inventory.py    load set -> every def node, <ParentName> resolved
  layer 2  THIS FILE           "what is an animal, and what do I want to know"
  layer 3  (offline vs live diff — separate tool)

Layer 1 owns everything category-agnostic: resolving which folders the game
actually loads, parsing all 8,294 def files exactly once, and merging each def
with its whole ParentName ancestry. It hands back DefRecords; the only two
things this file asks of one are `.own` (the raw declared element) and
`.element` (the inheritance-RESOLVED element).

That split is not cosmetic. `.element` is the only convenient way to read a
field, so a new column CANNOT accidentally be read pre-inheritance — which is
exactly the bug v1.3 had to fix here. `.own` still exists, and this file uses
it in precisely two places, both deliberate and both commented below: deciding
what counts as an animal, and computing inheritedFields.

MAINTENANCE — adding a column
  1. simple <race> field -> append to RACE_SIMPLE as (csvColumn, "race/xpath")
  2. statBases entry     -> add to STAT_MAP as "StatDefName": "csvColumn"
  3. comp-derived        -> extend parse_comps()
  4. derived/computed    -> compute in extract_thing() after the comp block, so
     the value is derived from the INHERITANCE-RESOLVED element, not the raw def
  5. ALWAYS add the name to COLUMNS. DictWriter uses extrasaction="ignore", so a
     column missing from COLUMNS is silently dropped. This is the one easy mistake.

  You do NOT have to think about inheritance. extract_thing() is handed
  DefRecord.element, which is already merged — layer 1's job, done before this
  file sees anything. Anything extract_thing() returns is then automatically
  eligible for the inheritedFields diff, which is computed by running it twice,
  once on `.own` and once on `.element`. Two rules follow from that:
    * do not read fields outside extract_thing(), or they escape both the
      inheritance guarantee and the inheritedFields diff;
    * do not reach for `.own` for a column value. It is the pre-merge node and
      is blank for the majority of animals on most fields.

  Columns sourced from a DIFFERENT def type (combatPower, ecoSystemWeight,
  wildGroupSize*, canArriveManhunter from PawnKindDef; biomeCount from the
  biome map) are joined in main(), not extract_thing(), and are therefore
  outside the inheritedFields diff. That is correct — they are not this def's
  fields — but it does mean PawnKindDef inheritance is still unresolved here
  (see STILL APPROXIMATE below).

PERFORMANCE: run natively on Windows. Through the Cowork device bridge the mount
does ~210 files/sec and this touches tens of thousands of XML files (>10 min).
Natively it is ~3-4s. Layer 1's inheritance merge is LAZY, so asking it for all
def types and then touching only the ~1,250 animals costs the scan plus 1,250
merges, not 51,000. Do not "optimise" that by narrowing layer 1's Name index —
it must stay global or parents stop resolving.

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
    Mitigation: scan_patches() scans Patches/ and reports every operation whose
    xpath touches an animal/biome, so you at least know where to look.
  * Mod-vs-mod override winners for identical defNames (flagged, not resolved).
  * True shortHashes. Computed with RimWorld's StableStringHash, but the game
    resolves collisions across the whole loaded set per defType, so treat the
    value as a CANDIDATE until cross-checked against a live dump.

<ParentName> INHERITANCE — resolved by layer 1, and what is still approximate
----------------------------------------------------------------------------
RESOLVED (since 1.3; owned by def_inventory.py since 1.5). Every def that
carries a Name attribute in the whole load set is indexed, cross-mod, including
abstract bases that carry no <race> at all (BasePawn). Each animal's ParentName
chain is walked to the root and merged with RimWorld's XmlInheritance rules: the
child's own value always wins, named-child nodes (race, statBases, wildBiomes)
merge per name, and <li> list nodes (tools, comps, lifeStageAges, tradeTags,
litterSizeCurve/points) are REPLACED wholesale by any child that declares them.
Inherit="False" forces replacement. Cycles and runaway chains are capped; a
ParentName with no matching Name lands in the unresolvedParent column instead of
vanishing. The merge semantics live in def_inventory.py — read them there.

STILL APPROXIMATE:
  * Duplicate abstract Names across mods. Last in load order wins here. The
    game logs an error and its winner is not guaranteed to be the same one.
  * MayRequire / MayRequireAnyOf on inherited <li> nodes is NOT evaluated, so
    an inherited comps/recipes list can include entries a real load would drop.
    Animals inherit the Anomaly-gated comps on AnimalThingBase whether or not
    Anomaly is active.
  * PawnKindDef inheritance is not resolved, so the pawnkind-sourced columns
    (combatPower, ecoSystemWeight, wildGroupSizeMin/Max, canArriveManhunter)
    still read the def's own XML only. Layer 1 could resolve them — this is a
    deliberate hold, because changing it changes column values and 1.5 is a
    behaviour-neutral refactor. Do it as its own versioned change.
  * Which ThingDefs count as animals is still decided on the def's OWN <race>
    element, before merging. A def that inherits <race> and declares none is
    not listed. Deliberate: it keeps the row set identical to v1.2's.
  * Patches still run after inheritance in the real game; see above.

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
  inheritance   inheritDepth inheritChain inheritedFields unresolvedParent
  temperament   wildness trainability petness intelligence nameOnTameChance
                nuzzleMtbHours roamMtbDays playerCanChangeMaster
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
from collections import defaultdict

# Layer 1. Everything to do with WHICH files the game loads, parsing them, and
# resolving <ParentName> lives there and nowhere else — this file used to carry
# its own copy of all three and that copy is gone. The D_* path defaults come
# from there too so the two tools cannot drift apart on which machine they mean.
#
# rimworld_loadset is imported directly for def_dirs() only, which scan_patches()
# needs to find each mod's Patches/ folders; layer 1 has no opinion about
# patches (it deliberately reads base XML only).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from def_inventory import (build, walk_xml,                      # noqa: E402
                           D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA)
from rimworld_loadset import def_dirs                            # noqa: E402

# The def types this projection needs a record for. Passed to layer 1 purely to
# avoid allocating ~50k DefRecords we would never look at: it does NOT narrow
# the parse (every file is still read, because a parent can live in any file)
# and it does NOT narrow the global Name index that inheritance resolves
# against. Narrowing either of those would silently break resolution.
WANT_TYPES = ("ThingDef", "PawnKindDef", "BiomeDef")

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


# ---------------------------------------------------------------- extraction
RACE_SIMPLE = [
    # (csv column, xpath under the ThingDef)
    # NOTE: wildness is NOT here. In 1.6 it is a StatDef, not a race field —
    # see the DEAD XPATHS note under STAT_MAP.
    ("trainability", "race/trainability"),
    ("petness", "race/petness"), ("intelligence", "race/intelligence"),
    ("nameOnTameChance", "race/nameOnTameChance"),
    ("nuzzleMtbHours", "race/nuzzleMtbHours"), ("roamMtbDays", "race/roamMtbDays"),
    ("playerCanChangeMaster", "race/playerCanChangeMaster"),
    ("predator", "race/predator"), ("maxPreyBodySize", "race/maxPreyBodySize"),
    ("manhunterOnDamageChance", "race/manhunterOnDamageChance"),
    ("manhunterOnTameFailChance", "race/manhunterOnTameFailChance"),
    # deathActionWorker is not here either: 1.6 stores it as a Class ATTRIBUTE
    # on <race><deathAction>, and txt() reads element text. Handled explicitly
    # in extract_thing().
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

# DEAD XPATHS — measured against the resolved load set, 1,248 ThingDefs with
# <race>, 2026-08-10. These are the traps that made columns look "poorly
# covered" when in fact the tool was reading a field the game no longer uses:
#
#   race/wildness               1 def   (0.1%)   -> statBases/Wildness  1054 (84.5%)
#   race/deathActionWorkerClass 0 defs  (0.0%)   -> race/deathAction Class= 77 (6.2%)
#   race/nameOnNuzzleChance     0 defs  (0.0%)   -> gone in 1.6; column removed
#   statBases/Insulation_Cold   0 defs  (0.0%)   -> apparel-only stat
#   statBases/Insulation_Heat   0 defs  (0.0%)   -> apparel-only stat
#
# Consequence of the last two: no animal carries an insulation stat, so
# effectiveTempMin/Max are always exactly comfyTempMin/Max. The derivation is
# kept because it is correct and would pick up a modded insulation stat if one
# ever appeared, but do not read it as "insulation has been accounted for".
#
# The lesson generalises: a 0% column is far more likely to be a dead xpath
# than a genuinely empty field. Check before believing a coverage number.
STAT_MAP = {
    "Wildness": "wildness",
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


def extract_thing(node, meta):
    """
    Every field this tool reads out of ONE ThingDef element, plus the derived
    columns. Returns (row, tools, lifeStages).

    Called twice per animal: once on the def's own XML — used only to work out
    which columns it declares itself, for inheritedFields — and once on the
    inheritance-resolved XML, which is what is written. Keeping derivation in
    here is the point: v1.2 derived FAST_BREEDER, RENEWABLE_YIELD and the
    temperature group from unresolved values, so they were blank for any animal
    whose gestation or comfy temps came from its base.

    This function is xpath-against-an-element and nothing else. It does not know
    where the element came from and must not: layer 1 has already merged it.
    """
    r = dict(meta)
    r["label"] = txt(node, "label")
    r["description"] = re.sub(r"\s+", " ", txt(node, "description"))[:400]
    r["tickerType"] = txt(node, "tickerType")
    r["tradeability"] = txt(node, "tradeability")
    r["tradeTags"] = ";".join(
        x.text.strip() for x in node.findall("tradeTags/li") if x.text)
    r["modExtensions"] = ";".join(
        (x.get("Class", "") or "").split(".")[-1]
        for x in node.findall("modExtensions/li"))[:150]

    for col, xp in RACE_SIMPLE:
        r[col] = txt(node, xp)

    # deathAction has TWO shapes in the wild, and the common one is not the
    # obvious one. Measured over the resolved load set: 63 defs use a
    # <workerClass> CHILD (<deathAction><workerClass>DeathActionWorker_
    # BigExplosion</workerClass></deathAction>, e.g. Boomalope) and 14 use a
    # Class ATTRIBUTE (<deathAction Class="DeathActionProperties_Divide">).
    # Reading only the attribute silently loses the Boomalope class of animal —
    # exactly the explosive ones we most want flagged.
    da = node.find("race/deathAction")
    death = ""
    if da is not None:
        death = da.get("Class", "") or txt(da, "workerClass")
    r["deathActionWorker"] = death.split(".")[-1] if death else ""

    for col in STAT_MAP.values():               # so the own/resolved diff is fair
        r.setdefault(col, "")
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

    r.update(parse_comps(node))
    r["litterSizeMin"], r["litterSizeMax"] = parse_litter(node)
    ls, n_ls, adult = parse_lifestages(node)
    r["lifeStageCount"], r["ageAdultYears"] = n_ls, adult

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
    # Effective survivable range = comfy range widened by any insulation stat
    # the def declares OR INHERITS. Load-bearing for the desert world: who
    # actually survives extreme heat.
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
    return r, tools, ls


# ---------------------------------------------------------------- projection
def project(ds):
    """
    Turn layer 1's DefSet into the animal-shaped data this tool writes.

    There is no scanning and no inheritance work in here any more — by the time
    this runs, every file has been parsed and every ParentName chain walked.
    What is left is three harvests over the DefSet, in scan (= load) order:

      PawnKindDef  -> per-race aggregation (combatPower, group sizes, ...)
      BiomeDef     -> wildAnimals lists, one entry per biome, last mod wins
      ThingDef     -> the animals themselves

    `.own` vs `.element` — the two places `.own` is used are both load-bearing:

      * SELECTION. An animal is a ThingDef whose OWN element declares <race>.
        Not the resolved one: every child of AnimalThingBase inherits a <race>,
        so selecting on the merged element would drag in vehicles, mechs and
        anything else hanging off a pawn base. This is also what keeps the row
        set identical to v1.2's.
      * inheritedFields. Computed by extracting twice, from `.own` and from
        `.element`, and diffing. That is the honest definition of "this column's
        value did not come from this def", and it is only possible because
        layer 1 keeps both elements addressable.

    PawnKindDef and BiomeDef are read from `.own` for a duller reason: v1.4 read
    them unmerged and 1.5 is behaviour-neutral. See STILL APPROXIMATE up top —
    switching them to `.element` is a real (and probably good) change, not a
    refactor, so it does not belong in this version.
    """
    pawnkinds, biomes = defaultdict(list), {}

    for rec in ds.of_type("PawnKindDef"):
        node = rec.own
        pawnkinds[txt(node, "race")].append({
            "defName": rec.defName, "combatPower": txt(node, "combatPower"),
            "ecoSystemWeight": txt(node, "ecoSystemWeight"),
            "wildGroupSizeMin": txt(node, "wildGroupSize/min"),
            "wildGroupSizeMax": txt(node, "wildGroupSize/max"),
            "canArriveManhunter": txt(node, "canArriveManhunter"),
            "shortHashCandidate": short_hash(rec.defName), "mod": rec.modName,
        })

    for rec in ds.of_type("BiomeDef"):
        if not rec.defName:
            continue
        biomes[rec.defName] = {                  # last mod in load order wins
            "mod": rec.modName, "packageId": rec.packageId, "file": rec.sourceFile,
            "label": txt(rec.own, "label"),
            "wildAnimals": [(w.tag, (w.text or "").strip())
                            for w in rec.own.findall("wildAnimals/*")],
        }

    animals, attacks, lifestages = {}, [], []
    # Which mods declared each animal defName. Only race-bearing ThingDefs are
    # counted, so this is narrower than layer 1's ds.duplicates() (which sees
    # every ThingDef) — and it has to be, or a non-animal ThingDef sharing a
    # defName would light up duplicateDefName for an animal it has nothing to
    # do with. Recorded, not adjudicated: last in load order wins the row.
    owners = defaultdict(list)

    for rec in ds.of_type("ThingDef"):
        if rec.own.find("race") is None:         # SELECTION — see docstring
            continue
        dn = rec.defName
        # defName, Name and ParentName are read off the def's OWN element on
        # purpose. Taking them post-merge would hand an abstract-only def its
        # parent's defName and make abstract rows indistinguishable.
        meta = {
            "defName": dn, "abstractName": rec.own.get("Name", ""),
            "parentName": rec.own.get("ParentName", ""),
            "modName": rec.modName, "packageId": rec.packageId,
            "workshopId": rec.workshopId, "loadOrder": rec.loadOrder,
            "sourceFile": rec.sourceFile, "shortHashCandidate": short_hash(dn),
        }
        resolved = rec.element                   # layer 1 merges here, lazily
        r, tools, ls = extract_thing(resolved, meta)

        # A def with no parent gets its own element back unchanged, so there is
        # nothing to diff and no second extraction to pay for.
        if resolved is rec.own:
            inherited = []
        else:
            own, _, _ = extract_thing(rec.own, meta)
            inherited = [k for k in sorted(r) if str(r[k]) != str(own.get(k, ""))]
        r["inheritDepth"] = rec.inheritDepth
        r["inheritChain"] = " > ".join(rec.inheritChain)
        r["inheritedFields"] = ";".join(inherited)[:600]
        r["unresolvedParent"] = rec.unresolvedParent
        rec.release()                            # do not hold 1,250 merged trees

        for t in tools:
            attacks.append(dict(t, defName=dn, modName=rec.modName))
        for x in ls:
            lifestages.append(dict(x, defName=dn, modName=rec.modName))
        if dn:
            owners[dn].append(rec.modName)
        animals[dn or f"<abstract:{rec.own.get('Name','')}>"] = r

    return animals, pawnkinds, biomes, attacks, lifestages, owners


PATCH_KEYS = ("wildAnimals", "wildBiomes", "PawnKindDef", "race/", "BiomeDef",
              "tools/", "statBases", "comps/")


def scan_patches(mods):
    """
    Every PatchOperation xpath that touches an animal or a biome.

    Deliberately a raw TEXT scan, not an XML one, and deliberately outside layer
    1: layer 1 reads Defs/ and states plainly that patches have not run. This is
    the mitigation for that blind spot — it does not tell you what a patch does,
    only that one is aimed at something you care about.
    """
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
    + ["inheritDepth", "inheritChain", "inheritedFields", "unresolvedParent"]
    + ["wildness", "trainability", "petness", "intelligence", "nameOnTameChance",
       "nuzzleMtbHours", "roamMtbDays", "playerCanChangeMaster",
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

    # One call does the load-set resolution AND the whole scan. quiet=True
    # because layer 1's own banner says the same things in a different shape and
    # these two lines are what the README documents.
    ds = build(a.config, a.workshop, a.local, a.data, types=WANT_TYPES, quiet=True)
    mods, missing = ds.mods, ds.missing
    ndirs = sum(len(m["contentDirs"]) for m in mods)
    print(f"load set: version {ds.gameVersion}, {len(mods)} active mods "
          f"-> {ndirs} content folders")
    print(f"active mods resolved: {len(mods)}   unresolved packageIds: {len(missing)}")
    for x in missing[:10]:
        print("   ! no folder for:", x)

    animals, pawnkinds, biomes, attacks, lifestages, owners = project(ds)
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
        mods_owning = set(owners.get(r["defName"], []))
        r["duplicateDefName"] = " | ".join(sorted(mods_owning)) if len(mods_owning) > 1 else ""
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
