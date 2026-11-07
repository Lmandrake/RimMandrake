// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// cord_shape_variation_probe (GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE): how alike two laid cords of about one length are. Each edge's
// first strand is sampled by arc length into its own frame (start at the origin, the far end along +X, in cells), so a cord
// moved or turned on the map reads as itself; the distance is the mean point gap between two samples, the smallest over running
// either way and mirrored. Shared by the offline SelfTest and the live probe ("shapetable"), so the same number is proved in both.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public sealed class ShapeClass
    {
        public int Length, Cords, Pairs, TooAlike;
        public double MinDistance = double.MaxValue, MeanDistance;
        public string ClosestA, ClosestB;
    }

    public static class CordShape
    {
        public const int Samples = 48;
        /// <summary>Length classes are this many cells wide: edges of one class lie side by side as "the same cord".</summary>
        public const int ClassWidth = 2;
        /// <summary>Below this mean gap (cells) two cords read as one stamped curve; a cord is 0.08 wide and a loop 0.6-1 across.</summary>
        public const double TooAlikeBelow = 0.3;

        internal static double[] Sample(List<V2> pts)
        {
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            var o = new double[Samples * 2];
            V2 a = pts[0], ax = (pts[pts.Count - 1] - a).Norm();
            if (ax.Len < 0.5) ax = new V2(1, 0);
            V2 up = ax.Perp;
            int k = 0;
            for (int i = 0; i < Samples; i++)
            {
                // by exact arc length, so a cord run the other way samples the same points
                double at = L * i / (Samples - 1);
                while (k < pts.Count - 2 && cum[k + 1] < at) k++;
                double seg = cum[k + 1] - cum[k], t = seg > 1e-9 ? (at - cum[k]) / seg : 0;
                V2 d = pts[k] + (pts[k + 1] - pts[k]) * t - a;
                o[2 * i] = d.X * ax.X + d.Z * ax.Z;
                o[2 * i + 1] = d.X * up.X + d.Z * up.Z;
            }
            return o;
        }

        /// <summary>The mean point gap between two samples, the smallest of running the same way, the other way, and mirrored.</summary>
        internal static double Distance(double[] a, double[] b)
        {
            double best = double.MaxValue, span = a[2 * (Samples - 1)];
            foreach (bool rev in new[] { false, true })
                foreach (bool mir in new[] { false, true })
                {
                    double sum = 0;
                    for (int i = 0; i < Samples; i++)
                    {
                        int j = rev ? Samples - 1 - i : i;
                        double bx = b[2 * j], bz = b[2 * j + 1];
                        if (rev) { bx = b[2 * (Samples - 1)] - bx; bz = -bz; }
                        if (mir) bz = -bz;
                        double dx = a[2 * i] - bx, dz = a[2 * i + 1] - bz;
                        sum += Math.Sqrt(dx * dx + dz * dz);
                    }
                    best = Math.Min(best, sum / Samples);
                }
            return best;
        }

        /// <summary>A fold is two arms meeting at a point: the heading turns past KinkDeg over KinkArc either side of it, and each arm
        /// holds its line (within KinkArmDeg) on out to KinkArm. The arms are what tell it from a coil, whose heading never stops
        /// turning: a heap's tight coils are the art, and a fold is a spike or an elbow the ribbon cannot draw.</summary>
        public const double KinkArc = 0.1, KinkDeg = 60, KinkArm = 0.3, KinkArmDeg = 45;

        private static double TurnDeg(V2 u, V2 v)
        {
            if (u.Len < 1e-6 || v.Len < 1e-6) return 0;
            double cos = (u.X * v.X + u.Z * v.Z) / (u.Len * v.Len);
            return Math.Acos(Math.Max(-1, Math.Min(1, cos))) * 180 / Math.PI;
        }

        private static int AtArc(double[] cum, int from, double arc)
        {
            int j = from;
            if (arc < 0) while (j > 0 && cum[from] - cum[j] < -arc) j--;
            else while (j < cum.Length - 1 && cum[j] - cum[from] < arc) j++;
            return j;
        }

        /// <summary>Where a strand folds back on itself. The ends are skipped: they are the art's (plugs, frays, wall plates).</summary>
        internal static List<V2> Kinks(List<V2> pts, double skipEnds = 0.25)
        {
            var o = new List<V2>();
            if (pts == null || pts.Count < 5) return o;
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1], last = double.MinValue;
            if (L < 1.2) return o;                       // a machine's lead from the strip beside it: under the plug and the machine's art
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i] < skipEnds || cum[i] > L - skipEnds || cum[i] - last < 0.3) continue;
                int a = AtArc(cum, i, -KinkArc), b = AtArc(cum, i, KinkArc), a2 = AtArc(cum, i, -KinkArm), b2 = AtArc(cum, i, KinkArm);
                V2 u = pts[i] - pts[a], v = pts[b] - pts[i];
                if (TurnDeg(u, v) < KinkDeg) continue;
                if (TurnDeg(pts[a] - pts[a2], u) > KinkArmDeg || TurnDeg(v, pts[b2] - pts[b]) > KinkArmDeg) continue;
                o.Add(pts[i]);
                last = cum[i];
            }
            return o;
        }

        /// <summary>A jag is the heading kicking one way past JagDeg over JagArc and straight back within JagSpan. A coil turns one way only and a real bend is far longer,
        /// so neither reads as one. The settle leaves these where it bunches spare length in a straight stretch: a rope buckling, which a ribbon draws as a sawtooth.</summary>
        public const double JagArc = 0.08, JagDeg = 22, JagSpan = 0.3, JagReach = 0.3;

        private static double SignedTurnDeg(V2 u, V2 v)
        {
            if (u.Len < 1e-6 || v.Len < 1e-6) return 0;
            return Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z) * 180 / Math.PI;
        }

        /// <summary>Where a strand's heading jags. The ends are skipped: they are the art's (plugs, frays, wall plates).</summary>
        internal static List<int> Jags(List<V2> pts, double skipEnds = 0.25)
        {
            var o = new List<int>();
            if (pts == null || pts.Count < 7) return o;
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            var turn = new double[pts.Count];
            for (int i = 1; i < pts.Count - 1; i++)
                turn[i] = SignedTurnDeg(pts[i] - pts[AtArc(cum, i, -JagArc)], pts[AtArc(cum, i, JagArc)] - pts[i]);
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i] < skipEnds || cum[i] > L - skipEnds || Math.Abs(turn[i]) < JagDeg) continue;
                for (int j = i + 1; j < pts.Count - 1 && cum[j] - cum[i] <= JagSpan && cum[j] <= L - skipEnds; j++)
                    if (Math.Abs(turn[j]) >= JagDeg && turn[j] * turn[i] < 0)
                    {
                        o.Add(i);
                        i = j;
                        break;
                    }
            }
            return o;
        }

        /// <summary>Stretches of sawtooth: three or more jags in a row, each within SawGap of the last. One or two are the neck of a loop, where it leaves the run and comes back.</summary>
        public const double SawGap = 0.8;

        internal static int Saws(List<V2> pts)
        {
            List<int> at = Jags(pts);
            if (at.Count < 3) return 0;
            double[] cum = Geo.CumLen(pts);
            int saws = 0, run = 1;
            for (int k = 1; k < at.Count; k++)
            {
                run = cum[at[k]] - cum[at[k - 1]] <= SawGap ? run + 1 : 1;
                if (run == 3) saws++;
            }
            return saws;
        }

        /// <summary>Relax every jag into the line either side of it, leaving the rest of the strand where it lies. A point the relaxing would put off walkable ground stays.</summary>
        internal static List<V2> Dejag(CordWorld w, List<V2> pts, double skipEnds = 0.25)
        {
            List<V2> P = pts;
            for (int guard = 0; guard < 12; guard++)
            {
                List<int> at = Jags(P, skipEnds);
                if (at.Count == 0) return P;
                double[] cum = Geo.CumLen(P);
                var Q = new List<V2>(P);
                foreach (int c in at)
                {
                    int a = Math.Max(1, AtArc(cum, c, -JagReach)), b = Math.Min(P.Count - 2, AtArc(cum, c, JagReach));
                    for (int it = 0; it < 6; it++)
                    {
                        var prev = new List<V2>(Q);
                        for (int i = a; i <= b; i++)
                        {
                            double fade = Math.Min(1, Math.Min(i - a + 1, b - i + 1) / 3.0);
                            V2 q = prev[i] + ((prev[i - 1] + prev[i + 1]) * 0.5 - prev[i]) * (0.5 * fade);
                            if (w == null || w.IsWalkable(q.Floor)) Q[i] = q;
                        }
                    }
                }
                P = Q;
            }
            return P;
        }

        /// <summary>A cord reads as more cords than it is where it runs back alongside itself: two straight stretches at least DoubledGapArc apart along the cord, within
        /// DoubledNear of each other and within about 30 degrees of the same line (owner 2026-11-07: "three separate cables ... to a single terminal"; one cord out past a heater,
        /// back to the junction and out again drew three parallel lines between them). Straight is what tells it from a coil, whose sides never hold a line.</summary>
        public const double DoubledNear = 1.1, DoubledGapArc = 1.5, DoubledStraightArc = 0.6, DoubledStraightDeg = 25, DoubledCos = 0.86, DoubledMax = 1.2;
        private const double DoubledStep = 0.15;

        /// <summary>The longest stretch of this strand, in cells, running alongside another stretch of itself. Over <see cref="DoubledMax"/> it reads as a second cord.</summary>
        internal static double Doubled(List<V2> pts)
        {
            if (pts == null || pts.Count < 8) return 0;
            List<V2> q = Geo.Resample(pts, DoubledStep);
            int n = q.Count, reach = (int)Math.Round(DoubledStraightArc / DoubledStep);
            if (n <= 2 * reach + 1) return 0;
            var straight = new bool[n];
            var dir = new V2[n];
            for (int i = reach; i < n - reach; i++)
            {
                V2 u = q[i] - q[i - reach], v = q[i + reach] - q[i];
                straight[i] = TurnDeg(u, v) <= DoubledStraightDeg;
                dir[i] = (q[i + reach] - q[i - reach]).Norm();
            }
            // the longest unbroken stretch alongside: a coil's flat side beside a straight run is a touch, not a second cord
            int gap = (int)Math.Round(DoubledGapArc / DoubledStep), hits = 0, run = 0;
            for (int i = reach; i < n - reach; i++)
            {
                bool along = false;
                if (straight[i])
                    for (int j = reach; j < n - reach && !along; j++)
                        along = Math.Abs(i - j) >= gap && straight[j] && V2.Dist(q[i], q[j]) <= DoubledNear
                            && Math.Abs(dir[i].X * dir[j].X + dir[i].Z * dir[j].Z) >= DoubledCos;
                run = along ? run + 1 : 0;
                hits = Math.Max(hits, run);
            }
            return hits * DoubledStep;
        }

        /// <summary>Times a strand goes under a door beyond what its route asks: once for a door the planned line runs through, never for any other. A slack excursion that wanders under a door
        /// comes out the far side and back again, and from above each pass is one more cable out of that doorway (owner 2026-11-07: "three separate cables coming out of a doorway").</summary>
        internal static int DoorStrays(CordWorld w, List<V2> pts, List<V2> plan)
        {
            if (pts == null || pts.Count == 0) return 0;
            var planned = new HashSet<Cell>();
            if (plan != null)
                foreach (V2 p in plan)
                    if (w.IsDoor(p.Floor)) planned.Add(p.Floor);
            var entered = new HashSet<Cell>();
            int strays = 0;
            bool any = false;
            Cell prev = default(Cell);
            foreach (V2 p in pts)
            {
                Cell c = p.Floor;
                if ((!any || !c.Equals(prev)) && w.IsDoor(c) && (!planned.Contains(c) || !entered.Add(c))) strays++;
                prev = c;
                any = true;
            }
            return strays;
        }

        /// <summary>Times a strand's slack runs in under a powered machine its route does not cross. A bench or a battery is pass-through, so the game calls that floor, but the cord vanishes under the machine and comes
        /// back out, and from above each pass reads as one more cable into it (seen at a smithy in a played colony; owner 2026-11-07: "multiple cables for no reason"). A strand's own plug run is added after this is read.</summary>
        internal static int MachineStrays(CordWorld w, List<V2> pts, List<V2> plan)
        {
            if (pts == null || pts.Count == 0 || w.Machines.Count == 0) return 0;
            var under = new HashSet<Cell>();
            foreach (MachineInfo m in w.Machines)
                for (int x = m.X0; x < m.X0 + m.W; x++)
                    for (int z = m.Z0; z < m.Z0 + m.H; z++) under.Add(new Cell(x, z));
            if (plan != null) foreach (V2 p in plan) under.Remove(p.Floor);
            int strays = 0;
            bool inside = false;
            foreach (V2 p in pts)
            {
                bool now = under.Contains(p.Floor);
                if (now && !inside) strays++;
                inside = now;
            }
            return strays;
        }

        /// <summary>How far either side of a fold the rounding reaches, and the widest it opens a fold that doubles straight back.</summary>
        private const double UnfoldReach = 0.3, UnfoldFlare = 0.13;

        /// <summary>Round every fold into a small bend, leaving the rest of the strand exactly where it lies, so its loops and its
        /// ends do not move. A fold whose bend would leave walkable ground stays: the floor rule outranks the look.</summary>
        internal static List<V2> Unfold(CordWorld w, List<V2> pts, double skipEnds = 0.25)
        {
            List<V2> P = Polish(w, Dejag(w, pts, skipEnds), Math.Max(PolishPin, skipEnds));
            var stuck = new List<V2>();
            for (int guard = 0; guard < 60; guard++)
            {
                V2? at = null;
                foreach (V2 k in Kinks(P, skipEnds))
                    if (!stuck.Any(q => V2.Dist(q, k) < 0.05)) { at = k; break; }
                if (at == null) return P;
                List<V2> round = RoundFold(w, P, at.Value);
                if (round == null) stuck.Add(at.Value); else P = round;
            }
            return P;
        }

        /// <summary>How far from each end the polish leaves a strand alone (the art's plug or fray lines up there), the arc it fades in over, and its passes of a 1-2-1 filter on samples PolishStep apart.
        /// Eight passes are a blur of 0.1 cell: enough to take a settle's ripple and any corner off a cord, while a 0.2 cell coil only draws in by a seventh.</summary>
        public const double PolishPin = 0.2, PolishFade = 0.15, PolishStep = 0.05;
        public const int PolishPasses = 8;

        /// <summary>The last word on a laid strand: a cord has no corners and no ripple at any scale it can be seen at (shape lab on a played colony: 55 of 70 strands had a sharp corner, and a sawtooth
        /// on a stretch along a wall, while the fold check read clean). Only the fine scale moves, so the loops and the lay stay as they were. A point that would leave walkable ground stays where it is.</summary>
        internal static List<V2> Polish(CordWorld w, List<V2> pts, double pinEnds = PolishPin)
        {
            if (pts == null || pts.Count < 7) return pts;
            // the ends stay exactly as laid, point for point: what the art lines up with, a live end's straight run and a dead end's curl
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            int ia = 0, ib = pts.Count - 1;
            while (ia < pts.Count - 1 && cum[ia] < pinEnds) ia++;
            while (ib > 0 && cum[ib] > L - pinEnds) ib--;
            if (ib - ia < 6) return pts;
            List<V2> P = Geo.Resample(pts.GetRange(ia, ib - ia + 1), PolishStep);
            int n = P.Count;
            if (n < 7) return pts;
            V2 first = P[0], last = P[n - 1];
            var weight = new double[n];
            for (int i = 0; i < n; i++) weight[i] = Math.Min(1, Math.Min(i, n - 1 - i) * PolishStep / PolishFade);
            var X = P.ToArray();
            var tmp = new V2[n];
            for (int pass = 0; pass < PolishPasses; pass++)
            {
                Array.Copy(X, tmp, n);
                for (int i = 1; i < n - 1; i++)
                {
                    if (weight[i] <= 0) continue;
                    V2 q = tmp[i] + ((tmp[i - 1] + tmp[i + 1]) * 0.5 - tmp[i]) * (0.5 * weight[i]);
                    if (w == null || w.IsWalkable(q.Floor)) X[i] = q;
                }
            }
            // a needle, two arms lying together, only shortens under a blur: what still reads as a corner gets its own passes, until it opens or it has retracted into the line
            for (int guard = 0; guard < PolishNeedleRounds; guard++)
            {
                var list = new List<V2>(X);
                List<V2> corners = CordShapeAudit.Corners(list, 0.05);
                if (corners.Count == 0) break;
                foreach (V2 c in corners)
                {
                    int at = list.IndexOf(c), reach = (int)Math.Round(PolishNeedleReach / PolishStep);
                    if (at < 0) continue;
                    for (int pass = 0; pass < PolishPasses; pass++)
                    {
                        Array.Copy(X, tmp, n);
                        for (int i = Math.Max(1, at - reach); i <= Math.Min(n - 2, at + reach); i++)
                        {
                            double fade = Math.Min(1, (reach + 1 - Math.Abs(i - at)) / 3.0) * weight[i];
                            if (fade <= 0) continue;
                            V2 q = tmp[i] + ((tmp[i - 1] + tmp[i + 1]) * 0.5 - tmp[i]) * (0.5 * fade);
                            if (w == null || w.IsWalkable(q.Floor)) X[i] = q;
                        }
                    }
                }
            }
            X[0] = first;
            X[n - 1] = last;
            var o = new List<V2>(pts.Count + n);
            o.AddRange(pts.GetRange(0, ia));
            o.AddRange(X);
            o.AddRange(pts.GetRange(ib + 1, pts.Count - ib - 1));
            return o;
        }

        private const int PolishNeedleRounds = 6;
        private const double PolishNeedleReach = 0.4;

        private static List<V2> RoundFold(CordWorld w, List<V2> P, V2 at)
        {
            int i = P.IndexOf(at);
            double[] cum = Geo.CumLen(P);
            int a = i, b = i;
            while (a > 1 && cum[i] - cum[a] < UnfoldReach) a--;
            while (b < P.Count - 2 && cum[b] - cum[i] < UnfoldReach) b++;
            if (a < 1 || b > P.Count - 2 || a >= b) return null;
            V2 s = P[a], e = P[b], ts = (P[a] - P[a - 1]).Norm(), te = (P[b + 1] - P[b]).Norm();
            V2 gap = e - s, axis = ts - te;
            axis = axis.Len < 1e-6 ? ts : axis.Norm();
            V2 lat = gap.Len > 1e-6 ? gap.Norm() : axis.Perp;
            double flare = Math.Max(0, UnfoldFlare - gap.Len / 2), k = Math.Max(0.16, gap.Len * 0.6);
            V2 c1 = s + axis * k - lat * flare, c2 = e + axis * k + lat * flare;
            var bend = new List<V2>();
            const int n = 14;
            for (int q = 1; q < n; q++)
            {
                double t = q / (double)n, it = 1 - t;
                V2 pt = s * (it * it * it) + c1 * (3 * it * it * t) + c2 * (3 * it * t * t) + e * (t * t * t);
                if (w != null && !w.IsWalkable(pt.Floor)) return null;
                bend.Add(pt);
            }
            var o = new List<V2>(P.Count);
            o.AddRange(P.GetRange(0, a + 1));
            o.AddRange(bend);
            o.AddRange(P.GetRange(b, P.Count - b));
            return o;
        }

        /// <summary>The pairwise table per length class, over the cords of the given pieces (end-to-end edges only).</summary>
        public static List<ShapeClass> Table(IEnumerable<LaidPiece> pieces)
        {
            var byClass = new SortedDictionary<int, List<(string key, double[] s)>>();
            foreach (LaidPiece p in pieces)
            {
                if (p.EndA == null || p.Strands.Count == 0) continue;
                CordStrand s = p.Strands[0];
                if (s.Pts == null || s.Pts.Count < 4 || p.PathLen < 2) continue;
                int c = (int)Math.Round(p.PathLen / ClassWidth) * ClassWidth;
                if (!byClass.TryGetValue(c, out var l)) byClass[c] = l = new List<(string, double[])>();
                l.Add((p.EndA + "|" + p.EndB, Sample(s.Pts)));
            }
            var o = new List<ShapeClass>();
            foreach (var kv in byClass)
            {
                var t = new ShapeClass { Length = kv.Key, Cords = kv.Value.Count };
                double sum = 0;
                for (int i = 0; i < kv.Value.Count; i++)
                    for (int j = i + 1; j < kv.Value.Count; j++)
                    {
                        double d = Distance(kv.Value[i].s, kv.Value[j].s);
                        t.Pairs++;
                        sum += d;
                        if (d < TooAlikeBelow) t.TooAlike++;
                        if (d < t.MinDistance) { t.MinDistance = d; t.ClosestA = kv.Value[i].key; t.ClosestB = kv.Value[j].key; }
                    }
                t.MeanDistance = t.Pairs > 0 ? sum / t.Pairs : 0;
                o.Add(t);
            }
            return o;
        }
    }
}
