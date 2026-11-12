#!/usr/bin/env python3
r"""ship_contributions.py -- does every shipped biome give the gravship something, and does the list say so truly?

    python3 src/RimMandrake/Utils/ship_contributions.py              # the check (exit 1 on any FAIL)
    python3 src/RimMandrake/Utils/ship_contributions.py --inventory  # every player-buildable def per biome mod
    ... [--json out.json] [--data <RimWorld Data dir>]

THE QUESTION (BIOME_SHIP_CONTRIBUTIONS_1, owner 2026-09-24): "how can this biome uniquely add something to the
ship?" Its verify: every shipped biome mod has at least one ship-buildable contribution or an owner-ruled exemption;
the running list in infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md matches what the mods actually ship.

SHIPPED BIOME MODS: every entry with group "biome" in src/RimMandrake/Biomes.compose.json whose wave <= compose_wave
(composed into mandrake.rm.biomes). The list is read, never hard-wired.

SHIP-BUILDABLE, decided the way the engine decides it (decompiled 1.6, measured 2026-11-11):
  * GenConstruct.CanBuildOnTerrain checks c.GetAffordances(map); GridsUtility.GetAffordances returns the FOUNDATION's
    affordances when a foundation is present. The Odyssey `Substructure` TerrainDef (merged through FloorBase)
    carries Light, Medium, Heavy, Walkable, Substructure. So a def whose terrainAffordanceNeeded is one of those (or
    unset) passes the terrain test on a deck cell, floors included (a floor's top terrain sits over the foundation).
  * the def must be player-buildable: a designationCategory (ThingDef or TerrainDef), not abstract.
  * no placeWorker that refuses a deck or pins the thing to one site (geyser, vent, pool rim, tile mutator,
    beside a terrain, biome-floor-only, InvalidOverSubstructure). Custom placeWorkers are classified below by
    reading their C#; an UNKNOWN one fails the def as UNMEASURED rather than passing it.
  * it must fly: Gravship.cs (1.6) leaves behind any thing whose def sets bringAlongOnGravship false.
  The substructure affordance set is READ from the game's Odyssey defs on every run, not assumed.

THE LIST: the `## running list` table of the item file. Column 1 names the biome (its compose label or key);
column 3, `defs`, names every def the row claims in backticks; a row whose contribution text starts with
"EXEMPT" must cite an owner ruling (`--owner-said`/`--by-card` text or a dated quote). Checks:
  coverage   every shipped biome has exactly one row
  real       every def a row names exists in src/ and is ship-buildable (a named def that is not is a FALSE claim)
  obtainable (and fuel: every RM_ fuel of a Refuelable comp likewise) every research prerequisite of a named def is a real ResearchProjectDef, and every RM_/RUT_/RSW_
             material in its costList is named by something that hands it out (a mention outside every costList)
  own        each row names at least one def that is the biome's own: defined in that biome's mod folder, or
             costing a material defined there (otherwise the gift is not that biome's)
  also       (information, not a failure) every other ship-placeable def the biome mod defines: the row names the
             biome's GIFT, a choice; a dig shaft or a tipping pad can stand on a deck without being what the
             biome gives the ship. --json carries the full list per biome.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
COMPOSE = SRC / "RimMandrake" / "Biomes.compose.json"
ITEM = ROOT / "infrastructure" / "state" / "items" / "BIOME_SHIP_CONTRIBUTIONS_1.md"
DEFAULT_DATA = [
    "/mnt/d/SteamLibrary/steamapps/common/RimWorld/Data",
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
    r"D:\SteamLibrary\steamapps\common\RimWorld\Data",
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
]

# placeWorker verdicts, each from reading the class (vanilla: decompiled 1.6; ours: the repo C#).
PW_DECK_OK = {   # each read in decompiled 1.6 / the repo on 2026-11-11: none refuses a deck cell
    "PlaceWorker_GlowRadius", "PlaceWorker_Heater", "PlaceWorker_PreventInteractionSpotOverlap",
    "PlaceWorker_ReportWorkSpeedPenalties", "PlaceWorker_ShowTurretRadius", "PlaceWorker_TurretTop",
    "PlaceWorker_DoorLearnOpeningSpeed",
    "PlaceWorker_OnSubstructure",                     # requires the deck
    "RimMandrake.Cauldron.RM_PlaceWorker_OnShipHull",  # FoundationAt(loc).IsSubstructure or refuse: deck ONLY
    "RimMandrake.Scarlands.RM_PlaceWorker_WallAdjacent",  # a full impassable edifice beside it: hulls count
}
PW_SITE_BOUND = {
    "PlaceWorker_InvalidOverSubstructure": "refuses a deck cell",
    "PlaceWorker_OnSteamGeyser": "needs a steam geyser (never on a deck)",
    "RimMandrake.Cauldron.RM_PlaceWorker_OnCauldronVent": "needs a Cauldron vent",
    "RimMandrake.EnvironmentalHazards.RM_PlaceWorker_OnRequiredVentComp": "needs a resource vent under it",
    "RimMandrake.EnvironmentalHazards.RM_PlaceWorker_RequiresTileMutator": "needs a tile mutator on THIS tile",
    "RimMandrake.Scarlands.PlaceWorker_NearReactionPool": "needs a reaction-pool rim",
    "RimMandrake.Stillsand.RM_PlaceWorker_BesideTerrain": "needs a named terrain beside it",
    "RimMandrake.TerminalBiomes.RM_PlaceWorker_ChillFloorOnly": "Chill seabed only",
}


def find_data(arg):
    for p in ([arg] if arg else []) + DEFAULT_DATA:
        if p and Path(p).is_dir():
            return Path(p)
    sys.exit("ship_contributions: no RimWorld Data dir found (tried %s); pass --data" % DEFAULT_DATA)


def is_list(el):
    kids = list(el)
    return bool(kids) and all(k.tag == "li" for k in kids)


def merge(parent, child):
    """XmlInheritance: child overrides; list nodes append unless Inherit=False; dict nodes merge recursively, child
    elements matched to the parent's by tag in order (an unmatched one is appended); IsNull=True removes."""
    out = ET.Element(child.tag, dict(child.attrib))
    out.text = child.text
    if child.get("Inherit", "").lower() == "false":
        for k in child:
            out.append(k)
        return out
    if is_list(child) or (is_list(parent) and len(child) == 0 and not (child.text or "").strip()):
        for k in parent:
            out.append(k)
        for k in child:
            out.append(k)
        return out
    if len(child) == 0:
        if (child.text or "").strip() or not len(parent):
            return out
    pool = [pk for pk in parent]
    merged = []
    for k in child:
        hit = next((i for i, pk in enumerate(pool) if pk is not None and pk.tag == k.tag and k.tag != "li"), None)
        if hit is None:
            merged.append((None, k))
        else:
            merged.append((hit, merge(pool[hit], k)))
            pool[hit] = None
    for i, pk in enumerate(pool):        # parent order first, overridden in place
        if pk is not None:
            out.append(pk)
        else:
            for h, m in merged:
                if h == i:
                    out.append(m)
    for h, m in merged:
        if h is None:
            out.append(m)
    for el in list(out):
        if el.get("IsNull", "").lower() == "true":
            out.remove(el)
    return out


