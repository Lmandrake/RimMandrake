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

        /// <summary>How far either side of a fold the rounding reaches, and the widest it opens a fold that doubles straight back.</summary>
        private const double UnfoldReach = 0.3, UnfoldFlare = 0.13;

        /// <summary>Round every fold into a small bend, leaving the rest of the strand exactly where it lies, so its loops and its
        /// ends do not move. A fold whose bend would leave walkable ground stays: the floor rule outranks the look.</summary>
        internal static List<V2> Unfold(CordWorld w, List<V2> pts, double skipEnds = 0.25)
        {
            List<V2> P = Dejag(w, pts, skipEnds);
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
