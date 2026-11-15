// FlowWorks 0.1.0 blind challenge, cycle 1 (design/concepts/FlowWorks/version/blind_challenge/cycle_1/): cases the blind
// judge added where a planted fault or a lane-1 row showed a decider could stay green while the behaviour broke. Each case
// is named inside its bar's recorded --only glob (Converter*, Sheet*, Sprinkler*, DrillSurvey*) so the decider runs it.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class BlindCycle1Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(string rel) => RiverSwitchFlipChecks.Src(rel);

        // the converter's rare tick exactly as CompLiquidConverter.CompTickRare runs it for one input that always runs
        private static long ConverterDay(float perTick, int inU, int days)
        {
            float accrued = 0f;
            long eaten = 0;
            for (int t = 0; t < RM_ConversionMath.RareTicksPerDay * days; t++)
            {
                accrued += perTick;
                float capped = RM_ConversionMath.CapAccrued(accrued, inU, perTick);
                int n = RM_ConversionMath.Batches(capped, inU, 1, int.MaxValue / 2, -1);
                int pick = n > 0 ? 0 : -1;
                float clipped = pick >= 0 ? RM_ConversionMath.ClippedIncome(accrued, capped, perTick) : 0f;
                accrued = RM_ConversionMath.AccruedAfterPick(accrued, new List<float> { capped }, pick);
                if (pick >= 0)
                {
                    accrued -= n * inU;
                    accrued += clipped;
                    eaten += n * (long)inU;
                }
            }
            return eaten;
        }

        public static void Run(Action<string, Action> Case)
        {
            // CONVERTER_RATE_FIX_CAP_EATS_REMAINDER (blind cycle 1, lane 1 row conv_rate_loss_when_income_beats_a_batch): when one
            // rare tick's income was more than a batch and not a whole number of batches, the remainder was lost every tick, so
            // the converterRateMultiplier slider (0.1..5) ran up to 40 % short (Detox Works Repaired at 2x: 4,000 of 6,667 a tick).
            Case("Converter_rate_setting_delivers_its_rate", () =>
            {
                // Detox Works Repaired: 80,000 L a day, tier 1.0, toxic water's 400 L detox batch; the slider at 2x
                float perTick = RM_ConversionMath.BudgetPerRareTick(80000f * RM_Volume.UnitsPerLitre, 1f, 2f, 1f);
                long day = ConverterDay(perTick, 400 * RM_Volume.UnitsPerLitre, 1);
                double want = perTick * RM_ConversionMath.RareTicksPerDay;
                Assert(day >= want - 400 * RM_Volume.UnitsPerLitre, "Detox Works at 2x ate " + day + " units in a day, want about " + want.ToString("0"));
                double worst = 0; string at = "";
                for (int inU = 1; inU <= 200; inU++)
                    for (int p10 = 10; p10 <= 4000; p10 += 7)
                    {
                        float p = p10 / 10f;
                        long e = ConverterDay(p, inU, 1);
                        double loss = (p * RM_ConversionMath.RareTicksPerDay - e - inU) / (p * RM_ConversionMath.RareTicksPerDay);
                        if (loss > worst) { worst = loss; at = "batch " + inU + ", income " + p + " a tick: " + e; }
                    }
                Assert(worst <= 1e-4, "a converter ran " + (worst * 100).ToString("0.#") + " % below its rate (" + at + ")");
                // the idle bound still holds: a week dry, then one tick runs at most one tick's income plus one batch
                float acc = 0f;
                for (int t = 0; t < 7 * RM_ConversionMath.RareTicksPerDay; t++) acc = RM_ConversionMath.CapAccrued(acc + perTick, 4000, perTick);
                int burst = RM_ConversionMath.Batches(RM_ConversionMath.CapAccrued(acc + perTick, 4000, perTick), 4000, 1, int.MaxValue / 2, -1);
                Assert(burst * 4000 <= perTick + 4000 + 1e-3, "a dry week then a full tank ran " + burst + " batches at once");
            });

            // the caller keeps the income the cap clipped (CAP_EATS_CHANGE): planted fault CALLER_CONV_DROPS_CLIPPED survived
            // every converter decider. Verse-bound, so a source law: the add-back follows the spend, on the picked path.
            Case("Converter_caller_keeps_clipped_income", () =>
            {
                string c = Src("Machinery/CompLiquidConverter.cs");
                Assert(c.Contains("float clipped = pick >= 0 ? RM_ConversionMath.ClippedIncome(accrued, cand[pick].capped, perTick) : 0f;"), "can-fail: clipped income is read before the pick's cap replaces the budget");
                int spend = c.IndexOf("accrued -= n * step.InputUnits;", StringComparison.Ordinal);
                int back = c.IndexOf("accrued += clipped;", StringComparison.Ordinal);
                Assert(spend > 0 && back > spend, "can-fail: the clipped income is added back after the batch is spent");
                Assert(c.Contains("RM_ConversionMath.CapAccrued(accrued, step.InputUnits, perTick)"), "can-fail: the cap is the kernel's");
            });

            // SHEET_LEVEL_FIX_DRY_ISLAND_UNDER_POOL (blind cycle 1, lane 1 row sheet_walled_yard_lies_level): a square whose
            // micro-relief sat 0.6 cm up inside a 3 cm pool stayed dry for good (its flux, diff/5 = 97 dL, was under the 100 dL a
            // dry square needs, and levelling never adds a dry square), a dry island the water stood 2.4 cm above.
            Case("Sheet_dry_square_under_a_pool_is_wetted", () =>
            {
                var p = new RM_SheetMath.Params();
                var w = new RM_SheetMath.World(7, 7);
                var lips = new List<int>();
                for (int c = 0; c < 49; c++)
                {
                    int x = c % 7, z = c / 7;
                    w.Kinds[c] = x == 0 || z == 0 || x == 6 || z == 6 ? RM_SheetMath.Kind.Blocked : RM_SheetMath.Kind.Open;
                    if (w.Kinds[c] == RM_SheetMath.Kind.Open) lips.Add(c);
                }
                lips.Sort((a, b) => { int da = Math.Abs(a % 7 - 3) + Math.Abs(a / 7 - 3), db = Math.Abs(b % 7 - 3) + Math.Abs(b / 7 - 3); return da != db ? da.CompareTo(db) : a.CompareTo(b); });
                var s = new RM_SheetMath.State(7, 7, 12345);
                int spill = 25 * 3 * RM_SheetMath.DlPerCm;
                int got = RM_SheetMath.ResolveSpills(s, w, p, new List<RM_SheetMath.SpillOffer> { new RM_SheetMath.SpillOffer { LipNearestFirst = lips.ToArray(), AmountDl = spill, Fluid = 1, From = RM_SheetMath.Source.Pump } })[0];
                Assert(got == spill, "the yard takes the whole spill, got " + got);
                for (int t = 0; t < 400; t++) RM_SheetMath.Pulse(s, w, p, null);
                long lo = long.MaxValue, hi = long.MinValue; int wet = 0;
                foreach (int c in lips)
                {
                    if (s.Dl[c] <= 0) continue;
                    wet++;
                    long surf = s.Dl[c] + RM_SheetMath.Relief(s.Salt, c, p.ReliefDl);
                    lo = Math.Min(lo, surf); hi = Math.Max(hi, surf);
                }
                Assert(s.Standing == spill && s.LedgerCloses, "nothing lost: " + s.Standing + " of " + spill);
                Assert(wet == 25, "every square of a 3 cm pool is under water: " + wet + " of 25 wet");
                Assert(hi - lo <= 1, "one level surface: spread " + (hi - lo) + " dL");
            });

            // SPRINKLER_HEADS_BUILD_PUMP_REQUIRED in the caller: planted fault CALLER_SPR_SPRAYS_WITHOUT_PUMP (pressure without
            // HasPressure) survived every sprinkler decider. Verse-bound, so a source law on the one path every head pulses through.
            Case("Sprinkler_caller_asks_for_a_pump", () =>
            {
                string sp = Src("Sprinklers/RM_Sprinkle.cs");
                Assert(sp.Contains("bool pressure = enabled && switchOn && HasPressure(head);"), "can-fail: a pulse's pressure is the network's pump");
                Assert(sp.Contains("RM_SprinklerKernel.Decide(enabled, switchOn, pressure,"), "can-fail: that pressure is what the kernel decides on");
                int a = sp.IndexOf("public static bool HasPressure(Thing head)", StringComparison.Ordinal);
                int b = a < 0 ? -1 : sp.IndexOf("public static", a + 10, StringComparison.Ordinal);
                Assert(a >= 0 && b > a, "HasPressure found");
                string body = sp.Substring(a, b - a);
                Assert(body.Contains("m is Building_LiquidPump p && p.Spawned && p.Working") && body.Contains("return false;"), "can-fail: only a spawned, working pump on the head's network gives pressure");
            });

            // DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM, inside inv_drilling's decider glob: planted fault DRILL_CHARGES_WHOLE_LEVEL
            // survived T_DRILL (its regression case GptA1024_drill_spends_only_what_landed is outside the recorded glob).
            Case("DrillSurvey_charge_is_only_what_landed", () =>
            {
                const long U = RM_LevelSolve.U;
                Assert(Math.Abs(RM_DrillSurveyMath.SpentUnits(5000, U, U, 1f) - 0.5f) < 1e-6f, "half a level landed, half a level charged");
                var r = new Random(13);
                for (int run = 0; run < 500; run++)
                {
                    long dl = 0; double spent = 0; float unit = (float)(0.1 + r.NextDouble() * 5);
                    for (int k = 0; k < 30; k++)
                    {
                        long after = Math.Max(0, dl + r.Next(-3000, 9000));
                        float s = RM_DrillSurveyMath.SpentUnits(dl, after, U, unit);
                        Assert(s >= 0f, "never negative");
                        spent += s;
                        if (after > dl) dl = after;
                    }
                    double want = dl / (double)U * unit;
                    Assert(Math.Abs(spent - want) <= 1e-3 * Math.Max(1, want), "seed 13 run " + run + ": charged " + spent + " for " + dl + " dL landed (want " + want + ")");
                }
            });
        }
    }
}