class Index:
    def __init__(self):
        self.named = {}       # (tag, Name) -> node
        self.defs = {}        # (tag, defName) -> (node, mod folder)
        self.dups = set()     # keys defined twice in scope (the first indexed wins here; the engine may differ)
        self.bad_files = []   # (path, error) that failed to parse

    def add_file(self, path, mod):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as e:
            self.bad_files.append((str(path), str(e)))
            return
        if root.tag != "Defs":
            return
        for n in root:
            if not isinstance(n.tag, str):
                continue
            name = n.get("Name")
            if name:
                if (n.tag, name) in self.named:
                    self.dups.add((n.tag, name))
                self.named.setdefault((n.tag, name), n)
            dn = n.findtext("defName")
            if dn and n.get("Abstract", "").lower() != "true":
                if (n.tag, dn.strip()) in self.defs:
                    self.dups.add((n.tag, dn.strip()))
                self.defs.setdefault((n.tag, dn.strip()), (n, mod))

    def resolve(self, node, depth=0):
        pn = node.get("ParentName")
        if not pn or depth > 30:
            return node
        parent = self.named.get((node.tag, pn))
        if parent is None:
            return node
        return merge(self.resolve(parent, depth + 1), node)


MODLIST = ROOT / "infrastructure" / "state" / "modlists" / "ModsConfig.FULL.LATEST.xml"
_SCOPE = None


