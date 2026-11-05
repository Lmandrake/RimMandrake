// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: the clothoid-chain solver (Hose/HoseClothoid.cs) on synthetic problems with known
// answers, measured by the same ruler as the stations (HoseCurveMetrics): a taut straight, a slack straight that must drape, a
// quarter turn and a U-turn between fittings, a tail re-laid onto a port, and a hose-to-hose mate. Each case also checks the solver's own claims
// (exact length, ends met, bounds held) against the drawn points, so a solver that reports Feasible on a wrong curve fails.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseClothoidChecks
    {
        private const double R = 1.2, Kmax = 1 / R;

        private static List<V2> Line(V2 a, V2 b, int n = 20)
        {
            var o = new List<V2>();
            for (int i = 0; i <= n; i++) o.Add(a + (b - a) * (i / (double)n));
            return o;
        }

        private static V2 Dir(double th) => new V2(Math.Cos(th), Math.Sin(th));

        /// <summary>Solves, then checks the result with the ruler: the solver's points must start and end where asked, be the
        /// asked length, and pass every requirement.</summary>
        private static void Check(string name, HoseClothoid.Problem pr, double ruleStraight0, double ruleStraight1)
        {
            HoseClothoid.Result r = HoseClothoid.Solve(pr);
            string diag = $"{name}: feasible={r.Feasible} why={r.Why} it={r.Iterations} gap={r.EndErr:0.00000} head={r.HeadErr:0.00000}";
            if (!r.Feasible) throw new Exception(diag);
            if (r.HeadErr >= HoseClothoid.EndTol) throw new Exception(diag + " Feasible with the end heading off by >= EndTol (HOSESNAP_FIX_HEADING_AND_RAMP_SCALE)");
            double len = Geo.Length(r.Pts);
            if (Math.Abs(len - pr.L) > 1e-3 * pr.L) throw new Exception(diag + $" length {len:0.0000} vs {pr.L:0.0000}");
            var s = pr.Theta0.HasValue ? HoseCurveMetrics.EndSpec.Fitting(pr.P0, Dir(pr.Theta0.Value), ruleStraight0, "start")
                                       : HoseCurveMetrics.EndSpec.Free(pr.P0, "start");
            var e = pr.Theta1.HasValue ? HoseCurveMetrics.EndSpec.Fitting(pr.P1, -Dir(pr.Theta1.Value), ruleStraight1, "end")
                                       : HoseCurveMetrics.EndSpec.Free(pr.P1, "end");
            HoseCurveMetrics.Report rep = HoseCurveMetrics.Measure(r.Pts, s, e, Kmax, pr.L);
            if (!rep.Ok) throw new Exception(diag + " ruler: " + rep.Line());
        }

        internal static void Run(Action<string, Action> Case)
        {
            V2 o = new V2(0, 0);
            Case("HoseClothoid taut straight between two fittings", () =>
                Check("taut", new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 1.6, P1 = new V2(5, 0), Theta1 = 0, Lead1 = 0.6,
                    L = 5, Track = Line(o, new V2(5, 0)), Kmax = Kmax }, 1.6, 0.6));
            Case("HoseClothoid slack straight drapes (10% extra, free ends)", () =>
                Check("slack", new HoseClothoid.Problem { P0 = o, P1 = new V2(8, 0), L = 8.8, Track = Line(o, new V2(8, 0)), Kmax = Kmax }, 0, 0));
            Case("HoseClothoid slack straight between fittings (5% extra)", () =>
                Check("slackfit", new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 1.6, P1 = new V2(10, 0), Theta1 = 0, Lead1 = 0.6,
                    L = 10.5, Track = Line(o, new V2(10, 0)), Kmax = Kmax }, 1.6, 0.6));
            Case("HoseClothoid quarter turn between fittings", () =>
            {
                var tr = new List<V2> { o, new V2(2.5, 0), new V2(4, 1.5), new V2(4, 5) };
                Check("quarter", new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 1.6, P1 = new V2(4, 5), Theta1 = Math.PI / 2, Lead1 = 0.6,
                    L = Geo.Length(tr) * 1.03, Track = tr, Kmax = Kmax }, 1.6, 0.6);
            });
            Case("HoseClothoid a straight lead is its own length, not rounded out to the node grid", () =>
            {
                // HOSE_FIT_HARDEN_FREE_LENGTH_SHORT_LEAD: the solver used to pin every node within a straight run rounded OUT to
                // its uniform grid plus one drawn sample, so a 0.6 lead stayed dead straight to arc 1.0 (and a 0.75 coupling grew
                // to ~1.15), which tight mates cannot afford. Can-fail: HEAD 8d64560c3f's solver draws heading 0 at arc 0.9 here.
                var tr = new List<V2> { o, new V2(2.5, 0), new V2(4, 1.5), new V2(4, 5) };
                var pr = new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 0.6, P1 = new V2(4, 5), Theta1 = Math.PI / 2, Lead1 = 0.6,
                    L = Geo.Length(tr) * 1.03, Track = tr, Kmax = Kmax };
                Check("exact-lead", pr, 0.6, 0.6);
                List<V2> p = HoseClothoid.Solve(pr).Pts;
                double[] s = Geo.CumLen(p);
                double Head(double at)
                {
                    int i = 0;
                    while (i < p.Count - 2 && s[i + 1] < at) i++;
                    return Math.Atan2(p[i + 1].Z - p[i].Z, p[i + 1].X - p[i].X);
                }
                double h06 = Math.Abs(Head(0.59)), h09 = Math.Abs(Head(0.9));
                if (h06 > 1e-9 || h09 < 1e-3) throw new Exception($"heading at arc 0.59 {h06:0.000000} (want 0), at 0.9 {h09:0.000000} (want > 0.001: the bend starts where the lead ends)");
            });
            Case("HoseClothoid U-turn between fittings", () =>
            {
                var tr = new List<V2> { o, new V2(4, 0), new V2(5.5, 1.5), new V2(4, 3), new V2(0, 3) };
                Check("uturn", new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 1.6, P1 = new V2(0, 3), Theta1 = Math.PI, Lead1 = 0.6,
                    L = Geo.Length(tr) * 1.03, Track = tr, Kmax = Kmax }, 1.6, 0.6);
            });
            Case("HoseClothoid tail re-laid onto a port keeps the head and meets the port straight", () =>
            {
                // a hose running east that must couple into a port 2 cells north of its line, entering northwards. The port sits
                // where a 9-cell hose can reach it: at (8, 1.5) the end straight leaves 0.9 < R to turn in, so the shortest
                // path within R dips south first and runs 6.74 + 1.98 + 0.6 = 9.32 cells (infeasible); at (7, 2) it is about
                // 8.3, and the fit has 0.7 of slack to drape
                var pts = Line(o, new V2(9, 0), 36);
                List<V2> t = HoseClothoid.TailOnto(pts, new V2(7, 2), new V2(0, 1), 0.6, Kmax, 1.6, out int kept);
                if (t == null) throw new Exception("no window fits:" + HoseClothoid.TailWhy);
                for (int i = 0; i < kept; i++) if (V2.Dist(t[i], pts[i]) > 1e-9) throw new Exception("kept sample " + i + " moved");
                double len = Geo.Length(t);
                if (Math.Abs(len - 9) > 0.01) throw new Exception($"length {len:0.000} vs 9 (kept {kept})");
                var rep = HoseCurveMetrics.Measure(t, HoseCurveMetrics.EndSpec.Fitting(o, new V2(1, 0), 1.6, "start"),
                    HoseCurveMetrics.EndSpec.Fitting(new V2(7, 2), new V2(0, -1), 0.6, "port"), Kmax, 9);
                if (!rep.Ok) throw new Exception("kept " + kept + " ruler: " + rep.Line());
            });
            Case("HoseClothoid mate: two slack hoses meeting at a right angle couple keeping their lengths and start leads", () =>
            {
                // step 2 (design section 6): A runs east from its nozzle, B north from its own; both are laid to the same coupling point
                List<V2> Drape(V2 a, V2 d, double len, double amp, int n)
                {
                    var p = new List<V2>();
                    V2 nrm = new V2(-d.Z, d.X);
                    for (int i = 0; i <= n; i++)
                    {
                        double t = i / (double)n, s = t * len, w = s <= 1.6 ? 0 : Math.Sin(Math.PI * (s - 1.6) / (len - 1.6)), lift = amp * w * w * w; // G2 at the lead's end
                        p.Add(a + d * s + nrm * lift);
                    }
                    return p;
                }
                List<V2> A = Drape(o, new V2(1, 0), 9, 0.5, 45), B = Drape(new V2(9, -9), new V2(0, 1), 9, -0.6, 45);
                bool was = HoseMath.G2On;
                HoseMath.G2On = true;
                try
                {
                    const double vis = 0.25;
                    HoseSpliceMath.Mate m = HoseSpliceMath.MatePair(A, B, A[A.Count - 1], Kmax, vis, out List<V2> Am, out List<V2> Bm, 1.6, 1.6);
                    if (m == null) throw new Exception("no mate:" + HoseClothoid.TailWhy);
                    double straight = HoseSpliceMath.CouplingStraight(vis);
                    foreach (var (raw, got, ax, nm) in new[] { (A, Am, m.Axis, "A"), (B, Bm, -m.Axis, "B") })
                    {
                        double l0 = Geo.Length(raw), l1 = Geo.Length(got);
                        if (Math.Abs(l1 - l0) > 0.01 * l0) throw new Exception($"{nm} length {l1:0.000} vs {l0:0.000}");
                        double[] sr = Geo.CumLen(raw);
                        for (int i = 0; i < raw.Count && sr[i] <= 1.6; i++)
                            if (i >= got.Count || V2.Dist(raw[i], got[i]) > 1e-9) throw new Exception($"{nm} lead sample {i} moved or lost ({got.Count} samples)");
                        V2 d0 = (raw[1] - raw[0]).Norm();
                        var rep = HoseCurveMetrics.Measure(got, HoseCurveMetrics.EndSpec.Fitting(raw[0], d0, 1.6, "nozzle"),
                            HoseCurveMetrics.EndSpec.Fitting(m.C, -ax, straight, "mate"), Kmax, l0);
                        if (!rep.Ok) throw new Exception(nm + " ruler: " + rep.Line());
                    }
                }
                finally { HoseMath.G2On = was; }
            });
        }
        /// <summary>HOSESNAP_FIX_HEADING_AND_RAMP_SCALE: Snap (the stretch-and-turn that closes a near-taut gap) on hand-made
        /// results. (1) Solve promises Feasible = every end equality within EndTol, but Snap accepted an end heading off by up to
        /// SnapTurn (50x EndTol) and turned a fixed start heading with it. (2) Stretching by sc spaces nodes h*sc, so the ramp
        /// bound becomes dk*sc; Snap compared against dk/sc, the unstretched bound. Can-fail: the pre-fix Snap returns true on the
        /// turned straight and on the ramp profile at the unstretched bound.</summary>
        internal static void RunSnap(Action<string, Action> Case)
        {
            Case("HoseClothoid snap: Feasible only with both end headings within EndTol, ramp bound stretched as dk*sc", () =>
            {
                const double h0 = 0.5, kmax = 1, L = 5;
                int n = (int)(L / h0);
                double[] H = new double[n], Dk = new double[n];
                for (int i = 0; i < n; i++) { H[i] = h0; Dk[i] = 0.1; }
                List<V2> Ray(double ang, double len) => Line(new V2(0, 0), Dir(ang) * len, 2 * n);
                HoseClothoid.Result R(List<V2> pts, double[] k) => new HoseClothoid.Result { Pts = pts, Kappa = k, Theta0 = 0, Step = h0 };
                var probs = new List<string>();

                // (1) a straight drawn 0.005 rad off its chord and 0.2% short: the turn that lands its end turns both headings by
                // 0.005 rad, 25x EndTol
                double[] K0 = new double[n + 1];
                var fit = new HoseClothoid.Problem { P0 = new V2(0, 0), Theta0 = 0, P1 = new V2(L, 0), Theta1 = 0, L = L, Kmax = kmax };
                var r1 = R(Ray(0.005, L * 0.998), K0);
                if (HoseClothoid.Snap(r1, fit, K0, H, kmax, Dk, 0) && r1.EndErr < HoseClothoid.EndTol)
                    probs.Add($"fitted ends: Snap turned 0.005 rad and reported met (head {r1.HeadErr:0.00000}, start {Math.Abs(r1.Theta0):0.00000}, EndTol {HoseClothoid.EndTol})");
                // the same turn with only the end fitted: the end heading still misses by the turn
                var endOnly = new HoseClothoid.Problem { P0 = new V2(0, 0), P1 = new V2(L, 0), Theta1 = 0, L = L, Kmax = kmax };
                var r1b = R(Ray(0.005, L * 0.998), K0);
                if (HoseClothoid.Snap(r1b, endOnly, K0, H, kmax, Dk, 0))
                    probs.Add($"end fitted: Snap reported met with the end heading off by {r1b.HeadErr:0.00000}");
                // control: free headings, the same turn is a legal snap
                var free = new HoseClothoid.Problem { P0 = new V2(0, 0), P1 = new V2(L, 0), L = L, Kmax = kmax };
                var r1c = R(Ray(0.005, L * 0.998), K0);
                if (!HoseClothoid.Snap(r1c, free, K0, H, kmax, Dk, 0)) probs.Add("free ends: Snap refused a 0.005 rad turn + 0.2% stretch");
                // control: fitted ends, a pure stretch (no turn) is a legal snap
                var r1d = R(Ray(0, L * 0.998), K0);
                if (!HoseClothoid.Snap(r1d, fit, K0, H, kmax, Dk, 0)) probs.Add($"fitted ends: Snap refused a pure 0.2% stretch (head {r1d.HeadErr:0.00000})");

                // (2) sc < 1 (drawn 0.8% long): a ramp exactly at the unstretched bound dk must be refused, since the stretched
                // profile's ramp dK/sc exceeds dk*sc; a ramp at 0.98 dk*sc^2 must pass
                double sc = 1 / 1.008;
                double[] Zig(double step) { var k = new double[n + 1]; for (int i = 0; i <= n; i++) k[i] = i % 2 == 0 ? 0 : step; return k; }
                double[] Kat = Zig(Dk[0]), Kin = Zig(0.98 * Dk[0] * sc * sc);
                var r2 = R(Ray(0, L * 1.008), Kat);
                if (HoseClothoid.Snap(r2, free, Kat, H, kmax, Dk, 0))
                    probs.Add($"ramp: Snap accepted ramp {Dk[0] / sc:0.000000} on the stretched curve, bound dk*sc {Dk[0] * sc:0.000000}");
                var r2b = R(Ray(0, L * 1.008), Kin);
                if (!HoseClothoid.Snap(r2b, free, Kin, H, kmax, Dk, 0)) probs.Add("ramp: Snap refused a ramp inside the stretched bound");
                if (probs.Count > 0) throw new Exception(string.Join("; ", probs));
            });
        }
    }
}
