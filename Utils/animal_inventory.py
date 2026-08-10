#!/usr/bin/env python3
"""
animal_inventory.py — dump every animal in the modded game to CSV.

VERSION 1.4  (2026-08-10)   Project: G:/My Drive/Personal/Rimworld/Utils/
Docs/manifest: Utils/README.md  ("animal_inventory.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

CHANGELOG
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
  4. derived/computed    -> compute in extract_thing() after the comp block, so
     the value is derived from the INHERITANCE-RESOLVED element, not the raw def
  5. ALWAYS add the name to COLUMNS. DictWriter uses extrasaction="ignore", so a
     column missing from COLUMNS is silently dropped. This is the one easy mistake.

  Anything extract_thing() returns is automatically eligible for the
  inheritedFields diff — it is computed by running extract_thing() twice, once
  on the def's own element and once on the resolved one. Do not read fields
  outside extract_thing() or they will silently escape inheritance.

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
  * Mod-vs-mod override winners for identical defNames (flagged, not resolved).
  * True shortHashes. Computed with RimWorld's StableStringHash, but the game
    resolves collisions across the whole loaded set per defType, so treat the
    value as a CANDIDATE until cross-checked against a live dump.

<ParentName> INHERITANCE — what v1.3 resolves, and what is still approximate
---------------------------------------------------------------------------
RESOLVED (new in 1.3). Every ThingDef with a Name attribute in the whole load
set is indexed, cross-mod, including abstract bases that carry no <race> at all
(BasePawn). Each animal's ParentName chain is walked to the root and merged with
RimWorld's XmlInheritance rules: the child's own value always wins, named-child
nodes (race, statBases, wildBiomes) merge per name, and <li> list nodes (tools,
comps, lifeStageAges, tradeTags, litterSizeCurve/points) are REPLACED wholesale
by any child that declares them. Inherit="False" forces replacement. Cycles and
runaway chains are capped at INHERIT_MAX_DEPTH; a ParentName with no matching
Name lands in the unresolvedParent column instead of vanishing.

STILL APPROXIMATE:
  * Duplicate abstract Names across mods. Last in load order wins here. The
    game logs an error and its winner is not guaranteed to be the same one.
  * MayRequire / MayRequireAnyOf on inherited <li> nodes is NOT evaluated, so
    an inherited comps/recipes list can include entries a real load would drop.
    This matters more in 1.3 than it did in 1.2: animals now inherit the
    Anomaly-gated comps on AnimalThingBase whether or not Anomaly is active.
  * PawnKindDef inheritance is not resolved, so the pawnkind-sourced columns
    (combatPower, ecoSystemWeight, wildGroupSizeMin/Max, canArriveManhunter)
    still read the def's own XML only.
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
import copy
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


# ---------------------------------------------------------------- inheritance
# <ThingDef ParentName="AnimalThingBase"> is not decoration: most animals get
# the bulk of their <race> block from an abstract base, frequently one owned by
# a DIFFERENT mod. RimWorld resolves this AFTER every mod's XML is loaded, so a
# parent may sit anywhere in load order relative to its children — which is why
# the scan is two-pass (index every Name, then resolve).
#
# Merge rule, mirroring XmlInheritance.RecursiveNodeCopyOverwriteElements:
#   * the CHILD's own value always wins; a parent value only fills a gap;
#   * a node whose children are <li> items — tools, comps, lifeStageAges,
#     tradeTags, litterSizeCurve/points — is REPLACED WHOLESALE by a child that
#     declares it. It is NOT merged element-wise. Getting this wrong invents
#     attacks and comps that the animal does not have;
#   * a node whose children are named elements — race, statBases, wildBiomes —
#     merges per child name, recursively;
#   * a leaf value node replaces its parent's outright;
#   * Inherit="False" forces wholesale replacement regardless.
INHERIT_MAX_DEPTH = 20

# Name/ParentName/Abstract describe a node's own place in the graph and must
# never be copied down from a parent (RimWorld strips them from the clone too).
_INHERIT_ATTRS = ("Name", "ParentName", "Abstract")


def _is_list_node(el):
    """True when this node's children are <li> items, i.e. a RimWorld List<>."""
    return any(ch.tag == "li" for ch in el)


def _overwrite(child, cur):
    """cur takes the child's content wholesale: text, children, attributes."""
    cur.text = child.text
    cur[:] = [copy.deepcopy(ch) for ch in child]
    cur.attrib.update(child.attrib)


def _merge_into(child, cur):
    """Lay one child node over the already-resolved parent node cur, in place."""
    if (child.get("Inherit") or "").strip().lower() == "false":
        _overwrite(child, cur)
        return
    # Either side being a text leaf, or either side being a <li> list, means the
    # child replaces the node outright. Everything else is an element container
    # and merges per child name — including a child that is EMPTY, which is a
    # no-op, not a wipe. (Clearing an inherited list needs Inherit="False";
    # that is the whole reason the attribute exists.)
    if ((child.text or "").strip() or (cur.text or "").strip()
            or _is_list_node(child) or _is_list_node(cur)):
        _overwrite(child, cur)
        return
    cur.attrib.update(child.attrib)
    for ce in child:
        match = cur.find(ce.tag)
        if match is None:
            cur.append(copy.deepcopy(ce))
        else:
            _merge_into(ce, match)


