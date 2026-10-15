#!/usr/bin/env python3
"""selftest_flowworks_gpt_c.py — the FlowWorks pre-release GPT-consult fixes, builder C (cross-cutting).

WHY: `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` confirmed bugs whose fix lives in Verse-bound code
(Tick bodies, Harmony postfixes, placement call sites, proof hooks) that the C# SelfTest cannot compile. Each case
here reads the PRODUCTION .cs file (comments masked), scopes to the method that must hold the fix, and asserts the
fixed shape is present (and the old shape absent).

CAN IT FAIL: every case carries `undo` — a (new, old) text splice that puts today's fix back to the shape GPT found.
Each run applies it to an in-memory copy and the case must go RED there; a case whose undo stays green fails.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_gpt_c.py
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source"


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments (keeping strings and line structure) so a fix kept only in a comment is gone."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def block_after(text: str, anchor: str) -> str | None:
    """The brace block that follows the first match of `anchor` (a regex), or None."""
    m = re.search(anchor, text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def _p(pattern: str) -> re.Pattern:
    """A literal space in a pattern means 'any whitespace, or none'."""
    return re.compile(pattern.replace(" ", r"\s*"), re.S)


@dataclass
class Case:
    item: str
    finding: str
    file: str                       # relative to Source/
    scope: str                      # anchor regex of the method whose block must hold the fix
    present: list                   # regexes that must all match inside the scope
    undo: tuple                     # (new_text, old_text): splice applied to the RAW file for the can-fail probe
    absent: list = field(default_factory=list)
    order: tuple = ()               # (a, b): a's first match precedes b's first match


CASES = [
    # ── FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS ──
    Case("FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS", "C4-F4", "RM_LiquidHeat.cs",
         r"public void Tick\(Map map, RM_MapComponent_Excavation ex\)",
         [r"if \( ! RimMandrakeFlowWorksSettings\.liquidHeatPushEnabled \) \{[^}]*nextRescanTick = 0 ;[^}]*return ;"],
         ("\t\t\t\tnextRescanTick = 0;\n\t\t\t\treturn;", "\t\t\t\treturn;")),
    Case("FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS", "C6-F3 (re-appliable)", "Rivers/RM_RiverWorks.cs",
         r"public static void Reapply\(\)",
         [r"applied\.TryGetValue \( t , out int had \)", r"extraNonDraftedPerceivedPathCost \+= want - had",
          r"Notify_CellDelta \( m\.BoundsRect \( \) \)"],
         ("t.extraNonDraftedPerceivedPathCost += want - had;", "t.extraNonDraftedPerceivedPathCost += want;")),
    Case("FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS", "C6-F3 (called on settings write)", "RimMandrakeFlowWorksMod.cs",
         r"public override void WriteSettings\(\)",
         [r"Rivers\.RM_RiverPathCost\.Reapply \( \) ;"],
         ("            Rivers.RM_RiverPathCost.Reapply();\n", "")),
    Case("FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS", "C6-F5", "Rivers/RM_Weir.cs",
         r"private void TickBreach\(\)",
         [r"if \( ! RM_RiversSettings\.breachEnabled \) \{[^}]*cascadeFireTicks\?\.Clear\(\) ;[^}]*breachEndTick = now ;"],
         ("\t\t\t\tbreachEndTick = now;\n", "")),
    # ── MAP_STATICS_PRUNE_GHOST_MAPS ──
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "pruner runs on map removal", "Machinery/RM_LiquidNet.cs",
         r"public override void MapRemoved\(\)",
         [r"PruneAll \( \) ;"],
         ("\t\t\tbase.MapRemoved();\n\t\t\tPruneAll();\n", "\t\t\tbase.MapRemoved();\n")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "pruner runs on load", "Machinery/RM_LiquidNet.cs",
         r"public override void FinalizeInit\(\)",
         [r"PruneAll \( \) ;"],
         ("\t\t\tbase.FinalizeInit();\n\t\t\tPruneAll();\n", "\t\t\tbase.FinalizeInit();\n")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "C1-F2 C3-F2 C5-F3 every table pruned", "Machinery/RM_LiquidNet.cs",
         r"public static void PruneAll\(\)",
         [r"RM_LiquidNet\.PruneDeadMaps \( \) ;", r"RM_PitPathing\.PruneDeadMaps \( \) ;", r"RM_DigDiscovery\.PruneDeadMaps \( \) ;"],
         ("\t\t\tRM_PitPathing.PruneDeadMaps();\n", "")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "the component never steals the spawn patch's attributes", "Machinery/RM_LiquidNet.cs",
         "",
         [r"\[HarmonyLib\.HarmonyPatch \( typeof \( Building \) , nameof \( Building\.SpawnSetup \) \) \] "
          r"\[RimMandrake\.Shared\.PatchFeature \( \"Universal pipes\"[^\]\n]*\] public static class RM_Patch_NetTopologySpawn"],
         ("\tpublic static class RM_Patch_NetTopologySpawn", "\tpublic class Wedged { }\n\tpublic static class RM_Patch_NetTopologySpawn")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "C1-F2 net tables", "Machinery/RM_LiquidNet.cs",
         r"public static void PruneDeadMaps\(\)",
         [r"states\.Remove \( m \)", r"rotations\.Remove \( m \)", r"RM_HoseLinks\.PruneDeadMaps \( \) ;"],
         ("\t\t\tRM_HoseLinks.PruneDeadMaps();\n", "")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "C3-F2 pit grids disposed (ladders too)", "Superdeep/RM_PitPathing.cs",
         r"public static void PruneDeadMaps\(\)",
         [r"PruneDeadLadders \( \) ;", r"entryCache\.Clear \( \) ;", r"g\.avoidPits\?\.cells\.Dispose \( \) ;"],
         ("\t\t\tPruneDeadLadders();\n", "")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "C5-F3 dig pool unpinned", "RM_DigDiscovery.cs",
         r"public static void PruneDeadMaps\(\)",
         [r"poolMap = null ;"],
         ("\t\t\t\tpoolMap = null;\n", "")),
    Case("MAP_STATICS_PRUNE_GHOST_MAPS", "C5-F4 overlay meshes destroyed", "RM_LiquidSurface.cs",
         r"public override void MapRemoved\(\)",
         [r"UnityEngine\.Object\.Destroy \( mesh \) ;", r"meshPool\.Clear \( \) ;"],
         ("\t\t\t\t\tUnityEngine.Object.Destroy(mesh);\n", "")),
    # ── PLACEMENT_FAILURE_MEND_LOST_IN_POSTING ──
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "helper", "LiquidTypes/RM_LiquidBottleUtility.cs",
         r"public static void PlacePaidFor\(Thing t, IntVec3 c, Map map\)",
         [r"if \( ! GenPlace\.TryPlaceThing \( t , c , map , ThingPlaceMode\.Near \) && ! t\.Destroyed && ! t\.Spawned \)"
          r" \{ GenSpawn\.Spawn \( t , c , map \) ;"],
         ("                GenSpawn.Spawn(t, c, map);\n", "")),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C1-F13", "Machinery/Kits/RM_LiquidReaction.cs",
         r"private void Drop\(ThingDef def, int count\)",
         [r"RM_LiquidBottleUtility\.PlacePaidFor \( t , at , parent\.Map \)"],
         ("RM_LiquidBottleUtility.PlacePaidFor(t, at, parent.Map);",
          "GenPlace.TryPlaceThing(t, at, parent.Map, ThingPlaceMode.Near);"),
         absent=[r"GenPlace\.TryPlaceThing"]),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C2-F6 (fill from tank)", "LiquidTypes/JobDriver_FillBottleFromTank.cs",
         r"finish\.initAction = delegate",
         [r"RM_LiquidBottleUtility\.PlacePaidFor \( filled , pawn\.Position , Map \)"],
         ("RM_LiquidBottleUtility.PlacePaidFor(filled, pawn.Position, Map);",
          "GenPlace.TryPlaceThing(filled, pawn.Position, Map, ThingPlaceMode.Near);"),
         absent=[r"GenPlace\.TryPlaceThing"]),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C2-F6 (revert)", "LiquidTypes/RM_CompLiquidRevert.cs",
         r"private void Revert\(\)",
         [r"parent\.Destroy \( \) ; RM_LiquidBottleUtility\.PlacePaidFor \( made , pos , map \)"],
         ("RM_LiquidBottleUtility.PlacePaidFor(made, pos, map);",
          "GenPlace.TryPlaceThing(made, pos, map, ThingPlaceMode.Near);"),
         absent=[r"GenPlace\.TryPlaceThing"]),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C2-F6 (revert in a container)", "LiquidTypes/RM_CompLiquidRevert.cs",
         r"private void Revert\(\)",
         [r"if \( ! owner\.TryAdd \( made \) && ! made\.Destroyed \) \{ if \( heldMap != null \) \{ "
          r"RM_LiquidBottleUtility\.PlacePaidFor \( made , heldAt , heldMap \) ;"],
         ("\t\t\t\t\tRM_LiquidBottleUtility.PlacePaidFor(made, heldAt, heldMap);\n", "")),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C5-F12", "RM_DigDiscovery.cs",
         r"if \(!GenPlace\.TryPlaceThing\(made, lip, map, ThingPlaceMode\.Near, out Thing placed\)\)",
         [r"int left = made\.Destroyed \? 0 : made\.stackCount ;",
          r"if \( left < count \) \{ budgetLeft -= cost \* \( count - left \) / count ; \}", r"made\.Destroy \( \) ;"],
         ("\t\t\t\t\tbudgetLeft -= cost * (count - left) / count;\n", "")),
    Case("PLACEMENT_FAILURE_MEND_LOST_IN_POSTING", "C6-F9", "Rivers/RM_Weir.cs",
         r"private int Deposit\(ThingDef def, int count\)",
         [r"int left = t\.Destroyed \? 0 : t\.stackCount ;", r"return n - left ;"],
         ("\t\t\treturn n - left;", "\t\t\treturn 0;"),
         absent=[r"\? n : 0"]),
]


def check(case: Case, raw: str) -> list:
    text = mask_comments(raw)
    block = block_after(text, case.scope) if case.scope else text
    if block is None:
        return [f"scope not found: {case.scope}"]
    errs = []
    for pat in case.present:
        if not _p(pat).search(block):
            errs.append(f"missing: {pat}")
    for pat in case.absent:
        if _p(pat).search(block):
            errs.append(f"old shape present: {pat}")
    if case.order:
        a, b = (_p(x).search(block) for x in case.order)
        if not a or not b or a.start() > b.start():
            errs.append(f"order: {case.order[0]} must precede {case.order[1]}")
    return errs


def main() -> int:
    fails = 0
    for case in CASES:
        raw = (SRC / case.file).read_text(encoding="utf-8-sig")
        errs = check(case, raw)
        new, old = case.undo
        if new not in raw:
            errs.append(f"probe splice not found verbatim: {new!r}")
        else:
            if not check(case, raw.replace(new, old, 1)):
                errs.append("CAN'T FAIL: the undo probe stayed green")
        tag = f"{case.item} {case.finding}"
        if errs:
            fails += 1
            print(f"FAIL {tag}: " + "; ".join(errs))
        else:
            print(f"PASS {tag}")
    print(f"{len(CASES) - fails}/{len(CASES)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
