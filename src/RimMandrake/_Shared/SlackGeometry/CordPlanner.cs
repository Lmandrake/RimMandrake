// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Port of nodal.plan / astar / _pull / round_corners (design §8.2.3).
using System;
using System.Collections.Generic;

// _Shared/SlackGeometry (hose port step 1): linked by GimmeSomeSlack AND FlowWorks; top-level types INTERNAL (see DrawOrder.cs).
namespace RimMandrake.Shared.Slack
{
    internal enum WaypointKind { Corner, Door, Knot, Via }

    internal sealed class CordPlan
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
    internal sealed class DiveSpan
    {
        public int Index;
        public V2 InFace, InInto, OutFace, OutInto;
        public BlockKind InKind, OutKind;
        public int Cells;
    }

    internal static class CordPlanner
    {
        // CORDPLANNER_ASTAR_SHRINK_TO_ZERO_ALLOC (hose/wire advisory 2026-10-28 §4 #4): both searches run on one per-thread scratch
        // of flat arrays indexed by cell (z * Width + x), stamped per call so nothing is cleared, and an indexed binary heap
        // ordered (f, g, cell) -- the same total order the SortedSet had, so every pop and every route is identical (GSS must
        // be identical on load). Decrease-key sifts the cell's one heap entry in place, as the SortedSet's remove + add did.
        // Only an endpoint may lie off the map: it takes one of two spare slots past the grid.
        private sealed class Scratch
        {
            public int[] Stamp = new int[0], Came = new int[0], Pos = new int[0], Heap = new int[0];
            public double[] G = new double[0], F = new double[0];
            public int Cur, Count, W, N;
            public Cell Start, Goal;
            public bool Busy;

            public void Begin(CordWorld w, Cell start, Cell goal)
            {
                W = w.Width; N = w.Width * w.Height; Start = start; Goal = goal;
                int need = N + 2;
                if (Stamp.Length < need)
                {
                    Stamp = new int[need]; Came = new int[need]; Pos = new int[need]; Heap = new int[need];
                    G = new double[need]; F = new double[need]; Cur = 0;
                }
                if (++Cur == int.MaxValue) { Array.Clear(Stamp, 0, Stamp.Length); Cur = 1; }
                Count = 0;
            }

            public int Index(Cell c, CordWorld w) =>
                w.InBounds(c) ? c.Z * W + c.X : c == Start ? N : c == Goal ? N + 1 : -1;

            public Cell CellOf(int i) => i < N ? new Cell(i % W, i / W) : i == N ? Start : Goal;

            public bool Seen(int i) => Stamp[i] == Cur;

            public void Visit(int i, double g, double f, int came)
            {
                if (Stamp[i] != Cur) { Stamp[i] = Cur; Pos[i] = -1; }
                G[i] = g; F[i] = f; Came[i] = came;
                if (Pos[i] < 0) { Pos[i] = Count; Heap[Count++] = i; }
                Up(Pos[i]);
            }

            private bool Less(int a, int b)
            {
                int k = F[a].CompareTo(F[b]);
                if (k != 0) return k < 0;
                k = G[a].CompareTo(G[b]);
                return k != 0 ? k < 0 : CellOf(a).CompareTo(CellOf(b)) < 0;
            }

            private void Up(int p)
            {
                int i = Heap[p];
                while (p > 0)
                {
                    int parent = (p - 1) >> 1, j = Heap[parent];
                    if (!Less(i, j)) break;
                    Heap[p] = j; Pos[j] = p; p = parent;
                }
                Heap[p] = i; Pos[i] = p;
            }

            public int Pop()
            {
                int top = Heap[0];
                Pos[top] = -1;
                if (--Count > 0)
                {
                    int i = Heap[Count], p = 0;
                    while (true)
                    {
                        int l = 2 * p + 1;
                        if (l >= Count) break;
                        int r = l + 1, m = r < Count && Less(Heap[r], Heap[l]) ? r : l;
                        if (!Less(Heap[m], i)) break;
                        Heap[p] = Heap[m]; Pos[Heap[p]] = p; p = m;
                    }
                    Heap[p] = i; Pos[i] = p;
                }
                return top;
            }
        }

