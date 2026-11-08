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

        // ---------------------------------------------------------------- never_taut_straight_cord: sharp bends over the whole cord
        /// <summary>The owner, 2026-11-07 7:07 PM: "cords take slowly curving paths rather than straight lines often: what they avoid are sharp curves unless they must". The Conductor's
        /// pass rule (2026-11-08 1:18 AM): no turn tighter than about 90 degrees within one cell, anywhere on a cord, ends included, that no wall, building or socket forces.
        /// A bend is a stretch of cord whose heading turns past <see cref="BendDeg"/> within <see cref="BendArc"/> of its length (the turn summed with its sign, so an S does not add up).
        /// A broad loop, the cord coming round <see cref="LoopDeg"/> or more one way at a radius of <see cref="LoopKeepR"/> or wider, is the north star's own loop, not a bend.</summary>
        public const double BendDeg = 90, BendArc = 1.0, BendStep = 0.05, LoopDeg = 300, LoopKeepR = 0.45;

        internal struct Bend
        {
            /// <summary>The sharpest point; how far along the cord it is and from its nearer end; whether that end is the strand's first.</summary>
            public V2 Apex;
            public double S, FromEnd;
            public bool NearFirst;
            /// <summary>Degrees the heading turns over the bend; its arc (cells); the sharpest turn over 0.2 cell round the apex.</summary>
            public double Turn, Arc, Sharp;
            /// <summary>Degrees the cord keeps turning one way through it, and the radius of that stretch: a loop comes round 300 or more.</summary>
            public double Round, RoundR;
            public bool IsLoop => Round >= LoopDeg && RoundR >= LoopKeepR;
        }

        private static double SignedTurn(V2 u, V2 v)
        {
            if (u.Len < 1e-9 || v.Len < 1e-9) return 0;
            return Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z);
        }

        /// <summary>Radians a strand turns through, either way, from point i0 to point i1.</summary>
        internal static double TotalTurn(List<V2> pts, int i0, int i1)
        {
            double t = 0;
            for (int k = Math.Max(1, i0 + 1); k < Math.Min(pts.Count - 1, i1); k++) t += Math.Abs(SignedTurn(pts[k] - pts[k - 1], pts[k + 1] - pts[k]));
            return t;
        }

        /// <summary>Every bend of a strand, ends included (<see cref="BendDeg"/> within <see cref="BendArc"/>).</summary>
        internal static List<Bend> Bends(List<V2> pts)
        {
            var o = new List<Bend>();
            if (pts == null || pts.Count < 3) return o;
            List<V2> q = Geo.Resample(pts, BendStep);
            int n = q.Count;
            if (n < 4) return o;
            var t = new double[n];
            for (int k = 1; k < n - 1; k++) t[k] = SignedTurn(q[k] - q[k - 1], q[k + 1] - q[k]);
            double[] cum = Geo.CumLen(q);
            double L = cum[n - 1], thr = BendDeg * Math.PI / 180;
            int win = Math.Max(2, (int)Math.Round(BendArc / BendStep));
            var mark = new bool[n];
            for (int i = 1; i < n - 1; i++)
            {
                double sum = 0;
                for (int j = i; j < Math.Min(n - 1, i + win); j++)
                {
                    sum += t[j];
                    if (Math.Abs(sum) > thr) { for (int k = i; k <= j; k++) mark[k] = true; break; }
                }
            }
            int w2 = Math.Max(1, (int)Math.Round(0.1 / BendStep));
            for (int k = 0; k < n; k++)
            {
                if (!mark[k]) continue;
                int j = k;
                while (j + 1 < n && mark[j + 1]) j++;
                double tot = 0;
                for (int m = k; m <= j; m++) tot += t[m];
                double best = -1;
                int apex = k;
                for (int m = k; m <= j; m++)
                {
                    double v = 0;
                    for (int r = Math.Max(1, m - w2); r <= Math.Min(n - 2, m + w2); r++) v += t[r];
                    if (Math.Abs(v) > best) { best = Math.Abs(v); apex = m; }
                }
                // how far the turning keeps one way round it: a coil goes round, a hairpin stops
                int lo = k, hi = j, sg = tot >= 0 ? 1 : -1;
                while (lo > 1 && t[lo - 1] * sg > -0.02) lo--;
                while (hi < n - 2 && t[hi + 1] * sg > -0.02) hi++;
                double oneway = 0;
                for (int m = lo; m <= hi; m++) oneway += t[m];
                oneway = Math.Abs(oneway);
                o.Add(new Bend
                {
                    Apex = q[apex], S = cum[apex], FromEnd = Math.Min(cum[apex], L - cum[apex]), NearFirst = cum[apex] <= L - cum[apex],
                    Turn = Math.Abs(tot) * 180 / Math.PI, Arc = cum[j] - cum[k], Sharp = best * 180 / Math.PI,
                    Round = oneway * 180 / Math.PI, RoundR = oneway > 1e-6 ? (cum[hi] - cum[lo]) / oneway : 99
                });
                k = j;
            }
            return o;
        }

        /// <summary>What a bend is, for the bar: "loop" (a broad loop, the north star's own), "hidden" (under a wall or the art of the machine the cord plugs into), "wall" or "building"
        /// (within <see cref="ForceNear"/> of an unwalkable cell, another machine or furniture: it makes the cord bend), "door" (the cord goes through one straight), "socket" (within
        /// <see cref="SocketReach"/> of an end whose fitting faces a fixed way, a junction arm, a strip socket, a wall plate or a pile port, when the cord's course from there lies
        /// <see cref="BendDeg"/> or more off that facing), "limp" (a dead end's curl, the art of break_live_and_dead_ends_differ), or "unforced". A machine's plug is never a socket:
        /// the mod chooses which side a cord goes in by, so a hook there is a fault.</summary>
        internal static string Why(CordWorld w, string endA, string endB, List<V2> pts, Bend b)
        {
            if (b.IsLoop) return "loop";
            string end = b.NearFirst ? endA : endB;
            string kind = end == null ? "pile" : end.Split(':')[0];
            List<MachineInfo> own = w == null ? new List<MachineInfo>() : OwnMachines(w, endA, endB);
            V2 a = b.Apex;
            if (w != null)
            {
                if (!w.IsWalkable(a.Floor)) return "hidden";
                foreach (MachineInfo m in own)
                    if (InArt(m, a)) return "hidden";
                if (kind == "terminal" && b.FromEnd <= LimpReach) return "limp";
                if (NearCell(a, ForceNear, c => !w.IsWalkable(c))) return "wall";
                if (NearCell(a, ForceNear, c => w.IsFurniture(c)) || w.Machines.Any(m => !own.Contains(m) && RectDist(m.X0, m.Z0, m.W, m.H, a) <= ForceNear)) return "building";
                if (NearCell(a, DoorNear, c => w.IsDoor(c))) return "door";
            }
            bool socket = kind == "junction" || kind.StartsWith("stub_", StringComparison.Ordinal) || kind == "tangle" || kind == "pile" || kind == "terminal";
            if (socket && b.FromEnd <= SocketReach && NeededTurn(pts, b.NearFirst) >= BendDeg) return "socket";
            if (Fitted(endA) && Fitted(endB) && b.Sharp <= FitSharpDeg && b.Turn <= EndsTurn(pts) * 180 / Math.PI + FitSpareDeg && FittingsForce(pts)) return "socket";
            return "unforced";
        }

        /// <summary>A fitting that faces one fixed way: a junction arm, a wall or rock plate, a pile port, a cut end's box. Not a machine's plug (the mod picks its side).</summary>
        private static bool Fitted(string end)
        {
            string k = end == null ? "pile" : end.Split(':')[0];
            return k == "junction" || k.StartsWith("stub_", StringComparison.Ordinal) || k == "tangle" || k == "pile";
        }

        /// <summary>Radians between the way a strand leaves its first end (its first 0.15 cell) and the way it goes into its last.</summary>
        internal static double EndsTurn(List<V2> pts)
        {
            double L = Geo.Length(pts);
            if (L < 0.4) return 0;
            V2 la = PointAt(pts, 0.15) - pts[0], lb = pts[pts.Count - 1] - PointAt(pts, L - 0.15);
            return Math.Abs(SignedTurn(la, lb));
        }

        /// <summary>Two fittings too close to come round between: every way from the one's facing to the other's at <see cref="FitForceR"/> (the radius a quarter turn takes a
        /// whole cell to make) turns more than <see cref="FitForceTurn"/>, a whole loop. A short lead between them must bend tighter than the bar somewhere or throw a ring, so the
        /// fittings force its bend (the ruling's "forced bends at a socket edge"), provided it turns no further than the facings ask (<see cref="FitSpareDeg"/>) and is round, not a
        /// kink (<see cref="FitSharpDeg"/>): a hook is not forced.</summary>
        internal static bool FittingsForce(List<V2> pts)
        {
            if (pts == null || pts.Count < 4) return false;
            double L = Geo.Length(pts);
            if (L > FitForceLen || L < 0.4) return false;
            V2 a = pts[0], b = pts[pts.Count - 1], la = PointAt(pts, 0.15) - a, lb = b - PointAt(pts, L - 0.15);
            foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(a, Math.Atan2(la.Z, la.X), b, Math.Atan2(lb.Z, lb.X), FitForceR))
                if (dp.Turning <= FitForceTurn) return false;
            return true;
        }
        /// <summary><see cref="FitSharpDeg"/>: the most a forced turn may turn within 0.1 cell either side of its apex (a 0.25-cell radius); a kink is never forced.</summary>
        public const double FitForceR = 0.64, FitForceTurn = 1.5 * Math.PI, FitForceLen = 3.0, FitSpareDeg = 25, FitSharpDeg = 45;

        private static V2 PointAt(List<V2> pts, double s)
        {
            double acc = 0;
            for (int i = 1; i < pts.Count; i++)
            {
                double d = V2.Dist(pts[i - 1], pts[i]);
                if (acc + d >= s) return d < 1e-12 ? pts[i] : pts[i - 1] + (pts[i] - pts[i - 1]) * ((s - acc) / d);
                acc += d;
            }
            return pts[pts.Count - 1];
        }
        public const double ForceNear = 0.3, DoorNear = 0.6, SocketReach = 0.75, LimpReach = 1.0;

        /// <summary>How many of a strand's bends the bar counts against it (<see cref="Why"/> "unforced").</summary>
        internal static int Unforced(CordWorld w, string endA, string endB, List<V2> pts)
        {
            int k = 0;
            foreach (Bend b in Bends(pts)) if (Why(w, endA, endB, pts, b) == "unforced") k++;
            return k;
        }

        /// <summary>Degrees between the way a strand leaves one end (its first 0.15 cell) and the way its course runs from there (to the point 1.5 cells on, or 0.6 of it on a short cord).</summary>
        internal static double NeededTurn(List<V2> pts, bool first)
        {
            var q = new List<V2>(pts);
            if (!first) q.Reverse();
            double[] cum = Geo.CumLen(q);
            double L = cum[cum.Length - 1];
            V2 At(double s)
            {
                for (int i = 1; i < q.Count; i++) if (cum[i] >= s) return q[i];
                return q[q.Count - 1];
            }
            V2 leave = At(0.15) - q[0], course = At(Math.Min(1.5, 0.6 * L)) - q[0];
            if (leave.Len < 1e-9 || course.Len < 1e-9) return 0;
            return Math.Abs(SignedTurn(leave, course)) * 180 / Math.PI;
        }

        private static bool NearCell(V2 p, double r, Func<Cell, bool> hit)
        {
            for (int cx = (int)Math.Floor(p.X - r); cx <= (int)Math.Floor(p.X + r); cx++)
                for (int cz = (int)Math.Floor(p.Z - r); cz <= (int)Math.Floor(p.Z + r); cz++)
                    if (hit(new Cell(cx, cz)) && RectDist(cx, cz, 1, 1, p) <= r) return true;
            return false;
        }

        private static double RectDist(int x0, int z0, int w, int h, V2 p)
        {
            double dx = Math.Max(Math.Max(x0 - p.X, 0), p.X - (x0 + w)), dz = Math.Max(Math.Max(z0 - p.Z, 0), p.Z - (z0 + h));
            return Math.Sqrt(dx * dx + dz * dz);
        }

        /// <summary>Inside the drawn art of a machine: its footprint less the art's insets.</summary>
        private static bool InArt(MachineInfo m, V2 p) =>
            p.X >= m.X0 + m.InsetW && p.X <= m.X0 + m.W - m.InsetE && p.Z >= m.Z0 + m.InsetS && p.Z <= m.Z0 + m.H - m.InsetN;

        /// <summary>The machines a piece's two ends name (their cell inside the footprint, or one of its hookups).</summary>
        internal static List<MachineInfo> OwnMachines(CordWorld w, string endA, string endB)
        {
            var o = new List<MachineInfo>();
            foreach (string e in new[] { endA, endB })
            {
                if (e == null) continue;
                int c = e.IndexOf(':');
                if (c < 0) continue;
                string[] xy = e.Substring(c + 1).Split(',');
                if (xy.Length < 2 || !int.TryParse(xy[0], out int x) || !int.TryParse(xy[1], out int z)) continue;
                var cell = new Cell(x, z);
                foreach (MachineInfo m in w.Machines)
                    if ((m.Contains(cell) || m.Hookups.Contains(cell)) && !o.Contains(m)) o.Add(m);
            }
            return o;
        }

        /// <summary>The bar's count over a set of pieces: every bend with what it is, the unforced ones first.</summary>
        public sealed class BendTally
        {
            public int Strands, Bends, Unforced;
            public readonly Dictionary<string, int> ByWhy = new Dictionary<string, int>();
            private readonly List<string> rows = new List<string>();
            private static string F(double d) => d.ToString("0.00", CultureInfo.InvariantCulture);

            internal void Add(CordWorld w, LaidPiece p, CordStrand s)
            {
                if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) return;
                Strands++;
                string name = p.EndA == null ? p.Key : p.EndA + "|" + p.EndB;
                foreach (Bend b in CordShapeAudit.Bends(s.Pts))
                {
                    string why = Why(w, p.EndA, p.EndB, s.Pts, b);
                    Bends++;
                    ByWhy[why] = ByWhy.TryGetValue(why, out int k) ? k + 1 : 1;
                    if (why == "unforced") Unforced++;
                    if (rows.Count < 300 && why != "loop")
                        rows.Add("{\"why\":\"" + why + "\",\"x\":" + F(b.Apex.X) + ",\"z\":" + F(b.Apex.Z) + ",\"turn\":" + F(b.Turn) + ",\"arc\":" + F(b.Arc) + ",\"sharp\":" + F(b.Sharp)
                                 + ",\"fromEnd\":" + F(b.FromEnd) + ",\"piece\":\"" + name + "\"}");
                }
            }

            public string Json() => "{\"strands\":" + Strands + ",\"bends\":" + Bends + ",\"unforced\":" + Unforced + ",\"why\":{" +
                                     string.Join(",", ByWhy.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => "\"" + kv.Key + "\":" + kv.Value)) + "},\"rows\":[" +
                                     string.Join(",", rows.OrderBy(r => r.StartsWith("{\"why\":\"unforced\"", StringComparison.Ordinal) ? 0 : 1)) + "]}";
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
                    if (rows.Count < 400) rows.Add("{\"sharp\":[" + F(k.X) + "," + F(k.Z) + "],\"piece\":\"" + name + "\"}");
                double rod = LongestRod(s.Pts, out V2 at);
                if (rod >= RodLen)
                {
                    Rods++;
                    if (rows.Count < 400) rows.Add("{\"rod\":" + F(rod) + ",\"at\":[" + F(at.X) + "," + F(at.Z) + "],\"piece\":\"" + name + "\"}");
                }
            }

            public string Json() => "{\"strands\":" + Strands + ",\"sharpStrands\":" + SharpStrands + ",\"corners\":" + Corners + ",\"rods\":" + Rods + ",\"rows\":[" + string.Join(",", rows) + "]}";
        }
    }
}
