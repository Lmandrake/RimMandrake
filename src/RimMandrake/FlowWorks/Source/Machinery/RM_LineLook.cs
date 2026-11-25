// Verse-free (the FlowWorks SelfTest compiles this file): which FlowWorks parts a "Choose style" pick changes, and to what.
//
// RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY. Owner walk 2026-11-22 (station 24, Futuristic): "Clicking 'change
// style' on an object is supposed to change everything along its connected length. It does not currently. Each item changes
// alone." Owner ruling 2026-11-22: "Both Flow Works need the "change everything on this line" (for flow works items) and GSS
// needs "change everything on this line" (for GSS items). They don't need to change each other's items though. Each mod can
// handle only its own, that's ok."
//
//   the line    what the FlowWorks liquid net PHYSICALLY joins, walked through every FlowWorks part. Unlike the liquid kernel
//               (RM_LiquidNetKernel), tanks and machines conduct here: station 24's pump sits between two pipe runs, and the
//               kernel's rule (a machine never conducts) would split that one line in two.
//   joins       the net's own joins, each read both ways:
//                 pipe cell -- pipe cell      cardinal, plus pipe-pole span edges (IRM_LineGraph.PipeNeighbours);
//                 pipe cell -- tank|machine   the member 8-way around the cell or on it (owner 2026-10-20);
//                 machine   -- tank           touching 8-way (a machine's touch store); tank-tank and machine-machine touching
//                                             is NOT a join (the net moves nothing between them either);
//                 reel      -- part           the reel's body port, its laid hose's free-end port, or the relay reel it feeds
//                                             (a HOSE coupling, RM_LineLook.Couples). A reel that only stands beside a pipe,
//                                             tank or machine is NOT joined to it (RM_LineLook.Joins is touch only).
//   skipped     a part that is not FlowWorks' (a GSS container at a hose end, a VE pipe, a wall on a pipe cell) or not the
//               player's: never changed. As a would-be conductor it is not a join (the net conducts nothing through it), so
//               the walk does not pass it; standing ON a walked pipe cell it is simply passed over and the pipe goes on.
//   look map    every FlowWorks picker shares the four look NAMES (PipeStyles.Looks == HoseStyles.Looks, PipeStyleChecks).
//               A part takes the picked look in its own def's style (<def>_<Look>); a part whose def has no style of that
//               look keeps its look. A part already wearing that look as its stored style is left alone.
//   a fitting   (faucet, pipe pole) is a part of the pipe cell it joins: picked up with that cell's pipe, never a join by
//               touch. Clicked, it starts the walk at the pipe cells it joins; a fitting on no pipe changes itself only.
//   size        the walk stops at the cap (the net's own search cap, RM_LiquidNet.MaxPipeCells, as the old pipe run did),
//               breadth-first from the clicked part, so the parts nearest it change first and the cut is the same every time.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>What a vertex of the look walk is. None: not FlowWorks', not the player's, or not there (never walked).</summary>
    public enum RM_LinePart { None, Pipe, Tank, Machine, Reel, Fitting }

    /// <summary>What the look walk reads. A pipe vertex is its CELL; every other vertex is the part itself. The adapter answers
    /// with raw neighbours; the join rules (which kinds join which) are the kernel's, below.</summary>
    public interface IRM_LineGraph
    {
        RM_LinePart KindOf(object v);
        /// <summary>Pipe cells joined to a pipe cell: cardinal, plus pipe-pole span edges.</summary>
        IEnumerable<object> PipeNeighbours(object cell);
        /// <summary>Things 8-way around or on a pipe cell (the kernel keeps tanks and machines; a pipe thing listed here is
        /// skipped, never walked as a cell).</summary>
        IEnumerable<object> AroundCell(object cell);
        /// <summary>Pipe cells 8-way around or under a part.</summary>
        IEnumerable<object> PipeCellsAround(object part);
        /// <summary>Things touching a part 8-way, the part itself excluded (a pipe thing listed here is skipped: the pipe joins
        /// come from PipeCellsAround).</summary>
        IEnumerable<object> Touching(object part);
        /// <summary>Hose couplings at v: for a reel, what its hose couples (body port, free-end port, the relay it feeds); for any
        /// other vertex, the reels whose hose couples to it.</summary>
        IEnumerable<object> HoseJoins(object v);
        /// <summary>The things standing on a pipe cell that may wear the line's look: the pipe and its fittings (faucet, pipe
        /// pole), with KindOf naming each; the kernel drops any whose KindOf is None. Never a sprinkler head (a machine, reached
        /// by AroundCell) and never a bridge deck over the pipe.</summary>
        IEnumerable<object> PartsOn(object cell);
        /// <summary>The pipe cells a fitting joins: a faucet its own cell, a pipe pole its join cells (under it, then 8-way).</summary>
        IEnumerable<object> FittingCells(object fitting);
    }

    public static class RM_LineLook
    {
        /// <summary>Does a TOUCH (cells side by side, or a part on a pipe cell) between kinds a and b carry the line? Pipe-pipe,
        /// pipe-tank, pipe-machine, machine-tank, both ways. A reel or a fitting that merely stands beside a part is not joined
        /// to it: a reel joins only through its hose's couplings (<see cref="Couples"/>), a fitting only through its cell.</summary>
        public static bool Joins(RM_LinePart a, RM_LinePart b)
        {
            if (a == RM_LinePart.Pipe || b == RM_LinePart.Pipe)
            {
                RM_LinePart o = a == RM_LinePart.Pipe ? b : a;
                return o == RM_LinePart.Pipe || o == RM_LinePart.Tank || o == RM_LinePart.Machine;
            }
            return (a == RM_LinePart.Tank && b == RM_LinePart.Machine) || (a == RM_LinePart.Machine && b == RM_LinePart.Tank);
        }

        /// <summary>Does a HOSE coupling between kinds a and b carry the line? One end must be the reel; the other is any line
        /// part a hose can couple to (pipe, tank, machine, another reel). Nothing couples a fitting or a non-FlowWorks part.</summary>
        public static bool Couples(RM_LinePart a, RM_LinePart b)
        {
            if (a != RM_LinePart.Reel && b != RM_LinePart.Reel) return false;
            RM_LinePart o = a == RM_LinePart.Reel ? b : a;
            return o == RM_LinePart.Pipe || o == RM_LinePart.Tank || o == RM_LinePart.Machine || o == RM_LinePart.Reel;
        }

        /// <summary>The vertices of the line(s) holding <paramref name="starts"/>, breadth-first, at most <paramref name="cap"/>.
        /// <paramref name="capped"/> is true when some joined vertex was left out by the cap.</summary>
        public static List<object> Walk(IRM_LineGraph g, IEnumerable<object> starts, int cap, out bool capped)
        {
            capped = false;
            var order = new List<object>();
            var seen = new HashSet<object>();
            var q = new Queue<object>();
            foreach (object s in starts)
            {
                if (s != null && g.KindOf(s) != RM_LinePart.None && seen.Add(s)) q.Enqueue(s);
            }
            while (q.Count > 0)
            {
                if (order.Count >= cap)
                {
                    capped = true;
                    break;
                }
                object v = q.Dequeue();
                order.Add(v);
                RM_LinePart kv = g.KindOf(v);
                foreach (object n in Touches(g, v, kv))
                {
                    if (n == null || seen.Contains(n)) continue;
                    RM_LinePart kn = g.KindOf(n);
                    if (kv == RM_LinePart.Fitting ? kn != RM_LinePart.Pipe : !Joins(kv, kn)) continue;
                    seen.Add(n);
                    q.Enqueue(n);
                }
                // every kind may carry a hose coupling (a reel's own hose, or a hose coupled to a pipe, tank or machine)
                foreach (object n in g.HoseJoins(v))
                {
                    if (n == null || seen.Contains(n) || !Couples(kv, g.KindOf(n))) continue;
                    seen.Add(n);
                    q.Enqueue(n);
                }
            }
            return order;
        }

        private static IEnumerable<object> Touches(IRM_LineGraph g, object v, RM_LinePart kv)
        {
            switch (kv)
            {
                // AroundCell and Touching list THINGS, the pipe things in those cells too. A pipe vertex is only ever its cell, and
                // the cell queries (PipeNeighbours, PipeCellsAround) already give every pipe join; a pipe thing taken from a touch
                // list would be walked as a cell (InvalidCastException, visit 11, 2026-11-24) or join pipes diagonally. Skip it.
                case RM_LinePart.Pipe:
                    foreach (object n in g.PipeNeighbours(v)) yield return n;
                    foreach (object n in g.AroundCell(v)) if (g.KindOf(n) != RM_LinePart.Pipe) yield return n;
                    break;
                case RM_LinePart.Tank:
                case RM_LinePart.Machine:
                    foreach (object n in g.PipeCellsAround(v)) yield return n;
                    foreach (object n in g.Touching(v)) if (g.KindOf(n) != RM_LinePart.Pipe) yield return n;
                    break;
                case RM_LinePart.Fitting:
                    // a fitting is walked only as a START (nothing joins one by touch or hose): it leads to the pipe cells it
                    // joins, and comes back as a part of those cells (PartsOn)
                    foreach (object n in g.FittingCells(v)) yield return n;
                    break;
            }
        }

        /// <summary>The parts the walk's vertices stand for: a pipe cell's pipe and fittings, every other vertex itself.</summary>
        public static List<object> Parts(IRM_LineGraph g, List<object> vertices)
        {
            var parts = new List<object>();
            var seen = new HashSet<object>();
            foreach (object v in vertices)
            {
                if (g.KindOf(v) == RM_LinePart.Pipe)
                {
                    // the cell's things as the adapter lists them; one not FlowWorks' or not the player's is passed over here
                    foreach (object p in g.PartsOn(v))
                        if (p != null && g.KindOf(p) != RM_LinePart.None && seen.Add(p)) parts.Add(p);
                }
                else if (seen.Add(v))
                {
                    parts.Add(v);
                }
            }
            return parts;
        }

        /// <summary>The changes a pick of <paramref name="look"/> makes: each part that has a style of that look in its own
        /// picker (<paramref name="hasLook"/>) and does not already store it (<paramref name="storedLook"/>), in walk order.</summary>
        public static List<object> Plan(IEnumerable<object> parts, string look, Func<object, string, bool> hasLook, Func<object, string> storedLook)
        {
            var change = new List<object>();
            if (string.IsNullOrEmpty(look)) return change;
            foreach (object p in parts)
            {
                if (p == null || !hasLook(p, look)) continue;   // no style of this look for that kind: it keeps its look
                if (storedLook(p) == look) continue;            // already wears it
                change.Add(p);
            }
            return change;
        }

        /// <summary>Walk, collect and plan in one: what one pick changes.</summary>
        public static List<object> Changes(IRM_LineGraph g, IEnumerable<object> starts, string look, int cap,
                                           Func<object, string, bool> hasLook, Func<object, string> storedLook, out bool capped)
        {
            return Plan(Parts(g, Walk(g, starts, cap, out capped)), look, hasLook, storedLook);
        }
    }
}
