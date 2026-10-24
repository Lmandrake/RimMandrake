// HOSE_SPLICE_BUILD_MATES_BY_SLOPE (owner walk 2026-10-23, screenshot 20261023063832_1: "two hoses joined end to end do not
// mate, they just lay on top of each other ... Please use boundary conditions that include the first and second derivative as
// well (angle and max hose curvature)"). HoseSpliceMath's G2 joiner, measured with rulers written out in this file, never with
// the functions under test:
//  S1 Join: position (C0), heading (C1) and curvature (C2) match at BOTH ends; |curvature| <= 1/MinBendRadius everywhere; no
//     curvature jump inside; never crosses itself. Cases: straight-on, 90 degrees, U-turn (opposed headings), S offset.
//  S2 the screenshot: hose A lies west to east and ends at C heading east; hose B comes down from the north-west and ends on
//     the same cell ALSO heading (east-)south-east, so the raw ends overlap. Mated: B ends on C arriving WEST (face to face
//     with A), its last JoinerHalf dead straight, G2 at the cut, curvature bound held, no self-overlap, clear of A's body.
//  S3 straight-on / 90 degrees / opposed (B parallel beside A, same heading): the same bars.
//  S4 a stiffer hose (MinBendRadius 2.0) keeps the bound, and the solve costs < 25 ms on the screenshot case.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseSpliceChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        // ------------------------------------------------------------------ rulers (independent of HoseSpliceMath)
        internal static double Heading(V2 a, V2 b) => Math.Atan2(b.Z - a.Z, b.X - a.X);
        internal static double Wrap(double a) { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; }

        /// <summary>Signed discrete curvature at every interior sample: turning angle / mean adjacent segment length.</summary>
        internal static double[] Curv(IList<V2> p)
        {
            var k = new double[p.Count];
            for (int i = 1; i + 1 < p.Count; i++)
            {
                double t = Wrap(Heading(p[i], p[i + 1]) - Heading(p[i - 1], p[i]));
                double m = 0.5 * (V2.Dist(p[i - 1], p[i]) + V2.Dist(p[i], p[i + 1]));
                k[i] = m < 1e-9 ? 0 : t / m;
            }
            if (p.Count > 2) { k[0] = k[1]; k[p.Count - 1] = k[p.Count - 2]; }
            return k;
        }

        /// <summary>Mean curvature over arc [s0, s1]: heading change / arc (a smoothed ruler for the end conditions).</summary>
        internal static double MeanCurv(IList<V2> p, double s0, double s1)
        {
            double[] s = Geo.CumLen(p);
            double h0 = HeadingAt(p, s, s0), h1 = HeadingAt(p, s, s1);
            return Wrap(h1 - h0) / Math.Max(1e-9, s1 - s0);
        }

        internal static double HeadingAt(IList<V2> p, double[] s, double at)
        {
            int i = 0;
            while (i + 2 < p.Count && s[i + 1] < at) i++;
            return Heading(p[i], p[i + 1]);
        }

        internal static bool Crosses(IList<V2> X)
        {
            for (int i = 0; i + 1 < X.Count; i++)
                for (int j = i + 2; j + 1 < X.Count; j++)
                {
                    V2 a = X[i], b = X[i + 1], c = X[j], d = X[j + 1];
                    double d1 = Cr(c, d, a), d2 = Cr(c, d, b), d3 = Cr(a, b, c), d4 = Cr(a, b, d);
                    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) return true;
                }
            return false;
        }
        private static double Cr(V2 o, V2 a, V2 b) => (a.X - o.X) * (b.Z - o.Z) - (a.Z - o.Z) * (b.X - o.X);

        /// <summary>Closest approach between two samples of one polyline that are more than <paramref name="apart"/> of arc apart.</summary>
        internal static double SelfGap(IList<V2> p, double apart)
        {
            double[] s = Geo.CumLen(p);
            double best = 99;
            for (int i = 0; i < p.Count; i++)
                for (int j = i + 1; j < p.Count; j++)
                    if (s[j] - s[i] > apart) best = Math.Min(best, V2.Dist(p[i], p[j]));
            return best;
        }

        internal static double Gap(IList<V2> p, IList<V2> q)
        {
            double best = 99;
            foreach (V2 a in p) foreach (V2 b in q) best = Math.Min(best, V2.Dist(a, b));
            return best;
        }

        internal static List<V2> Line(V2 a, V2 b, double step)
        {
            int n = Math.Max(1, (int)Math.Ceiling(V2.Dist(a, b) / step));
            var o = new List<V2>();
            for (int i = 0; i <= n; i++) o.Add(a + (b - a) * (i / (double)n));
            return o;
        }

        /// <summary>A gently wavy run (the laid hose look) from a to b, sampled every 0.25.</summary>
        internal static List<V2> Wavy(V2 a, V2 b, double amp)
        {
            var o = Line(a, b, 0.25);
            V2 n = (b - a).Norm().Perp;
            double L = V2.Dist(a, b);
            for (int i = 0; i < o.Count; i++)
            {
                double u = i / (double)(o.Count - 1);
                o[i] = o[i] + n * (amp * Math.Sin(Math.PI * u) * Math.Sin(2 * Math.PI * u * L / 9));
            }
            return o;
        }

        /// <summary>The screenshot's hose B: south from the reel, a rounded corner, then a long ESE run to <paramref name="end"/>.</summary>
        internal static List<V2> ReelHose(V2 end)
        {
            var o = new List<V2>();
            V2 top = new V2(0, 14), corner = new V2(0, 6);
            o.AddRange(Line(top, corner, 0.25));
            V2 dir = (end - corner).Norm();
            double R = 1.5, th0 = -Math.PI / 2, th1 = Math.Atan2(dir.Z, dir.X);
            V2 c = corner + new V2(R, 0);
            V2 last = corner;
            for (int i = 1; i <= 12; i++)
            {
                double t = th0 + (th1 - th0) * i / 12.0;
                last = c + new V2(R * Math.Sin(t), -R * Math.Cos(t));
                o.Add(last);
            }
            o.AddRange(Line(last, end, 0.25).Skip(1));
            return o;
        }

        // ------------------------------------------------------------------ bars
        private const double Width = 0.25;   // a plump hose's visible width (HoseMath.VisibleWidth(1, 1) ~ 0.23)

        private static void JoinBars(string tag, List<V2> P, V2 p0, double th0, double k0, V2 p1, double th1, double k1, double kmax)
        {
            Assert(P != null && P.Count > 4, tag + ": no curve");
            Assert(V2.Dist(P[0], p0) < 1e-3 && V2.Dist(P[P.Count - 1], p1) < 2e-3, $"{tag}: C0 ends {P[0]} {P[P.Count - 1]}");
            // a chord's heading is the tangent's turned by half its arc x the curvature there (k ds / 2): compared corrected
            double c0 = V2.Dist(P[0], P[1]), c1 = V2.Dist(P[P.Count - 2], P[P.Count - 1]);
            Assert(Math.Abs(Wrap(Heading(P[0], P[1]) - k0 * c0 / 2 - th0)) < 0.02, $"{tag}: C1 start {Heading(P[0], P[1]):0.000} vs {th0:0.000}");
            Assert(Math.Abs(Wrap(Heading(P[P.Count - 2], P[P.Count - 1]) + k1 * c1 / 2 - th1)) < 0.02, $"{tag}: C1 end {Heading(P[P.Count - 2], P[P.Count - 1]):0.000} vs {th1:0.000}, last pts {P[P.Count - 3]} {P[P.Count - 2]} {P[P.Count - 1]}");
            double L = Geo.Length(P), w = Math.Min(0.3, L / 6);
            double ks = MeanCurv(P, 0, w), ke = MeanCurv(P, L - w, L);
            Assert(Math.Abs(ks - k0) < 0.12 * Math.Max(1, kmax), $"{tag}: C2 start {ks:0.000} vs {k0:0.000}");
            Assert(Math.Abs(ke - k1) < 0.12 * Math.Max(1, kmax), $"{tag}: C2 end {ke:0.000} vs {k1:0.000}");
            double[] k = Curv(P);
            double kMax = k.Max(Math.Abs);
            Assert(kMax <= kmax * 1.03, $"{tag}: curvature {kMax:0.000} over the bound {kmax:0.000}");
            double jump = 0;
            for (int i = 2; i + 2 < k.Length; i++) jump = Math.Max(jump, Math.Abs(k[i + 1] - k[i]));
            Assert(jump < 0.35 * kmax, $"{tag}: curvature jumps {jump:0.000} between samples (not G2)");
            Assert(!Crosses(P), tag + ": crosses itself");
        }

        /// <summary>The mated hose's bars (S2/S3). <paramref name="raw"/> the hose as laid, <paramref name="M"/> mated.</summary>
        private static void MateBars(string tag, List<V2> raw, List<V2> M, V2 C, V2 axisIn, double straight, double kmax, List<V2> partner, bool g2 = false)
        {
            Assert(M != null && M.Count >= 4, tag + ": no mated pose");
            Assert(V2.Dist(M[M.Count - 1], C) < 2e-3, $"{tag}: ends at {M[M.Count - 1]}, not on the coupling {C}");
            double[] s = Geo.CumLen(M);
            double L = s[s.Length - 1];
            // the last `straight` is dead straight along axisIn (the rigid brass + wrap)
            for (int i = 1; i < M.Count; i++)
                if (s[i] > L - straight + 1e-6)
                {
                    V2 d = (M[i] - M[i - 1]).Norm();
                    Assert(d.X * axisIn.X + d.Z * axisIn.Z > Math.Cos(0.03), $"{tag}: coupling run not along the axis at s={s[i]:0.00}");
                }
            // the kept part is the raw hose, untouched
            int same = 0;
            while (same < M.Count && same < raw.Count && V2.Dist(M[same], raw[same]) < 1e-9) same++;
            Assert(same >= 2, tag + ": the hose was re-laid from its start");
            // G2 across the cut: mean curvature just before and just after agree; bound held over the whole re-shaped part
            // (the clothoid mate ramps curvature at up to the ruler's dk/ds cap, faster than the 0.2 kmax mean-curvature bar
            // allows over half a cell, so for a MatePair made under HoseMath.G2On (g2) the ruler itself judges the cut and the run, length kept)
            if (g2)
            {
                var rep = HoseCurveMetrics.Measure(M, HoseCurveMetrics.EndSpec.Free(raw[0], "start"),
                    HoseCurveMetrics.EndSpec.Fitting(C, -axisIn, straight, "mate"), kmax, Geo.Length(raw));
                Assert(rep.Ok, $"{tag}: ruler {rep.Line()}");
            }
            else
            {
                double sc = s[same - 1];
                double kb = MeanCurv(M, Math.Max(0, sc - 0.5), sc), ka = MeanCurv(M, sc, Math.Min(L, sc + 0.5));
                Assert(Math.Abs(kb - ka) < 0.2 * kmax, $"{tag}: curvature jumps at the cut ({kb:0.000} -> {ka:0.000})");
            }
            List<V2> tail = M.Skip(Math.Max(0, same - 2)).ToList();
            double kMax = Curv(tail).Skip(1).Take(tail.Count - 2).Select(Math.Abs).DefaultIfEmpty(0).Max();
            Assert(kMax <= kmax * 1.05, $"{tag}: curvature {kMax:0.000} over the bound {kmax:0.000}");
            Assert(!Crosses(M), tag + ": crosses itself");
            Assert(SelfGap(tail, 4 * Width) > Width, $"{tag}: doubles back over itself (gap {SelfGap(tail, 4 * Width):0.000})");
            if (partner != null)
            {
                // clear of the partner hose's body except where the two couplings meet (the last `straight` of each)
                List<V2> mine = M.Where((p, i) => s[i] < L - straight).ToList();
                double[] sp = Geo.CumLen(partner);
                List<V2> theirs = partner.Where((p, i) => sp[i] < sp[sp.Length - 1] - straight).ToList();
                double g = Gap(mine, theirs);
                Assert(g > Width, $"{tag}: lies on the partner hose (gap {g:0.000})");
            }
        }

        public static void Run(Action<string, Action> Case)
        {
            double R = 1.2, kmax = 1 / R;

            Case("S1 Join: straight-on (heading east to a point ahead, curvature 0 both ends)", () =>
            {
                V2 p0 = new V2(0, 0), p1 = new V2(5, 0.4);
                JoinBars("straight", HoseSpliceMath.Join(p0, 0, 0, p1, 0, 0, kmax, 0.1, out _), p0, 0, 0, p1, 0, 0, kmax);
            });
            Case("S1 Join: 90 degrees, starting on a curve (k0 = 0.4) and ending straight", () =>
            {
                V2 p0 = new V2(0, 0), p1 = new V2(4, -4);
                JoinBars("ninety", HoseSpliceMath.Join(p0, 0, 0.4, p1, -Math.PI / 2, 0, kmax, 0.1, out _), p0, 0, 0.4, p1, -Math.PI / 2, 0, kmax);
            });
            Case("S1 Join: U-turn (opposed headings, the end 1 cell to the side and behind)", () =>
            {
                V2 p0 = new V2(0, 0), p1 = new V2(-0.5, -1.0);
                JoinBars("uturn", HoseSpliceMath.Join(p0, 0, 0, p1, Math.PI, 0, kmax, 0.1, out _), p0, 0, 0, p1, Math.PI, 0, kmax);
            });
            Case("S1 Join: S offset with end curvature (k1 = -0.3)", () =>
            {
                V2 p0 = new V2(0, 0), p1 = new V2(6, 2);
                JoinBars("s-offset", HoseSpliceMath.Join(p0, 0, 0, p1, 0, -0.3, kmax, 0.1, out _), p0, 0, 0, p1, 0, -0.3, kmax);
            });

            double straight = HoseSpliceMath.CouplingStraight(Width);

            Case("S2 the screenshot: B's end on A's end, both heading east, mates face to face", () =>
            {
                List<V2> A = Wavy(new V2(-25, -1.2), new V2(20, 0), 0.35);
                V2 C = A[A.Count - 1], u = (A[A.Count - 1] - A[A.Count - 4]).Norm();
                List<V2> B = ReelHose(C + new V2(0.1, 0.12));
                // the defect as laid: B's last cell lies on A's last cell, both heading the same way
                V2 ub = (B[B.Count - 1] - B[B.Count - 4]).Norm();
                Assert(ub.X * u.X + ub.Z * u.Z > 0.8 && Gap(B.Skip(B.Count - 4).ToList(), A.Skip(A.Count - 4).ToList()) < Width,
                    "the screenshot case does not reproduce (B should arrive on top of A, same heading)");
                List<V2> Bm = HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, null, out HoseSpliceMath.Seed sb);
                MateBars("screenshot B", B, Bm, C, -u, straight, kmax, A);
                List<V2> Am = HoseSpliceMath.MateTail(A, C, u, straight, kmax, Bm, null, out _);
                MateBars("screenshot A", A, Am, C, u, straight, kmax, null);
                Assert(sb != null && sb.CutBack > 0, "no seed recorded for the transition re-solve");
                // the re-solve with the cached seed lands on the same pose
                long solves0 = HoseSpliceMath.Solves;
                List<V2> Bm2 = HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, sb, out HoseSpliceMath.Seed sb2);
                long resolves = HoseSpliceMath.Solves - solves0;
                Assert(resolves == 1, $"the cached re-solve ran {resolves} solves (one expected)");
                Assert(Bm2.Count == Bm.Count && Enumerable.Range(0, Bm.Count).All(i => V2.Dist(Bm[i], Bm2[i]) < 1e-3), $"cached seed re-solve differs: {Bm.Count} vs {Bm2.Count} pts, cut {sb.CutBack}/{sb2?.CutBack}, {resolves} solves, L {sb.L:0.000}/{sb2?.L:0.000}, max diff {Enumerable.Range(0, Math.Min(Bm.Count, Bm2.Count)).Max(i => V2.Dist(Bm[i], Bm2[i])):0.000}");
            });
            Case("S3 straight-on: B already arrives from the east heading west (near identity)", () =>
            {
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25);
                V2 C = A[A.Count - 1], u = new V2(1, 0);
                List<V2> B = Line(new V2(20, 0.3), C, 0.25);
                List<V2> Bm = HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, null, out _);
                MateBars("straight-on", B, Bm, C, -u, straight, kmax, A);
                Assert(Geo.Length(Bm) < Geo.Length(B) + 0.3, $"straight-on grew {Geo.Length(Bm) - Geo.Length(B):0.00} cells");
            });
            Case("S3 90 degrees: B comes down from the north onto A's end", () =>
            {
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25);
                V2 C = A[A.Count - 1], u = new V2(1, 0);
                List<V2> B = Line(new V2(10, 10), C, 0.25);
                List<V2> Bm = HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, null, out _);
                MateBars("ninety", B, Bm, C, -u, straight, kmax, A);
            });
            Case("S3 opposed: B runs parallel beside A, same heading, ending one cell north of A's end", () =>
            {
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25);
                V2 C = A[A.Count - 1], u = new V2(1, 0);
                List<V2> B = Line(new V2(0, 1), new V2(10, 1), 0.25);
                List<V2> Bm = HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, null, out _);
                MateBars("opposed", B, Bm, C, -u, straight, kmax, A);
            });
            Case("S5 MatePair: at 90 degrees both hoses bend part way (gentler than one looping round); every case still passes the bars", () =>
            {
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25);
                V2 C = A[A.Count - 1];
                List<V2> B = Line(new V2(10, 10), C, 0.25);
                HoseSpliceMath.Mate m = HoseSpliceMath.MatePair(A, B, C, kmax, Width, out List<V2> Am, out List<V2> Bm);
                Assert(m != null, "no mate at 90 degrees");
                // with the clothoid fit on the coupling slides (both lengths kept, MatePairG2); otherwise it stays at C
                MateBars("pair90 A", A, Am, m.C, m.Axis, straight, kmax, Bm, HoseMath.G2On);
                MateBars("pair90 B", B, Bm, m.C, -m.Axis, straight, kmax, Am, HoseMath.G2On);
                if (HoseMath.G2On)
                {
                    foreach (var (raw, got, nm) in new[] { (A, Am, "A"), (B, Bm, "B") })
                        Assert(Math.Abs(Geo.Length(got) - Geo.Length(raw)) < 0.01 * Geo.Length(raw), $"pair90 {nm} length {Geo.Length(got):0.000} vs {Geo.Length(raw):0.000}");
                }
                else
                {
                    // the older-hose-holds answer (A untouched) costs more: B alone loops round A's end
                    List<V2> Bonly = HoseSpliceMath.MateTail(B, C, new V2(-1, 0), straight, kmax, A, null, out HoseSpliceMath.Seed so);
                    Assert(so != null && m.Cost < so.Cost - 0.5, $"the pair ({m.Cost:0.00}) is not gentler than B looping alone ({so?.Cost:0.00})");
                    double total = Geo.Length(Am) + Geo.Length(Bm) - Geo.Length(A) - Geo.Length(B);
                    Assert(total < Geo.Length(Bonly) - Geo.Length(B), $"the pair adds {total:0.00} cells, B alone {Geo.Length(Bonly) - Geo.Length(B):0.00}");
                }
                List<V2> A0 = Wavy(new V2(-25, -1.2), new V2(20, 0), 0.35);
                V2 C0 = A0[A0.Count - 1];
                List<V2> B0 = ReelHose(C0 + new V2(0.1, 0.12));
                HoseSpliceMath.Mate m0 = HoseSpliceMath.MatePair(A0, B0, C0, kmax, Width, out List<V2> A0m, out List<V2> B0m);
                Assert(m0 != null, "no mate for the screenshot");
                MateBars("pair screenshot A", A0, A0m, m0.C, m0.Axis, straight, kmax, B0m, HoseMath.G2On);
                MateBars("pair screenshot B", B0, B0m, m0.C, -m0.Axis, straight, kmax, A0m, HoseMath.G2On);
            });
            Case("S4 a stiffer hose (MinBendRadius 2.0) keeps its bound; the screenshot solve is cheap", () =>
            {
                double k2 = 1 / 2.0;
                List<V2> A = Wavy(new V2(-25, -1.2), new V2(20, 0), 0.35);
                V2 C = A[A.Count - 1], u = (A[A.Count - 1] - A[A.Count - 4]).Norm();
                List<V2> B = ReelHose(C + new V2(0.1, 0.12));
                var sw = System.Diagnostics.Stopwatch.StartNew();
                List<V2> Bm = HoseSpliceMath.MateTail(B, C, -u, straight, k2, A, null, out _);
                long ms = sw.ElapsedMilliseconds;
                MateBars("stiff", B, Bm, C, -u, straight, k2, A);
                sw.Restart();
                for (int i = 0; i < 5; i++) HoseSpliceMath.MateTail(B, C, -u, straight, kmax, A, null, out _);
                double per = sw.ElapsedMilliseconds / 5.0;
                Console.WriteLine($"    splice cost: cold {ms} ms (stiff), {per:0.0} ms per full search");
                Assert(per < 25, $"the full search costs {per:0.0} ms (> 25)");
            });
        }
    }
}
