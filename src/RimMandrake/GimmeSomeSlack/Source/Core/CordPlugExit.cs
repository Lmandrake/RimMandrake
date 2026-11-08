// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// How a cord leaves a plug standing in a strip socket (owner, 2026-11-08 sitting, round 2): "the cord leaves STRAIGHT for a stiff length; a
// high-stress bend at the plug only where a wall or object forces it; otherwise a tight wire-tied strain-relief LOOP (small closed loop, tie band
// where the cord crosses itself, about 0.3-0.4 cell) or a right-angle plug. No Gamma corners."
// The rule was solved offline before a line of this was written (D:\ClaudeWork\rimmandrake\gss_sitting\tools\plug_exit_sweep.py, region table in
// FIXES_20261108.md): over every arrival angle (5 degree steps), free run, wall, neighbour plugs and socket, a natural exit (straight, then a bend of
// radius 0.45-1.0) passes for a course within 70 degrees of the plug; a tied loop for 75 degrees and more; a forced tight bend only where a wall or
// object stands within reach. This file lays those same candidates on the real map and keeps the first that passes the same bars.
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class CordPlugExit
    {
        /// <summary>The bars, the sweep's: no more than HookDeg turned in the first HookLen cells off the plug (a tied loop left out); the first StiffLen
        /// cells straight to within StiffTol degrees; the new lay within Dev of the old course; another plug's body and its first quarter cell of cord
        /// kept NbClear off.</summary>
        public const double HookDeg = 100, HookLen = 1.2, StiffLen = 0.2, StiffTol = 5, Dev = 0.75, NbClear = 0.07, CrossMinDeg = 30;
        /// <summary>A tied loop's diameter, cells (owner: "about 0.3-0.4 cell").</summary>
        public const double LoopDiaMin = 0.30, LoopDiaMax = 0.42;
        /// <summary>A wall or object this close to the plug excuses a hooked (HookNear) or bent (StiffNear) exit; one this close to a bend's apex excuses the bend
        /// (<see cref="CordShapeAudit.ForceNear"/>); a forced bend is tried only with one this close to its first ForcedLook cells.</summary>
        public const double HookNear = 0.6, StiffNear = 0.5, ForcedNear = 0.4, ForcedLook = 0.6;
        /// <summary>Where along the old cord the new exit rejoins it (cells from the plug), in the order tried: the sweep's rule (1.0, else 1.6, else 0.6), then 2.2.</summary>
        public static readonly double[] Joins = { 1.0, 1.6, 0.6, 2.2 };
        /// <summary>Old cord kept past a join, cells: a join this near the end of the run handed to <see cref="Lay"/> is not tried.</summary>
        public const double JoinRest = 0.3;
        private static readonly double[] NatStraight = { 0.25, 0.35, 0.5 }, NatR = { 0.7, 1.0, 0.45 };
        private static readonly double[] LoopStraight = { 0.25, 0.35 }, LoopR = { 0.17, 0.19 };
        private static readonly double[] LoopPsi = { 45, 60, 90, 120 };
        private static readonly double[] ForcedR = { 0.25, 0.3 };
        private const double ForcedStraight = 0.08, Step = 0.05;

        /// <summary>What a plug's surroundings are, for <see cref="Lay"/>: where it is clear (<paramref name="Clear"/>, true near the plug), how far a point is from a wall
        /// or another machine (<paramref name="WallDist"/>), and the other plugs in the same strip as segments (their head to a quarter cell past their tip).</summary>
        internal sealed class Site
        {
            public V2 Tip, Out;
            public Func<V2, bool> Clear;
            public Func<V2, double> WallDist;
            public List<V2[]> Neighbours = new List<V2[]>();
        }

        internal enum Kind { Kept, Natural, Loop, Forced, LeastFails }

        private sealed class Cand
        {
            public Kind Kind;
            public List<V2> Pts;           // from the tip to the join (join included)
            public double TieS0 = -1, TieS1 = -1, Psi;
            public V2 TieAt;
            public double Len;
        }

        /// <summary>Lays the first <paramref name="q"/> cells of a strand (running out of the plug: q[0] at the tip) again as the rule says. Returns the new run, or q when the old
        /// lay already passes or nothing does better; <paramref name="tie"/> is set (arc from q[0]) when the new run makes a tied loop.</summary>
        internal static List<V2> Lay(List<V2> q, Site site, out CordTie? tie, out Kind kind)
        {
            tie = null; kind = Kind.Kept;
            if (q == null || q.Count < 3) return q;
            double[] cum = Geo.CumLen(q);
            double L = cum[cum.Length - 1];
            List<V2> course = Head(q, cum, 4.0);
            // the old lay, judged by the same bars: a cord that already leaves its plug well keeps its lay
            int oldFails = Fails(q, site, course, null, Kind.Kept, -1, -1);
            if (oldFails == 0) return q;
            double hOut = Math.Atan2(site.Out.Z, site.Out.X);
            Cand least = null;
            int leastFails = oldFails;
            foreach (double J in Joins)
            {
                if (J > L - JoinRest) continue;
                V2 P = PointAt(q, cum, J, out V2 tan);
                double h1 = Math.Atan2(tan.Z, tan.X);
                double theta = Wrap(h1 - hOut) * 180 / Math.PI;
                List<V2> rest = q.GetRange(Index(cum, J), q.Count - Index(cum, J));
                foreach (Kind k in new[] { Kind.Natural, Kind.Loop, Kind.Forced })
                {
                    Cand best = null;
                    foreach (Cand c in Candidates(k, site, hOut, P, h1, theta))
                    {
                        if (k == Kind.Forced && !NearWall(c.Pts, site, ForcedLook, ForcedNear)) continue;
                        List<V2> full = Join(c.Pts, rest);
                        int f = Fails(full, site, course, c, k, c.TieS0, c.TieS1);
                        if (f == 0) { if (best == null || c.Len < best.Len) best = c; }
                        else if (f < leastFails) { leastFails = f; least = c; least.Pts = full; }
                    }
                    if (best != null)
                    {
                        kind = k;
                        if (k == Kind.Loop) tie = new CordTie { S0 = best.TieS0, S1 = best.TieS1, At = best.TieAt, Angle = hOut + best.Psi / 2 + Math.PI / 2 };
                        return Join(best.Pts, rest);
                    }
                }
            }
            if (least != null)
            {
                kind = Kind.LeastFails;
                if (least.Kind == Kind.Loop) tie = new CordTie { S0 = least.TieS0, S1 = least.TieS1, At = least.TieAt, Angle = hOut + least.Psi / 2 + Math.PI / 2 };
                return least.Pts;
            }
            return q;
        }

        private static List<V2> Join(List<V2> a, List<V2> rest)
        {
            var o = new List<V2>(a);
            int k = 0;
            while (k < rest.Count && V2.Dist(rest[k], a[a.Count - 1]) < 1e-4) k++;
            for (; k < rest.Count; k++) o.Add(rest[k]);
            return o;
        }

        private static IEnumerable<Cand> Candidates(Kind k, Site site, double hOut, V2 P, double h1, double theta)
        {
            V2 T = site.Tip, u = site.Out;
            if (k == Kind.Natural)
            {
                foreach (double S in NatStraight)
                    foreach (double R in NatR)
                    {
                        V2 X = T + u * S;
                        foreach (List<V2> d in Paths(X, hOut, P, h1, R, 2))
                            yield return Make(Kind.Natural, Line(T, u, S), d);
                    }
            }
            else if (k == Kind.Loop)
            {
                var signs = new List<double> { theta >= 0 ? 1 : -1 };
                if (Math.Abs(theta) >= 95) signs.Add(-signs[0]);          // a course round the strip's far end: the loop may turn either way
                foreach (double S in LoopStraight)
                    foreach (double r in LoopR)
                    {
                        V2 X = T + u * S;
                        var psis = new List<double> { theta };
                        foreach (double sg in signs) foreach (double v in LoopPsi) if (v <= Math.Abs(theta) + 1e-6 || sg != (theta >= 0 ? 1 : -1)) psis.Add(sg * v);
                        foreach (double psiDeg in psis)
                        {
                            if (Math.Abs(psiDeg) < CrossMinDeg) continue;       // a loop crossing itself too flat is no loop: the tie would slide off
                            double hp = hOut + psiDeg * Math.PI / 180;
                            List<V2> loop = null;
                            foreach (CordShape.Dubins.Path lp in Sorted(CordShape.Dubins.All(X, hOut, X, hp, r)))
                                if (lp.Len > 3 * r) { loop = CordShape.Dubins.Sample(X, hOut, lp, Step); break; }
                            if (loop == null) continue;
                            foreach (List<V2> d in Paths(X, hp, P, h1, NatR[0], 2))
                            {
                                var pts = Line(T, u, S);
                                double s0 = Geo.Length(pts);
                                pts.AddRange(loop);
                                double s1 = Geo.Length(pts);
                                Cand c = Make(Kind.Loop, pts, d);
                                c.TieS0 = s0; c.TieS1 = s1; c.TieAt = X; c.Psi = psiDeg * Math.PI / 180;
                                yield return c;
                            }
                        }
                    }
            }
            else
            {
                foreach (double r in ForcedR)
                {
                    V2 X = T + u * ForcedStraight;
                    foreach (List<V2> d in Paths(X, hOut, P, h1, r, 2))
                        yield return Make(Kind.Forced, Line(T, u, ForcedStraight), d);
                }
            }
        }

        private static Cand Make(Kind k, List<V2> head, List<V2> tail)
        {
            var pts = new List<V2>(head);
            pts.AddRange(tail);
            return new Cand { Kind = k, Pts = pts, Len = Geo.Length(pts) };
        }

        private static List<V2> Line(V2 T, V2 u, double S)
        {
            var o = new List<V2> { T };
            int m = Math.Max(1, (int)Math.Ceiling(S / Step));
            for (int i = 1; i <= m; i++) o.Add(T + u * (S * i / m));
            return o;
        }

        private static IEnumerable<CordShape.Dubins.Path> Sorted(List<CordShape.Dubins.Path> all)
        {
            all.Sort((a, b) => a.Len.CompareTo(b.Len));
            return all;
        }

        private static IEnumerable<List<V2>> Paths(V2 a, double ha, V2 b, double hb, double r, int take)
        {
            int n = 0;
            foreach (CordShape.Dubins.Path p in Sorted(CordShape.Dubins.All(a, ha, b, hb, r)))
            {
                if (n++ >= take) yield break;
                yield return CordShape.Dubins.Sample(a, ha, p, Step);
            }
        }

        private static bool NearWall(List<V2> pts, Site site, double look, double near)
        {
            double s = 0;
            for (int i = 0; i < pts.Count && s <= look; i++)
            {
                if (i > 0) s += V2.Dist(pts[i], pts[i - 1]);
                if (site.WallDist(pts[i]) <= near) return true;
            }
            return false;
        }

        /// <summary>How many of the bars a lay off the plug breaks (0 = it passes): its first 4 cells, the tied loop (<paramref name="t0"/>..<paramref name="t1"/>) left out of the turns.</summary>
        private static int Fails(List<V2> full, Site site, List<V2> course, Cand c, Kind k, double t0, double t1)
        {
            List<V2> pts = Head(full, Geo.CumLen(full), 4.0);
            List<V2> q = Geo.Resample(pts, Step);
            int n = q.Count;
            if (n < 4) return 0;
            double[] s = Geo.CumLen(q);
            var ties = t0 >= 0 ? new List<CordTie> { new CordTie { S0 = t0, S1 = t1 } } : null;
            int fails = 0;
            // clear ground, off the other plugs
            bool hit = false, over = false;
            for (int i = 0; i < n && !(hit && over); i++)
            {
                if (s[i] < 0.02) continue;
                if (!hit && !site.Clear(q[i])) hit = true;
                if (!over) foreach (V2[] sg in site.Neighbours) if (SegDist(q[i], sg[0], sg[1]) < NbClear) { over = true; break; }
            }
            if (hit) fails++;
            if (over) fails++;
            // signed turn per point, the loop left out
            var t = new double[n];
            for (int i = 1; i < n - 1; i++) t[i] = CordShapeAudit.InTie(ties, s[i]) ? 0 : Turn(q[i] - q[i - 1], q[i + 1] - q[i]);
            // stiff: straight off the plug unless a wall is right there
            double st = 0;
            for (int i = 1; i < n - 1 && s[i] <= StiffLen; i++) st += t[i];
            if (Math.Abs(st) * 180 / Math.PI > StiffTol && site.WallDist(site.Tip) > StiffNear && k != Kind.Forced) fails++;
            // hook: no more than HookDeg in HookLen of cord outside the loop
            double hk = 0, out_ = 0;
            for (int i = 1; i < n - 1 && out_ <= HookLen; i++)
            {
                if (CordShapeAudit.InTie(ties, s[i])) continue;
                out_ += s[i] - s[i - 1];
                hk += t[i];
            }
            if (Math.Abs(hk) * 180 / Math.PI > HookDeg && site.WallDist(site.Tip) > HookNear) fails++;
            // the audit's own bends and corners, as it will count them; a wall or object at the apex forces one
            foreach (CordShapeAudit.Bend b in CordShapeAudit.Bends(pts, ties))
                if (!b.IsLoop && b.S > 0.05 && b.S < Geo.Length(pts) - BendTailIgnore && site.WallDist(b.Apex) > CordShapeAudit.ForceNear) { fails++; break; }
            foreach (V2 cn in CordShapeAudit.Corners(pts, 0.05, ties))
                if (site.WallDist(cn) > CordShapeAudit.ForceNear) { fails++; break; }
            // keeps to its course
            double dev = 0;
            for (int i = 0; i < n; i++)
            {
                double best = double.MaxValue;
                for (int j = 0; j + 1 < course.Count; j++) best = Math.Min(best, SegDist(q[i], course[j], course[j + 1]));
                dev = Math.Max(dev, best);
            }
            if (dev > Dev) fails++;
            // the loop's size
            if (ties != null)
            {
                double dia = 0;
                var lp = new List<V2>();
                for (int i = 0; i < n; i++) if (s[i] >= t0 && s[i] <= t1) lp.Add(q[i]);
                foreach (V2 a in lp) foreach (V2 b in lp) dia = Math.Max(dia, V2.Dist(a, b));
                if (dia < LoopDiaMin - 1e-6 || dia > LoopDiaMax) fails++;
            }
            return fails;
        }

        /// <summary>The last cells of the judged run are a cut, not the cord's end: a bend there is judged again where the whole strand is audited.</summary>
        private const double BendTailIgnore = 0.6;

        private static List<V2> Head(List<V2> q, double[] cum, double len)
        {
            var o = new List<V2>();
            for (int i = 0; i < q.Count; i++) { o.Add(q[i]); if (cum[i] >= len) break; }
            return o;
        }

        private static int Index(double[] cum, double s)
        {
            int i = 0;
            while (i < cum.Length - 1 && cum[i] < s) i++;
            return i;
        }

        private static V2 PointAt(List<V2> q, double[] cum, double s, out V2 tan)
        {
            int i = Math.Max(1, Index(cum, s));
            // the heading over the next 0.2 cell: one kinked point does not set the course
            int j = i;
            while (j < q.Count - 1 && cum[j] - cum[i] < 0.2) j++;
            tan = (q[j] - q[i - 1]).Norm();
            return q[i];
        }

        private static double Wrap(double a)
        {
            while (a > Math.PI) a -= 2 * Math.PI;
            while (a < -Math.PI) a += 2 * Math.PI;
            return a;
        }

        private static double Turn(V2 u, V2 v)
        {
            if (u.Len < 1e-9 || v.Len < 1e-9) return 0;
            return Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z);
        }

        internal static double SegDist(V2 p, V2 a, V2 b)
        {
            V2 ab = b - a;
            double l2 = ab.X * ab.X + ab.Z * ab.Z;
            double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((p.X - a.X) * ab.X + (p.Z - a.Z) * ab.Z) / l2));
            return V2.Dist(p, a + ab * t);
        }
    }
}
