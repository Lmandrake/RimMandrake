#!/usr/bin/env python3
"""T_STATICS_CENSUS (GimmeSomeSlack 0.1.0, bars statics_clear_between_games and game_statics_reset): a source census of every
static field in Source/ (SelfTest/ excluded), so a new static that can carry one game's objects into the next is caught before
any game is loaded.

Each static is put in one class:
  RESET    can hold a game's objects or per-game state, and GssSessionReset's constructor calls the line that empties it
  LISTED   can hold a game's objects, and is named below with the reason it is safe across games
  table    any other collection: strings, defs, materials, numbers built from defs, the same in every game
  value    a scalar, string, def, reflection handle or settings value: holds no game object

"Can hold a game's objects" = its type names a game object (Map, Thing, Pawn, a comp, a power net, a cord piece, a
gravship, a delegate) or it is keyed by int/long (thing or map ids), or it is one of the four tables the bar names (the tap
registry, the style picks, the printed-section set, the live-wire path costs). A DANGER static in neither RESET nor LISTED
is a refusal, and so is a RESET line GssSessionReset no longer calls.

--plant (also run on every normal run): a new static List<Thing> nobody resets, and GssSessionReset with the tap-registry
line removed, must each go red. Exit 0 PASS, 1 FAIL.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_statics_census.py [--list]
"""
import glob
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
RESET_FILE = "GssSessionReset.cs"

# field (file-relative "path::name") -> the call GssSessionReset's constructor must make to empty it
RESET = {
    "Aerial/CompPowerTap.cs::ledger": "Aerial.TapRegistry.Clear();",
    "SectionLayer_RM_MessyCords.cs::PrintedStatic": "SectionLayer_RM_MessyCords.PrintedStatic.Clear();",
    "Aerial/ConduitStylePicker.cs::lastPicked": "Aerial.ConduitStylePicker.ClearPicks();",
    "Aerial/StylePicker.cs::Core": "Aerial.StylePicker.ClearPicks();",
    "Aerial/RM_LiveWirePathCost.cs::byMap": "Aerial.RM_LiveWirePathCost.Clear();",
    "GimmeSomeSlackProbe.cs::sameFrameWall": "GimmeSomeSlackProbe.ResetSameFrame();",
    "GimmeSomeSlackProbe.cs::sameFrameMap": "GimmeSomeSlackProbe.ResetSameFrame();",
    "GimmeSomeSlackProbe.cs::request": 'GimmeSomeSlackProbe.request = "";',
    "Aerial/AerialProbe.cs::request": 'Aerial.AerialProbe.request = "";',
    "Aerial/CompAerialAnchor.cs::debugSkipReseed": "Aerial.CompAerialAnchor.debugSkipReseed = false;",
    "Core/CordBuilder.cs::StepTrace": "Core.CordBuilder.StepTrace = null;",
}
# field -> why it is safe across games
LISTED = {
    "Aerial/AerialLineProfiles.cs::pipeSag": "FlowWorks registers its pipe-pole readers once at mod load: process-wide by design",
    "Aerial/AerialLineProfiles.cs::pipeMaxSpan": "FlowWorks' pipe-pole reader, registered at mod load",
    "Aerial/AerialLineProfiles.cs::pipeOn": "FlowWorks' pipe-pole switch reader, registered at mod load",
    "Aerial/AerialLineProfiles.cs::spansChanged": "listeners registered at mod load; each is called with the map, holds none",
    "Aerial/AerialMaterials.cs::styleGraphic": "a reflection field handle: no state",
    "RM_MapComponent_CordGraph.cs::mapOf": "a reflection field handle: no state",
    "RM_MapComponent_CordGraph.cs::flagNames": "a pure name function",
    "Aerial/CompPowerTap.cs::InNet": "a pure predicate",
    "Aerial/CompPowerTap.cs::Drained": "an event PowerTheftConsequences subscribes to at mod load; it holds no game object",
    "Aerial/RM_FallenWireShock.cs::liveWireSources": "FlowWorks registers its dropped-cord source once at mod load; it is asked per map",
    "CordUnderLiquid.cs::floorSeen": "FlowWorks' under-liquid reader, bound once at mod load",
    "CordUnderLiquid.cs::faded": "a material cache keyed by texture and fade level, not by a map or thing",
    "Core/CordBuilder.cs::incidentIndexes": "a ConditionalWeakTable: an entry dies with its graph",
    "Core/CordBuilder.cs::finalRepairOwn": "a [ThreadStatic] scratch list refilled on each use",
    "Core/CordBuilder.cs::HopWhy": "a debug trace hook, null in play",
    "Core/CordSlacken.cs::Why": "a debug trace hook (the geometry lab), null in play",
    "Core/CordBuilder.cs::HeapWalkTrace": "a debug trace hook, null in play",
    "Core/CordBuilder.cs::HeapWalkWhy": "a debug trace hook, null in play",
    "Core/CordBuilder.cs::FitProf": "a [ThreadStatic] profiling hook no code in the mod sets: null in play",
    "Core/CordLiveEnd.cs::LayWhy": "a [ThreadStatic] debug trace hook, set only under CordBuilder.FitTrace (SelfTest) and nulled after each Lay",
    "Core/CordLiveEnd.cs::FitWhy": "a [ThreadStatic] debug trace hook, set only under CordBuilder.FitTrace (SelfTest) and nulled after each Fit",
    "SectionLayer_RM_MessyCords.cs::PrintedVariants": "a print census keyed by variant number (not an id), read by probes as a delta",
    "Aerial/StylePicker.cs::core": "StyleIndex.core: an alias of StylePicker.Core (the same object), whose picks the RESET of Core empties",
    "Aerial/CompAerialAnchor.cs::aboardCache": "rebuilt whenever the gravship asked about is not aboardCacheFor; a new game's ship is a new object",
    "Aerial/CompAerialAnchor.cs::aboardCacheFor": "the key of aboardCache: compared by reference, so an old game's ship never matches a new "
                                                  "one (it keeps that one ship alive until the next launch: a small leak, not carried state)",
}
GAME = set("Map Thing Pawn Building CompPower CompAerialAnchor PowerNet LaidPiece CordGraph Gravship Action Func event "
           "IncidentIndex MachineInfo TapLedger StylePickerCore".split())
