#!/usr/bin/env python3
"""selftest_flowworks_call_sites.py — the CALL SITES of the P4-P11 FlowWorks fixes.

WHY (independent review, Transient/flowworks_review_P4_P8_20261011.md, 92875a4de): every P-series fix moved its rule
into a Verse-free pure function the C# SelfTest compiles and runs (RM_StockMath, RM_PumpMath, RM_FireMath,
RM_LiquidHeatMath, RM_ExcavationSanityMath, RM_DriverInputs). The production CALL SITES depend on Verse and are not
compiled into that SelfTest, so deleting a call (the pump's backed-up loop, the drill's backed-up branch, the flood's
placement and cooling, the burn pulse, the palette writers, the heat budget, the station reach, the terrain-change
hook) left every test green.

WHAT THIS CHECKS, over the PRODUCTION .cs files (comments masked, so a call that survives only in a comment is gone):
  * each fixed function is CALLED inside the method that must call it (scoped to that method's brace block, or a block
    nested in it, never just "somewhere in the file");
  * where order matters, the call precedes the thing it guards (P7: CanClaim before the source debit);
  * the old inline rule the fix replaced is ABSENT from that method (e.g. P5's one-level debit in the engine branch,
    P11's circle about Position) - these are the real-source replacements for the old-rule lambdas the C# cases carried;
  * the caller chain up to a ticked entry point (a site nobody calls is a deleted call one level up);
  * every site file is in the mod's <Compile> list (EnableDefaultCompileItems is false there).

CAN IT FAIL: every run, for each site, a throwaway copy of the production file is written to a temp dir with the call
deleted inside its scope ONLY (the same call elsewhere in the file is left alone), and the same check is re-run on that
copy; it must go red. A site whose deletion stays green is itself a failure. The real files are never written.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_call_sites.py
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_call_sites.py --source <a throwaway copy of FlowWorks/Source>
"""
from __future__ import annotations

import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

FW = Path(__file__).resolve().parent
SRC = FW / "Source"
PROJ = SRC / "RimMandrake_FlowWorks.csproj"


def _p(pattern: str) -> re.Pattern:
    """A literal space in a pattern means 'any whitespace, or none' (calls wrap across lines)."""
    return re.compile(pattern.replace(" ", r"\s*"))


@dataclass
class Site:
    fix: str
    file: str                      # relative to Source/
    scope: list                    # anchor regexes; each narrows to the brace block (or ';' statement) after it
    calls: list                    # regexes that must ALL match inside the scope; calls[0] is the one deleted by the probe
    what: str
    absent: list = field(default_factory=list)   # old-rule regexes that must NOT match inside the scope
    order: tuple = ()              # (a, b): a's first match must precede b's first match inside the scope
    old: str = ""                  # the old rule VERBATIM from the fix's parent commit; the probe splices it back in


