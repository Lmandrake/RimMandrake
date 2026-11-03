#!/usr/bin/env python3
"""plant_economy_census.py — every plant we ship, measured against the plant economy bar.

Item PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE. The bar and why it is the bar:
design/RimMandrake/plant_economy_rule_2026-11-01.md. In one line: the water rule (x0.1 dry, x10 wet and lit,
x4 wet natives, tree drink, a harvest uses up the water) lives at RUNTIME in ExplosiveGrowth; the def numbers
it multiplies sit at VANILLA PARITY at x1, so the water, not the def, makes the swing.

What it reads (no game, no dump needed for our defs):
  * every XML under src/RimMandrake, src/RimStarWars, src/RimUtinni (our defs and our patches);
  * the base game's Data/*/Defs (Ludeon parents such as PlantBase/TreeBase, and products such as WoodLog);
  * the ExplosiveGrowth roster (<notTrees>, <treeRulesExempt>, <fungi>).
Inheritance is resolved RimWorld's way (child scalars override, <li> lists append unless Inherit="False").
Patches whose xpath names `/Defs/ThingDef[defName="X" (or ...)]/plant/<field>` with Replace/Add are applied.
Not modelled (a limit, not a pass): a Sequence that stops at a failed op (the census assumes every op applies; a
failed op is a load error our load checks see), and a Conditional whose condition depends on an EARLIER patch's
result (conditions are read against the unpatched XML).
A product found in neither tree is looked up in the frozen def dump if present; failing that it is UNMEASURED,
and an UNMEASURED row fails --check exactly as an off-rule row does (an unseen number is not a passing one).

Usage:
  plant_economy_census.py            table of every off-rule / unmeasured row, then the totals line
  plant_economy_census.py --all      every row
  plant_economy_census.py --check    exit 1 unless "0 off-rule, 0 unmeasured"
  plant_economy_census.py --json P   write every row as JSON to P
"""
import argparse
import copy
import glob
import json
import math
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # .../src
REPO = os.path.dirname(ROOT)
OUR_TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
ROSTER = os.path.join(ROOT, "RimMandrake", "ExplosiveGrowth", "Defs", "ExplosiveGrowth", "RM_ExplosiveGrowthRoster.xml")
GAME_DATA_CANDIDATES = [
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
]
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCALLOW  # noqa: E402
DUMP_CANDIDATES = [
    LOCALLOW + "/DefDump/defs.sqlite",
]

# ---- the bar (design/RimMandrake/plant_economy_rule_2026-11-01.md §2; keep the two in step) ----
VALUE_PER_GROWDAY_MAX = 4.0       # E1: silver of harvest per grow day; vanilla ordinary max Plant_TreeCocoa 3.75
NUTRITION_PER_GROWDAY_MAX = 0.135  # E2: nutrition per grow day; vanilla max Plant_Ambrosia 0.133, Plant_Haygrass 0.129
LOGS_PER_GROWDAY_MAX = 3.0        # E4: wood per grow day; vanilla Plant_SaguaroCactus / Plant_TreePolux 3.0
MIN_PLANTS = 300                  # live tree on 2026-11-01: 394; far fewer means the census is blind, not that we cut plants
TREE_MIN_VISUAL = 3.0             # E3: Q2 "SIZE 3.0+ ONLY" (tree_burst_design_2026-10-17.md §2)
WOOD_TAGS = ("WoodLog",)

# Per-def allowances. Each needs a reason a reader can check; keep this list short.
# A ThingDef whose parent is outside our tree and the base game is reported UNMEASURED (it might be a plant) unless
# its parent is known not to be one.
KNOWN_NONPLANT_PARENTS = {
    "AdaptiveStorageBase": "Adaptive Storage Framework's storage-building base (our shelves), never a plant",
}