        [ThreadStatic] private static Scratch scratch;

        private static double H(Cell c, Cell goal)
        {
            int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
            return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
        }

        /// <summary>The one search behind <see cref="AStar"/> and <see cref="AStarDive"/>. into is cleared and receives the
        /// route start..goal; false = no route within maxExpand. Allocation-free once this thread's scratch fits the map and
        /// into has the capacity (a re-entrant call, from a callback, takes a fresh scratch).</summary>
        private static bool Search(CordWorld w, Cell start, Cell goal, bool dive, Func<Cell, bool> exempt, int maxExpand, List<Cell> into)
        {
            into.Clear();
            if (start == goal) { into.Add(start); return true; }
            Scratch s = scratch ?? (scratch = new Scratch());
            if (s.Busy) s = new Scratch();
            s.Busy = true;
            try
            {
                s.Begin(w, start, goal);
                int si = s.Index(start, w);
                s.Visit(si, 0, H(start, goal), -1);
                int expanded = 0;
                while (s.Count > 0)
                {
                    int ci = s.Pop();
                    Cell c = s.CellOf(ci);
                    if (c == goal)
                    {
                        for (int i = ci; i >= 0; i = s.Came[i]) into.Add(s.CellOf(i));
                        // by hand: on net472/Mono List<T>.Reverse() goes through the non-generic Array.Reverse, which boxes
                        // every element of a non-primitive struct
                        for (int lo = 0, hi = into.Count - 1; lo < hi; lo++, hi--) { Cell tmp = into[lo]; into[lo] = into[hi]; into[hi] = tmp; }
                        return true;
                    }
                    if (++expanded > maxExpand) return false;
                    double cg = s.G[ci];
                    foreach (Cell d in Cell.Dirs8)
                    {
                        Cell q = c + d;
                        bool diag = d.X != 0 && d.Z != 0;
                        double step;
                        if (!dive)
                        {
                            if (!Walk(w, q, start, goal)) continue;
                            if (diag && !(Walk(w, new Cell(c.X + d.X, c.Z), start, goal) && Walk(w, new Cell(c.X, c.Z + d.Z), start, goal))) continue;
                            if (!w.StepAllowed(c, q)) continue;
                            step = cg + (diag ? 1.414 : 1.0) + w.ExtraCost(q);
                        }
                        else
                        {
                            if (!w.InBounds(q)) continue;
                            if (diag && !(Open(w, c, start, goal, exempt) && Open(w, q, start, goal, exempt)
                                          && Open(w, new Cell(c.X + d.X, c.Z), start, goal, exempt)
                                          && Open(w, new Cell(c.X, c.Z + d.Z), start, goal, exempt))) continue;
                            if (!w.StepAllowed(c, q)) continue;
                            step = cg + (diag ? 1.414 : 1.0) + (Open(w, q, start, goal, exempt) ? w.ExtraCost(q) : DiveCost);
                        }
                        int qi = s.Index(q, w);
                        if (!s.Seen(qi) || step < s.G[qi] - 1e-12) s.Visit(qi, step, step + H(q, goal), ci);
                    }
                }
                return false;
            }
            finally { s.Busy = false; }
        }

        private static bool Walk(CordWorld w, Cell c, Cell start, Cell goal) => c == start || c == goal || w.IsWalkable(c);

        private static bool Open(CordWorld w, Cell c, Cell start, Cell goal, Func<Cell, bool> exempt) =>
            c == start || c == goal || w.IsWalkable(c) || (exempt != null && exempt(c));

        /// <summary>8-connected A* over walkable cells; no corner cutting past an unwalkable cell.
        /// Start and goal are always allowed (an endpoint may sit in a blocked cell's face).</summary>
        public static List<Cell> AStar(CordWorld w, Cell start, Cell goal, int maxExpand = 40000)
        {
            var path = new List<Cell>();
            return Search(w, start, goal, false, null, maxExpand, path) ? path : null;
        }

