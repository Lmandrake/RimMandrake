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
         [r"long beforeDl = excavation\.WaterDlAt \( outlet \) ; if \( excavation\.TrySetDriverFill \( outlet , fill \+ levels , canalFluid \) \)"
          r" \{ pendingUnits -= RM_DrillSurveyMath\.SpentUnits \( beforeDl , excavation\.WaterDlAt \( outlet \)"],
         ("pendingUnits -= RM_DrillSurveyMath.SpentUnits(beforeDl, excavation.WaterDlAt(outlet), RM_LevelSolve.U, unitPerLevel);",
          "pendingUnits -= levels * unitPerLevel;"),
         absent=[r"pendingUnits -= levels \* unitPerLevel"]),

    # ── UNLIMITED_SINK_FIX_FRACTIONAL_WATER (FA_core_sim_1.4) ──
    Case("UNLIMITED_SINK_FIX_FRACTIONAL_WATER", "the sink drains part-notch water", "MapControls/RM_FlowTaps.cs",
         r"public class Building_RM_FlowSink[\s\S]*?public override void FlowPulse\(RM_MapComponent_Excavation ex\)",
         [r"long w = ex\.WaterDlAt \( c \) ; if \( w > 0 &&",
          r"long took = ex\.TryTakeDl \( candCells \[ pick \] , Math\.Min \( RM_LevelSolve\.U , dueDl - doneDl \) , out _ \) ;"
          r" if \( took <= 0 \) \{ break ; \} doneDl \+= took ;",
          r"ex\.NoteMapControlFlowDl \( 0 , doneDl \)"],
         ("long w = ex.WaterDlAt(c);", "long w = ex.FillAt(c);"),
         absent=[r"ex\.FillAt \(", r"ex\.TryTakeLevel \("]),
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
]


if __name__ == "__main__":
    _c.CASES = CASES
    sys.exit(_run())