EXCEPTIONS = {
    # The base game's own Plant_Ambrosia is 4 Ambrosia (15 silver, 0.2 nutrition) in 6 days = 10 silver a day; our
    # Ambrosyx is its exact twin (same 4 x 15 in 6) and a vanilla special, not a crop to farm.
    "RM_AmbrosyxFungus": (("E1",), "vanilla special twin: Plant_Ambrosia is 10 silver per grow day"),
    # Never sown and in no biome's wildPlants: Pyrelands' FireEcologyHook (Patch_FireTick_AshAndScorchFruit) spawns it
    # only on a burning cell, it ripens on the heat and rots in a day. Its 5 fruit are the reward of ONE fire, so a
    # per-grow-day rate (0.05 days) measures nothing.
    "RM_FE_Plant_ScorchFruit": (("E1", "E2"), "fire-spawned event plant: its yield is per fire, not per grow day"),
}


# ------------------------------------------------------------------ XML loading and inheritance
def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, UnicodeDecodeError, OSError):
        return None


def _skip_path(p):
    q = p.replace("\\", "/")
    # an older version folder is not what 1.6 loads
    return bool(re.search(r"/1\.[0-5]/", q)) or "/Transient/" in q


def load_defs(paths, origin):
    """Return (named, concrete): Name -> element for parents, (type, defName) -> (element, path) for concrete defs."""
    named, concrete = {}, {}
    for p in paths:
        if _skip_path(p):
            continue
        r = _parse(p)
        if r is None or r.tag != "Defs":
            continue
        for el in r:
            if not isinstance(el.tag, str):
                continue
            nm = el.get("Name")
            if nm:
                named[(el.tag, nm)] = (el, p, origin)
                named.setdefault(("*", nm), (el, p, origin))
            dn = el.findtext("defName")
            if dn and el.get("Abstract", "").lower() != "true":
                concrete.setdefault((el.tag, dn.strip()), []).append((el, p, origin))
    return named, concrete


def _merge(parent, child):
    """RimWorld XmlInheritance: child overrides; <li> children append unless Inherit="False"."""
    out = copy.deepcopy(parent)
    out.attrib = dict(child.attrib)
    if child.get("Inherit", "").lower() == "false":
        return copy.deepcopy(child)
    kids = [k for k in child if isinstance(k.tag, str)]
    if not kids:
        # a leaf replaces the parent's node whole; an empty one (<harvestedThingDef></harvestedThingDef>) clears it
        return copy.deepcopy(child)
    if all(k.tag == "li" for k in kids):
        for k in kids:
            out.append(copy.deepcopy(k))
        return out
    for k in kids:
        existing = out.find(k.tag)
        if existing is None or k.tag == "li":
            out.append(copy.deepcopy(k))
        else:
            idx = list(out).index(existing)
            out.remove(existing)
            out.insert(idx, _merge(existing, k))
    return out


def resolve(el, named, seen=None):
    seen = seen or set()
    pn = el.get("ParentName")
    if not pn:
        return el, []
    if pn in seen:
        return el, ["cycle at " + pn]
    seen.add(pn)
    hit = named.get((el.tag, pn)) or named.get(("*", pn))
    if hit is None:
        return el, [pn]
    parent, missing = resolve(hit[0], named, seen)
    return _merge(parent, el), missing


def ancestors(el, named):
    """Every Name up the ParentName chain (its own Name included)."""
    out, seen = [], set()
    while el is not None:
        if el.get("Name"):
            out.append(el.get("Name"))
        pn = el.get("ParentName")
        if not pn or pn in seen:
            break
        seen.add(pn)
        hit = named.get((el.tag, pn)) or named.get(("*", pn))
        el = hit[0] if hit else None
    return out


