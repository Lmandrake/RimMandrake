#!/usr/bin/env python3
"""junk_spawn_census.py - static census of the ThingDefs map generation can lay down as outdoor
junk / wreck / ruin scatter on an ordinary surface map of ours.        (item FASCINATING_WORLD_JUNK_1)

Reads, never runs the game:
  * vanilla GenStepDefs that place junk (Core/Ideology/Biotech/Odyssey CommonMapGenerator.xml) -
    ScatterGroup things, ScatterThings thingDef, ScatterGroupPrefabs prefab contents (recursive);
  * a hand table (HARDCODED below) for C# GenSteps whose defs live in code, one row per def with
    the method its IL names it in;
  * our sources: StructureInjectionsRUT zeddos_yard.txt THING lines and every GenStepDef under
    src/RimUtinni/UtinniPatches/Defs/MapGeneration (non-junk ones are reported apart, not in "all").
--apply-patch FILE (repeatable) applies the PatchOperationRemove ops of a patch file to the parsed
vanilla GenStepDefs first (plain, inside PatchOperationSequence / PatchOperationConditional, or inside
any custom Operation whose <match> holds them). Only three xpath shapes are understood; any other
shape or any other op class is refused (exit 3).

Output: --json prints {source: [defNames], "all": [...], "unresolved": [...], ...}.
--roster FILE diffs the spawnable set against junk_roster.json ({"kinds":[{"defs":[..]}],"cut":[{"def":..}]}).
Exit 0 ok, 1 roster failures, 2 sanity probe failed (AncientTank not seen unpatched), 3 refused patch.

Game data: --data DIR, else $RIMWORLD_DATA, else the Steam library default below.
"""
import argparse
import copy
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_DATA = "/mnt/d/SteamLibrary/steamapps/common/RimWorld/Data"
PACKAGES = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

# The vanilla junk GenSteps (CommonMapGenerator genSteps list, plus Odyssey's Scarlands pair).
VANILLA_STEPS = [
    "ScatterRuinsSimple", "ScatterRoadDebris", "ScatterCaveDebris", "AncientUtilityBuilding",
    "MechanoidRemains", "AncientTurret", "AncientMechs", "AncientLandingPad", "AncientFences",
    "AncientPipelineSection", "AncientJunkClusters", "AncientPollutionJunk",
    "ScarlandsJunkClusters", "ScarlandsJunkPrefabs",
]