NAMED = set(RESET)  # the bar's four tables (and the probe state) are danger by name, whatever their type
DECL = re.compile(r"^\s*(?:\[[^\]]*\]\s*)*((?:(?:public|internal|private|protected|static|readonly|volatile|new)\s+)+)"
                  r"([\w<>\[\],.?() ]+?)\s+(\w+)\s*(=|;)", re.M)
COLL = re.compile(r"\b(List|Dictionary|HashSet|Queue|Stack|IReadOnlyList|IReadOnlyDictionary|ConditionalWeakTable)\b|\[\]")


def strip_generics(t):
    while True:
        n = re.sub(r"<[^<>]*>", "", t)
        if n == t:
            return t
        t = n


def statics(files):
    """(key, type, readonly) for every static field declaration; method parameters and locals are not fields."""
    out = []
    for rel, text in files:
        s = re.sub(r"//[^\n]*", "", text)
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
        s = re.sub(r'@?"(?:[^"\\\n]|\\.)*"', '""', s)
        for m in DECL.finditer(s):
            mods, typ, name = m.group(1).split(), m.group(2).strip(), m.group(3)
            if "static" not in mods or "const" in mods:
                continue
            names = [name]
            depth, cut = 0, None                           # "Func<float> a, b" declares a and b: split the type off
            for i, ch in enumerate(typ):
                depth += ch in "<([" and 1 or ch in ">)]" and -1 or 0
                if ch == " " and depth == 0 and i and typ[i - 1] not in ",":
                    cut = i
                    break
            if cut is not None and typ[cut:].strip().endswith(","):
                names = [n.strip() for n in typ[cut:].split(",") if n.strip()] + [name]
                typ = typ[:cut]
            if "(" in strip_generics(typ) and not typ.startswith("("):
                continue                                   # a method's parameter default, not a field
            if typ.split()[-1] in ("return", "new", "else", "var", "class", "struct", "enum", "using"):
                continue
            for n in names:
                out.append(("%s::%s" % (rel, n), typ, "readonly" in mods))
    return out


