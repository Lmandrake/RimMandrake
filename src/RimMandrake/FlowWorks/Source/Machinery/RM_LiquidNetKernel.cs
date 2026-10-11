// Verse-free (the FlowWorks SelfTest compiles this file): the liquid net's rules, as production code over an injected graph
// (hose port step 6; design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md §3.1-3.4, §3.7). RM_LiquidNet is the
// thin Verse adapter that builds the graph from the map; HoseNetChecks.cs asserts against THIS file.
//
//   vertices  opaque objects: a tank or machine THING, a universal-pipe CELL, a relay REEL (a laid hose ends on its intake)
//   edges     pipe cells conduct to their cardinal pipe neighbours; a laid flexible hose is one LINK between two vertices
//   rules     a machine is an origin, never a conductor; a tank is an endpoint: it is added and never walked through (two
//             pipe runs never merge through a tank, and a hose screwed onto a tank in a pipe run does not join the run);
//             links are crossed from the origin, from pipe cells and from relay vertices only; every tank keeps the FIRST
//             route that reached it (one route per tank); a ring cannot loop (visited vertices and links).
//   flow      a hose shows flow while its lease runs: every successful transfer over a route extends each route link's lease
//             to now + 1.5 x the crediting machine's cadence, never shortening a longer one (monotonic). The colour it shows
//             switches to a new liquid only after that liquid has been credited continuously for minPlumpDwell ticks.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
    public enum RM_NetRole { None, Tank, Pipe, Machine, Relay }

    /// <summary>One laid hose as a net edge: its two vertices and the reel that owns it (the thing credited).</summary>
    public sealed class RM_NetLink
    {
        public int Id;
        public object A, B;
        public object Reel;

        public object Other(object from) => Equals(A, from) ? B : Equals(B, from) ? A : null;
        public override string ToString() => "link" + Id;
    }

    /// <summary>What the kernel walks. Every enumeration is in a deterministic order chosen by the adapter.</summary>
    public interface IRM_NetGraph
    {
        RM_NetRole RoleOf(object v);
        /// <summary>Tanks touching the origin (8-way), excluding the origin itself.</summary>
        IEnumerable<object> OriginTanks(object origin);
        /// <summary>Pipe cells around and under the origin.</summary>
        IEnumerable<object> OriginPipeCells(object origin);
        /// <summary>Tanks cardinal to, then on, a pipe cell.</summary>
        IEnumerable<object> PipeTanks(object pipeCell);
        /// <summary>Cardinal pipe neighbours of a pipe cell.</summary>
        IEnumerable<object> PipeNeighbours(object pipeCell);
        /// <summary>Live hose links with an end at v (already filtered by the eligibility rule).</summary>
        IList<RM_NetLink> LinksAt(object v);
        /// <summary>universalPipesEnabled: off, pipes conduct nothing (a machine reaches only touching tanks and hoses).</summary>
        bool PipesEnabled { get; }
    }

    public sealed class RM_NetResult
    {
        /// <summary>Tanks in the order first reached (adjacent tanks lead), never the origin.</summary>
        public readonly List<object> Tanks = new List<object>();
        /// <summary>Tank -> the hose links crossed to reach it (empty for a tank reached by touch or pipe alone).</summary>
        public readonly Dictionary<object, List<RM_NetLink>> Routes = new Dictionary<object, List<RM_NetLink>>();
        public int Visited;
        public bool Truncated;
    }

    public static class RM_LiquidNetKernel
    {
        /// <summary>Search cap: vertices visited (a link counts as one). PROVISIONAL, as RM_LiquidNet.MaxPipeCells.</summary>
        public const int MaxVisits = 1500;

        /// <summary>Every tank the origin reaches, with the route to each.</summary>
        public static RM_NetResult Walk(IRM_NetGraph g, object origin)
        {
            var res = new RM_NetResult();
            var w = new Walker(g, origin, res);
            foreach (object t in g.OriginTanks(origin)) w.AddTank(t, Empty);
            if (g.PipesEnabled)
                foreach (object c in g.OriginPipeCells(origin)) w.Enqueue(c, Empty);
            foreach (RM_NetLink l in g.LinksAt(origin)) w.Cross(l, origin, Empty);
            w.Run();
            return res;
        }

        /// <summary>The tanks reached by crossing ONE link away from <paramref name="from"/> (the owner's Q7 ruling: a tank feeds a
        /// hose screwed onto it, no pump needed). Nothing around <paramref name="from"/> itself is walked: a tank is never a
        /// conductor, so the tanks of a pipe run the feeding tank stands in are not reached.</summary>
        public static RM_NetResult Across(IRM_NetGraph g, RM_NetLink link, object from)
        {
            var res = new RM_NetResult();
            var w = new Walker(g, from, res);
            w.Cross(link, from, Empty);
            w.Run();
            return res;
        }

        private static readonly List<RM_NetLink> Empty = new List<RM_NetLink>();

        private sealed class Walker
        {
            private readonly IRM_NetGraph g;
            private readonly object origin;
            private readonly RM_NetResult res;
            private readonly HashSet<object> seen = new HashSet<object>();
            private readonly HashSet<int> crossed = new HashSet<int>();
            private readonly Queue<KeyValuePair<object, List<RM_NetLink>>> q = new Queue<KeyValuePair<object, List<RM_NetLink>>>();

            public Walker(IRM_NetGraph g, object origin, RM_NetResult res)
            {
                this.g = g;
                this.origin = origin;
                this.res = res;
                seen.Add(origin);
            }

            public void AddTank(object t, List<RM_NetLink> route)
            {
                if (t == null || Equals(t, origin) || res.Routes.ContainsKey(t)) return;
                res.Tanks.Add(t);
                res.Routes[t] = route;
            }

            public void Enqueue(object v, List<RM_NetLink> route)
            {
                if (v == null || !seen.Add(v)) return;
                if (seen.Count > MaxVisits) { res.Truncated = true; return; }
                q.Enqueue(new KeyValuePair<object, List<RM_NetLink>>(v, route));
            }

            public void Cross(RM_NetLink l, object from, List<RM_NetLink> route)
            {
                if (l == null || !crossed.Add(l.Id)) return;
                object other = l.Other(from);
                if (other == null) return;
                var r2 = new List<RM_NetLink>(route.Count + 1);
                r2.AddRange(route);
                r2.Add(l);
                switch (g.RoleOf(other))
                {
                    case RM_NetRole.Tank: AddTank(other, r2); break;                  // an endpoint: never walked through
                    case RM_NetRole.Pipe: if (g.PipesEnabled) Enqueue(other, r2); break;
                    case RM_NetRole.Relay: Enqueue(other, r2); break;                 // continues along the relay's own hose
                    default: break;                                                    // a machine (or nothing) ends it
                }
            }

            public void Run()
            {
                while (q.Count > 0)
                {
                    KeyValuePair<object, List<RM_NetLink>> e = q.Dequeue();
                    res.Visited++;
                    object v = e.Key;
                    RM_NetRole role = g.RoleOf(v);
                    if (role == RM_NetRole.Pipe)
                    {
                        foreach (object t in g.PipeTanks(v)) AddTank(t, e.Value);
                        foreach (object n in g.PipeNeighbours(v)) Enqueue(n, e.Value);
                    }
                    if (role == RM_NetRole.Pipe || role == RM_NetRole.Relay)
                        foreach (RM_NetLink l in g.LinksAt(v)) Cross(l, v, e.Value);
                }
            }
        }

        // ---------------------------------------------------------------- the flow lease (§3.2-3.3)
        public const int NoLease = int.MinValue;

        /// <summary>A successful transfer at <paramref name="now"/> by a machine cycling every <paramref name="cadence"/> ticks keeps
        /// the hose flowing to now + 1.5 x cadence; a later or shorter credit never shortens a longer lease.</summary>
        public static int Lease(int flowUntil, int now, int cadence) => Math.Max(flowUntil, now + Math.Max(1, cadence) + Math.Max(1, cadence) / 2);

        public static bool Flowing(int flowUntil, int now) => flowUntil != NoLease && now <= flowUntil;

        /// <summary>The tint candidate of one tick's credits: the liquid with the most units; ties by name (ordinal), so the
        /// answer never depends on which machine credited first.</summary>
        public static string Candidate(IDictionary<string, int> unitsByLiquid)
        {
            string best = null;
            int bu = int.MinValue;
            if (unitsByLiquid == null) return null;
            foreach (KeyValuePair<string, int> kv in unitsByLiquid)
                if (kv.Key != null && (kv.Value > bu || (kv.Value == bu && string.CompareOrdinal(kv.Key, best) < 0)))
                {
                    best = kv.Key;
                    bu = kv.Value;
                }
            return best;
        }

        /// <summary>The colour switch (§3.4). A hose with no tint takes the first credited liquid at once. A different liquid
        /// becomes the tint only after it has been the candidate continuously (each of its credits inside the lease window of the
        /// one before, <paramref name="pendingUntil"/>) for <paramref name="dwell"/> ticks.</summary>
        public static void TintStep(ref string tint, ref string pending, ref int pendingSince, ref int pendingUntil,
                                    string candidate, int now, int cadence, int dwell)
        {
            if (candidate == null) return;
            if (tint == null || candidate == tint)
            {
                if (tint == null) tint = candidate;
                pending = null;
                pendingUntil = NoLease;
                return;
            }
            if (pending != candidate || !Flowing(pendingUntil, now))
            {
                pending = candidate;            // a new candidate, or the old one's credits broke off: the dwell restarts
                pendingSince = now;
                pendingUntil = NoLease;
            }
            pendingUntil = Lease(pendingUntil, now, cadence);
            if (now - pendingSince >= Math.Max(0, dwell))
            {
                tint = candidate;
                pending = null;
                pendingUntil = NoLease;
            }
        }

        // ---------------------------------------------------------------- a tank feeding a hose (owner, Q7 ruling 2026-10-11)
        /// <summary>Units a tank at one end of a hose passes on to a destination tank this cycle (no pump needed): liquid runs
        /// from the fuller tank (by fraction of capacity) toward the emptier, at most <paramref name="perCycle"/> units, never past
        /// level, only into the same liquid or an empty tank. 0 when nothing should move.</summary>
        public static int TankFeedUnits(int srcUnits, int srcCap, int dstUnits, int dstCap, bool compatible, int perCycle)
        {
            if (!compatible || srcUnits <= 0 || srcCap <= 0 || dstCap <= 0 || dstUnits >= dstCap) return 0;
            // move u so that (src-u)/srcCap ~= (dst+u)/dstCap: u = (src*dstCap - dst*srcCap) / (srcCap + dstCap)
            long num = (long)srcUnits * dstCap - (long)dstUnits * srcCap;
            if (num <= 0) return 0;
            int level = (int)(num / (srcCap + dstCap));
            return Math.Max(0, Math.Min(Math.Min(perCycle, level), Math.Min(srcUnits, dstCap - dstUnits)));
        }

        /// <summary>The destination a feeding tank passes to: the compatible tank with the lowest fill fraction (ties: first
        /// reached). -1 when none would take anything.</summary>
        public static int FeedTarget(IList<(int units, int cap, bool compatible)> dsts, int srcUnits, int srcCap, int perCycle)
        {
            int best = -1;
            double bf = double.MaxValue;
            for (int i = 0; i < dsts.Count; i++)
            {
                if (TankFeedUnits(srcUnits, srcCap, dsts[i].units, dsts[i].cap, dsts[i].compatible, perCycle) <= 0) continue;
                double f = dsts[i].units / (double)dsts[i].cap;
                if (f < bf) { bf = f; best = i; }
            }
            return best;
        }

        // ---------------------------------------------------------------- route liveness (§3.5)
        /// <summary>A route still carries only if every link on it is still live (a hose wound in, dropped or despawned since the
        /// walk drops the route).</summary>
        public static bool RouteLive(IList<RM_NetLink> route, Func<RM_NetLink, bool> live)
        {
            if (route == null) return false;
            for (int i = 0; i < route.Count; i++) if (!live(route[i])) return false;
            return true;
        }
    }
}
