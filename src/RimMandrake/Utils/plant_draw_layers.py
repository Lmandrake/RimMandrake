#!/usr/bin/env python3
"""plant_draw_layers.py -- census of every plant our biome rosters can spawn, with its
EFFECTIVE draw layer, size and a ground-cover classification.

VERSION 1.0 (2026-10-14). Item: ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS.
Owner, typed 2026-10-14: "Lower all such plants in all biomes. Small ground cover on the
appropriate layer."

WHY
===
A plant draws at its def's AltitudeLayer, and `Plant.Print` lifts a plant plane's top edge
by 0.1 altitude (`Printer_Plane.PrintPlane(..., topVerticesAltitudeBias 0.1f, ...)`) while
layers sit 0.0366 apart (Altitudes.AltInc). So a ground-cover plant is only GUARANTEED under
a LowPlant (11) plant when it sits at least 3 layers lower, i.e. <= Filth (8). Within one
layer the order between two plants is hash-random -- the "moss sometimes in front" report.
Nothing in the decompiled 1.6 source branches on a plant's altitudeLayer except drawing
(searched `altitudeLayer ==|<|>` and `AltitudeLayer.LowPlant`: no logic hits).

WHAT IT READS (no dump, no game)
================================
* the load set of `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (the owner's
  full list; the live ModsConfig is often a minimal list), via rimworld_loadset.py;
* every mandrake.* mod is read from THIS REPO, not the deployed copy, so undeployed commits
  count (the composed `mandrake.rm.biomes` is mapped member-by-member through its deployed
  LoadFolders.xml + `src/RimMandrake/Biomes.compose.json`);
* all ThingDef / BiomeDef XML, top-level `MayRequire`/`MayRequireAnyOf` honoured;
* every Patches/ operation in load order, applied with lxml (full XPath 1.0) to a document of
  the ThingDef + BiomeDef nodes. Classes it cannot run are COUNTED and the ones whose xpath
  mentions a field this census reads are LISTED -- never silently skipped;
* ParentName inheritance resolved per field (nearest declaration wins).

Roster = every `<wildPlants>` entry of a BiomeDef DEFINED by a mandrake.* package (owner read
from the defining package, never from the defName prefix), after patches, MayRequire-gated,
plus every plant whose own `plant/wildBiomes` names one of those biomes.

USAGE
    python3 src/RimMandrake/Utils/plant_draw_layers.py            # table to stdout (TSV)
    python3 src/RimMandrake/Utils/plant_draw_layers.py --json out.json
    python3 src/RimMandrake/Utils/plant_draw_layers.py --from-json out.json --md table.md
                                      # reclassify a saved census; write the markdown table
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys

from lxml import etree as LX

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import rimworld_loadset as LS  # noqa: E402

FULL_MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")
COMPOSE = os.path.join(REPO, "src", "RimMandrake", "Biomes.compose.json")
REPO_TIERS = [os.path.join(REPO, "src", t) for t in ("RimMandrake", "RimStarWars", "RimUtinni")]

# Verse.AltitudeLayer, read from decompiled 1.6 (Verse/AltitudeLayer.cs).
ALT = {n: i for i, n in enumerate([
    "BelowTerrain", "TerrainEdges", "Terrain", "TerrainScatter", "Floor", "Conduits",
    "FloorCoverings", "FloorEmplacement", "Filth", "Zone", "SmallWire", "LowPlant", "MoteLow",
    "Shadows", "DoorMoveable", "Building", "BuildingBelowTop", "BuildingOnTop", "Item",
    "ItemImportant", "LayingPawn", "PawnRope", "Projectile", "Pawn", "PawnUnused", "PawnState",
    "Blueprint", "MoteOverheadLow", "MoteOverhead", "Gas", "Skyfaller", "Weather",
    "LightingOverlay", "VisEffects", "FogOfWar", "Darkness", "WorldClipper", "Silhouettes",
    "MapDataOverlay", "MetaOverlays"])}
DEFAULT_ALT = "Item"            # BuildableDef.altitudeLayer = AltitudeLayer.Item
TARGET_ALT = "FloorEmplacement"  # 7: >= 3 layers under LowPlant (11)
MAX_SAFE = ALT["Filth"]          # 8: anything at or below is already guaranteed under LowPlant

FIELDS_WATCHED = ("altitudeLayer", "wildPlants", "wildBiomes", "visualSizeRange", "drawSize",
                  "maxMeshCount")

# ── classification ───────────────────────────────────────────────────────────────────────
# Written criteria (also printed into the design md). A plant is GROUND_COVER when ALL hold:
#   C1 not a tree (plant/treeCategory unset or None, no plant/harvestedThingDef that is wood);
#   C2 not sown (no plant/sowTags) -- crops are upright by design;
#   C3 mature footprint drawSize.x * visualSizeRange.max <= GC_MAX_CELLS;
#   C4 its NAME or LABEL or DESCRIPTION reads as low, spreading cover (GC_WORDS) and NOT as an
#      upright form (UPRIGHT_WORDS): caps, stalks, shrubs, flowers, reeds, cacti, trees.
# UPRIGHT when C1 or C2 fails, or C3 fails, or only UPRIGHT_WORDS hit.
# BORDERLINE when both word sets hit, or neither does, while C1-C3 hold -- listed for the
# owner, never changed. OVERRIDES (below) settle named plants by reading their description;
# each carries its reason.
GC_MAX_CELLS = 1.2
GC_WORDS = re.compile(
    r"\b(moss\w*|grass\w*|turf|lichen\w*|carpet\w*|mat|mats|matted|creep\w*|crust\w*|"
    r"clover|sedge\w*|ground ?cover|groundcover|sward|film|bloom of algae|algae|slime mold|"
    r"mycelium|mycelial|felt|fuzz|scurf|fur of|velvet|sprawl\w*|trailing|hugs the ground|"
    r"low[- ]growing|flat|spreading|carpeting)\b", re.I)
UPRIGHT_WORDS = re.compile(
    r"\b(mushroom\w*|toadstool\w*|cap|caps|capped|stalk\w*|stem\w*|shrub\w*|bush\w*|"
    r"tree\w*|trunk\w*|flower\w*|blossom\w*|bloom\w*|reed\w*|cact\w*|spire\w*|frond\w*|"
    r"tall|tower\w*|upright|stool|puffball\w*|bulb\w*|pod\w*|vine\w*|fern\w*|thorn\w*|"
    r"bramble\w*|stand\w*|spike\w*|plume\w*|column\w*|pillar\w*)\b", re.I)

_GC, _UP, _BL = "GROUND_COVER", "UPRIGHT", "BORDERLINE"
OVERRIDES: dict[str, tuple[str, str]] = {
    # defName: (class, reason). Settled by READING the description when the word rules could
    # not decide, or decided wrongly. One line of reason each. (2026-10-14)
    # -- named by the owner: the item asked about "sagecrust, dewshrooms, fruiting bodies"
    #    and he answered "Lower all such plants", so these three are ground cover by ruling.
    "RM_Dewshrooms": (_GC, "owner named it (tiny caps in clusters, 0.5 cell, 9 meshes)"),
    "RM_FruitingBodies": (_GC, "owner named it (mold pins carpeting the floor)"),
    "RM_Sagecrust": (_GC, "owner named it (crust on rock and mat)"),
    # -- read as low spreading cover
    "RM_Pillowmoss": (_GC, "desc: a fat, low cushion of moss"),
    "RM_Masonmat": (_GC, "desc: a mat spreading across the sediment"),
    "RM_Nemreth": (_GC, "desc: a low mat of hair-fine stalks"),
    "RM_Pallasheen": (_GC, "desc: one leaf pressed flat, never stands up"),
    "RM_UltrissPad": (_GC, "desc: a flat pad flush with the ground"),
    "RM_Wessaline": (_GC, "desc: a continuous skin over the salt pans"),
    "RM_Threllick": (_GC, "desc: a mat of surface roots, the ground itself"),
    "RM_LightPipeNub": (_GC, "desc: a glass knuckle flush with the sand, 0.2 cell"),
    "RM_TwistingThorngrass": (_GC, "grass with small thorns; grass habit"),
    # -- read as upright (the word rules saw both or neither)
    "RM_Seepril": (_UP, "desc: a barrel of a stem"),
    "RM_Dewblade": (_UP, "desc: shin-high tufts standing edge-on"),
    "RM_Kettlewick": (_UP, "desc: a single upright string"),
    "RM_Salvecomb": (_UP, "desc: one waist-high arched frond"),
    "RM_Boilbulb": (_UP, "desc: a bulb swollen into a dome"),
    "RM_FalseFruit": (_UP, "desc: shaped to match the mushroom caps it mimics"),
    "RM_YearningFruit": (_UP, "desc: a heavy-fruiting bush"),
    "RM_HoardVenomvine": (_UP, "desc: man-high knot of canes"),
    "RM_WalkingVenomvine": (_UP, "desc: man-high cane at the tail"),
    "RM_Mournweft": (_UP, "desc: a waist-high loom"),
    "RM_Vashpuk": (_UP, "desc: a squat waist-high bladder"),
    "RM_Plant_Bellows": (_UP, "desc: a knee-high sac"),
    "RM_Foamgorse": (_UP, "desc: a thicket straining upward"),
    "RM_Sevvuq": (_UP, "desc: skull-sized globes"),
    "RM_SpherePlant": (_UP, "desc: a helmet-sized sphere held clear on spines"),
    "RM_Kethevar": (_UP, "desc: a hand-high spiral coil"),
    "RM_Virr": (_UP, "desc: a hand-high branching tube"),
    "RM_Luqqim": (_UP, "desc: clusters of tulip cups"),
    "RM_Pusmelon": (_UP, "desc: a gourd-shaped fungus"),
    "RM_CubicSculpture": (_UP, "desc: a geometric solid block"),
    "RM_Hushcoral": (_UP, "desc: a coral"),
    "RM_Seepcandle": (_UP, "desc: a dripstone candle"),
    "RM_Brinecomb": (_UP, "desc: a row of standing teeth"),
    "RM_Dripfringe": (_UP, "desc: a curtain hanging from overhangs"),
    "RM_Sellith": (_UP, "desc: hanging fringes under the lines"),
    "RM_Neverset": (_UP, "desc: a small sprig"),
    "RM_KuvraSpout": (_UP, "desc: an upside-down cone"),
    "RM_Lanternstone_Sowable": (_UP, "a sown lanternstone, already on Building"),
    "RM_WildHealroot": (_UP, "healroot habit: an upright herb"),
    "RUT_WildHealroot": (_UP, "healroot habit: an upright herb"),
    "Plant_HubbaGourd_Wild": (_UP, "a gourd crop plant"),
    "RSW_Plant_HubbaGourd_Wild": (_UP, "a gourd crop plant"),
    "Plant_TookeTrap_Wild": (_UP, "a carnivorous flowering plant"),
    # -- stays borderline on purpose (listed for the owner)
    "AB_RedLeaves": (_BL, "'ocular plant' 1.2 cells; desc says grass, label says plant"),
    "RM_Claithe": (_BL, "flat rosette, but on a root-plate that lifts clear of the mud"),
    "RM_FE_Plant_EmberGrass": (_BL, "a grass, but desc: 'puts everything into height'"),
    "RM_Ghostpane": (_BL, "hand-wide panes joined at angles: flat or standing?"),
}


def _txt(e, path):
    n = e.find(path) if e is not None else None
    return (n.text or "").strip() if n is not None and n.text else None


# ── load set, with mandrake.* read from the repo ────────────────────────────────────────

def _repo_index():
    return LS.discover_mods(REPO_TIERS)


def _compose_sources():
    try:
        j = json.load(open(COMPOSE))
    except (OSError, ValueError):
        return {}, None
    return ({e["key"]: e["source"] for e in j.get("entries", [])},
            (j.get("shell") or {}).get("source"))


def load_set(modlist=FULL_MODLIST):
    from game_paths import WORKSHOP, LOCAL_MODS, GAME_DATA
    mods, missing, version = LS.build_load_set(modlist, [WORKSHOP, LOCAL_MODS, GAME_DATA])
    active = {m["packageId"] for m in mods}
    names = {m["name"] for m in mods}
    repo = _repo_index()
    comp, shell = _compose_sources()
    for m in mods:
        pid = m["packageId"]
        m["fromRepo"] = False
        if not pid.startswith("mandrake."):
            continue
        if pid == "mandrake.rm.biomes":
            dirs = []
            for cd in m["contentDirs"]:
                rel = os.path.relpath(cd, m["folder"]).replace("\\", "/")
                key = rel.rstrip("/").split("/")[-1]
                if rel in (".", ""):
                    src = shell
                else:
                    src = comp.get(key)
                if src and os.path.isdir(os.path.join(REPO, "src", "RimMandrake", src)):
                    dirs.append(os.path.join(REPO, "src", "RimMandrake", src))
                else:
                    dirs.append(cd)
            m["contentDirs"] = dirs
            m["fromRepo"] = True
        elif pid in repo:
            rf = repo[pid]["folder"]
            m["contentDirs"] = LS.resolve_load_folders(rf, version, active)
            m["folder"] = rf
            m["fromRepo"] = True
    return mods, missing, version, active, names


def _rel_files(mod, sub):
    """Shadowing as the engine does it: later LoadFolders roots win a relative path."""
    seen, out = set(), []
    for base in reversed(mod["contentDirs"]):
        d = os.path.join(base, sub)
        if not os.path.isdir(d):
            continue
        for dp, dns, fns in os.walk(d):
            dns.sort()
            for fn in sorted(fns):
                if not fn.lower().endswith(".xml"):
                    continue
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, d).lower()
                if rel in seen:
                    continue
                seen.add(rel)
                out.append(p)
    return out


def _parse(path):
    try:
        return LX.parse(path, LX.XMLParser(remove_comments=True, recover=True,
                                            remove_blank_text=True)).getroot()
    except (LX.XMLSyntaxError, OSError):
        return None


def _may_require_ok(e, active):
    mr = e.get("MayRequire")
    if mr and not all(p.strip().lower() in active for p in mr.split(",") if p.strip()):
        return False
    mra = e.get("MayRequireAnyOf")
    if mra and not any(p.strip().lower() in active for p in mra.split(",") if p.strip()):
        return False
    return True


KEEP_TAG = re.compile(r"(^|\.)(ThingDef|BiomeDef)$")


def build_doc(mods, active):
    root = LX.Element("Defs")
    nfiles = 0
    for m in mods:
        for p in _rel_files(m, "Defs"):
            r = _parse(p)
            nfiles += 1
            if r is None or r.tag != "Defs":
                continue
            for e in list(r):
                if not isinstance(e.tag, str) or not KEEP_TAG.search(e.tag):
                    continue
                if not _may_require_ok(e, active):
                    continue
                e.tag = "ThingDef" if e.tag.endswith("ThingDef") else "BiomeDef"
                e.set("_pkg", m["packageId"])
                e.set("_file", p)
                root.append(e)
    return root, nfiles


# ── a PatchOperation runner on lxml ─────────────────────────────────────────────────────

class Patcher:
    def __init__(self, root, active, names):
        self.root = root
        self.tree = LX.ElementTree(root)
        self.active = active
        self.names = names
        self.ops = 0
        self.unsupported = {}       # class -> count
        self.unsupported_watched = []  # (file, class, xpath) mentioning a watched field
        self.xpath_errors = 0
        self.touched = []           # (file, class, xpath) that changed a watched field

    def _sel(self, xp):
        try:
            r = self.tree.xpath(xp)
        except (LX.XPathError, LX.XPathEvalError, TypeError):
            self.xpath_errors += 1
            return []
        return [n for n in r if isinstance(n, LX._Element)] if isinstance(r, list) else []

    def run_file(self, path):
        r = _parse(path)
        if r is None:
            return
        ops = [r] if r.tag == "Operation" else [o for o in r if o.tag == "Operation"]
        for op in ops:
            self.apply(op, path)

    def _watch(self, op):
        s = LX.tostring(op, encoding="unicode")
        return any(f in s for f in FIELDS_WATCHED)

    def apply(self, op, path):
        cls = (op.get("Class") or "").split(".")[-1]
        succ = (_txt(op, "success") or "Normal")
        ok = self._apply(op, cls, path)
        if succ == "Always":
            return True
        if succ == "Never":
            return False
        if succ == "Invert":
            return not ok
        return ok

    def _apply(self, op, cls, path):
        self.ops += 1
        if cls == "PatchOperationSequence":
            for li in op.findall("operations/li"):
                if not self.apply(li, path):
                    return False
            return True
        if cls == "PatchOperationFindMod":
            mods = [(li.text or "").strip() for li in op.findall("mods/li")]
            hit = any(n in self.names for n in mods)
            br = op.find("match" if hit else "nomatch")
            return self.apply(br, path) if br is not None else hit
        if cls == "PatchOperationConditional":
            hit = bool(self._sel(_txt(op, "xpath") or ""))
            br = op.find("match" if hit else "nomatch")
            return self.apply(br, path) if br is not None else hit
        if cls == "PatchOperationTest":
            return bool(self._sel(_txt(op, "xpath") or ""))
        xp = _txt(op, "xpath")
        known = {"PatchOperationAdd", "PatchOperationInsert", "PatchOperationReplace",
                 "PatchOperationRemove", "PatchOperationAttributeAdd",
                 "PatchOperationAttributeSet", "PatchOperationAttributeRemove",
                 "PatchOperationSetName", "PatchOperationAddModExtension"}
        if cls not in known or xp is None:
            self.unsupported[cls or "?"] = self.unsupported.get(cls or "?", 0) + 1
            if self._watch(op):
                self.unsupported_watched.append((path, cls, xp))
            return True
        nodes = self._sel(xp)
        if not nodes:
            return False
        val = op.find("value")
        kids = [c for c in val if isinstance(c.tag, str)] if val is not None else []
        order = _txt(op, "order")
        if self._watch(op):
            self.touched.append((path, cls, xp))
        for n in nodes:
            if cls == "PatchOperationAdd":
                if order == "Prepend":
                    for i, v in enumerate(kids):
                        n.insert(i, copy.deepcopy(v))
                else:
                    for v in kids:
                        n.append(copy.deepcopy(v))
                    if val is not None and not kids and val.text and val.text.strip():
                        n.text = (n.text or "") + val.text
            elif cls == "PatchOperationInsert":
                par = n.getparent()
                if par is None:
                    continue
                i = par.index(n) + (1 if order == "Append" else 0)
                for k, v in enumerate(kids):
                    par.insert(i + k, copy.deepcopy(v))
            elif cls == "PatchOperationReplace":
                par = n.getparent()
                if par is None:
                    continue
                i = par.index(n)
                par.remove(n)
                for k, v in enumerate(kids):
                    par.insert(i + k, copy.deepcopy(v))
            elif cls == "PatchOperationRemove":
                par = n.getparent()
                if par is not None:
                    par.remove(n)
            elif cls in ("PatchOperationAttributeAdd", "PatchOperationAttributeSet"):
                a, v = _txt(op, "attribute"), _txt(op, "value")
                if a and (cls == "PatchOperationAttributeSet" or n.get(a) is None):
                    n.set(a, v or "")
            elif cls == "PatchOperationAttributeRemove":
                a = _txt(op, "attribute")
                if a and a in n.attrib:
                    del n.attrib[a]
            elif cls == "PatchOperationSetName":
                nm = _txt(op, "name")
                if nm:
                    n.tag = nm
            elif cls == "PatchOperationAddModExtension":
                me = n.find("modExtensions")
                if me is None:
                    me = LX.SubElement(n, "modExtensions")
                for v in kids:
                    me.append(copy.deepcopy(v))
        return True


# ── inheritance + extraction ────────────────────────────────────────────────────────────

class Resolver:
    def __init__(self, root):
        self.by_name = {}
        self.by_def = {}
        for e in root:
            if e.tag != "ThingDef":
                continue
            if e.get("Name"):
                self.by_name[e.get("Name")] = e
            dn = _txt(e, "defName")
            if dn and (e.get("Abstract") or "").lower() != "true":
                self.by_def[dn] = e     # a later load wins, as the engine's replace does

    def chain(self, e):
        seen = set()
        while e is not None and id(e) not in seen:
            seen.add(id(e))
            yield e
            pn = e.get("ParentName")
            e = self.by_name.get(pn) if pn else None

    def field(self, e, path):
        for a in self.chain(e):
            n = a.find(path)
            if n is not None:
                return n
        return None

    def text(self, e, path):
        n = self.field(e, path)
        return (n.text or "").strip() if n is not None and n.text else None


def _vec(s):
    if not s:
        return None
    m = re.findall(r"-?\d*\.?\d+", s)
    return [float(x) for x in m] if m else None


def _records(node, active):
    """[(name, commonality)] from a wildPlants / wildBiomes node, both XML shapes."""
    out = []
    if node is None:
        return out
    for c in node:
        if not isinstance(c.tag, str) or not _may_require_ok(c, active):
            continue
        if c.tag == "li":
            nm = _txt(c, "plant") or _txt(c, "biome")
            cm = _txt(c, "commonality")
        else:
            nm, cm = c.tag, (c.text or "").strip()
        try:
            out.append((nm, float(cm)))
        except (TypeError, ValueError):
            out.append((nm, None))
    return out


def classify(r):
    if r["defName"] in OVERRIDES:
        return OVERRIDES[r["defName"]]
    if r["tree"]:
        return ("UPRIGHT", "tree")
    if r["sowTags"]:
        return ("UPRIGHT", "sown crop")
    cells = r["matureCells"]
    if cells is not None and cells > GC_MAX_CELLS:
        return ("UPRIGHT", "mature %.2f cells > %.1f" % (cells, GC_MAX_CELLS))
    name_text = " ".join([r["defName"], r["label"] or ""])
    split = re.sub(r"([a-z])([A-Z])", r"\1 \2", name_text).replace("_", " ")
    gn, un = GC_WORDS.search(split), UPRIGHT_WORDS.search(split)
    if gn and not un:
        return ("GROUND_COVER", "name: " + gn.group(0))
    if un and not gn:
        return ("UPRIGHT", "name: " + un.group(0))
    desc = r["description"] or ""
    gd, ud = GC_WORDS.search(desc), UPRIGHT_WORDS.search(desc)
    if (gn or gd) and not (un or ud):
        return ("GROUND_COVER", "desc: " + (gn or gd).group(0))
    if (un or ud) and not (gn or gd):
        return ("UPRIGHT", "desc: " + (un or ud).group(0))
    return ("BORDERLINE", "words both/neither: +%s -%s" % (
        (gn or gd).group(0) if (gn or gd) else "", (un or ud).group(0) if (un or ud) else ""))


def census(modlist=FULL_MODLIST):
    mods, missing, version, active, names = load_set(modlist)
    root, nfiles = build_doc(mods, active)
    pt = Patcher(root, active, names)
    npatch = 0
    for m in mods:
        for p in _rel_files(m, "Patches"):
            npatch += 1
            pt.run_file(p)
    R = Resolver(root)
    our_biomes = {}
    for e in root:
        if e.tag == "BiomeDef" and (e.get("_pkg") or "").startswith("mandrake."):
            dn = _txt(e, "defName")
            if dn and (e.get("Abstract") or "").lower() != "true":
                our_biomes[dn] = e
    roster = {}       # plant -> {biome: commonality}
    for bd, e in our_biomes.items():
        for nm, c in _records(e.find("wildPlants"), active):
            roster.setdefault(nm, {})[bd] = c
    for dn, e in R.by_def.items():
        for bd, c in _records(R.field(e, "plant/wildBiomes"), active):
            if bd in our_biomes:
                roster.setdefault(dn, {}).setdefault(bd, c)
    rows, dangling = [], []
    for dn in sorted(roster):
        e = R.by_def.get(dn)
        if e is None:
            dangling.append(dn)
            continue
        alt = R.text(e, "altitudeLayer") or DEFAULT_ALT
        ds = _vec(R.text(e, "graphicData/drawSize"))
        vsr = _vec(R.text(e, "plant/visualSizeRange"))
        mmc = R.text(e, "plant/maxMeshCount")
        sow = R.field(e, "plant/sowTags")
        sow_l = [(li.text or "").strip() for li in sow] if sow is not None else []
        tc = R.text(e, "plant/treeCategory")
        harv = R.text(e, "plant/harvestedThingDef") or ""
        tree = (tc not in (None, "None")) or ("wood" in harv.lower() and "log" in harv.lower())
        dsx = ds[0] if ds else 1.0
        vmax = vsr[-1] if vsr else 1.0
        file_hint = e.get("_file")
        row = {
            "defName": dn, "package": e.get("_pkg"), "label": _txt(e, "label"),
            "description": R.text(e, "description"),
            "altitudeLayer": alt, "altIndex": ALT.get(alt),
            "drawSize": ds, "visualSizeRange": vsr, "maxMeshCount": int(mmc) if mmc else 1,
            "matureCells": round(dsx * vmax, 3), "sowTags": sow_l, "treeCategory": tc,
            "tree": bool(tree), "thingClass": R.text(e, "thingClass"),
            "biomes": roster[dn], "file": file_hint,
        }
        row["class"], row["why"] = classify(row)
        rows.append(row)
    stats = {"version": version, "mods": len(mods), "missing": missing, "defFiles": nfiles,
             "patchFiles": npatch, "patchOps": pt.ops, "unsupported": pt.unsupported,
             "unsupportedWatched": pt.unsupported_watched, "xpathErrors": pt.xpath_errors,
             "touched": pt.touched, "ourBiomes": sorted(our_biomes), "dangling": dangling,
             "fromRepo": sorted(m["packageId"] for m in mods if m["fromRepo"])}
    return rows, stats


def md_tables(rows):
    out = []
    for cl in ("GROUND_COVER", "BORDERLINE", "UPRIGHT"):
        rs = [r for r in rows if r["class"] == cl]
        out.append("\n### %s (%d)\n" % (cl, len(rs)))
        out.append("| defName | label | owner package | layer now | drawSize | visualSizeRange "
                   "| mature cells | meshes | sowTags | tree | biomes | why |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in sorted(rs, key=lambda r: (r["package"], r["defName"])):
            out.append("| %s |" % " | ".join(str(x).replace("|", "/") for x in (
                "`%s`" % r["defName"], r["label"] or "", r["package"],
                "%s (%s)" % (r["altitudeLayer"], r["altIndex"]),
                "x".join("%g" % v for v in (r["drawSize"] or [])) or "-",
                "~".join("%g" % v for v in (r["visualSizeRange"] or [])) or "-",
                r["matureCells"], r["maxMeshCount"], ",".join(r["sowTags"]) or "-",
                "yes" if r["tree"] else "-", ", ".join(sorted(r["biomes"])), r["why"])))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--modlist", default=FULL_MODLIST)
    ap.add_argument("--json")
    ap.add_argument("--from-json", help="reclassify a saved census instead of rebuilding it")
    ap.add_argument("--md", help="write the census as markdown tables (one per class)")
    a = ap.parse_args(argv)
    if a.from_json:
        j = json.load(open(a.from_json))
        rows, st = j["rows"], j["stats"]
        for r in rows:
            r["class"], r["why"] = classify(r)
    else:
        rows, st = census(a.modlist)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"rows": rows, "stats": st}, f, indent=1, default=str)
    if a.md:
        with open(a.md, "w") as f:
            f.write(md_tables(rows))
    s = {k: v for k, v in st.items() if k not in ("touched", "unsupportedWatched", "dangling",
                                                    "ourBiomes", "fromRepo")}
    print(json.dumps(s, default=str))
    print("ourBiomes=%d plants=%d dangling=%d unsupportedWatched=%d" % (
        len(st["ourBiomes"]), len(rows), len(st["dangling"]), len(st["unsupportedWatched"])))
    for r in rows:
        print("\t".join(str(x) for x in (r["class"], r["defName"], r["package"],
                                         r["altitudeLayer"], r["matureCells"],
                                         r["maxMeshCount"], r["why"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
