using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// HOSE_SPLICE_BUILD_MATES_BY_SLOPE (owner walk 2026-10-23: "two hoses joined end to end do not mate, they just lay on top of
    /// each other. We need a universal joiner that understands slope/angles ... Please use boundary conditions that include the
    /// first and second derivative as well (angle and max hose curvature)"). Verse-free, selftested by HoseSpliceChecks.
    ///
    /// <see cref="Join"/>: a G2 curve between two hose states (position, heading AND curvature matched at both ends) whose
    /// curvature never exceeds kmax = 1 / MinBendRadius. The curvature is piecewise LINEAR in arc length (a chain of clothoid /
    /// Euler-spiral pieces): knots K_0..K_M, K_0 and K_M fixed to the end curvatures, the inner knots and the length L solved by
    /// Gauss-Newton (minimum-norm steps, active-set clamp at +-kmax) so the curve lands on the far end with the far heading
    /// (winding included). Because the curvature is linear between knots its largest magnitude is AT a knot, so the bound is
    /// exact, not sampled. Seeds: every Dubins word (HoseMath.DubinsAll) at a few radii >= the minimum, its curvature profile
    /// box-smoothed onto the knots. Of the converged curves the gentlest is kept: added length plus bending energy
    /// R * integral(k^2), never one that crosses or doubles back over itself.
    ///
    /// <see cref="MateTail"/>: a drawn hose's end re-shaped so it arrives at a coupling point travelling along the coupling axis,
    /// its last <see cref="CouplingStraight"/> dead straight (the rigid brass and cloth), joined G2 to the untouched hose at a
    /// cut-back arc; used for two hose ends coupled face to face (RM_MapComponent_Hoses.MatePartner).
    /// </summary>
    public static class HoseSpliceMath
    {
        /// <summary>The solved curve's profile, kept so a re-solve (a fill transition re-poses the hose every tick) starts on it.</summary>
        public sealed class Seed
        {
            public double CutBack;
            public double[] K;
            public double L, Turn;
            /// <summary>Gentleness cost of the re-shaped end: added length + bending energy (MateTail's ranking).</summary>
            public double Cost;
        }

        /// <summary>Straight run each side of a hose-to-hose coupling: one joiner half (couplings + wrap) and a 0.1-cell lead.</summary>
        public static double CouplingStraight(double visible) => HoseMath.JoinerHalf(visible) + 0.1;

        /// <summary>Seed radii as multiples of the minimum bend radius (the gentlest feasible wins on cost).</summary>
        private static readonly double[] RadiusFactors = { 1.15, 1.5, 2.2 };
        /// <summary>Cut-backs tried (cells of the hose's own end replaced), shortest first.</summary>
        internal static readonly double[] CutBacks = { 1.5, 2.5, 4, 6, 8.5 };
        /// <summary>Integration substeps per knot interval (Simpson; the heading is exactly quadratic there).</summary>
        private const int Sub = 4;
        /// <summary>Fairing passes on the winning curve.</summary>
        private const int FairPasses = 6;

        /// <summary>Work counters (probe/selftest): Gauss-Newton solves started and iterations run.</summary>
        public static long Solves, Iterations;

        // ------------------------------------------------------------------ the curvature-profile curve
        private static int KnotCount(double L) => Math.Max(8, Math.Min(24, (int)Math.Ceiling(L / 0.5)));

        /// <summary>Integrate the profile from (p0, th0): node arrays (s, heading, x, z) at Sub points per knot interval.</summary>
        private static void Integrate(V2 p0, double th0, double[] K, double L, out double[] th, out double[] x, out double[] z)
        {
            int M = K.Length - 1, N = M * Sub;
            double h = L / M, ds = h / Sub;
            th = new double[N + 1]; x = new double[N + 1]; z = new double[N + 1];
            th[0] = th0; x[0] = p0.X; z[0] = p0.Z;
            for (int j = 0; j < M; j++)
            {
                double ka = K[j], kb = K[j + 1];
                for (int q = 0; q < Sub; q++)
                {
                    int i = j * Sub + q;
                    double u0 = q / (double)Sub, um = (q + 0.5) / Sub, u1 = (q + 1.0) / Sub;
                    // heading inside the interval: th_j + h (ka u + (kb - ka) u^2 / 2), u in [0, 1]
                    double thj = th[j * Sub];
                    double T(double u) => thj + h * (ka * u + (kb - ka) * u * u / 2);
                    double t0 = T(u0), tm = T(um), t1 = T(u1);
                    th[i + 1] = t1;
                    x[i + 1] = x[i] + ds / 6 * (Math.Cos(t0) + 4 * Math.Cos(tm) + Math.Cos(t1));
                    z[i + 1] = z[i] + ds / 6 * (Math.Sin(t0) + 4 * Math.Sin(tm) + Math.Sin(t1));
                }
            }
        }

        private static double TurnOf(double[] K, double L)
        {
            int M = K.Length - 1;
            double h = L / M, t = 0;
            for (int j = 0; j < M; j++) t += h * (K[j] + K[j + 1]) / 2;
            return t;
        }

        /// <summary>Curvature sharpness bound (per cell of arc): sigma = kmax^2 / 2, so the hose takes at least two minimum bend
        /// radii of length to go from straight to its tightest bend, and the curvature it carries in at an end is held, not
        /// dropped at once. Applied at both ends as a tube round the end curvatures; inside, the fairing pass keeps the profile
        /// smooth.</summary>
        internal static double Sharpness(double kmax) => 0.5 * kmax * kmax;

        /// <summary>The bounds of knot j: |k| &lt;= kmax, and within sigma x arc of each end's curvature.</summary>
        private static void Bounds(double[] K, double L, double kmax, int j, out double lo, out double hi)
        {
            int M = K.Length - 1;
            double sj = L * j / M, sg = Sharpness(kmax), kcap = kmax * 0.999;
            hi = Math.Min(kcap, Math.Min(K[0] + sg * sj, K[M] + sg * (L - sj)));
            lo = Math.Max(-kcap, Math.Max(K[0] - sg * sj, K[M] - sg * (L - sj)));
            if (lo > hi) { double m = 0.5 * (lo + hi); lo = hi = m; }
        }

        private static double Res(V2 p0, double th0, V2 p1, double turn, double[] K, double L, out double rx, out double rz, out double rt)
        {
            Integrate(p0, th0, K, L, out double[] t, out double[] xx, out double[] zz);
            int N = t.Length - 1;
            rx = xx[N] - p1.X; rz = zz[N] - p1.Z; rt = TurnOf(K, L) - turn;
            return Math.Sqrt(rx * rx + rz * rz + rt * rt);
        }

        /// <summary>Jacobian of (x_end, z_end, turn) in the inner knots (analytic: d end / d K_j = integral of the hat function
        /// times the lever arm) and L (by difference); column n-1 is L.</summary>
        private static double[,] Jac(V2 p0, double th0, V2 p1, double turn, double[] K, double L, double ex, double ez, double et)
        {
            int M = K.Length - 1, n = M;
            Integrate(p0, th0, K, L, out double[] th, out double[] xs, out double[] zs);
            int N = th.Length - 1;
            double h = L / M, ds = h / Sub;
            var J = new double[3, n];
            for (int j = 1; j < M; j++)
            {
                double ax = 0, az = 0;
                for (int i = Math.Max(0, (j - 1) * Sub); i <= Math.Min(N, (j + 1) * Sub); i++)
                {
                    double hat = Math.Max(0, 1 - Math.Abs(i / (double)Sub - j));
                    if (hat <= 0) continue;
                    double w = (i == 0 || i == N) ? ds / 2 : ds;
                    ax += -w * hat * (zs[N] - zs[i]);
                    az += w * hat * (xs[N] - xs[i]);
                }
                J[0, j - 1] = ax; J[1, j - 1] = az; J[2, j - 1] = h;
            }
            double dL = 1e-5 * Math.Max(1, L);
            Res(p0, th0, p1, turn, K, L + dL, out double fx, out double fz, out double ft);
            J[0, n - 1] = (fx - ex) / dL; J[1, n - 1] = (fz - ez) / dL; J[2, n - 1] = (ft - et) / dL;
            return J;
        }

        /// <summary>Weighted minimum-norm solve of J step = rhs (W = 0 freezes a column).</summary>
        private static bool MinNorm(double[,] J, double[] W, double[] rhs, double[] step)
        {
            int n = W.Length;
            var A = new double[3, 3];
            for (int a = 0; a < 3; a++)
                for (int b = 0; b < 3; b++)
                {
                    double acc = a == b ? 1e-10 : 0;
                    for (int c = 0; c < n; c++) acc += J[a, c] * W[c] * J[b, c];
                    A[a, b] = acc;
                }
            if (!Solve3(A, rhs, out double[] y)) return false;
            for (int c = 0; c < n; c++) step[c] = W[c] * (J[0, c] * y[0] + J[1, c] * y[1] + J[2, c] * y[2]);
            return true;
        }

        /// <summary>Gauss-Newton on the inner knots and L: lands on (p1, th0 + turn), every knot inside its Bounds. Then a
        /// fairing pass (the curvature profile's roughness sum (K_j+1 - K_j)^2 lowered along the constraint null space, re-landed
        /// each step). True when converged.</summary>
        private static bool Solve(V2 p0, double th0, V2 p1, double turn, double kmax, double[] K, ref double L, int maxIter = 40, int fair = 0)
        {
            Solves++;
            if (!Land(p0, th0, p1, turn, kmax, K, ref L, maxIter)) return false;
            int M = K.Length - 1;
            for (int f = 0; f < fair; f++)
            {
                double rough = Rough(K);
                Res(p0, th0, p1, turn, K, L, out double ex, out double ez, out double et);
                double[,] J = Jac(p0, th0, p1, turn, K, L, ex, ez, et);
                // gradient of the roughness in the free knots, projected onto J's null space (the move keeps the ends)
                var g = new double[M];
                var W = new double[M];
                for (int j = 1; j < M; j++)
                {
                    g[j - 1] = 2 * (2 * K[j] - K[j - 1] - K[j + 1]);
                    Bounds(K, L, kmax, j, out double lo, out double hi);
                    bool pinned = (K[j] >= hi - 1e-9 && g[j - 1] < 0) || (K[j] <= lo + 1e-9 && g[j - 1] > 0);
                    W[j - 1] = pinned ? 0 : 1;
                }
                W[M - 1] = 0;
                var jg = new double[3];
                for (int a = 0; a < 3; a++) { double acc = 0; for (int c = 0; c < M; c++) acc += J[a, c] * W[c] * g[c]; jg[a] = acc; }
                var corr = new double[M];
                if (!MinNorm(J, W, jg, corr)) break;
                var Kn = (double[])K.Clone();
                double Ln = L;
                bool better = false;
                for (double alpha = 0.25; alpha > 0.01; alpha *= 0.5)
                {
                    Array.Copy(K, Kn, M + 1);
                    Ln = L;
                    for (int j = 1; j < M; j++)
                    {
                        Bounds(K, L, kmax, j, out double lo, out double hi);
                        Kn[j] = Math.Max(lo, Math.Min(hi, K[j] - alpha * W[j - 1] * (g[j - 1] - corr[j - 1])));
                    }
                    if (Land(p0, th0, p1, turn, kmax, Kn, ref Ln, 12) && Rough(Kn) < rough - 1e-9) { better = true; break; }
                }
                if (!better) break;
                Array.Copy(Kn, K, M + 1);
                L = Ln;
            }
            return true;
        }

        private static double Rough(double[] K)
        {
            double r = 0;
            for (int j = 0; j + 1 < K.Length; j++) r += (K[j + 1] - K[j]) * (K[j + 1] - K[j]);
            return r;
        }

        private static bool Land(V2 p0, double th0, V2 p1, double turn, double kmax, double[] K, ref double L, int maxIter)
        {
            int M = K.Length - 1, n = M;   // unknowns: K[1..M-1] and L (index M-1 in the vector)
            for (int j = 1; j < M; j++) { Bounds(K, L, kmax, j, out double lo, out double hi); K[j] = Math.Max(lo, Math.Min(hi, K[j])); }
            double r = Res(p0, th0, p1, turn, K, L, out double ex, out double ez, out double et);
            var frozen = new bool[M + 1];
            var W = new double[n];
            var step = new double[n];
            var Kn = new double[M + 1];
            for (int it = 0; it < maxIter; it++)
            {
                if (r < 1e-5) return true;
                Iterations++;
                double[,] J = Jac(p0, th0, p1, turn, K, L, ex, ez, et);
                // a knot pinned at its bound and pushed outward is frozen and the step re-solved
                for (int pass = 0; pass < M + 1; pass++)
                {
                    for (int c = 0; c < n - 1; c++) W[c] = frozen[c + 1] ? 0 : 1;
                    W[n - 1] = 0.5;
                    if (!MinNorm(J, W, new[] { -ex, -ez, -et }, step)) return false;
                    bool changed = false;
                    for (int j = 1; j < M; j++)
                    {
                        if (frozen[j]) continue;
                        Bounds(K, L, kmax, j, out double lo, out double hi);
                        if ((K[j] >= hi - 1e-12 && step[j - 1] > 0) || (K[j] <= lo + 1e-12 && step[j - 1] < 0)) { frozen[j] = true; changed = true; }
                    }
                    if (!changed) break;
                }
                double alpha = 1;
                bool took = false;
                for (int bt = 0; bt < 8; bt++, alpha *= 0.5)
                {
                    Array.Copy(K, Kn, M + 1);
                    double Ln = Math.Max(0.05, L + alpha * step[n - 1]);
                    for (int j = 1; j < M; j++)
                    {
                        Bounds(K, Ln, kmax, j, out double lo, out double hi);
                        Kn[j] = Math.Max(lo, Math.Min(hi, K[j] + alpha * step[j - 1]));
                    }
                    double rn = Res(p0, th0, p1, turn, Kn, Ln, out double nx, out double nz, out double nt);
                    if (rn < r)
                    {
                        Array.Copy(Kn, K, M + 1); L = Ln; r = rn; ex = nx; ez = nz; et = nt; took = true;
                        break;
                    }
                }
                if (!took) return r < 1e-5;
                for (int j = 1; j < M; j++)
                {
                    if (!frozen[j]) continue;
                    Bounds(K, L, kmax, j, out double lo, out double hi);
                    if (K[j] < hi - 1e-9 && K[j] > lo + 1e-9) frozen[j] = false;
                }
            }
            return r < 1e-5;
        }

        private static bool Solve3(double[,] A, double[] b, out double[] x)
        {
            x = new double[3];
            var m = new double[3, 4];
            for (int i = 0; i < 3; i++) { for (int j = 0; j < 3; j++) m[i, j] = A[i, j]; m[i, 3] = b[i]; }
            for (int c = 0; c < 3; c++)
            {
                int p = c;
                for (int r = c + 1; r < 3; r++) if (Math.Abs(m[r, c]) > Math.Abs(m[p, c])) p = r;
                if (Math.Abs(m[p, c]) < 1e-14) return false;
                if (p != c) for (int k = 0; k < 4; k++) { double t = m[c, k]; m[c, k] = m[p, k]; m[p, k] = t; }
                for (int r = 0; r < 3; r++)
                {
                    if (r == c) continue;
                    double f = m[r, c] / m[c, c];
                    for (int k = c; k < 4; k++) m[r, k] -= f * m[c, k];
                }
            }
            for (int i = 0; i < 3; i++) x[i] = m[i, 3] / m[i, i];
            return true;
        }

        /// <summary>A Dubins seed's curvature profile on K knots (box-smoothed over one knot spacing), its length and turn.</summary>
        private static double[] Profile(V2 p0, double th0, double k0, IList<V2> dub, double k1, out double L, out double turn)
        {
            var pts = new List<V2> { p0 };
            pts.AddRange(dub);
            double[] s = Geo.CumLen(pts);
            double Lt = s[s.Length - 1];
            L = Lt;
            int n = pts.Count;
            var hd = new double[n - 1];
            double prev = th0;
            for (int i = 0; i + 1 < n; i++)
            {
                double a = Math.Atan2(pts[i + 1].Z - pts[i].Z, pts[i + 1].X - pts[i].X);
                double d = a - prev;
                while (d > Math.PI) d -= 2 * Math.PI;
                while (d < -Math.PI) d += 2 * Math.PI;
                hd[i] = prev + d; prev = hd[i];
            }
            turn = hd[n - 2] - th0;
            double HeadAt(double at)
            {
                if (at <= 0) return th0;
                if (at >= Lt) return hd[n - 2];
                int i = 0;
                while (i + 1 < n - 1 && s[i + 1] < at) i++;
                return hd[i];
            }
            int M = KnotCount(Lt);
            double h = Lt / M;
            var K = new double[M + 1];
            K[0] = k0; K[M] = k1;
            for (int j = 1; j < M; j++) K[j] = (HeadAt(j * h + h / 2) - HeadAt(j * h - h / 2)) / h;
            return K;
        }

        /// <summary>The curve's points about every <paramref name="step"/>, p0 first, the solved end last.</summary>
        private static List<V2> SampleCurve(V2 p0, double th0, double[] K, double L, double step)
        {
            int M = K.Length - 1;
            int per = Math.Max(1, (int)Math.Ceiling(L / M / step));
            var KK = new double[M * per + 1];   // the same piecewise-linear profile on a finer knot grid
            for (int i = 0; i <= M * per; i++)
            {
                int j = Math.Min(M - 1, i / per);
                double u = (i - j * per) / (double)per;
                KK[i] = K[j] + (K[j + 1] - K[j]) * u;
            }
            Integrate(p0, th0, KK, L, out double[] th, out double[] x, out double[] z);
            var o = new List<V2>(M * per + 1);
            for (int i = 0; i <= M * per; i++) o.Add(new V2(x[i * Sub], z[i * Sub]));
            return o;
        }

        /// <summary>Gentleness cost of a profile: length plus R x bending energy (integral of k^2 over the piecewise-linear k).</summary>
        private static double Energy(double[] K, double L, double kmax)
        {
            int M = K.Length - 1;
            double h = L / M, e = 0;
            for (int j = 0; j < M; j++) e += h * (K[j] * K[j] + K[j] * K[j + 1] + K[j + 1] * K[j + 1]) / 3;
            return e / Math.Max(1e-9, kmax);
        }

        internal sealed class Cand
        {
            public List<V2> Pts;
            public double[] K;
            public double L, Turn, Cost;
        }

        /// <summary>Every converged G2 curve from (p0, th0, k0) to (p1, th1, k1) under kmax, one per distinct seed.</summary>
        internal static List<Cand> Candidates(V2 p0, double th0, double k0, V2 p1, double th1, double k1, double kmax, double step)
        {
            var o = new List<Cand>();
            k0 = Math.Max(-kmax, Math.Min(kmax, k0));
            k1 = Math.Max(-kmax, Math.Min(kmax, k1));
            var h0 = new V2(Math.Cos(th0), Math.Sin(th0));
            var h1 = new V2(Math.Cos(th1), Math.Sin(th1));
            foreach (double f in RadiusFactors)
                foreach (List<V2> dub in HoseMath.DubinsAll(p0, h0, p1, h1, f / kmax, 0.05, true))
                {
                    double[] K = Profile(p0, th0, k0, dub, k1, out double L, out double turnSeed);
                    // the seed's turn is read off its last chord (off the true end heading by k x step / 2): keep only its winding
                    double turn = th1 - th0 + Math.Round((turnSeed - (th1 - th0)) / (2 * Math.PI)) * 2 * Math.PI;
                    bool dup = false;
                    foreach (Cand c in o) if (Math.Abs(c.Turn - turn) < 1e-3 && Math.Abs(c.L - L) < 0.05) dup = true;
                    if (dup) continue;
                    if (!Solve(p0, th0, p1, turn, kmax, K, ref L)) continue;
                    List<V2> P = SampleCurve(p0, th0, K, L, step);
                    P[P.Count - 1] = p1;
                    o.Add(new Cand { Pts = P, K = K, L = L, Turn = turn, Cost = L + Energy(K, L, kmax) });
                }
            return o;
        }

        /// <summary>The gentlest G2 join (see the class summary), sampled about every <paramref name="step"/>; null when none
        /// converges without crossing itself.</summary>
        internal static List<V2> Join(V2 p0, double th0, double k0, V2 p1, double th1, double k1, double kmax, double step, out Seed seed)
        {
            seed = null;
            Cand best = null;
            foreach (Cand c in Candidates(p0, th0, k0, p1, th1, k1, kmax, step))
                if (!HoseMath.SelfIntersects(c.Pts) && (best == null || c.Cost < best.Cost)) best = c;
            if (best == null) return null;
            // the winner alone is faired (smoothest curvature profile with the same ends)
            var K = (double[])best.K.Clone();
            double L = best.L;
            if (Solve(p0, th0, p1, best.Turn, kmax, K, ref L, 40, FairPasses))
            {
                List<V2> P = SampleCurve(p0, th0, K, L, step);
                P[P.Count - 1] = p1;
                if (!HoseMath.SelfIntersects(P)) best = new Cand { Pts = P, K = K, L = L, Turn = best.Turn };
            }
            seed = new Seed { K = best.K, L = best.L, Turn = best.Turn };
            return best.Pts;
        }

        // ------------------------------------------------------------------ hose ends
        /// <summary>Heading of the polyline at arc <paramref name="at"/> (the segment containing it).</summary>
        private static double HeadingAt(IList<V2> p, double[] s, double at, out int seg)
        {
            seg = 0;
            while (seg + 2 < p.Count && s[seg + 1] <= at) seg++;
            return Math.Atan2(p[seg + 1].Z - p[seg].Z, p[seg + 1].X - p[seg].X);
        }

        private static double AngleDiff(double a, double b)
        {
            double d = a - b;
            while (d > Math.PI) d -= 2 * Math.PI;
            while (d < -Math.PI) d += 2 * Math.PI;
            return d;
        }

        /// <summary>
        /// <paramref name="pts"/> (a drawn hose, start at its reel) with its end re-shaped to couple at <paramref name="C"/>:
        /// the last <paramref name="straight"/> runs dead straight along <paramref name="axisIn"/> (unit, the direction the
        /// hose travels INTO the coupling), and the run before it is a G2 join (heading and curvature continuous with the kept
        /// hose at the cut, curvature 0 where the straight starts, |k| &lt;= <paramref name="kmax"/>). The kept hose's samples
        /// are untouched (same indices). Of the cut-backs and seeds that stay clear of their own body and of
        /// <paramref name="partner"/> (the other hose, its own coupling run excepted) and off <paramref name="blocked"/>
        /// ground, the gentlest wins (added length + bending energy). <paramref name="seed"/> (from an earlier solve of the
        /// same layout) is tried first and kept when it still passes. Null when nothing passes: the caller draws the hose as laid.
        /// </summary>
        internal static List<V2> MateTail(List<V2> pts, V2 C, V2 axisIn, double straight, double kmax, IList<V2> partner, Seed seed,
            out Seed used, double width = 0.25, Func<V2, bool> blocked = null)
        {
            used = null;
            if (pts == null || pts.Count < 3) return null;
            axisIn = axisIn.Norm();
            double[] s = Geo.CumLen(pts);
            double Lp = s[s.Length - 1];
            double step = Math.Max(0.05, Math.Min(0.25, Lp / Math.Max(1, pts.Count - 1)));
            V2 Q = C - axisIn * straight;
            double thQ = Math.Atan2(axisIn.Z, axisIn.X);
            // the partner's body, its own coupling run excepted (the two couplings meet there by design)
            var theirs = new List<V2>();
            if (partner != null && partner.Count > 1)
            {
                double[] sp = Geo.CumLen(partner);
                for (int i = 0; i < partner.Count; i++) if (sp[i] < sp[sp.Length - 1] - straight) theirs.Add(partner[i]);
            }
            var cuts = new List<double>();
            // a cached cut-back is tried first only while it still fits the hose (a shorter pose than the seed's would cut before
            // its own start)
            if (seed != null && seed.CutBack > 0 && seed.CutBack <= Math.Max(Lp - 0.3, 0) + 1e-9) cuts.Add(seed.CutBack);
            foreach (double cb in CutBacks) if (cb < Lp - 0.3 && !cuts.Contains(cb)) cuts.Add(cb);
            if (cuts.Count == 0 && Lp > 0.6) cuts.Add(Lp - 0.3);
            List<V2> bestPts = null;
            Seed bestSeed = null;
            double bestCost = double.MaxValue;
            // the winner's cut context, for the fairing pass
            V2 bP0 = default(V2);
            double bTh0 = 0, bSc = 0;
            List<V2> bKept = null;
            bool usedCache = false;
            List<V2> Assemble(List<V2> kept, V2 P0, List<V2> curve)
            {
                var outp = new List<V2>(kept);
                if (V2.Dist(P0, kept[kept.Count - 1]) > 1e-6) outp.Add(P0);
                for (int i = 1; i < curve.Count; i++) outp.Add(curve[i]);
                int ns = Math.Max(1, (int)Math.Ceiling(straight / step));
                for (int i = 1; i <= ns; i++) outp.Add(Q + axisIn * (straight * i / ns));
                return outp;
            }
            for (int ci = 0; ci < cuts.Count; ci++)
            {
                double cb = cuts[ci], sc = Lp - cb;
                double th0 = HeadingAt(pts, s, sc, out int seg);
                double u = (sc - s[seg]) / Math.Max(1e-12, s[seg + 1] - s[seg]);
                V2 P0 = pts[seg] + (pts[seg + 1] - pts[seg]) * u;
                // the kept hose's curvature at the cut: its heading change over the last 0.75 cell before it
                double back = Math.Min(0.75, sc);
                double k0 = back > 0.2 ? AngleDiff(th0, HeadingAt(pts, s, sc - back, out _)) / back : 0;
                k0 = Math.Max(-kmax, Math.Min(kmax, k0));
                var kept = new List<V2>(seg + 2);
                for (int i = 0; i <= seg; i++) kept.Add(pts[i]);
                var cands = new List<Cand>();
                bool seeded = ci == 0 && seed != null && seed.K != null && Math.Abs(seed.CutBack - cb) < 1e-9;
                if (seeded)
                {
                    // the layout's cached winner (already faired): re-landed only, so an unchanged layout redraws identically
                    var K = (double[])seed.K.Clone();
                    K[0] = k0; K[K.Length - 1] = 0;
                    double L = seed.L;
                    double turn = thQ - th0 + Math.Round((seed.Turn - (thQ - th0)) / (2 * Math.PI)) * 2 * Math.PI;
                    if (Solve(P0, th0, Q, turn, kmax, K, ref L))
                    {
                        List<V2> P = SampleCurve(P0, th0, K, L, step);
                        P[P.Count - 1] = Q;
                        cands.Add(new Cand { Pts = P, K = K, L = L, Turn = turn, Cost = L + Energy(K, L, kmax) });
                    }
                }
                if (cands.Count == 0) cands = Candidates(P0, th0, k0, Q, thQ, 0, kmax, step);
                // least disturbance: how far the new run strays from where the hose lay (area between them, cells^2)
                var rawTail = new List<V2>();
                for (int i = seg; i < pts.Count; i++) rawTail.Add(pts[i]);
                foreach (Cand c in cands) c.Cost += DisplaceWeight * Displacement(c.Pts, rawTail);
                cands.Sort((x, y) => x.Cost.CompareTo(y.Cost));
                foreach (Cand c in cands)
                {
                    double cost = c.Cost + straight - cb;
                    if (cost >= bestCost) break;
                    List<V2> outp = Assemble(kept, P0, c.Pts);
                    if (!Clear(outp, kept.Count, sc, theirs, width, blocked)) continue;
                    bestCost = cost;
                    bestPts = outp;
                    bestSeed = new Seed { CutBack = cb, K = c.K, L = c.L, Turn = c.Turn, Cost = cost };
                    bP0 = P0; bTh0 = th0; bSc = sc; bKept = kept;
                    break;
                }
                if (seeded && bestPts != null) { usedCache = true; break; }   // the cached layout still holds: one solve per frame
            }
            if (bestPts != null && !usedCache)
            {
                // fair the winner (smoothest curvature profile with the same ends); kept only if it still clears everything
                var K = (double[])bestSeed.K.Clone();
                double L = bestSeed.L;
                if (Solve(bP0, bTh0, Q, bestSeed.Turn, kmax, K, ref L, 40, FairPasses))
                {
                    List<V2> P = SampleCurve(bP0, bTh0, K, L, step);
                    P[P.Count - 1] = Q;
                    List<V2> outp = Assemble(bKept, bP0, P);
                    if (Clear(outp, bKept.Count, bSc, theirs, width, blocked))
                    {
                        bestPts = outp;
                        bestSeed = new Seed { CutBack = bestSeed.CutBack, K = K, L = L, Turn = bestSeed.Turn, Cost = bestSeed.Cost };
                    }
                }
            }
            used = bestSeed;
            return bestPts;
        }

        /// <summary>Weight of <see cref="Displacement"/> in MateTail's cost: a coupling should move the hoses as little as it
        /// can, so the hose a player laid still lies where it was laid.</summary>
        public const double DisplaceWeight = 0.5;

        /// <summary>Area (cells^2) between a new run and the polyline it replaces: each sample's distance to the old run x its
        /// spacing.</summary>
        internal static double Displacement(IList<V2> run, IList<V2> old)
        {
            double a = 0;
            for (int i = 1; i < run.Count; i++)
            {
                double best = double.MaxValue;
                for (int j = 0; j + 1 < old.Count; j++) best = Math.Min(best, SegDist(run[i], old[j], old[j + 1]));
                if (old.Count == 1) best = V2.Dist(run[i], old[0]);
                a += best * V2.Dist(run[i - 1], run[i]);
            }
            return a;
        }

        private static double SegDist(V2 p, V2 a, V2 b)
        {
            V2 ab = b - a;
            double l2 = ab.X * ab.X + ab.Z * ab.Z;
            double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((p.X - a.X) * ab.X + (p.Z - a.Z) * ab.Z) / l2));
            return V2.Dist(p, a + ab * t);
        }

        /// <summary>A solved hose-to-hose coupling: the axis (unit, the direction hose A travels into it; B travels -Axis), the
        /// coupling point, and each end's cached solve.</summary>
        internal sealed class Mate
        {
            public V2 C, Axis;
            public Seed SeedA, SeedB;
            public double Cost;
            /// <summary>A's re-shaped end as the pair solve accepted it: B was judged clear of this body, so
            /// <see cref="MateEnd"/> re-solves B against it too.</summary>
            public List<V2> PtsA;
        }

        /// <summary>Unit direction a polyline travels into its last point (chord over its last ~0.75 cell).</summary>
        internal static V2 Arrival(IList<V2> p)
        {
            int n = p.Count, i = n - 1;
            double acc = 0;
            while (i > 0 && acc < 0.75) { acc += V2.Dist(p[i - 1], p[i]); i--; }
            return (p[n - 1] - p[i]).Norm();
        }

        /// <summary>
        /// Two hose ends coupled face to face at <paramref name="C"/>. The coupling axis is chosen, not assumed: A's own
        /// arrival, B's own arrival reversed, and their bisector are tried, each end re-shaped by <see cref="MateTail"/> (A
        /// travelling along the axis, B against it, each clear of the other), and the axis with the least summed cost wins --
        /// two hoses meeting at a right angle each bend half way rather than one looping round the other. Null when no axis
        /// works (the caller draws both as laid). With the clothoid fit on (<see cref="HoseMath.G2On"/>) each end is re-shaped
        /// by <see cref="MateTailG2"/> instead: the hose's length kept and nothing within <paramref name="leadA"/> /
        /// <paramref name="leadB"/> (each hose's straight lead-out from its nozzle) touched.
        /// </summary>
        internal static Mate MatePair(List<V2> A, List<V2> B, V2 C, double kmax, double visible, out List<V2> Am, out List<V2> Bm,
            double leadA = 0, double leadB = 0)
        {
            Am = Bm = null;
            if (A == null || B == null || A.Count < 3 || B.Count < 3) return null;
            double straight = CouplingStraight(visible), width = visible;
            V2 ua = Arrival(A), ub = Arrival(B);
            var axes = new List<V2> { ua, -ub };
            V2 bis = ua - ub;
            if (bis.Len > 0.2) axes.Add(bis.Norm());
            if (HoseMath.G2On) return MatePairG2(A, B, C, axes, straight, kmax, width, leadA, leadB, out Am, out Bm);
            Mate best = null;
            foreach (V2 u in axes)
            {
                List<V2> a, b;
                Seed sa = null, sb = null;
                double cost;
                a = MateTail(A, C, u, straight, kmax, null, null, out sa, width);
                if (a == null) continue;
                b = MateTail(B, C, -u, straight, kmax, a, null, out sb, width);
                if (b == null) continue;
                cost = sa.Cost + sb.Cost;
                // A's re-shaped end must clear B's final body too (B's own coupling run excepted)
                if (!ClearOf(a, A, b, straight, width)) continue;
                if (best != null && cost >= best.Cost) continue;
                best = new Mate { C = C, Axis = u, SeedA = sa, SeedB = sb, Cost = cost, PtsA = a };
                Am = a; Bm = b;
            }
            return best;
        }

        /// <summary>Rings (cells) the coupling point may slide back from <c>C</c> when the clothoid mate keeps both lengths.</summary>
        internal static readonly double[] MateSlide = { 0, 0.3, 0.6, 1.0, 1.6, 2.4 };

        /// <summary>
        /// <see cref="MatePair"/> with the clothoid fit on. Both hoses keep their length (R6), so turning either end onto a
        /// shared axis costs material it does not have if the coupling stays where the two were laid: every bend toward the
        /// other hose lengthens the run to <c>C</c>. The coupling therefore slides -- it is where the two hoses' ends meet,
        /// not a fixed point -- first not at all, then back by each ring of <see cref="MateSlide"/> toward the inner corner
        /// (behind both arrivals), behind A and behind B. The first ring with any axis whose two ends both fit, are clear of
        /// each other and keep their leads wins, cheapest pair inside it. Null when no ring works.
        /// </summary>
        private static Mate MatePairG2(List<V2> A, List<V2> B, V2 C, List<V2> axes, double straight, double kmax, double width,
            double leadA, double leadB, out List<V2> Am, out List<V2> Bm)
        {
            Am = Bm = null;
            V2 ua = Arrival(A), ub = Arrival(B);
            var dirs = new List<V2>();
            V2 corner = -(ua + ub);
            if (corner.Len > 0.2) dirs.Add(corner.Norm());
            dirs.Add(-ua); dirs.Add(-ub);
            foreach (V2 back in new[] { -ua, -ub }) { dirs.Add((back + back.Perp).Norm()); dirs.Add((back - back.Perp).Norm()); }
            Mate best = null;
            foreach (double r in MateSlide)
            {
                foreach (V2 d in r == 0 ? new List<V2> { new V2(0, 0) } : dirs)
                {
                    V2 Ci = C + d * r;
                    foreach (V2 u in axes)
                    {
                        List<V2> a = MateTailG2(A, Ci, u, straight, kmax, null, width, leadA, out double ca);
                        if (a == null) continue;
                        List<V2> b = MateTailG2(B, Ci, -u, straight, kmax, a, width, leadB, out double cb);
                        if (b == null) continue;
                        if (!ClearOf(a, A, b, straight, width)) continue;
                        if (best != null && ca + cb >= best.Cost) continue;
                        best = new Mate { C = Ci, Axis = u, Cost = ca + cb, PtsA = a };
                        Am = a; Bm = b;
                    }
                }
                if (best != null) break;
            }
            return best;
        }

        /// <summary>One end of a solved pair re-shaped onto its coupling (<paramref name="isA"/>: A travels along the axis, B
        /// against it): <see cref="MateTailG2"/> with the fit on, else <see cref="MateTail"/> with the pair's cached seed. B is
        /// re-solved clear of A's accepted end (<see cref="Mate.PtsA"/>), as the pair solve judged it, so a window the pair
        /// refused for crossing A is refused here too. The game's draw and the offline ruler share it. Null when the re-shape
        /// fails (the caller draws the pose as laid).</summary>
        internal static List<V2> MateEnd(List<V2> pts, Mate m, bool isA, double kmax, double visible, double startLead)
        {
            V2 ax = isA ? m.Axis : -m.Axis;
            double straight = CouplingStraight(visible);
            IList<V2> partner = isA ? null : m.PtsA;
            if (HoseMath.G2On) return MateTailG2(pts, m.C, ax, straight, kmax, partner, visible, startLead, out _);
            return MateTail(pts, m.C, ax, straight, kmax, partner, isA ? m.SeedA : m.SeedB, out _, visible);
        }

        /// <summary>
        /// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 2: <paramref name="pts"/> with its end re-shaped to couple at
        /// <paramref name="C"/> along <paramref name="axisIn"/> by <see cref="HoseClothoid.TailOnto"/> -- the cut is G2 (position,
        /// heading and curvature kept), the re-solved window has the SAME material length as the run it replaces (so the hose
        /// keeps its length, R6), the last <paramref name="straight"/> runs dead straight along the axis, and nothing within
        /// <paramref name="startLead"/> + 0.25 cell of the reel is touched (R2/R3 at the start). The window grows until the new
        /// run is clear of its own body and of <paramref name="partner"/> (its coupling run excepted) as <see cref="MateTail"/>
        /// requires. <paramref name="cost"/> = bending energy (R x integral of k^2) + <see cref="DisplaceWeight"/> x the area
        /// between the new run and the old. Null when no window passes.
        /// </summary>
        internal static List<V2> MateTailG2(List<V2> pts, V2 C, V2 axisIn, double straight, double kmax, IList<V2> partner,
            double width, double startLead, out double cost)
        {
            cost = double.MaxValue;
            if (pts == null || pts.Count < 3) return null;
            axisIn = axisIn.Norm();
            var theirs = new List<V2>();
            if (partner != null && partner.Count > 1)
            {
                double[] sp = Geo.CumLen(partner);
                for (int i = 0; i < partner.Count; i++) if (sp[i] < sp[sp.Length - 1] - straight) theirs.Add(partner[i]);
            }
            List<V2> o = HoseClothoid.TailOnto(pts, C, axisIn, straight, kmax, startLead, out int kept, (q, k) =>
            {
                double[] sq = Geo.CumLen(q);
                return Clear(q, k, sq[Math.Max(0, k - 1)], theirs, width, null);
            });
            if (o == null) return null;
            var oldTail = new List<V2>();
            for (int i = Math.Max(0, kept - 1); i < pts.Count; i++) oldTail.Add(pts[i]);
            var newTail = new List<V2>();
            for (int i = Math.Max(0, kept - 1); i < o.Count; i++) newTail.Add(o[i]);
            cost = BendEnergy(newTail) / Math.Max(1e-9, kmax) + DisplaceWeight * Displacement(newTail, oldTail);
            return o;
        }

        /// <summary>Integral of k^2 ds along a polyline (turning angle squared over the mean spacing at each interior sample).</summary>
        private static double BendEnergy(IList<V2> p)
        {
            double e = 0;
            for (int i = 1; i + 1 < p.Count; i++)
            {
                V2 a = p[i] - p[i - 1], b = p[i + 1] - p[i];
                double la = a.Len, lb = b.Len;
                if (la < 1e-9 || lb < 1e-9) continue;
                double t = AngleDiff(Math.Atan2(b.Z, b.X), Math.Atan2(a.Z, a.X)), h = 0.5 * (la + lb);
                e += t * t / h;
            }
            return e;
        }

        /// <summary>The part of <paramref name="a"/> that differs from <paramref name="raw"/> stays a width clear of
        /// <paramref name="other"/>'s body, both coupling runs excepted.</summary>
        private static bool ClearOf(List<V2> a, List<V2> raw, List<V2> other, double straight, double width)
        {
            int same = 0;
            while (same < a.Count && same < raw.Count && V2.Dist(a[same], raw[same]) < 1e-9) same++;
            double[] sa = Geo.CumLen(a), so = Geo.CumLen(other);
            double La = sa[sa.Length - 1], Lo = so[so.Length - 1];
            for (int i = Math.Max(0, same - 1); i < a.Count; i++)
            {
                if (sa[i] >= La - straight) break;
                for (int j = 0; j < other.Count; j++)
                    if (so[j] < Lo - straight && V2.Dist(a[i], other[j]) < width) return false;
            }
            return true;
        }

        /// <summary>The re-shaped hose crosses nothing: no self crossing, no stretch of its new part within one width of its own
        /// body more than 4 widths of arc away, none within one width of the partner's body, none on blocked ground.</summary>
        private static bool Clear(List<V2> P, int keptCount, double sc, List<V2> theirs, double width, Func<V2, bool> blocked)
        {
            if (HoseMath.SelfIntersects(P)) return false;
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1];
            int from = Math.Max(0, keptCount - 1);
            // the kept hose's last 2 cells before the cut must already be clear of the partner (a longer cut-back fixes that)
            for (int i = from; i >= 0 && s[i] > sc - 2; i--)
                foreach (V2 q in theirs) if (V2.Dist(P[i], q) < width) return false;
            for (int i = from; i < P.Count; i++)
            {
                if (blocked != null && blocked(P[i])) return false;
                for (int j = 0; j < P.Count; j++)
                    if (Math.Abs(s[j] - s[i]) > 4 * width && V2.Dist(P[i], P[j]) < width) return false;
                if (s[i] >= L - 1e-9) continue;
                foreach (V2 q in theirs) if (V2.Dist(P[i], q) < width) return false;
            }
            return true;
        }
    }
}