def shipped_mod_dirs():
    """src mod folders that ship: packageId on the FULL test list, or composed into mandrake.rm.biomes."""
    global _SCOPE
    if _SCOPE is not None:
        return _SCOPE
    active = {li.text.strip().lower() for li in ET.parse(MODLIST).getroot().find("activeMods") if li.text}
    comp = json.loads(COMPOSE.read_text(encoding="utf-8"))
    folded = {e["source"] for e in comp["entries"] if e["wave"] <= comp["compose_wave"]} | {comp["shell"]["source"]}
    out = []
    for tier in ("RimMandrake", "RimUtinni", "RimStarWars"):
        base = SRC / tier
        for mod in sorted(base.iterdir()) if base.is_dir() else []:
            about = mod / "About" / "About.xml"
            pid = ""
            if about.is_file():
                try:
                    pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
                except ET.ParseError:
                    pid = ""
            if pid in active or (tier == "RimMandrake" and mod.name in folded and "mandrake.rm.biomes" in active):
                out.append((tier, mod))
    _SCOPE = out
    return out


def mod_files(mod, suffix):
    for p in sorted(mod.rglob("*" + suffix)):
        rel = p.relative_to(mod).parts
        if any(x in ("Textures", "SelfTest", "Languages", "obj", "bin") for x in rel) or p.name == "Program.cs":
            continue
        yield p, rel


def build_index(data):
    ix = Index()
    for d in sorted(data.iterdir()):
        for p in sorted((d / "Defs").rglob("*.xml")) if (d / "Defs").is_dir() else []:
            ix.add_file(p, "Data/" + d.name)
    data_bad = list(ix.bad_files)
    if data_bad:
        sys.exit("ship_contributions: UNMEASURED, %d game Data def file(s) failed to parse, e.g. %s"
                 % (len(data_bad), data_bad[0]))
    for tier, mod in shipped_mod_dirs():
        for p, rel in mod_files(mod, ".xml"):
            if "Defs" in rel and "Patches" not in rel:
                ix.add_file(p, "%s/%s" % (tier, mod.name))
    return ix


def substructure_affordances(ix):
    hit = ix.defs.get(("TerrainDef", "Substructure"))
    if not hit:
        sys.exit("ship_contributions: Odyssey TerrainDef Substructure not found under the Data dir: cannot judge")
    node = ix.resolve(hit[0])
    aff = [li.text.strip() for li in node.findall("affordances/li") if li.text]
    if "Substructure" not in aff or "Light" not in aff:
        sys.exit("ship_contributions: Substructure affordances read as %s: the merge cannot see FloorBase" % aff)
    return set(aff)


def texts(node, path):
    return [li.text.strip() for li in node.findall(path) if li.text and li.text.strip()]


