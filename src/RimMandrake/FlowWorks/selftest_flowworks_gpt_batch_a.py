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

]


if __name__ == "__main__":
    _c.CASES = CASES
    sys.exit(_run())