SITES = [
    # ── P4 c98e8e926 PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD ──
    Site("P4", "LiquidTypes/Building_LiquidPump.cs", [r"private string TryPour\(\)"],
         [r"ex\.NoteDriverBackedUp\( cells\[c\] \)",
          # the exact condition the C# P4 scene re-implements (its pump cycle cannot compile TryPour)
          r"if \( cd\[c\]\.room <= 0 && cd\[c\]\.wet && tk\.Any\( x => x\.canProvide && x\.fluid != null && x\.fluid == cd\[c\]\.fill \) \)"],
         "a pump backed up against a brimming outlet of its liquid re-marks it a flow input"),
    Site("P4", "Drilling/Building_LiquidDrill.cs", [r"public override void TickRare\(\)", r"if \( room <= 0 \)"],
         [r"excavation\.NoteDriverBackedUp\( outlet \)"],
         "a drill backed up against a brimming outlet re-marks it"),
    Site("P4", "RM_MapComponent_Excavation.cs", [r"public void NoteDriverBackedUp\( IntVec3 c \)"],
         [r"driverInputs\.NoteBackedUp\( i ,", r"depthGrid\[i\] > 0 && fillGrid\[i\] >= depthGrid\[i\]"],
         "NoteDriverBackedUp marks into the production RM_DriverInputs, only on an excavated brimming cell"),
    Site("P4", "RM_MapComponent_Excavation.cs", [r"public DriverFillOutcome TrySetDriverFillOutcome\("],
         [r"driverInputs\.NoteWrite\( i , fillGrid\[i\] , fill ,"],
         "a driver write marks through RM_DriverInputs.NoteWrite", absent=[r"driverInputTick"], old='driverInputTick[i] = Find.TickManager.TicksGame;'),
    Site("P4", "RM_MapComponent_Excavation.cs", [r"private void DoPulse\(\)"],
         [r"\(System\.Func<int, bool>\) ?driverInputs\.Contains", r"PruneDriverInputs\( \)"],
         "the flow kernel's external input IS the driver-input set, pruned every pulse"),
    Site("P4", "RM_MapComponent_Excavation.cs", [r"private void PruneDriverInputs\(\)"],
         [r"driverInputs\.Prune\("], "the prune goes through RM_DriverInputs.Prune", absent=[r"driverInputTick"], old='driverInputTick.Remove(k);'),

    # ── P5 5dcae23f0 FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL ──
    # (P5's float-notch rule, FloodFillTarget + FloodLevelDebit, was replaced by the dL ledger: CANAL_OVERFLOW step 1, §6 item 15)
    Site("P5", "Flood_FlowWorks.cs",
         [r"private void PlaceFluid\(", r"if \( policy == RM_StockMath\.FloodCellPolicy\.ViaEngine \)"],
         [r"ledger\.Place\( want \)",
          r"long want = RM_FloodReleaseMath\.DugPourDl\( ledger\.Remaining , cellRoom , RM_MapComponent_Excavation\.LevelExact \)",
          r"excavation\.TryPourDl\( c , fluidDef , want \)"],
         "the engine branch pours exactly DugPourDl's dL and debits exactly that",
         absent=[r"remainingVolume -= ", r"TrySetDriverFillOutcome\( c , excavation\.DepthAt"], old='remainingVolume -= fluidDef.volumePerTile;'),
    Site("P5", "Flood_FlowWorks.cs", [r"private void PlaceFluid\(", r"if \( policy == RM_StockMath\.FloodCellPolicy\.ViaEngine \)"],
         [r"long want = RM_FloodReleaseMath\.DugPourDl\("],
         "the pour amount comes from DugPourDl (probe: delete the amount call)"),
    Site("P5", "Flood_FlowWorks.cs", [r"private void SpreadOneTile\(\)"], [r"PlaceFluid\( map , target , excavation \)"],
         "the spread reaches PlaceFluid"),
    Site("P5", "Flood_FlowWorks.cs", [r"protected override void Tick\(\)"], [r"SpreadOneTile\( \)"],
         "the release tick reaches the spread"),

    # ── P6a 57b4b4120 FLOOD_SWITCH_RACE_MEND_ENGINE_OFF ──
    Site("P6a", "Flood_FlowWorks.cs", [r"private void PlaceFluid\("],
         [r"RM_StockMath\.FloodPolicy\( excavation != null && excavation\.IsExcavated\( c \) , RimMandrakeFlowWorksSettings\.legacyFloodViaEngineEnabled \)",
          r"if \( policy == RM_StockMath\.FloodCellPolicy\.HandsOff \) \{ Refuse\( c \) ; return ; \}"],
         "placement asks FloodPolicy and returns hands-off before any temp-terrain write",
         absent=[r"legacyFloodViaEngineEnabled && excavation"], old='if (RimMandrakeFlowWorksSettings.legacyFloodViaEngineEnabled && excavation != null && excavation.IsExcavated(c)) { }',
         order=(r"FloodCellPolicy\.HandsOff", r"SetTempTerrain")),
    Site("P6a", "Flood_FlowWorks.cs", [r"private void PlaceFluid\("],
         [r"if \( policy == RM_StockMath\.FloodCellPolicy\.HandsOff \) \{ Refuse\( c \) ; return ; \}"],
         "the hands-off early return (probe: delete the HandsOff branch)"),

    # ── FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE: the settings line for legacyFloodViaEngineEnabled says that with it
    # off most spills place nothing, which is true only while the spread is confined to cells CanLiquidEnter admits.
    Site("P6a-off", "Flood_FlowWorks.cs", [r"private bool CanFloodInto\("],
         [r"if \( excavation != null && ! excavation\.CanLiquidEnter\( c \) \) \{ return false ; \}"],
         "the spread is confined to cells the excavation admits (the OFF settings text depends on it)"),

    # ── P6b ae21b56db TAR_COOLING_GLASS_MEND_ENGINE_CELLS ──
    Site("P6b", "Flood_FlowWorks.cs", [r"private void CoolFrontToGlass\(\)"],
         [r"RM_StockMath\.MayCoolToGlass\( IsFrontCell\( c \) , excavation != null && excavation\.IsExcavated\( c \) \)"],
         "cooling asks MayCoolToGlass with the engine-owned flag before SetTerrain",
         absent=[r"if \( ! IsFrontCell\( c \) \)"], old='if (!IsFrontCell(c)) { continue; }',
         order=(r"MayCoolToGlass", r"SetTerrain\( c , fluidDef\.coolsToGlassEdge \)")),
    Site("P6b", "Flood_FlowWorks.cs", [r"protected override void Tick\(\)"], [r"CoolFrontToGlass\( \)"],
         "the release tick reaches the cooling"),

    # ── P7 e393177fd FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO ──
    Site("P7", "RM_FlowKernel.cs", [r"private void ResolveComponent\("],
         [r"if \( fill\[r\] == 0 && ! world\.CanClaim\( world\.DonorFluid\( donor , IsSource\( donor \) \) \) \)"],
         "the kernel refuses a dry recipient that cannot record the fluid",
         order=(r"world\.CanClaim\(", r"world\.TryDebitLevel\( donor \)")),
    Site("P7", "RM_MapComponent_Excavation.cs", [r"bool RM_IFlowWorld\.CanClaim\( object fluid \)"],
         [r"return TryPaletteKey\("], "the world's CanClaim asks the real palette"),
    Site("P7", "RM_MapComponent_Excavation.cs", [r"private bool TryPaletteKey\("],
         [r"RM_ExcavationSanityMath\.AllocateKey\( fluidPalette , fluidGrid , fluid , RM_ExcavationSanityMath\.MaxPaletteKeys ,"],
         "the palette key comes from AllocateKey (compacts a full palette)", absent=[r"Count >= 254"], old='if (fluidPalette.Count >= 254) { return false; }'),
    Site("P7", "RM_MapComponent_Excavation.cs", [r"private void Displace\("],
         [r"bool keyOk = TryPaletteKey\( fluid , out byte claimKey \)", r"\( ! WetDug\( i \) && ! keyOk \)", r"fluidGrid\[ci\] = claimKey"],
         "displacement claims a dry cell's key before filling it", absent=[r"fluidGrid\[ci\] = PaletteKey\("], old='fluidGrid[ci] = PaletteKey(fluid);',
         order=(r"TryPaletteKey\(", r"fillGrid\[ci\] = \(byte\)")),
    Site("P7", "RM_MapComponent_Excavation.cs", [r"private void ApplyRain\(\)"],
         [r"if \( ! TryPaletteKey\( fluid , out rainKey \) \) \{ continue ; \}", r"fluidGrid\[i\] = rainKey"],
         "rain leaves a dry cell dry when no key is free", absent=[r"fluidGrid\[i\] = PaletteKey\("], old='fluidGrid[i] = PaletteKey(fluid);'),
    Site("P7", "RM_MapComponent_Excavation.cs", [r"public DriverFillOutcome TrySetDriverFillOutcome\("],
         [r"if \( ! TryPaletteKey\( fluid , out driverKey \) \) \{ return DriverFillOutcome\.Refused ; \}"],
         "a driver fill is refused before any fill changes when no key is free",
         absent=[r"fluidGrid\[i\] = PaletteKey\("],
         order=(r"TryPaletteKey\( fluid , out driverKey \)", r"driverInputs\.NoteWrite\(")),

    # ── P8 18e516743 FIRE_BURN_PULSE_PROVE_REFILL_RACE ──
    Site("P8", "RM_LiquidFire.cs", [r"public void BurnPulse\("],
         # levelTicks since CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: canalTicks, or the chemfuel inferno's seconds-scale rate
         [r"int levels = RM_FireMath\.CanalLevelsToBurn\( lit != null , ref acc , pulseTicks , levelTicks \)"],
         "a canal cell burns only CanalLevelsToBurn of the liquid that burns now",
         absent=[r"LevelsDue\( ref acc , pulseTicks , (canal|level)Ticks \)"], old='int levels = RM_FireMath.LevelsDue(ref acc, pulseTicks, levelTicks);',
         order=(r"FluidDef lit = BurnableFluidAt\(", r"CanalLevelsToBurn\(")),
    Site("P8", "RM_LiquidFire.cs", [r"private const int CheckInterval"], [r"= RM_FireMath\.FireCheckIntervalTicks"],
         "Maintain's cadence IS the selftested FireCheckIntervalTicks"),
    Site("P8", "RimMandrakeFlowWorksMod.cs", [r"public static int PulseIntervalTicks"],
         [r"Mathf\.Max\( RM_FireMath\.MinFlowPulseTicks ,"], "the pulse floor IS the selftested MinFlowPulseTicks"),
    Site("P8", "RM_MapComponent_Excavation.cs", [r"private void DoPulse\(\)"],
         [r"liquidFire\.BurnPulse\( map , this , RimMandrakeFlowWorksSettings\.PulseIntervalTicks \)"],
         "the pulse reaches the burn pulse"),

    # ── P9a 8d1d33e86 heat budget split ──
    Site("P9a", "RM_LiquidHeat.cs", [r"private void Push\("],
         [r"RM_LiquidHeatMath\.SplitBudget\( excavatedSources , natural , out int exVisit , out float exScale , out int natVisit , out float natScale \)",
          r"RM_LiquidHeatMath\.Rotate\( ref exCursor , excavatedSources \)",
          r"RM_LiquidHeatMath\.Rotate\( ref cursor , natural \)",
          r"for \( int j = 0 ; j < exVisit ;", r"for \( int j = 0 ; j < natVisit ;"],
         "the heat budget is split by SplitBudget and each class rotates on its own cursor",
         absent=[r"lastVisited < visit", r"RM_LiquidHeatMath\.Budget\( total"], old='for (int j = 0; j < excavatedSources && lastVisited < visit; j++, lastVisited++) { }'),
    Site("P9a", "RM_LiquidHeat.cs", [r"private void Push\("], [r"RM_LiquidHeatMath\.Rotate\( ref exCursor , excavatedSources \)"],
         "the excavated class rotates (probe: delete the excavated rotation)"),
    Site("P9a", "RM_LiquidHeat.cs", [r"public void Tick\( Map map , RM_MapComponent_Excavation ex \)"],
         [r"Push\( map , ex ,"], "the heat tick reaches Push"),

    # ── P9b 5cc4357f9 natural heat list stale on a terrain kind change ──
    Site("P9b", "RM_LiquidHeat.cs", [r"public static void Postfix\( Map ___map , IntVec3 c , TerrainDef oldTerr , TerrainDef newTerr \)"],
         [r"ex\.LiquidHeat\.NotifyNaturalStale\( \)",
          r"if \( ex != null && RM_LiquidHeatMath\.TerrainChangeStalesNatural\( o , n , ex\.IsExcavated\( c \) \) \)"],
         "the terrain-change postfix marks the natural list stale through TerrainChangeStalesNatural"),
    Site("P9b", "RM_LiquidHeat.cs", [r"public static class RM_Patch_LiquidHeatTerrainChanged"],
         [r"public static void Postfix\("], "the patch class carries its postfix (probe: delete the postfix)"),
    Site("P9b", "RM_LiquidHeat.cs", [r"public void NotifyNaturalStale\(\)"], [r"nextRescanTick = 0 ;"],
         "the notice forces the next interval's rescan"),

    # ── P11 2ba620c32 station reach from the footprint ──
    Site("P11", "LiquidTypes/Building_LiquidPump.cs", [r"private IEnumerable<IntVec3> ReachCells\(\)"],
         [r"RM_PumpMath\.InFootprintReach\( rect\.minX , rect\.minZ , rect\.maxX , rect\.maxZ , c\.x , c\.z , reach \)",
          r"OrderBy\( q => RM_PumpMath\.FootprintDistSq\( rect\.minX , rect\.minZ , rect\.maxX , rect\.maxZ , q\.x , q\.z \) \)"],
         "station reach is InFootprintReach from OccupiedRect, nearest first by FootprintDistSq",
         absent=[r"RadialCellsAround\( Position"], old='foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, reach + rect.Width / 2f, true)) { }'),
    Site("P11", "LiquidTypes/Building_LiquidPump.cs", [r"private IEnumerable<IntVec3> ReachCells\(\)"],
         [r"OrderBy\( q => RM_PumpMath\.FootprintDistSq\("], "nearest first (probe: delete the ordering)"),
    Site("P11", "LiquidTypes/Building_LiquidPump.cs", [r"private string TryPour\(\)"], [r"ReachCells\( \)"],
         "the pump's pour reads ReachCells"),

    # ── OVF1 CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED stage 1: the sheet layer's hooks ──
    Site("OVF1", "RM_MapComponent_Excavation.cs", [r"private void DoPulse\(\)"],
         [r"GetComponent<Sheet\.RM_MapComponent_Sheet>\( \)\?\.EnginePulse\( \)"],
         "the engine pulse runs the sheet before the channel solve",
         order=(r"EnginePulse\( \)", r"if \( excavatedCells\.Count == 0 \)")),
    Site("OVF1", "RM_MapComponent_Excavation.cs", [r"private void ApplyRain\(\)"],
         [r"Sheet\.RM_MapComponent_Sheet\.RainOverflow\( map , c , levels , fluid \)"],
         "rain on a brimming square runs over the lip"),
    Site("OVF1", "RM_MapComponent_Excavation.cs", [r"private void ApplyRain\(\)"],
         [r"Sheet\.RM_MapComponent_Sheet\.RainOverflow\( map , c , levels - add , fluid \)"],
         "rain past a square's room runs over the lip"),
    Site("OVF1", "RM_MapComponent_Excavation.cs", [r"private void Displace\("],
         [r"remaining -= Sheet\.RM_MapComponent_Sheet\.SpillHomeless\( map , from , remaining , fluid \)"],
         "fill-in's homeless remainder spills before anything is reported destroyed (D1)",
         order=(r"remaining -= Sheet\.RM_MapComponent_Sheet\.SpillHomeless\(", r"ReportOverflow\( from , remaining \)")),
    Site("OVF1", "LiquidTypes/Building_LiquidPump.cs", [r"private string TryPour\(\)"],
         [r"Sheet\.RM_MapComponent_Sheet\.PumpSpillOutlet\( Map , cells , cd , units , out IntVec3 spillAt \)",
          r"Sheet\.RM_MapComponent_Sheet\.SpillLeg\( Map , spillAt ,"],
         "a pump backed up against a brimming canal of water spills its level over the lip",
         order=(r"Sheet\.RM_MapComponent_Sheet\.PumpSpillOutlet\(", r"ex\.NoteDriverBackedUp\( cells\[c\] \)")),
    # ── OVF2 CANAL_OVERFLOW step 1: a release's leftover goes to the sheet, then is disclosed; the one end ──
    Site("OVF2", "Flood_FlowWorks.cs", [r"private void EndRelease\(\)"],
         [r"ex\.ReportLiquidLost\( Position , lost ,", r"long lost = ledger\.Lose\( \)", r"DrainToSheet\( \)"],
         "a release ends by offering the rest to the sheet and disclosing what nobody took",
         order=(r"DrainToSheet\( \)", r"ledger\.Lose\( \)")),
    Site("OVF2", "Flood_FlowWorks.cs", [r"private bool DrainToSheet\(\)"],
         [r"Sheet\.RM_MapComponent_Sheet\.SpillRelease\( map , Position , ledger\.Remaining , fluidDef \)"],
         "the drain offers to the sheet as a flood (D2)"),
    Site("OVF2", "Flood_FlowWorks.cs", [r"protected override void Tick\(\)"], [r"EndRelease\( \)"],
         "the release tick reaches its one end"),
    Site("OVF1", "RM_MouseoverDepth.cs", [r"public static string DepthSuffix\("],
         [r"Sheet\.RM_MapComponent_Sheet\.ReadoutAt\( map , c \)"], "the mouseover reads spilled water"),
]

