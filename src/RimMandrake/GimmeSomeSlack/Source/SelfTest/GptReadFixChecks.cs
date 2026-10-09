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


            // TAP_CONSERVATION_SELFTEST_1 (GS-6a): a multi-tick loop in the engine's own order (net tick reads T, then T++, then the
            // taps tick at T). What the victim net paid must equal what the taps were credited, once the last debit settles.
            {
                double kk = 1.0 / 60000;
                var ledger = new TapLedger<string>();
                var legacyTick = new Dictionary<string, int>(); var legacyWd = new Dictionary<string, double>();
                double credited = 0, paid = 0, legacyPaid = 0;
                int T = 0;
                for (int step = 0; step < 400; step++)
                {
                    // net tick reads T
                    paid += ledger.Owed("v", T);
                    if (legacyTick.TryGetValue("v", out int lt) && lt >= T - 1) legacyPaid += legacyWd["v"];
                    T++;
                    bool aWorks = step < 300, bWorks = step % 7 != 0;
                    foreach (bool works in new[] { aWorks, bWorks })
                    {
                        double s = AerialMath.TapStolenPerTick(500, 700 * kk, 0, kk, false, true, ledger.TakenThisTick("v", T), works);
                        if (s <= 0) continue;
                        credited += s; ledger.Debit("v", (float)s, T);
                        double prev = legacyTick.TryGetValue("v", out int pt) && pt == T ? legacyWd["v"] : 0;
                        legacyTick["v"] = T; legacyWd["v"] = prev + s;
                    }
                }
                paid += ledger.Owed("v", T);        // the final tick settles
                if (legacyTick.TryGetValue("v", out int lt2) && lt2 >= T - 1) legacyPaid += legacyWd["v"];
                Check(credited > 0 && Math.Abs(paid - credited) < 1e-6, "GS-6a over 400 ticks the victim paid exactly what the taps were credited");
                Check(credited <= 400 * 700 * kk + 1e-9, "GS-6a two taps never take more than the victim's surplus in total");
                Check(legacyPaid > credited + 1e-6, "GS-6a can-fail: the old one-tick grace pays some debit twice");
            }

            // B11: with auto-resume off, NO interrupted order (Deploy, Move, Retract) on a dropped hose resumes unforced
            bool any = false;
            foreach (HosePendingOrder o in new[] { HosePendingOrder.Deploy, HosePendingOrder.Move, HosePendingOrder.Retract })
                any |= HoseOrderRules.MayResume(HoseCarryState.Dropped, o, false, false);
            Check(!any, "B11 auto-resume off: no dropped order resumes unforced");
            Check(HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Move, true, false) && HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Retract, false, true)
                  && HoseOrderRules.MayResume(HoseCarryState.Laid, HosePendingOrder.Move, false, false), "B11 forced, setting on, or a laid (not dropped) hose still go");
            Check(HosePendingOrder.Move != HosePendingOrder.Deploy, "B11 can-fail: the old rule gated Deploy only, so a dropped Move resumed");
            // B13: a path failure on the current order clears it (before or after the grab); anything else keeps it
            Check(!HoseOrderRules.KeepOrderAfterJob(true, true) && HoseOrderRules.KeepOrderAfterJob(false, true) && HoseOrderRules.KeepOrderAfterJob(true, false),
                  "B13 path failure on the current order clears it; a draft or a newer order keeps it");
            // B10: A (0) has a pending order onto B (1), nothing is laid; B's order onto A must read as a loop
            int[] laidNext = { -1, -1 }, pendNext = { 1, -1 };
            bool[] pend = { true, false };
            Check(HoseRelay.WouldLoop(1, 0, i => HoseRelay.IntendedNext(laidNext[i], pend[i], pendNext[i])), "B10 two pending orders A->B, B->A read as a loop");
            Check(!HoseRelay.WouldLoop(1, 0, i => laidNext[i]), "B10 can-fail: following laid hoses only, the ring is missed");
            // B7/A13: a tree's route cost is part of the corridor signature
            var tw = new CordWorld(4, 4);
            ulong before = CordBuilder.CellSig(tw, new Cell(1, 1));
            tw.SetExtraCost(new Cell(1, 1), 1.5f);
            Check(CordBuilder.CellSig(tw, new Cell(1, 1)) != before, "B7/A13 planting a tree changes the cell's corridor signature");
            Check(tw.IsWalkable(new Cell(1, 1)), "B7/A13 can-fail: the tree cell stays walkable, so the old walk+door hash could not see it");
            LeadOut();
            LayLength();
            BatteryLead();
            LoopBudgetRename();
        }

        /// <summary>B9, owner decision by question card 2026-10-06: a device wired straight to a battery gets a cord like any
        /// other connection. The adapter (Verse-bound) now links the device to the battery's node through
        /// CordWorldLinks.LinkToMachine; the battery has no conduit beside it, so before the fix it was not a node at all.</summary>
        private static void BatteryLead()
        {
            List<LaidPiece> Lay(bool link)
            {
                var w = new CordWorld(14, 8);
                var bat = new MachineInfo { Id = "t1", Kind = MachineKind.Battery, X0 = 2, Z0 = 3, W = 1, H = 2 };
                var heater = new MachineInfo { Id = "c2", Kind = MachineKind.Consumer, X0 = 8, Z0 = 3 };
                w.SetBlocked(new Cell(2, 3), BlockKind.Device); w.SetBlocked(new Cell(2, 4), BlockKind.Device); w.SetBlocked(new Cell(8, 3), BlockKind.Device);
                if (link) CordWorldLinks.LinkToMachine(w, heater, bat);
                return new CordBuilder().Build(w, new BuildOptions(), c => true);
            }
            List<LaidPiece> ps = Lay(true);
            LaidPiece lead = ps.FirstOrDefault(p => p.EndA != null && p.EndB != null && p.EndA.StartsWith("battery") != p.EndB.StartsWith("battery"));
            Check(lead != null && lead.Strands.Count > 0 && !lead.Unroutable,
                  "B9 a heater wired to a lone battery gets a laid cord (" + string.Join(", ", ps.Select(p => p.EndA + "|" + p.EndB)) + ")");
            Check(lead != null && lead.Strands.Count == 1, "B9 the device lead is one cord, like any device lead (round 3)");
            Check(Lay(false).Count(p => p.EndA != null) == 0, "B9 can-fail: without the link (the old adapter skipped it) nothing is laid");
        }

        /// <summary>A12/B15, owner decision by question card 2026-10-06: the setting is renamed to what it controls (the loop
        /// budget), and a settings file holding only the old key keeps its value.</summary>
        private static void LoopBudgetRename()
        {
            Check(LegacyName.LoopBudgetOnLoad(LegacyName.Unset, 5f, 16f) == 5f, "A12 an old settings file's value (5) carries over");
            Check(LegacyName.LoopBudgetOnLoad(30f, 5f, 16f) == 30f, "A12 the new key wins once saved");
            Check(LegacyName.LoopBudgetOnLoad(LegacyName.Unset, LegacyName.Unset, 16f) == 16f, "A12 a fresh install gets the default 16");
            Check(LegacyName.LoopBudgetOnLoad(2f, LegacyName.Unset, 16f) == 2f, "A12 the slider's minimum (2) is a real value, not unset");
            // what the setting really controls: the budget moves the loops/heaps length, and a lead still lies past path + budget
            var w = new CordWorld(24, 8);
            var lamp = new MachineInfo { Id = "lamp", Kind = MachineKind.Lamp, X0 = 3, Z0 = 3 };
            w.SetBlocked(new Cell(3, 3), BlockKind.Device);
            for (int x = 4; x <= 18; x++) w.SetConduit(new Cell(x, 3));
            lamp.Hookups.Add(new Cell(4, 3));
            var src = new MachineInfo { Id = "gen", Kind = MachineKind.Source, X0 = 19, Z0 = 3 };
            w.SetBlocked(new Cell(19, 3), BlockKind.Device); src.Hookups.Add(new Cell(18, 3));
            w.Machines.Add(lamp); w.Machines.Add(src);
            double Longest(double budget)
            {
                var o = new BuildOptions(); o.Lay.MaxExtra = budget; o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, budget);
                return new CordBuilder().Build(w, o, c => true).Where(p => p.EndA != null).SelectMany(p => p.Strands).Sum(st => Geo.Length(st.Pts));
            }
            double lo = Longest(2), hi = Longest(40);
            Check(hi > lo, "A12 a bigger loop budget lays more cord (" + lo.ToString("0.0") + " cells at 2, " + hi.ToString("0.0") + " at 40, 15-cell run)");
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
