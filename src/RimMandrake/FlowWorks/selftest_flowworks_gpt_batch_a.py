#!/usr/bin/env python3
"""selftest_flowworks_gpt_batch_a.py — FlowWorks GPT high-depth review (2026-10-23), batch A: the liquid-sim core.

WHY: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` confirmed defects whose fix sits in Verse-bound code (bottle
debit, drill tick, map-control pulses, hose load, flood placement) that the C# SelfTest cannot compile. The arithmetic
each fix calls is tested behaviourally in Source/SelfTest/GptBatchA1024Checks.cs; this file holds the CALL SITES: it
reads the production .cs (comments masked), scopes to the method that must hold the fix and asserts the fixed shape.

CAN IT FAIL: every case carries `undo`, a (fixed, old) splice that restores the shape GPT found; each run applies it to an
in-memory copy and the case must go RED there. A case whose undo stays green fails.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_gpt_batch_a.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from selftest_flowworks_gpt_c import Case, main as _run  # noqa: E402
import selftest_flowworks_gpt_c as _c  # noqa: E402

CASES = [
    # ── DUG_WATER_FILL_FIX_NO_CANAL_DEBIT (FA_core_sim_1.1) ──
    Case("DUG_WATER_FILL_FIX_NO_CANAL_DEBIT", "a dug cell pays from its own water", "LiquidTypes/RM_LiquidBottleUtility.cs",
         r"public static bool TryDebitTerrain\(Map map, IntVec3 c, int units\)",
         [r"if \( ex\.IsExcavated \( c \) \) \{[^}]*RM_ContainerMaterialMath\.DugCellDebitDl \( units , ex\.WaterDlAt \( c \)"
          r"[^}]*ex\.TryTakeDl \( c , dl , out _ \) == dl"],
         ("            if (ex.IsExcavated(c))\n", "            if (false)\n"),
         order=(r"ex\.IsExcavated \( c \)", r"ex\.Stock\.TryDebit")),
    # ── DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM (FA_core_sim_1.2) ──
    Case("DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM", "the drill spends what landed", "Drilling/Building_LiquidDrill.cs",
         r"public override void TickRare\(\)",
         [r"long beforeDl = excavation\.WaterDlAt \( outlet \) ; if \( excavation\.TrySetDriverWaterDl \( outlet , beforeDl \+ addDl , canalFluid \) \)"
          r" \{ pendingUnits -= RM_DrillSurveyMath\.SpentUnits \( beforeDl , excavation\.WaterDlAt \( outlet \)"],
         ("pendingUnits -= RM_DrillSurveyMath.SpentUnits(beforeDl, excavation.WaterDlAt(outlet), RM_LevelSolve.U, unitPerLevel);",
          "pendingUnits -= addDl * unitPerLevel / RM_LevelSolve.U;"),
         absent=[r"pendingUnits -= addDl \* unitPerLevel"]),

    # ── UNLIMITED_SINK_FIX_FRACTIONAL_WATER (FA_core_sim_1.4) ──
    Case("UNLIMITED_SINK_FIX_FRACTIONAL_WATER", "the sink drains part-notch water", "MapControls/RM_FlowTaps.cs",
         r"public class Building_RM_FlowSink[\s\S]*?public override void FlowPulse\(RM_MapComponent_Excavation ex\)",
         [r"long w = ex\.WaterDlAt \( c \) ; if \( w > 0 &&",
          r"long took = ex\.TryTakeDl \( candCells \[ pick \] , Math\.Min \( RM_LevelSolve\.U , dueDl - doneDl \) , out _ \) ;"
          r" if \( took <= 0 \) \{ break ; \} doneDl \+= took ;",
          r"ex\.NoteMapControlFlowDl \( 0 , doneDl \)"],
         ("long w = ex.WaterDlAt(c);", "long w = ex.FillAt(c);"),
         absent=[r"ex\.FillAt \(", r"ex\.TryTakeLevel \("]),
    # ── WET_CELL_CENSUS_FIX_SHEETS_READ_DRY (FA_core_sim_2.4) ──
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the census counts a part-notch sheet wet", "RM_FluidIdentity.cs",
         r"public static string ProofCensus\(\)",
         [r"if \( ex\.ExcavatedDepthAt \( c \) == 0 \|\| ex\.WaterDlAt \( c \) == 0 \) continue ;"],
         ("ex.WaterDlAt(c) == 0) continue;", "ex.FillAt(c) == 0) continue;"),
         absent=[r"ex\.FillAt \("]),
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "a part-notch acid sheet still reads as acid", "RM_FluidIdentity.cs",
         r"public static bool CellHoldsAcid\(Map map, IntVec3 c\)",
         [r"ex != null && ex\.WaterDlAt \( c \) > 0 \? ex\.FluidAt \( c \) : null"],
         ("ex.WaterDlAt(c) > 0 ? ex.FluidAt(c)", "ex.FillAt(c) > 0 ? ex.FluidAt(c)"),
         absent=[r"ex\.FillAt \("]),
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the flow meter holds and names a part-notch sheet", "MapControls/RM_FlowMeter.cs",
         r"public void Read\(RM_MapComponent_Excavation ex\)",
         [r"long w = ex\.WaterDlAt \( c \) ; heldDl \+= w ; dug \+= ex\.DepthAt \( c \) ; if \( w > 0 \)"],
         ("long w = ex.WaterDlAt(c);", "long w = ex.FillAt(c);"),
         absent=[r"ex\.FillAt \("]),
    # The meter REPORTS held levels as heldDl / U: U is an int, so the division must be floating or a part-notch sheet
    # reads 0 held levels again (Reading, label, StateLine, FlowPulse samples). Scoped to the whole class: the property
    # is expression-bodied, and every report must route through it.
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the flow meter reports part-notch held levels as a fraction, never 0",
         "MapControls/RM_FlowMeter.cs",
         r"public class Building_RM_FlowMeter\b",
         [r"private float HeldLevelsExact => \( float \) \( heldDl / \( double \) RM_LevelSolve\.U \) ;",
          r"float amount = kind == \"channel\" \? HeldLevelsExact :",
          r"private string HeldText\(string format\) \{ return HeldLevelsExact\.ToString \("],
         ("(float)(heldDl / (double)RM_LevelSolve.U)", "(float)(heldDl / RM_LevelSolve.U)"),
         absent=[r"heldDl\s*/(?!\s*\(\s*double\s*\))"]),
    # Each REPORT the meter prints (inspect Reading, dev-overlay label, StateLine log) must show held levels through
    # HeldText: a site that prints RM_MapControlMath.HeldLevels(...) instead rounds a part-notch sheet to 0 again.
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the meter's inspect reading prints exact held levels",
         "MapControls/RM_FlowMeter.cs",
         r"private string Reading\(\)",
         [r"return \"Channel: \" \+ cells \+ \" dug square\(s\), \" \+ HeldText \( \"0\.##\" \) \+ \" of \" \+ dug"],
         ('HeldText("0.##") + " of "', 'RM_MapControlMath.HeldLevels(heldDl, RM_LevelSolve.U).ToString() + " of "'),
         absent=[r"HeldLevels \(", r"heldDl"]),
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the meter's overlay label prints exact held levels",
         "MapControls/RM_FlowMeter.cs",
         r"public override void DrawGUIOverlay\(\)",
         [r"string s = kind == \"channel\" \? HeldText \( \"0\.#\" \) \+ \"/\" \+ dug"],
         ('HeldText("0.#") + "/"', 'RM_MapControlMath.HeldLevels(heldDl, RM_LevelSolve.U).ToString() + "/"'),
         absent=[r"HeldLevels \(", r"heldDl"]),
    Case("WET_CELL_CENSUS_FIX_SHEETS_READ_DRY", "the meter's state line prints exact held levels and raw dL",
         "MapControls/RM_FlowMeter.cs",
         r"public override string StateLine\(\)",
         [r"\" held=\" \+ HeldText \( \"0\.##\" \) \+ \" heldDl=\" \+ heldDl \+ \" dug=\""],
         ('" held=" + HeldText("0.##")', '" held=" + RM_MapControlMath.HeldLevels(heldDl, RM_LevelSolve.U).ToString()'),
         absent=[r"HeldLevels \("]),
    # ── LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN (FA_core_sim_2.3) ──
    Case("LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN", "the holder measures held water in dL", "MapControls/RM_LevelHolder.cs",
         r"private void Measure\(RM_MapComponent_Excavation ex, out long heldDl, out int capacity\)",
         [r"capacity \+= ex\.DepthAt \( c \) ; heldDl \+= ex\.WaterDlAt \( c \) ;"],
         ("heldDl += ex.WaterDlAt(c);", "heldDl += ex.FillAt(c);"),
         absent=[r"ex\.FillAt \("]),
    Case("LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN", "the holder drains part notches and steers on dL", "MapControls/RM_LevelHolder.cs",
         r"private void HoldChannel\(RM_MapComponent_Excavation ex, int due\)",
         [r"lastHeld = RM_MapControlMath\.HeldLevels \( heldDl , RM_LevelSolve\.U \) ;",
          r"RM_MapControlMath\.HeldLevels \( heldDl \+ poured - taken , RM_LevelSolve\.U \)",
          r"need < 0 && ex\.WaterDlAt \( c \) > 0 && Mine \( ex , c \)",
          r"long took = ex\.TryTakeDl \( candCells \[ pick \] , RM_LevelSolve\.U , out _ \) ;",
          r"ex\.NoteMapControlFlowDl \( poured , taken \)"],
         ("need < 0 && ex.WaterDlAt(c) > 0 && Mine(ex, c)", "need < 0 && ex.FillAt(c) > 0 && Mine(ex, c)"),
         absent=[r"ex\.TryTakeLevel \(", r"need < 0 && ex\.FillAt"]),
    # ── HOSE_RELOAD_FIX_SPILLS_SAVED_FLOW (FB_hose_gss_1.5) ──
    Case("HOSE_RELOAD_FIX_SPILLS_SAVED_FLOW", "the flow lease is saved with the held liquid", "Hose/CompHoseReel.cs",
         r"public override void PostExposeData\(\)",
         [r"Scribe_Values\.Look \( ref heldUnits , \"rmHoseHeldUnits\" , 0 \) ;"
          r" Scribe_Values\.Look \( ref flowUntil , \"rmHoseFlowUntil\" , RimMandrake\.FlowWorks\.Machinery\.RM_LiquidNetKernel\.NoLease \) ;"],
         ("            Scribe_Values.Look(ref flowUntil, \"rmHoseFlowUntil\", RimMandrake.FlowWorks.Machinery.RM_LiquidNetKernel.NoLease);\n", "")),
    # ── DUG_FILL_FIX_WALKS_TO_SHEET (batch A code review): the search skips a dug cell that cannot pay ──
    Case("DUG_FILL_FIX_WALKS_TO_SHEET", "the fill search never walks to a sheet thinner than the container",
         "LiquidTypes/RM_LiquidBottleUtility.cs",
         r"private static bool TryFindLiquidCellUncached\(",
         [r"if \( ex != null && ex\.IsExcavated \( c \) && RM_ContainerMaterialMath\.DugCellDebitDl \("
          r" container != null \? RM_ContainerMaterials\.UnitsIn \( container , candidate , size \) : candidate\.UnitsFor \( size \) ,"
          r" ex\.WaterDlAt \( c \) , RM_MapComponent_Excavation\.LevelExact , RM_LevelSolve\.U \) < 0 \) \{ continue ; \}"],
         ("if (ex != null && ex.IsExcavated(c) && RM_ContainerMaterialMath", "if (false && ex.IsExcavated(c) && RM_ContainerMaterialMath"),
         order=(r"ex\.Stock\.CanSupply", r"ex\.IsExcavated \( c \) && RM_ContainerMaterialMath\.DugCellDebitDl")),
    # ── TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH (FA_core_sim_1.8, option A) ──
    Case("TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH", "the undug bank beside the release hardens to glass", "Flood_FlowWorks.cs",
         r"private void CoolFrontToGlass\(\)",
         [r"List<int> bank = RM_StockMath\.GlassBankCells \( map\.Size\.x , map\.Size\.z , placedIdx ,"
          r" n => placedLookup\.Contains \( idx\.IndexToCell \( n \) \) , n => MayBankToGlass \( map , idx\.IndexToCell \( n \) , excavation \) \) ;",
          r"for \( int i = 0 ; i < bank\.Count ; i\+\+ \) \{ map\.terrainGrid\.SetTerrain \( idx\.IndexToCell \( bank \[ i \] \) , fluidDef\.coolsToGlassEdge \) ; \}"],
         ("\t\t\t\tmap.terrainGrid.SetTerrain(idx.IndexToCell(bank[i]), fluidDef.coolsToGlassEdge);\n", ""),
         order=(r"GlassBankCells", r"SetTerrain \( idx\.IndexToCell \( bank")),
    Case("TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH", "the bank never rewrites engine, liquid, floor or edifice cells", "Flood_FlowWorks.cs",
         r"private bool MayBankToGlass\(Map map, IntVec3 c, RM_MapComponent_Excavation excavation\)",
         [r"top\.IsWater \|\| baseDef\.IsWater",
          r"excavation\.IsExcavated \( c \) \|\| excavation\.CanLiquidEnter \( c \)",
          r"g\.TempTerrainAt \( c \) != null \|\| g\.UnderTerrainAt \( c \) != null \|\| g\.FoundationAt \( c \) != null",
          r"return c\.GetEdifice \( map \) == null ;"],
         ("(excavation.IsExcavated(c) || excavation.CanLiquidEnter(c))", "(false)")),
]


if __name__ == "__main__":
    _c.CASES = CASES
    sys.exit(_run())