def classify(key, typ):
    toks = set(re.findall(r"[A-Za-z_]\w*", typ))
    danger = bool(toks & GAME) or bool(re.search(r"(Dictionary|HashSet)<\s*(int|long)\b", typ)) or key in NAMED
    if danger:
        return "RESET" if key in RESET else "LISTED" if key in LISTED else "DANGER"
    return "table" if COLL.search(typ) else "value"


def census(files, reset_text):
    rows = [(k, t, ro, classify(k, t)) for k, t, ro in statics(files)]
    faults = ["%s (%s): can hold a game's objects; neither reset in %s nor listed with a reason" % (k, t, RESET_FILE)
              for k, t, ro, c in rows if c == "DANGER"]
    ctor = reset_text[reset_text.find("public GssSessionReset(Game game)"):]
    ctor = ctor[:ctor.find("\n        }")]
    seen = {k for k, _, _, _ in rows}
    for k, call in RESET.items():
        if k not in seen:
            faults.append("%s: in the RESET table but no such static (renamed? update the table)" % k)
        elif call not in ctor:
            faults.append("%s: GssSessionReset's constructor no longer calls %s" % (k, call))
    for k in LISTED:
        if k not in seen:
            faults.append("%s: listed but no such static (renamed? update the list)" % k)
    return rows, faults


def load():
    files = []
    for f in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
        rel = os.path.relpath(f, SRC).replace(os.sep, "/")
        if rel.startswith("SelfTest/") or "/obj/" in rel or "/bin/" in rel:
            continue
        files.append((rel, open(f, encoding="utf-8").read()))
    return files, open(os.path.join(SRC, RESET_FILE), encoding="utf-8").read()


def main(argv):
    files, reset_text = load()
    rows, faults = census(files, reset_text)
    ok = True
    by = {}
    for _, _, _, c in rows:
        by[c] = by.get(c, 0) + 1
    print("statics: %d in %d files: %s" % (len(rows), len(files), ", ".join("%s %d" % kv for kv in sorted(by.items()))))
    if "--list" in argv:
        for k, t, ro, c in rows:
            print("  %-7s %s  %s%s" % (c, k, t, " readonly" if ro else ""))
    for f in faults:
        print("FAIL " + f)
        ok = False
    # the bar's four tables are each RESET (not merely listed)
    for k in ("Aerial/CompPowerTap.cs::ledger", "Aerial/ConduitStylePicker.cs::lastPicked",
              "SectionLayer_RM_MessyCords.cs::PrintedStatic", "Aerial/RM_LiveWirePathCost.cs::byMap"):
        c = next((c for kk, _, _, c in rows if kk == k), None)
        if c != "RESET":
            print("FAIL %s: the bar names it; it must be RESET, reads %s" % (k, c))
            ok = False
    # planted faults: each must be refused
    leak = files + [("Aerial/Planted.cs", "    internal static class Planted\n    {\n        private static readonly List<Thing> leak = new List<Thing>();\n    }\n")]
    _, f1 = census(leak, reset_text)
    _, f2 = census(files, reset_text.replace("Aerial.TapRegistry.Clear();", ""))
    planted = [any("Planted.cs::leak" in x for x in f1), any("TapRegistry.Clear" in x for x in f2)]
    print("planted: a new unreset static List<Thing> %s; the tap-registry reset removed %s"
          % tuple("refused" if p else "NOT CAUGHT" for p in planted))
    ok = ok and all(planted)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
