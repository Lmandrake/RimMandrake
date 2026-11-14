// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE round 8: properties of ../RM_VaporColumnMath.cs (the production rule). Family
// "ventcol": a steam geyser feeds a vapour column unless every one of its squares stands in liquid (a vent drowned in a
// FlowWorks pit sends no haze or ash spirals over the water; owner 2026-11-13: "It should be bubbling water, not faint
// ghost bubbles rising up"). Checked over every footprint size 0..9 and every wet count against a written-out oracle.
using System;

namespace RimMandrake.EnvironmentalHazards.SelfTest
{
    internal static class VentColumnChecks
    {
        public static int Cases;

        public static bool Run(string only)
        {
            if (only != null && only != "ventcol") return true;
            bool ok = true;
            for (int squares = 0; squares <= 9; squares++)
            {
                for (int wet = 0; wet <= squares; wet++)
                {
                    Cases++;
                    bool want = squares == 0 || wet != squares;   // oracle: only a wholly drowned vent goes quiet
                    bool got = RM_VaporColumnMath.GeyserFeedsColumn(squares, wet);
                    if (got != want)
                    {
                        Console.WriteLine("FAIL ventcol squares=" + squares + " wet=" + wet + " feeds=" + got + " want " + want);
                        ok = false;
                    }
                }
            }
            if (!RM_VaporColumnMath.GeyserFeedsColumn(4, 3) || RM_VaporColumnMath.GeyserFeedsColumn(4, 4))
            {
                Console.WriteLine("FAIL ventcol: a 2x2 geyser with one dry square must steam, a drowned one must not");
                ok = false;
            }
            Console.WriteLine("  ventcol: " + Cases + " cases " + (ok ? "ok" : "FAIL"));
            return ok;
        }
    }
}