def judge(ix, tag, dn, deck_aff):
    """-> dict(buildable, deck, why, costs, mod)"""
    node, mod = ix.defs[(tag, dn)]
    r = ix.resolve(node)
    cat = (r.findtext("designationCategory") or "").strip()
    out = {"def": dn, "type": tag, "mod": mod, "category": cat, "label": (r.findtext("label") or "").strip()}
    cl = r.find("costList")
    costs = [k.tag for k in cl] if cl is not None else []
    costs += ["stuff:" + s for s in texts(r, "stuffCategories/li")]
    out["costs"] = costs
    minified = (r.findtext("minifiedDef") or "").strip()
    if cat:
        out["how"] = "built (%s tab)" % cat
    elif minified and tag == "ThingDef":
        out["how"] = "installed (minified; never constructed)"
    else:
        out.update(buildable=False, deck=False, why="no designationCategory and not minifiable (not player-placeable)")
        return out
    out["buildable"] = True
    if (r.findtext("bringAlongOnGravship") or "").strip().lower() == "false":
        out.update(deck=False, why="bringAlongOnGravship false: the ship leaves it behind")
        return out
    if r.find("plant") is not None:
        out.update(deck=False, why="a plant: it roots by fertility and a deck's is 0")
        return out
    need = (r.findtext("terrainAffordanceNeeded") or "").strip()
    if need and need not in deck_aff:
        out.update(deck=False, why="needs affordance %s; a deck gives %s" % (need, sorted(deck_aff)))
        return out
    for pw in texts(r, "placeWorkers/li"):
        if pw in PW_SITE_BOUND:
            out.update(deck=False, why="%s: %s" % (pw.split(".")[-1], PW_SITE_BOUND[pw]))
            return out
        if pw not in PW_DECK_OK:
            out.update(deck=False, why="UNMEASURED placeWorker %s: classify it in ship_contributions.py" % pw)
            return out
    out.update(deck=True, why="affordance %s on a deck; placeWorkers deck-safe" % (need or "unset"))
    if not cat:
        src = material_sources(dn)
        out["sources"] = src
        if not src and not (r.findtext("tradeTags/li") or r.findtext("thingSetMakerTags/li")):
            out.update(deck=False, why="install-only and nothing in src/ hands it to the player (no source names it)")
    return out


# A mention hands an item OUT only in these contexts (a WHITELIST: code review 2026-11-11 showed a blacklist leaks
# through hyperlinks, defaultStuff, affordance tags, disallow patches and C# lookup tables).
SOURCE_FIELDS = {"mineableThing", "leatherDef", "harvestedThingDef", "woolDef", "milkDef", "gatherDef", "thingToSpawn",
                 "eggFertilizedDef", "eggUnfertilizedDef", "boneDef", "greatBoneDef"}   # text == item
SOURCE_DICTS = {"butcherProducts", "products", "killedLeavings", "leavings", "smeltProducts",
                "leaveResourcesWhenKilled"}                                           # <item>n</item> under these
THING_FIELDS = {"thingDef", "thing"}            # text == item, only under a SOURCE_OWNERS ancestor
SOURCE_OWNERS = ("StockGenerator", "QuestNode", "ThingSetMaker", "GenStep", "Reward", "leavings")
SPAWN_CS = re.compile(r"MakeThing|GenSpawn|GenPlace|TryPlaceThing|MakeMinified|TryDropThing|ThingSetMaker|"
                      r"butcherProducts|SpawnThing|DropPod", re.S)
_XML = None
_CS = None


def _load_scope():
    global _XML, _CS
    if _XML is not None:
        return
    _XML, _CS = [], []
    for tier, mod in shipped_mod_dirs():
        for p, rel in mod_files(mod, ".xml"):
            if p.name == "About.xml":
                continue
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
                _XML.append((p, raw, ET.fromstring(raw.encode("utf-8"))))
            except (ET.ParseError, OSError, ValueError):
                pass
        for p, rel in mod_files(mod, ".cs"):
            try:
                code = re.sub(r"//[^\n]*|/\*.*?\*/", "", p.read_text(encoding="utf-8", errors="replace"), flags=re.S)
            except OSError:
                continue
            if SPAWN_CS.search(code):                 # only files that spawn something can be a source
                _CS.append((p, code))


