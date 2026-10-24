using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS (owner 2026-10-23 22:15: "Each pipe segment must join with the others absolutely by
    /// location and slope and curvature"). A hose centreline as a chain of clothoid pieces in MATERIAL coordinates: curvature is
    /// stored at nodes ~0.5 cell of hose apart and varies linearly between them, heading and position are its integrals. So
    /// position, heading and curvature are continuous everywhere by construction (G2), and the hard limits are linear in the
    /// unknowns: |kappa| &lt;= kmax at every node (hence everywhere), |kappa(i+1) - kappa(i)| &lt;= J x interval (the sharpest
    /// curvature ramp), kappa = 0 over every straight lead and joiner span, and the total length is exactly the hose's.
    /// The ends (position, and heading where a fitting fixes the axis) are hard equalities of a Gauss-Newton SQP (analytic
    /// Jacobian, KKT step, L1 merit line search, then a minimum-norm Newton polish), the limits are steep one-sided penalties,
    /// and both are then checked exactly; the shape preference (stay on the planned route, fair curvature) is the only soft part.
    /// Design: design/RimMandrake/flowworks_hose_geometry_g2_2026-10-23.md (method chosen after the GPT attack, section 5).
    /// Verse-free; the offline selftest (HoseCurveChecks) and the game share it.
    /// </summary>
    internal static class HoseClothoid
    {
        /// <summary>Material spacing of the curvature nodes (cells); the drawn samples are twice as dense.</summary>
        public const double NodeStep = 0.5;
        /// <summary>The steepest curvature ramp the solver allows, as a multiple of kmax per cell (the ruler's cap is 2.5).</summary>
        public const double JerkPerKmax = 2.2;
        /// <summary>An end equality counts as met within this (cells / radians).</summary>
        public const double EndTol = 2e-4;
        /// <summary>The largest stretch (fraction of length) and turn (rad) Snap may use to close a near-taut gap.</summary>
        public const double SnapFrac = 0.01, SnapTurn = 0.01;

        public sealed class Problem
        {
            public V2 P0;
            /// <summary>Start heading (radians); null = free (an end with no fitting axis).</summary>
            public double? Theta0;
            /// <summary>Curvature at the start node (0 at a fitting or free end; the kept hose's at a tail cut).</summary>
            public double Kappa0;
            public V2 P1;
            /// <summary>End heading (radians, the direction of travel at the end); null = free.</summary>
            public double? Theta1;
            /// <summary>Straight run (kappa 0) from the start / to the end, cells of hose.</summary>
            public double Lead0, Lead1;
            /// <summary>Material length of the hose (exact).</summary>
            public double L;
            /// <summary>The route the shape should stay on (matched by arc fraction).</summary>
            public IList<V2> Track;
            public double TrackWeight = 1;
            /// <summary>Further straight spans [s0, s1] in material coordinates (joiners).</summary>
            public List<(double s0, double s1)> Straight = new List<(double, double)>();
            public double Kmax;
            /// <summary>Sharpness limit (1/cell^2); 0 = JerkPerKmax x Kmax.</summary>
            public double J = 0;
            /// <summary>Drawn samples per node interval.</summary>
            public int Sub = 2;
            /// <summary>Node spacing (cells of hose); 0 = <see cref="NodeStep"/>. A short window takes finer nodes so it keeps
            /// enough free curvatures for its end equalities.</summary>
            public double Step = 0;
        }

        public sealed class Result
        {
            public bool Feasible;
            public string Why;
            public double[] Kappa;
            public double Theta0, Step, EndErr, HeadErr;
            public bool Snapped;
            public int Iterations;
            public List<V2> Pts;
        }

        /// <summary>Cost counters for the offline ruler (SolverCost); a few adds per solve.</summary>
        public static long Solves, Iters, Ticks, Feasibles, FeasIters, FeasTicks;

        private static double Clamp(double v, double lo, double hi) => v < lo ? lo : v > hi ? hi : v;

        // ------------------------------------------------------------------------------------------------ integration
        /// <summary>Heading and position along one clothoid piece: start (p, th), curvature k0 -> k1 over length l, at t.</summary>
        private static V2 Piece(V2 p, double th, double k0, double k1, double l, double t)
        {
            // 4-point Gauss-Legendre over [0, t] (heading is quadratic in t, so the error is tiny for t <= 0.5 cell)
            double x = 0, z = 0;
            for (int g = 0; g < 4; g++)
            {
                double tau = 0.5 * t * (1 + GX[g]);
                double a = th + k0 * tau + (k1 - k0) * tau * tau / (2 * l);
                x += GW[g] * Math.Cos(a);
                z += GW[g] * Math.Sin(a);
            }
            return new V2(p.X + 0.5 * t * x, p.Z + 0.5 * t * z);
        }

        private static readonly double[] GX = { -0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526 };
        private static readonly double[] GW = { 0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538 };

        /// <summary>The curve's drawn samples (nodes and sub-samples), the end heading out.</summary>
        internal static List<V2> Sample(V2 p0, double th0, double[] K, double l, int sub, out double thEnd)
        {
            var o = new List<V2>(K.Length * sub);
            V2 p = p0;
            double th = th0;
            o.Add(p);
            for (int i = 0; i + 1 < K.Length; i++)
            {
                for (int q = 1; q <= sub; q++) o.Add(Piece(p, th, K[i], K[i + 1], l, l * q / sub));
                p = o[o.Count - 1];
                th += 0.5 * l * (K[i] + K[i + 1]);
            }
            thEnd = th;
            return o;
        }

        // ------------------------------------------------------------------------------------------------ solve
        /// <summary>Solves <paramref name="pr"/>. The result's points always come from the curve (never snapped onto the ends);
        /// Feasible = every end equality met within EndTol and every bound held.</summary>
        public static Result Solve(Problem pr)
        {
            long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
            long it0 = Iters;
            Result r = SolveCore(pr);
            long dt = System.Diagnostics.Stopwatch.GetTimestamp() - t0;
            Ticks += dt;
            if (r.Feasible) { Feasibles++; FeasIters += Iters - it0; FeasTicks += dt; }
            return r;
        }

        private static Result SolveCore(Problem pr)
        {
            Solves++;
            var res = new Result();
            double kmax = pr.Kmax, J = pr.J > 0 ? pr.J : JerkPerKmax * pr.Kmax;
            int N = Math.Max(2, (int)Math.Ceiling(pr.L / (pr.Step > 0 ? pr.Step : NodeStep) - 1e-9));
            double l = pr.L / N;
            int sub = Math.Max(1, pr.Sub);
            res.Step = l / sub;
            // fixed nodes: the start node at Kappa0, the end node at 0, every node of a straight lead or span
            var fixedK = new double?[N + 1];
            fixedK[0] = Clamp(pr.Kappa0, -kmax, kmax);
            fixedK[N] = 0;
            // a straight run covers its length plus one drawn sample, so the ruler's stencil at its release reads it straight
            double pad = res.Step + 1e-6;
            for (int i = 0; i <= N; i++)
            {
                double s = i * l;
                if (pr.Lead0 > 0 && s <= pr.Lead0 + l + pad - 1e-9 && s <= Math.Ceiling((pr.Lead0 + pad) / l - 1e-9) * l + 1e-9) fixedK[i] = 0;
                if (pr.Lead1 > 0 && pr.L - s <= Math.Ceiling((pr.Lead1 + pad) / l - 1e-9) * l + 1e-9) fixedK[i] = 0;
                foreach (var sp in pr.Straight)
                    if (s >= Math.Floor((sp.s0 - pad) / l) * l - 1e-9 && s <= Math.Ceiling((sp.s1 + pad) / l) * l + 1e-9) fixedK[i] = 0;
            }
            if (pr.Lead0 > 0 && Math.Abs(fixedK[0].Value) > 0) fixedK[0] = 0;
            var vars = new List<int>();
            for (int i = 0; i <= N; i++) if (!fixedK[i].HasValue) vars.Add(i);
            bool freeTh = !pr.Theta0.HasValue;
            int nv = vars.Count + (freeTh ? 1 : 0);
            // the route, resampled at the drawn samples' arc fractions
            int ns = N * sub + 1;
            var Q = new V2[ns];
            {
                double[] sr = Geo.CumLen(pr.Track);
                double Lr = sr[sr.Length - 1];
                int j = 0;
                for (int q = 0; q < ns; q++)
                {
                    double t = Lr * q / (ns - 1);
                    while (j < sr.Length - 2 && sr[j + 1] < t) j++;
                    double seg = sr[j + 1] - sr[j];
                    double u = seg < 1e-12 ? 0 : Clamp((t - sr[j]) / seg, 0, 1);
                    Q[q] = pr.Track[j] + (pr.Track[j + 1] - pr.Track[j]) * u;
                }
            }
            // the initial curvature: the route's own, read at each node, then made to satisfy every bound
            var K = new double[N + 1];
            {
                for (int i = 0; i <= N; i++)
                {
                    if (fixedK[i].HasValue) { K[i] = fixedK[i].Value; continue; }
                    int q = Math.Min(ns - 2, Math.Max(1, i * sub));
                    int a = Math.Max(0, q - sub), b = Math.Min(ns - 1, q + sub);
                    V2 u = Q[q] - Q[a], v = Q[b] - Q[q];
                    double len = 0.5 * (u.Len + v.Len);
                    K[i] = len < 1e-9 ? 0 : Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z) / len;
                }
                MakeFeasible(K, fixedK, kmax, J * l);
                if (!BoundsHold(K, kmax, J * l, 1e-9)) { Array.Clear(K, 0, K.Length); for (int i = 0; i <= N; i++) if (fixedK[i].HasValue) K[i] = fixedK[i].Value; MakeFeasible(K, fixedK, kmax, J * l); }
            }
            if (!BoundsHold(K, kmax, J * l, 1e-9)) { res.Why = "no curvature profile meets the straight runs and the ramp limit"; return Finish(res, pr, K, pr.Theta0 ?? 0, l, sub); }
            double th0 = pr.Theta0 ?? Math.Atan2((Q[Math.Min(ns - 1, sub)] - Q[0]).Z, (Q[Math.Min(ns - 1, sub)] - Q[0]).X);
            // the end heading target, unwrapped to the turn the route makes
            double th1 = 0;
            if (pr.Theta1.HasValue)
            {
                Sample(pr.P0, th0, K, l, sub, out double thE);
                th1 = pr.Theta1.Value + Math.Round((thE - pr.Theta1.Value) / (2 * Math.PI)) * 2 * Math.PI;
            }
            // Gauss-Newton SQP on the node curvatures (2026-10-24, replaces a finite-difference Levenberg-Marquardt that cost
            // seconds per lay): the soft part (track the route at the nodes, fair curvature, bending energy, and the curvature
            // and ramp limits as one-sided quadratic penalties, which are linear in the unknowns and so exact in Gauss-Newton) is
            // minimised subject to the end equalities (position, and heading where a fitting fixes it) as hard linearised
            // constraints, solved through the KKT system's Schur complement. The Jacobian is analytic: past node j+1 a change of
            // kappa_j only turns the rest of the chain rigidly about node j+1, so every product of two columns over the track
            // rows is a closed form in suffix sums and the normal matrix costs O(nv^2) per iteration, not O(rows x nv^2).
            double dk = J * l, kIn = kmax * 0.995, dIn = dk * 0.995;
            int nE = 2 + (pr.Theta1.HasValue ? 1 : 0);
            double wT2 = Math.Max(1e-9, pr.TrackWeight) * l, wF2 = 0.15 / l, wB2 = 0.02 * l, wI2 = 1e6;
            var Qn = new V2[N + 1];
            for (int i = 0; i <= N; i++) Qn[i] = Q[Math.Min(ns - 1, i * sub)];
            int nk = vars.Count;
            var varOf = new int[N + 1];
            for (int i = 0; i <= N; i++) varOf[i] = -1;
            for (int v = 0; v < nk; v++) varOf[vars[v]] = v;
            var pN = new V2[N + 1];
            var thN = new double[N + 1];
            var E0 = new V2[N];
            var E1 = new V2[N];
            // the node chain (positions, headings) and, per interval, d(end of piece)/d(k at its start, k at its end)
            void Chain(double[] KK, double t0, bool derivs)
            {
                pN[0] = pr.P0;
                thN[0] = t0;
                for (int i = 0; i < N; i++)
                {
                    double x = 0, z = 0, x0 = 0, z0 = 0, x1 = 0, z1 = 0, k0 = KK[i], k1 = KK[i + 1], th = thN[i];
                    for (int g = 0; g < 4; g++)
                    {
                        double tau = 0.5 * l * (1 + GX[g]);
                        double q2 = tau * tau / (2 * l);
                        double a = th + k0 * tau + (k1 - k0) * q2;
                        double c = Math.Cos(a) * GW[g], s = Math.Sin(a) * GW[g];
                        x += c; z += s;
                        if (derivs) { x0 += -s * (tau - q2); z0 += c * (tau - q2); x1 += -s * q2; z1 += c * q2; }
                    }
                    pN[i + 1] = new V2(pN[i].X + 0.5 * l * x, pN[i].Z + 0.5 * l * z);
                    thN[i + 1] = th + 0.5 * l * (k0 + k1);
                    if (derivs) { E0[i] = new V2(0.5 * l * x0, 0.5 * l * z0); E1[i] = new V2(0.5 * l * x1, 0.5 * l * z1); }
                }
            }
            V2 Rot(V2 a) => new V2(-a.Z, a.X);
            double SoftCost(double[] KK)
            {
                double f = 0;
                for (int q = 1; q <= N; q++) { V2 d = pN[q] - Qn[q]; f += wT2 * (d.X * d.X + d.Z * d.Z); }
                for (int i = 0; i < N; i++) { double d = KK[i + 1] - KK[i]; f += wF2 * d * d; double o = Math.Abs(d) - dIn; if (o > 0) f += wI2 * o * o; }
                for (int i = 0; i <= N; i++) { f += wB2 * KK[i] * KK[i]; double o = Math.Abs(KK[i]) - kIn; if (o > 0) f += wI2 * o * o; }
                return 0.5 * f;
            }
            double[] Cons()
            {
                var c = new double[nE];
                c[0] = pN[N].X - pr.P1.X; c[1] = pN[N].Z - pr.P1.Z;
                if (nE == 3) c[2] = thN[N] - th1;
                return c;
            }
            var KC = (double[])K.Clone();
            double thC = th0;
            int it = 0, stall = 0, active = 0;
            {
                var U = new V2[nv];
                var Cc = new double[nv];
                var D = new V2[nv];
                var St = new int[nv];
                var Sn = new double[N + 2];
                var Sr = new V2[N + 2];
                var SW = new V2[N + 2];
                var SWr = new double[N + 2];
                var S2 = new double[N + 2];
                var H = new double[nv * nv];
                var g = new double[nv];
                var A = new double[nE * nv];
                double rho = 10, mu = 1e-8;
                bool perturbed = false;
                Chain(KC, thC, true);
                double fC = SoftCost(KC);
                double[] cC = Cons();
                for (; it < 60; it++)
                {
                    Iters++;
                    // columns: rigid form J_q = U + C x Rot(p_q) for q >= St, plus node j's own D at q = j
                    for (int v = 0; v < nk; v++)
                    {
                        int j = vars[v];
                        V2 Dj = j >= 1 ? E1[j - 1] : new V2(0, 0);
                        double dth = j >= 1 ? 0.5 * l : 0;
                        V2 dp1 = Dj + Rot(pN[j + 1] - pN[j]) * dth + E0[j];
                        Cc[v] = dth + 0.5 * l;
                        U[v] = dp1 - Rot(pN[j + 1]) * Cc[v];
                        D[v] = Dj;
                        St[v] = j + 1;
                    }
                    if (freeTh) { U[nv - 1] = -Rot(pN[0]); Cc[nv - 1] = 1; D[nv - 1] = new V2(0, 0); St[nv - 1] = 0; }
                    Sn[N + 1] = 0; Sr[N + 1] = new V2(0, 0); SW[N + 1] = new V2(0, 0); SWr[N + 1] = 0; S2[N + 1] = 0;
                    for (int q = N; q >= 0; q--)
                    {
                        V2 r = q == 0 ? new V2(0, 0) : pN[q] - Qn[q], w = Rot(pN[q]);
                        Sn[q] = Sn[q + 1] + 1;
                        Sr[q] = Sr[q + 1] + r;
                        SW[q] = SW[q + 1] + w;
                        SWr[q] = SWr[q + 1] + w.X * r.X + w.Z * r.Z;
                        S2[q] = S2[q + 1] + w.X * w.X + w.Z * w.Z;
                    }
                    V2 RigidAt(int a, int q) => q >= St[a] ? U[a] + Rot(pN[q]) * Cc[a] : (a < nk && q == vars[a] ? D[a] : new V2(0, 0));
                    double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;
                    for (int a = 0; a < nv; a++)
                    {
                        // the track rows; node 0 is the fixed start (residual 0, column 0)
                        double ga = Dot(U[a], Sr[St[a]]) + Cc[a] * SWr[St[a]];
                        if (a < nk) { int ja = vars[a]; if (ja >= 1) ga += Dot(D[a], pN[ja] - Qn[ja]); }
                        g[a] = wT2 * ga;
                        for (int b = a; b < nv; b++)
                        {
                            // later start = the column with the larger first nonzero row
                            int lo = a, hi = b;
                            int fa = a < nk ? vars[a] : -1, fb = b < nk ? vars[b] : -1;
                            if (fa > fb) { lo = b; hi = a; }
                            int Q0 = St[hi];
                            double h = Sn[Q0] * Dot(U[a], U[b]) + Cc[b] * Dot(U[a], SW[Q0]) + Cc[a] * Dot(U[b], SW[Q0]) + Cc[a] * Cc[b] * S2[Q0];
                            if (hi < nk) { int jh = vars[hi]; if (jh >= 1) h += Dot(RigidAt(lo, jh), D[hi]); }
                            H[a * nv + b] = H[b * nv + a] = wT2 * h;
                        }
                        for (int e = 0; e < nE; e++) A[e * nv + a] = e < 2 ? (e == 0 ? RigidAt(a, N).X : RigidAt(a, N).Z) : Cc[a];
                    }
                    // fairness, bending and the one-sided limit penalties (rows on the node curvatures only)
                    void Pair(int i0, int i1, double w, double r)
                    {
                        int a = varOf[i0], b = varOf[i1];
                        if (a >= 0) { g[a] -= w * r; H[a * nv + a] += w; }
                        if (b >= 0) { g[b] += w * r; H[b * nv + b] += w; }
                        if (a >= 0 && b >= 0) { H[a * nv + b] -= w; H[b * nv + a] -= w; }
                    }
                    for (int i = 0; i < N; i++)
                    {
                        double d = KC[i + 1] - KC[i];
                        Pair(i, i + 1, wF2, d);
                        double o = Math.Abs(d) - dIn;
                        if (o > 0) Pair(i, i + 1, wI2, Math.Sign(d) * o);
                    }
                    for (int v = 0; v < nk; v++)
                    {
                        double kv = KC[vars[v]];
                        g[v] += wB2 * kv; H[v * nv + v] += wB2;
                        double o = Math.Abs(kv) - kIn;
                        if (o > 0) { g[v] += wI2 * Math.Sign(kv) * o; H[v * nv + v] += wI2; }
                    }
                    bool took = false, restart = false;
                    for (int tries = 0; tries < 8 && !took; tries++)
                    {
                        double[] d = KktStep(H, g, A, cC, nv, nE, mu, out double[] lam);
                        if (d == null && !perturbed)
                        {
                            // a degenerate start (a dead straight chain with slack to spare: the end cannot move along the
                            // chord to first order) is broken by one small deterministic drape, then made to hold the bounds
                            perturbed = restart = true;
                            for (int v = 0; v < nk; v++) KC[vars[v]] += 0.15 * kmax * Math.Cos(2 * Math.PI * vars[v] / N);
                            MakeFeasible(KC, fixedK, kIn, dIn);
                            break;
                        }
                        if (d == null) { mu = Math.Max(1e-6, mu * 100); stall++; continue; }
                        for (int e = 0; e < nE; e++) rho = Math.Max(rho, 1.5 * Math.Abs(lam[e]));
                        double phi0 = fC + rho * L1(cC);
                        for (double alpha = 1; alpha > 1e-3 && !took; alpha *= 0.5)
                        {
                            var KN = (double[])KC.Clone();
                            for (int v = 0; v < nk; v++) KN[vars[v]] += alpha * d[v];
                            double thT = freeTh ? thC + alpha * d[nv - 1] : thC;
                            Chain(KN, thT, false);
                            double fN = SoftCost(KN);
                            double[] cN = Cons();
                            if (fN + rho * L1(cN) < phi0 - 1e-12 * (1 + Math.Abs(phi0)))
                            {
                                double moved = 0;
                                for (int v = 0; v < nv; v++) moved = Math.Max(moved, Math.Abs(alpha * d[v]));
                                KC = KN; thC = thT; fC = fN; cC = cN;
                                took = true;
                                mu = Math.Max(1e-10, mu * 0.3);
                                if (moved < 1e-9 && L1(cC) < 1e-7) it = 1000;
                            }
                            else stall++;
                        }
                        if (!took) mu = Math.Max(1e-6, mu * 100);
                    }
                    if (restart) { Chain(KC, thC, true); fC = SoftCost(KC); cC = Cons(); continue; }
                    if (!took || it >= 1000) break;
                    Chain(KC, thC, true);
                }
                if (it >= 1000) it = it - 1000 + 1;
                // polish: a near-met end the merit search stopped short of is closed by minimum-norm Newton steps on the end
                // equalities alone (quadratic convergence; the soft part barely moves), kept only while they shrink the gap
                for (int pol = 0; pol < 6 && L1(cC) > 1e-10 && L1(cC) < 0.1; pol++)
                {
                    Chain(KC, thC, true);
                    for (int v = 0; v < nk; v++)
                    {
                        int j = vars[v];
                        V2 Dj = j >= 1 ? E1[j - 1] : new V2(0, 0);
                        double dth = j >= 1 ? 0.5 * l : 0;
                        double cj = dth + 0.5 * l;
                        V2 dpN = Dj + Rot(pN[j + 1] - pN[j]) * dth + E0[j] + Rot(pN[N] - pN[j + 1]) * cj;
                        A[v] = dpN.X; A[nv + v] = dpN.Z; if (nE == 3) A[2 * nv + v] = cj;
                    }
                    if (freeTh) { V2 r0 = Rot(pN[N] - pN[0]); A[nv - 1] = r0.X; A[2 * nv - 1] = r0.Z; if (nE == 3) A[3 * nv - 1] = 1; }
                    var I = new double[nv * nv];
                    for (int v = 0; v < nv; v++) I[v * nv + v] = 1;
                    double[] d = KktStep(I, new double[nv], A, cC, nv, nE, 0, out _);
                    if (d == null) break;
                    var KN = (double[])KC.Clone();
                    for (int v = 0; v < nk; v++) KN[vars[v]] += d[v];
                    double thT = freeTh ? thC + d[nv - 1] : thC;
                    Chain(KN, thT, false);
                    double[] cN = Cons();
                    if (L1(cN) >= L1(cC)) break;
                    KC = KN; thC = thT; cC = cN;
                }
                for (int i = 0; i <= N; i++) if (Math.Abs(KC[i]) > kIn + 1e-9) active++;
                for (int i = 0; i < N; i++) if (Math.Abs(KC[i + 1] - KC[i]) > dIn + 1e-9) active++;
            }
            res.Iterations = it;
            double[] KF = KC;
            res.Theta0 = thC;
            res = Finish(res, pr, KF, res.Theta0, l, sub);
            res.HeadErr = pr.Theta1.HasValue ? Math.Abs(Sum(KF, l) + res.Theta0 - th1) : 0;
            bool ok = res.EndErr < EndTol && res.HeadErr < EndTol && BoundsHold(KF, kmax, J * l, 1e-6);
            if (!ok && res.EndErr < SnapFrac * pr.L) ok = Snap(res, pr, KF, l, kmax, J * l, th1);
            res.Feasible = ok;
            if (!ok && res.Why == null) res.Why = $"ends not met (gap {res.EndErr:0.0000}, heading {res.HeadErr:0.0000}, {it} it, {stall} stalls, {active} limits pressed, N {N}, free {vars.Count})";
            return res;
        }

        /// <summary>Closes a small end gap left by a near-taut length by the one similarity about the start that lands the end
        /// exactly: a uniform stretch (at most SnapFrac) and a turn (at most SnapTurn rad). A stretch or turn that small is
        /// invisible (well under a pixel per cell and 0.6 degrees) and keeps every derivative continuous; curvature scales by
        /// 1/stretch, so the bounds are re-checked on the scaled profile.</summary>
        private static bool Snap(Result res, Problem pr, double[] K, double l, double kmax, double dk, double th1)
        {
            List<V2> P = res.Pts;
            V2 a = P[P.Count - 1] - pr.P0, b = pr.P1 - pr.P0;
            if (a.Len < 1e-9 || b.Len < 1e-9) return false;
            double sc = b.Len / a.Len;
            double phi = Wrap(Math.Atan2(b.Z, b.X) - Math.Atan2(a.Z, a.X));
            if (Math.Abs(sc - 1) > SnapFrac || Math.Abs(phi) > SnapTurn) return false;
            double c = Math.Cos(phi) * sc, sn = Math.Sin(phi) * sc;
            var Ks = new double[K.Length];
            for (int i = 0; i < K.Length; i++) Ks[i] = K[i] / sc;
            if (!BoundsHold(Ks, kmax, dk / sc, 1e-6)) return false;
            double head = pr.Theta1.HasValue ? Math.Abs(Sum(K, l) + res.Theta0 + phi - th1) : 0;
            if (head > SnapTurn) return false;
            for (int i = 0; i < P.Count; i++)
            {
                V2 d = P[i] - pr.P0;
                P[i] = pr.P0 + new V2(c * d.X - sn * d.Z, sn * d.X + c * d.Z);
            }
            res.Kappa = Ks;
            res.Theta0 += phi;
            res.Step *= sc;
            res.EndErr = V2.Dist(P[P.Count - 1], pr.P1);
            res.HeadErr = head;
            res.Snapped = true;
            return res.EndErr < EndTol;
        }

        private static double Sum(double[] K, double l)
        {
            double t = 0;
            for (int i = 0; i + 1 < K.Length; i++) t += 0.5 * l * (K[i] + K[i + 1]);
            return t;
        }

        private static Result Finish(Result res, Problem pr, double[] K, double th0, double l, int sub)
        {
            res.Kappa = K;
            res.Pts = Sample(pr.P0, th0, K, l, sub, out _);
            res.EndErr = V2.Dist(res.Pts[res.Pts.Count - 1], pr.P1);
            return res;
        }

        internal static bool BoundsHold(double[] K, double kmax, double dk, double tol)
        {
            for (int i = 0; i < K.Length; i++)
            {
                if (Math.Abs(K[i]) > kmax + tol) return false;
                if (i + 1 < K.Length && Math.Abs(K[i + 1] - K[i]) > dk + tol) return false;
            }
            return true;
        }

        /// <summary>Moves the free nodes of K into |k| &lt;= kmax and |dk| &lt;= dk, pinned nodes kept: each free node is held inside
        /// the envelope every pinned node allows it (pinned value +- dk x distance), then neighbours are relaxed in turn.</summary>
        internal static void MakeFeasible(double[] K, double?[] fixedK, double kmax, double dk)
        {
            int n = K.Length;
            var lo = new double[n];
            var hi = new double[n];
            for (int i = 0; i < n; i++) { lo[i] = -kmax; hi[i] = kmax; }
            for (int f = 0; f < n; f++)
            {
                if (!fixedK[f].HasValue) continue;
                for (int i = 0; i < n; i++)
                {
                    double r = dk * Math.Abs(i - f);
                    lo[i] = Math.Max(lo[i], fixedK[f].Value - r);
                    hi[i] = Math.Min(hi[i], fixedK[f].Value + r);
                }
            }
            for (int i = 0; i < n; i++) if (!fixedK[i].HasValue) K[i] = lo[i] > hi[i] ? 0.5 * (lo[i] + hi[i]) : Clamp(K[i], lo[i], hi[i]);
            for (int pass = 0; pass < 2 * n + 4; pass++)
            {
                bool moved = false;
                for (int i = 1; i < n; i++)
                    if (!fixedK[i].HasValue && Math.Abs(K[i] - K[i - 1]) > dk) { K[i] = Clamp(K[i], K[i - 1] - dk, K[i - 1] + dk); moved = true; }
                for (int i = n - 2; i >= 0; i--)
                    if (!fixedK[i].HasValue && Math.Abs(K[i] - K[i + 1]) > dk) { K[i] = Clamp(K[i], K[i + 1] - dk, K[i + 1] + dk); moved = true; }
                if (!moved) break;
            }
        }

        private static double L1(double[] c) { double t = 0; foreach (double v in c) t += Math.Abs(v); return t; }

        /// <summary>One Gauss-Newton step of min 1/2 d'Md + g'd subject to A d = -c (M = H + mu diag, nE &lt;= 3 rows of A): the
        /// Schur complement through one Cholesky of M. Null when M is not positive definite or the constraints are degenerate.</summary>
        internal static double[] KktStep(double[] H, double[] g, double[] A, double[] c, int n, int nE, double mu, out double[] lam)
        {
            lam = new double[nE];
            var M = new double[n * n];
            for (int i = 0; i < n * n; i++) M[i] = H[i];
            for (int i = 0; i < n; i++) M[i * n + i] += mu * (H[i * n + i] + 1e-6) + 1e-12;
            if (!Cholesky(M, n)) return null;
            double[] y = CholSolve(M, n, g);
            var Z = new double[nE][];
            for (int e = 0; e < nE; e++) { var a = new double[n]; Array.Copy(A, e * n, a, 0, n); Z[e] = CholSolve(M, n, a); }
            // (A M^-1 A') lam = c - A M^-1 g
            var S = new double[nE, nE + 1];
            for (int e = 0; e < nE; e++)
            {
                double ay = 0;
                for (int i = 0; i < n; i++) ay += A[e * n + i] * y[i];
                S[e, nE] = c[e] - ay;
                for (int f = 0; f < nE; f++) { double t = 0; for (int i = 0; i < n; i++) t += A[e * n + i] * Z[f][i]; S[e, f] = t; }
            }
            double[] l = Gauss(S, nE);
            if (l == null) return null;
            lam = l;
            var d = new double[n];
            for (int i = 0; i < n; i++)
            {
                double t = y[i];
                for (int e = 0; e < nE; e++) t += Z[e][i] * l[e];
                d[i] = -t;
            }
            return d;
        }

        /// <summary>In-place lower Cholesky of a dense symmetric n x n matrix (row-major); false when not positive definite.</summary>
        private static bool Cholesky(double[] M, int n)
        {
            for (int j = 0; j < n; j++)
            {
                double s = M[j * n + j];
                for (int k = 0; k < j; k++) s -= M[j * n + k] * M[j * n + k];
                if (!(s > 1e-300)) return false;
                double d = Math.Sqrt(s);
                M[j * n + j] = d;
                for (int i = j + 1; i < n; i++)
                {
                    double t = M[i * n + j];
                    int ri = i * n, rj = j * n;
                    for (int k = 0; k < j; k++) t -= M[ri + k] * M[rj + k];
                    M[i * n + j] = t / d;
                }
            }
            return true;
        }

        private static double[] CholSolve(double[] M, int n, double[] b)
        {
            var y = new double[n];
            for (int i = 0; i < n; i++) { double t = b[i]; for (int k = 0; k < i; k++) t -= M[i * n + k] * y[k]; y[i] = t / M[i * n + i]; }
            for (int i = n - 1; i >= 0; i--) { double t = y[i]; for (int k = i + 1; k < n; k++) t -= M[k * n + i] * y[k]; y[i] = t / M[i * n + i]; }
            return y;
        }

        /// <summary>Gaussian elimination with partial pivoting on an n x (n+1) augmented matrix; null when singular.</summary>
        internal static double[] Gauss(double[,] A, int n)
        {
            for (int c = 0; c < n; c++)
            {
                int p = c;
                double best = Math.Abs(A[c, c]);
                for (int r = c + 1; r < n; r++) if (Math.Abs(A[r, c]) > best) { best = Math.Abs(A[r, c]); p = r; }
                if (best < 1e-14) return null;
                if (p != c) for (int k = c; k <= n; k++) { double t = A[c, k]; A[c, k] = A[p, k]; A[p, k] = t; }
                for (int r = c + 1; r < n; r++)
                {
                    double f = A[r, c] / A[c, c];
                    if (f == 0) continue;
                    for (int k = c; k <= n; k++) A[r, k] -= f * A[c, k];
                }
            }
            var x = new double[n];
            for (int r = n - 1; r >= 0; r--)
            {
                double s = A[r, n];
                for (int k = r + 1; k < n; k++) s -= A[r, k] * x[k];
                x[r] = s / A[r, r];
            }
            return x;
        }

        // ------------------------------------------------------------------------------------------------ uses
        /// <summary>Heading of a polyline's first / last stretch (radians).</summary>
        internal static double HeadingOf(V2 d) => Math.Atan2(d.Z, d.X);

        /// <summary>A laid pose re-shaped as one clothoid chain of length <paramref name="L"/> tracking <paramref name="route"/>:
        /// start at route[0] (heading <paramref name="startAxis"/> with a straight <paramref name="lead0"/>, or free), end at
        /// route[last] (arriving along <paramref name="endAxis"/> with a straight <paramref name="lead1"/>, or free). Null result
        /// points when the solve is not feasible.</summary>
        internal static Result Fair(IList<V2> route, double L, V2? startAxis, double lead0, V2? endAxis, double lead1,
            List<(double, double)> spans, double kmax, double trackWeight)
        {
            var pr = new Problem
            {
                P0 = route[0], P1 = route[route.Count - 1], L = L, Track = route, Kmax = kmax, TrackWeight = trackWeight,
                Theta0 = startAxis.HasValue ? HeadingOf(startAxis.Value) : (double?)null, Lead0 = startAxis.HasValue ? lead0 : 0,
                Theta1 = endAxis.HasValue ? HeadingOf(endAxis.Value) : (double?)null, Lead1 = endAxis.HasValue ? lead1 : 0,
            };
            if (spans != null) pr.Straight.AddRange(spans);
            return Solve(pr);
        }

        /// <summary>A drawn hose whose end must couple at <paramref name="end"/> arriving along <paramref name="axisIn"/> (unit,
        /// the direction of travel into the fitting), the last <paramref name="straight"/> cells dead straight: the hose is cut at
        /// an exact arc position, its state there (position, heading, curvature) kept, and the window after it re-solved as a
        /// clothoid chain of the SAME material length; the window grows (2.5, 4, 6 cells, then all but the start lead) until a
        /// solve is feasible (and, given <paramref name="accept"/>, passes it: the whole new pose and its kept count). The kept
        /// samples are untouched, and nothing before <paramref name="startLead"/> + 0.25 cell is ever cut. Null when no window
        /// works. <paramref name="kept"/> = the number of leading samples kept.</summary>
        internal static List<V2> TailOnto(IList<V2> pts, V2 end, V2 axisIn, double straight, double kmax, double startLead, out int kept,
            Func<List<V2>, int, bool> accept = null)
        {
            kept = 0;
            TailWhy = "";
            if (pts == null || pts.Count < 3) return null;
            double[] s = Geo.CumLen(pts);
            double Lp = s[s.Length - 1];
            double minCut = Math.Max(0, startLead) + 0.25;
            foreach (double Wn in new[] { 2.5, 4.0, 6.0, double.MaxValue })
            {
                double W = Math.Min(Wn, Lp - minCut);
                if (W < straight + 0.5) { if (Wn == double.MaxValue) break; continue; }
                double sc = Lp - W;
                int seg = 0;
                while (seg < pts.Count - 2 && s[seg + 1] < sc) seg++;
                double u = Clamp((sc - s[seg]) / Math.Max(1e-12, s[seg + 1] - s[seg]), 0, 1);
                V2 P0 = pts[seg] + (pts[seg + 1] - pts[seg]) * u;
                double th0 = HeadingAt(pts, s, sc);
                // the kept hose's one-sided curvature at the cut: heading change over the 0.5 cell before it
                double back = Math.Min(0.5, sc);
                double k0 = back > 0.2 ? Wrap(th0 - HeadingAt(pts, s, sc - back)) / back : 0;
                // two guides, tried in turn: the old tail bent so it ends on the fitting (keeps the drape the hose had), then a
                // plain approach (on along the cut's heading, round to a point a bend radius plus the straight back from the
                // fitting, then in along its axis) for a fitting the old tail pointed away from
                var tail = new List<V2> { P0 };
                for (int i = seg + 1; i < pts.Count; i++) tail.Add(pts[i]);
                foreach (List<V2> guide in new[] { Bent(tail, end), Approach(P0, th0, end, axisIn, straight, 1 / kmax, W) })
                {
                    var pr = new Problem
                    {
                        P0 = P0, Theta0 = th0, Kappa0 = k0, P1 = end, Theta1 = HeadingOf(axisIn), Lead1 = straight, L = W,
                        Track = guide, Kmax = kmax, TrackWeight = 0.3,
                        // at least ~8 free curvatures between the cut and the straight (3 end equalities)
                        Step = Math.Max(0.15, Math.Min(NodeStep, (W - straight) / 8)),
                    };
                    Result r = Solve(pr);
                    if (!r.Feasible) { TailWhy += $" W{W:0.0}: {r.Why};"; continue; }
                    var o = new List<V2>(seg + 1 + r.Pts.Count);
                    for (int i = 0; i <= seg; i++) o.Add(pts[i]);
                    if (V2.Dist(o[o.Count - 1], P0) < 1e-6) o.RemoveAt(o.Count - 1);
                    int k = o.Count;
                    o.AddRange(r.Pts);
                    if (accept != null && !accept(o, k)) { TailWhy += $" W{W:0.0}: not accepted;"; continue; }
                    kept = k;
                    return o;
                }
                if (W >= Lp - minCut - 1e-9) break;
            }
            return null;
        }

        /// <summary>Why the last TailOnto found no window (diagnostics only).</summary>
        internal static string TailWhy = "";

        /// <summary>The polyline moved, in proportion to arc fraction (smootherstep), so its last point lands on
        /// <paramref name="end"/> while its first stays put.</summary>
        private static List<V2> Bent(List<V2> p, V2 end)
        {
            double[] s = Geo.CumLen(p);
            double L = Math.Max(1e-9, s[s.Length - 1]);
            V2 d = end - p[p.Count - 1];
            var o = new List<V2>(p.Count);
            for (int i = 0; i < p.Count; i++)
            {
                double x = s[i] / L;
                o.Add(p[i] + d * (x * x * x * (x * (6 * x - 15) + 10)));
            }
            return o;
        }

        /// <summary>A plain way in: from <paramref name="p0"/> on along heading <paramref name="th0"/>, to the point a bend
        /// radius plus the straight back from the fitting along its axis, then in along the axis.</summary>
        private static List<V2> Approach(V2 p0, double th0, V2 end, V2 axisIn, double straight, double r, double W)
        {
            V2 pre = end - axisIn * (straight + r);
            double on = Math.Min(r, 0.25 * W);
            return new List<V2> { p0, p0 + new V2(Math.Cos(th0), Math.Sin(th0)) * on, pre, end - axisIn * straight, end };
        }

        private static double Wrap(double a)
        {
            while (a > Math.PI) a -= 2 * Math.PI;
            while (a < -Math.PI) a += 2 * Math.PI;
            return a;
        }

        /// <summary>Heading of the polyline at arc position t (its segment's direction).</summary>
        internal static double HeadingAt(IList<V2> p, double[] s, double t)
        {
            int seg = 0;
            while (seg < p.Count - 2 && s[seg + 1] < t) seg++;
            // skip a degenerate segment
            int a = seg, b = seg + 1;
            while (b < p.Count - 1 && V2.Dist(p[a], p[b]) < 1e-9) b++;
            V2 d = p[b] - p[a];
            return Math.Atan2(d.Z, d.X);
        }
    }
}
