#!/usr/bin/env python3
"""Ratchet: no NEW static field holding per-game state in the ratchet-experiment mods' C#.

Lesson (infrastructure/state/lessons/20261015T025544Z-BENCH-static-session-wide-table-keyed-by.md): a static
(session-wide) table keyed by thing/pawn ids breaks across save/fixture reloads, because a reload re-issues the
same ids at the same tick, so "already handled" entries from the old load refuse the new map. RimWorld does NOT
run MapComponent.MapRemoved on a game reload (MemoryUtility.ClearAllMapsAndWorld just nulls Map fields); it runs
Game.Dispose -> Map.Dispose. So a static table is only safe if it is keyed by an object REFERENCE (Map, Pawn,
Gravship: a new object per load), weak (ConditionalWeakTable), pruned against Find.Maps, or guarded by a
`Current.Game` identity check.

Every static field in GimmeSomeSlack, FlowWorks, Pyrelands, PyrelandsMechanics and the JawaBench companion whose
type can hold per-game state must be listed in REVIEWED below with the reason it is safe. A new one fails until
someone reads it and decides (move it to a MapComponent/GameComponent, or add the guard, then list it). A listed
field that no longer exists fails too, so the list stays a census rather than a graveyard.

Census: Transient/experiment_2026-10-14/static_state_audit.md.   python3 <this file>
"""
from __future__ import annotations

import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ROOTS = [
    "src/RimMandrake/GimmeSomeSlack",
    "src/RimMandrake/FlowWorks",
    "src/RimMandrake/Pyrelands",
    "src/RimUtinni/PyrelandsMechanics",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools",
]
SKIP_DIRS = {"obj", "bin", "SelfTest"}

# A static FIELD declaration (not a method/property/const): `... static [readonly] <type> <name> (=|;)`
FIELD = re.compile(r"^\s*(?:\[[^\]]*\]\s*)*(?:(?:private|internal|public|protected)\s+)*static\s+(?:readonly\s+|volatile\s+)*"
                   r"(?P<type>[A-Za-z_][\w.]*(?:<[^=;]*>)?(?:\[\])?)\s+(?P<names>\w+(?:\s*,\s*\w+)*)\s*(?:=|;)")
PER_GAME_KEY = r"(?:(?:int|long|Thing|Pawn|Map|Ideo|Faction|Game|Region|Gravship)\b|\()"
COLLECTION = re.compile(r"^(?:[\w.]*\.)?(?:Dictionary|HashSet|List|Queue|SortedDictionary|SortedSet|Stack)<\s*" + PER_GAME_KEY)
OBJECT = re.compile(r"^(?:Map|Pawn|Thing|Game|Gravship|Ideo|Faction|RM_MapComponent_\w+|MapComponent_\w+)$")
WEAK = re.compile(r"ConditionalWeakTable<")
TICKNAME = re.compile(r"(?i)tick$")

# relpath::field -> why it is safe across a game reload. Read the code before adding a line here.
REVIEWED = {
    # GimmeSomeSlack
    "src/RimMandrake/GimmeSomeSlack/Source/SectionLayer_RM_MessyCords.cs::PrintedVariants": "keyed by strand VARIANT index, a probe counter, not game ids",
    "src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs::aboardCacheFor": "Gravship reference: a reload makes a new Gravship, so the id set is rebuilt",
    "src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs::aboardCache": "rebuilt whenever aboardCacheFor != Current.Game.Gravship",
    "src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs::groundedMessageTick": "one-message-per-launch dedupe; a launch at the exact reload tick loses one message (cosmetic, accepted)",
    # FlowWorks
    "src/RimMandrake/FlowWorks/Source/Hose/HoseCarry.cs::Default": "the carry state machine's constant transition table (tuple key of enums)",
    "src/RimMandrake/FlowWorks/Source/Hose/HoseRelay.cs::NoFeeders": "a shared empty readonly sentinel",
    "src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs::NoJoints": "a shared empty readonly sentinel",
    "src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs::shadowPool": "Material pool keyed by a colour/alpha hash, not game ids",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs::regionCache": "cleared every tick and each entry checks ReferenceEquals(e.map, p.Map)",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs::regionCacheTick": "with regionCache",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs::lastReroute": "cleared when Current.Game changes (rerouteGame); now < last reads as expired",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs::rerouteGame": "the Game guard for lastReroute",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs::walker": "[ThreadStatic], set only for the length of one Pawn_PathFollower.StartPath call and restored by its Finalizer; WalkerAt also requires w.Spawned && w.Map == map",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPathing.cs::grids": "Map reference; PruneDeadMaps drops keys not in Find.Maps",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPathing.cs::ladderGrids": "Map reference; dead maps pruned on each new-map miss",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPathing.cs::entryCache": "key carries the Map reference; cleared every tick",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPathing.cs::entryCacheTick": "with entryCache",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_CliffMask.cs::masks": "Map reference; released by PathFinderMapData.Dispose, which Game.Dispose -> Map.Dispose runs on reload",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_CliffMask.cs::notedPawn": "prefix->postfix hand-off inside one call",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs::floodMap": "set at the start of each flood; compared by reference",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs::sweepMap": "compared by reference; a new map re-sweeps",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitStepCost.cs::current": "prefix/postfix __state hand-off inside one call",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs::cachedMap": "reference cache; a new map re-reads its component",
    "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs::cachedComp": "with cachedMap",
    "src/RimMandrake/FlowWorks/Source/RM_Patch_SuperdeepShooting.cs::cachedMap": "reference cache; Forget on MapRemoved",
    "src/RimMandrake/FlowWorks/Source/RM_Patch_SuperdeepShooting.cs::cachedEngine": "with cachedMap",
    "src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs::poolMap": "ReferenceEquals(map, poolMap) gate",
    "src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs::poolTick": "with poolMap",
    "src/RimMandrake/FlowWorks/Source/RM_PitExposure.cs::charityCache": "Ideo reference + same-tick gate; bounded at 64 so dead games' Ideos do not pile up",
    "src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs::states": "Map reference; dead maps pruned on each new-map miss",
    "src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs::rotations": "Map reference; dead maps pruned on each new-map miss",
    "src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs::byMap": "Map reference; dead maps pruned on each new-map miss",
    # Pyrelands
    "src/RimMandrake/Pyrelands/Source/CompFurnaceWarmthAura.cs::byMap": "cleared when Current.Game changes (ownerGame); dead maps pruned on Register",
    "src/RimMandrake/Pyrelands/Source/CompFurnaceWarmthAura.cs::ownerGame": "the Game guard for byMap",
    "src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs::lastMap": "reference cache, re-read when the map or its component changes",
    "src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs::lastComp": "with lastMap",
    # JawaBench companion
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::Critical": "caller-armed ids; a fixture reload re-issues the same ids, which is what the caller means",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::Specimens": "re-resolved by id in EnsureEpoch when the Game changes",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::_specimenLost": "cleared with the specimen re-resolve in EnsureEpoch",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::SpecimensUnresolved": "re-resolved in EnsureEpoch",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::Prev": "nulled in EnsureEpoch",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::_threats": "cleared in EnsureEpoch",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs::LastSampleTick": "diagnostic stamp, re-written each sample",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchAwareness.cs::Open": "keyed by our own monotonic context ids, never game ids",
    "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsSampler.cs::_game": "the sampler's own Game guard",
}

