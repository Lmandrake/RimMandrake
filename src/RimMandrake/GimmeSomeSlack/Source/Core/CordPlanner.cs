// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Port of nodal.plan / astar / _pull / round_corners (design §8.2.3).
using System;
using System.Collections.Generic;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public enum WaypointKind { Corner, Door, Knot, Via }

    public sealed class CordPlan
    {
        public List<V2> Points = new List<V2>();
        public List<KeyValuePair<V2, WaypointKind>> Waypoints = new List<KeyValuePair<V2, WaypointKind>>();
        /// <summary>False when A* found no walkable route between the endpoints (§8.2.3 "unroutable").</summary>
        public bool Ok = true;
        /// <summary>Dive-through (owner 2026-10-06): where the only route crosses a wall, rock, water or another building, the
        /// cord dives at the face it meets and resurfaces on the far side. Each span's InFace is Points[Index] and its OutFace
        /// Points[Index + 1]; the cord is not drawn between them.</summary>
        public List<DiveSpan> Dives = new List<DiveSpan>();
    }

    /// <summary>One dive of a cord under a barrier: entry and exit faces, each with the unit direction from the open cell INTO
    /// the barrier (like a stub's Into) and what the barrier is there (the plate art: wall plate, rock hole, none for water).</summary>
    public sealed class DiveSpan
    {
        public int Index;
        public V2 InFace, InInto, OutFace, OutInto;
        public BlockKind InKind, OutKind;
        public int Cells;
    }

    public static class CordPlanner
    {
        /// <summary>8-connected A* over walkable cells; no corner cutting past an unwalkable cell.
        /// Start and goal are always allowed (an endpoint may sit in a blocked cell's face).</summary>
        public static List<Cell> AStar(CordWorld w, Cell start, Cell goal, int maxExpand = 40000)
        {
            if (start == goal) return new List<Cell> { start };
            bool Ok(Cell c) => c == start || c == goal || w.IsWalkable(c);
            double H(Cell c)
            {
                int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
                return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
            }
            var g = new Dictionary<Cell, double> { [start] = 0 };
            var came = new Dictionary<Cell, Cell>();
            var open = new SortedSet<(double f, double g, Cell c)>(Comparer<(double f, double g, Cell c)>.Create((a, b) =>
            {
                int k = a.f.CompareTo(b.f);
                if (k != 0) return k;
                k = a.g.CompareTo(b.g);
                return k != 0 ? k : a.c.CompareTo(b.c);
            }));
            open.Add((H(start), 0, start));
            int expanded = 0;
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                Cell c = top.c;
                if (c == goal)
                {
                    var path = new List<Cell> { c };
                    while (came.TryGetValue(c, out Cell p)) { c = p; path.Add(c); }
                    path.Reverse();
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++expanded > maxExpand) return null;
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!Ok(q)) continue;
                    if (d.X != 0 && d.Z != 0 && !(Ok(new Cell(c.X + d.X, c.Z)) && Ok(new Cell(c.X, c.Z + d.Z)))) continue;
                    double ng = top.g + (d.X != 0 && d.Z != 0 ? 1.414 : 1.0) + w.ExtraCost(q);
                    if (!g.TryGetValue(q, out double old) || ng < old - 1e-12)
                    {
                        if (g.TryGetValue(q, out double o2)) open.Remove((o2 + H(q), o2, q));
                        g[q] = ng;
                        came[q] = c;
                        open.Add((ng + H(q), ng, q));
                    }
                }
            }
            return null;
        }

        /// <summary>Cost of one barrier cell in a dive route: a detour of up to this many cells over open floor is taken
        /// first, so a cord dives only where it must and through the thinnest barrier near its line.</summary>
        public const double DiveCost = 12.0;

        /// <summary>Dive-through A* (owner 2026-10-06: "cords dive through walls and water"): any in-bounds cell may be crossed,
        /// a barrier cell (unwalkable and not exempt) at <see cref="DiveCost"/>. Diagonal steps only between open cells, so every
        /// dive enters and leaves square through one face. exempt: the two ends' own footprints (never a dive).</summary>
        public static List<Cell> AStarDive(CordWorld w, Cell start, Cell goal, Func<Cell, bool> exempt, int maxExpand = 60000)
        {
            if (start == goal) return new List<Cell> { start };
            bool Open(Cell c) => c == start || c == goal || w.IsWalkable(c) || (exempt != null && exempt(c));
            double H(Cell c)
            {
                int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
                return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
            }
            var g = new Dictionary<Cell, double> { [start] = 0 };
            var came = new Dictionary<Cell, Cell>();
            var open = new SortedSet<(double f, double g, Cell c)>(Comparer<(double f, double g, Cell c)>.Create((a, b) =>
            {
                int k = a.f.CompareTo(b.f);
                if (k != 0) return k;
                k = a.g.CompareTo(b.g);
                return k != 0 ? k : a.c.CompareTo(b.c);
            }));
            open.Add((H(start), 0, start));
            int expanded = 0;
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                Cell c = top.c;
                if (c == goal)
                {
                    var path = new List<Cell> { c };
                    while (came.TryGetValue(c, out Cell p)) { c = p; path.Add(c); }
                    path.Reverse();
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++expanded > maxExpand) return null;
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!w.InBounds(q)) continue;
                    bool diag = d.X != 0 && d.Z != 0;
                    if (diag && !(Open(c) && Open(q) && Open(new Cell(c.X + d.X, c.Z)) && Open(new Cell(c.X, c.Z + d.Z)))) continue;
                    double ng = top.g + (diag ? 1.414 : 1.0) + (Open(q) ? w.ExtraCost(q) : DiveCost);
                    if (!g.TryGetValue(q, out double old) || ng < old - 1e-12)
                    {
                        if (g.TryGetValue(q, out double o2)) open.Remove((o2 + H(q), o2, q));
                        g[q] = ng;
                        came[q] = c;
                        open.Add((ng + H(q), ng, q));
                    }
                }
            }
            return null;
        }

        /// <summary>The route the planner takes between two cells: the walkable A*, else (dive on) the dive A*. Null = unroutable.</summary>
        public static List<Cell> FindPath(CordWorld w, Cell start, Cell goal, bool dive, Func<Cell, bool> exempt)
        {
            List<Cell> p = AStar(w, start, goal);
            if (p != null || !dive) return p;
            return AStarDive(w, start, goal, exempt);
        }

        private static bool Clear(CordWorld w, V2 a, V2 b, V2 p0, V2 p1)
        {
            int n = (int)(V2.Dist(a, b) / 0.05) + 2;
            for (int i = 0; i < n; i++)
            {
                V2 s = a + (b - a) * (i / (double)(n - 1));
                if (V2.Dist(s, p0) <= 0.3 || V2.Dist(s, p1) <= 0.3) continue;
                if (w.Clearance(s) <= 0.2) return false;
            }
            return true;
        }

        /// <summary>String-pull: keep the furthest point in clear line of sight, never skipping a door.</summary>
        private static void Pull(CordWorld w, List<V2> pts, List<bool> isDoor, V2 p0, V2 p1,
                                 List<V2> outp, List<KeyValuePair<V2, WaypointKind>> way)
        {
            int i = 0;
            while (i < pts.Count - 1)
            {
                int nxtDoor = pts.Count - 1;
                for (int k = i + 1; k < pts.Count; k++) if (isDoor[k]) { nxtDoor = k; break; }
                int j = i + 1;
                for (int k = nxtDoor; k > i; k--)
                    if (Clear(w, pts[i], pts[k], p0, p1)) { j = k; break; }
                outp.Add(pts[j]);
                if (j < pts.Count - 1) way.Add(new KeyValuePair<V2, WaypointKind>(pts[j], isDoor[j] ? WaypointKind.Door : WaypointKind.Corner));
                i = j;
            }
        }

        /// <summary>Plan one cord edge from pa to pb through mandatory stops (knots, a ring's via). dive: a leg with no walkable
        /// route dives through the barrier (<see cref="AStarDive"/>); exempt = the ends' own footprints.</summary>
        public static CordPlan Plan(CordWorld w, V2 pa, V2 pb, IList<KeyValuePair<V2, WaypointKind>> mids,
                                    bool dive = false, Func<Cell, bool> exempt = null)
        {
            var stops = new List<V2> { pa };
            foreach (var m in mids) stops.Add(m.Key);
            stops.Add(pb);
            var plan = new CordPlan();
            plan.Points.Add(stops[0]);
            for (int si = 0; si < stops.Count - 1; si++)
            {
                V2 p0 = stops[si], p1 = stops[si + 1];
                List<Cell> path = AStar(w, p0.Floor, p1.Floor);
                if (path == null && dive) path = AStarDive(w, p0.Floor, p1.Floor, exempt);
                if (path == null)
                {
                    plan.Ok = false;
                    plan.Points.Add(p1);
                    continue;
                }
                Cell sc = p0.Floor, gc = p1.Floor;
                bool Barrier(Cell c) => c != sc && c != gc && !w.IsWalkable(c) && !(exempt != null && exempt(c));
                int i0 = 0;          // first cell of the current surface run
                V2 from = p0;
                for (int k = 1; k < path.Count; k++)
                {
                    if (!Barrier(path[k])) continue;
                    int k2 = k;
                    while (k2 + 1 < path.Count && Barrier(path[k2 + 1])) k2++;
                    Cell L = path[k - 1], D = path[k], D2 = path[k2], L2 = path[k2 + 1];
                    var inInto = new V2(D.X - L.X, D.Z - L.Z);
                    var outInto = new V2(D2.X - L2.X, D2.Z - L2.Z);
                    var span = new DiveSpan
                    {
                        InInto = inInto, InFace = L.Centre + inInto * 0.5, InKind = w.BlockAt(D),
                        OutInto = outInto, OutFace = L2.Centre + outInto * 0.5, OutKind = w.BlockAt(D2), Cells = k2 - k + 1
                    };
                    PullRun(w, path, i0, k - 1, from, span.InFace, false, plan);
                    span.Index = plan.Points.Count - 1;
                    plan.Dives.Add(span);
                    plan.Points.Add(span.OutFace);
                    from = span.OutFace;
                    i0 = k2 + 1;
                    k = k2 + 1;
                }
                PullRun(w, path, i0, path.Count - 1, from, p1, true, plan);
                if (si < stops.Count - 2) plan.Waypoints.Add(new KeyValuePair<V2, WaypointKind>(p1, mids[si].Value));
            }
            return plan;
        }

        /// <summary>String-pull one surface run of a path (cells a..b) from point s to point t. The run's first cell stands
        /// for s only at the path start (its own endpoint); its last cell stands for t only at the path end.</summary>
        private static void PullRun(CordWorld w, List<Cell> path, int a, int b, V2 s, V2 t, bool toEnd, CordPlan plan)
        {
            var pts = new List<V2> { s };
            var isDoor = new List<bool> { false };
            int k0 = a == 0 ? 1 : a, k1 = toEnd ? b - 1 : b;
            for (int k = k0; k <= k1; k++) { pts.Add(path[k].Centre); isDoor.Add(w.IsDoor(path[k])); }
            pts.Add(t);
            isDoor.Add(false);
            Pull(w, pts, isDoor, s, t, plan.Points, plan.Waypoints);
        }

        /// <summary>Corner-cut the waypoint polyline, then a centripetal Catmull-Rom.</summary>
        public static List<V2> RoundCorners(IList<V2> P, double r = 0.45)
        {
            if (P.Count < 3) return Geo.Resample(P, 0.05);
            var cut = new List<V2> { P[0] };
            for (int i = 1; i < P.Count - 1; i++)
            {
                V2 a = P[i - 1], b = P[i], c = P[i + 1];
                double l0 = V2.Dist(a, b), l1 = V2.Dist(b, c);
                double rr = Math.Min(r, Math.Min(0.4 * l0, 0.4 * l1));
                cut.Add(b - (b - a) * (1 / Math.Max(l0, 1e-9)) * rr);
                cut.Add(b);
                cut.Add(b + (c - b) * (1 / Math.Max(l1, 1e-9)) * rr);
            }
            cut.Add(P[P.Count - 1]);
            return Geo.Resample(Geo.Catmull(cut, 8), 0.05);
        }
    }
}
