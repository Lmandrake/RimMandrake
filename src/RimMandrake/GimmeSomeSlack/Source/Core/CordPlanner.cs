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

        /// <summary>Plan one cord edge from pa to pb through mandatory stops (knots, a ring's via).</summary>
        public static CordPlan Plan(CordWorld w, V2 pa, V2 pb, IList<KeyValuePair<V2, WaypointKind>> mids)
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
                if (path == null)
                {
                    plan.Ok = false;
                    plan.Points.Add(p1);
                    continue;
                }
                var pts = new List<V2> { p0 };
                var isDoor = new List<bool> { false };
                for (int k = 1; k < path.Count - 1; k++) { pts.Add(path[k].Centre); isDoor.Add(w.IsDoor(path[k])); }
                pts.Add(p1);
                isDoor.Add(false);
                Pull(w, pts, isDoor, p0, p1, plan.Points, plan.Waypoints);
                if (si < stops.Count - 2) plan.Waypoints.Add(new KeyValuePair<V2, WaypointKind>(p1, mids[si].Value));
            }
            return plan;
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
