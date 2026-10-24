using System;
using System.Collections.Generic;
using System.Text;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS (owner 2026-10-23 22:15: "There should be constraints on the absolute (location), first
    /// derivative (slope/angle), and second derivative (curvature) of the hoses ... Each pipe segment must join with the others
    /// absolutely by location and slope and curvature"). The RULER of a drawn hose centreline, Verse-free, shared by the offline
    /// selftest (HoseCurveChecks) and the live probe (HoseCurveProbe, verb "curves"), so the two read one instrument. It never
    /// calls the code it measures. Thresholds: design/RimMandrake/flowworks_hose_geometry_g2_2026-10-23.md section 1.
    ///
    /// Discrete curvature at an interior sample = signed turning angle / mean of the two adjacent segment lengths, so a cusp (a
    /// 150-degree turn in one sample) reads as a huge curvature instead of hiding in a resample. The ends are INCLUDED: the old
    /// MinBendRadius skipped half a cell at each end, which is exactly where the owner's screenshots show the kinks.
    /// </summary>
    internal static class HoseCurveMetrics
    {
        /// <summary>R1: an end lies within this distance (cells) of the point it couples to.</summary>
        public const double MaxEndGap = 0.02;
        /// <summary>R2: inside a straight lead the drawn heading stays within this many degrees of the fitting's axis.</summary>
        public const double MaxLeadAngleDeg = 2.0;
        /// <summary>R3: inside a straight lead the curvature stays below this (1/cells; 0.05 = a 20-cell radius, visibly straight).</summary>
        public const double MaxLeadKappa = 0.05;
        /// <summary>R4: |kappa| may exceed kmax by this factor (discretisation slack of a 0.25-cell sampling).</summary>
        public const double KappaSlack = 1.05;
        /// <summary>R3/G2: the steepest allowed curvature change per cell of arc, as a multiple of kmax: kappa may ramp from 0 to
        /// kmax over no less than 0.4 cell (a G1 line-to-arc joint changes it in one sample, 0.25 cell, and fails).</summary>
        public const double JerkPerKmax = 2.5;
        /// <summary>R6: the drawn length differs from the reference (laid) length by at most this fraction.</summary>
        public const double MaxLengthErr = 0.02;
        /// <summary>Samples closer than this are one sample (a duplicated knot is not a cusp).</summary>
        public const double MinSeg = 1e-4;

        /// <summary>What an end of the hose must do: lie on <see cref="At"/> and, for the first <see cref="Straight"/> cells of
        /// arc from that end, run along <see cref="Axis"/> (unit, pointing INTO the hose, away from the fitting).</summary>
        public struct EndSpec
        {
            public V2 At;
            public V2? Axis;
            public double Straight;
            public string Name;
            public static EndSpec Free(V2 at, string name) => new EndSpec { At = at, Axis = null, Straight = 0, Name = name };
            public static EndSpec Fitting(V2 at, V2 axisIntoHose, double straight, string name) =>
                new EndSpec { At = at, Axis = axisIntoHose.Norm(), Straight = straight, Name = name };
        }

        public sealed class Report
        {
            public double StartGap, EndGap, StartAngleDeg, EndAngleDeg, StartLeadKappa, EndLeadKappa;
            public double KappaMax, KappaMaxAt, JerkMax, JerkMaxAt, Length, LengthErr, Kmax;
            public int Samples;
            public readonly List<string> Fails = new List<string>();
            public bool Ok => Fails.Count == 0;
            public string Line()
            {
                var sb = new StringBuilder();
                sb.Append($"gap {StartGap:0.000}/{EndGap:0.000} lead {StartAngleDeg:0.0}/{EndAngleDeg:0.0}deg leadK {StartLeadKappa:0.00}/{EndLeadKappa:0.00}");
                sb.Append($" kmax {KappaMax:0.00}@{KappaMaxAt:0.0} (cap {Kmax * KappaSlack:0.00}) dk/ds {JerkMax:0.0}@{JerkMaxAt:0.0} (cap {Kmax * JerkPerKmax:0.0})");
                sb.Append($" len {Length:0.00} err {LengthErr * 100:0.0}%");
                if (Fails.Count > 0) sb.Append(" FAIL[" + string.Join(",", Fails) + "]");
                return sb.ToString();
            }
        }

        /// <summary>The samples with near-duplicates merged (the ends kept exactly).</summary>
        public static List<V2> Clean(IList<V2> pts)
        {
            var o = new List<V2>(pts.Count);
            for (int i = 0; i < pts.Count; i++)
            {
                if (o.Count > 0 && V2.Dist(o[o.Count - 1], pts[i]) < MinSeg)
                {
                    if (i == pts.Count - 1) o[o.Count - 1] = pts[i];
                    continue;
                }
                o.Add(pts[i]);
            }
            return o;
        }

        /// <summary>Signed discrete curvature at every sample (0 at the two ends) and the arc length at every sample.</summary>
        public static double[] Kappa(IList<V2> p, out double[] s)
        {
            int n = p.Count;
            s = new double[n];
            for (int i = 1; i < n; i++) s[i] = s[i - 1] + V2.Dist(p[i - 1], p[i]);
            var k = new double[n];
            for (int i = 1; i < n - 1; i++)
            {
                V2 a = p[i] - p[i - 1], b = p[i + 1] - p[i];
                double th = Math.Atan2(a.X * b.Z - a.Z * b.X, a.X * b.X + a.Z * b.Z);
                double seg = 0.5 * (a.Len + b.Len);
                k[i] = seg > MinSeg ? th / seg : 0;
            }
            return k;
        }

        /// <summary>Largest heading deviation (degrees) from <paramref name="axis"/> and largest |kappa| over the first
        /// <paramref name="straight"/> cells of arc of p (p runs away from the fitting).</summary>
        public static void Lead(IList<V2> p, V2 axis, double straight, out double angleDeg, out double leadKappa)
        {
            double[] k = Kappa(p, out double[] s);
            angleDeg = 0;
            leadKappa = 0;
            double reach = Math.Max(straight, 1e-6);
            for (int i = 1; i < p.Count; i++)
            {
                if (s[i - 1] >= reach) break;
                V2 d = p[i] - p[i - 1];
                if (d.Len < MinSeg) continue;
                V2 u = d.Norm();
                double c = Geo.Clamp(u.X * axis.X + u.Z * axis.Z, -1, 1);
                angleDeg = Math.Max(angleDeg, Math.Acos(c) * 180 / Math.PI);
                if (i < p.Count - 1 && s[i] < reach) leadKappa = Math.Max(leadKappa, Math.Abs(k[i]));
            }
        }

        /// <summary>Measure a drawn centreline against R1..R4 and R6 (R5 is <see cref="Shared"/>). refLen &lt;= 0 skips R6.</summary>
        public static Report Measure(IList<V2> raw, EndSpec start, EndSpec end, double kmax, double refLen)
        {
            var r = new Report { Kmax = kmax };
            List<V2> p = Clean(raw);
            r.Samples = p.Count;
            if (p.Count < 3) { r.Fails.Add("too-few-samples"); return r; }
            r.StartGap = V2.Dist(p[0], start.At);
            r.EndGap = V2.Dist(p[p.Count - 1], end.At);
            if (r.StartGap > MaxEndGap) r.Fails.Add("R1-start-gap");
            if (r.EndGap > MaxEndGap) r.Fails.Add("R1-end-gap");
            if (start.Axis.HasValue)
            {
                Lead(p, start.Axis.Value, start.Straight, out r.StartAngleDeg, out r.StartLeadKappa);
                if (r.StartAngleDeg > MaxLeadAngleDeg) r.Fails.Add("R2-start-angle");
                if (r.StartLeadKappa > MaxLeadKappa) r.Fails.Add("R3-start-lead-kappa");
            }
            if (end.Axis.HasValue)
            {
                var rev = new List<V2>(p);
                rev.Reverse();
                Lead(rev, end.Axis.Value, end.Straight, out r.EndAngleDeg, out r.EndLeadKappa);
                if (r.EndAngleDeg > MaxLeadAngleDeg) r.Fails.Add("R2-end-angle");
                if (r.EndLeadKappa > MaxLeadKappa) r.Fails.Add("R3-end-lead-kappa");
            }
            double[] k = Kappa(p, out double[] s);
            r.Length = s[s.Length - 1];
            for (int i = 1; i < p.Count - 1; i++)
                if (Math.Abs(k[i]) > r.KappaMax) { r.KappaMax = Math.Abs(k[i]); r.KappaMaxAt = s[i]; }
            // curvature change per arc between consecutive interior samples (the end samples carry no curvature)
            for (int i = 1; i < p.Count - 2; i++)
            {
                double ds = s[i + 1] - s[i];
                if (ds < MinSeg) continue;
                double j = Math.Abs(k[i + 1] - k[i]) / Math.Max(ds, 0.1);
                if (j > r.JerkMax) { r.JerkMax = j; r.JerkMaxAt = s[i]; }
            }
            if (r.KappaMax > kmax * KappaSlack) r.Fails.Add("R4-kappa");
            if (r.JerkMax > kmax * JerkPerKmax) r.Fails.Add("R3-dk/ds");
            if (refLen > 0)
            {
                r.LengthErr = Math.Abs(r.Length - refLen) / refLen;
                if (r.LengthErr > MaxLengthErr) r.Fails.Add("R6-length");
            }
            return r;
        }

        /// <summary>A splice: hose A's end and hose B's end couple at one point. Measured as ONE curve, A then B reversed, so the
        /// coupling is an interior point and position, slope and curvature continuity across it are R1..R4 of the joined curve.</summary>
        public static Report Splice(IList<V2> a, IList<V2> b, EndSpec aStart, EndSpec bStart, double kmax, out double seamGap)
        {
            List<V2> A = Clean(a), B = Clean(b);
            seamGap = A.Count > 0 && B.Count > 0 ? V2.Dist(A[A.Count - 1], B[B.Count - 1]) : 99;
            var joined = new List<V2>(A);
            for (int i = B.Count - 1; i >= 0; i--) joined.Add(B[i]);
            Report r = Measure(joined, aStart, bStart, kmax, 0);
            if (seamGap > MaxEndGap) r.Fails.Add("R1-seam-gap");
            return r;
        }

        /// <summary>R5: two hoses on one fitting. Each must leave along its OWN axis: over the first <paramref name="straight"/>
        /// cells, each drawn heading's deviation from its own axis (stricter than comparing the angle between the two headings
        /// with the angle between the axes, which two hoses bent alike would pass); returns the worse deviation in degrees,
        /// judged against MaxLeadAngleDeg by the caller.</summary>
        public static double Shared(IList<V2> fromFittingA, V2 axisA, IList<V2> fromFittingB, V2 axisB, double straight)
        {
            Lead(Clean(fromFittingA), axisA, straight, out double a, out _);
            Lead(Clean(fromFittingB), axisB, straight, out double b, out _);
            return Math.Max(a, b);
        }
    }
}