def resolve_inherit(node, by_name, cache):
    """
    Merge a def with its whole ParentName ancestry.

    Returns (resolved element, chain, unresolvedParent). The chain is listed
    nearest parent first. The resolved element is always a fresh copy unless the
    def has no parent at all, so the indexed nodes are never mutated.

    Two failure modes are reported rather than swallowed: a ParentName with no
    matching Name anywhere in the load set, and a cycle (or a chain longer than
    INHERIT_MAX_DEPTH) — both land in unresolvedParent.
    """
    chain, ancestors, visited, unresolved, base = [], [], set(), "", None
    n = node
    while len(chain) < INHERIT_MAX_DEPTH:
        pn = (n.get("ParentName") or "").strip()
        if not pn:
            break
        if pn in visited:                       # cycle
            unresolved = pn
            break
        visited.add(pn)
        p = by_name.get(pn)
        if p is None:                           # parent defined by no active mod
            unresolved = pn
            break
        chain.append(pn)
        if pn in cache:                         # rest of the chain already done
            base, cchain, cunres = cache[pn]
            chain.extend(cchain)
            unresolved = unresolved or cunres
            break
        ancestors.append(p)
        n = p
    else:
        unresolved = (n.get("ParentName") or "").strip()   # depth cap hit

    if base is None:
        if not ancestors:
            return node, chain, unresolved
        base = ancestors.pop()                  # topmost we managed to reach

    resolved = copy.deepcopy(base)
    for anc in reversed(ancestors):             # farthest first, nearest last
        for k in _INHERIT_ATTRS:
            resolved.attrib.pop(k, None)
        _merge_into(anc, resolved)
    for k in _INHERIT_ATTRS:
        resolved.attrib.pop(k, None)
    _merge_into(node, resolved)
    resolved.attrib.clear()
    resolved.attrib.update(node.attrib)

    name = (node.get("Name") or "").strip()
    # Cache the load-order winner only, and never a broken chain: a cycle
    # resolves differently depending on where you entered it.
    if name and not unresolved and by_name.get(name) is node:
        cache[name] = (resolved, chain, unresolved)
    return resolved, chain, unresolved


# ---------------------------------------------------------------- extraction
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


# ---------------------------------------------------------------- scan
def scan_defs(mods):
    """
    Two passes over the load set.

    PASS A indexes, in load order, every ThingDef that either carries a Name
    (a potential parent — abstract bases such as BasePawn have no <race> and
    would be lost by a race-only filter, yet they hold statBases every animal
    inherits) or carries a <race> (a potential animal). PawnKindDefs and
    BiomeDefs are harvested here too; they need no second look.

    PASS B resolves each animal's ParentName chain against that index and
    extracts its columns from the MERGED element.

    Two passes are not optional: a parent may be declared by a mod that loads
    after its children, and RimWorld resolves inheritance only once all XML is
    in. Duplicate Names follow the same rule this tool documents for defNames —
    last in load order wins.
    """
    pawnkinds, biomes = defaultdict(list), {}
    dupnames = defaultdict(list)
    by_name = {}          # Name attribute -> raw element (last mod in load order wins)
    candidates = []       # (element, mod, relpath) for every ThingDef with a <race>

    # ---- pass A: index -------------------------------------------------
    for m in mods:
        for d in def_dirs(m, "Defs"):
            for path in walk_xml(d):
                root = parse_xml(path)
                if root is None or root.tag != "Defs":
                    continue
                rel = os.path.relpath(path, m["folder"])
                for node in root:
                    dn = txt(node, "defName")

                    if node.tag == "ThingDef":
                        name = (node.get("Name") or "").strip()
                        if name:
                            by_name[name] = node
                        if node.find("race") is not None:
                            candidates.append((node, m, rel))

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

    # ---- pass B: resolve inheritance, then extract ----------------------
    animals, attacks, lifestages = {}, [], []
    cache = {}
    for node, m, rel in candidates:
        dn = txt(node, "defName")
        # defName, Name and ParentName are read off the def's OWN element on
        # purpose. Taking them post-merge would hand an abstract-only def its
        # parent's defName and make abstract rows indistinguishable.
        meta = {
            "defName": dn, "abstractName": node.get("Name", ""),
            "parentName": node.get("ParentName", ""),
            "modName": m["name"], "packageId": m["packageId"],
            "workshopId": m["workshopId"], "loadOrder": m["order"],
            "sourceFile": rel, "shortHashCandidate": short_hash(dn),
        }
        resolved, chain, unresolved = resolve_inherit(node, by_name, cache)
        r, tools, ls = extract_thing(resolved, meta)

        if resolved is node:
            inherited = []
        else:
            own, _, _ = extract_thing(node, meta)
            inherited = [k for k in sorted(r) if str(r[k]) != str(own.get(k, ""))]
        r["inheritDepth"] = len(chain)
        r["inheritChain"] = " > ".join(chain)
        r["inheritedFields"] = ";".join(inherited)[:600]
        r["unresolvedParent"] = unresolved

        for t in tools:
            attacks.append(dict(t, defName=dn, modName=m["name"]))
        for x in ls:
            lifestages.append(dict(x, defName=dn, modName=m["name"]))
        if dn:
            dupnames[("ThingDef", dn)].append(m["name"])
        animals[dn or f"<abstract:{node.get('Name','')}>"] = r

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