# ------------------------------------------------------------------ patches on plant fields
# RimWorld applies every patch to the RAW def XML and only then resolves inheritance (LoadedModManager: ApplyPatches
# before ParseAndProcessXML/XmlInheritance.Resolve). So a patch on a child's plant/visualSizeRange misses when the
# child only inherits that field, and a patch on a parent reaches its children. The census does the same: patches go
# onto the raw elements, then every def is resolved.
_XP = re.compile(r'^/?Defs/ThingDef\[(?P<cond>[^\]]+)\]/plant(?:/(?P<field>[A-Za-z]+))?\s*$')
_COND = re.compile(r'^\s*defName\s*=\s*"[^"]+"(\s+or\s+defName\s*=\s*"[^"]+")*\s*$')
READ_FIELDS = ("growDays", "harvestYield", "harvestedThingDef", "visualSizeRange", "harvestTag")
ECON_WORDS = READ_FIELDS + ("statBases", "MarketValue", "Nutrition", "stuffProps")
_DN = re.compile(r'defName\s*=\s*"([^"]+)"')
_ANYNAME = re.compile(r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']')
CONTAINERS = ("PatchOperationSequence",)
LOGIC_OPS = ("PatchOperationSequence", "PatchOperationConditional", "PatchOperationFindMod")


def _vals(val):
    """Every tag at any depth under a patch <value>."""
    return set() if val is None else {e.tag for e in val.iter() if isinstance(e.tag, str)}


def _touches_economy(xp, val, short=""):
    """Does this op change a number the census reads: a plant field, a product's MarketValue/Nutrition, or Woody-ness?"""
    if "ThingDef" not in xp:
        return False
    if short.endswith(("Remove", "AttributeSet", "AttributeAdd", "AttributeRemove", "Insert", "SetName")) and (
            re.search(r"(/plant|/statBases|/stuffProps|/categories|\])\s*$", xp)):
        return True        # removing or re-parenting a whole block can expose an inherited, off-bar value
    if any(w in xp for w in READ_FIELDS + ("MarketValue", "Nutrition")):
        return True
    tags = _vals(val)
    if re.search(r"/plant\s*$", xp):
        return bool(tags & set(READ_FIELDS))
    if re.search(r"/statBases\s*$", xp):
        return bool(tags & {"MarketValue", "Nutrition"})
    if "stuffProps" in xp:
        return "categories" in xp or "Woody" in "".join((e.text or "") for e in (val.iter() if val is not None else []))
    if re.search(r"\]\s*$", xp):         # an op on the whole def
        return bool(tags & ({"plant", "MarketValue", "Nutrition", "stuffProps"} | set(READ_FIELDS)))
    return False


_CONDXP = re.compile(r'^/?Defs/ThingDef\[(?P<cond>[^\]]+)\](?P<path>(/[A-Za-z]+)*)\s*$')


def collect_plant_patches(paths, exists=None):
    """Return (handled, unhandled).

    handled:   [(defName, field, op_class, value_element, path)]: a plain Replace/Add, at top level or in a Sequence, whose
               xpath is /Defs/ThingDef[defName="X" (or defName="Y")...]/plant[/<field>].
    unhandled: [(names, path, why)]: any other op that touches a field the census reads (a conditional or FindMod
               branch, an xpath predicate it does not evaluate, a stat or product patch, a whole-plant op...). The
               names it mentions become UNMEASURED; with no name readable, the whole census is.
    """
    handled, unhandled = [], []

    def branch(sb, path, g):
        # a branch is either one op (<match Class="...">) or a list of <li Class="..."> ops; walk each op ONCE
        if sb.get("Class"):
            walk(sb, path, g)
        else:
            for li in sb:
                walk(li, path, g)

    def walk(op, path, guarded):
        if not isinstance(op.tag, str):
            return
        cls = op.get("Class", "")
        short = cls.split(".")[-1]
        xp = (op.findtext("xpath") or "").strip()
        val = op.find("value")
        if "RosterDef" in xp or "notTrees" in xp or "treeRulesExempt" in xp:
            unhandled.append((set(), path, "patch on the ExplosiveGrowth roster (E3's notTrees/treeRulesExempt)"))
        if short in LOGIC_OPS:
            branches = ("operations", "match", "nomatch")
            if short == "PatchOperationConditional" and exists is not None:
                cm = _CONDXP.match(xp)
                hit = exists(cm.group("cond"), cm.group("path")) if cm and _COND.match(cm.group("cond")) else None
                if hit is not None:
                    # an evaluable condition on our own defs: walk only the branch the game would take
                    sb = op.find("match" if hit else "nomatch")
                    if sb is not None:
                        branch(sb, path, guarded)
                    return
            g = guarded or short not in CONTAINERS
            for sub in branches:
                sb = op.find(sub)
                if sb is not None:
                    branch(sb, path, g)
            return
        if not xp or not _touches_economy(xp, val, short):
            return
        m = _XP.match(xp)
        whole_plant_replace = m is not None and not m.group("field") and short == "PatchOperationReplace"
        ok = (m is not None and _COND.match(m.group("cond")) and not guarded and val is not None
              and short in ("PatchOperationReplace", "PatchOperationAdd") and not whole_plant_replace)
        if ok:
            prepend = (op.findtext("order") or "").strip().lower() == "prepend"
            kind = short + ("Prepend" if prepend else "")
            for dn in _DN.findall(m.group("cond")):
                if m.group("field"):
                    handled.append((dn, m.group("field"), kind, val, path))
                else:
                    for k in val:
                        if isinstance(k.tag, str) and k.tag in READ_FIELDS:
                            one = ET.Element("value")
                            one.append(copy.deepcopy(k))
                            handled.append((dn, k.tag, "PlantLevel" + short, one, path))
        else:
            why = "guarded (conditional/FindMod)" if guarded else "%s on %s not evaluated" % (short or "op", xp)
            unhandled.append((set(_ANYNAME.findall(xp)), path, why))

    for p in paths:
        if _skip_path(p):
            continue
        r = _parse(p)
        if r is None or r.tag != "Patch":
            continue
        for op in r:
            walk(op, p, False)
    return handled, unhandled