# The fixes this test was written for (Transient/experiment_2026-10-14/static_state_audit.md): each must stay fixed.
REGRESSIONS = [
    ("src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs", r"static\s+readonly\s+Dictionary<int,\s*int>\s+lastTimeout", False,
     "burrow timeout table is static again (it must live on MapComponent_BurnLine)"),
    ("src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs", r"private readonly Dictionary<int, int> lastBurrowTimeout", True,
     "MapComponent_BurnLine lost its per-map burrow timeout table"),
    ("src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs", r"now < last \|\| now - last >= RerouteCooldown", True,
     "reroute cooldown no longer treats now < last (an earlier save) as expired"),
    ("src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs", r"!ReferenceEquals\(rerouteGame, Current\.Game\)", True,
     "reroute table lost its Game guard"),
    ("src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs", r"ReferenceEquals\(e\.map, p\.Map\)", True,
     "trap-region cache no longer checks the entry's map"),
    ("src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchArtboardTools.cs", r"ArtboardPawnIds", False,
     "artboard pawn table is keyed by thingIDNumber again (a reload lets it destroy a real player pawn)"),
    ("src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs", r"_gameKey = Current\.Game; Epoch\+\+;[\s\S]{0,700}ResolveSpecimens\(ids\)", True,
     "vitals EnsureEpoch no longer re-resolves specimens in the new game"),
    ("src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs", r"ConditionalWeakTable<Map, object> toldAboutHoses", True,
     "toldAboutHoses holds dead maps again"),
]


def risky(ftype: str, name: str) -> bool:
    if WEAK.search(ftype):
        return False
    if COLLECTION.search(ftype):
        return True
    if OBJECT.match(ftype):
        return True
    return ftype in ("int", "long") and bool(TICKNAME.search(name))


def scan():
    found = {}
    for root in ROOTS:
        for dp, dns, fns in os.walk(os.path.join(REPO, root)):
            dns[:] = [d for d in dns if d not in SKIP_DIRS]
            for fn in fns:
                if not fn.endswith(".cs"):
                    continue
                path = os.path.join(dp, fn)
                rel = os.path.relpath(path, REPO).replace(os.sep, "/")
                with open(path, encoding="utf-8-sig", errors="replace") as fh:
                    for ln, line in enumerate(fh, 1):
                        if "static" not in line or re.search(r"\bconst\b|\bstatic\s+(?:class|extern)\b", line):
                            continue
                        m = FIELD.match(line)
                        if not m:
                            continue
                        ftype = m.group("type")
                        for name in [n.strip() for n in m.group("names").split(",")]:
                            if risky(ftype, name):
                                found[rel + "::" + name] = (ln, ftype)
    return found


def main() -> int:
    fails = []
    found = scan()
    if len(found) < 20:   # the instrument must be able to see: today's census is 44 rows
        fails.append("scan found only %d per-game statics; the regex has gone blind" % len(found))
    for key, (ln, ftype) in sorted(found.items()):
        if key not in REVIEWED:
            path, name = key.split("::")
            fails.append("UNREVIEWED static per-game state %s:%d %s %s -- move it to a Map/GameComponent or guard it on "
                         "Current.Game, then list it in REVIEWED with the reason" % (path, ln, ftype, name))
    for key in sorted(REVIEWED):
        if key not in found:
            fails.append("REVIEWED entry no longer found (renamed, moved or fixed?): " + key)
    for rel, pat, must, msg in REGRESSIONS:
        with open(os.path.join(REPO, rel), encoding="utf-8-sig") as fh:
            src = fh.read()
        if bool(re.search(pat, src)) != must:
            fails.append("REGRESSION %s: %s" % (rel, msg))
    checks = 2 + len(found) + len(REGRESSIONS)
    if fails:
        for f in fails:
            print("FAIL", f)
        print("selftest_static_game_state: %d/%d FAIL" % (len(fails), checks))
        return 1
    print("selftest_static_game_state: %d/%d PASS (%d per-game statics reviewed, %d regressions held)"
          % (checks, checks, len(found), len(REGRESSIONS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
