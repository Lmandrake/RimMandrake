// Colonist-carried hose, stage S4 (live drawing) selftest: the end-kind rule, the carried hose's prefix + tail geometry,
// the retract clip and the animated auto-retract (design/RimMandrake/hose_carry_design_2026-10-04.md sections 6-7).
// Every row has a can-fail: a mutated input the same assertion must reject.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class HoseLiveChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hoselive: " + msg);

        private static double MaxGap(IList<V2> p)
        {
            double m = 0;
            for (int i = 1; i < p.Count; i++) m = Math.Max(m, V2.Dist(p[i - 1], p[i]));
            return m;
        }

        public static void Run()
        {
            // 1. section 7 end-kind rule, exhaustive over the 16 inputs, against an independent spec (priority Relay > Port > Water)
            int bad = 0;
            for (int m = 0; m < 16; m++)
            {
                bool o = (m & 1) != 0, rl = (m & 2) != 0, pt = (m & 4) != 0, wa = (m & 8) != 0;
                HoseEndKind want = !o ? HoseEndKind.None : rl ? HoseEndKind.Relay : pt ? HoseEndKind.Port : wa ? HoseEndKind.Water : HoseEndKind.Free;
                if (HoseLive.EndKind(o, rl, pt, wa) != want) bad++;
            }
            Check(bad == 0, "end kind: all 16 (out, relay, port, water) inputs follow Relay > Port > Water > Free (bad " + bad + ")");
            Check(HoseLive.EndKind(true, false, true, true) != HoseEndKind.Water, "end kind can-fail: a tank beside a pond reads Port, never Water");

            // 2. carried hose: prefix along a walked L-trail (east 8, then north 6) pulled taut + rounded, tail to the hand
            var w = new CordWorld(40, 40);
            for (int z = 0; z < 6; z++) w.SetBlocked(new Cell(6, z), BlockKind.Wall);   // a wall stub the L walks round
            var t = new HoseTrail(new V2(1.0, 7.5), double.PositiveInfinity);
            for (int x = 1; x <= 9; x++) t.Cells.Add(new Cell(x, 7));
            for (int z = 8; z <= 13; z++) t.Cells.Add(new Cell(9, z));
            List<V2> pulled = t.Pulled(w);
            List<V2> pre = HoseLive.Prefix(pulled, 1.2, HoseLive.SampleNear, out V2 corner);
            Check(V2.Dist(pre[0], new V2(1.0, 7.5)) < 1e-9, "carry prefix starts at the reel mouth");
            Check(V2.Dist(corner, new Cell(9, 13).Centre) < 1e-9, "carry prefix's corner is the last trail cell's centre");
            double back = V2.Dist(pre[pre.Count - 1], corner);
            Check(back > 0.3 && back < HoseLive.JunctionBack + 0.05, "carry prefix stops ~0.5 before the corner (" + back.ToString("0.###") + ")");
            Check(MaxGap(pre) <= HoseLive.SampleNear + 1e-6, "carry prefix sampled at <= 0.25 (" + MaxGap(pre).ToString("0.###") + ")");
            Check(HoseMath.Clear(w, pre, 0), "carry prefix never crosses the wall stub it was walked round");
            // the pawn mid-way into the next cell north
            var hand = new V2(9.5, 14.2);
            List<V2> tail = HoseLive.Tail(pre[pre.Count - 1], corner, hand, HoseLive.SampleNear);
            Check(V2.Dist(tail[0], pre[pre.Count - 1]) < 1e-9 && V2.Dist(tail[tail.Count - 1], hand) < 1e-9, "carry tail joins the prefix and ends at the hand");
            Check(MaxGap(tail) <= HoseLive.SampleNear + 1e-6, "carry tail is continuous (max gap " + MaxGap(tail).ToString("0.###") + ")");
            double tl = Geo.Length(tail), direct = back + V2.Dist(corner, hand);
            Check(tl <= direct + 1e-6 && tl >= V2.Dist(tail[0], hand) - 1e-6, "carry tail is no longer than via the corner and no shorter than the chord");
            // can-fail: a hand AT the corner gives a tail that ends on the corner (not a dangling hook)
            List<V2> t0 = HoseLive.Tail(pre[pre.Count - 1], corner, corner, HoseLive.SampleNear);
            Check(V2.Dist(t0[t0.Count - 1], corner) < 1e-9, "carry tail with the pawn on the corner ends on the corner");
            // the carried line follows the walk ROUND an obstacle: a second walk goes north past the top of a wall, east,
            // then south behind it; the hose wraps the wall's end (pulled taut over the walked cells, as the length and the
            // dropped lay are measured), it never chords through the wall
            var w2 = new CordWorld(40, 40);
            for (int z = 0; z <= 10; z++) w2.SetBlocked(new Cell(5, z), BlockKind.Wall);
            var t2 = new HoseTrail(new V2(1.0, 3.5), double.PositiveInfinity);
            for (int z = 3; z <= 12; z++) t2.Cells.Add(new Cell(1, z));
            for (int x = 2; x <= 9; x++) t2.Cells.Add(new Cell(x, 12));
            for (int z = 11; z >= 3; z--) t2.Cells.Add(new Cell(9, z));
            List<V2> pre2 = HoseLive.Prefix(t2.Pulled(w2), 1.2, HoseLive.SampleNear, out V2 cn2);
            var all2 = new List<V2>(pre2); all2.AddRange(HoseLive.Tail(pre2[pre2.Count - 1], cn2, new V2(9.5, 2.9), 0.25).Skip(1));
            Check(HoseMath.Clear(w2, all2, 0) && all2.Max(p => p.Z) > 10.9, "carried line wraps the wall it was walked round (top z " + all2.Max(p => p.Z).ToString("0.##") + ")");
            Check(!HoseMath.Clear(w2, Geo.Resample(new List<V2> { new V2(1.0, 3.5), new V2(9.5, 2.9) }, 0.25), 0), "carried line can-fail: the reel-to-hand chord crosses the wall");
            var all = new List<V2>(pre); all.AddRange(tail.Skip(1));
            // u continuity: the tail's s0 continues the prefix's texture
            double s0 = HoseLive.ContinueS0(0.37, Geo.Length(pre), 0.3);
            Check(Math.Abs(s0 * 4 - (0.37 * 4 + Geo.Length(pre) / (0.3 * 4))) < 1e-9, "tail texture u continues the prefix's");
            // LOD: far sampling halves the prefix's sample count (roughly)
            List<V2> preFar = HoseLive.Prefix(pulled, 1.2, HoseLive.SampleFar, out _);
            Check(preFar.Count < pre.Count * 0.6, "LOD: far-zoom prefix has about half the samples (" + preFar.Count + " vs " + pre.Count + ")");
            // a one-cell trail (just grabbed): prefix is the mouth alone, the tail runs mouth -> hand
            var t1 = new HoseTrail(new V2(1.0, 7.5), double.PositiveInfinity); t1.Cells.Add(new Cell(2, 7));
            List<V2> p1 = HoseLive.Prefix(t1.Pulled(w), 1.2, 0.25, out V2 c1);
            List<V2> tl1 = HoseLive.Tail(p1[p1.Count - 1], c1, new V2(2.9, 7.5), 0.25);
            Check(V2.Dist(p1[0], new V2(1.0, 7.5)) < 1e-9 && V2.Dist(tl1[0], p1[p1.Count - 1]) < 1e-9 && V2.Dist(tl1[tl1.Count - 1], new V2(2.9, 7.5)) < 1e-9, "just grabbed: the hose runs from the mouth to the hand");

            // 3. retract clip: winding w of a total T leaves (1 - w/T) of the drawn pose, one sample of tolerance
            List<V2> lay = Geo.Resample(all, 0.25);
            double L = Geo.Length(lay), T = 17.3;
            int clipBad = 0;
            foreach (double wd in new[] { 0.0, 1.0, 4.5, 8.0, 12.25, 17.0, 17.3, 30.0 })
            {
                List<V2> c = HoseLive.ClipWound(lay, wd, T);
                double want = Math.Max(0, L * (1 - Math.Min(1, wd / T)));
                if (Math.Abs(Geo.Length(c) - want) > 0.25 + 1e-6 && !(want < 0.05 && c.Count == 2)) clipBad++;
                if (V2.Dist(c[0], lay[0]) > 1e-9) clipBad++;
            }
            Check(clipBad == 0, "retract clip: drawn length = (1 - wound/total) of the pose within one sample, from the reel end (bad " + clipBad + ")");
            List<V2> half = HoseLive.ClipWound(lay, T / 2, T);
            Check(Math.Abs(Geo.Length(half) - L / 2) < 0.26 && Math.Abs(Geo.Length(half) - L) > 1, "retract clip can-fail: half wound is not the full hose");
            var joints = new List<int> { 3, 20, half.Count - 2, half.Count + 5 };
            Check(HoseLive.JointsWithin(joints, half.Count).SequenceEqual(new[] { 3, 20 }), "joiners past the clip are not drawn");

            // 4. animated auto-retract of a cut 30-cell hose: 3 cells/s, monotone, done at 600 ticks, not before
            Check(!HoseLive.AutoDone(599, 30) && HoseLive.AutoDone(600, 30), "auto-retract: a 30-cell hose winds in over 600 ticks (10 s)");
            double prev = -1; bool mono = true;
            for (int k = 0; k <= 600; k += 30) { double a = HoseLive.AutoWound(k); if (a < prev) mono = false; prev = a; }
            Check(mono && HoseLive.AutoWound(-5) == 0, "auto-retract wound length is monotone from 0");
        }
    }
}