def apply_patch(el, field, cls, val):
    """Apply one handled op to a RAW def element (before inheritance). A target that is not there is a miss, as in game."""
    plant = el.find("plant")
    if plant is None:
        return False
    target = plant.find(field)
    if cls.startswith("PlantLevel"):
        if cls.endswith("Replace"):
            return False                       # Replace on /plant replaces the whole block: never handled (see above)
        for k in val:                          # Add on /plant appends; a second same-named child: the later one is read
            if target is not None:
                plant.remove(target)
            plant.append(copy.deepcopy(k))
        return True
    if target is None:
        return False
    if "Replace" in cls:
        idx = list(plant).index(target)
        plant.remove(target)
        for k in val:
            if isinstance(k.tag, str):
                plant.insert(idx, copy.deepcopy(k))
                idx += 1
        return True
    # Add on a field node appends the value's children, TEXT included (<value>0</value> onto 1 reads 10)
    if (val.text or "").strip():
        if cls.endswith("Prepend"):
            target.text = val.text.strip() + (target.text or "")
        else:
            target.text = (target.text or "") + val.text.strip()
    for k in val:
        if isinstance(k.tag, str):
            target.append(copy.deepcopy(k))
    return True


# ------------------------------------------------------------------ numbers
class Malformed(ValueError):
    pass


def _f(el, path, default=None):
    t = el.findtext(path)
    if t is None or not t.strip():
        return default
    try:
        v = float(t.strip())
    except ValueError:
        raise Malformed("%s=%r is not a number" % (path, t.strip()))
    if not math.isfinite(v):
        raise Malformed("%s=%r is not finite" % (path, t.strip()))
    return v


def _range_max(el, path):
    t = el.findtext(path)
    if not t or not t.strip():
        return None
    parts = re.split(r"~", t.strip())
    try:
        v = float(parts[-1])
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def _stat(el, stat):
    sb = el.find("statBases")
    if sb is None:
        return None
    v = sb.findtext(stat)
    if v is None or not v.strip():
        return None
    try:
        f = float(v)
    except ValueError:
        raise Malformed("statBases/%s=%r is not a number" % (stat, v.strip()))
    if not math.isfinite(f):
        raise Malformed("statBases/%s=%r is not finite" % (stat, v.strip()))
    return f