# ⚠️ Scope: "calls[0] is deleted by the probe", so a site whose probe should delete something other than its first call
# is written as its own small Site (see the P5/P6a/P9a/P9b/P11 "(probe: ...)" rows).


def mask(text: str, strings_too: bool) -> str:
    """Blank comments (and optionally string/char literal contents) with spaces, keeping every offset and newline."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        ch, nx = text[i], text[i + 1] if i + 1 < n else ""
        if ch == "/" and nx == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif ch == "/" and nx == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif ch == '"' or (ch == "@" and nx == '"') or (ch == "$" and nx == '"'):
            verbatim = ch == "@"
            j = i + (2 if ch in "@$" else 1)
            while j < n:
                if text[j] == "\\" and not verbatim:
                    j += 2
                    continue
                if text[j] == '"':
                    if verbatim and j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            if strings_too:
                for k in range(i + (2 if ch in "@$" else 1), min(j, n)):
                    out[k] = " "
            i = j + 1
        elif ch == "'":
            j = i + 1
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            if strings_too:
                for k in range(i + 1, min(j, n)):
                    out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


def scope_span(code: str, braces: str, anchors: list, lo=0, hi=None):
    """(start, end) of the region the anchors name, or an error string."""
    hi = len(code) if hi is None else hi
    for a in anchors:
        hits = [m for m in _p(a).finditer(code, lo, hi)]
        if len(hits) != 1:
            return "anchor %r matched %d times (want exactly 1)" % (a, len(hits))
        j = hits[0].end()
        while j < hi and braces[j] not in "{;":
            j += 1
        if j >= hi:
            return "anchor %r has no body" % a
        if braces[j] == ";":
            lo, hi = hits[0].start(), j + 1
            continue
        depth, k = 0, j
        while k < hi:
            if braces[k] == "{":
                depth += 1
            elif braces[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        if depth != 0:
            return "anchor %r: unbalanced braces" % a
        lo, hi = hits[0].start(), k + 1
    return lo, hi


def check(site: Site, text: str) -> list:
    code, braces = mask(text, False), mask(text, True)
    span = scope_span(code, braces, site.scope)
    if isinstance(span, str):
        return ["%s %s: %s" % (site.fix, site.file, span)]
    lo, hi = span
    errs = []
    for c in site.calls:
        if not _p(c).search(code, lo, hi):
            errs.append("%s %s: missing in scope: %s  [%s]" % (site.fix, site.file, c, site.what))
    for a in site.absent:
        if _p(a).search(code, lo, hi):
            errs.append("%s %s: OLD RULE back in scope: %s  [%s]" % (site.fix, site.file, a, site.what))
    if site.order:
        a, b = (_p(x).search(code, lo, hi) for x in site.order)
        if not a or not b or a.start() > b.start():
            errs.append("%s %s: order broken, want %r before %r  [%s]" % (site.fix, site.file, site.order[0], site.order[1], site.what))
    return errs


def delete_call(site: Site, text: str) -> tuple:
    """A copy of text with site.calls[0] deleted inside the site's scope only. (mutant, deletions-in-scope, total-in-file).
    What this probe proves is NARROW: check() searches the same regex in the same scope, so whenever deleted > 0 the
    mutant is red by construction. It proves the pattern is present in scope (not a typo matching nothing); it does NOT
    prove the pattern matches the right call (one in a dead branch would pass). The order and old-rule splices are the
    checks that can catch a wrong-but-present match."""
    code, braces = mask(text, False), mask(text, True)
    lo, hi = scope_span(code, braces, site.scope)
    pat = _p(site.calls[0])
    hits = list(pat.finditer(code, lo, hi))
    total = len(list(pat.finditer(code)))
    out = text
    for m in reversed(hits):
        out = out[:m.start()] + "/*P-CALL-DELETED*/" + out[m.end():]
    return out, len(hits), total


def splice_old(site: Site, text: str) -> str:
    """A copy of text with the fix's old rule (verbatim from its parent commit) spliced back in at the top of the scope."""
    code, braces = mask(text, False), mask(text, True)
    lo, hi = scope_span(code, braces, site.scope)
    j = braces.find("{", lo, hi)
    at = j + 1 if j >= 0 else lo
    return text[:at] + "\n" + site.old + "\n" + text[at:]


