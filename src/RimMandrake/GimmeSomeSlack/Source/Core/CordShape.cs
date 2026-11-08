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

        private static double Radius(V2 a, V2 b, V2 c)
        {
            double cross = Math.Abs((b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X));
            return cross < 1e-12 ? double.MaxValue : V2.Dist(a, b) * V2.Dist(b, c) * V2.Dist(c, a) / (2 * cross);
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

            internal static List<Path> All(V2 a, double ha, V2 b, double hb, double r)
            {
                var o = new List<Path>();
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
            internal static List<V2> Sample(V2 a, double ha, Path p, double step)
            {
                var o = new List<V2>();
                string w = Words[p.Word];
                double x = a.X, z = a.Z, h = ha;
                double[] len = { p.T * p.R, p.P * p.R, p.Q * p.R };
                for (int sgi = 0; sgi < 3; sgi++)
                {
                    char k = w[sgi];
                    int m = Math.Max(1, (int)Math.Ceiling(len[sgi] / step));
                    double ds = len[sgi] / m;
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
                        if (len[sgi] > 1e-9) o.Add(new V2(x, z));
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