# C# GenSteps that hard-code what they place. Read from Assembly-CSharp.dll IL (ldsfld of
# ThingDefOf.* inside the named method; RimSage was not reachable on the reading host, so the
# citation is the class.method, not file:line). Read 2026-11-11 against RimWorld 1.6.
# value: list of (defName, citation, note)
HARDCODED = {
    "GenStep_ScatterRoadDebris": [
        # only when the map has AncientAsphaltRoad / AncientAsphaltHighway (HasAncientRoads)
        ("AncientRustedCarFrame", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientRustedJeep", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientRustedCar", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientTank", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientPodCar", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientHydrant", "GenStep_ScatterRoadDebris.<get_Debris>d__11.MoveNext", ""),
        ("AncientLargeRustedEngineBlock", "GenStep_ScatterRoadDebris.ScatterAt", ""),
        ("AncientRustedEngineBlock", "GenStep_ScatterRoadDebris.ScatterAt", ""),
    ],
    "GenStep_ScatterCaveDebris": [
        # bed with a Drifter corpse, under mountain roof (caves of a surface map)
        ("AncientBed", "GenStep_ScatterCaveDebris.ScatterAt", "roofed cave, not open ground"),
    ],
    "GenStep_ScatterAncientTurret": [
        ("AncientSecurityTurret", "GenStep_ScatterAncientTurret.ScatterAt", ""),
    ],
    "GenStep_ScatterAncientMechs": [
        ("AncientWarwalkerTorso", "GenStep_ScatterAncientMechs.<get_MechThingDefs>d__4.MoveNext", ""),
        ("AncientMiniWarwalkerRemains", "GenStep_ScatterAncientMechs.<get_MechThingDefs>d__4.MoveNext", ""),
        ("AncientWarspiderRemains", "GenStep_ScatterAncientMechs.<get_MechThingDefs>d__4.MoveNext", ""),
        ("AncientWarwalkerFoot", "GenStep_ScatterAncientMechs.<get_MechThingDefs>d__4.MoveNext", ""),
        ("AncientWarwalkerLeg", "GenStep_ScatterAncientMechs.ScatterAt", "parts laid around the torso"),
        ("AncientWarwalkerClaw", "GenStep_ScatterAncientMechs.ScatterAt", "parts laid around the torso"),
    ],
    "GenStep_ScatterAncientFences": [
        ("AncientFence", "GenStep_ScatterAncientFences.CanScatterAt", ""),
        ("AncientRazorWire", "GenStep_ScatterAncientFences.CanScatterAt", ""),
    ],
    "GenStep_ScatterAncientLandingPad": [
        # SketchResolverDefOf.AncientLandingPad -> SketchResolver_AncientLandingPad.ResolveInt
        ("AncientShipBeacon", "SketchResolver_AncientLandingPad.ResolveInt", "terrain AncientConcrete not counted"),
    ],
    "GenStep_ScatterAncientUtilityBuilding": [
        # SketchResolverDefOf.AncientUtilityBuilding -> SketchResolver_AncientUtilityBuilding.ResolveInt
        ("AncientFence", "SketchResolver_AncientUtilityBuilding.ResolveInt", ""),
        ("AncientGenerator", "SketchResolver_AncientUtilityBuilding.ResolveInt", ""),
        ("Table1x2c", "SketchResolver_AncientUtilityBuilding.ResolveInt", "via AddWallEdgeThings"),
        ("Wall", "LayoutSketch.get_WallThing", "RoomLayoutGenerator layout flushed with LayoutSketch defaults"),
        ("Door", "LayoutSketch.get_DoorThing", "RoomLayoutGenerator layout flushed with LayoutSketch defaults"),
    ],
    "GenStep_ScatterRuinsSimple": [
        # ScatterAt resolves SketchResolverDefOf.MonumentRuin only; MonumentRuin -> Monument (+DamageBuildings)
        ("Drape", "SketchResolver_MonumentRuin.ResolveInt", ""),
        ("Wall", "SketchResolver_Monument.ResolveInt", "random stuff (AssignRandomStuff)"),
        ("Door", "SketchResolver_Monument.ResolveInt", ""),
        ("Column", "SketchResolver_Monument.ResolveInt", "also SketchResolver_AddColumns"),
        ("Urn", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        ("SteleLarge", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        ("SteleGrand", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        ("Table1x2c", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        ("Table2x2c", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        ("Sarcophagus", "SketchResolver_Monument.TryPlaceFurniture", "furniture: placement conditional"),
        # ThingDefOf.WoodLog also appears in SketchResolver_Monument.ResolveInt: a stuff, not placed.
    ],
}
# What the hand table could not pin down statically (reported, never dropped).
HARDCODED_UNRESOLVED = {
    "GenStep_ScatterRuinsSimple": "SketchResolver_Monument furniture branch conditions and "
                                  "AddInnerMonuments recursion not evaluated; stuff for walls is random",
    "GenStep_ScatterAncientUtilityBuilding": "LayoutSketch wall/door fields may be overridden by the caller; "
                                             "defaults Wall/Door assumed",
}

# Our GenStepDefs that place something other than junk/wreck/ruin scatter: kept out of "all".
OUR_NONJUNK = {
    "RUT_ContagionRingScatter": "filth band, no things",
    "RUT_FoundryFloor": "no genStep body",
    "RUT_FoundryFloor_MeltChannels": "terrain channels",
    "RUT_FoundryFloor_TenderSpawn": "anchored pawn (Mech_Pikeman)",
    "RUT_FoundryTowerScatter": "structure entrance marker, not scatter junk",
    "RUT_LanternDeepKyberScatter": "kyber crystal formations (resource)",
    "RUT_LanternDeepMindstoneGallery": "mineable veins",
    "RUT_PhrikiteDesertLumps": "mineable lumps",
    "RUT_ZersiumForgeLumps": "mineable lumps",
    "RUT_ScarlandsGraveWardScatter": "sentinel grave wards (hazard)",
    "RUT_Jawa_ScatterWastesBrineTekk": "brine deposit (resource)",
    "RUT_Jawa_ScatterWastesBrineDrazz": "brine deposit (resource)",
    "RUT_Jawa_ScatterWastesBrinePlate": "brine deposit (resource)",
}
# Fields of our custom GenStep classes that name a ThingDef they place (C# not evaluated).
CUSTOM_THING_FIELDS = ("thingDef", "markerDef", "forcedDefToScatter", "veinDef")

OUR_GENSTEP_GLOB = "src/RimUtinni/UtinniPatches/Defs/MapGeneration/*.xml"
ZEDDOS_YARD = "src/RimUtinni/StructureInjectionsRUT/Templates/zeddos_yard.txt"


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"junk_spawn_census: skip unparsable {path}: {e}", file=sys.stderr)
        return None


def load_defs(data):
    """Return (gensteps{name: elem}, prefabs{name: elem}, thingdefs set, our_gensteps{name: elem})."""
    gensteps, prefabs, things, filth = {}, {}, set(), set()
    vanilla_files = []
    for pkg in PACKAGES:
        vanilla_files += sorted(glob.glob(os.path.join(data, pkg, "Defs", "**", "*.xml"), recursive=True))
    our_files = sorted(glob.glob(os.path.join(REPO, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True))
    if not vanilla_files:
        raise SystemExit(f"junk_spawn_census: no vanilla Defs under {data} (set --data or RIMWORLD_DATA)")
    our_steps = {}
    our_step_files = set(os.path.abspath(p) for p in glob.glob(os.path.join(REPO, OUR_GENSTEP_GLOB)))
    for origin, files in (("vanilla", vanilla_files), ("ours", our_files)):
        for f in files:
            root = parse(f)
            if root is None:
                continue
            for d in root:
                name = d.findtext("defName")
                if not name:
                    continue
                if d.tag == "ThingDef":
                    things.add(name)
                    if (d.findtext("category") or "").strip() == "Filth" or name.startswith("Filth_") \
                            or "Filth" in (d.get("ParentName") or ""):
                        filth.add(name)
                elif d.tag == "PrefabDef":
                    prefabs[name] = d
                elif d.tag == "GenStepDef":
                    if origin == "vanilla":
                        gensteps[name] = d
                    elif os.path.abspath(f) in our_step_files:
                        our_steps[name] = d
    return gensteps, prefabs, things | {"__filth__:" + f for f in filth}, our_steps


# ---------------------------------------------------------------- patch application
XP_HEAD = r'^/Defs/GenStepDef\[defName="(?P<step>[^"]+)"\]/genStep/groups'
XP_THING = re.compile(XP_HEAD + r'/li/things/(?P<def>[A-Za-z0-9_]+)$')
XP_EMPTY = re.compile(XP_HEAD + r'/li\[not\(things/\*\)\]$')
XP_GROUP = re.compile(XP_HEAD + r'/(?P<def>[A-Za-z0-9_]+)$')


class Refused(Exception):
    pass


def xpath_targets(xpath, gensteps):
    """Return [(parent, child)] the xpath selects in the parsed GenStepDefs."""
    xp = xpath.strip()
    for rx, kind in ((XP_THING, "thing"), (XP_EMPTY, "empty"), (XP_GROUP, "group")):
        m = rx.match(xp)
        if not m:
            continue
        step = gensteps.get(m.group("step"))
        groups = step.find("genStep/groups") if step is not None else None
        if groups is None:
            return []
        if kind == "thing":
            out = []
            for li in groups.findall("li"):
                things = li.find("things")
                if things is not None:
                    out += [(things, c) for c in things.findall(m.group("def"))]
            return out
        if kind == "empty":
            out = []
            for li in groups.findall("li"):
                things = li.find("things")
                if things is None or len(things) == 0:
                    out.append((groups, li))
            return out
        if m.group("def") == "li":
            raise Refused(f"xpath selects whole groups/li: {xp}")
        return [(groups, c) for c in groups.findall(m.group("def"))]
    raise Refused(f"xpath shape not understood: {xp}")


def apply_op(op, gensteps, report, where):
    cls = op.get("Class", "")
    if cls == "PatchOperationRemove":
        xp = op.findtext("xpath") or ""
        hits = xpath_targets(xp, gensteps)
        for parent, child in hits:
            parent.remove(child)
        report.append({"file": where, "xpath": xp.strip(), "removed": len(hits)})
        return bool(hits)
    if cls == "PatchOperationSequence":
        ok = True
        for li in op.findall("operations/li"):
            ok = apply_op(li, gensteps, report, where) and ok
        return ok
    if cls == "PatchOperationConditional":
        xp = op.findtext("xpath") or ""
        branch = op.find("match") if xpath_targets(xp, gensteps) else op.find("nomatch")
        return apply_op(branch, gensteps, report, where) if branch is not None else True
    if op.find("match") is not None and op.find("xpath") is None:
        # a custom gate Operation (or PatchOperationFindMod; every DLC/mod assumed present)
        return apply_op(op.find("match"), gensteps, report, where)
    raise Refused(f"{where}: operation class {cls or '(none)'} not supported")


def apply_patch_file(path, gensteps, report):
    root = parse(path)
    if root is None:
        raise Refused(f"cannot parse patch {path}")
    for op in root.findall("Operation"):
        apply_op(op, gensteps, report, os.path.basename(path))


# ---------------------------------------------------------------- collection
def expand_prefab(name, prefabs, unresolved, src, seen=None):
    seen = set() if seen is None else seen
    if name in seen:
        return set()
    seen.add(name)
    p = prefabs.get(name)
    if p is None:
        unresolved.append(f"{src}: PrefabDef {name} not found")
        return set()
    out = {c.tag for c in (p.find("things") if p.find("things") is not None else [])}
    for sub in (p.find("prefabs") if p.find("prefabs") is not None else []):
        out |= expand_prefab(sub.tag, prefabs, unresolved, src, seen)
    return out


def collect_step(name, step, prefabs, unresolved, src):
    gs = step.find("genStep")
    if gs is None:
        return set()
    cls = gs.get("Class", "")
    short = cls.rsplit(".", 1)[-1]
    out = set()
    if short == "GenStep_ScatterGroup":
        for li in gs.findall("groups/li"):
            things = li.find("things")
            out |= {c.tag for c in (things if things is not None else [])}
            if li.findtext("spawnAtCenter"):
                out.add(li.findtext("spawnAtCenter").strip())
    elif short == "GenStep_ScatterGroupPrefabs":
        for grp in (gs.find("groups") if gs.find("groups") is not None else []):
            out |= expand_prefab(grp.tag, prefabs, unresolved, src)
    elif short == "GenStep_ScatterThings" or gs.findtext("thingDef"):
        if gs.findtext("thingDef"):
            out.add(gs.findtext("thingDef").strip())
        if short != "GenStep_ScatterThings":
            unresolved.append(f"{src}: custom class {cls}: thingDef field read, C# not evaluated")
    elif short in HARDCODED:
        out |= {d for d, _c, _n in HARDCODED[short]}
        if short in HARDCODED_UNRESOLVED:
            unresolved.append(f"{src}: {HARDCODED_UNRESOLVED[short]}")
    else:
        for f in CUSTOM_THING_FIELDS:
            if gs.findtext(f):
                out.add(gs.findtext(f).strip())
        why = {"GenStep_ScatterShrines": " (BaseGen ancient-shrine symbol resolvers: contents not followed)",
               "RM_GenStep_PlacedSetPieces": " (set-piece elements spawn a marker whose C# places the contents)"
               }.get(short, "")
        unresolved.append(f"{src}: class {cls} not statically resolved{why}"
                          + (f" (fields read: {sorted(out)})" if out else ""))
    return out


def collect(gensteps, prefabs, our_steps, things, unresolved, nonjunk):
    sources = {}
    for name in VANILLA_STEPS:
        step = gensteps.get(name)
        if step is None:
            unresolved.append(f"vanilla:{name}: GenStepDef not found")
            continue
        sources[f"vanilla:{name}"] = collect_step(name, step, prefabs, unresolved, f"vanilla:{name}")
    for name in sorted(our_steps):
        sub_unres = []
        defs = collect_step(name, our_steps[name], prefabs, sub_unres, f"ours:{name}")
        if name in OUR_NONJUNK:
            nonjunk[f"ours:{name}"] = {"reason": OUR_NONJUNK[name], "defs": sorted(defs)}
            continue
        unresolved += sub_unres
        sources[f"ours:{name}"] = defs
    yard = os.path.join(REPO, ZEDDOS_YARD)
    with open(yard, encoding="utf-8") as fh:
        sources["ours:zeddos_yard"] = {ln.split("\t")[1] for ln in fh if ln.startswith("THING\t")}
    filth = {t.split(":", 1)[1] for t in things if t.startswith("__filth__:")}
    for k in sources:  # filth is dirt, not junk: counted apart
        dropped = sources[k] & filth
        if dropped:
            nonjunk.setdefault("filth_in_sources", {})[k] = sorted(dropped)
            sources[k] -= dropped
    unknown = sorted({d for s in sources.values() for d in s} - things)
    for d in unknown:
        unresolved.append(f"{d}: named by a source but no ThingDef of that name was found")
    return {k: sorted(v) for k, v in sources.items()}


def run(data, patches):
    gensteps, prefabs, things, our_steps = load_defs(data)
    # unpatched vanilla first: the sanity probe looks here
    probe_unres, probe_nonjunk = [], {}
    base = collect(copy.deepcopy(gensteps), prefabs, our_steps, things, probe_unres, probe_nonjunk)
    vanilla_seen = {d for k, v in base.items() if k.startswith("vanilla:") for d in v}
    report = []
    for p in patches:
        apply_patch_file(p, gensteps, report)
    unresolved, nonjunk = [], {}
    sources = collect(gensteps, prefabs, our_steps, things, unresolved, nonjunk) if patches else base
    if not patches:
        unresolved, nonjunk = probe_unres, probe_nonjunk
    out = dict(sources)
    out["all"] = sorted({d for v in sources.values() for d in v})
    out["unresolved"] = sorted(set(unresolved))
    out["excluded_nonjunk"] = nonjunk
    if patches:
        out["patch_report"] = report
    return out, vanilla_seen


def roster_diff(out, roster_path, patched):
    with open(roster_path, encoding="utf-8") as fh:
        roster = json.load(fh)
    kept = {d for k in roster.get("kinds", []) for d in k.get("defs", [])}
    cut = {c["def"] for c in roster.get("cut", [])}
    spawn = set(out["all"])
    covered = sorted(spawn & kept)
    on_cut = sorted(spawn & cut)
    absent = sorted(spawn - kept - cut)
    both = sorted(kept & cut)
    print(f"spawnable: {len(spawn)}")
    print(f"covered by a kept kind: {len(covered)}")
    print(f"on the cut list{' (FAILURE: patches applied)' if patched else ' (unpatched: expected)'}: {len(on_cut)}")
    for d in on_cut:
        print(f"  CUT {d}  from {[k for k, v in out.items() if isinstance(v, list) and k not in ('all', 'unresolved') and d in v]}")
    print(f"absent from the roster (FAILURE): {len(absent)}")
    for d in absent:
        print(f"  ABSENT {d}  from {[k for k, v in out.items() if isinstance(v, list) and k not in ('all', 'unresolved') and d in v]}")
    if both:
        print(f"roster names these both kept and cut (FAILURE): {both}")
    for r in out.get("patch_report", []):
        if r["removed"] == 0:
            print(f"  NOTE patch op matched nothing: {r['file']} {r['xpath']}")
    return bool(absent or both or (patched and on_cut))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=os.environ.get("RIMWORLD_DATA", DEFAULT_DATA))
    ap.add_argument("--apply-patch", action="append", default=[], metavar="FILE")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--roster", metavar="junk_roster.json")
    a = ap.parse_args(argv)
    try:
        out, vanilla_seen = run(a.data, a.apply_patch)
    except Refused as e:
        print(f"junk_spawn_census: REFUSED: {e}", file=sys.stderr)
        return 3
    if a.json:
        print(json.dumps(out, indent=1))
    elif not a.roster:
        for k, v in out.items():
            if isinstance(v, list) and k != "unresolved":
                print(f"{k}: {len(v)}")
        print(f"unresolved: {len(out['unresolved'])}")
    fail = roster_diff(out, a.roster, bool(a.apply_patch)) if a.roster else False
    if "AncientTank" not in vanilla_seen:
        print("junk_spawn_census: SANITY FAIL: AncientTank not reachable from unpatched vanilla "
              "(the instrument cannot see)", file=sys.stderr)
        return 2
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
