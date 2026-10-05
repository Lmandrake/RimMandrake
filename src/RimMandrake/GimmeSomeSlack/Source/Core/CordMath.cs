// Gimme Some Slack core: Verse-free on purpose. Source/SelfTest compiles this file directly, so
// nothing here may reference Verse, RimWorld or UnityEngine. Port of the Python oracle in
// src/RimMandrake/Utils/mockups/messy_conduit/ (render.py helpers).
using System;
using System.Collections.Generic;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>
    /// Round 3 (owner 2026-10-04, "the wires should go beneath the Power Switch"): the draw-stack rule a building's art obeys
    /// against our cords. Unity draws by render queue, then (opaque/cutout) by the depth buffer: a building drawn with a
    /// depth-writing shader (Cutout, queue 2450) hides a cord printed BELOW it (Conduits altitude) whatever the cord's
    /// queue; a Transparent building (queue 3000, no depth write) is painted over by any cord material at the same or a
    /// later queue (strands 3000, plugs/junctions 3001). Verse-free so the SelfTest checks it.
    /// </summary>
    public static class DrawStack
    {
        public const int CutoutQueue = 2450, TransparentQueue = 3000;

        public static bool CordsPaintOver(int buildingQueue, bool buildingWritesDepth, int cordQueue) =>
            !buildingWritesDepth && cordQueue >= buildingQueue;
    }

    /// <summary>An integer map cell. Ordered by X then Z, exactly like the oracle's (x, y) tuples.</summary>
    public struct Cell : IEquatable<Cell>, IComparable<Cell>
    {
        public readonly int X;
        public readonly int Z;

        public Cell(int x, int z) { X = x; Z = z; }

        public bool Equals(Cell o) => X == o.X && Z == o.Z;
        public override bool Equals(object obj) => obj is Cell c && Equals(c);
        public override int GetHashCode() => unchecked(X * 73856093 ^ Z * 19349663);
        public int CompareTo(Cell o) => X != o.X ? X.CompareTo(o.X) : Z.CompareTo(o.Z);
        public static bool operator ==(Cell a, Cell b) => a.Equals(b);
        public static bool operator !=(Cell a, Cell b) => !a.Equals(b);
        public static Cell operator +(Cell a, Cell b) => new Cell(a.X + b.X, a.Z + b.Z);
        public V2 Centre => new V2(X + 0.5, Z + 0.5);
        public override string ToString() => "(" + X + "," + Z + ")";

        public static readonly Cell[] Dirs4 = { new Cell(1, 0), new Cell(-1, 0), new Cell(0, 1), new Cell(0, -1) };
        public static readonly Cell[] Dirs8 =
        {
            new Cell(1, 0), new Cell(-1, 0), new Cell(0, 1), new Cell(0, -1),
            new Cell(1, 1), new Cell(1, -1), new Cell(-1, 1), new Cell(-1, -1)
        };
    }

    /// <summary>A 2D point in cell units: X east, Z the map's second axis.</summary>
    public struct V2
    {
        public readonly double X;
        public readonly double Z;

        public V2(double x, double z) { X = x; Z = z; }

        public static V2 operator +(V2 a, V2 b) => new V2(a.X + b.X, a.Z + b.Z);
        public static V2 operator -(V2 a, V2 b) => new V2(a.X - b.X, a.Z - b.Z);
        public static V2 operator -(V2 a) => new V2(-a.X, -a.Z);
        public static V2 operator *(V2 a, double k) => new V2(a.X * k, a.Z * k);
        public static V2 operator *(double k, V2 a) => new V2(a.X * k, a.Z * k);
        public double Len => Math.Sqrt(X * X + Z * Z);
        public V2 Norm() { double l = Len; return l < 1e-9 ? new V2(1, 0) : new V2(X / l, Z / l); }
        public V2 Perp => new V2(-Z, X);
        public Cell Floor => new Cell((int)Math.Floor(X), (int)Math.Floor(Z));
        public static double Dist(V2 a, V2 b) => (a - b).Len;
        public override string ToString() => "(" + X.ToString("0.###") + "," + Z.ToString("0.###") + ")";
    }

    /// <summary>
    /// Local, seeded PRNG (splitmix64). Never Verse.Rand and never System.Random: every choice in
    /// the mod is a pure function of its key, so a cord is identical across frames, reloads and
    /// machines (design §8.2.5).
    /// </summary>
    public sealed class CordRng
    {
        private ulong state;

        public CordRng(ulong seed) { state = seed ^ 0x9E3779B97F4A7C15UL; }

        public static CordRng Of(params object[] key) => new CordRng(Hash(key));

        public static ulong Hash(params object[] key)
        {
            ulong h = 14695981039346656037UL;              // FNV-1a over the key's text form
            foreach (object o in key)
            {
                string s = (o == null ? "~" : Fmt(o)) + "|";
                for (int i = 0; i < s.Length; i++)
                {
                    h ^= s[i];
                    h *= 1099511628211UL;
                }
            }
            return h;
        }

        private static string Fmt(object o)
        {
            if (o is double d) return d.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
            if (o is float f) return ((double)f).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
            if (o is V2 v) return Fmt(v.X) + "," + Fmt(v.Z);
            return Convert.ToString(o, System.Globalization.CultureInfo.InvariantCulture);
        }

        public ulong NextULong()
        {
            ulong z = state += 0x9E3779B97F4A7C15UL;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            return z ^ (z >> 31);
        }

        public double Value() => (NextULong() >> 11) * (1.0 / 9007199254740992.0);
        public double Range(double a, double b) => a + (b - a) * Value();
        /// <summary>Inclusive both ends, like Python's randint.</summary>
        public int Int(int lo, int hi) => lo + (int)(NextULong() % (ulong)(hi - lo + 1));
        public int Sign() => Value() < 0.5 ? -1 : 1;
        public bool Chance(double p) => Value() < p;
    }

    public static class Geo
    {
        public static double[] CumLen(IList<V2> p)
        {
            var s = new double[p.Count];
            for (int i = 1; i < p.Count; i++) s[i] = s[i - 1] + V2.Dist(p[i - 1], p[i]);
            return s;
        }

        public static double Length(IList<V2> p)
        {
            double s = 0;
            for (int i = 1; i < p.Count; i++) s += V2.Dist(p[i - 1], p[i]);
            return s;
        }

        /// <summary>Uniform resample at ~step spacing (render.resample).</summary>
        public static List<V2> Resample(IList<V2> p, double step)
        {
            var outp = new List<V2>();
            if (p.Count == 0) return outp;
            double[] cl = CumLen(p);
            double tot = cl[cl.Length - 1];
            if (tot < 1e-9) { outp.Add(p[0]); outp.Add(p[0]); return outp; }
            int n = Math.Max(2, (int)Math.Ceiling(tot / step) + 1);
            int j = 1;
            for (int k = 0; k < n; k++)
            {
                double s = tot * k / (n - 1);
                while (j < cl.Length - 1 && cl[j] < s) j++;
                double seg = cl[j] - cl[j - 1];
                double t = seg < 1e-12 ? 0 : (s - cl[j - 1]) / seg;
                if (t < 0) t = 0;
                if (t > 1) t = 1;
                outp.Add(p[j - 1] + (p[j] - p[j - 1]) * t);
            }
            return outp;
        }

        /// <summary>Unit tangent and left normal at each point (numpy.gradient semantics).</summary>
        public static void TanNorm(IList<V2> p, int i, out V2 t, out V2 n)
        {
            if (p.Count < 2) { t = new V2(1, 0); n = new V2(0, 1); return; }
            V2 g;
            if (i == 0) g = p[1] - p[0];
            else if (i == p.Count - 1) g = p[i] - p[i - 1];
            else g = (p[i + 1] - p[i - 1]) * 0.5;
            t = g.Norm();
            n = new V2(-t.Z, t.X);
        }

        /// <summary>Centripetal Catmull-Rom through pts (never overshoots); render.catmull.</summary>
        public static List<V2> Catmull(IList<V2> pts, int per)
        {
            if (pts.Count < 3) return Resample(pts, 0.05);
            var P = new List<V2> { pts[0] * 2 - pts[1] };
            P.AddRange(pts);
            P.Add(pts[pts.Count - 1] * 2 - pts[pts.Count - 2]);
            var outp = new List<V2>();
            for (int i = 0; i < P.Count - 3; i++)
            {
                V2 p0 = P[i], p1 = P[i + 1], p2 = P[i + 2], p3 = P[i + 3];
                double t0 = 0;
                double t1 = t0 + Math.Sqrt(Math.Max(V2.Dist(p0, p1), 1e-6));
                double t2 = t1 + Math.Sqrt(Math.Max(V2.Dist(p1, p2), 1e-6));
                double t3 = t2 + Math.Sqrt(Math.Max(V2.Dist(p2, p3), 1e-6));
                for (int k = 0; k < per; k++)
                {
                    double t = t1 + (t2 - t1) * k / per;
                    V2 a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1;
                    V2 a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2;
                    V2 a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3;
                    V2 b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2;
                    V2 b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3;
                    outp.Add((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2);
                }
            }
            outp.Add(P[P.Count - 2]);
            return outp;
        }

        public static double Clamp(double v, double lo, double hi) => v < lo ? lo : v > hi ? hi : v;
    }
}
