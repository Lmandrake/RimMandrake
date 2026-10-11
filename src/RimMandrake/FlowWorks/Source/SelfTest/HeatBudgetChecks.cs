// HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE (FlowWorks P9a, GPT G3.8). Above the 3000-cell budget, RM_LiquidHeat.Push
// spent the budget on an excavated PREFIX from index 0 every interval, with one global scale. The result: later
// excavated cells never warmed anything, natural cells got nothing once the excavated cells filled the budget, and
// the excavated cells that were visited every interval were overweighted by the global scale. The production split
// (RM_LiquidHeatMath.SplitBudget) is driven here through the same two-cursor rotation Push runs. Over K intervals
// each cell's credited weight (visits x scale) must be K within one scale step. Each case has a can-fail: the old
// prefix rule computed beside it.
using System;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static partial class Program
    {
        // Push's loop shape (same SplitBudget + Rotate calls): returns per-cell credited weight, excavated cells first then natural.
        private static double[] HeatWeightsNew(int ex, int nat, int intervals, out float exScale, out float natScale)
        {
            var w = new double[ex + nat];
            int exCursor = 0, cursor = 0;
            exScale = natScale = 1f;
            for (int t = 0; t < intervals; t++)
            {
                RM_LiquidHeatMath.SplitBudget(ex, nat, out int exVisit, out exScale, out int natVisit, out natScale);
                for (int j = 0; j < exVisit; j++) w[RM_LiquidHeatMath.Rotate(ref exCursor, ex)] += exScale;
                for (int j = 0; j < natVisit; j++) w[ex + RM_LiquidHeatMath.Rotate(ref cursor, nat)] += natScale;
            }
            return w;
        }

        // The pre-fix Push loop, verbatim in shape.
        private static double[] HeatWeightsOld(int ex, int nat, int intervals)
        {
            var w = new double[ex + nat];
            int cursor = 0;
            for (int t = 0; t < intervals; t++)
            {
                int visit = RM_LiquidHeatMath.Budget(ex + nat, out float scale);
                int visited = 0;
                for (int j = 0; j < ex && visited < visit; j++, visited++) w[j] += scale;
                for (int j = 0; j < nat && visited < visit; j++, visited++) { if (cursor >= nat) cursor = 0; w[ex + cursor++] += scale; }
            }
            return w;
        }

        private static string HeatWeightsExact(double[] w, int ex, int intervals, float exScale, float natScale)
        {
            for (int i = 0; i < w.Length; i++)
            {
                double tol = (i < ex ? exScale : natScale) + 1e-3;
                if (w[i] <= 0 || Math.Abs(w[i] - intervals) > tol)
                    return (i < ex ? "excavated" : "natural") + " cell " + (i < ex ? i : i - ex) + " weight " + w[i].ToString("F2") + " vs " + intervals;
            }
            return null;
        }

        private static void RunHeatBudget()
        {
            const int K = 60;
            int B = RM_LiquidHeatMath.CellBudgetPerInterval;

            Case("P9a_heat_budget_under_the_budget_visits_everything_at_face_value", () =>
            {
                RM_LiquidHeatMath.SplitBudget(100, 200, out int ev, out float es, out int nv, out float ns);
                Assert(ev == 100 && nv == 200 && es == 1f && ns == 1f, "under budget: all cells, scale 1");
                RM_LiquidHeatMath.SplitBudget(0, 0, out ev, out es, out nv, out ns);
                Assert(ev == 0 && nv == 0, "nothing to visit");
            });

            Case("P9a_heat_budget_late_excavated_cells_are_not_starved", () =>
            {
                int ex = B + 2000;
                var w = HeatWeightsNew(ex, 0, K, out float es, out float ns);
                string bad = HeatWeightsExact(w, ex, K, es, ns);
                Assert(bad == null, "every excavated cell's average power is exact: " + bad);
                var old = HeatWeightsOld(ex, 0, K);
                Assert(old[ex - 1] == 0 && old[0] > K * 1.5, "can-fail: the old prefix starves cell " + (ex - 1) + " (" + old[ex - 1] + ") and overweights cell 0 (" + old[0].ToString("F1") + ")");
            });

            Case("P9a_heat_budget_natural_cells_get_a_share_when_excavated_fill_the_budget", () =>
            {
                int ex = B + 1000, nat = 2000;
                RM_LiquidHeatMath.SplitBudget(ex, nat, out int ev, out _, out int nv, out _);
                Assert(ev + nv == B && nv > 0, "the budget is spent whole, natural gets " + nv + " slots");
                var w = HeatWeightsNew(ex, nat, K, out float es, out float ns);
                string bad = HeatWeightsExact(w, ex, K, es, ns);
                Assert(bad == null, "both classes exact: " + bad);
                var old = HeatWeightsOld(ex, nat, K);
                double oldNat = 0; for (int i = ex; i < ex + nat; i++) oldNat += old[i];
                Assert(oldNat == 0, "can-fail: under the old rule natural liquid pushes nothing (" + oldNat + ")");
            });

            Case("P9a_heat_budget_few_excavated_beside_a_big_lake_are_not_overweighted", () =>
            {
                int ex = 100, nat = 10000;
                var w = HeatWeightsNew(ex, nat, K, out float es, out float ns);
                string bad = HeatWeightsExact(w, ex, K, es, ns);
                Assert(bad == null, "both classes exact: " + bad);
                // one slot minimum for a tiny class above the budget
                RM_LiquidHeatMath.SplitBudget(1, 50000, out int ev1, out float es1, out _, out _);
                Assert(ev1 == 1 && es1 == 1f, "a lone excavated cell keeps a slot at scale 1");
                var old = HeatWeightsOld(ex, nat, K);
                Assert(old[0] > K * 3, "can-fail: the old rule credits an excavated cell " + old[0].ToString("F0") + " vs " + K + " (x" + (old[0] / K).ToString("F2") + ")");
            });
        }
    }
}