def _context_names(el, parent, xpath_tail=""):
    """Tags and Class attributes from el up to the root, plus the patch's xpath tail when inside a <value>."""
    out, a = [], el
    while a is not None:
        out.append(a.tag)
        if a.get("Class"):
            out.append(a.get("Class"))
        if a.tag == "value" and xpath_tail:
            out.extend(xpath_tail)
        a = parent.get(a)
    return out


def _xml_source_hits(root, item):
    parent = {c: pnode for pnode in root.iter() for c in pnode}
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        is_dict = el.tag == item
        if not is_dict and (el.text or "").strip() != item:
            continue
        tail = []
        a = el
        while a is not None and a.tag != "value":
            a = parent.get(a)
        if a is not None:                                   # inside a patch <value>: read the xpath it targets
            op = parent.get(a)
            xp = (op.findtext("xpath") or "") if op is not None else ""
            if "Remove" in (op.get("Class") or "") if op is not None else False:
                continue
            tail = re.findall(r"[A-Za-z_]+", xp.split("]")[-1])
        names = _context_names(el, parent, tail)
        if any("Buy" in n for n in names) or "disallowedThingDefs" in names or "costList" in names:
            continue
        up = names[1] if len(names) > 1 else ""
        if a is not None and up == "value" and tail:
            up = tail[-1]
        if is_dict and (up in SOURCE_DICTS or "fishTypes" in names[1:3]):
            yield el                                        # fishTypes: Odyssey fishing, BiomeDef.fishTypes.<band>
        elif not is_dict and el.tag in SOURCE_FIELDS:
            yield el
        elif not is_dict and el.tag in THING_FIELDS | {"li"} and any(
                any(o in n for o in SOURCE_OWNERS) for n in names[1:]):
            if el.tag == "li" and not (len(names) > 3 and names[1] == "thingDefs"
                                       and any("StockGenerator" in n for n in names[2:4])):
                continue
            yield el


_SOURCES = {}


def material_sources(item):
    if item not in _SOURCES:
        _SOURCES[item] = _material_sources(item)
    return _SOURCES[item]


def _material_sources(item):
    """Files in shipped mods that hand the player `item`: an XML element naming it in a hand-out context
    (SOURCE_FIELDS, SOURCE_DICTS, or a thing field under a trader/quest/thing-set/genstep/leavings owner; a patch
    counts when the xpath it adds into is such a context), or a C# file that names it AND spawns things
    (SPAWN_CS; file-level, because spawns go through name tables, e.g. RM_ReactionPools.Reagents). About.xml, Languages, Textures, SelfTest and Program.cs are never sources."""
    _load_scope()
    hits = []
    for p, raw, root in _XML:
        if item in raw and any(True for _ in _xml_source_hits(root, item)):
            hits.append(str(p.relative_to(ROOT)))
    pat = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(item))
    for p, code in _CS:
        if item in code and pat.search(code):
            hits.append(str(p.relative_to(ROOT)))
    return hits


def obtainable(ix, item, depth=0):
    """'' if the player can get `item`, else why not. A recipeMaker counts only if a recipe user exists and its own
    RM_ costs are obtainable (to depth 4); otherwise a source in a shipped mod must name it."""
    if ("ThingDef", item) not in ix.defs:
        return "%s is not a ThingDef in scope" % item
    r = ix.resolve(ix.defs[("ThingDef", item)][0])
    if (r.findtext("tradeTags/li") or "") or (r.findtext("thingSetMakerTags/li") or ""):
        return ""                               # vanilla traders / reward generators pick it by tag
    try:
        if float((r.findtext("deepCommonality") or "0").strip()) > 0:
            return ""                           # vanilla deep scanner + deep drill (CompDeepScanner.ChooseLumpThingDef)
    except ValueError:
        pass
    if material_sources(item):
        return ""
    rm = r.find("recipeMaker")
    if rm is not None and depth < 4:
        users = texts(rm, "recipeUsers/li")
        if not any(("ThingDef", u) in ix.defs for u in users):
            return "%s is crafted only at %s, none of which exists" % (item, users or "no bench")
        cl = r.find("costList")
        for c in [k.tag for k in cl] if cl is not None else []:
            if re.match(r"(RM|RUT|RSW)_", c):
                why = obtainable(ix, c, depth + 1)
                if why:
                    return "%s is crafted from %s, and %s" % (item, c, why)
        return ""
    return "nothing in a shipped mod hands out %s (no mineable/butcher/recipe/trader/C# source)" % item