        /// <summary><see cref="AStar"/> into a caller's list (cleared first): allocation-free once warm. False = no route.</summary>
        public static bool AStarInto(CordWorld w, Cell start, Cell goal, List<Cell> into, int maxExpand = 40000) =>
            Search(w, start, goal, false, null, maxExpand, into);

        /// <summary>Cost of one barrier cell in a dive route: a detour of up to this many cells over open floor is taken
        /// first, so a cord dives only where it must and through the thinnest barrier near its line.</summary>
        public const double DiveCost = 12.0;

        /// <summary>Dive-through A* (owner 2026-10-06: "cords dive through walls and water"): any in-bounds cell may be crossed,
        /// a barrier cell (unwalkable and not exempt) at <see cref="DiveCost"/>. Diagonal steps only between open cells, so every
        /// dive enters and leaves square through one face. exempt: the two ends' own footprints (never a dive).</summary>
        public static List<Cell> AStarDive(CordWorld w, Cell start, Cell goal, Func<Cell, bool> exempt, int maxExpand = 60000)
        {
            var path = new List<Cell>();
            return Search(w, start, goal, true, exempt, maxExpand, path) ? path : null;
        }

        /// <summary><see cref="AStarDive"/> into a caller's list (cleared first): allocation-free once warm. False = no route.</summary>
        public static bool AStarDiveInto(CordWorld w, Cell start, Cell goal, Func<Cell, bool> exempt, List<Cell> into, int maxExpand = 60000) =>
            Search(w, start, goal, true, exempt, maxExpand, into);

        /// <summary>The route the planner takes between two cells: the walkable A*, else (dive on) the dive A*. Null = unroutable.</summary>
        public static List<Cell> FindPath(CordWorld w, Cell start, Cell goal, bool dive, Func<Cell, bool> exempt)
        {
            List<Cell> p = AStar(w, start, goal);
            if (p != null || !dive) return p;
            return AStarDive(w, start, goal, exempt);
        }

        private static bool Clear(CordWorld w, V2 a, V2 b, V2 p0, V2 p1, HashSet<Cell> onPath = null)
        {
            int n = (int)(V2.Dist(a, b) / 0.05) + 2;
            Cell prevCell = a.Floor;
            for (int i = 0; i < n; i++)
            {
                V2 s = a + (b - a) * (i / (double)(n - 1));
                // phase 6: a shortcut never steps between bands except across a link (ramp, ladder)
                Cell sc = s.Floor;
                if (!w.StepAllowed(prevCell, sc)) return false;
                prevCell = sc;
                if (V2.Dist(s, p0) <= 0.3 || V2.Dist(s, p1) <= 0.3) continue;
                if (w.Clearance(s) <= 0.2) return false;
                // GSS pre-release A5: a shortcut never enters a costed cell (a tree) the A* route went around; the route's
                // own costed cells stay allowed (it chose to cross them)
                if (onPath != null) { Cell c = s.Floor; if (w.ExtraCost(c) > 0 && !onPath.Contains(c)) return false; }
            }
            return true;
        }

        /// <summary>String-pull: keep the furthest point in clear line of sight, never skipping a door.</summary>
        private static void Pull(CordWorld w, List<V2> pts, List<bool> isDoor, V2 p0, V2 p1,
                                 List<V2> outp, List<KeyValuePair<V2, WaypointKind>> way)
        {
            var onPath = new HashSet<Cell>();
            foreach (V2 q in pts) onPath.Add(q.Floor);
            int i = 0;
            while (i < pts.Count - 1)
            {
                int nxtDoor = pts.Count - 1;
                for (int k = i + 1; k < pts.Count; k++) if (isDoor[k]) { nxtDoor = k; break; }
                int j = i + 1;
                for (int k = nxtDoor; k > i; k--)
                    if (Clear(w, pts[i], pts[k], p0, p1, onPath)) { j = k; break; }
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