class Products:
    """Market value, nutrition and woodiness of a harvest product: our XML, then Ludeon XML, then the dump."""

    def __init__(self, named, concrete, dump_path):
        self.named, self.concrete = named, concrete
        self.dump = None
        if dump_path and os.path.exists(dump_path):
            try:
                self.dump = sqlite3.connect("file:%s?mode=ro" % dump_path, uri=True)
            except sqlite3.Error:
                self.dump = None
        self.cache = {}

    def get(self, name):
        if name in self.cache:
            return self.cache[name]
        hits = self.concrete.get(("ThingDef", name))
        res = None
        if hits:
            el, pmiss = resolve(hits[-1][0], self.named)
            cats = [li.text.strip() for li in el.findall("stuffProps/categories/li") if li.text]
            try:
                mv, nu = _stat(el, "MarketValue"), _stat(el, "Nutrition")
            except Malformed as e:
                mv, nu, pmiss = None, None, pmiss + [str(e)]
            res = {"mv": mv, "nu": nu, "woody": "Woody" in cats, "src": "xml", "missing": pmiss}
            if res["mv"] is None and self.dump is not None:
                d = self._dump(name)
                if d:
                    res["mv"] = d["mv"]
                    res["src"] = "xml+dump"
                    if res["nu"] is None:
                        res["nu"] = d["nu"]
        elif self.dump is not None:
            res = self._dump(name)
        self.cache[name] = res
        return res

    def _dump(self, name):
        row = self.dump.execute("select json from defs where def_type='ThingDef' and def_name=?", (name,)).fetchone()
        if not row:
            return None
        f = json.loads(row[0]).get("fields", {})
        mv = nu = None
        for m in f.get("statBases") or []:
            if m.get("stat") == "MarketValue":
                mv = m.get("value")
            if m.get("stat") == "Nutrition":
                nu = m.get("value")
        cats = (f.get("stuffProps") or {}).get("categories") or []
        return {"mv": mv, "nu": nu, "woody": "Woody" in cats, "src": "dump"}


def roster_lists(path):
    r = _parse(path)
    out = {"notTrees": set(), "treeRulesExempt": set(), "fungi": set()}
    if r is None:
        return out
    for k in out:
        for li in r.iter(k):
            out[k].update((x.text or "").strip() for x in li.findall("li") if (x.text or "").strip())
    return out