PLACEMENT_FIELDS = ("bringAlongOnGravship", "placeWorkers", "terrainAffordanceNeeded", "designationCategory",
                    "minifiedDef", "plant", "useStuffTerrainAffordance")


_PATCHES = None


def parent_names(ix, node):
    out, seen = [], set()
    while node is not None and node.get("ParentName") and node.get("ParentName") not in seen:
        pn = node.get("ParentName")
        seen.add(pn)
        out.append(pn)
        node = ix.named.get((node.tag, pn))
    return out


def patches_touching(dn, parents=()):
    """[(patch file, placement_relevant)] for every shipped patch operation whose xpath names `dn` (either quote
    style). Placement-relevant = that operation removes the def or touches a PLACEMENT_FIELDS field (in its xpath
    tail or its own value), or rewrites its ParentName: the static verdict cannot see it. Judged per operation
    element. KNOWN LIMIT: xpath is matched by pattern (defName=, @Name/@ParentName of an ancestor, contains/
    starts-with/ends-with on defName), not evaluated; a selector on another field (e.g. [designationCategory=..])
    is not seen. The patched tree itself is effective_def_lint.py's job (whole mod list, Windows python)."""
    out = []
    alts = [r"defName\s*=\s*[\"']%s[\"']" % re.escape(dn)]
    alts += [r"@(Parent)?Name\s*=\s*[\"']%s[\"']" % re.escape(n) for n in parents]  # ancestor / its children
    alts += [r"(?<!not\()(contains|starts-with|ends-with)\(\s*defName\s*,\s*[\"'][^\"']*[\"']"]  # judged below
    pat = re.compile("|".join(alts))
    global _PATCHES
    if _PATCHES is None:
        _PATCHES = [(p, p.read_text(encoding="utf-8", errors="replace")) for tier, mod in shipped_mod_dirs()
                    for p, rel in mod_files(mod, ".xml") if "Patches" in rel]
    keys = [dn] + list(parents) + ["defName,", "defName ,", "defName,"]
    for p, t in _PATCHES:
        if not any(k in t for k in keys[:1 + len(parents)]) and "(defName" not in t.replace(" ", ""):
            continue
            for m in re.finditer(r"(contains|starts-with|ends-with)\(\s*defName\s*,\s*[\"']([^\"']*)[\"']", t):
                fn, sub = m.group(1), m.group(2)
                hit = (sub in dn if fn == "contains" else dn.startswith(sub) if fn == "starts-with"
                       else dn.endswith(sub))
                if not hit:
                    t = t.replace(m.group(0), "")                                  # a selector not matching dn
            if not pat.search(t):
                continue
            try:
                root = ET.fromstring(t.encode("utf-8"))
            except ET.ParseError:
                out.append((str(p.relative_to(ROOT)), True))   # unreadable patch on a claimed def: fail safe
                continue
            hot = False
            for op in root.iter():
                xp = op.findtext("xpath") if isinstance(op.tag, str) else None
                if not xp or not pat.search(xp):
                    continue
                tail = xp[pat.search(xp).end():]
                value = op.find("value")
                vtags = {e.tag for e in value.iter()} if value is not None else set()
                cls = op.get("Class") or ""
                if any(re.search(r"\b%s\b" % f, tail) for f in PLACEMENT_FIELDS) or any(
                        f in vtags for f in PLACEMENT_FIELDS) or (
                        ("Remove" in cls and tail.strip(" ]/") == "") or (
                        "Attribute" in cls and (op.findtext("attribute") or "").strip() == "ParentName")):
                    hot = True
            out.append((str(p.relative_to(ROOT)), hot))
    return out


