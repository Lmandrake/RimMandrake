// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// cord_shape_variation_probe (GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE): how alike two laid cords of about one length are. Each edge's
// first strand is sampled by arc length into its own frame (start at the origin, the far end along +X, in cells), so a cord
// moved or turned on the map reads as itself; the distance is the mean point gap between two samples, the smallest over running
// either way and mirrored. Shared by the offline SelfTest and the live probe ("shapetable"), so the same number is proved in both.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public sealed class ShapeClass
    {
        public int Length, Cords, Pairs, TooAlike;
        public double MinDistance = double.MaxValue, MeanDistance;
        public string ClosestA, ClosestB;
    }

    public static class CordShape
    {
        public const int Samples = 48;
        /// <summary>Length classes are this many cells wide: edges of one class lie side by side as "the same cord".</summary>
        public const int ClassWidth = 2;
        /// <summary>Below this mean gap (cells) two cords read as one stamped curve; a cord is 0.08 wide and a loop 0.6-1 across.</summary>
        public const double TooAlikeBelow = 0.3;

        internal static double[] Sample(List<V2> pts)
        {
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            var o = new double[Samples * 2];
            V2 a = pts[0], ax = (pts[pts.Count - 1] - a).Norm();
            if (ax.Len < 0.5) ax = new V2(1, 0);
            V2 up = ax.Perp;
            int k = 0;
            for (int i = 0; i < Samples; i++)
            {
                // by exact arc length, so a cord run the other way samples the same points
                double at = L * i / (Samples - 1);
                while (k < pts.Count - 2 && cum[k + 1] < at) k++;
                double seg = cum[k + 1] - cum[k], t = seg > 1e-9 ? (at - cum[k]) / seg : 0;
                V2 d = pts[k] + (pts[k + 1] - pts[k]) * t - a;
                o[2 * i] = d.X * ax.X + d.Z * ax.Z;
                o[2 * i + 1] = d.X * up.X + d.Z * up.Z;
            }
            return o;
        }

        /// <summary>The mean point gap between two samples, the smallest of running the same way, the other way, and mirrored.</summary>
        internal static double Distance(double[] a, double[] b)
        {
            double best = double.MaxValue, span = a[2 * (Samples - 1)];
            foreach (bool rev in new[] { false, true })
                foreach (bool mir in new[] { false, true })
                {
                    double sum = 0;
                    for (int i = 0; i < Samples; i++)
                    {
                        int j = rev ? Samples - 1 - i : i;
                        double bx = b[2 * j], bz = b[2 * j + 1];
                        if (rev) { bx = b[2 * (Samples - 1)] - bx; bz = -bz; }
                        if (mir) bz = -bz;
                        double dx = a[2 * i] - bx, dz = a[2 * i + 1] - bz;
                        sum += Math.Sqrt(dx * dx + dz * dz);
                    }
                    best = Math.Min(best, sum / Samples);
                }
            return best;
        }

        /// <summary>A fold is two arms meeting at a point: the heading turns past KinkDeg over KinkArc either side of it, and each arm
        /// holds its line (within KinkArmDeg) on out to KinkArm. The arms are what tell it from a coil, whose heading never stops
        /// turning: a heap's tight coils are the art, and a fold is a spike or an elbow the ribbon cannot draw.</summary>
        public const double KinkArc = 0.1, KinkDeg = 60, KinkArm = 0.3, KinkArmDeg = 45;

        private static double TurnDeg(V2 u, V2 v)
        {
            if (u.Len < 1e-6 || v.Len < 1e-6) return 0;
            double cos = (u.X * v.X + u.Z * v.Z) / (u.Len * v.Len);
            return Math.Acos(Math.Max(-1, Math.Min(1, cos))) * 180 / Math.PI;
        }

        private static int AtArc(double[] cum, int from, double arc)
        {
            int j = from;
            if (arc < 0) while (j > 0 && cum[from] - cum[j] < -arc) j--;
            else while (j < cum.Length - 1 && cum[j] - cum[from] < arc) j++;
            return j;
        }

        /// <summary>Where a strand folds back on itself. The ends are skipped: they are the art's (plugs, frays, wall plates).</summary>
        internal static List<V2> Kinks(List<V2> pts, double skipEnds = 0.25)
        {
            var o = new List<V2>();
            if (pts == null || pts.Count < 5) return o;
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1], last = double.MinValue;
            if (L < 1.2) return o;                       // a machine's lead from the strip beside it: under the plug and the machine's art
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i] < skipEnds || cum[i] > L - skipEnds || cum[i] - last < 0.3) continue;
                int a = AtArc(cum, i, -KinkArc), b = AtArc(cum, i, KinkArc), a2 = AtArc(cum, i, -KinkArm), b2 = AtArc(cum, i, KinkArm);
                V2 u = pts[i] - pts[a], v = pts[b] - pts[i];
                if (TurnDeg(u, v) < KinkDeg) continue;
                if (TurnDeg(pts[a] - pts[a2], u) > KinkArmDeg || TurnDeg(v, pts[b2] - pts[b]) > KinkArmDeg) continue;
                o.Add(pts[i]);
                last = cum[i];
            }
            return o;
        }

        /// <summary>A jag is the heading kicking one way past JagDeg over JagArc and straight back within JagSpan. A coil turns one way only and a real bend is far longer,
        /// so neither reads as one. The settle leaves these where it bunches spare length in a straight stretch: a rope buckling, which a ribbon draws as a sawtooth.</summary>
        public const double JagArc = 0.08, JagDeg = 22, JagSpan = 0.3, JagReach = 0.3;

        private static double SignedTurnDeg(V2 u, V2 v)
        {
            if (u.Len < 1e-6 || v.Len < 1e-6) return 0;
            return Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z) * 180 / Math.PI;
        }

        /// <summary>Where a strand's heading jags. The ends are skipped: they are the art's (plugs, frays, wall plates).</summary>
        internal static List<int> Jags(List<V2> pts, double skipEnds = 0.25)
        {
            var o = new List<int>();
            if (pts == null || pts.Count < 7) return o;
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            var turn = new double[pts.Count];
            for (int i = 1; i < pts.Count - 1; i++)
                turn[i] = SignedTurnDeg(pts[i] - pts[AtArc(cum, i, -JagArc)], pts[AtArc(cum, i, JagArc)] - pts[i]);
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i] < skipEnds || cum[i] > L - skipEnds || Math.Abs(turn[i]) < JagDeg) continue;
                for (int j = i + 1; j < pts.Count - 1 && cum[j] - cum[i] <= JagSpan && cum[j] <= L - skipEnds; j++)
                    if (Math.Abs(turn[j]) >= JagDeg && turn[j] * turn[i] < 0)
                    {
                        o.Add(i);
                        i = j;
                        break;
                    }
            }
            return o;
        }

        /// <summary>Stretches of sawtooth: three or more jags in a row, each within SawGap of the last. One or two are the neck of a loop, where it leaves the run and comes back.</summary>
        public const double SawGap = 0.8;

        internal static int Saws(List<V2> pts)
        {
            List<int> at = Jags(pts);
            if (at.Count < 3) return 0;
            double[] cum = Geo.CumLen(pts);
            int saws = 0, run = 1;
            for (int k = 1; k < at.Count; k++)
            {
                run = cum[at[k]] - cum[at[k - 1]] <= SawGap ? run + 1 : 1;
                if (run == 3) saws++;
            }
            return saws;
        }

        /// <summary>Relax every jag into the line either side of it, leaving the rest of the strand where it lies. A point the relaxing would put off walkable ground stays.</summary>
        internal static List<V2> Dejag(CordWorld w, List<V2> pts, double skipEnds = 0.25)
        {
            List<V2> P = pts;
            for (int guard = 0; guard < 12; guard++)
            {
                List<int> at = Jags(P, skipEnds);
                if (at.Count == 0) return P;
                double[] cum = Geo.CumLen(P);
                var Q = new List<V2>(P);
                foreach (int c in at)
                {
                    int a = Math.Max(1, AtArc(cum, c, -JagReach)), b = Math.Min(P.Count - 2, AtArc(cum, c, JagReach));
                    for (int it = 0; it < 6; it++)
                    {
                        var prev = new List<V2>(Q);
                        for (int i = a; i <= b; i++)
                        {
                            double fade = Math.Min(1, Math.Min(i - a + 1, b - i + 1) / 3.0);
                            V2 q = prev[i] + ((prev[i - 1] + prev[i + 1]) * 0.5 - prev[i]) * (0.5 * fade);
                            if (w == null || w.IsWalkable(q.Floor)) Q[i] = q;
                        }
                    }
                }
                P = Q;
            }
            return P;
        }

        /// <summary>A cord reads as more cords than it is where it runs back alongside itself: two straight stretches at least DoubledGapArc apart along the cord, within
        /// DoubledNear of each other and within about 30 degrees of the same line (owner 2026-11-07: "three separate cables ... to a single terminal"; one cord out past a heater,
        /// back to the junction and out again drew three parallel lines between them). Straight is what tells it from a coil, whose sides never hold a line.</summary>
        public const double DoubledNear = 1.1, DoubledGapArc = 1.5, DoubledStraightArc = 0.6, DoubledStraightDeg = 25, DoubledCos = 0.86, DoubledMax = 1.2;
        private const double DoubledStep = 0.15;

        /// <summary>The longest stretch of this strand, in cells, running alongside another stretch of itself. Over <see cref="DoubledMax"/> it reads as a second cord.</summary>
        internal static double Doubled(List<V2> pts)
        {
            if (pts == null || pts.Count < 8) return 0;
            List<V2> q = Geo.Resample(pts, DoubledStep);
            int n = q.Count, reach = (int)Math.Round(DoubledStraightArc / DoubledStep);
            if (n <= 2 * reach + 1) return 0;
            var straight = new bool[n];
            var dir = new V2[n];
            for (int i = reach; i < n - reach; i++)
            {
                V2 u = q[i] - q[i - reach], v = q[i + reach] - q[i];
                straight[i] = TurnDeg(u, v) <= DoubledStraightDeg;
                dir[i] = (q[i + reach] - q[i - reach]).Norm();
            }
            // the longest unbroken stretch alongside: a coil's flat side beside a straight run is a touch, not a second cord
            int gap = (int)Math.Round(DoubledGapArc / DoubledStep), hits = 0, run = 0;
            for (int i = reach; i < n - reach; i++)
            {
                bool along = false;
                if (straight[i])
                    for (int j = reach; j < n - reach && !along; j++)
                        along = Math.Abs(i - j) >= gap && straight[j] && V2.Dist(q[i], q[j]) <= DoubledNear
                            && Math.Abs(dir[i].X * dir[j].X + dir[i].Z * dir[j].Z) >= DoubledCos;
                run = along ? run + 1 : 0;
                hits = Math.Max(hits, run);
            }
            return hits * DoubledStep;
        }

        /// <summary>Times a strand goes under a door beyond what its route asks: once for a door the planned line runs through, never for any other. A slack excursion that wanders under a door
        /// comes out the far side and back again, and from above each pass is one more cable out of that doorway (owner 2026-11-07: "three separate cables coming out of a doorway").</summary>
        internal static int DoorStrays(CordWorld w, List<V2> pts, List<V2> plan)
        {
            if (pts == null || pts.Count == 0) return 0;
            var planned = new HashSet<Cell>();
            if (plan != null)
                foreach (V2 p in plan)
                    if (w.IsDoor(p.Floor)) planned.Add(p.Floor);
            var entered = new HashSet<Cell>();
            int strays = 0;
            bool any = false;
            Cell prev = default(Cell);
            foreach (V2 p in pts)
            {
                Cell c = p.Floor;
                if ((!any || !c.Equals(prev)) && w.IsDoor(c) && (!planned.Contains(c) || !entered.Add(c))) strays++;
                prev = c;
                any = true;
            }
            return strays;
        }

        /// <summary>Times a strand's slack runs in under a powered machine its route does not cross. A bench or a battery is pass-through, so the game calls that floor, but the cord vanishes under the machine and comes
        /// back out, and from above each pass reads as one more cable into it (seen at a smithy in a played colony; owner 2026-11-07: "multiple cables for no reason"). A strand's own plug run is added after this is read.</summary>
        internal static int MachineStrays(CordWorld w, List<V2> pts, List<V2> plan)
        {
            if (pts == null || pts.Count == 0 || w.Machines.Count == 0) return 0;
            var under = new HashSet<Cell>();
            foreach (MachineInfo m in w.Machines)
                for (int x = m.X0; x < m.X0 + m.W; x++)
                    for (int z = m.Z0; z < m.Z0 + m.H; z++) under.Add(new Cell(x, z));
            if (plan != null) foreach (V2 p in plan) under.Remove(p.Floor);
            int strays = 0;
            bool inside = false;
            foreach (V2 p in pts)
            {
                bool now = under.Contains(p.Floor);
                if (now && !inside) strays++;
                inside = now;
            }
            return strays;
        }

        /// <summary>How many times a strand goes in under furniture (<see cref="CordWorld.IsFurniture"/>: a bed, a table, a shelf) at a cell its route
        /// <paramref name="plan"/> does not cross: its slack wandering under a bed and out again reads as more cables going into it (judge, pass 12: a bed
        /// "plugged in twice"). A cord whose route must cross the furniture is no stray there.</summary>
        internal static int FurnitureStrays(CordWorld w, List<V2> pts, List<V2> plan)
        {
            if (pts == null || pts.Count == 0 || !w.HasFurniture) return 0;
            HashSet<Cell> on = null;
            if (plan != null) { on = new HashSet<Cell>(); foreach (V2 p in plan) on.Add(p.Floor); }
            int strays = 0;
            bool inside = false;
            bool Under(V2 q)
            {
                Cell c = q.Floor;
                return w.IsFurniture(c) && (on == null || !on.Contains(c));
            }
            foreach (V2 p in pts)
            {
                // a graze along its edge is under the art's own margin: only a pass FurnitureDeep inside counts
                bool now = Under(p) && Under(p + new V2(FurnitureDeep, 0)) && Under(p - new V2(FurnitureDeep, 0)) && Under(p + new V2(0, FurnitureDeep)) && Under(p - new V2(0, FurnitureDeep));
                if (now && !inside) strays++;
                inside = now;
            }
            return strays;
        }
        /// <summary>How far in under furniture a cord must go before it reads as passing under it, cells.</summary>
        public const double FurnitureDeep = 0.2;

        /// <summary>The ring round a strand's own end, and round a door, that one cord should cross no more than it has to: a loop inside it draws extra lines at that point.</summary>
        public const double EndRing = 1.5, DoorRing = 1.5;

        /// <summary>Lines this strand draws at its own ends and at any door beyond what it needs: one at each end, two at a door (in and out). A coil laid on the end or the door crosses the ring
        /// three times or more, and from above that is more cables reaching one place (owner 2026-11-07: "three separate cables coming out of a doorway to go to a single terminal node").</summary>
        internal static int RingReturns(CordWorld w, List<V2> pts) => RingReturns(w, pts, out _);

        /// <summary><see cref="RingReturns(CordWorld, List{V2})"/>, and how many of those extra lines are at a door.</summary>
        internal static int RingReturns(CordWorld w, List<V2> pts, out int atDoors)
        {
            atDoors = 0;
            if (pts == null || pts.Count < 3) return 0;
            List<V2> q = Geo.Resample(pts, DoubledStep / 2);
            int extra = Math.Max(0, Crossings(q, pts[0], EndRing) - 1) + Math.Max(0, Crossings(q, pts[pts.Count - 1], EndRing) - 1);
            var doors = new HashSet<Cell>();
            Cell last = new Cell(int.MinValue, int.MinValue);
            foreach (V2 p in q)
            {
                Cell c = p.Floor;
                if (c.Equals(last)) continue;
                last = c;
                for (int dx = -2; dx <= 2; dx++)
                    for (int dz = -2; dz <= 2; dz++)
                    {
                        var d = new Cell(c.X + dx, c.Z + dz);
                        if (w.InBounds(d) && w.IsDoor(d)) doors.Add(d);
                    }
            }
            foreach (Cell d in doors) atDoors += Math.Max(0, Crossings(q, d.Centre, DoorRing) - 2);
            return extra + atDoors;
        }

        internal static int Crossings(List<V2> q, V2 at, double r)
        {
            int n = 0;
            bool inside = false, any = false;
            foreach (V2 p in q)
            {
                bool now = V2.Dist(p, at) <= r;
                if (any && now != inside) n++;
                inside = now;
                any = true;
            }
            return n;
        }

        /// <summary>How far either side of a fold the rounding reaches, and the widest it opens a fold that doubles straight back.</summary>
        private const double UnfoldReach = 0.3, UnfoldFlare = 0.13;

        /// <summary>Round every fold into a small bend, leaving the rest of the strand exactly where it lies, so its loops and its
        /// ends do not move. A fold whose bend would leave walkable ground stays: the floor rule outranks the look.</summary>
        internal static List<V2> Unfold(CordWorld w, List<V2> pts, double skipEnds = 0.25)
        {
            List<V2> P = Polish(w, Dejag(w, pts, skipEnds), Math.Max(PolishPin, skipEnds));
            var stuck = new List<V2>();
            for (int guard = 0; guard < 60; guard++)
            {
                V2? at = null;
                foreach (V2 k in Kinks(P, skipEnds))
                    if (!stuck.Any(q => V2.Dist(q, k) < 0.05)) { at = k; break; }
                if (at == null) return P;
                List<V2> round = RoundFold(w, P, at.Value);
                if (round == null) stuck.Add(at.Value); else P = round;
            }
            return P;
        }

        /// <summary>How far from each end the polish leaves a strand alone (the art's plug or fray lines up there), the arc it fades in over, and its passes of a 1-2-1 filter on samples PolishStep apart.
        /// Eight passes are a blur of 0.1 cell: enough to take a settle's ripple and any corner off a cord, while a 0.2 cell coil only draws in by a seventh.</summary>
        public const double PolishPin = 0.2, PolishFade = 0.15, PolishStep = 0.05;
        public const int PolishPasses = 8;

        /// <summary>The last word on a laid strand: a cord has no corners and no ripple at any scale it can be seen at (shape lab on a played colony: 55 of 70 strands had a sharp corner, and a sawtooth
        /// on a stretch along a wall, while the fold check read clean). Only the fine scale moves, so the loops and the lay stay as they were. A point that would leave walkable ground stays where it is.</summary>
        internal static List<V2> Polish(CordWorld w, List<V2> pts, double pinEnds = PolishPin)
        {
            if (pts == null || pts.Count < 7) return pts;
            // the ends stay exactly as laid, point for point: what the art lines up with, a live end's straight run and a dead end's curl
            double[] cum = Geo.CumLen(pts);
            double L = cum[cum.Length - 1];
            int ia = 0, ib = pts.Count - 1;
            while (ia < pts.Count - 1 && cum[ia] < pinEnds) ia++;
            while (ib > 0 && cum[ib] > L - pinEnds) ib--;
            if (ib - ia < 6) return pts;
            List<V2> P = Geo.Resample(pts.GetRange(ia, ib - ia + 1), PolishStep);
            int n = P.Count;
            if (n < 7) return pts;
            V2 first = P[0], last = P[n - 1];
            var weight = new double[n];
            for (int i = 0; i < n; i++) weight[i] = Math.Min(1, Math.Min(i, n - 1 - i) * PolishStep / PolishFade);
            var X = P.ToArray();
            var tmp = new V2[n];
            for (int pass = 0; pass < PolishPasses; pass++)
            {
                Array.Copy(X, tmp, n);
                for (int i = 1; i < n - 1; i++)
                {
                    if (weight[i] <= 0) continue;
                    V2 q = tmp[i] + ((tmp[i - 1] + tmp[i + 1]) * 0.5 - tmp[i]) * (0.5 * weight[i]);
                    if (w == null || w.IsWalkable(q.Floor)) X[i] = q;
                }
            }
            // a needle, two arms lying together, only shortens under a blur: what still reads as a corner gets its own passes, until it opens or it has retracted into the line
            for (int guard = 0; guard < PolishNeedleRounds; guard++)
            {
                var list = new List<V2>(X);
                List<V2> corners = CordShapeAudit.Corners(list, 0.05);
                if (corners.Count == 0) break;
                foreach (V2 c in corners)
                {
                    int at = list.IndexOf(c), reach = (int)Math.Round(PolishNeedleReach / PolishStep);
                    if (at < 0) continue;
                    for (int pass = 0; pass < PolishPasses; pass++)
                    {
                        Array.Copy(X, tmp, n);
                        for (int i = Math.Max(1, at - reach); i <= Math.Min(n - 2, at + reach); i++)
                        {
                            double fade = Math.Min(1, (reach + 1 - Math.Abs(i - at)) / 3.0) * weight[i];
                            if (fade <= 0) continue;
                            V2 q = tmp[i] + ((tmp[i - 1] + tmp[i + 1]) * 0.5 - tmp[i]) * (0.5 * fade);
                            if (w == null || w.IsWalkable(q.Floor)) X[i] = q;
                        }
                    }
                }
            }
            X[0] = first;
            X[n - 1] = last;
            var o = new List<V2>(pts.Count + n);
            o.AddRange(pts.GetRange(0, ia));
            o.AddRange(X);
            o.AddRange(pts.GetRange(ib + 1, pts.Count - ib - 1));
            return o;
        }

        /// <summary>The owner, 2026-11-07 7:07 PM: "cords take slowly curving paths rather than straight lines often: what they avoid are sharp curves unless they must". The last shaping a laid
        /// floor strand gets: wherever it bends tighter than <see cref="FairR"/> on open floor it is drawn toward its chord a little at a time, so the bend opens and the cord gives up the
        /// length the tight bend took, until no such bend is left. Its broad loops (<see cref="CordShapeAudit.LoopKeepR"/> and wider) and the art at its two ends (<paramref name="pinA"/>,
        /// <paramref name="pinB"/> cells) stay exactly as laid. A point never moves onto ground the cord may not lie on, into a doorway, furniture or a machine it does not plug into,
        /// or closer to a wall than it was: a bend a wall or a building makes is left as that thing makes it.</summary>
        internal static List<V2> Fair(CordWorld w, List<V2> pts, double pinA, double pinB, List<MachineInfo> own = null, HashSet<Cell> within = null, bool cutLoops = true)
        {
            if (pts == null || pts.Count < 7) return pts;
            double L0 = Geo.Length(pts);
            if (L0 < pinA + pinB + 2 * FairK * FairStep) return pts;
            HashSet<Cell> machine = null;
            if (w != null && w.Machines.Count > 0)
            {
                machine = new HashSet<Cell>();
                double x0 = pts.Min(q => q.X) - 2, x1 = pts.Max(q => q.X) + 2, z0 = pts.Min(q => q.Z) - 2, z1 = pts.Max(q => q.Z) + 2;
                foreach (MachineInfo m in w.Machines)
                {
                    if ((own != null && own.Contains(m)) || m.X0 > x1 || m.X0 + m.W < x0 || m.Z0 > z1 || m.Z0 + m.H < z0) continue;
                    for (int x = m.X0; x < m.X0 + m.W; x++)
                        for (int z = m.Z0; z < m.Z0 + m.H; z++) machine.Add(new Cell(x, z));
                }
            }
            bool Ok(V2 from, V2 to)
            {
                if (w == null) return true;
                Cell cf = from.Floor, ct = to.Floor;
                if (!w.IsWalkable(ct) || (within != null && !within.Contains(ct))) return false;
                if (ct != cf && (w.IsFurniture(ct) || (w.IsDoor(ct) && !w.IsDoor(cf)) || (machine != null && machine.Contains(ct)))) return false;
                double c = w.Clearance(to);
                return c >= LayParams.RC || c >= w.Clearance(from) - 1e-6;
            }
            List<V2> X = Geo.Resample(pts, FairStep);
            V2 first = pts[0], last = pts[pts.Count - 1];
            int cuts = 0;
            for (int round = 0; round < FairRounds; round++)
            {
                int n = X.Count;
                if (n < 2 * FairK + 3) break;
                double[] cum = Geo.CumLen(X);
                double L = cum[n - 1];
                var still = new bool[n];
                for (int i = 0; i < n; i++) still[i] = i == 0 || i == n - 1 || cum[i] < pinA || cum[i] > L - pinB;
                List<CordShapeAudit.Bend> bends = CordShapeAudit.Bends(X);
                // a loop too tight to be a broad one is taken out whole where the cord crosses itself: drawn in, it only pinches into a teardrop
                bool cut = false;
                foreach (CordShapeAudit.Bend b in bends)
                {
                    if (!cutLoops || b.Round < CordShapeAudit.LoopDeg || b.IsLoop || cuts >= 8) continue;
                    double half = 0.5 * b.Round * Math.PI / 180 * b.RoundR + 0.3;
                    int lo = 0, hi = n - 1;
                    while (lo < n - 1 && cum[lo] < b.S - half) lo++;
                    while (hi > 0 && cum[hi] > b.S + half) hi--;
                    int bi = -1, bj = -1;
                    V2 at = default(V2);
                    for (int i = Math.Max(lo, 1); i < hi; i++)
                        for (int j = hi - 1; j > i + 2 && (bj < 0 || j - i > bj - bi); j--)
                            if (!still[i] && !still[j + 1] && Cross(X[i], X[i + 1], X[j], X[j + 1], out V2 c)) { bi = i; bj = j; at = c; break; }
                    if (bi < 0) continue;
                    var Xn = new List<V2>(X.GetRange(0, bi + 1)) { at };
                    Xn.AddRange(X.GetRange(bj + 1, n - bj - 1));
                    X = Geo.Resample(Xn, FairStep);
                    cut = true;
                    break;
                }
                if (cut) { cuts++; round--; continue; }
                foreach (CordShapeAudit.Bend b in bends)
                    if (b.IsLoop)
                    {
                        // the whole round stretch stays: a broad loop is the north star's own
                        double half = 0.5 * b.Round * Math.PI / 180 * b.RoundR + 0.1;
                        for (int i = 0; i < n; i++) if (Math.Abs(cum[i] - b.S) <= half) still[i] = true;
                    }
                var h = new double[n];
                var Y = new V2[n];
                var Z = X.ToArray();
                bool moved = false;
                for (int it = 0; it < FairIters; it++)
                {
                    bool any = false;
                    Array.Clear(h, 0, n);
                    for (int i = FairK; i < n - FairK; i++)
                    {
                        if (still[i] || Radius(Z[i - FairK], Z[i], Z[i + FairK]) >= FairR) continue;
                        any = true;
                        for (int j = Math.Max(1, i - 2 * FairK); j <= Math.Min(n - 2, i + 2 * FairK); j++) h[j] = Math.Max(h[j], 1 - Math.Abs(i - j) / (2.0 * FairK + 1));
                    }
                    if (!any) break;
                    Array.Copy(Z, Y, n);
                    for (int i = 1; i < n - 1; i++)
                    {
                        if (h[i] <= 0 || still[i]) continue;
                        int a = Math.Max(0, i - FairK), b = Math.Min(n - 1, i + FairK);
                        V2 m = Y[a];
                        for (int j = a + 1; j <= b; j++) m = m + Y[j];
                        V2 q = Y[i] + (m * (1.0 / (b - a + 1)) - Y[i]) * (0.5 * h[i]);
                        if (Ok(Y[i], q)) { Z[i] = q; moved = true; }
                    }
                }
                if (!moved) break;
                X = Geo.Resample(Z, FairStep);
            }
            X[0] = first;
            X[X.Count - 1] = last;
            return X;
        }
        /// <summary><see cref="Fair"/>: no bend on open floor tighter than this (cells), read over +-<see cref="FairK"/> samples <see cref="FairStep"/> apart; <see cref="FairRounds"/> rounds of
        /// <see cref="FairIters"/> steps, resampled between rounds so a drawn-in bend is read over the same arc again.</summary>
        public const double FairR = 0.7, FairStep = 0.05;
        private const int FairK = 6, FairIters = 12, FairRounds = 8;

        // RepairPin is the measurement ignore zone and the default protected end run.
        // Preserve its original vertices exactly; cut ends receive longer protected runs.
        internal const double RepairPin = 0.35;
        private const double RepairRadiusFloor = 0.10, RepairRadiusTarget = 1.15 * RepairRadiusFloor;
        private const double RepairStep = 0.0125, RepairTiePad = 0.08;
        private static readonly (double A, double B)[] RepairWindows =
        {
            (0.9, 0.9), (0.6, 0.6), (1.3, 1.3),
            (0.4, 0.8), (0.8, 0.4), (1.9, 1.9), (2.8, 2.8),
            (0.4, 0.4), (0.25, 0.25), (0.25, 0.5), (0.5, 0.25),
            (0.6, 1.2), (1.2, 0.6), (0.9, 1.8), (1.8, 0.9),
            (1.3, 2.6), (2.6, 1.3), (1.9, 3.8), (3.8, 1.9),
            (2.8, 5.6), (5.6, 2.8)
        };
        private static readonly double[] RepairRadii = { 0.32, 0.24, 0.45, 0.6, 0.72, 0.85, 0.18, 0.14, 0.12 };
        private static readonly double[] RepairOffsets = { 0, 0.06, -0.06, 0.18, -0.18, 0.36, -0.36 };
        private static readonly double[] RepairAwayOffsets = { 0.06, 0, 0.18, -0.06, 0.36, -0.18, -0.36 };
        private static readonly double[] RepairRescueOffsets = { 0, 0.06, 0.12, 0.18, 0.24, 0.36, -0.06, -0.18, -0.36 };
        private static readonly double[] RepairRescueRadii = { 0.14, 0.12, 0.18, 0.24, 0.32, 0.45, 0.6, 0.72, 0.85 };
        private static readonly double[] RepairScales = { 0.08, 0.16, 0.24 };
        private static readonly Comparison<Dubins.Path> RepairPathOrder = (a, b) => a.Len.CompareTo(b.Len);
        // Shared by the entire call; each window also yields promptly to wider windows.
        private const int RepairSampleLimit = 48, RepairVerifyLimit = 16, RepairOffsetLimit = 112;
        private const int RepairWindowSamples = 6, RepairWindowVerifies = 4, RepairWindowOffsets = 14;

        private sealed class RepairScratch
        {
            internal double[] Cum = Array.Empty<double>(), ScanCum = Array.Empty<double>();
            internal double[] Positive = Array.Empty<double>(), Negative = Array.Empty<double>();
            internal int[] MinHeading = Array.Empty<int>(), MaxHeading = Array.Empty<int>();
            internal readonly int[] Cursors = new int[14];
            internal readonly HashSet<Cell> Doors = new HashSet<Cell>(), MachineCells = new HashSet<Cell>();
            internal readonly Dictionary<Cell, double> ClearanceFloors = new Dictionary<Cell, double>();
            internal readonly RepairCellGrid OriginalGrid = new RepairCellGrid(), Fittings = new RepairCellGrid(), WindowGrid = new RepairCellGrid();
            internal readonly List<double> KeepOff = new List<double>();
            internal readonly List<V2> Stuck = new List<V2>();
            internal readonly RepairQuality BeforeQuality = new RepairQuality(), AfterQuality = new RepairQuality();
            internal double FittingReach;
            internal Func<V2, bool> FittingPolicy;
            internal bool FittingClear(V2 q) => Fittings.PointClear(q, KeepOff, FittingReach);
            internal readonly List<double> Faults = new List<double>(), Remaining = new List<double>();
            internal readonly List<double> QualityFaults = new List<double>();
            internal readonly List<V2> BasePatch = new List<V2>(), Patch = new List<V2>(), Candidate = new List<V2>();
            internal readonly List<CordTie> Ties = new List<CordTie>();
            internal readonly List<Dubins.Path> Paths = new List<Dubins.Path>(6);
            internal readonly List<(int A, int B)> Windows = new List<(int A, int B)>();
            internal readonly List<(int Sign, double Peak, double S, double Last)> Lobes =
                new List<(int Sign, double Peak, double S, double Last)>();
            internal readonly List<(double S, V2 Dir, double Heading)> Tangents =
                new List<(double S, V2 Dir, double Heading)>();
        }

        // Reused half-cell buckets. Queries visit nearby segments, never the whole strand.
        private sealed class RepairCellGrid
        {
            private const double CellSize = 0.5;
            private readonly Dictionary<Cell, List<int>> cells = new Dictionary<Cell, List<int>>();
            private readonly List<List<int>> buckets = new List<List<int>>();
            private int used;
            private List<V2> pts;
            private bool pointsOnly;
            private static int Index(double x) => (int)Math.Floor(x / CellSize);

            internal void Set(List<V2> points, int first, int last, bool asPoints = false)
            {
                for (int i = 0; i < used; i++) buckets[i].Clear();
                cells.Clear();
                used = 0;
                pts = points;
                pointsOnly = asPoints;
                int end = asPoints ? last + 1 : last;
                for (int i = first; i < end; i++)
                {
                    V2 a = pts[i], b = asPoints ? a : pts[i + 1];
                    int x0 = Index(Math.Min(a.X, b.X)), x1 = Index(Math.Max(a.X, b.X));
                    int z0 = Index(Math.Min(a.Z, b.Z)), z1 = Index(Math.Max(a.Z, b.Z));
                    for (int x = x0; x <= x1; x++)
                        for (int z = z0; z <= z1; z++)
                        {
                            var c = new Cell(x, z);
                            if (!cells.TryGetValue(c, out List<int> bucket))
                            {
                                if (used == buckets.Count) buckets.Add(new List<int>());
                                bucket = buckets[used++];
                                cells.Add(c, bucket);
                            }
                            bucket.Add(i);
                        }
                }
            }

            internal double Distance(V2 q, double reach)
            {
                double best = double.PositiveInfinity;
                int x0 = Index(q.X - reach), x1 = Index(q.X + reach);
                int z0 = Index(q.Z - reach), z1 = Index(q.Z + reach);
                for (int x = x0; x <= x1; x++)
                    for (int z = z0; z <= z1; z++)
                        if (cells.TryGetValue(new Cell(x, z), out List<int> bucket))
                            for (int k = 0; k < bucket.Count; k++)
                            {
                                int i = bucket[k];
                                best = Math.Min(best, RepairPointSegment2(q, pts[i], pointsOnly ? pts[i] : pts[i + 1]));
                            }
                return Math.Sqrt(best);
            }

            internal bool PointClear(V2 q, List<double> floors, double reach)
            {
                int x0 = Index(q.X - reach), x1 = Index(q.X + reach);
                int z0 = Index(q.Z - reach), z1 = Index(q.Z + reach);
                for (int x = x0; x <= x1; x++)
                    for (int z = z0; z <= z1; z++)
                        if (cells.TryGetValue(new Cell(x, z), out List<int> bucket))
                            for (int k = 0; k < bucket.Count; k++)
                            {
                                int i = bucket[k];
                                double floor = Math.Max(0, floors[i] - 1e-6);
                                if (RepairPointSegment2(q, pts[i], pts[i]) < floor * floor) return false;
                            }
                return true;
            }

            internal double CellClearance(Cell c, double reach)
            {
                double best = reach;
                int x0 = Index(c.X - reach), x1 = Index(c.X + 1 + reach);
                int z0 = Index(c.Z - reach), z1 = Index(c.Z + 1 + reach);
                for (int x = x0; x <= x1; x++)
                    for (int z = z0; z <= z1; z++)
                        if (cells.TryGetValue(new Cell(x, z), out List<int> bucket))
                            for (int k = 0; k < bucket.Count; k++)
                            {
                                int i = bucket[k];
                                best = Math.Min(best, RepairCellSegmentDistance(pts[i], pts[i + 1], c));
                                if (best <= -0.5) return -0.5;
                            }
                return best;
            }
        }

        // Fault peaks, normalized by their own thresholds: radius curvature,
        // opposite-peak saw and signed V-turn. Measure the affected neighbourhood
        // and each join separately so an improvement cannot move damage to a join.
        private sealed class RepairQuality
        {
            private readonly double[] peak = new double[9];
            internal void Clear() => Array.Clear(peak, 0, peak.Length);

            internal void Add(string kind, double s, double value, double a, double b)
            {
                if (s < a - 0.65 || s > b + 0.65) return;
                int k = kind == "radius" ? 0 : kind == "saw" ? 1 : 2;
                peak[k] = Math.Max(peak[k], value);
                if (s <= a + 0.30) peak[3 + k] = Math.Max(peak[3 + k], value);
                if (s >= b - 0.30) peak[6 + k] = Math.Max(peak[6 + k], value);
            }

            internal double Worst => Math.Max(peak[0], Math.Max(peak[1], peak[2]));
            internal bool RadiusClear => peak[0] == 0;

            internal bool NoWorseThan(RepairQuality before)
            {
                for (int i = 0; i < peak.Length; i++)
                    if (peak[i] > before.peak[i] + 1e-6) return false;
                return true;
            }
        }

        private static RepairQuality MeasureRepairQuality(List<V2> pts, List<CordTie> ties, double a, double b,
                                                          double radiusTarget = RepairRadiusTarget)
        {
            RepairQuality quality = RepairWork.BeforeQuality;
            quality.Clear();
            CurvatureFaults(pts, ties, RepairWork.QualityFaults, a - 1.3, b + 1.3,
                measure: (kind, s, value) => quality.Add(kind, s, value, a, b),
                radiusTarget: radiusTarget);
            return quality;
        }

        [ThreadStatic] private static RepairScratch repairScratch;
        private static RepairScratch RepairWork => repairScratch ?? (repairScratch = new RepairScratch());

        internal static bool HasCurvatureFaults(List<V2> pts, List<CordTie> ties = null)
        {
            return MayNeedCurvatureRepair(pts, ties)
                && CurvatureFaults(pts, ties, RepairWork.Faults).Count != 0;
        }

        internal static Func<V2, bool> ExistingFittingClearance(List<V2> pts, List<V2> boxes, double reach)
        {
            RepairScratch work = RepairWork;
            work.OriginalGrid.Set(pts, 0, pts.Count - 1);
            work.Fittings.Set(boxes, 0, boxes.Count - 1, asPoints: true);
            work.KeepOff.Clear();
            work.FittingReach = reach;
            for (int i = 0; i < boxes.Count; i++)
                work.KeepOff.Add(Math.Min(reach, work.OriginalGrid.Distance(boxes[i], reach)));
            return work.FittingPolicy ?? (work.FittingPolicy = work.FittingClear);
        }

        private static double RepairPointSegment2(V2 q, V2 a, V2 b)
        {
            V2 d = b - a, v = q - a;
            double dd = d.X * d.X + d.Z * d.Z;
            double t = dd > 1e-20 ? Math.Max(0, Math.Min(1, (v.X * d.X + v.Z * d.Z) / dd)) : 0;
            V2 gap = v - d * t;
            return gap.X * gap.X + gap.Z * gap.Z;
        }

        private static double RepairCellPointDistance(V2 q, Cell c)
        {
            double x = Math.Max(c.X - q.X, q.X - c.X - 1);
            double z = Math.Max(c.Z - q.Z, q.Z - c.Z - 1);
            if (x <= 0 && z <= 0) return Math.Max(x, z);
            x = Math.Max(0, x); z = Math.Max(0, z);
            return Math.Sqrt(x * x + z * z);
        }

        // Exact minimum signed distance from a segment to a unit obstacle cell.
        // Negative values retain an existing graze inside furniture, without deepening it.
        private static double RepairCellSegmentDistance(V2 a, V2 b, Cell c)
        {
            double best = Math.Min(RepairCellPointDistance(a, c), RepairCellPointDistance(b, c));
            if (best >= 0)
                for (int corner = 0; corner < 4; corner++)
                {
                    V2 q = new V2(c.X + (corner & 1), c.Z + ((corner >> 1) & 1));
                    best = Math.Min(best, Math.Sqrt(RepairPointSegment2(q, a, b)));
                }
            if (Math.Max(a.X, b.X) < c.X || Math.Min(a.X, b.X) > c.X + 1
                || Math.Max(a.Z, b.Z) < c.Z || Math.Min(a.Z, b.Z) > c.Z + 1) return best;
            V2 d = b - a;
            double C(int side) => side == 0 ? c.X - a.X : side == 1 ? a.X - c.X - 1
                : side == 2 ? c.Z - a.Z : a.Z - c.Z - 1;
            double D(int side) => side == 0 ? -d.X : side == 1 ? d.X : side == 2 ? -d.Z : d.Z;
            // Inside the rectangle the signed distance is the maximum of four affine
            // functions. Its minimum is at an endpoint or an intersection of two.
            for (int i = 0; i < 4; i++)
                for (int j = i + 1; j < 4; j++)
                {
                    double den = D(i) - D(j);
                    if (Math.Abs(den) < 1e-20) continue;
                    double t = (C(j) - C(i)) / den;
                    if (t > 0 && t < 1)
                        best = Math.Min(best, RepairCellPointDistance(a + d * t, c));
                }
            return best;
        }

        private static double[] RepairCum(List<V2> pts, ref double[] into)
        {
            if (into.Length < pts.Count) Array.Resize(ref into, Math.Max(pts.Count, Math.Max(64, into.Length * 2)));
            into[0] = 0;
            for (int i = 1; i < pts.Count; i++) into[i] = into[i - 1] + V2.Dist(pts[i - 1], pts[i]);
            return into;
        }

        private static bool RepairTied(List<CordTie> ties, double a, double b)
        {
            if (ties != null)
                for (int i = 0; i < ties.Count; i++)
                    if (a <= ties[i].S1 + RepairTiePad && b >= ties[i].S0 - RepairTiePad) return true;
            return false;
        }

        /// <summary>Conservative O(n) bounds on the original polyline, using reused buffers.
        /// Radius needs enough absolute turn over its own diameter; a saw needs both signs;
        /// a V-turn needs 155 degrees within its tangent span. Broad one-way coils pass cheaply.</summary>
        internal static bool MayNeedCurvatureRepair(List<V2> pts, List<CordTie> ties = null)
        {
            if (pts == null || pts.Count < 4) return false;
            RepairScratch work = RepairWork;
            double[] cum = RepairCum(pts, ref work.ScanCum);
            int n = pts.Count;
            double L = cum[n - 1];
            if (L <= 2 * RepairPin) return false;
            if (work.Positive.Length < n)
            {
                int size = Math.Max(n, Math.Max(64, work.Positive.Length * 2));
                Array.Resize(ref work.Positive, size);
                Array.Resize(ref work.Negative, size);
            }
            double[] positive = work.Positive, negative = work.Negative;
            positive[0] = negative[0] = 0;
            for (int i = 1; i < n - 1; i++)
            {
                if (cum[i] - cum[i - 1] < 1e-9 || cum[i + 1] - cum[i] < 1e-9) return true;
                if (cum[i - 1] >= RepairPin && cum[i + 1] <= L - RepairPin
                    && !RepairTied(ties, cum[i - 1], cum[i + 1])
                    && Radius(pts[i - 1], pts[i], pts[i + 1]) < RepairRadiusTarget) return true;
                double turn = cum[i] < RepairPin || cum[i] > L - RepairPin || RepairTied(ties, cum[i], cum[i])
                    ? 0 : SignedTurnDeg(pts[i] - pts[i - 1], pts[i + 1] - pts[i]);
                positive[i] = positive[i - 1] + Math.Max(0, turn);
                negative[i] = negative[i - 1] + Math.Max(0, -turn);
            }
            for (int pass = 0; pass < 5; pass++)
            {
                double span = pass < 3 ? 2 * RepairScales[pass] : pass == 3 ? 0.65 : 0.68;
                double threshold = pass < 3 ? RepairScales[pass] * 180 / (Math.PI * RepairRadiusTarget) : 155;
                int left = 1;
                for (int right = 1; right < n - 1; right++)
                {
                    while (left < right && cum[right] - cum[left] > span + 1e-9) left++;
                    double p = positive[right] - positive[left - 1];
                    double m = negative[right] - negative[left - 1];
                    if (pass == 3 ? p >= 24 - 1e-8 && m >= 24 - 1e-8
                        : p + m > threshold - 1e-8) return true;
                }
            }
            return false;
        }

        /// <summary>The final local repair, after plug exits: copy everything outside a replacement window verbatim.
        /// Endpoint poses and tied loops stay untouched; a replacement must pass the curvature checks through its joins.
        /// Own machine runs are intentional, and an existing narrow wall gap may be retained but never narrowed.</summary>
        internal static List<V2> RepairCurvature(CordWorld w, List<V2> pts, List<CordTie> ties = null, Func<V2, bool> extraClear = null,
                                               List<MachineInfo> own = null, Action<string> trace = null,
                                               double pinA = RepairPin, double pinB = RepairPin, bool faultsReady = false,
                                               Func<List<V2>, bool> approachClear = null,
                                               Func<List<V2>, double[], double, (double Lo, double Hi)> approachBounds = null)
        {
            // FinalCurvature already measured this strand before constructing its fitting policy.
            if (!faultsReady && !HasCurvatureFaults(pts, ties)) return pts;
            List<V2> result = RepairCurvatureSlow(w, pts, ties, extraClear, own, trace, pinA, pinB,
                approachClear: approachClear, approachBounds: approachBounds);
            if (RepairWork.Faults.Count == 0) return result;
            // Preserve successful ordinary repairs. Exhaust the alternative bows at
            // the preferred margin before allowing the smaller, still-safe target.
            for (int pass = 0; pass < 2; pass++)
            {
                double target = pass == 0 ? RepairRadiusTarget : RepairRadiusFloor * 1.001;
                for (int profile = 1; profile <= 3; profile++)
                {
                    CurvatureFaults(result, ties, RepairWork.Faults, radiusTarget: target);
                    if (RepairWork.Faults.Count == 0) return result;
                    if (trace != null)
                        trace("rescue profile " + profile + " radius target "
                            + target.ToString("0.0000", System.Globalization.CultureInfo.InvariantCulture));
                    result = RepairCurvatureSlow(w, result, ties, extraClear, own, trace,
                        pinA, pinB, profile, target, approachClear, approachBounds);
                }
            }
            return result;
        }

        private static List<V2> RepairCurvatureSlow(CordWorld w, List<V2> pts, List<CordTie> ties, Func<V2, bool> extraClear,
                                                   List<MachineInfo> own, Action<string> trace, double pinA, double pinB,
                                                   int bowProfile = 0, double radiusTarget = RepairRadiusTarget,
                                                   Func<List<V2>, bool> approachClear = null,
                                                   Func<List<V2>, double[], double, (double Lo, double Hi)> approachBounds = null)
        {
            RepairScratch work = RepairWork;
            List<double> faults = work.Faults;
            if (faults.Count == 0) return pts;
            HashSet<Cell> doors = work.Doors;
            doors.Clear();
            work.MachineCells.Clear();
            if (w != null) foreach (V2 q in pts) if (w.IsDoor(q.Floor)) doors.Add(q.Floor);
            // Graph and world may hold different snapshot objects for the same machine.
            bool Own(MachineInfo m)
            {
                if (own != null)
                    for (int i = 0; i < own.Count; i++)
                    {
                        MachineInfo o = own[i];
                        if (o.X0 == m.X0 && o.Z0 == m.Z0 && o.W == m.W && o.H == m.H) return true;
                    }
                return false;
            }
            if (w != null)
                for (int i = 0; i < w.Machines.Count; i++)
                {
                    MachineInfo m = w.Machines[i];
                    if (Own(m)) continue;
                    for (int x = m.X0; x < m.X0 + m.W; x++)
                    {
                        for (int z = m.Z0; z < m.Z0 + m.H; z++) work.MachineCells.Add(new Cell(x, z));
                        if (m.Kind == MachineKind.Lamp) work.MachineCells.Add(new Cell(x, m.Z0 + m.H));
                    }
                }
            bool OwnCell(Cell c)
            {
                if (own != null)
                    for (int i = 0; i < own.Count; i++) if (own[i].Contains(c)) return true;
                return false;
            }
            bool Blocked(Cell c) => !OwnCell(c)
                && (!w.IsWalkable(c) || w.IsFurniture(c) || work.MachineCells.Contains(c));
            string groundWhy = null;
            bool GroundNo(string reason, V2 q)
            {
                if (trace != null) groundWhy = reason + " at " + q;
                return false;
            }
            bool Clear(V2 q)
            {
                if (extraClear != null && !extraClear(q)) return GroundNo("fitting-keep-off", q);
                if (w != null && w.IsDoor(q.Floor) && !doors.Contains(q.Floor)) return GroundNo("new-door", q);
                return true;
            }
            Func<V2, bool> clearPoint = Clear;
            bool SegmentClear(V2 a, V2 b)
            {
                // Keep fitting and doorway checks through every crossed cell.
                if (!RepairSegmentClear(null, a, b, clearPoint)) return false;
                if (w == null) return true;
                double reach = LayParams.RC;
                int x0 = (int)Math.Floor(Math.Min(a.X, b.X) - reach);
                int x1 = (int)Math.Floor(Math.Max(a.X, b.X) + reach);
                int z0 = (int)Math.Floor(Math.Min(a.Z, b.Z) - reach);
                int z1 = (int)Math.Floor(Math.Max(a.Z, b.Z) + reach);
                for (int x = x0; x <= x1; x++)
                    for (int z = z0; z <= z1; z++)
                    {
                        var c = new Cell(x, z);
                        if (!Blocked(c)) continue;
                        if (!work.ClearanceFloors.TryGetValue(c, out double floor))
                        {
                            floor = work.WindowGrid.CellClearance(c, reach);
                            work.ClearanceFloors.Add(c, floor);
                        }
                        if (RepairCellSegmentDistance(a, b, c) < floor - 1e-6)
                            return GroundNo("span-clearance " + c, (a + b) * 0.5);
                    }
                return true;
            }
            double ObstacleDistance(V2 q)
            {
                if (w == null) return 0.5;
                double best = 0.5;
                int x0 = (int)Math.Floor(q.X - 0.5), x1 = (int)Math.Floor(q.X + 0.5);
                int z0 = (int)Math.Floor(q.Z - 0.5), z1 = (int)Math.Floor(q.Z + 0.5);
                for (int x = x0; x <= x1; x++)
                    for (int z = z0; z <= z1; z++)
                    {
                        var c = new Cell(x, z);
                        if (Blocked(c)) best = Math.Min(best, RepairCellPointDistance(q, c));
                    }
                return best;
            }
            List<V2> P = pts;
            List<V2> stuck = work.Stuck;
            stuck.Clear();
            bool rescue = bowProfile != 0;
            int verifyLimit = rescue ? 32 : RepairVerifyLimit;
            int offsetLimit = rescue ? 432 : RepairOffsetLimit;
            int sampled = 0, verified = 0, offsetTried = 0;
            for (int guard = 0; guard < 12; guard++)
            {
                double[] cum = RepairCum(P, ref work.Cum);
                double L = cum[P.Count - 1];
                double S = 0;
                for (int i = 0; i < faults.Count; i++)
                {
                    double s = faults[i];
                    if (s <= pinA || s >= L - pinB) continue;
                    V2 at = RepairAt(P, cum, s);
                    bool blocked = false;
                    for (int k = 0; k < stuck.Count; k++)
                        if (V2.Dist(stuck[k], at) < 0.12) { blocked = true; break; }
                    if (!blocked) { S = s; break; }
                }
                if (S == 0) return P;
                V2 fault = RepairAt(P, cum, S);
                double windowLo = pinA, windowHi = L - pinB;
                if (approachBounds != null)
                {
                    var bounds = approachBounds(P, cum, S);
                    windowLo = Math.Max(windowLo, bounds.Lo);
                    windowHi = Math.Min(windowHi, bounds.Hi);
                }
                int ia = 1, ib = P.Count - 2;
                while (ia < P.Count - 2 && (cum[ia] < windowLo || !Clear(P[ia]))) ia++;
                while (ib > 1 && (cum[ib] > windowHi || !Clear(P[ib]))) ib--;
                if (ib - ia < 2 || cum[ia] >= S || cum[ib] <= S)
                {
                    trace?.Invoke("at " + fault + " no clear window between protected poses");
                    stuck.Add(fault);
                    continue;
                }
                List<V2> best = null, partialBest = null;
                List<CordTie> bestTies = null, partialTies = null;
                double partialGain = 0;
                var why = trace == null ? null : new Dictionary<string, int>();
                var firstReasons = trace == null ? null : new HashSet<string>();
                string attempt = null;
                void No(string reason)
                {
                    if (why != null) why[reason] = why.TryGetValue(reason, out int count) ? count + 1 : 1;
                    if (firstReasons != null && firstReasons.Add(attempt))
                        trace("try " + attempt + " first=" + reason);
                }
                double rodNow = CordShapeAudit.LongestRod(P, out _);
                work.Windows.Clear();
                // One defect produces many neighbouring fault samples. Try replacing that
                // whole cluster before spending the unchanged budgets on its fragments.
                double faultEnd = S;
                for (int k = 0; k < faults.Count; k++)
                {
                    if (faults[k] < S) continue;
                    if (faults[k] - faultEnd > 0.35) break;
                    faultEnd = faults[k];
                }
                for (int wi = -1; wi < RepairWindows.Length; wi++)
                {
                    if (sampled >= RepairSampleLimit || verified >= verifyLimit || offsetTried >= offsetLimit) break;
                    var window = wi < 0
                        ? (A: 0.4, B: Math.Min(5.6, faultEnd - S + 0.4))
                        : RepairWindows[wi];
                    if (trace != null)
                        attempt = "w" + (wi + 1) + "("
                            + window.A.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture) + ","
                            + window.B.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture) + ")";
                    int a = Array.BinarySearch(cum, 0, P.Count, S - window.A);
                    int b = Array.BinarySearch(cum, 0, P.Count, S + window.B);
                    if (a < 0) a = ~a - 1;
                    if (b < 0) b = ~b;
                    a = Math.Max(ia, a); b = Math.Min(ib, b);
                    // Original obstacle clearance is legal at either join. Only a fitting
                    // or a new doorway requires extending to another original vertex.
                    while (a > ia && !Clear(P[a])) a--;
                    while (b < ib && !Clear(P[b])) b++;
                    if (trace != null)
                        attempt += "@" + cum[a].ToString("0.000", System.Globalization.CultureInfo.InvariantCulture)
                            + ".." + cum[b].ToString("0.000", System.Globalization.CultureInfo.InvariantCulture);
                    if (b - a < 2 || cum[a] >= S || cum[b] <= S) { No("pin/window"); continue; }
                    if (work.Windows.Contains((a, b))) { No("duplicate-window"); continue; }
                    work.Windows.Add((a, b));
                    if (!Clear(P[a]) || !Clear(P[b])) { No(groundWhy ?? "blocked-join"); continue; }
                    if (RepairTied(ties, cum[a], cum[b])) { No("tie"); continue; }
                    int sampleEnd = Math.Min(RepairSampleLimit, sampled + RepairWindowSamples);
                    int verifyEnd = Math.Min(verifyLimit, verified + (rescue ? 6 : RepairWindowVerifies));
                    int offsetEnd = Math.Min(offsetLimit, offsetTried + (rescue ? 54 : RepairWindowOffsets));
                    RepairQuality beforeQuality = null;
                    V2 ta = P[a] - P[a - 1], tb = P[b + 1] - P[b];
                    if (ta.Len < 1e-9 || tb.Len < 1e-9) { No("pose"); continue; }
                    double ha = Math.Atan2(ta.Z, ta.X), hb = Math.Atan2(tb.Z, tb.X), old = cum[b] - cum[a];
                    int oldCrossings = CordBuilder.CrossingsOf(P, a, b);
                    work.WindowGrid.Set(P, a, b);
                    work.ClearanceFloors.Clear();
                    bool Near(V2 q) => work.WindowGrid.Distance(q, 0.5) <= 0.5;
                    // Prefer the side with more obstacle clearance. SegmentClear compares
                    // exact continuous distances against this original window, per obstacle cell.
                    V2 axis = P[b] - P[a];
                    V2 normal = axis.Len > 1e-9 ? axis.Norm().Perp : new V2(-Math.Sin(ha), Math.Cos(ha));
                    double plus = ObstacleDistance(fault + normal * 0.12);
                    double minus = ObstacleDistance(fault - normal * 0.12);
                    int away = plus > minus + 1e-6 ? 1 : minus > plus + 1e-6 ? -1 : 0;
                    double[] offsets = rescue ? RepairRescueOffsets : away == 0 ? RepairOffsets : RepairAwayOffsets;
                    string windowAttempt = attempt;
                    foreach (double r in rescue ? RepairRescueRadii : RepairRadii)
                    {
                        if (trace != null)
                            attempt = windowAttempt + "/r=" + r.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture);
                        List<Dubins.Path> paths = Dubins.All(P[a], ha, P[b], hb, r, work.Paths);
                        paths.Sort(RepairPathOrder);
                        if (paths.Count == 0) No("no-path");
                        foreach (Dubins.Path dp in paths)
                        {
                            if (dp.Turning > 2.5 * Math.PI || dp.Len > old + 0.8) { No("turn/length"); continue; }
                            if (sampled >= sampleEnd || verified >= verifyEnd || offsetTried >= offsetEnd)
                            {
                                No("window-budget");
                                break;
                            }
                            sampled++;
                            List<V2> basePatch = Dubins.Sample(P[a], ha, dp, RepairStep, work.BasePatch);
                            if (basePatch.Count == 0 || V2.Dist(basePatch[basePatch.Count - 1], P[b]) > 1e-6) { No("endpoint"); continue; }
                            basePatch.Insert(0, P[a]);
                            int count = 1;
                            for (int k = 1; k < basePatch.Count; k++)
                                if (V2.Dist(basePatch[count - 1], basePatch[k]) > 1e-8) basePatch[count++] = basePatch[k];
                            if (count < basePatch.Count) basePatch.RemoveRange(count, basePatch.Count - count);
                            if (basePatch.Count < 2) { No("empty"); continue; }
                            basePatch[basePatch.Count - 1] = P[b];
                            string pathAttempt = attempt;
                            for (int oi = 0; oi < offsets.Length && offsetTried < offsetEnd; oi++)
                            {
                            offsetTried++;
                            double offset = offsets[oi] * (away == 0 ? 1 : away);
                            if (trace != null)
                                attempt = pathAttempt + "/side=" + offset.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture);
                            List<V2> patch = OffsetRepairPatch(basePatch, ha, offset, work.Patch, bowProfile);
                            bool near = true;
                            for (int k = 0; k < patch.Count && near; k++) near = Near(patch[k]);
                            if (!near) { No("stray"); continue; }
                            bool clear = true;
                            for (int k = 1; k < patch.Count && clear; k++)
                                clear = SegmentClear(patch[k - 1], patch[k]);
                            if (!clear) { No(groundWhy ?? "ground/clearance"); continue; }
                            if (verified >= verifyEnd)
                            {
                                No("verification-limit");
                                break;
                            }
                            List<V2> Q = work.Candidate;
                            Q.Clear();
                            for (int k = 0; k <= a; k++) Q.Add(P[k]);
                            for (int k = 1; k < patch.Count; k++) Q.Add(patch[k]);
                            for (int k = b + 1; k < P.Count; k++) Q.Add(P[k]);
                            if (approachClear != null && !approachClear(Q)) { No("slide-under-approach"); continue; }
                            verified++;
                            if (CordBuilder.CrossingsOf(Q, a, a + patch.Count - 1) > oldCrossings) { No("crossing"); continue; }
                            double delta = Geo.Length(patch) - old;
                            List<CordTie> qt = null;
                            if (ties != null)
                            {
                                qt = work.Ties;
                                qt.Clear();
                                qt.AddRange(ties);
                            }
                            if (qt != null)
                                for (int k = 0; k < qt.Count; k++)
                                {
                                    CordTie t = qt[k];
                                    if (t.S0 > cum[b]) { t.S0 += delta; t.S1 += delta; qt[k] = t; }
                                }
                            double patchEnd = cum[b] + delta;
                            bool RetainedFault(double s)
                            {
                                if (s > cum[a] + RepairStep && s < patchEnd - RepairStep) return false;
                                double before = s <= cum[a] ? s : s - delta;
                                for (int k = 0; k < faults.Count; k++)
                                    if (Math.Abs(faults[k] - before) <= 4 * RepairStep) return true;
                                return false;
                            }
                            // Only this window and its joins can change. Extra context contains
                            // every measurement span; distant cord need not be sampled per candidate.
                            RepairQuality afterQuality = work.AfterQuality;
                            afterQuality.Clear();
                            List<double> remaining = CurvatureFaults(Q, qt, work.Remaining,
                                cum[a] - 1.3, patchEnd + 1.3,
                                measure: (kind, s, value) => afterQuality.Add(kind, s, value, cum[a], patchEnd),
                                radiusTarget: radiusTarget);
                            bool newFault = false;
                            for (int k = 0; k < remaining.Count; k++)
                            {
                                double s = remaining[k];
                                if (s >= cum[a] - 0.65 && s <= patchEnd + 0.65 && !RetainedFault(s))
                                {
                                    newFault = true;
                                    break;
                                }
                            }
                            // Neither partial improvement nor a retained join bypasses this pass's radius target.
                            if (!afterQuality.RadiusClear) { No("radius-margin"); continue; }
                            beforeQuality ??= MeasureRepairQuality(P, ties, cum[a], cum[b], radiusTarget);
                            if (!afterQuality.NoWorseThan(beforeQuality)) { No("worse-fault/join"); continue; }
                            double gain = beforeQuality.Worst - afterQuality.Worst;
                            // Prefer a clean patch. A partial patch must reduce the worst
                            // normalized fault by at least 0.01 and worsen no fault peak.
                            if (newFault && gain <= 0.01) { No("fault/join"); continue; }
                            double rodAfter = CordShapeAudit.LongestRod(Q, out _);
                            if (rodAfter >= CordShapeAudit.RodLen && rodAfter > rodNow + 1e-6) { No("rod"); continue; }
                            if (newFault)
                            {
                                if (gain > partialGain)
                                {
                                    partialBest = new List<V2>(Q);
                                    partialTies = qt == null ? null : new List<CordTie>(qt);
                                    partialGain = gain;
                                }
                                continue;
                            }
                            best = new List<V2>(Q);
                            bestTies = qt == null ? null : new List<CordTie>(qt);
                            if (trace != null) trace("try " + attempt + " accepted");
                            break;
                            }
                            // Rescue spends its samples across radii instead of exhausting
                            // them on several words at the first radius.
                            if (best != null || rescue) break;
                        }
                        if (best != null || sampled >= sampleEnd || verified >= verifyEnd || offsetTried >= offsetEnd) break;
                    }
                    if (best != null) break;
                }
                if (best == null && partialBest != null)
                {
                    best = partialBest;
                    bestTies = partialTies;
                    trace?.Invoke("partial improvement " + partialGain.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
                }
                if (trace != null)
                    trace("at " + fault + " S " + S.ToString("0.000") + "/" + L.ToString("0.000")
                        + " mutable " + cum[ia].ToString("0.000") + ".." + cum[ib].ToString("0.000")
                        + (best == null ? " stuck " : " repaired ")
                        + string.Join(" ", why.Select(kv => kv.Key + ":" + kv.Value)));
                if (best == null) stuck.Add(fault);
                else
                {
                    P = best;
                    if (ties != null) { ties.Clear(); ties.AddRange(bestTies); }
                    CurvatureFaults(P, ties, faults, radiusTarget: radiusTarget);
                    stuck.Clear();
                }
                if (sampled >= RepairSampleLimit || verified >= verifyLimit || offsetTried >= offsetLimit)
                {
                    trace?.Invoke("call budget; remaining fault samples " + faults.Count);
                    return P;
                }
            }
            trace?.Invoke("round limit 12; remaining fault samples " + faults.Count);
            return P;
        }


        // Every profile preserves endpoint positions and analytic tangents.
        // Profile 0 also preserves endpoint curvature. Rescue profiles act earlier
        // near the joins; actual sampled curvature and clearance are still checked.
        private static List<V2> OffsetRepairPatch(List<V2> pts, double heading, double amount, List<V2> into,
                                                  int profile = 0)
        {
            into.Clear();
            if (amount == 0)
            {
                into.AddRange(pts);
                return into;
            }
            double length = Geo.Length(pts), s = 0;
            V2 axis = pts[pts.Count - 1] - pts[0];
            V2 normal = axis.Len > 1e-9 ? axis.Norm().Perp : new V2(-Math.Sin(heading), Math.Cos(heading));
            for (int i = 0; i < pts.Count; i++)
            {
                if (i > 0) s += V2.Dist(pts[i - 1], pts[i]);
                if (i == 0 || i == pts.Count - 1)
                {
                    into.Add(pts[i]);
                    continue;
                }
                double u = length > 1e-12 ? s / length : 0;
                double v = u * (1 - u);
                double bow = profile == 0 ? 64 * v * v * v : 16 * v * v;
                if (profile == 2) bow *= 2 * (1 - u);
                else if (profile == 3) bow *= 2 * u;
                into.Add(pts[i] + normal * (amount * bow));
            }
            return into;
        }

        internal static bool Cross(V2 a, V2 b, V2 c, V2 d, out V2 at)
        {
            at = default(V2);
            double rx = b.X - a.X, rz = b.Z - a.Z, sx = d.X - c.X, sz = d.Z - c.Z, den = rx * sz - rz * sx;
            if (Math.Abs(den) < 1e-12) return false;
            double t = ((c.X - a.X) * sz - (c.Z - a.Z) * sx) / den, u = ((c.X - a.X) * rz - (c.Z - a.Z) * rx) / den;
            if (t < 0 || t > 1 || u < 0 || u > 1) return false;
            at = new V2(a.X + rx * t, a.Z + rz * t);
            return true;
        }

        /// <summary>The lab's radius, opposite-peak saw and signed V-turn tests, sampled on the original polyline.
        /// Tied-loop ranges are intentional strain relief and excluded. Diagnostic summaries omit those exclusions.</summary>
        internal static List<double> CurvatureFaults(List<V2> pts, List<CordTie> ties = null, List<double> into = null,
                                                     double from = RepairPin, double to = double.MaxValue,
                                                     Action<string, double> report = null,
                                                     Action<string, double, double> measure = null,
                                                     double radiusTarget = RepairRadiusTarget)
        {
            List<double> faults = into ?? new List<double>();
            faults.Clear();
            if (pts == null || pts.Count < 3) return faults;
            RepairScratch work = RepairWork;
            double[] cum = RepairCum(pts, ref work.ScanCum);
            double lo = Math.Max(RepairPin, from), hi = Math.Min(cum[pts.Count - 1] - RepairPin, to);
            if (hi <= lo) return faults;
            int[] cursors = work.Cursors;
            Array.Clear(cursors, 0, cursors.Length);
            V2 At(double s, int slot)
            {
                int i = cursors[slot];
                while (i < pts.Count - 2 && cum[i + 1] < s) i++;
                cursors[slot] = i;
                double len = cum[i + 1] - cum[i];
                double t = len > 1e-12 ? Math.Max(0, Math.Min(1, (s - cum[i]) / len)) : 0;
                return pts[i] + (pts[i + 1] - pts[i]) * t;
            }
            void Add(double a, double b, string kind, double severity)
            {
                if (a < lo - 1e-9 || b > hi + 1e-9) return;
                if (RepairTied(ties, a, b)) return;
                double s = (a + b) * 0.5;
                faults.Add(s);
                report?.Invoke(kind, s);
                measure?.Invoke(kind, s, severity);
            }
            double? Turn(double s, double h, int slot)
            {
                if (s - h < lo - 1e-9 || s + h > hi + 1e-9) return null;
                V2 a = At(s - h, slot), b = At(s, slot + 1), c = At(s + h, slot + 2);
                V2 u = b - a, v = c - b;
                if (u.Len < 1e-10 || v.Len < 1e-10) return null;
                return SignedTurnDeg(u, v);
            }
            // Check original vertices too: span averages can hide a short tight bend.
            for (int i = 1; i < pts.Count - 1; i++)
            {
                if (cum[i - 1] < lo - 1e-9 || cum[i + 1] > hi + 1e-9
                    || RepairTied(ties, cum[i - 1], cum[i + 1])) continue;
                double radius = Radius(pts[i - 1], pts[i], pts[i + 1]);
                if (radius < radiusTarget)
                    Add(cum[i], cum[i], "radius", radiusTarget / radius);
            }
            int n = Math.Max(0, (int)Math.Floor((hi - lo) / RepairStep + 1e-9));
            var lobes = work.Lobes;
            var tangents = work.Tangents;
            lobes.Clear();
            tangents.Clear();
            for (int i = 0; i <= n; i++)
            {
                // Fixed spacing: a length change cannot move samples before the repair.
                double s = lo + RepairStep * i;
                for (int scale = 0; scale < RepairScales.Length; scale++)
                {
                    double h = RepairScales[scale];
                    double? turn = Turn(s, h, 3 * scale);
                    if (turn.HasValue && Math.Abs(turn.Value) * Math.PI / 180 / h > 1 / radiusTarget)
                        Add(s - h, s + h, "radius", Math.Abs(turn.Value) * Math.PI / 180 / h * radiusTarget);
                }
                double? saw = Turn(s, 0.10, 9);
                if (saw.HasValue && Math.Abs(saw.Value) >= 7.5)
                {
                    int sign = Math.Sign(saw.Value);
                    double peak = Math.Abs(saw.Value);
                    if (lobes.Count > 0 && lobes[lobes.Count - 1].Sign == sign && s - lobes[lobes.Count - 1].Last <= 0.45)
                    {
                        var lobe = lobes[lobes.Count - 1];
                        lobe.Last = s;
                        if (peak > lobe.Peak) { lobe.Peak = peak; lobe.S = s; }
                        lobes[lobes.Count - 1] = lobe;
                    }
                    else lobes.Add((sign, peak, s, s));
                }
                if (s - 0.04 >= lo - 1e-9 && s + 0.04 <= hi + 1e-9)
                {
                    V2 d = At(s + 0.04, 13) - At(s - 0.04, 12);
                    if (d.Len > 1e-10)
                    {
                        double heading = tangents.Count == 0 ? 0 : tangents[tangents.Count - 1].Heading + SignedTurnDeg(tangents[tangents.Count - 1].Dir, d);
                        tangents.Add((s, d, heading));
                    }
                }
            }
            for (int i = 0; i < lobes.Count; i++)
                for (int j = i + 1; j < lobes.Count; j++)
                {
                    if (lobes[j].S - lobes[i].S > 0.45) break;
                    if (lobes[i].Sign != lobes[j].Sign && Math.Min(lobes[i].Peak, lobes[j].Peak) >= 24)
                        Add(lobes[i].S - 0.10, lobes[j].S + 0.10, "saw", Math.Min(lobes[i].Peak, lobes[j].Peak) / 24.0);
                }
            if (work.MinHeading.Length < tangents.Count)
            {
                int size = Math.Max(tangents.Count, Math.Max(64, work.MinHeading.Length * 2));
                Array.Resize(ref work.MinHeading, size);
                Array.Resize(ref work.MaxHeading, size);
            }
            int[] minHeading = work.MinHeading, maxHeading = work.MaxHeading;
            int first = 0, minFirst = 0, minEnd = 0, maxFirst = 0, maxEnd = 0;
            for (int j = 0; j < tangents.Count; j++)
            {
                while (tangents[j].S - tangents[first].S > 0.60 + 1e-9) first++;
                while (minFirst < minEnd && minHeading[minFirst] < first) minFirst++;
                while (maxFirst < maxEnd && maxHeading[maxFirst] < first) maxFirst++;
                double heading = tangents[j].Heading;
                while (minFirst < minEnd && tangents[minHeading[minEnd - 1]].Heading >= heading) minEnd--;
                while (maxFirst < maxEnd && tangents[maxHeading[maxEnd - 1]].Heading <= heading) maxEnd--;
                minHeading[minEnd++] = j;
                maxHeading[maxEnd++] = j;
                // Most neighbourhoods cannot contain a V-turn. Only enumerate pairs
                // when an extremum proves one possible; preserve every original hit.
                if (heading - tangents[minHeading[minFirst]].Heading <= 155
                    && tangents[maxHeading[maxFirst]].Heading - heading <= 155) continue;
                for (int i = first; i < j; i++)
                    if (Math.Abs(heading - tangents[i].Heading) > 155)
                        Add(tangents[i].S - 0.04, tangents[j].S + 0.04, "V-turn", Math.Abs(heading - tangents[i].Heading) / 155.0);
            }
            faults.Sort();
            int count = 0;
            for (int i = 0; i < faults.Count; i++)
                if (count == 0 || Math.Abs(faults[i] - faults[count - 1]) > 1e-9)
                    faults[count++] = faults[i];
            if (count < faults.Count) faults.RemoveRange(count, faults.Count - count);
            return faults;
        }

        /// <summary>Diagnostic only: group neighbouring fault samples by type, retaining
        /// each group's arc range and an actual fault position. No tied ranges are hidden.</summary>
        internal static string CurvatureFaultSummary(List<V2> pts)
        {
            var hits = new List<(string Kind, double S)>();
            CurvatureFaults(pts, report: (kind, s) => hits.Add((kind, s)));
            if (hits.Count == 0) return "";
            hits.Sort((a, b) =>
            {
                int kind = StringComparer.Ordinal.Compare(a.Kind, b.Kind);
                return kind != 0 ? kind : a.S.CompareTo(b.S);
            });
            double[] cum = Geo.CumLen(pts);
            var text = new System.Text.StringBuilder();
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            for (int i = 0; i < hits.Count;)
            {
                var first = hits[i];
                double last = first.S;
                int j = i + 1;
                while (j < hits.Count && hits[j].Kind == first.Kind && hits[j].S - last <= 0.15)
                    last = hits[j++].S;
                V2 q = RepairAt(pts, cum, first.S);
                if (text.Length > 0) text.Append("; ");
                text.Append(first.Kind).Append(" at (")
                    .Append(q.X.ToString("0.000", inv)).Append(',')
                    .Append(q.Z.ToString("0.000", inv)).Append(") S=")
                    .Append(first.S.ToString("0.000", inv)).Append("..")
                    .Append(last.ToString("0.000", inv));
                i = j;
            }
            return text.ToString();
        }

        private static double Radius(V2 a, V2 b, V2 c)
        {
            double cross = Math.Abs((b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X));
            return cross < 1e-12 ? double.MaxValue : V2.Dist(a, b) * V2.Dist(b, c) * V2.Dist(c, a) / (2 * cross);
        }

        private static V2 RepairAt(List<V2> pts, double[] cum, double s)
        {
            int i = Array.BinarySearch(cum, 0, pts.Count, s);
            if (i >= 0) return pts[i];
            i = Math.Max(0, Math.Min(pts.Count - 2, ~i - 1));
            double len = cum[i + 1] - cum[i];
            double t = len > 1e-12 ? Math.Max(0, Math.Min(1, (s - cum[i]) / len)) : 0;
            return pts[i] + (pts[i + 1] - pts[i]) * t;
        }

        /// <summary>Check segment interiors as well as vertices. Split at every grid boundary so even a tiny corner
        /// crossing visits its cell; clearance samples have a half-step margin between them.
        /// A supplied clearance policy handles intentional own-machine runs and existing narrow gaps.</summary>
        internal static bool RepairSegmentClear(CordWorld w, V2 a, V2 b, Func<V2, bool> clear = null,
                                                Func<V2, double, bool> clearance = null)
        {
            V2 d = b - a;
            double len = d.Len;
            bool Ok(V2 q, double margin) => (clear == null || clear(q))
                && (clearance != null ? clearance(q, margin)
                    : w == null || (w.IsWalkable(q.Floor) && w.Clearance(q) >= LayParams.RC + margin));
            if (!Ok(a, 0) || !Ok(b, 0)) return false;
            // Walk grid crossings directly; candidate arcs call this for every segment.
            double tx = double.PositiveInfinity, tz = double.PositiveInfinity;
            double dx = double.PositiveInfinity, dz = double.PositiveInfinity;
            if (Math.Abs(d.X) > 1e-12)
            {
                dx = 1 / Math.Abs(d.X);
                double edge = d.X > 0 ? Math.Floor(a.X) + 1 : Math.Ceiling(a.X) - 1;
                tx = (edge - a.X) / d.X;
            }
            if (Math.Abs(d.Z) > 1e-12)
            {
                dz = 1 / Math.Abs(d.Z);
                double edge = d.Z > 0 ? Math.Floor(a.Z) + 1 : Math.Ceiling(a.Z) - 1;
                tz = (edge - a.Z) / d.Z;
            }
            double start = 0;
            while (start < 1)
            {
                double end = Math.Min(1, Math.Min(tx, tz));
                double span = Math.Max(0, end - start);
                int n = Math.Max(1, (int)Math.Ceiling(len * span / 0.01));
                double dt = span / n;
                for (int k = 0; k < n; k++)
                    if (!Ok(a + d * (start + (k + 0.5) * dt), len * dt * 0.5)) return false;
                if (end >= 1) break;
                if (tx <= end + 1e-12) tx += dx;
                if (tz <= end + 1e-12) tz += dz;
                start = end;
            }
            return true;
        }

        // ---------------------------------------------------------------- an end that comes round, never hooks
        /// <summary>The shortest way from one pose to another that turns no tighter than a radius (Dubins 1957; the six words after A. Walker's dubins.c). Headings are radians from +X toward +Z;
        /// L turns that way, R the other. A path's three numbers are its segments' lengths in radii.</summary>
        internal static class Dubins
        {
            internal struct Path
            {
                public int Word;
                public double T, P, Q, R;
                public double Len => (T + P + Q) * R;
                /// <summary>Radians turned in all.</summary>
                public double Turning => T + Q + (Word >= 4 ? P : 0);
            }
            // LSL, LSR, RSL, RSR, RLR, LRL
            private static readonly string[] Words = { "LSL", "LSR", "RSL", "RSR", "RLR", "LRL" };
            private static double Mod2Pi(double a) { a %= 2 * Math.PI; return a < 0 ? a + 2 * Math.PI : a; }

            internal static List<Path> All(V2 a, double ha, V2 b, double hb, double r, List<Path> into = null)
            {
                List<Path> o = into ?? new List<Path>(6);
                o.Clear();
                double dx = b.X - a.X, dz = b.Z - a.Z, D = Math.Sqrt(dx * dx + dz * dz), d = D / r;
                double th = D > 1e-9 ? Mod2Pi(Math.Atan2(dz, dx)) : 0, al = Mod2Pi(ha - th), be = Mod2Pi(hb - th);
                double sa = Math.Sin(al), sb = Math.Sin(be), ca = Math.Cos(al), cb = Math.Cos(be), cab = Math.Cos(al - be), d2 = d * d;
                void Add(int word, double t, double p, double q) => o.Add(new Path { Word = word, T = t, P = p, Q = q, R = r });
                double ps = 2 + d2 - 2 * cab + 2 * d * (sa - sb);                     // LSL
                if (ps >= 0) { double t1 = Math.Atan2(cb - ca, d + sa - sb); Add(0, Mod2Pi(t1 - al), Math.Sqrt(ps), Mod2Pi(be - t1)); }
                ps = -2 + d2 + 2 * cab + 2 * d * (sa + sb);                            // LSR
                if (ps >= 0) { double p = Math.Sqrt(ps), t0 = Math.Atan2(-ca - cb, d + sa + sb) - Math.Atan2(-2.0, p); Add(1, Mod2Pi(t0 - al), p, Mod2Pi(t0 - be)); }
                ps = -2 + d2 + 2 * cab - 2 * d * (sa + sb);                            // RSL
                if (ps >= 0) { double p = Math.Sqrt(ps), t0 = Math.Atan2(ca + cb, d - sa - sb) - Math.Atan2(2.0, p); Add(2, Mod2Pi(al - t0), p, Mod2Pi(be - t0)); }
                ps = 2 + d2 - 2 * cab + 2 * d * (sb - sa);                             // RSR
                if (ps >= 0) { double t1 = Math.Atan2(ca - cb, d - sa + sb); Add(3, Mod2Pi(al - t1), Math.Sqrt(ps), Mod2Pi(t1 - be)); }
                double c = (6 - d2 + 2 * cab + 2 * d * (sa - sb)) / 8;                 // RLR
                if (Math.Abs(c) <= 1) { double phi = Math.Atan2(ca - cb, d - sa + sb), p = Mod2Pi(2 * Math.PI - Math.Acos(c)), t = Mod2Pi(al - phi + Mod2Pi(p / 2)); Add(4, t, p, Mod2Pi(al - be - t + p)); }
                c = (6 - d2 + 2 * cab + 2 * d * (sb - sa)) / 8;                        // LRL
                if (Math.Abs(c) <= 1) { double phi = Math.Atan2(ca - cb, d + sa - sb), p = Mod2Pi(2 * Math.PI - Math.Acos(c)), t = Mod2Pi(-al - phi + p / 2); Add(5, t, p, Mod2Pi(be - al - t + p)); }
                return o;
            }

            /// <summary>The path's points from <paramref name="a"/> (left out) to its end, <paramref name="step"/> cells apart.</summary>
            internal static List<V2> Sample(V2 a, double ha, Path p, double step, List<V2> into = null)
            {
                List<V2> o = into ?? new List<V2>();
                o.Clear();
                string w = Words[p.Word];
                double x = a.X, z = a.Z, h = ha;
                for (int sgi = 0; sgi < 3; sgi++)
                {
                    char k = w[sgi];
                    double len = (sgi == 0 ? p.T : sgi == 1 ? p.P : p.Q) * p.R;
                    int m = Math.Max(1, (int)Math.Ceiling(len / step));
                    double ds = len / m;
                    for (int i = 0; i < m; i++)
                    {
                        if (k == 'S') { x += Math.Cos(h) * ds; z += Math.Sin(h) * ds; }
                        else
                        {
                            double turn = (k == 'L' ? 1 : -1) * ds / p.R, h1 = h + turn;
                            // along the arc exactly: the chord at the mean heading
                            double chord = 2 * p.R * Math.Sin(Math.Abs(turn) / 2), hm = h + turn / 2;
                            x += Math.Cos(hm) * chord; z += Math.Sin(hm) * chord;
                            h = h1;
                        }
                        if (len > 1e-9) o.Add(new V2(x, z));
                    }
                }
                return o;
            }
        }

        /// <summary>The radii an end tries to come round at, widest first (cells): <see cref="FairR"/> and wider is never read as a sharp bend.</summary>
        public static readonly double[] ArriveRadii = { 0.78, 0.62, 0.5, 0.4, 0.3 };

        /// <summary>Lay one end of a strand so it comes round to its fitting at no tighter than <see cref="ArriveRadii"/> (a Dubins path from a point on the laid cord to the start of the
        /// fitting's straight bit), never the hook the old approach drew in the last half cell when the cord came from the wrong side. Of every cut back along the cord (from half a cell
        /// to six tenths of it, at most three cells) the one that turns least is kept, so a cord that ran on past its plug and wrapped round to it is cut where it first came by.
        /// <paramref name="clear"/> says where a point may lie. Null when no clear path is found at any radius; <paramref name="turning"/> is that path's turn, radians.</summary>
        internal static List<V2> ArriveRound(List<V2> P, bool atEnd, V2 target, V2 arrive, double straight, Func<V2, bool> clear, out double turning, double keepFar = 0.5)
        {
            turning = double.MaxValue;
            var Q = new List<V2>(P);
            if (!atEnd) Q.Reverse();
            if (Q.Count < 4) return null;
            arrive = arrive.Norm();
            double[] cum = Geo.CumLen(Q);
            double L = cum[cum.Length - 1];
            V2 E = target - arrive * straight;
            double he = Math.Atan2(arrive.Z, arrive.X);
            // a short lead (a junction box right beside its machine) may be laid again whole, from just off its other end
            // never into the other end's own fitted run (<paramref name="keepFar"/>: a cut end's straight live run or limp curl, another fitting's straight bit)
            double sMin = Math.Min(0.5, 0.35 * L), sMax = Math.Min(3.0, Math.Min(Math.Max(0.6 * L, L - 0.3), L - keepFar));
            if (sMax < sMin) return null;
            foreach (double r in ArriveRadii)
            {
                List<V2> best = null;
                double bestCost = double.MaxValue;
                int bestJ = -1;
                for (double back = sMin; back <= sMax + 1e-9; back += 0.1)
                {
                    int j = Array.BinarySearch(cum, L - back);
                    if (j < 0) j = ~j;
                    j = Math.Max(1, Math.Min(j, Q.Count - 2));
                    V2 a = Q[j], t = Q[j] - Q[j - 1];
                    if (t.Len < 1e-9) continue;
                    double ha = Math.Atan2(t.Z, t.X);
                    foreach (Dubins.Path dp in Dubins.All(a, ha, E, he, r))
                    {
                        // a path that turns little reads as the cord coming in; one that loops round to get there is a coil it did not have
                        double cost = dp.Turning + 0.15 * Math.Abs(dp.Len - back);
                        if (cost >= bestCost || dp.Turning > 1.5 * Math.PI) continue;
                        List<V2> pts = Dubins.Sample(a, ha, dp, 0.05);
                        if (pts.Any(q => !clear(q))) continue;
                        best = pts; bestCost = cost; bestJ = j; turning = dp.Turning;
                    }
                }
                if (best == null) continue;
                var R = Q.GetRange(0, bestJ + 1);
                R.AddRange(best);
                int ns = Math.Max(1, (int)Math.Round(straight / 0.05));
                for (int q = 1; q <= ns; q++) R.Add(E + arrive * (straight * q / ns));
                R[R.Count - 1] = target;
                if (!atEnd) R.Reverse();
                return R;
            }
            turning = double.MaxValue;
            return null;
        }

        private const int PolishNeedleRounds = 6;
        private const double PolishNeedleReach = 0.4;

        private static List<V2> RoundFold(CordWorld w, List<V2> P, V2 at)
        {
            int i = P.IndexOf(at);
            double[] cum = Geo.CumLen(P);
            int a = i, b = i;
            while (a > 1 && cum[i] - cum[a] < UnfoldReach) a--;
            while (b < P.Count - 2 && cum[b] - cum[i] < UnfoldReach) b++;
            if (a < 1 || b > P.Count - 2 || a >= b) return null;
            V2 s = P[a], e = P[b], ts = (P[a] - P[a - 1]).Norm(), te = (P[b + 1] - P[b]).Norm();
            V2 gap = e - s, axis = ts - te;
            axis = axis.Len < 1e-6 ? ts : axis.Norm();
            V2 lat = gap.Len > 1e-6 ? gap.Norm() : axis.Perp;
            double flare = Math.Max(0, UnfoldFlare - gap.Len / 2), k = Math.Max(0.16, gap.Len * 0.6);
            V2 c1 = s + axis * k - lat * flare, c2 = e + axis * k + lat * flare;
            var bend = new List<V2>();
            const int n = 14;
            for (int q = 1; q < n; q++)
            {
                double t = q / (double)n, it = 1 - t;
                V2 pt = s * (it * it * it) + c1 * (3 * it * it * t) + c2 * (3 * it * t * t) + e * (t * t * t);
                if (w != null && !w.IsWalkable(pt.Floor)) return null;
                bend.Add(pt);
            }
            var o = new List<V2>(P.Count);
            o.AddRange(P.GetRange(0, a + 1));
            o.AddRange(bend);
            o.AddRange(P.GetRange(b, P.Count - b));
            return o;
        }

        /// <summary>The pairwise table per length class, over the cords of the given pieces (end-to-end edges only).</summary>
        public static List<ShapeClass> Table(IEnumerable<LaidPiece> pieces)
        {
            var byClass = new SortedDictionary<int, List<(string key, double[] s)>>();
            foreach (LaidPiece p in pieces)
            {
                if (p.EndA == null || p.Strands.Count == 0) continue;
                CordStrand s = p.Strands[0];
                if (s.Pts == null || s.Pts.Count < 4 || p.PathLen < 2) continue;
                int c = (int)Math.Round(p.PathLen / ClassWidth) * ClassWidth;
                if (!byClass.TryGetValue(c, out var l)) byClass[c] = l = new List<(string, double[])>();
                l.Add((p.EndA + "|" + p.EndB, Sample(s.Pts)));
            }
            var o = new List<ShapeClass>();
            foreach (var kv in byClass)
            {
                var t = new ShapeClass { Length = kv.Key, Cords = kv.Value.Count };
                double sum = 0;
                for (int i = 0; i < kv.Value.Count; i++)
                    for (int j = i + 1; j < kv.Value.Count; j++)
                    {
                        double d = Distance(kv.Value[i].s, kv.Value[j].s);
                        t.Pairs++;
                        sum += d;
                        if (d < TooAlikeBelow) t.TooAlike++;
                        if (d < t.MinDistance) { t.MinDistance = d; t.ClosestA = kv.Value[i].key; t.ClosestB = kv.Value[j].key; }
                    }
                t.MeanDistance = t.Pairs > 0 ? sum / t.Pairs : 0;
                o.Add(t);
            }
            return o;
        }
    }
}
