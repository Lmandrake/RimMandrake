// Messy Conduit core: Verse-free (see CordMath.cs header).
// Phase 1a slack laying (design §8.10): the oracle's excursions + CANNED loop / figure-eight / heap
// shapes (rope.py _loop/_figure8/_heap) spliced only where every point lies on walkable floor, then a
// light bend smoothing and a hard projection out of unwalkable cells. NO position-based-dynamics
// settle yet (that is phase 1b), so the laid points do not match the oracle point-for-point; the
// SelfTest checks the geometric PROPERTIES instead.
using System;
using System.Collections.Generic;

namespace RimMandrake.MessyConduit.Core
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

        public string Fingerprint() =>
            string.Join(",", SlackScale.ToString("0.###"), MinExtra, MaxExtra, Cap, LoopsPerCell, HeapP, CordsMin, CordsMax);
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
        {
            List<V2> P = Geo.Resample(P0, 0.05);
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
            int nb = Math.Max(1, (int)Math.Round(L / 2.6));
            for (int b = 0; b < nb; b++)                       // 1. broad excursions, shared by the bundle
            {
                double c = rrBundle.Range(0.15, 0.85) * L;
                double wdt = rrBundle.Range(1.2, 2.6);
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
            for (int i = 0; i < n; i++) lat[i] = lat[i] * ramp[i] * kAmp + ramp[i] * 0.06 * Math.Sin(s[i] / wav + ph);
            double[] up = FreeReach(w, P, N, 1, cap), down = FreeReach(w, P, N, -1, cap);
            var Q = new List<V2>(n);
            for (int i = 0; i < n; i++) Q.Add(P[i] + N[i] * Geo.Clamp(lat[i], -down[i], up[i]));
            double target = Math.Min(L * (1 + slack), L + maxExtra);
            Q = AddLoops(w, Q, ramp, prm, rrStrand, target);
            Q = Geo.Resample(Q, 0.05);
            Smooth(w, Q, 6);
            return Q;
        }

        private static List<V2> AddLoops(CordWorld w, List<V2> Q, double[] ramp, LayParams prm, CordRng rr, double target)
        {
            double[] s = Geo.CumLen(Q);
            double L = s[s.Length - 1];
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

        /// <summary>The broken end that hangs out of a wall terminal's hole and droops down the face
        /// (screen-down = -Z in game coordinates), nodal.draw_stubs.</summary>
        public static List<V2> HangingTail(V2 hole, V2 into)
        {
            var side = new V2(-into.Z, into.X);
            var down = new V2(0, -1);
            V2 a = hole - side * 0.08;
            var o = new List<V2>(16);
            for (int i = 0; i < 16; i++)
            {
                double t = i / 15.0;
                o.Add(a - side * (0.14 * t + 0.03 * Math.Sin(t * 4)) + down * (0.36 * Math.Pow(t, 1.3)));
            }
            return o;
        }
    }
}
