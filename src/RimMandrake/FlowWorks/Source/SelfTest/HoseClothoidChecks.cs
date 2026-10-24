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
            Case("HoseClothoid U-turn between fittings", () =>
            {
                var tr = new List<V2> { o, new V2(4, 0), new V2(5.5, 1.5), new V2(4, 3), new V2(0, 3) };
                Check("uturn", new HoseClothoid.Problem { P0 = o, Theta0 = 0, Lead0 = 1.6, P1 = new V2(0, 3), Theta1 = Math.PI, Lead1 = 0.6,
                    L = Geo.Length(tr) * 1.03, Track = tr, Kmax = Kmax }, 1.6, 0.6);
            });
            Case("HoseClothoid tail re-laid onto a port keeps the head and meets the port straight", () =>
            {
                // a hose running east that must couple into a port 1.5 cells north of its line, entering northwards
                var pts = Line(o, new V2(9, 0), 36);
                List<V2> t = HoseClothoid.TailOnto(pts, new V2(8, 1.5), new V2(0, 1), 0.6, Kmax, 1.6, out int kept);
                if (t == null) throw new Exception("no window fits:" + HoseClothoid.TailWhy);
                for (int i = 0; i < kept; i++) if (V2.Dist(t[i], pts[i]) > 1e-9) throw new Exception("kept sample " + i + " moved");
                double len = Geo.Length(t);
                if (Math.Abs(len - 9) > 0.01) throw new Exception($"length {len:0.000} vs 9 (kept {kept})");
                var rep = HoseCurveMetrics.Measure(t, HoseCurveMetrics.EndSpec.Fitting(o, new V2(1, 0), 1.6, "start"),
                    HoseCurveMetrics.EndSpec.Fitting(new V2(8, 1.5), new V2(0, -1), 0.6, "port"), Kmax, 9);
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
                        for (int i = 0; i < raw.Count && sr[i] <= 1.6; i++) if (V2.Dist(raw[i], got[i]) > 1e-9) throw new Exception($"{nm} lead sample {i} moved");
                        V2 d0 = (raw[1] - raw[0]).Norm();
                        var rep = HoseCurveMetrics.Measure(got, HoseCurveMetrics.EndSpec.Fitting(raw[0], d0, 1.6, "nozzle"),
                            HoseCurveMetrics.EndSpec.Fitting(m.C, -ax, straight, "mate"), Kmax, l0);
                        if (!rep.Ok) throw new Exception(nm + " ruler: " + rep.Line());
                    }
                }
                finally { HoseMath.G2On = was; }
            });
        }
    }
}
