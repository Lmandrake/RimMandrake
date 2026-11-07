// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// What a player sees as a cord that is not a loose too-long cord, measured on the laid polyline as drawn: a sharp corner anywhere on it, plugs included (a machine's own run under its
// art is left out), and a straight rod. Shared by the shape lab, the SelfTest and the live probe "shapeaudit".
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class CordShapeAudit
    {
        /// <summary>Over this arc either side, a turn past SharpDeg is a corner the eye reads as a corner: a cord 0.08 wide cannot bend that tight.</summary>
        public const double SharpArc = 0.1, SharpDeg = 70;
        /// <summary>A straight rod: this many cells or more holding within RodDeg of one line.</summary>
        public const double RodLen = 2.2, RodDeg = 7;

        private static double Turn(V2 u, V2 v)
        {
            if (u.Len < 1e-6 || v.Len < 1e-6) return 0;
            return Math.Acos(Math.Max(-1, Math.Min(1, (u.X * v.X + u.Z * v.Z) / (u.Len * v.Len)))) * 180 / Math.PI;
        }

        /// <summary>Sharp corners of a strand, one per corner, positions on the map. <paramref name="skipEnd"/>: the arc at each end to leave out (under a plug).</summary>
        internal static List<V2> Corners(List<V2> pts, double skipEnd = 0.05)
        {
            var o = new List<V2>();
            if (pts == null || pts.Count < 3) return o;
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1], last = double.MinValue;
            int a = 0, b = 0;
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i] < skipEnd || cum[i] > L - skipEnd || cum[i] - last < 0.25) continue;
                while (a < i && cum[i] - cum[a + 1] >= SharpArc) a++;
                while (b < pts.Count - 1 && cum[b] - cum[i] < SharpArc) b++;
                if (cum[i] - cum[a] < SharpArc * 0.5 || cum[b] - cum[i] < SharpArc * 0.5) continue;
                if (Turn(pts[i] - pts[a], pts[b] - pts[i]) < SharpDeg) continue;
                o.Add(pts[i]);
                last = cum[i];
            }
            return o;
        }

        /// <summary>The longest stretch of the strand holding one line, cells. Runs under art are not excluded here: the caller trims a machine's run off first.</summary>
        internal static double LongestRod(List<V2> pts, out V2 at)
        {
            at = pts != null && pts.Count > 0 ? pts[0] : new V2(0, 0);
            if (pts == null || pts.Count < 2) return 0;
            List<V2> q = Geo.Resample(pts, 0.1);
            double best = 0;
            for (int i = 0; i < q.Count - 1; i++)
            {
                V2 dir = default(V2);
                int j = i + 1;
                for (; j < q.Count; j++)
                {
                    V2 d = q[j] - q[i];
                    if (d.Len < 0.6) continue;
                    if (dir.Len < 1e-6) dir = d;
                    if (Turn(dir, d) > RodDeg) break;
                }
                double len = 0.1 * (j - 1 - i);
                if (len > best) { best = len; at = q[i]; }
                if (j >= q.Count) break;
            }
            return best;
        }

        public sealed class Tally
        {
            public int Strands, SharpStrands, Corners, Rods;
            private readonly List<string> rows = new List<string>();
            private static string F(double d) => d.ToString("0.00", CultureInfo.InvariantCulture);

            internal void Add(LaidPiece p, CordStrand s)
            {
                if (s.Pts == null || s.Pts.Count < 3) return;
                Strands++;
                List<V2> c = CordShapeAudit.Corners(s.Pts);
                if (c.Count > 0) SharpStrands++;
                Corners += c.Count;
                string name = p.EndA == null ? p.Key : p.EndA + "|" + p.EndB;
                foreach (V2 k in c)
                    if (rows.Count < 60) rows.Add("{\"sharp\":[" + F(k.X) + "," + F(k.Z) + "],\"piece\":\"" + name + "\"}");
                double rod = LongestRod(s.Pts, out V2 at);
                if (rod >= RodLen)
                {
                    Rods++;
                    if (rows.Count < 60) rows.Add("{\"rod\":" + F(rod) + ",\"at\":[" + F(at.X) + "," + F(at.Z) + "],\"piece\":\"" + name + "\"}");
                }
            }

            public string Json() => "{\"strands\":" + Strands + ",\"sharpStrands\":" + SharpStrands + ",\"corners\":" + Corners + ",\"rods\":" + Rods + ",\"rows\":[" + string.Join(",", rows) + "]}";
        }
    }
}