def research_missing(ix, r):
    return [rp for rp in texts(r, "researchPrerequisites/li") if ("ResearchProjectDef", rp) not in ix.defs]


def shipped_biomes():
    d = json.loads(COMPOSE.read_text(encoding="utf-8"))
    wave = d["compose_wave"]
    return [e for e in d["entries"] if e["group"] == "biome" and e["wave"] <= wave]


def own_defs(ix, folder):
    mod = "RimMandrake/" + folder
    return sorted(dn for (tag, dn), (_, m) in ix.defs.items() if m == mod and tag in ("ThingDef", "TerrainDef"))


def parse_list(item=None):
    item = Path(item) if item else ITEM
    text = item.read_text(encoding="utf-8")
    m = re.search(r"^## running list\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return None, "no '## running list' section in %s" % item
    rows = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        if line.count("|") != 5:
            return None, "malformed table line (want 4 columns): %s" % line[:120]
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0].lower() == "biome":
            continue
        rows.append({"biome": cells[0], "contribution": cells[1], "defs": re.findall(r"`([A-Za-z0-9_]+)`", cells[2]),
                     "source": cells[3]})
    return rows, None


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower().replace("the ", ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data")
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--item", help="read the running list from this file instead of the item (selftests)")
    a = ap.parse_args(argv)
    ix = build_index(find_data(a.data))
    deck = substructure_affordances(ix)
    biomes = shipped_biomes()
    report = {"deck_affordances": sorted(deck), "biomes": []}
    defs_where = {}
    for (tag, dn) in ix.defs:
        if tag in ("ThingDef", "TerrainDef"):
            defs_where.setdefault(dn, tag)
    print("deck affordances (read from Odyssey Substructure): %s" % ", ".join(sorted(deck)))
    print("shipped biome mods (Biomes.compose.json): %d" % len(biomes))
    inv = {}
    for e in biomes:
        mine = [judge(ix, defs_where[dn], dn, deck) for dn in own_defs(ix, e["source"])]
        inv[e["key"]] = [j for j in mine if j["buildable"]]
    if a.inventory:
        for e in biomes:
            print("\n## %s (%s)" % (e["label"], e["source"]))
            for j in inv[e["key"]] or []:
                print("  %-5s %-34s %-12s %s | cost %s%s" % ("DECK" if j["deck"] else "site", j["def"],
                                                            j["category"] or "install", j["why"],
                                                            ",".join(j["costs"]) or "-",
                                                            " | from " + ", ".join(j.get("sources", [])[:3])
                                                            if j.get("sources") else ""))
            if not inv[e["key"]]:
                print("  (no player-buildable ThingDef/TerrainDef)")
        return 0
    rows, err = parse_list(a.item)
    fails = []
    if err:
        print("FAIL list: " + err)
        return 1
    keyed = {}
    for r in rows:
        hit = [e for e in biomes if norm(r["biome"]) in (norm(e["label"]), norm(e["key"]))]
        if not hit:
            fails.append("list row '%s' names no shipped biome" % r["biome"])
            print("FAIL   list row '%s' names no shipped biome" % r["biome"])
            continue
        if hit[0]["key"] in keyed:
            fails.append("biome %s has two rows" % hit[0]["key"])
            print("FAIL   biome %s has two rows" % hit[0]["key"])
        keyed[hit[0]["key"]] = r
    for e in biomes:
        k = e["key"]
        r = keyed.get(k)
        entry = {"biome": k, "label": e["label"], "folder": e["source"], "row": r, "defs": [], "verdict": "PASS",
                 "problems": []}
        own_names = set(own_defs(ix, e["source"]))
        if r is None:
            entry["problems"].append("coverage: no row in the running list")
        elif r["contribution"].upper().startswith("EXEMPT"):
            # the ruling must sit in the EXEMPT text itself: a row's source column may carry an owner date for a
            # former gift, which is no exemption (fourth review, 2026-11-11)
            if not re.search(r"owner(-said|,? by card|,?) ?20\d\d-\d\d-\d\d|per-ruling [A-Z_0-9]+",
                             r["contribution"][len("EXEMPT"):]):
                entry["problems"].append("exempt row cites no owner ruling")
            entry["verdict"] = "EXEMPT"
        else:
            if not r["defs"]:
                entry["problems"].append("real: the row names no def")
            own_hit = False
            for dn in r["defs"]:
                tag = defs_where.get(dn)
                if not tag:
                    entry["problems"].append("real: `%s` is not a ThingDef/TerrainDef in src/ or the game" % dn)
                    continue
                j = judge(ix, tag, dn, deck)
                entry["defs"].append(j)
                if not j["buildable"] or not j["deck"]:
                    entry["problems"].append("real: `%s` is not ship-buildable: %s" % (dn, j["why"]))
                    continue
                if dn in own_names or any(c in own_names for c in j["costs"]):
                    own_hit = True
                node = ix.resolve(ix.defs[(tag, dn)][0])
                for rp in research_missing(ix, node):
                    entry["problems"].append("obtainable: `%s` needs research %s, which is not a ResearchProjectDef"
                                             % (dn, rp))
                for c in j["costs"]:
                    if c.startswith("stuff:") or not re.match(r"(RM|RUT|RSW)_", c):
                        continue
                    why = obtainable(ix, c)
                    if why:
                        entry["problems"].append("obtainable: `%s` costs %s: %s" % (dn, c, why))
                for li in node.findall("comps/li"):
                    if "Refuelable" not in (li.get("Class") or ""):
                        continue
                    fuels = texts(li, "fuelFilter/thingDefs/li")
                    whys = [obtainable(ix, f) if re.match(r"(RM|RUT|RSW)_", f) else "" for f in fuels]
                    if fuels and all(whys):           # a fuel filter is an OR: one obtainable fuel runs it
                        entry["problems"].append("obtainable: `%s` burns only %s, none obtainable: %s"
                                                 % (dn, ", ".join(fuels), whys[0]))
                for pf, hot in patches_touching(dn, parent_names(ix, ix.defs[(tag, dn)][0])):
                    if hot:
                        entry["problems"].append("a patch edits `%s`'s placement (remove/placeWorkers/affordance/"
                                                 "bringAlongOnGravship...): %s; the static verdict cannot see it"
                                                 % (dn, pf))
                    else:
                        entry.setdefault("warnings", []).append("a patch names `%s` (no placement field): %s"
                                                                % (dn, pf))
                if (tag, dn) in ix.dups:
                    entry["problems"].append("`%s` is defined twice in scope; which one loads is unmeasured" % dn)
            if r["defs"] and not own_hit:
                entry["problems"].append("own: no named ship-buildable def is %s's own (defined in %s or costing "
                                         "its material)" % (k, e["source"]))
            entry["also"] = [j["def"] for j in inv[k] if j["deck"] and j["def"] not in r["defs"]]
        if entry["problems"]:
            entry["verdict"] = "FAIL"
            fails.extend("%s: %s" % (k, p) for p in entry["problems"])
        report["biomes"].append(entry)
        names = ", ".join("%s%s" % (j["def"], "" if j["deck"] else "(!)") for j in entry["defs"]) or "-"
        print("%-6s %-20s %s%s" % (entry["verdict"], e["label"], names,
                                   "   (also deck-placeable: %d)" % len(entry.get("also", [])) if entry.get("also") else ""))
        for p in entry["problems"]:
            print("         - " + p)
        for w in entry.get("warnings", []):
            print("         ~ " + w)
    if ix.bad_files:
        print("WARN   %d src def file(s) failed to parse and were skipped, e.g. %s" % (len(ix.bad_files),
                                                                                   ix.bad_files[0][0]))
    print("%d/%d biomes PASS or EXEMPT; %d problem(s)" % (sum(b["verdict"] != "FAIL" for b in report["biomes"]),
                                                          len(biomes), len(fails)))
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
