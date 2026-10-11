using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Round 6 (owner 2026-10-04: "So if the hose can only reach 30 cells, how does the player go farther? Maybe they place
    /// another reel out there to connect to? If so we should show that working."). Verse-free rules of a RELAY: a hose that
    /// ends at another reel's intake feeds that reel, which lays its own hose onward.
    ///   * intake: a cell just outside the relay's footprint across one of its SIDE edges (never a corner), like a pipe or
    ///     tank coupled to a reel (HosePortRule). The hose ends on the shared edge, a coupling pointing into the relay.
    ///   * which intake: the walkable one whose centre is nearest the feeding reel's mouth; ties in side order E, N, W, S,
    ///     then the lowest cell along that side.
    ///   * a reel feeds the relay whose intake cell its laid free end is on (derived, never saved; two candidates -> the
    ///     lowest index given, the caller passes them in thing-id order).
    ///   * each hose keeps its own length cap, route search, re-route and retract: nothing about a hose changes because
    ///     it is in a chain.
    ///   * a chain may not loop back on itself (refused at lay time; ignored by the flow read).
    /// </summary>
    public static class HoseRelay
    {
        /// <summary>Work counter (review S1 perf test): how many times a reel's intake cells were enumerated.</summary>
        public static long IntakeCellCalls;

        /// <summary>The relay's intake cells, in side order E, N, W, S and along each side.</summary>
        internal static List<Cell> IntakeCells(HoseReelRect relay)
        {
            IntakeCellCalls++;
            var o = new List<Cell>();
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s)) o.Add(e + s);
            return o;
        }

        internal static bool IsIntakeOf(HoseReelRect relay, Cell c) => IntakeCells(relay).Contains(c);

        /// <summary>The intake a hose from <paramref name="fromMouth"/> ends on, or false when every intake is blocked.</summary>
        internal static bool TryIntake(HoseReelRect relay, V2 fromMouth, Func<Cell, bool> walkable, out Cell intake)
        {
            intake = new Cell(0, 0);
            double best = double.MaxValue;
            bool found = false;
            foreach (Cell c in IntakeCells(relay))
            {
                if (walkable != null && !walkable(c)) continue;
                double d = V2.Dist(c.Centre, fromMouth);
                if (d < best - 1e-9) { best = d; intake = c; found = true; }
            }
            return found;
        }

        /// <summary>The unit step from the intake cell into the relay (zero when the cell is not an intake).</summary>
        internal static Cell SideInto(HoseReelRect relay, Cell intake)
        {
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s))
                    if (e + s == intake) return new Cell(-s.X, -s.Z);
            return new Cell(0, 0);
        }

        /// <summary>Where the hose ends: the midpoint of the edge the intake cell shares with the relay.</summary>
        internal static V2 IntakePoint(HoseReelRect relay, Cell intake)
        {
            Cell d = SideInto(relay, intake);
            return intake.Centre + new V2(d.X * 0.5, d.Z * 0.5);
        }

        /// <summary>Round 7 (owner, station 42: "pipe does NOT hook up properly to the next reel station"): where the hose
        /// that ends on <paramref name="intake"/> is DRAWN to, and the direction its last stretch and end coupling point
        /// (into the relay). On a 2x2 reel: from the west, the art's one brass inlet (the coupling's face meets the inlet's
        /// face, both west cells); from the east, north or south, the place along that cell's half of the edge where the
        /// drawn reel comes closest to the edge, the coupling's face on the drawn outline (ReelIntakeGeometry, measured
        /// per look and per art: <paramref name="deployed"/> = the relay has laid its own hose). Always within
        /// <see cref="EndTolerance"/> of the footprint edge. Any other footprint: the edge midpoint (IntakePoint).</summary>
        internal static V2 DrawnEnd(HoseReelRect relay, Cell intake, string look, bool deployed, out V2 inward)
        {
            Cell d = SideInto(relay, intake);
            inward = new V2(d.X, d.Z);
            if (relay.W != 2 || relay.H != 2 || (d.X == 0 && d.Z == 0)) return IntakePoint(relay, intake);
            V2 c = relay.Centre;
            double perp, depth;
            if (d.X == 1)       // intake on the WEST side
            {
                ReelIntakeGeometry.WestInlet(look, deployed, out perp, out depth);
                return new V2(relay.X0 - depth, c.Z + perp);
            }
            if (d.X == -1)      // EAST
            {
                ReelIntakeGeometry.Edge(look, deployed, 0, intake.Z - relay.Z0, out perp, out depth);
                return new V2(relay.X0 + relay.W + depth, c.Z + perp);
            }
            if (d.Z == -1)      // NORTH
            {
                ReelIntakeGeometry.Edge(look, deployed, 1, intake.X - relay.X0, out perp, out depth);
                return new V2(c.X + perp, relay.Z0 + relay.H + depth);
            }
            ReelIntakeGeometry.Edge(look, deployed, 2, intake.X - relay.X0, out perp, out depth);   // SOUTH
            return new V2(c.X + perp, relay.Z0 - depth);
        }

        /// <summary>How far a drawn relay end may sit from the footprint edge (cells): the reel art overhangs or falls short
        /// of its 2x2 footprint by up to ~0.3 cell, and the hose ends on the drawing, not in the air beside it.</summary>
        public const double EndTolerance = 0.35;

        /// <summary>The straight run the hose makes into its end coupling (cells), so the coupling's axis is the intake's.</summary>
        public const double EndStraight = 0.6;

        /// <summary>Signed distance of <paramref name="p"/> from the relay's edge on the side the hose comes in from (+ =
        /// outside), and whether p lies within that edge's span (between its corners).</summary>
        internal static double EdgeOffset(HoseReelRect relay, V2 inward, V2 p, out bool withinSpan)
        {
            V2 o = new V2(-inward.X, -inward.Z);
            if (o.X != 0)
            {
                double edge = o.X > 0 ? relay.X0 + relay.W : relay.X0;
                withinSpan = p.Z > relay.Z0 && p.Z < relay.Z0 + relay.H;
                return (p.X - edge) * o.X;
            }
            double ez = o.Z > 0 ? relay.Z0 + relay.H : relay.Z0;
            withinSpan = p.X > relay.X0 && p.X < relay.X0 + relay.W;
            return (p.Z - ez) * o.Z;
        }

        /// <summary>Index of the relay a hose whose free end is on <paramref name="far"/> feeds, or -1. self is skipped.</summary>
        internal static int RelayOf(Cell far, IList<HoseReelRect> reels, int self)
        {
            for (int i = 0; i < reels.Count; i++)
                if (i != self && IsIntakeOf(reels[i], far)) return i;
            return -1;
        }

        /// <summary>True when laying a hose from reel <paramref name="from"/> into relay <paramref name="to"/> would close a
        /// loop: following the chain downstream from <paramref name="to"/> (next(i) = the relay i feeds, -1 = none) reaches
        /// <paramref name="from"/>.</summary>
        /// <summary>GPT source read 2026-10-06 B10: where a reel's hose WILL end for the loop test: a pending carry order's end
        /// (Deploy or Move) wins over the laid end, so two pending orders cannot close a ring that neither sees laid.</summary>
        public static int IntendedNext(int laidNext, bool pendingEnd, int pendingNext) => pendingEnd ? pendingNext : laidNext;

        public static bool WouldLoop(int from, int to, Func<int, int> next)
        {
            var seen = new HashSet<int>();
            for (int i = to; i >= 0 && seen.Add(i); i = next(i))
                if (i == from) return true;
            return false;
        }

        /// <summary>The reels a chain passes through from <paramref name="start"/> downstream (start first); stops at a loop.</summary>
        public static List<int> Chain(int start, Func<int, int> next)
        {
            var o = new List<int>();
            var seen = new HashSet<int>();
            for (int i = start; i >= 0 && seen.Add(i); i = next(i)) o.Add(i);
            return o;
        }
    }
    /// <summary>
    /// Review S1 (design FINAL §3.1 "Index", G1.17): the relay adjacency of one map, built ONCE in O(reels) and shared by
    /// drawing, Loops, FeedersOf, the debug flow provider and RM_HoseLinks. Inputs are in thing-id order (the relay
    /// tie-break): each reel's footprint, its laid free end (null = not laid) and its debug-flow flag.
    ///   * next(i): the relay i's laid hose ends on (the lowest-index reel other than i with that intake cell), or -1.
    ///   * a laid edge i -> next(i) closes a loop exactly when i lies on a cycle of next (functional graph), so
    ///     Loops(i, next(i)) is a precomputed flag, and Feeders(r) = { j : next(j) = r, j not on a cycle }.
    /// </summary>
    public sealed class HoseRelayIndex
    {
        public readonly int Count;
        private readonly int[] next;
        private readonly bool[] onCycle;
        private readonly bool[] debug;
        private readonly List<int>[] feeders;
        private readonly Dictionary<Cell, List<int>> intake = new Dictionary<Cell, List<int>>();
        private static readonly List<int> NoFeeders = new List<int>();

        /// <summary>True when any reel carries the debug-flow flag; with none the debug provider has nothing to say.</summary>
        public readonly bool AnyDebug;

        /// <summary>Work counter: feeder steps the debug provider walked (review S1: an idle map walks none).</summary>
        public static long DebugWalkSteps;

        internal HoseRelayIndex(IList<HoseReelRect> rects, IList<Cell?> laidFar, IList<bool> debugFlag)
        {
            Count = rects.Count;
            next = new int[Count];
            onCycle = new bool[Count];
            debug = new bool[Count];
            feeders = new List<int>[Count];
            for (int i = 0; i < Count; i++)
            {
                foreach (Cell c in HoseRelay.IntakeCells(rects[i]))
                {
                    if (!intake.TryGetValue(c, out List<int> l)) intake[c] = l = new List<int>(1);
                    if (l.Count == 0 || l[l.Count - 1] != i) l.Add(i);
                }
                debug[i] = debugFlag != null && debugFlag[i];
                if (debug[i]) AnyDebug = true;
            }
            for (int i = 0; i < Count; i++) next[i] = laidFar[i].HasValue ? RelayAt(laidFar[i].Value, i) : -1;
            // cycle marking on the functional graph: 0 unvisited, 1 on the current path, 2 finished
            var state = new byte[Count];
            var path = new List<int>();
            for (int s = 0; s < Count; s++)
            {
                if (state[s] != 0) continue;
                path.Clear();
                int i = s;
                while (i >= 0 && state[i] == 0) { state[i] = 1; path.Add(i); i = next[i]; }
                if (i >= 0 && state[i] == 1)
                    for (int k = path.IndexOf(i); k < path.Count; k++) onCycle[path[k]] = true;
                foreach (int p in path) state[p] = 2;
            }
            for (int j = 0; j < Count; j++)
            {
                int r = next[j];
                if (r < 0 || onCycle[j]) continue;
                if (feeders[r] == null) feeders[r] = new List<int>();
                feeders[r].Add(j);
            }
        }

        /// <summary>The reel (other than <paramref name="self"/>) with <paramref name="c"/> as an intake cell, or -1.</summary>
        internal int RelayAt(Cell c, int self)
        {
            if (!intake.TryGetValue(c, out List<int> l)) return -1;
            foreach (int i in l) if (i != self) return i;
            return -1;
        }

        /// <summary>The relay reel i's laid hose ends on, or -1 (loops included: this is the raw laid end).</summary>
        public int Next(int i) => i >= 0 && i < Count ? next[i] : -1;

        /// <summary>True when reel i's laid hose closes a loop (Loops(i, Next(i))).</summary>
        public bool OnLoop(int i) => i >= 0 && i < Count && onCycle[i];

        /// <summary>Reels feeding r, ascending (thing-id order), loops excluded.</summary>
        public IReadOnlyList<int> Feeders(int r) => r >= 0 && r < Count && feeders[r] != null ? feeders[r] : NoFeeders;

        /// <summary>HoseRelay.WouldLoop over the laid ends.</summary>
        public bool WouldLoop(int from, int to) => HoseRelay.WouldLoop(from, to, Next);

        /// <summary>The debug provider's chain read: does any reel feeding r down a relay chain carry the debug flag?
        /// <paramref name="walkable"/> = the feeder has a laid hose with a lay (only those pass the flag on).</summary>
        public bool FedByDebug(int r, Func<int, bool> walkable)
        {
            if (!AnyDebug || r < 0 || r >= Count) return false;
            var seen = new HashSet<int> { r };
            var stack = new Stack<int>();
            stack.Push(r);
            while (stack.Count > 0)
                foreach (int f in Feeders(stack.Pop()))
                {
                    DebugWalkSteps++;
                    if (!seen.Add(f) || !walkable(f)) continue;
                    if (debug[f]) return true;
                    stack.Push(f);
                }
            return false;
        }
    }
}
