// The incident's "blocked in" phase (quietPhase, tps_record.md Acceptance item 2: every 2-10 s hitch names where the
// main thread was blocked). The watchdog wakes once per WatchdogPeriodSeconds and, when the main thread has been quiet
// longer than QuietTagSeconds, tags the phase it is in with the beat it measured against; the main thread's incident
// takes the tag only when that beat belongs to THIS gap. Live run J20261126T000829Z-98bb6f found 3 of 15 hitches of
// 2.05-2.25 s with no phase under the old rule (tag only when quiet > 1.5 s, untagged): a 2.0-2.5 s gap can end before
// any wakeup sees 1.5 s of quiet. This unit sweeps the regime, not examples: every gap length 2.01-10 s, every wakeup
// phase, sampling periods from the 1 s sleep up to 1.45 s (timer slack + a slow heartbeat write), the block before or
// after the frame's tick update, and stale tags left by earlier quiet frames.
using System;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        // One gap through the watchdog's wakeups. place < 0: the block runs in the frame BEFORE the gap, after its tick
        // update (its beat precedes g.Start by -place); place > 0: in the frame that ends the gap, before its tick update.
        private static string QuietSim(double G, double P, double o, double place, M.QuietTag stale, double thr, out double maxQ)
        {
            const double start = 100.0;
            var g = new M.Gap { Start = start, Seconds = G };
            double beat = start + place, end = start + G;
            M.QuietTag tag = stale;
            maxQ = 0;
            for (double s = start - 3.0 + o; s < end; s += P)
            {
                bool inGap = s > beat;
                double q = inGap ? s - beat : 0.016;          // before the block the main thread beats every frame
                if (inGap && q > maxQ) maxQ = q;
                var t = M.TagQuiet(inGap ? beat : s - q, q, "blk", thr);
                if (t != null) tag = t;
            }
            return M.QuietPhaseFor(g, tag);
        }

        private static void T_QuietPhaseSampledEveryGap()
        {
            double[] periods = { M.WatchdogPeriodSeconds, 1.016, 1.1, 1.25, 1.45 };
            double[] places = { -1.9, -0.3, -0.001, 0.001, 0.016 };
            var stales = new M.QuietTag[] { null, M.TagQuiet(100.0 - 40.0, 3.0, "stale-old"), M.TagQuiet(100.0 - 2.5, 0.9, "stale-near") };
            const int offsets = 20;
            long cases = 0, misses = 0, oldMisses = 0;
            double worst = double.MaxValue, oldWorstGap = 0;
            string firstMiss = null;
            for (int i = 201; i <= 1000; i++)
            {
                double G = i / 100.0;
                foreach (double P in periods)
                    for (int j = 0; j < offsets; j++)
                    {
                        double o = P * j / offsets;
                        foreach (double place in places)
                            foreach (var st in stales)
                            {
                                cases++;
                                string ph = QuietSim(G, P, o, place, st, M.QuietTagSeconds, out double maxQ);
                                worst = Math.Min(worst, maxQ - M.QuietTagSeconds);
                                if (ph == null || !ph.StartsWith("blk@", StringComparison.Ordinal))
                                {
                                    misses++;
                                    if (firstMiss == null) firstMiss = "G=" + G + " P=" + P + " o=" + o + " place=" + place + " got " + (ph ?? "null");
                                }
                                // the planted fault: the same sweep under the old rule must go red, or the sweep cannot see
                                if (P == M.WatchdogPeriodSeconds && st == null)
                                {
                                    string old = QuietSim(G, P, o, place, null, 1.5, out _);
                                    if (old == null) { oldMisses++; oldWorstGap = Math.Max(oldWorstGap, G); }
                                }
                            }
                    }
            }
            // the grid's offsets miss the exact worst wakeup (one lands AT the gap's end, the incident takes the tag first):
            // the bound is then the shortest gap less its block's head start and one period
            double bound = double.MaxValue;
            foreach (double P in periods) foreach (double place in places) bound = Math.Min(bound, 2.01 - Math.Max(place, 0) - P);
            Check(bound > M.QuietTagSeconds, "analytic worst sampled quiet " + M.F(bound, 3) + " s is not above the tag threshold");
            Check(misses == 0, misses + " of " + cases + " gaps without their own phase; first " + firstMiss);
            Check(worst > 0, "worst sampled quiet is only " + M.F(worst, 3) + " s over QuietTagSeconds");
            Check(oldMisses > 0, "the sweep cannot see the old rule's misses (quiet > 1.5 s, 1 s wakeups): 0 misses");
            // a gap no wakeup saw keeps NO phase: a stale tag never names another gap
            var g0 = new M.Gap { Start = 100.0, Seconds = 2.2 };
            Check(M.QuietPhaseFor(g0, stales[1]) == null, "a tag 40 s before the gap leaked into it");
            Check(M.QuietPhaseFor(g0, stales[2]) == null, "a tag 2.5 s before the gap leaked into it");
            Check(M.QuietPhaseFor(g0, null) == null, "no tag gave a phase");
            Check(M.QuietPhaseFor(g0, M.TagQuiet(102.3, 0.6, "late")) == null, "a tag after the gap's end leaked into it");
            Check(M.TagQuiet(100.0, M.QuietTagSeconds, "x") == null, "quiet AT the threshold tagged (want strictly above)");
            var t1 = M.TagQuiet(99.99, 2.149, "tl:Normal");
            Check(t1 != null && M.QuietPhaseFor(g0, t1) == "tl:Normal@2.1s", "own tag text: " + (t1 == null ? "null" : M.QuietPhaseFor(g0, t1)));
            Note = "worst sampled quiet " + M.F(worst + M.QuietTagSeconds, 3) + " s vs tag threshold " + M.F(M.QuietTagSeconds, 3) +
                   " s (limit: above; analytic worst " + M.F(bound, 3) + " s at a 1.45 s period), " + cases + " cases, " + misses + " misses; old rule (1.5 s): " + oldMisses +
                   " misses, longest missed gap " + M.F(oldWorstGap, 2) + " s";
        }
    }
}
