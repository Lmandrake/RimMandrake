// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Phase 1a slack laying (design §8.10): the oracle's excursions + CANNED loop / figure-eight / heap
// shapes (rope.py _loop/_figure8/_heap) spliced only where every point lies on walkable floor, then a
// light bend smoothing and a hard projection out of unwalkable cells. NO position-based-dynamics
// settle yet (that is phase 1b), so the laid points do not match the oracle point-for-point; the
// SelfTest checks the geometric PROPERTIES instead.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public sealed class LayParams
    {
        /// <summary>Multiplier on the seeded slack (0 = path-tight, 1 = owner level, 1.6 = feral).</summary>
        public double SlackScale = 1.0;
        public double MinExtra = 7.0, MaxExtra = 16.0;
        public double SlackLo = 1.4, SlackHi = 2.4;
        public double Cap = 2.6;
        public double LoopsPerCell = 0.35;
        public double HeapP = 0.8;
        public int CordsMin = 1, CordsMax = 3;
        public const double RC = 0.07;     // cable clearance from an obstacle face, cells

        // ---- phase 1b B1: rope settle + cord kind (wire vs stiff hose, phase-2 doc §3.5)
        public CordKind Kind = CordKind.Wire;
        /// <summary>Smallest bend radius the settle allows on free (unpinned) points, cells.</summary>
        public double MinBendRadius = 0.15;
        /// <summary>Bend-smoothing weight per settle iteration (rope.relax's 0.22; a hose is stiffer).</summary>
        public double BendSmooth = 0.22;
        /// <summary>PBD settle iterations (rope.py: 70). 0 = no settle (phase-1a canned smoothing).</summary>
        public int SettleIters = 70;
        /// <summary>Point-iteration budget per strand: a very long cord settles with fewer iterations
        /// (never under 20) so one edit can never cost more than ~this many point updates.</summary>
        public int SettleBudget = 160000;
        public double SampleStep = 0.05;
        /// <summary>Broad lateral excursions: length range along the cord (cells), and the small wobble.</summary>
        public double ExcursionLo = 1.2, ExcursionHi = 2.6, Wobble = 0.06;

        /// <summary>The stiff flexible-hose parameter set (phase-2 doc §3.5). Parameters only: hoses
        /// themselves are built later (lane L6); this is what the planner/settle will be handed.</summary>
        public static LayParams Hose() => new LayParams
        {
            Kind = CordKind.Hose, SlackLo = 0.15, SlackHi = 0.30, MinExtra = 1.0, MaxExtra = 6.0, Cap = 1.2,
            LoopsPerCell = 0, HeapP = 0, CordsMin = 1, CordsMax = 1, MinBendRadius = 1.2, BendSmooth = 0.8,
            SampleStep = 0.25, ExcursionLo = 6.0, ExcursionHi = 10.0, Wobble = 0
        };

        public string Fingerprint() =>
            string.Join(",", SlackScale.ToString("0.###"), MinExtra, MaxExtra, Cap, LoopsPerCell, HeapP, CordsMin, CordsMax,
                        Kind, MinBendRadius, BendSmooth, SettleIters, SettleBudget, SampleStep, ExcursionLo, ExcursionHi, Wobble);
    }

    public enum CordKind { Wire, Hose }

    /// <summary>What one rope settle did (probe/SelfTest evidence; never drawn).</summary>
    public sealed class SettleStats
    {
        public int Points, Iters;
        /// <summary>Largest (segment - rest) / rest after the settle (extension), and the largest compression.</summary>
        public double MaxStretch, MaxCompress;
        /// <summary>Intended (rest-sum) length and the settled length.</summary>
        public double RestLen, SettledLen;
        /// <summary>Smallest discrete bend radius over free interior points.</summary>
        public double MinBendR;
        /// <summary>Point updates spent (iterations x points + the final rounds) and exact clearance reads.</summary>
        public long Work, ObstacleTests;
        public int WorstSeg;
        /// <summary>Arc length (cells from the start) of every heap spliced in, the sprawled length, and
        /// how many of the heaps were the long-run end heaps (§8.7.6, phase 1b B2).</summary>
        public List<double> HeapsAt = new List<double>(), HeapsFromEnd = new List<double>();
        public double SprawlLen;
        public int EndHeaps;
        public string WorstNote;
    }

    public static class CordLayer
    {
        public static List<V2> Loop(V2 p, V2 t, V2 n, double r, int side)
        {
            var o = new List<V2>(60);
            for (int i = 0; i < 60; i++)
            {
                double th = 2 * Math.PI * i / 59.0;
                o.Add(p + t * (r * Math.Sin(th) + 0.04 * th) + n * (side * r * (1 - Math.Cos(th))));
            }
            return o;
        }

        public static List<V2> Figure8(V2 p, V2 t, V2 n, double r, int side)
        {
            var o = new List<V2>(90);
            for (int i = 0; i < 90; i++)
            {
                double th = 2 * Math.PI * i / 89.0;
                double x = r * 1.3 * Math.Sin(th);
                double y = r * 0.9 * Math.Sin(2 * th) / 2 + r * 0.55 * (1 - Math.Cos(th));
                o.Add(p + t * x + n * (side * y));
            }
            return o;
        }

        public static List<V2> Heap(V2 p, V2 t, V2 n, double r, int side, CordRng rr)
        {
            var o = new List<V2> { p };
            V2 c = p + n * (side * r * 1.1);
            V2 d0 = p - c;
            double a0 = Math.Atan2(d0.Z, d0.X);
            int loops = rr.Int(3, 5);
            for (int k = 0; k < loops; k++)
            {
                double rad = r * rr.Range(0.55, 1.05);
                V2 cc = c + new V2(rr.Range(-0.25, 0.25), rr.Range(-0.25, 0.25)) * r;
                double turn = 2 * Math.PI * rr.Range(0.8, 1.2) * (k % 2 == 1 ? 1 : -1);
                for (int i = 0; i < 50; i++)
                {
                    double th = a0 + turn * i / 49.0;
                    o.Add(new V2(cc.X + rad * Math.Cos(th), cc.Z + rad * 0.85 * Math.Sin(th)));
                }
            }
            o.Add(p);
            return o;
        }

        private static bool AllClear(CordWorld w, List<V2> shape, double min)
        {
            foreach (V2 q in shape) if (w.Clearance(q) <= min) return false;
            return true;
        }

        private static double[] FreeReach(CordWorld w, List<V2> P, List<V2> N, int sign, double cap)
        {
            var reach = new double[P.Count];
            const double step = 0.08;
            int steps = (int)(cap / step);
            for (int i = 0; i < P.Count; i++)
            {
                reach[i] = cap;
                for (int k = 1; k <= steps; k++)
                {
                    if (w.Clearance(P[i] + N[i] * (sign * k * step)) < LayParams.RC + 0.03)
                    {
                        reach[i] = Math.Max(0, (k - 1) * step);
                        break;
                    }
                }
            }
            return reach;
        }

        /// <summary>rope.sprawl without the PBD settle. P is the planned, rounded centreline.</summary>
        public static List<V2> Sprawl(CordWorld w, List<V2> P0, LayParams prm, double slack, double maxExtra,
                                      CordRng rrBundle, CordRng rrStrand, int nInBundle)
            => Sprawl(w, P0, prm, slack, maxExtra, rrBundle, rrStrand, nInBundle, out _);

        /// <summary>rope.sprawl: excursions, canned loops/heaps, then the PBD rope settle (phase 1b B1).</summary>
        public static List<V2> Sprawl(CordWorld w, List<V2> P0, LayParams prm, double slack, double maxExtra,
                                      CordRng rrBundle, CordRng rrStrand, int nInBundle, out SettleStats stats)
        {
            stats = null;
            double step = prm.SampleStep > 0 ? prm.SampleStep : 0.05;
            List<V2> P = Geo.Resample(P0, step);
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1];
            if (L < 1.2) return P;
            int n = P.Count;
            var pin = new bool[n];
            for (int i = 0; i < n; i++)
            {
                pin[i] = s[i] < 0.45 || s[i] > L - 0.45;
                if (w.IsDoor(P[i].Floor))
                    for (int j = 0; j < n; j++) if (Math.Abs(s[j] - s[i]) < 0.55) pin[j] = true;
            }
            // soft ramp off the pins (box filter, half-width 9 samples), zero on the pins themselves
            var ramp = new double[n];
            for (int i = 0; i < n; i++)
            {
                if (pin[i]) continue;
                double acc = 0;
                for (int k = -9; k <= 9; k++)
                {
                    int j = i + k;
                    if (j >= 0 && j < n && !pin[j]) acc += 1;
                }
                ramp[i] = acc / 19.0;
            }
            var T = new List<V2>(n);
            var N = new List<V2>(n);
            for (int i = 0; i < n; i++) { Geo.TanNorm(P, i, out V2 t, out V2 nn); T.Add(t); N.Add(nn); }
            double cap = prm.Cap;
            var lat = new double[n];
            int nb = Math.Max(1, (int)Math.Round(L / Math.Max(2.6, prm.ExcursionHi)));
            for (int b = 0; b < nb; b++)                       // 1. broad excursions, shared by the bundle
            {
                double c = rrBundle.Range(0.15, 0.85) * L;
                double wdt = rrBundle.Range(prm.ExcursionLo, prm.ExcursionHi);
                int j = Array.BinarySearch(s, c);
                if (j < 0) j = ~j;
                j = Math.Min(Math.Max(j, 0), n - 1);
                double sp = w.Clearance(P[j] + N[j] * (cap * 0.8)), sm = w.Clearance(P[j] - N[j] * (cap * 0.8));
                int side = sp >= sm ? 1 : -1;
                if (rrBundle.Value() < 0.3) side = -side;
                double amp = cap * rrBundle.Range(0.45, 1.0);
                for (int i = 0; i < n; i++)
                {
                    double u = (s[i] - c) / (wdt / 2);
                    lat[i] += side * amp * Math.Exp(-u * u);
                }
            }
            double kAmp = rrStrand.Range(0.85, 1.1), wav = rrStrand.Range(0.35, 0.6), ph = rrStrand.Range(0, 6);
            for (int i = 0; i < n; i++) lat[i] = lat[i] * ramp[i] * kAmp + ramp[i] * prm.Wobble * Math.Sin(s[i] / wav + ph);
            double[] up = FreeReach(w, P, N, 1, cap), down = FreeReach(w, P, N, -1, cap);
            var Q = new List<V2>(n);
            double wantLen = 0, gotLen = 0;
            for (int i = 0; i < n; i++)
            {
                Q.Add(P[i] + N[i] * Geo.Clamp(lat[i], -down[i], up[i]));
                if (i > 0)
                {
                    wantLen += V2.Dist(P[i - 1] + N[i - 1] * lat[i - 1], P[i] + N[i] * lat[i]);
                    gotLen += V2.Dist(Q[i - 1], Q[i]);
                }
            }
            double target = Math.Min(L * (1 + slack), L + maxExtra);
            // what an excursion could not spend sideways (it met a wall) it keeps as LENGTH; the
            // settle buckles that into a bunch against the obstacle (rope.sprawl's `lost`)
            double lost = Math.Max(0, wantLen - gotLen);
            var st = new SettleStats();
            if (prm.LoopsPerCell > 0 || prm.HeapP > 0) Q = AddLoops(w, Q, ramp, prm, rrStrand, target, st);
            Q = Geo.Resample(Q, step);
            st.SprawlLen = Geo.Length(Q);
            if (prm.SettleIters <= 0) { Smooth(w, Q, 6); stats = st; return Q; }
            double Lq = st.SprawlLen;
            // the budget survives the settle: never grow past the slack target (the clamp of §8.2.4)
            double restLen = Math.Min(Lq + 0.8 * lost, Math.Max(Lq, target));
            stats = Settle(w, Q, PinMask(w, Q), restLen, prm, st);
            return Q;
        }

        /// <summary>Pins: both ends (0.45 cell) and 0.55 cell either side of any doorway point (rope.pin_mask).</summary>
        public static bool[] PinMask(CordWorld w, List<V2> Q)
        {
            double[] s = Geo.CumLen(Q);
            double L = s[s.Length - 1];
            int n = Q.Count;
            var pin = new bool[n];
            for (int i = 0; i < n; i++) if (s[i] < 0.45 || s[i] > L - 0.45) pin[i] = true;
            for (int i = 0; i < n; i++)
            {
                if (!w.IsDoor(Q[i].Floor)) continue;
                for (int j = i; j >= 0 && s[i] - s[j] < 0.55; j--) pin[j] = true;
                for (int j = i; j < n && s[j] - s[i] < 0.55; j++) pin[j] = true;
            }
            pin[0] = pin[n - 1] = true;
            return pin;
        }

        /// <summary>
        /// Phase 1b B1 -- the relaxed-rope settle (rope.relax, position-based dynamics): per iteration
        /// bend smoothing, two Jacobi passes of inextensible segments (rest = restLen / segments),
        /// a minimum-bend-radius pass (the stiff hose), and a hard projection out of unwalkable cells
        /// along the clearance gradient; pinned points never move. Deterministic (pure arithmetic in a
        /// fixed order, no RNG). Cost is bounded: iterations = min(prm.SettleIters, budget / points),
        /// never under 20, and the obstacle test is skipped for any point whose cell and 8 neighbours
        /// are all walkable (clearance there is >= 1 cell, far above RC), cached per cell.
        /// </summary>
        public static SettleStats Settle(CordWorld w, List<V2> Q, bool[] pin, double restLen, LayParams prm, SettleStats into = null)
        {
            int n = Q.Count;
            SettleStats st = into ?? new SettleStats();
            st.Points = n;
            if (n < 3) { st.RestLen = st.SettledLen = Geo.Length(Q); return st; }
            int iters = Math.Max(20, Math.Min(prm.SettleIters, prm.SettleBudget / Math.Max(1, n)));
            iters = Math.Min(iters, Math.Max(20, prm.SettleIters));
            st.Iters = iters;
            // pinned-to-pinned segments keep their laid length; the free segments share the rest
            double pinnedLen = 0;
            int freeSegs = 0;
            for (int i = 0; i < n - 1; i++)
                if (pin[i] && pin[i + 1]) pinnedLen += V2.Dist(Q[i], Q[i + 1]);
                else freeSegs++;
            if (freeSegs == 0) { st.RestLen = st.SettledLen = Geo.Length(Q); return st; }
            double rest = Math.Max(1e-4, (restLen - pinnedLen) / freeSegs);
            st.RestLen = pinnedLen + rest * freeSegs;
            var near = new Dictionary<int, bool>();
            bool Near(V2 p)
            {
                Cell c = p.Floor;
                int key = c.Z * 65536 + c.X;
                if (near.TryGetValue(key, out bool v)) return v;
                v = false;
                for (int dz = -1; dz <= 1 && !v; dz++)
                    for (int dx = -1; dx <= 1; dx++)
                        if (!w.IsWalkable(new Cell(c.X + dx, c.Z + dz))) { v = true; break; }
                near[key] = v;
                return v;
            }
            var X = Q.ToArray();
            var tmp = new V2[n];
            double k = prm.BendSmooth;
            double turnMax = prm.MinBendRadius > 0 ? rest / prm.MinBendRadius : double.MaxValue;
            for (int it = 0; it < iters; it++)
            {
                // 1. bend smoothing
                Array.Copy(X, tmp, n);
                for (int i = 1; i < n - 1; i++)
                {
                    if (pin[i]) continue;
                    V2 avg = (tmp[i - 1] + tmp[i + 1]) * 0.5;
                    X[i] = tmp[i] + (avg - tmp[i]) * k;
                }
                // 2. stiffness: a free point bent tighter than the minimum radius is pulled toward the chord
                if (prm.MinBendRadius > 0.2)
                    for (int i = 1; i < n - 1; i++)
                    {
                        if (pin[i]) continue;
                        double th = Turn(X[i - 1], X[i], X[i + 1]);
                        if (th <= turnMax) continue;
                        V2 avg = (X[i - 1] + X[i + 1]) * 0.5;
                        X[i] = X[i] + (avg - X[i]) * Math.Min(0.9, 1 - turnMax / th);
                    }
                // 3. inextensible segments: one symmetric Gauss-Seidel sweep (forward then back), the
                //    correction split between free ends (Gauss-Seidel converges where rope.relax's two
                //    Jacobi passes leave ~20% stretch at 0.05-cell segments)
                Inextensible(X, pin, rest);
                // 4. obstacles: hard projection out of unwalkable cells, flattening/bunching the cable
                for (int i = 1; i < n - 1; i++)
                {
                    if (pin[i]) continue;
                    if (!Near(X[i])) continue;
                    double sd = w.Clearance(X[i]);
                    st.ObstacleTests++;
                    if (sd >= LayParams.RC) continue;
                    V2 g = w.ClearanceGradient(X[i]);
                    if (g.Len < 1e-9) continue;
                    X[i] = X[i] + g * (LayParams.RC - sd);
                }
                for (int i = 0; i < n; i++)
                    X[i] = new V2(Geo.Clamp(X[i].X, 0.04, w.Width - 0.04), Geo.Clamp(X[i].Z, 0.04, w.Height - 0.04));
                st.Work += n;
            }
            // final rounds: restore segment lengths and push out of obstacles, alternating, so the
            // budget and the floor rule both hold when the settle hands the strand back
            for (int pass = 0; pass < 16; pass++)
            {
                for (int i = 1; i < n - 1; i++)
                {
                    if (pin[i] || !Near(X[i])) continue;
                    double sd = w.Clearance(X[i]);
                    if (sd >= LayParams.RC) continue;
                    V2 g = w.ClearanceGradient(X[i]);
                    if (g.Len < 1e-9) continue;
                    X[i] = X[i] + g * (LayParams.RC - sd + 0.01);
                }
                Inextensible(X, pin, rest);
                st.Work += 2 * n;
            }
            // last word goes to the floor rule, but only for a point actually inside an unwalkable cell
            for (int i = 1; i < n - 1; i++)
            {
                if (pin[i] || !Near(X[i]) || w.IsWalkable(X[i].Floor)) continue;
                double sd = w.Clearance(X[i]);
                V2 g = w.ClearanceGradient(X[i]);
                if (g.Len > 1e-9) X[i] = X[i] + g * (LayParams.RC - sd + 0.01);
            }
            Inextensible(X, pin, rest);
            Inextensible(X, pin, rest);
            for (int i = 0; i < n; i++) Q[i] = X[i];
            double maxStr = 0, minR = double.MaxValue;
            for (int i = 0; i < n - 1; i++)
                if (!(pin[i] && pin[i + 1]))
                {
                    double str = (V2.Dist(X[i], X[i + 1]) - rest) / rest;      // stretch only: a short segment is the rope bunching
                    st.MaxCompress = Math.Max(st.MaxCompress, -str);
                    if (str > maxStr) { maxStr = str; st.WorstSeg = i; st.WorstNote = (pin[i] ? "P" : "f") + (pin[i + 1] ? "P" : "f") + " len " + V2.Dist(X[i], X[i + 1]).ToString("0.0000") + " rest " + rest.ToString("0.0000") + " at " + X[i] + " pins " + string.Concat(Enumerable.Range(Math.Max(0, i - 3), Math.Min(n, i + 5) - Math.Max(0, i - 3)).Select(j => pin[j] ? "P" : "f")) + " lens " + string.Join(",", Enumerable.Range(Math.Max(0, i - 3), Math.Min(n - 1, i + 4) - Math.Max(0, i - 3)).Select(j => V2.Dist(X[j], X[j + 1]).ToString("0.0000"))); }
                }
            for (int i = 1; i < n - 1; i++)
            {
                if (pin[i] || pin[i - 1] || pin[i + 1]) continue;
                double th = Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9) minR = Math.Min(minR, seg / th);
            }
            st.MaxStretch = maxStr;
            st.MinBendR = minR == double.MaxValue ? 99 : minR;
            st.SettledLen = Geo.Length(Q);
            return st;
        }

        private static void Inextensible(V2[] X, bool[] pin, double rest)
        {
            int n = X.Length;
            for (int dir = 0; dir < 2; dir++)
                for (int k = 0; k < n - 1; k++)
                {
                    int i = dir == 0 ? k : n - 2 - k;
                    double wa = pin[i] ? 0 : 1, wb = pin[i + 1] ? 0 : 1, both = wa + wb;
                    if (both <= 0) continue;
                    V2 d = X[i + 1] - X[i];
                    double ln = Math.Max(d.Len, 1e-9);
                    V2 corr = d * ((ln - rest) / ln);
                    X[i] = X[i] + corr * (wa / both);
                    X[i + 1] = X[i + 1] - corr * (wb / both);
                }
        }

        /// <summary>Turning angle at b (radians, 0 = straight).</summary>
        public static double Turn(V2 a, V2 b, V2 c)
        {
            V2 u = b - a, v = c - b;
            double lu = u.Len, lv = v.Len;
            if (lu < 1e-12 || lv < 1e-12) return 0;
            double cs = (u.X * v.X + u.Z * v.Z) / (lu * lv);
            return Math.Acos(Geo.Clamp(cs, -1, 1));
        }

        /// <summary>A cord longer than this (cells) gets one extra heap within EndHeapReach of each end,
        /// "where people look" (§8.7.6 very long runs; phase 1b B2).</summary>
        public const double LongRun = 40, EndHeapReach = 6;

        private static List<V2> AddLoops(CordWorld w, List<V2> Q, double[] ramp, LayParams prm, CordRng rr, double target, SettleStats st)
        {
            double[] s = Geo.CumLen(Q);
            double L = s[s.Length - 1];
            if (L > LongRun && prm.HeapP > 0)
            {
                // seeded from their own stream so a long cord's other shapes do not reshuffle
                CordRng re = new CordRng(rr.NextULong());
                foreach (bool atEnd in new[] { true, false })
                {
                    double d = re.Range(1.5, EndHeapReach - 1.0);
                    double at = atEnd ? s[s.Length - 1] - d : d;
                    int j = Array.BinarySearch(s, at);
                    if (j < 0) j = ~j;
                    if (j <= 2 || j >= Q.Count - 3) continue;
                    var win = Q.GetRange(Math.Max(0, j - 3), Math.Min(Q.Count, j + 4) - Math.Max(0, j - 3));
                    Geo.TanNorm(win, win.Count / 2, out V2 t, out V2 nrm);
                    int side = w.Clearance(Q[j] + nrm * 0.8) >= w.Clearance(Q[j] - nrm * 0.8) ? 1 : -1;
                    double r = 0.5 * prm.Cap / 1.6;
                    List<V2> shape = null;
                    for (int tries = 0; tries < 5 && r >= 0.18; tries++, r *= 0.7)
                    {
                        List<V2> c = Heap(Q[j], t, nrm, r, side, re);
                        if (AllClear(w, c, LayParams.RC + 0.02)) { shape = c; break; }
                    }
                    if (shape == null) continue;
                    double fromStart = s[j], fromEnd = s[s.Length - 1] - s[j];
                    var nq = new List<V2>(Q.Count + shape.Count);
                    nq.AddRange(Q.GetRange(0, j));
                    nq.AddRange(shape);
                    nq.AddRange(Q.GetRange(j + 1, Q.Count - j - 1));
                    Q = nq;
                    s = Geo.CumLen(Q);
                    st.HeapsAt.Add(fromStart);
                    st.HeapsFromEnd.Add(atEnd ? fromEnd : s[s.Length - 1] - fromStart);
                    st.EndHeaps++;
                }
                L = s[s.Length - 1];
                var rs = new double[Q.Count];
                for (int i = 0; i < rs.Length; i++) rs[i] = Math.Min(1, Math.Min(s[i], L - s[i]) / 0.9);
                ramp = rs;
            }
            int nloops = (int)(prm.LoopsPerCell * L + rr.Value());
            bool heap = rr.Value() < prm.HeapP;
            var cands = new List<KeyValuePair<bool, double>>();      // (isHeap, fraction)
            for (int i = 0; i < nloops; i++) cands.Add(new KeyValuePair<bool, double>(false, rr.Range(0.2, 0.8)));
            if (heap) cands.Add(new KeyValuePair<bool, double>(true, rr.Range(0.3, 0.7)));
            cands.Sort((a, b) => b.Value.CompareTo(a.Value));     // splice from the far end: indices stay valid
            foreach (var cand in cands)
            {
                int j = Array.BinarySearch(s, cand.Value * L);
                if (j < 0) j = ~j;
                if (j <= 2 || j >= Q.Count - 3 || ramp[Math.Min(j, ramp.Length - 1)] < 0.9) continue;
                var win = Q.GetRange(Math.Max(0, j - 3), Math.Min(Q.Count, j + 4) - Math.Max(0, j - 3));
                Geo.TanNorm(win, win.Count / 2, out V2 t, out V2 nrm);
                int side = w.Clearance(Q[j] + nrm * 0.8) >= w.Clearance(Q[j] - nrm * 0.8) ? 1 : -1;
                bool fig8 = rr.Value() < 0.35;
                double r = (cand.Key ? 0.5 : rr.Range(0.35, 0.5)) * prm.Cap / 1.6;
                List<V2> shape = null;
                for (int tries = 0; tries < 5; tries++)
                {
                    List<V2> c = cand.Key ? Heap(Q[j], t, nrm, r, side, rr) : fig8 ? Figure8(Q[j], t, nrm, r, side) : Loop(Q[j], t, nrm, r, side);
                    bool over = s[s.Length - 1] + Geo.Length(c) > target * 1.25;
                    if (AllClear(w, c, LayParams.RC + 0.02) && !over) { shape = c; break; }
                    r *= 0.7;
                    if (r < 0.18) break;
                }
                if (shape == null) continue;
                if (cand.Key) { st?.HeapsAt.Add(s[j]); st?.HeapsFromEnd.Add(s[s.Length - 1] - s[j]); }
                var nq = new List<V2>(Q.Count + shape.Count);
                nq.AddRange(Q.GetRange(0, j));
                nq.AddRange(shape);
                nq.AddRange(Q.GetRange(j + 1, Q.Count - j - 1));
                Q = nq;
                s = Geo.CumLen(Q);
                if (s[s.Length - 1] > target * 1.15) break;
            }
            return Q;
        }

        /// <summary>A few rounds of bend smoothing on the interior, each followed by a hard
        /// projection out of unwalkable cells (the part of rope.relax phase 1a keeps).</summary>
        public static void Smooth(CordWorld w, List<V2> Q, int iters)
        {
            int n = Q.Count;
            if (n < 5) { ProjectOut(w, Q); return; }
            var tmp = new V2[n];
            for (int it = 0; it < iters; it++)
            {
                for (int i = 0; i < n; i++) tmp[i] = Q[i];
                for (int i = 2; i < n - 2; i++)
                {
                    V2 avg = (tmp[i - 1] + tmp[i + 1]) * 0.5;
                    Q[i] = tmp[i] + (avg - tmp[i]) * 0.22;
                }
                ProjectOut(w, Q);
            }
        }

        /// <summary>Push every interior point with clearance below RC back out along the gradient.
        /// The two end points are pins (plugs, stub faces) and are left where the plan put them.</summary>
        public static void ProjectOut(CordWorld w, List<V2> Q)
        {
            for (int pass = 0; pass < 4; pass++)
            {
                bool any = false;
                for (int i = 1; i < Q.Count - 1; i++)
                {
                    double sd = w.Clearance(Q[i]);
                    if (sd >= LayParams.RC) continue;
                    V2 g = w.ClearanceGradient(Q[i]);
                    if (g.Len < 1e-9) continue;
                    Q[i] = Q[i] + g * (LayParams.RC - sd + 0.01);
                    any = true;
                }
                if (!any) return;
            }
        }

        /// <summary>A pointless loop in the cord at q (needless conduit, §8.7.5).</summary>
        public static List<V2> SpliceLoop(CordWorld w, List<V2> P, V2 q, CordRng rr, double r)
        {
            int j = 0;
            double best = double.MaxValue;
            for (int i = 0; i < P.Count; i++)
            {
                double d = V2.Dist(P[i], q);
                if (d < best) { best = d; j = i; }
            }
            if (j < 3 || j > P.Count - 4) return P;
            var win = P.GetRange(j - 3, 7);
            Geo.TanNorm(win, 3, out V2 t, out V2 n);
            for (int k = 0; k < 4; k++)
            {
                int side = rr.Sign();
                List<V2> shape = rr.Value() < 0.3 ? Figure8(P[j], t, n, r, side) : Loop(P[j], t, n, r, side);
                if (AllClear(w, shape, LayParams.RC))
                {
                    var o = new List<V2>(P.Count + shape.Count);
                    o.AddRange(P.GetRange(0, j));
                    o.AddRange(shape);
                    o.AddRange(P.GetRange(j + 1, P.Count - j - 1));
                    return o;
                }
                r *= 0.75;
            }
            return P;
        }

        /// <summary>A DEAD end lies limp: the last 0.7 cell falls sideways off the conduit's line
        /// (0.30 cell at the tip) and curls over, so it reads as slack and still next to a live end
        /// that sticks straight out. Tried on the seeded side, then the other, then at half size;
        /// a shape that would put any point on unwalkable ground is not used.</summary>
        public static void LimpTail(CordWorld w, List<V2> P, bool atEnd, int side, int strandIndex)
        {
            if (P.Count < 4) return;
            if (!atEnd) P.Reverse();
            double[] sl = Geo.CumLen(P);
            double L = sl[sl.Length - 1];
            int j = Array.BinarySearch(sl, L - Math.Min(0.7, L * 0.5));
            if (j < 0) j = ~j;
            j = Math.Max(1, Math.Min(j, P.Count - 2));
            int m = P.Count - j;
            var orig = P.GetRange(j, m);
            foreach (double amp in new[] { 1.0, -1.0, 0.5, -0.5 })
            {
                var cand = new V2[m];
                bool ok = true;
                for (int k = 0; k < m; k++)
                {
                    double u = m == 1 ? 1 : k / (double)(m - 1);
                    Geo.TanNorm(orig, k, out V2 t, out V2 nrm);
                    double curl = amp * side * (0.30 + 0.025 * strandIndex) * Math.Pow(u, 2.4);
                    double back = -0.12 * Math.Abs(amp) * u * u * u;
                    cand[k] = orig[k] + nrm * curl + t * back;
                    if (w != null && !w.IsWalkable(cand[k].Floor)) { ok = false; break; }
                }
                if (!ok) continue;
                for (int k = 0; k < m; k++) P[j + k] = cand[k];
                break;
            }
            if (!atEnd) P.Reverse();
        }

        /// <summary>Replace the last stretch of a strand (its first stretch when atEnd is false) with a
        /// smooth curve that ends exactly at target travelling along arrive, finishing with a straight
        /// run of `straight` cells. Left unchanged if the curve would touch unwalkable ground.</summary>
        public static List<V2> Approach(CordWorld w, List<V2> P, bool atEnd, V2 target, V2 arrive, double straight)
        {
            var Q = new List<V2>(P);
            if (!atEnd) Q.Reverse();
            arrive = arrive.Norm();
            if (Q.Count < 4 || Geo.Length(Q) < 0.6)
            {
                // a very short cord (a junction right beside the wall it runs into): a straight piece
                // from its far end to the target
                V2 a0 = Q[0];
                var line = new List<V2>();
                int nl = Math.Max(2, (int)(V2.Dist(a0, target) / 0.05) + 1);
                for (int q = 0; q < nl; q++) line.Add(a0 + (target - a0) * (q / (double)(nl - 1)));
                if (!atEnd) line.Reverse();
                return line;
            }
            double[] cl = Geo.CumLen(Q);
            double L = cl[cl.Length - 1];
            foreach (double frac in new[] { 1.0, 0.6 })
            {
                double use = Math.Min((0.45 + straight) * frac, Math.Max(L * 0.4, straight + 0.3));
                // cut back to the last point a full `use` from the TARGET (not from the old end: a
                // junction cord ran on to the node centre, past the arm tip it must now stop at)
                int j = Q.Count - 2;
                while (j > 1 && V2.Dist(Q[j], target) < use) j--;
                V2 s0 = Q[j], tS = (Q[j] - Q[j - 1]).Norm();
                double st = Math.Min(straight, Math.Max(0, V2.Dist(s0, target) - 0.15));
                V2 bend = target - arrive * st;
                double k = V2.Dist(s0, bend) * 0.45;
                V2 c1 = s0 + tS * k, c2 = bend - arrive * k;
                var add = new List<V2>();
                int nb = Math.Max(6, (int)(V2.Dist(s0, bend) / 0.05));
                for (int q = 1; q <= nb; q++)
                {
                    double t = q / (double)nb, it = 1 - t;
                    add.Add(s0 * (it * it * it) + c1 * (3 * it * it * t) + c2 * (3 * it * t * t) + bend * (t * t * t));
                }
                int ns = Math.Max(1, (int)(st / 0.05));
                for (int q = 1; q <= ns; q++) add.Add(bend + arrive * (st * q / ns));
                bool ok = true;
                for (int q = 0; q < add.Count - 1; q++)
                    if (w != null && !w.IsWalkable(add[q].Floor)) { ok = false; break; }
                if (!ok) continue;
                var R = Q.GetRange(0, j + 1);
                R.AddRange(add);
                if (!atEnd) R.Reverse();
                return R;
            }
            return P;
        }
    }
}