# ------------------------------------------------------------------ the census
def census(game_data=None, dump_path=None):
    our_paths = []
    for t in OUR_TIERS:
        our_paths += glob.glob(os.path.join(ROOT, t, "**", "*.xml"), recursive=True)
    game_data = game_data or next((g for g in GAME_DATA_CANDIDATES if os.path.isdir(g)), None)
    lud_paths = glob.glob(os.path.join(game_data, "*", "Defs", "**", "*.xml"), recursive=True) if game_data else []
    lud_named, lud_concrete = load_defs(lud_paths, "ludeon")
    our_named, our_concrete = load_defs(our_paths, "ours")
    named = dict(lud_named)
    named.update(our_named)
    concrete = dict(lud_concrete)
    concrete.update(our_concrete)
    dump_path = dump_path or next((d for d in DUMP_CANDIDATES if os.path.exists(d)), None)
    # patches first, onto the raw elements (see the patch section): parents and children are the same objects
    def exists(cond, sub):
        """Does /Defs/ThingDef[cond]<sub> match any raw def? None = cannot say."""
        found = False
        for dn in _DN.findall(cond):
            for el, _p, _o in concrete.get(("ThingDef", dn), []):
                if not sub or el.find(sub.strip("/")) is not None:
                    found = True
        return found

    handled, unhandled = collect_plant_patches(our_paths, exists)
    applied = 0
    for dn, field, cls, val, p in handled:
        for el, _p, _o in our_concrete.get(("ThingDef", dn), []):
            applied += bool(apply_patch(el, field, cls, val))
    blind_names, blind_global = set(), []
    for names, p, why in unhandled:
        if names:
            blind_names |= names
        else:
            blind_global.append("%s: %s" % (os.path.relpath(p, REPO), why))
    prods = Products(named, concrete, dump_path)
    lists = roster_lists(ROSTER)
    roster_ok = os.path.isfile(ROSTER) and _parse(ROSTER) is not None
    our_files = [p for p in our_paths if not _skip_path(p)]
    parse_failures = [os.path.relpath(p, REPO) for p in our_files if _parse(p) is None]

    rows = []
    copies = [(tag, dn, el, path) for (tag, dn), lst in sorted(our_concrete.items()) for (el, path, _o) in lst]
    for tag, dn, el, path in copies:
        if tag != "ThingDef":
            continue
        res, missing = resolve(el, named)
        if res.find("plant") is None:
            unknown = [m for m in missing if m not in KNOWN_NONPLANT_PARENTS]
            if unknown:
                # its parent is not in our tree or the base game, so we cannot tell whether it is a plant
                rows.append({"defName": dn, "path": os.path.relpath(path, REPO), "growDays": 0, "harvestYield": 0,
                             "product": None, "visualMax": 0, "flags": [], "excepted": None,
                             "unmeasured": ["a ThingDef whose parent %s is not found: is it a plant?" % ",".join(unknown)]})
            continue
        bad = []
        try:
            g = _f(res, "plant/growDays", 2.0)        # PlantProperties.growDays default 2
        except Malformed as e:
            g, bad = 0.0, bad + [str(e)]
        try:
            y = _f(res, "plant/harvestYield", 0.0)
        except Malformed as e:
            y, bad = 1.0, bad + [str(e)]
        h = (res.findtext("plant/harvestedThingDef") or "").strip()
        vis = _range_max(res, "plant/visualSizeRange")
        if vis is None:
            vis = 1.1                                   # PlantProperties.visualSizeRange default 0.9~1.1
        row = {"defName": dn, "path": os.path.relpath(path, REPO), "growDays": g, "harvestYield": y,
               "product": h or None, "visualMax": vis, "flags": [], "unmeasured": [], "excepted": None}
        if missing:
            row["unmeasured"].append("parent not found: " + ",".join(missing))
        row["unmeasured"] += bad
        prod_chain = []
        if h:
            for pel, _p, _o in concrete.get(("ThingDef", h), [])[-1:]:
                prod_chain = ancestors(pel, named)
        if blind_names & ({dn, h} | set(ancestors(el, named)) | set(prod_chain)):
            row["unmeasured"].append("a patch touching it (or its product) is not evaluated by the census")
        if (res.findtext("plant/visualSizeRange") or "").strip() and _range_max(res, "plant/visualSizeRange") is None:
            row["unmeasured"].append("plant/visualSizeRange is not a range")
        if h and y > 0:
            pr = prods.get(h)
            if pr is None:
                row["unmeasured"].append("product %s not found" % h)
            elif pr.get("missing"):
                row["unmeasured"].append("product %s not resolvable: %s" % (h, ",".join(pr["missing"])))
            else:
                wood = h in WOOD_TAGS or pr.get("woody")
                row["wood"] = bool(wood)
                mv, nu = pr.get("mv"), pr.get("nu")
                if mv is None:
                    row["unmeasured"].append("product %s has no MarketValue" % h)
                if g <= 0:
                    row["unmeasured"].append("growDays <= 0")
                else:
                    row["valuePerDay"] = round(y * (mv or 0) / g, 3)
                    row["nutritionPerDay"] = round(y * (nu or 0) / g, 4)
                    if mv is not None and y * mv / g > VALUE_PER_GROWDAY_MAX + 1e-9:
                        row["flags"].append("E1 value %.2f/day > %.2f" % (y * mv / g, VALUE_PER_GROWDAY_MAX))
                    if nu and y * nu / g > NUTRITION_PER_GROWDAY_MAX + 1e-9:
                        row["flags"].append("E2 nutrition %.3f/day > %.3f" % (y * nu / g, NUTRITION_PER_GROWDAY_MAX))
                    if wood:
                        if dn not in lists["treeRulesExempt"]:
                            if vis < TREE_MIN_VISUAL:
                                row["flags"].append("E3 wood from a plant drawn %.2f (< %.1f, Q3)" % (vis, TREE_MIN_VISUAL))
                            if dn in lists["notTrees"]:
                                row["flags"].append("E3 wood from a ruled not-a-tree")
                        if y / g > LOGS_PER_GROWDAY_MAX + 1e-9:
                            row["flags"].append("E4 logs %.2f/day > %.1f" % (y / g, LOGS_PER_GROWDAY_MAX))
        ex = EXCEPTIONS.get(dn)
        if ex:
            kept = [f for f in row["flags"] if not f.startswith(tuple(ex[0]))]
            if len(kept) != len(row["flags"]):
                row["excepted"] = ex[1]
            row["flags"] = kept
        rows.append(row)
    if not roster_ok:
        # E3's <notTrees> and <treeRulesExempt> come from the roster: without it a wood row cannot be judged
        for row in rows:
            if row.get("wood"):
                row["unmeasured"].append("ExplosiveGrowth roster not readable: %s" % ROSTER)
    meta = {"game_data": game_data, "roster_ok": roster_ok, "parse_failures": parse_failures,
            "blind_global": blind_global, "patches_applied": applied, "patches_unhandled": len(unhandled), "dump": dump_path, "ludeon_xml_files": len(lud_paths), "our_xml_files": len(our_paths),
            "plant_patches": len(handled)}
    return rows, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--game-data")
    ap.add_argument("--dump")
    a = ap.parse_args(argv)
    rows, meta = census(a.game_data, a.dump)
    if not meta["game_data"] or meta["ludeon_xml_files"] == 0:
        print("UNMEASURED: base game Data folder not found (needed for PlantBase/TreeBase and WoodLog)")
        return 2
    off = [r for r in rows if r["flags"]]
    unm = [r for r in rows if r["unmeasured"]]
    blind = list(meta["blind_global"]) + ["XML that does not parse: %s" % p for p in meta["parse_failures"]]
    missing_tiers = [t for t in OUR_TIERS if not os.path.isdir(os.path.join(ROOT, t))]
    if missing_tiers:
        blind.append("tier folder missing: %s" % ",".join(missing_tiers))
    if len(rows) < MIN_PLANTS:
        blind.append("only %d plant defs seen (< %d): the census is not looking at our tree" % (len(rows), MIN_PLANTS))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "rows": rows}, fh, indent=1)
    print("bar: E1 value <= %.2f/growDay  E2 nutrition <= %.3f/growDay  E3 wood only from trees (drawn >= %.1f, "
          "not notTrees)  E4 logs <= %.1f/growDay   (design/RimMandrake/plant_economy_rule_2026-11-01.md)"
          % (VALUE_PER_GROWDAY_MAX, NUTRITION_PER_GROWDAY_MAX, TREE_MIN_VISUAL, LOGS_PER_GROWDAY_MAX))
    for r in rows if a.all else off + [r for r in unm if r not in off]:
        print("%-34s g=%-6g y=%-5g %-26s vis=%-5g %s%s" % (
            r["defName"], r["growDays"], r["harvestYield"], r["product"] or "-", r["visualMax"],
            "; ".join(r["flags"]) or ("ok" if not r["unmeasured"] else ""),
            (" UNMEASURED: " + "; ".join(r["unmeasured"])) if r["unmeasured"] else ""))
    for b in blind:
        print("UNMEASURED (whole census): " + b)
    with_harvest = sum(1 for r in rows if r["product"] and r["harvestYield"] > 0)
    print("%d plant defs (%d with a harvest; %d plant-field patches, %d applied, %d not evaluated; %d excepted): "
          "%d off-rule, %d unmeasured%s"
          % (len(rows), with_harvest, meta["plant_patches"], meta["patches_applied"], meta["patches_unhandled"],
             sum(1 for r in rows if r["excepted"]), len(off), len(unm) + (1 if blind else 0),
             " (whole census blind)" if blind else ""))
    if a.check:
        return 0 if not off and not unm and not blind else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
