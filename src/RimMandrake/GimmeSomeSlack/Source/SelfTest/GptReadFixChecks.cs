// GPT source read 2026-10-06 (design/RimMandrake/gss_gpt_source_read_2026-10-06.md): one offline row per fixed finding whose
// logic is Verse-free (the Verse-bound fixes are checked by validation.py O7). Each row carries a can-fail: the old rule
// computed beside the new one must give the wrong answer the finding described.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class GptReadFixChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "gptfix: " + msg);

        public static void Run()
        {
            // B4: the reel's port cache starts at int.MinValue and must read as stale, not fresh
            Check(!HoseLive.CacheFresh(0, int.MinValue, 60), "B4 never-read port cache is stale at tick 0");
            Check(!HoseLive.CacheFresh(123456, int.MinValue, 60), "B4 never-read port cache is stale later in the game");
            Check(HoseLive.CacheFresh(100, 70, 60) && !HoseLive.CacheFresh(130, 70, 60), "B4 a read 30 ticks ago is fresh, 60 ago is not");
            Check(unchecked(0 - int.MinValue) < 60, "B4 can-fail: the old int subtraction overflows to fresh");

            // A19: lit and dark power strips draw at the same aspect (both PNGs are 64x32)
            Check(DecalAspect.Of(DecalKind.PowerStripDark) == DecalAspect.Of(DecalKind.PowerStrip) && DecalAspect.Of(DecalKind.PowerStrip) == 0.5f,
                  "A19 dark power strip aspect == lit == 0.5");
            Check(DecalAspect.Of(DecalKind.Plug) == 1f, "A19 can-fail: a square decal keeps aspect 1");

            // A1: two 500 W taps on a victim with 600 W surplus and no battery share 600 W, never 1000 W
            double k = 1.0 / 60000;
            double t1 = AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true, 0, true);
            double t2 = AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true, t1, true);
            Check(Math.Abs(t1 + t2 - 600 * k) < 1e-12, "A1 two taps share a 600 W surplus: " + ((t1 + t2) / k).ToString("0") + " W");
            Check(AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true) * 2 > 600 * k * 1.5, "A1 can-fail: the old rule lets both claim 500 W");
            Check(Math.Abs(AerialMath.TapStolenPerTick(500, 600 * k, 1000 * k, k, false, true, 500 * k, true) - 500 * k) < 1e-12,
                  "A1 the second tap still drinks from stored energy once the surplus is gone");
            // A2: a switched-off or broken clamp drains nothing
            Check(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, false, true, 0, false) == 0, "A2 switched-off tap takes 0");
            Check(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, false, true, 0, true) > 0, "A2 can-fail: the same tap switched on takes power");

            LeadOut();
            LayLength();
        }

        private static double MinBendUpTo(IList<V2> X, double upTo) => HoseMath.MinBendRadiusUpTo(X, HoseMath.EndSkip, upTo);

        /// <summary>B5, owner decision by question card 2026-10-06 (straight lead-out).</summary>
        private static void LeadOut()
        {
            // Dubins: lands on the target pose, never tighter than R, for every heading pair round a circle of targets
            int bad = 0, n = 0;
            for (int i = 0; i < 12; i++)
                for (int k = 0; k < 8; k++)
                {
                    double ang = i * Math.PI / 6, hk = k * Math.PI / 4;
                    var p1 = new V2(3 * Math.Cos(ang), 3 * Math.Sin(ang));
                    var h1 = new V2(Math.Cos(hk), Math.Sin(hk));
                    List<V2> d = HoseMath.Dubins(new V2(0, 0), new V2(-1, 0), p1, h1, 1.2, 0.0625);
                    n++;
                    if (d == null) { bad++; continue; }
                    var pl = new List<V2> { new V2(0, 0) }; pl.AddRange(d);
                    V2 last = pl[pl.Count - 1] - pl[pl.Count - 2];
                    if (V2.Dist(pl[pl.Count - 1], p1) > 1e-3 || Math.Abs(last.Norm().X - h1.X) + Math.Abs(last.Norm().Z - h1.Z) > 0.08 || HoseMath.MinBendRadius(pl, 0) < 1.2 * 0.97) bad++;
                }
            Check(bad == 0, "B5 Dubins lands on the pose and holds the radius in " + (n - bad) + "/" + n + " cases");
            // the old worst fuzz case (seed 2: a U-turn out of a west nozzle to a target behind and below): now straight, then round
            var c = GssFuzz.MakeHose(2, null);
            var prm = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay lay = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, prm, c.Seed, null, c.Reel.Outward);
            Check(lay.Ok && lay.Outlet && lay.LeadOutLen > 0, "B5 seed 2 lays with a lead-out (" + (lay.Reason ?? "ok") + ")");
            if (lay.Ok)
            {
                double S = HoseMath.LeadOutStraight(prm);
                double off = 0;
                double[] cs = Geo.CumLen(lay.Flat);
                for (int i = 0; i < lay.Flat.Count && cs[i] <= S; i++) off = Math.Max(off, Math.Abs(lay.Flat[i].Z - c.Reel.Mouth.Z));
                Check(off < 1e-6 && lay.Flat[1].X < c.Reel.Mouth.X, "B5 the first " + S.ToString("0.0") + " cells run dead straight out of the nozzle (off-line " + off.ToString("0.000") + ")");
                double mb = Math.Min(MinBendUpTo(lay.Flat, lay.LeadOutLen), MinBendUpTo(lay.Plump, lay.LeadOutLen));
                Check(mb >= c.MinR * 0.95, "B5 seed 2 lead-out bend " + mb.ToString("0.00") + " >= 0.95 x " + c.MinR.ToString("0.0") + " (was 0.33 with the 2R position blend)");
                // can-fail: the retired 2R position blend on the same flat hose bends far tighter
                var bent = new List<V2>(lay.Flat.Take(3)); bent.AddRange(new[] { lay.Flat[3] + new V2(0, 0.4) }); bent.AddRange(lay.Flat.Skip(4));
                Check(MinBendUpTo(bent, lay.LeadOutLen) < c.MinR * 0.95, "B5 can-fail: a kinked lead-out reads under the bar");
            }
            // a wall hard against the nozzle: refused with the reason, never laid without the lead-out
            var w = new CordWorld(30, 20);
            var reel = new HoseReelRect(10, 8, 2, 2);
            for (int z = 0; z < 20; z++) w.SetBlocked(new Cell(9, z), BlockKind.Wall);
            HoseLay blocked = HoseMath.Lay(w, reel.Mouth, new Cell(20, 9).Centre, new HoseShapeParams { MinBendRadius = 1.2 }, 7, null, reel.Outward);
            Check(!blocked.Ok && blocked.Reason == HoseMath.LeadOutBlocked, "B5 wall against the nozzle: refused '" + (blocked.Reason ?? "laid") + "'");
            HoseLay open = HoseMath.Lay(new CordWorld(30, 20), reel.Mouth, new Cell(20, 9).Centre, new HoseShapeParams { MinBendRadius = 1.2 }, 7, null, reel.Outward);
            Check(open.Ok && open.LeadOutLen > 0, "B5 can-fail: the same reel with the wall gone lays (" + (open.Reason ?? "ok") + ")");
        }

        /// <summary>B3: a laid hose is never longer than the hose; B2: the install check judges the shortest route.</summary>
        private static void LayLength()
        {
            // seed 13 was the G1 reproducer (hose 11.6 laid 12.70 out of the outlet)
            var c = GssFuzz.MakeHose(13, null);
            var prm = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay lay = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, prm, c.Seed, null, c.Reel.Outward);
            Check(!lay.Ok || Math.Max(lay.FlatLen, lay.PlumpLen) <= c.MaxLen + 1e-6, "B3 seed 13 laid " + (lay.Ok ? Math.Max(lay.FlatLen, lay.PlumpLen).ToString("0.00") : "refused: " + lay.Reason) + " within the hose " + c.MaxLen.ToString("0.00"));
            var big = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = double.PositiveInfinity, Slack = 1.0, PlumpAmount = 1.0 };
            HoseLay free = HoseMath.Lay(c.W, c.Reel.Mouth, c.Target.Centre, big, c.Seed, null, c.Reel.Outward);
            Check(free.Ok && Math.Max(free.FlatLen, free.PlumpLen) > c.MaxLen, "B3 can-fail: with no length cap the same lay runs " + (free.Ok ? Math.Max(free.FlatLen, free.PlumpLen).ToString("0.00") : "-") + ", over " + c.MaxLen.ToString("0.00"));
            Check(HoseMath.Overlong(new HoseLay { FlatLen = 12.7, PlumpLen = 12 }, 11.6) && !HoseMath.Overlong(new HoseLay { FlatLen = 11.5, PlumpLen = 11 }, 11.6), "B3 Overlong reads the longer pose");
        }
    }
}
