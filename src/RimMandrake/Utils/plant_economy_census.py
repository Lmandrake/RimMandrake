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
DUMP_CANDIDATES = [
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite",
]

# ---- the bar (design/RimMandrake/plant_economy_rule_2026-11-01.md §2; keep the two in step) ----
VALUE_PER_GROWDAY_MAX = 4.0       # E1: silver of harvest per grow day; vanilla ordinary max Plant_TreeCocoa 3.75
NUTRITION_PER_GROWDAY_MAX = 0.135  # E2: nutrition per grow day; vanilla max Plant_Ambrosia 0.133, Plant_Haygrass 0.129
LOGS_PER_GROWDAY_MAX = 3.0        # E4: wood per grow day; vanilla Plant_SaguaroCactus / Plant_TreePolux 3.0
TREE_MIN_VISUAL = 3.0             # E3: Q2 "SIZE 3.0+ ONLY" (tree_burst_design_2026-10-17.md §2)
WOOD_TAGS = ("WoodLog",)

# Per-def allowances. Each needs a reason a reader can check; keep this list short.
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
    if not pn or pn in seen:
        return el, []
    seen.add(pn)
    hit = named.get((el.tag, pn)) or named.get(("*", pn))
    if hit is None:
        return el, [pn]
    parent, missing = resolve(hit[0], named, seen)
    return _merge(parent, el), missing


# ------------------------------------------------------------------ patches on plant fields
_XP = re.compile(r'^/?Defs/ThingDef\[(?P<cond>[^\]]+)\]/plant(?:/(?P<field>[A-Za-z]+))?\s*$')
READ_FIELDS = ("growDays", "harvestYield", "harvestedThingDef", "visualSizeRange", "harvestTag")
_DN = re.compile(r'defName\s*=\s*"([^"]+)"')


def collect_plant_patches(paths):
    """[(defName, field, op_class, value_element, path)] for Replace/Add ops on /Defs/ThingDef[...]/plant/<field>."""
    out = []

    def walk(op, path):
        if not isinstance(op.tag, str):
            return
        cls = op.get("Class", "")
        xp = (op.findtext("xpath") or "").strip()
        m = _XP.match(xp)
        if m and cls.endswith(("PatchOperationReplace", "PatchOperationAdd")):
            val = op.find("value")
            if val is not None:
                for dn in _DN.findall(m.group("cond")):
                    if m.group("field"):
                        out.append((dn, m.group("field"), cls, val, path))
                    else:
                        # an op on /plant itself: each child of <value> it sets that we read is a field op of its own
                        for k in val:
                            if isinstance(k.tag, str) and k.tag in READ_FIELDS:
                                one = ET.Element("value")
                                one.append(copy.deepcopy(k))
                                out.append((dn, k.tag, "PlantLevel" + cls.split(".")[-1], one, path))
        for sub in ("operations", "match", "nomatch"):
            s = op.find(sub)
            if s is None:
                continue
            if s.get("Class"):
                walk(s, path)
            for li in s:
                walk(li, path)

    for p in paths:
        if _skip_path(p):
            continue
        r = _parse(p)
        if r is None or r.tag != "Patch":
            continue
        for op in r:
            walk(op, p)
    return out


def apply_patch(el, field, cls, val, defname):
    plant = el.find("plant")
    if plant is None:
        return
    target = plant.find(field)
    if cls.startswith("PlantLevel"):
        # Add/Replace on <plant>: the new child replaces any same-named one (two would be a load error, last wins)
        if target is not None:
            plant.remove(target)
        for k in val:
            plant.append(copy.deepcopy(k))
        return
    if cls.endswith("PatchOperationReplace"):
        if target is None:
            return
        idx = list(plant).index(target)
        plant.remove(target)
        for k in val:
            if isinstance(k.tag, str):
                plant.insert(idx, copy.deepcopy(k))
                idx += 1
    else:   # Add: appends the value's children to the matched node
        if target is None:
            return
        for k in val:
            if isinstance(k.tag, str):
                target.append(copy.deepcopy(k))


# ------------------------------------------------------------------ numbers
def _f(el, path, default=None):
    t = el.findtext(path)
    if t is None or not t.strip():
        return default
    try:
        return float(t.strip())
    except ValueError:
        return default


def _range_max(el, path):
    t = el.findtext(path)
    if not t or not t.strip():
        return None
    parts = re.split(r"~", t.strip())
    try:
        return float(parts[-1])
    except ValueError:
        return None


def _stat(el, stat):
    sb = el.find("statBases")
    if sb is None:
        return None
    v = sb.findtext(stat)
    try:
        return float(v) if v is not None and v.strip() else None
    except ValueError:
        return None


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
            el, _ = resolve(hits[-1][0], self.named)
            cats = [li.text.strip() for li in el.findall("stuffProps/categories/li") if li.text]
            res = {"mv": _stat(el, "MarketValue"), "nu": _stat(el, "Nutrition"), "woody": "Woody" in cats,
                   "src": "xml"}
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
    prods = Products(named, concrete, dump_path)
    patches = collect_plant_patches(our_paths)
    by_def = {}
    for dn, field, cls, val, p in patches:
        by_def.setdefault(dn, []).append((field, cls, val))
    lists = roster_lists(ROSTER)

    rows = []
    copies = [(tag, dn, el, path) for (tag, dn), lst in sorted(our_concrete.items()) for (el, path, _o) in lst]
    for tag, dn, el, path in copies:
        if tag != "ThingDef":
            continue
        res, missing = resolve(el, named)
        if res.find("plant") is None:
            continue
        for field, cls, val in by_def.get(dn, []):
            apply_patch(res, field, cls, val, dn)
        g = _f(res, "plant/growDays", 2.0)            # PlantProperties.growDays default 2
        y = _f(res, "plant/harvestYield", 0.0)
        h = (res.findtext("plant/harvestedThingDef") or "").strip()
        vis = _range_max(res, "plant/visualSizeRange")
        if vis is None:
            vis = 1.0                                   # PlantProperties.visualSizeRange default 0.9~1.1 -> ~1
        row = {"defName": dn, "path": os.path.relpath(path, REPO), "growDays": g, "harvestYield": y,
               "product": h or None, "visualMax": vis, "flags": [], "unmeasured": [], "excepted": None}
        if missing:
            row["unmeasured"].append("parent not found: " + ",".join(missing))
        if h and y > 0:
            pr = prods.get(h)
            if pr is None:
                row["unmeasured"].append("product %s not found" % h)
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
    meta = {"game_data": game_data, "dump": dump_path, "ludeon_xml_files": len(lud_paths), "our_xml_files": len(our_paths),
            "plant_patches": len(patches)}
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
    with_harvest = sum(1 for r in rows if r["product"] and r["harvestYield"] > 0)
    print("%d plant defs (%d with a harvest; %d plant patches; %d excepted): %d off-rule, %d unmeasured"
          % (len(rows), with_harvest, meta["plant_patches"], sum(1 for r in rows if r["excepted"]), len(off), len(unm)))
    if a.check:
        return 0 if not off and not unm else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