def compiled_files(proj_path: Path | None = None) -> set:
    proj = (proj_path or PROJ).read_text(encoding="utf-8")
    return {m.replace("\\", "/") for m in re.findall(r'<Compile Include="([^"]+)"', proj)}


def compile_list_fails(compiled: set) -> list:
    return ["%s is not in RimMandrake_FlowWorks.csproj's Compile list: its call sites compile into nothing" % f
            for f in sorted({s.file for s in SITES}) if f not in compiled]


def main() -> int:
    global SRC, PROJ
    if len(sys.argv) > 2 and sys.argv[1] == "--source":   # run against a throwaway copy of Source/ (can-fail demos)
        SRC = Path(sys.argv[2])
        PROJ = SRC / "RimMandrake_FlowWorks.csproj"      # the copy's csproj too, or a dropped <Compile> stays green
    fails, oks = [], 0
    if PROJ.resolve().parent != SRC.resolve():          # regression guard on the --source re-point above (can't fire today)
        fails.append("compile list read from %s, not from the source under test %s" % (PROJ, SRC))
    compiled = compiled_files()
    fails += compile_list_fails(compiled)
    # can-fail probe: a csproj missing one site file must go red
    if not compile_list_fails(compiled - {SITES[0].file}):
        fails.append("compile-list check CANNOT FAIL: dropping %s from the Compile list stayed green" % SITES[0].file)
    # sanity probe: the compile-list reader must see files we know are there
    if "RM_StockMath.cs" not in compiled or len(compiled) < 50:
        fails.append("compile-list reader is blind (%d entries, RM_StockMath.cs %s)" % (len(compiled), "RM_StockMath.cs" in compiled))
    tmpdir = tempfile.TemporaryDirectory(prefix="fw_callsite_mutants_")
    tmp = Path(tmpdir.name)
    real = {f: (SRC / f).read_text(encoding="utf-8") for f in {s.file for s in SITES}}
    for n, s in enumerate(SITES):
        errs = check(s, real[s.file])
        if errs:
            fails.extend(errs)
            continue
        mutant, deleted, total = delete_call(s, real[s.file])
        mpath = tmp / ("%02d_%s_%s" % (n, s.fix, Path(s.file).name))
        mpath.write_text(mutant, encoding="utf-8")
        red = check(s, mpath.read_text(encoding="utf-8"))
        if deleted == 0 or not red:
            fails.append("%s %s: pattern not in scope - deleting %r in a temp copy found nothing to delete [%s]" % (s.fix, s.file, s.calls[0], s.what))
            continue
        print("ok    %-4s %-38s %s" % (s.fix, Path(s.file).name, s.what))
        print("      in-scope probe (pattern present, not proof of the right call): deleted %d of %d in file -> %s" % (
            deleted, total, red[0].split(": ", 1)[1][:80]))
        if s.old:
            opath = tmp / ("%02d_%s_old_%s" % (n, s.fix, Path(s.file).name))
            opath.write_text(splice_old(s, real[s.file]), encoding="utf-8")
            ored = [e for e in check(s, opath.read_text(encoding="utf-8")) if "OLD RULE" in e]
            if not ored:
                fails.append("%s %s: CANNOT FAIL - the old rule %r spliced back stayed green [%s]" % (s.fix, s.file, s.old, s.what))
                continue
            print("      probe: old rule spliced back -> red: OLD RULE %s" % ored[0].split("OLD RULE back in scope: ", 1)[1][:70])
        oks += 1
    # a site checker that passes a file with nothing in it is blind
    blank = Site("probe", "x", [r"class Nothing"], [r"Nothing\(\)"], "probe")
    if not check(blank, "// class Nothing { void Nothing() {} }\n"):
        fails.append("checker reads comments as code")
    for msg in fails:
        print("FAIL  " + msg)
    print("%d/%d call sites asserted and proven able to fail (%d old-rule splices)" % (oks, len(SITES), sum(1 for x in SITES if x.old)))
    tmpdir.cleanup()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
