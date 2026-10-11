// POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK (owner 2026-10-10): the Verse-free half of the caught-theft goodwill leak
// (../Aerial/AerialMath.cs TheftSpotted / TheftGoodwillAccrue). The game half is Aerial/PowerTheftConsequences.cs.
using System;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class TheftChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "theft: " + msg);

        public static void Run()
        {
            Check(AerialMath.TheftSpotted(5, 12, true, true, false), "an awake victim 5 cells away with sight catches the clamp");
            Check(!AerialMath.TheftSpotted(13, 12, true, true, false), "13 cells is out of a 12-cell sight range");
            Check(!AerialMath.TheftSpotted(5, 12, false, true, false), "a wall between them hides the clamp");
            Check(!AerialMath.TheftSpotted(5, 12, true, false, false), "a sleeping or downed victim sees nothing");
            Check(!AerialMath.TheftSpotted(5, 12, true, true, true), "our own prisoner is no witness");
            Check(!AerialMath.TheftSpotted(double.NaN, 12, true, true, false) && !AerialMath.TheftSpotted(1, 0, true, true, false),
                  "NaN distance or zero range never catches");

            const int day = 60000, step = 250;
            int acc = 0, total = 0;
            for (int t = 0; t < day * 3; t += step) total += AerialMath.TheftGoodwillAccrue(ref acc, step, true, 2, day);
            Check(total == -6, "three days of caught draining at 2/day costs 6 goodwill (got " + total + ")");
            acc = 0; total = 0;
            for (int t = 0; t < day - step; t += step) total += AerialMath.TheftGoodwillAccrue(ref acc, step, true, 2, day);
            Check(total == 0 && acc == day - step, "less than a day costs nothing yet and the time is carried");
            total += AerialMath.TheftGoodwillAccrue(ref acc, step, true, 2, day);
            Check(total == -2 && acc == 0, "the tick that completes the day charges once and resets");
            acc = 100; total = 0;
            for (int t = 0; t < day * 5; t += step) total += AerialMath.TheftGoodwillAccrue(ref acc, step, false, 2, day);
            Check(total == 0 && acc == 100, "an idle clamp (not draining) accrues nothing: the drain stops when the theft stops");
            acc = 0;
            Check(AerialMath.TheftGoodwillAccrue(ref acc, day * 2, true, 0, day) == 0 && acc == 0, "a 0/day setting charges nothing");
            acc = 0;
            Check(AerialMath.TheftGoodwillAccrue(ref acc, day, true, 5, day) == -5, "the per-day setting is the charge");
            // can-fail: an energy-scaled rule (the stolen Wd) would charge a brief big theft more than a long small one; ours is time-only
            int a1 = 0, a2 = 0;
            int big = AerialMath.TheftGoodwillAccrue(ref a1, step, true, 2, day);
            int longSmall = 0; for (int t = 0; t < day; t += step) longSmall += AerialMath.TheftGoodwillAccrue(ref a2, step, true, 2, day);
            Check(big == 0 && longSmall == -2, "can-fail: steady means per day of draining, not per watt");
        }
    }

    /// <summary>GSS build-out 2026-10-10: the aerial "Wire sway" radio's Auto and Always used to behave identically (Auto
    /// meant CPU; no shader path for spans). Auto now follows the game's plant-sway option, Always overrides it.</summary>
    internal static class WireSwayModeChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "wireswaymode: " + msg);

        public static void Run()
        {
            Check(AerialMath.WireSwayPrefAllows(0, true) && !AerialMath.WireSwayPrefAllows(0, false), "Auto follows the plant-sway option");
            Check(AerialMath.WireSwayPrefAllows(1, true) && AerialMath.WireSwayPrefAllows(1, false), "Always sways with the option off");
            Check(!AerialMath.WireSwayPrefAllows(2, true) && !AerialMath.WireSwayPrefAllows(2, false), "Off never sways");
            bool differ = false;
            foreach (bool pref in new[] { true, false }) differ |= AerialMath.WireSwayPrefAllows(0, pref) != AerialMath.WireSwayPrefAllows(1, pref);
            Check(differ, "can-fail: Auto and Always are not the same setting");
        }
    }

    /// <summary>Design 2.5 drip loops (2026-10-10 build-out): AerialMath.SpanCurveDrip.</summary>
    internal static class DripLoopChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "driploop: " + msg);

        public static void Run()
        {
            var a = new P2(0, 0); var b = new P2(10, 0);   // east-west: a Z dip never moves the projected t
            var plain = AerialMath.SpanCurve(a, b, 0.06);
            var off = AerialMath.SpanCurveDrip(a, b, 0.06, 0, 0.45);
            Check(off.Count == plain.Count && off.Zip(plain, (p, q) => P2.Dist(p, q)).Max() < 1e-12, "depth 0 is exactly the plain span curve");
            var d = AerialMath.SpanCurveDrip(a, b, 0.06, 0.12, 0.45);
            Check(P2.Dist(d[0], a) < 1e-12 && P2.Dist(d[d.Count - 1], b) < 1e-12, "ends stay exactly on the insulators");
            double len = P2.Dist(a, b), sag = 0.06 * len;
            double Plain(double t) => a.Z + (b.Z - a.Z) * t - sag * 4 * t * (1 - t);
            double dipA = 0, dipB = 0, beyond = 0;
            foreach (P2 p in d)
            {
                double t = AerialMath.ProjectT(a, b, p), dist = Math.Min(t, 1 - t) * len, under = Plain(t) - p.Z;
                if (dist < 0.45) { if (t < 0.5) dipA = Math.Max(dipA, under); else dipB = Math.Max(dipB, under); }
                else beyond = Math.Max(beyond, Math.Abs(under));
            }
            Check(dipA > 0.10 && dipA <= 0.12 + 1e-9 && dipB > 0.10 && dipB <= 0.12 + 1e-9,
                  "a loop up to 0.12 cells deep hangs below EACH insulator (" + dipA.ToString("0.000") + ", " + dipB.ToString("0.000") + ")");
            Check(beyond < 1e-9, "beyond the loops the wire is the plain sag curve");
            Check(d.Zip(d.Skip(1), (p, q) => AerialMath.ProjectT(a, b, q) >= AerialMath.ProjectT(a, b, p) - 1e-12).All(x => x),
                  "samples run monotonically from A to B (sway pinning by projected t)");
            var shortSpan = AerialMath.SpanCurveDrip(new P2(0, 0), new P2(1, 0), 0.06, 0.12, 0.45);
            Check(shortSpan.All(p => !double.IsNaN(p.Z)) && shortSpan.Count >= 10, "a 1-cell span still lays (loop reach capped at a quarter span)");
            Check(AerialMath.ProjectT(a, b, a) == 0 && AerialMath.ProjectT(a, b, b) == 1 && AerialMath.ProjectT(a, b, new P2(-5, 0)) == 0, "ProjectT clamps");
        }
    }
}
