// Messy Conduit L5 (aerial lines) offline checks: the Verse-free half of the aerial feature
// (Source/Aerial/AerialMath.cs, the PRODUCTION file, compiled in directly). Design:
// design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 2. Called from Program.Main.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Aerial;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class AerialSelfTest
    {
        private static Action<bool, string> check;
        private static int mine, mineFails;

        private static void C(bool ok, string msg)
        {
            mine++;
            if (!ok) mineFails++;
            check(ok, "aerial: " + msg);
        }

        private static AnchorInfo A(int id, int x, int z, int faction = 0, int max = 4, params int[] linked) =>
            new AnchorInfo { Id = id, X = x, Z = z, Faction = faction, MaxLinks = max, Linked = new List<int>(linked) };

        public static void Run(Action<bool, string> chk)
        {
            check = chk;
            mine = mineFails = 0;
            Curve();
            Strands();
            Sway();
            Links();
            Spanning();
            Removal();
            Watchdog();
            Fallen();
            Explosion();
            Tap();
            CanFail();
            Console.WriteLine($"aerial: {mine - mineFails}/{mine} checks passed");
        }

        // ------------------------------------------------------------------ catenary-ish sag curve
        private static void Curve()
        {
            var a = new P2(10, 10);
            var b = new P2(22, 10);
            List<P2> pts = AerialMath.SpanCurve(a, b, 0.06);
            C(pts.Count >= 4, "span curve has samples (" + pts.Count + ")");
            if (pts.Count < 4) return;
            C(P2.Dist(pts[0], a) < 1e-9 && P2.Dist(pts[pts.Count - 1], b) < 1e-9, "span ends exactly at both insulators");
            int low = 0;
            for (int i = 1; i < pts.Count; i++) if (pts[i].Z < pts[low].Z) low = i;
            double tLow = (pts[low].X - a.X) / (b.X - a.X);
            C(Math.Abs(tLow - 0.5) < 0.06, "lowest point at t~0.5 (t=" + tLow.ToString("0.00") + ")");
            double sag12 = a.Z - pts[low].Z;
            C(Math.Abs(sag12 - 0.06 * 12) < 0.02, "sag = factor x length (" + sag12.ToString("0.000") + " vs 0.72)");
            List<P2> pts24 = AerialMath.SpanCurve(new P2(10, 10), new P2(34, 10), 0.06);
            double sag24 = 10 - pts24.Min(p => p.Z);
            C(Math.Abs(sag24 / sag12 - 2.0) < 0.05, "sag proportional to length (24 vs 12 cells: x" + (sag24 / sag12).ToString("0.00") + ")");
            double maxStep = 0;
            for (int i = 1; i < pts.Count; i++) maxStep = Math.Max(maxStep, P2.Dist(pts[i - 1], pts[i]));
            C(maxStep <= 0.6, "sampled about every 0.5 cell (max step " + maxStep.ToString("0.00") + ")");
            // a north-south span still droops screen-down (top-down fake height)
            List<P2> ns = AerialMath.SpanCurve(new P2(5, 5), new P2(5, 15), 0.06);
            C(ns.Any(p => p.Z < Math.Min(5, 15) + 5 - 0.001 && p.X == 5), "north-south span is sampled along its length");
            C(AerialMath.SpanCurve(a, b, 0.0).All(p => Math.Abs(p.Z - 10) < 1e-9), "sag 0 is a straight line");
        }

        private static void Strands()
        {
            List<StrandSpec> s1 = AerialMath.StrandsFor(12345, 3);
            List<StrandSpec> s2 = AerialMath.StrandsFor(12345, 3);
            C(s1.Count >= 1 && s1.Count <= 3, "1..3 strands per span (" + s1.Count + ")");
            C(s1.Count == s2.Count && s1.Zip(s2, (x, y) => x.SagMul == y.SagMul && x.Lateral == y.Lateral).All(v => v), "strands deterministic by seed");
            C(s1.All(s => s.SagMul >= 0.9 && s.SagMul <= 1.15 && Math.Abs(s.Lateral) <= 0.0401), "strand sag x0.9-1.15, lateral <= 0.04");
            C(AerialMath.StrandsFor(777, 1).Count == 1, "max strands 1 -> exactly one strand");
            var counts = new HashSet<int>();
            for (int seed = 0; seed < 60; seed++) counts.Add(AerialMath.StrandsFor(seed, 3).Count);
            C(counts.Count >= 2, "strand count varies by seed (" + string.Join(",", counts) + ")");
        }

        private static void Sway()
        {
            C(Math.Abs(AerialMath.Sway(0.0, 3.3, 1.0, 0.12, 7)) < 1e-9 && Math.Abs(AerialMath.Sway(1.0, 3.3, 1.0, 0.12, 7)) < 1e-9, "sway is 0 at both insulators");
            double peak = 0;
            for (double time = 0; time < 20; time += 0.05) peak = Math.Max(peak, Math.Abs(AerialMath.Sway(0.5, time, 1.0, 0.12, 7)));
            C(peak > 0.05 && peak <= 0.12 * 1.3 + 1e-9, "mid-span sways within amplitude (" + peak.ToString("0.000") + ")");
            C(Math.Abs(AerialMath.Sway(0.5, 3.3, 0.0, 0.12, 7)) < 1e-9, "no wind, no sway");
            C(AerialMath.Sway(0.5, 3.3, 1.0, 0.12, 7) == AerialMath.Sway(0.5, 3.3, 1.0, 0.12, 7), "sway deterministic in (t, time, seed)");
            C(AerialMath.Sway(0.5, 3.3, 1.0, 0.12, 7) != AerialMath.Sway(0.5, 3.3, 1.0, 0.12, 8), "seed changes the phase");
        }

        // ------------------------------------------------------------------ link rules
        private static void Links()
        {
            C(AerialMath.InRange(0, 0, 20, 0, 20) && !AerialMath.InRange(0, 0, 21, 0, 20), "range is inclusive at exactly range cells");
            C(AerialMath.InRange(0, 0, 12, 16, 20) && !AerialMath.InRange(0, 0, 12, 17, 20), "range is euclidean (12,16)=20 in, (12,17) out");
            C(AerialMath.CanLink(A(1, 0, 0), A(2, 10, 0), 20) == LinkVerdict.Ok, "two player anchors in range link");
            C(AerialMath.CanLink(A(1, 0, 0), A(2, 25, 0), 20) == LinkVerdict.OutOfRange, "beyond range refused");
            C(AerialMath.CanLink(A(1, 0, 0), A(1, 0, 0), 20) == LinkVerdict.Self, "self link refused");
            C(AerialMath.CanLink(A(1, 0, 0, 0, 4, 2), A(2, 5, 0, 0, 4, 1), 20) == LinkVerdict.AlreadyLinked, "duplicate link refused");
            C(AerialMath.CanLink(A(1, 0, 0, 0, 1, 9), A(2, 5, 0), 20) == LinkVerdict.FullA, "a full anchor refuses");
            C(AerialMath.CanLink(A(1, 0, 0), A(2, 5, 0, 0, 1, 9), 20) == LinkVerdict.FullB, "a full target refuses");
            C(AerialMath.CanLink(A(1, 0, 0, 0), A(2, 5, 0, 3), 20) == LinkVerdict.Foreign, "another faction's anchor refused (no grid merge)");
            var rf = A(2, 5, 0); rf.Roofed = true;
            C(AerialMath.CanLink(A(1, 0, 0), rf, 20) == LinkVerdict.Roofed, "a roofed anchor refuses");
            var na = A(2, 5, 0); na.IsAnchor = false;
            C(AerialMath.CanLink(A(1, 0, 0), na, 20) == LinkVerdict.NotAnchor, "a plain transmitter (their conduit) is not a link target");
            var others = new List<AnchorInfo> { A(2, 15, 0), A(3, 6, 0), A(4, 3, 0, 5), A(5, 2, 0, 0, 1, 77), A(6, 40, 0) };
            C(AerialMath.AutoLinkPick(A(1, 0, 0), others, 20) == 3, "auto-link picks the nearest VALID anchor (skips foreign 4, full 5)");
            C(AerialMath.AutoLinkPick(A(1, 0, 0), new List<AnchorInfo> { A(6, 40, 0) }, 20) == -1, "auto-link with nothing in range picks none");
            C(AerialMath.Owns(3, 9) && !AerialMath.Owns(9, 3), "a span is owned by the lower thing id");
        }

        private static void Spanning()
        {
            // a row of five anchors 8 apart plus one far away: the MST links the row as a chain (4 links), not all pairs
            var sel = new List<AnchorInfo> { A(1, 0, 0), A(2, 8, 0), A(3, 16, 0), A(4, 24, 0), A(5, 32, 0), A(6, 90, 0) };
            List<(int, int)> mst = AerialMath.MinimumSpanningLinks(sel, 20);
            C(mst.Count == 4, "MST over a 5-chain + 1 unreachable = 4 links (" + mst.Count + ")");
            C(mst.All(p => Math.Abs(sel.First(a => a.Id == p.Item1).X - sel.First(a => a.Id == p.Item2).X) == 8), "MST links only neighbours 8 apart");
            var star = new List<AnchorInfo> { A(1, 0, 0, 0, 2), A(2, 5, 0), A(3, -5, 0), A(4, 0, 5), A(5, 0, -5) };
            List<(int, int)> m2 = AerialMath.MinimumSpanningLinks(star, 20);
            int deg1 = m2.Count(p => p.Item1 == 1 || p.Item2 == 1);
            C(deg1 <= 2 && m2.Count == 4, "MST respects maxLinks (hub degree " + deg1 + ", links " + m2.Count + ")");
            var pre = new List<AnchorInfo> { A(1, 0, 0, 0, 4, 2), A(2, 8, 0, 0, 4, 1), A(3, 16, 0) };
            List<(int, int)> m3 = AerialMath.MinimumSpanningLinks(pre, 20);
            C(m3.Count == 1 && m3[0] == (2, 3), "MST keeps existing links and adds only the missing one");
        }

        // ------------------------------------------------------------------ the despawn gap (design 2.2)
        private static void Removal()
        {
            var spans = new List<(int, SpanState)> { (2, SpanState.Up), (3, SpanState.Up), (4, SpanState.Cut) };
            RemovalPlan k = AerialMath.PlanRemoval(1, true, spans);
            C(k.Reseed.OrderBy(x => x).SequenceEqual(new[] { 2, 3, 4 }), "kill: EVERY former partner is re-seeded (despawn gap)");
            C(k.Fallen.Count == 2 && k.Fallen.All(f => f.Survivor != 4 && f.TowardDead), "kill: each UP span falls onto its survivor; a CUT one already lies");
            RemovalPlan d = AerialMath.PlanRemoval(1, false, spans);
            C(d.Reseed.Count == 3 && d.Fallen.Count == 0, "dismantle: partners re-seeded, cable coiled (nothing falls)");
            C(AerialMath.PlanRemoval(1, true, new List<(int, SpanState)>()).Reseed.Count == 0, "an unlinked anchor re-seeds nothing");
            C(AerialMath.ReseedOnLinkChange(5, 9).OrderBy(x => x).SequenceEqual(new[] { 5, 9 }), "link/unlink/cut re-seeds both ends");
        }

        private static void Watchdog()
        {
            var reads = new List<SpanNetRead>
            {
                new SpanNetRead { Span = 0, State = SpanState.Up, NetA = 7, NetB = 7 },
                new SpanNetRead { Span = 1, State = SpanState.Up, NetA = 7, NetB = -1 },
                new SpanNetRead { Span = 2, State = SpanState.Up, NetA = 7, NetB = 8 },
                new SpanNetRead { Span = 3, State = SpanState.Cut, NetA = 7, NetB = 8 },
                new SpanNetRead { Span = 4, State = SpanState.Up, NetA = -1, NetB = -1 },
            };
            List<int> rep = AerialMath.WatchdogRepairs(reads);
            C(rep.OrderBy(x => x).SequenceEqual(new[] { 1, 2, 4 }), "watchdog repairs UP spans with a net-less or split end, never a cut span (" + string.Join(",", rep) + ")");
        }

        // ------------------------------------------------------------------ fallen span as a floor cord
        private static void Fallen()
        {
            Func<int, int, bool> open = (x, z) => true;
            FallenLay f = AerialMath.LayFallen(new P2(10.5, 10.5), new P2(22.5, 10.5), 12 * 1.05, 42, open);
            C(f.Pts.Count >= 4, "fallen cord has a polyline");
            if (f.Pts.Count < 4) return;
            double len = 0;
            for (int i = 1; i < f.Pts.Count; i++) len += P2.Dist(f.Pts[i - 1], f.Pts[i]);
            C(Math.Abs(len - 12.6) < 0.8, "fallen cord length ~ span x 1.05 (" + len.ToString("0.00") + ")");
            C(P2.Dist(f.Pts[0], new P2(10.5, 10.5)) < 1e-9, "fallen cord starts at the survivor's base");
            C(f.Tip.X > 18 && !f.Blocked, "on open ground it reaches toward the dead pole (tip x " + f.Tip.X.ToString("0.0") + ")");
            Func<int, int, bool> wall = (x, z) => x != 15;
            FallenLay g = AerialMath.LayFallen(new P2(10.5, 10.5), new P2(22.5, 10.5), 12.6, 42, wall);
            C(g.Blocked && g.Pts.All(p => (int)Math.Floor(p.X) != 15) && g.Tip.X < 15, "a wall stops the cord; the rest is 'over the wall' (no vertex in the wall)");
            FallenLay h = AerialMath.LayFallen(new P2(10.5, 10.5), new P2(22.5, 10.5), 12.6, 42, open);
            C(h.Pts.Count == f.Pts.Count && h.Pts.Zip(f.Pts, (p, q) => P2.Dist(p, q) < 1e-12).All(v => v), "fallen cord deterministic by seed");
            // B11 (owner review 2026-10-04): a cut wire still hangs from the pole TOP to the ground before it lies down
            var top = new P2(10.5, 10.5 + 2.66);
            int gi = AerialMath.GroundIndex(f.Pts);
            P2 ground = f.Pts[gi];
            List<P2> drop = AerialMath.FallenDrop(top, ground, 42);
            double dl = 0, maxZ = drop.Max(p => p.Z);
            for (int i = 1; i < drop.Count; i++) dl += P2.Dist(drop[i - 1], drop[i]);
            C(P2.Dist(drop[0], top) < 1e-9 && P2.Dist(drop[drop.Count - 1], ground) < 1e-9, "drop runs exactly from the insulator to the ground point");
            C(P2.Dist(f.Pts[0], ground) >= 0.35 - 1e-9 && P2.Dist(f.Pts[0], ground) < 0.7, "drop meets the ground 0.35-0.7 cell from the base");
            C(dl >= P2.Dist(top, ground) - 1e-9 && dl < P2.Dist(top, ground) * 1.2 && maxZ <= top.Z + 1e-9, "drop descends from the top, length " + dl.ToString("0.00"));
        }

        private static void Explosion()
        {
            var a = new P2(0, 0);
            var b = new P2(10, 0);
            C(AerialMath.SpanHit(a, b, new P2(5, 2), 2.5) && !AerialMath.SpanHit(a, b, new P2(5, 3), 2.5), "explosion hits a span whose ground line is within radius");
            C(Math.Abs(AerialMath.ClosestT(a, b, new P2(3, 4)) - 0.3) < 1e-9, "cut point = closest point on the span (t 0.3)");
            C(!AerialMath.SpanHit(a, b, new P2(-4, 0), 2.5), "beyond the end is a miss");
        }

        // ------------------------------------------------------------------ the one-way power tap
        private static void Tap()
        {
            double k = 1.6666667E-05;
            C(Math.Abs(AerialMath.TapStolenPerTick(500, 1000 * k, 0, k, false, true) - 500 * k) < 1e-12, "victim surplus 1000 W: tap takes its full 500 W");
            C(Math.Abs(AerialMath.TapStolenPerTick(500, 200 * k, 0, k, false, true) - 200 * k) < 1e-12, "victim surplus 200 W, no battery: tap takes only 200 W");
            C(Math.Abs(AerialMath.TapStolenPerTick(500, -100 * k, 600, k, false, true) - 500 * k) < 1e-12, "victim in deficit but with stored energy: batteries pay the full rate");
            C(AerialMath.TapStolenPerTick(500, -100 * k, 0, k, false, true) == 0, "victim with nothing to give: 0, never negative");
            C(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, true, true) == 0, "tapping our own net steals nothing");
            C(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, false, false) == 0, "taps disabled in settings: 0");
            C(Math.Abs(AerialMath.TapStolenPerTick(500, -100 * k, 300 * k, k, false, true) - 200 * k) < 1e-12, "deficit 100 W + 300 W-ticks stored: 200 W this tick");
        }

        // ------------------------------------------------------------------ a checker that cannot fail proves nothing
        private static void CanFail()
        {
            int before = mineFails;
            Action<bool, string> real = check;
            int planted = 0;
            check = (ok, msg) => { if (!ok) planted++; };
            C(AerialMath.CanLink(A(1, 0, 0), A(2, 25, 0), 20) == LinkVerdict.Ok, "planted: an out-of-range link reads Ok");
            C(AerialMath.SpanCurve(new P2(0, 0), new P2(10, 0), 0.06).All(p => p.Z == 0), "planted: a sagging span is straight");
            check = real;
            mineFails = before;
            mine -= 2;
            C(planted == 2, "sanity probe: both planted wrong expectations were detected (" + planted + "/2)");
        }
    }
}
