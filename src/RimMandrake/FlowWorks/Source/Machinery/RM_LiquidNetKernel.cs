// Verse-free (the FlowWorks SelfTest compiles this file): the liquid net's rules, as production code over an injected graph
// (hose port step 6; design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md §3.2-3.4; liquid networks build step
// L2, design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §3.1). RM_LiquidNet is the thin Verse adapter that shows
// the kernel the map; HoseNetChecks.cs and NetComponentChecks.cs assert against THIS file.
//
//   conductors  universal-pipe CELLS (they conduct cardinally), relay REELS, and each live hose LINK (one conductor). A
//               COMPONENT is a connected set of conductors.
//   members     tanks and machines ATTACH to every component they touch (a pipe cardinal to or under a tank, a pipe 8-way
//               around or under a machine, a hose end coupled to either) and never conduct: a tank between two pipe runs is
//               in both and the runs do not merge; a tank-hose-tank pair is one component of one conductor.
//   ports       a hose's free end with a role (Intake / Outflow, rev 2 §3.4) attaches to its hose's component as a PORT.
//   store       a member's store = the tanks attached to any component it is attached to, plus tanks touching it 8-way.
//   revision    components, membership, ports and one predecessor tree per component are built lazily, once per topology
//               revision (RM_NetTopologyCache); a component bigger than MaxConductors is REFUSED, never partly operated.
//   routes      the hoses credited for a move are the links on the component's tree path between the two attachments
//               (O(route length)); among several components the one whose path crosses the fewest hoses wins.
//   flow        a hose shows flow while its lease runs: every committed transfer over a route extends each route link's lease
//               to now + 1.5 x the crediting machine's cadence, never shortening a longer one (monotonic). The colour it shows
//               switches to a new liquid only after that liquid has been credited continuously for minPlumpDwell ticks.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.Machinery
{
    public enum RM_NetRole { None, Tank, Pipe, Machine, Relay, Port }

    /// <summary>What a hose's free end does (rev 2 §3.4): Capped (default) just connects nothing; Intake is a pump source;
    /// Outflow is where liquid enters the world.</summary>
    public enum RM_FreeEndRole { Capped, Intake, Outflow }

    /// <summary>A hose's free end with a role, as a component port: the reel it belongs to and the cell it lies on.</summary>
    public sealed class RM_NetPort
    {
        public object Reel;
        public object Cell;
        public RM_FreeEndRole Role;
        public override bool Equals(object o) => o is RM_NetPort p && Equals(p.Reel, Reel);
        public override int GetHashCode() => Reel?.GetHashCode() ?? 0;
        public override string ToString() => "port(" + Reel + "," + Role + ")";
    }

    /// <summary>One laid hose as a net conductor: its two ends and the reel that owns it (the thing credited).</summary>
    public sealed class RM_NetLink
    {
        public int Id;
        public object A, B;
        public object Reel;

        public object Other(object from) => Equals(A, from) ? B : Equals(B, from) ? A : null;
        public override string ToString() => "link" + Id;
    }

    /// <summary>What the kernel reads. Every enumeration is in a deterministic order chosen by the adapter.</summary>
    public interface IRM_NetGraph
    {
        RM_NetRole RoleOf(object v);
        /// <summary>Tanks touching a member 8-way (a machine's touch store), excluding the member itself.</summary>
        IEnumerable<object> OriginTanks(object member);
        /// <summary>Pipe cells a member attaches through: cardinal or under for a tank, 8-way or under for a machine.</summary>
        IEnumerable<object> OriginPipeCells(object member);
        /// <summary>Tanks cardinal to, then on, a pipe cell.</summary>
        IEnumerable<object> PipeTanks(object pipeCell);
        /// <summary>Machines 8-way around, or on, a pipe cell.</summary>
        IEnumerable<object> PipeMachines(object pipeCell);
        /// <summary>Cardinal pipe neighbours of a pipe cell.</summary>
        IEnumerable<object> PipeNeighbours(object pipeCell);
        /// <summary>Live hose links with an end at v (already filtered by the eligibility rule).</summary>
        IList<RM_NetLink> LinksAt(object v);
        /// <summary>universalPipesEnabled: off, pipes conduct nothing (a machine reaches only touching tanks and hoses).</summary>
        bool PipesEnabled { get; }
        /// <summary>The members' order key (thingIDNumber): ties and listing order never depend on who asked.</summary>
        int Order(object member);
    }

    /// <summary>A member's store: the tanks, the hose route to each, and whether a component it touches was refused.</summary>
    public sealed class RM_NetResult
    {
        /// <summary>Tanks: touching tanks first, then by hoses crossed, then by id. Never the member itself.</summary>
        public readonly List<object> Tanks = new List<object>();
        /// <summary>Tank -> the hose links crossed to reach it (empty for a tank reached by touch or pipe alone).</summary>
        public readonly Dictionary<object, List<RM_NetLink>> Routes = new Dictionary<object, List<RM_NetLink>>();
        /// <summary>Conductors and attachments of the components read (the ring/terminate bound).</summary>
        public int Visited;
        /// <summary>A component the member touches is over MaxConductors: refused, its tanks are not in the store.</summary>
        public bool Truncated;
    }

    /// <summary>One component: its conductors (pipe cells, relays, links) as a BFS tree, and what attaches to it.</summary>
    public sealed class RM_NetComponent
    {
        public int Id;
        public bool Refused;
        /// <summary>Conductors + attached members + ports (what MaxConductors counts).</summary>
        public int Size;
        public readonly List<object> Tanks = new List<object>();
        public readonly List<object> Machines = new List<object>();
        public readonly List<RM_NetPort> Ports = new List<RM_NetPort>();
        public readonly List<RM_NetLink> Links = new List<RM_NetLink>();
        internal readonly List<object> Nodes = new List<object>();
        internal readonly List<int> Parent = new List<int>();
        internal readonly List<int> Depth = new List<int>();
        /// <summary>Member or port -> the conductor nodes it attaches at.</summary>
        internal readonly Dictionary<object, List<int>> Attach = new Dictionary<object, List<int>>();

        public bool Has(object member) => Attach.ContainsKey(member);
    }

    /// <summary>
    /// The components of one topology revision, built lazily: a component is labelled the first time anything asks for a
    /// conductor in it. A new revision is a new instance (RM_NetTopologyCache); nothing in it is ever patched in place.
    /// </summary>
    public sealed class RM_NetComponents
    {
        /// <summary>PROVISIONAL (rev 2 §3.1): conductors + members + ports per component; larger is refused.</summary>
        public const int MaxConductors = 3000;

        private readonly IRM_NetGraph g;
        private readonly Dictionary<object, KeyValuePair<RM_NetComponent, int>> nodeOf = new Dictionary<object, KeyValuePair<RM_NetComponent, int>>();
        private readonly Dictionary<object, List<RM_NetComponent>> compsOf = new Dictionary<object, List<RM_NetComponent>>();
        private readonly Dictionary<object, RM_NetResult> stores = new Dictionary<object, RM_NetResult>();
        private readonly List<RM_NetComponent> all = new List<RM_NetComponent>();
        private readonly int cap;

        /// <summary>State read: components built (BFS runs) in this revision.</summary>
        public int Builds;

        public RM_NetComponents(IRM_NetGraph g, int cap = MaxConductors)
        {
            this.g = g;
            this.cap = cap;
        }

        public IReadOnlyList<RM_NetComponent> Built => all;

        private bool Conducts(object v)
        {
            RM_NetRole r = v is RM_NetLink ? RM_NetRole.None : g.RoleOf(v);
            return v is RM_NetLink || r == RM_NetRole.Relay || (r == RM_NetRole.Pipe && g.PipesEnabled);
        }

        /// <summary>The component a conductor (pipe cell, relay or link) belongs to, built on first use.</summary>
        public RM_NetComponent ComponentOfNode(object node)
        {
            if (node == null || !Conducts(node)) return null;
            return nodeOf.TryGetValue(node, out KeyValuePair<RM_NetComponent, int> e) ? e.Key : Build(node);
        }

        public RM_NetComponent ComponentOf(RM_NetLink l) => ComponentOfNode(l);

        /// <summary>The components a member (tank or machine) attaches to, in seed order (its pipe cells, then its hoses).</summary>
        public IReadOnlyList<RM_NetComponent> ComponentsOf(object member)
        {
            if (member == null) return new List<RM_NetComponent>();
            if (compsOf.TryGetValue(member, out List<RM_NetComponent> l)) return l;
            l = new List<RM_NetComponent>();
            foreach (object seed in Seeds(member))
            {
                RM_NetComponent c = ComponentOfNode(seed);
                if (c != null && !l.Contains(c)) l.Add(c);
            }
            compsOf[member] = l;
            return l;
        }

        private IEnumerable<object> Seeds(object member)
        {
            if (g.PipesEnabled)
                foreach (object c in g.OriginPipeCells(member))
                    if (g.RoleOf(c) == RM_NetRole.Pipe) yield return c;
            foreach (RM_NetLink l in g.LinksAt(member)) yield return l;
        }

        /// <summary>True when a component the member attaches to is over the cap (it reads "network too large").</summary>
        public bool TooLarge(object member)
        {
            foreach (RM_NetComponent c in ComponentsOf(member)) if (c.Refused) return true;
            return false;
        }

        private RM_NetComponent Build(object start)
        {
            Builds++;
            var comp = new RM_NetComponent { Id = all.Count };
            all.Add(comp);
            var q = new Queue<int>();
            Label(comp, start, -1, q);
            while (q.Count > 0)
            {
                int i = q.Dequeue();
                object v = comp.Nodes[i];
                if (comp.Size > cap) { comp.Refused = true; break; }
                if (v is RM_NetLink l)
                {
                    comp.Links.Add(l);
                    foreach (object end in new[] { l.A, l.B })
                    {
                        if (end == null) continue;
                        if (end is RM_NetPort port) { AttachPort(comp, port, i); continue; }
                        switch (g.RoleOf(end))
                        {
                            case RM_NetRole.Tank: AttachMember(comp, end, i, comp.Tanks); break;
                            case RM_NetRole.Machine: AttachMember(comp, end, i, comp.Machines); break;
                            case RM_NetRole.Pipe:
                            case RM_NetRole.Relay:
                                if (Conducts(end)) Visit(comp, end, i, q);
                                break;
                            case RM_NetRole.Port:
                                if (end is RM_NetPort p2) AttachPort(comp, p2, i);
                                break;
                        }
                    }
                    continue;
                }
                if (g.RoleOf(v) == RM_NetRole.Pipe)
                {
                    foreach (object t in g.PipeTanks(v)) AttachMember(comp, t, i, comp.Tanks);
                    foreach (object m in g.PipeMachines(v)) AttachMember(comp, m, i, comp.Machines);
                    foreach (object n in g.PipeNeighbours(v)) Visit(comp, n, i, q);
                }
                foreach (RM_NetLink l2 in g.LinksAt(v)) Visit(comp, l2, i, q);
            }
            if (comp.Size > cap) comp.Refused = true;
            return comp;
        }

        private void Visit(RM_NetComponent comp, object v, int parent, Queue<int> q)
        {
            if (v == null) return;
            if (nodeOf.TryGetValue(v, out KeyValuePair<RM_NetComponent, int> e))
            {
                if (e.Key != comp)
                {
                    // only a refused (stopped) component leaves conductors unlabelled: whatever reaches it is the same
                    // over-size network seen from elsewhere, and is refused too (never partly operated)
                    comp.Refused = true;
                    e.Key.Refused = true;
                }
                return;
            }
            if (!Conducts(v)) return;
            Label(comp, v, parent, q);
        }

        private void Label(RM_NetComponent comp, object v, int parent, Queue<int> q)
        {
            int i = comp.Nodes.Count;
            comp.Nodes.Add(v);
            comp.Parent.Add(parent);
            comp.Depth.Add(parent < 0 ? 0 : comp.Depth[parent] + 1);
            comp.Size++;
            nodeOf[v] = new KeyValuePair<RM_NetComponent, int>(comp, i);
            q.Enqueue(i);
        }

        private static void AttachMember(RM_NetComponent comp, object m, int node, List<object> list)
        {
            if (m == null) return;
            if (!comp.Attach.TryGetValue(m, out List<int> at))
            {
                comp.Attach[m] = at = new List<int>();
                list.Add(m);
                comp.Size++;
            }
            if (!at.Contains(node)) at.Add(node);
        }

        private static void AttachPort(RM_NetComponent comp, RM_NetPort p, int node)
        {
            if (p == null || p.Role == RM_FreeEndRole.Capped) return;
            if (!comp.Attach.ContainsKey(p))
            {
                comp.Attach[p] = new List<int> { node };
                comp.Ports.Add(p);
                comp.Size++;
            }
        }

        /// <summary>The nodes a member attaches at in <paramref name="comp"/>, read from the member's own side (its seeds) and
        /// from what the component saw.</summary>
        private List<int> AttachNodes(RM_NetComponent comp, object member)
        {
            var at = new List<int>();
            if (comp.Attach.TryGetValue(member, out List<int> l)) at.AddRange(l);
            foreach (object s in Seeds(member))
                if (nodeOf.TryGetValue(s, out KeyValuePair<RM_NetComponent, int> e) && e.Key == comp && !at.Contains(e.Value)) at.Add(e.Value);
            return at;
        }

        /// <summary>The links on the tree path between nodes a and b, in order from a to b.</summary>
        private static List<RM_NetLink> Path(RM_NetComponent c, int a, int b)
        {
            var up = new List<RM_NetLink>();
            var down = new List<RM_NetLink>();
            while (c.Depth[a] > c.Depth[b]) { if (c.Nodes[a] is RM_NetLink l) up.Add(l); a = c.Parent[a]; }
            while (c.Depth[b] > c.Depth[a]) { if (c.Nodes[b] is RM_NetLink l) down.Add(l); b = c.Parent[b]; }
            while (a != b) {
                if (c.Nodes[a] is RM_NetLink la) up.Add(la);
                if (c.Nodes[b] is RM_NetLink lb) down.Add(lb);
                a = c.Parent[a];
                b = c.Parent[b];
            }
            if (c.Nodes[a] is RM_NetLink lca) up.Add(lca);
            down.Reverse();
            up.AddRange(down);
            return up;
        }

        /// <summary>The hose route between two attached things in one component: the tree path crossing the fewest hoses
        /// among their attachment points (null if either is not attached to it).</summary>
        public List<RM_NetLink> RouteIn(RM_NetComponent c, object from, object to)
        {
            List<int> a = AttachNodes(c, from), b = AttachNodes(c, to);
            List<RM_NetLink> best = null;
            foreach (int i in a)
            {
                foreach (int j in b)
                {
                    List<RM_NetLink> p = Path(c, i, j);
                    if (best == null || p.Count < best.Count) best = p;
                    if (best.Count == 0) return best;
                }
            }
            return best;
        }

        /// <summary>A member's store (rev 2 §3.1), cached for the revision.</summary>
        public RM_NetResult StoreOf(object member)
        {
            if (member == null) return new RM_NetResult();
            if (stores.TryGetValue(member, out RM_NetResult r)) return r;
            r = new RM_NetResult();
            var empty = new List<RM_NetLink>();
            foreach (object t in g.OriginTanks(member))
            {
                if (t == null || Equals(t, member) || r.Routes.ContainsKey(t)) continue;
                r.Tanks.Add(t);
                r.Routes[t] = empty;
            }
            int touching = r.Tanks.Count;
            foreach (RM_NetComponent c in ComponentsOf(member))
            {
                r.Visited += c.Size;
                if (c.Refused) { r.Truncated = true; continue; }
                foreach (object t in c.Tanks)
                {
                    if (Equals(t, member)) continue;
                    List<RM_NetLink> route = RouteIn(c, member, t);
                    if (route == null) continue;
                    if (r.Routes.TryGetValue(t, out List<RM_NetLink> old))
                    {
                        if (route.Count < old.Count) r.Routes[t] = route;
                        continue;
                    }
                    r.Tanks.Add(t);
                    r.Routes[t] = route;
                }
            }
            // touching tanks lead; the rest by hoses crossed, then by id (never by who asked first)
            List<object> rest = r.Tanks.GetRange(touching, r.Tanks.Count - touching);
            rest.Sort((x, y) =>
            {
                int h = r.Routes[x].Count.CompareTo(r.Routes[y].Count);
                return h != 0 ? h : g.Order(x).CompareTo(g.Order(y));
            });
            r.Tanks.RemoveRange(touching, r.Tanks.Count - touching);
            r.Tanks.AddRange(rest);
            stores[member] = r;
            return r;
        }
    }

    /// <summary>
    /// One map's components, kept for a topology revision (rev 2 §3.1): the same revision returns the same components, a bumped
    /// revision builds new ones lazily. Nothing here is keyed on the tick, so a quiet map never rebuilds.
    /// </summary>
    public sealed class RM_NetTopologyCache
    {
        private long key = long.MinValue;
        private RM_NetComponents comps;

        /// <summary>State read: component sets made (one per revision actually used).</summary>
        public int Revisions;

        public RM_NetComponents Get(long revisionKey, Func<RM_NetComponents> make)
        {
            if (comps != null && key == revisionKey) return comps;
            key = revisionKey;
            Revisions++;
            return comps = make();
        }
    }

    /// <summary>A tank's job (rev 2 §3.2), saved as rmTankMode. Store (default) holds liquid for pumps and machines; Fill pulls the
    /// network's liquid in; Empty pushes its liquid to the other tanks; Dump marks a tank whose liquid may leave the network.</summary>
    public enum RM_TankMode { Store, Fill, Empty, Dump }

    /// <summary>Bottles and tank jobs (bottle-loop fix, 2026-10-11; design rev 2 §3.2 "Bottles"). A colonist hauling bottles
    /// on his own pours them only into a Fill tank; a player's order ("Prioritize emptying ...") may also pour into a Store
    /// tank. Bottles are filled from Store, Empty and Dump tanks, never from a Fill tank. So no tank both takes bottles
    /// unasked and gives them back, and liquid poured into a Fill tank never returns to a bottle (a Fill tank sends to no
    /// tank in the settle): the pour-then-refill loop cannot form. Empty takes no bottles (it takes nothing).</summary>
    public static class RM_TankBottleRules
    {
        /// <summary>May a bottle be poured into a tank on this job? <paramref name="playerOrdered"/>: a forced job.</summary>
        public static bool PoursInto(RM_TankMode mode, bool playerOrdered)
        {
            return mode == RM_TankMode.Fill || (playerOrdered && mode == RM_TankMode.Store);
        }

        /// <summary>May an empty bottle be filled from a tank on this job? Ordered or not: the same answer.</summary>
        public static bool FillsFrom(RM_TankMode mode)
        {
            return mode == RM_TankMode.Store || mode == RM_TankMode.Empty || mode == RM_TankMode.Dump;
        }
    }

    /// <summary>What the settle reads of one tank: id, stock, capacity, liquid identity and job.</summary>
    public struct RM_SettleTank
    {
        public int Id, Units, Cap;
        public object Liquid;
        public RM_TankMode Mode;
        public RM_SettleTank(int id, int units, int cap, object liquid, RM_TankMode mode) { Id = id; Units = units; Cap = cap; Liquid = liquid; Mode = mode; }
    }

    /// <summary>What a fill or draw plan reads of one tank (rev 2 §3.2): its id, stock, capacity, and whether it holds the
    /// liquid in question (Empty = holds nothing and may adopt it).</summary>
    public struct RM_TankView
    {
        public int Id, Units, Cap;
        public bool Holds, Empty;
        public RM_TankView(int id, int units, int cap, bool holds, bool empty) { Id = id; Units = units; Cap = cap; Holds = holds; Empty = empty; }
        public double Fraction => Cap > 0 ? Units / (double)Cap : 1.0;
    }

    /// <summary>
    /// G9 starvation (rev 2 §3.3): two machines that consume one liquid take turns. A machine that drew last yields while another
    /// one that wanted the same liquid went without since that draw; so each cycle starts with the machine served last-but-one.
    /// A machine alone on its liquid is never held back. Keyed by whatever the caller passes (a LiquidDef).
    /// </summary>
    public sealed class RM_ConsumerRotation
    {
        private readonly Dictionary<object, KeyValuePair<int, int>> served = new Dictionary<object, KeyValuePair<int, int>>();
        private readonly Dictionary<object, Dictionary<int, int>> starved = new Dictionary<object, Dictionary<int, int>>();

        /// <summary>How long a "went without" counts (ticks): two machine cycles.</summary>
        public int Window = 500;

        public bool MayDraw(object key, int machine, int now)
        {
            if (key == null || !served.TryGetValue(key, out KeyValuePair<int, int> s) || s.Key != machine) return true;
            if (!starved.TryGetValue(key, out Dictionary<int, int> w)) return true;
            foreach (KeyValuePair<int, int> kv in w)
                if (kv.Key != machine && kv.Value >= s.Value && now - kv.Value <= Window) return false;
            return true;
        }

        public void Served(object key, int machine, int now)
        {
            if (key == null) return;
            served[key] = new KeyValuePair<int, int>(machine, now);
            if (starved.TryGetValue(key, out Dictionary<int, int> w)) w.Remove(machine);
        }

        public void Starved(object key, int machine, int now)
        {
            if (key == null) return;
            if (!starved.TryGetValue(key, out Dictionary<int, int> w)) starved[key] = w = new Dictionary<int, int>();
            w[machine] = now;
        }
    }

    /// <summary>
    /// Liquid networks L8 (rev 2 §3.7, owner Q2 ruled REAL): a hose holds a little liquid while it carries. The units always come
    /// out of a committed move (never from nothing) and leave at an open end when the hose stops carrying (never back into a
    /// tank). One liquid at a time: a move of another liquid first flushes the held one out.
    /// </summary>
    public static class RM_HoseHold
    {
        /// <summary>Units a hose of <paramref name="cells"/> holds: ceil(cells x <paramref name="perCell"/>), 0 when off.</summary>
        public static int Capacity(double cells, float perCell) => cells <= 0 || perCell <= 0f ? 0 : (int)Math.Ceiling(Math.Round(cells * perCell, 3));

        /// <summary>Fill a hose a committed move of <paramref name="liquid"/> crossed: another liquid held is flushed first
        /// (<paramref name="flush"/>), then up to the room is taken (<paramref name="take"/> returns the units it really gave).
        /// Returns the units taken.</summary>
        public static int Fill(ref object heldLiquid, ref int held, int cap, object liquid, Func<int, int> take, Action<object, int> flush)
        {
            if (liquid == null || cap <= 0 || take == null) return 0;
            if (held > 0 && !Equals(heldLiquid, liquid))
            {
                flush?.Invoke(heldLiquid, held);
                held = 0;
                heldLiquid = null;
            }
            int need = cap - held;
            if (need <= 0) return 0;
            int got = Math.Max(0, Math.Min(need, take(need)));
            if (got > 0)
            {
                held += got;
                heldLiquid = liquid;
            }
            return got;
        }

        /// <summary>The hose stops carrying: everything held leaves through <paramref name="spill"/>. Returns the units.</summary>
        public static int Drain(ref object heldLiquid, ref int held, Action<object, int> spill)
        {
            int u = held;
            if (u > 0) spill?.Invoke(heldLiquid, u);
            held = 0;
            heldLiquid = null;
            return u;
        }

        /// <summary>A hose drains when it holds something and does not carry: holding switched off, not live (wound, dropped,
        /// decoupled, capped with no other carrying route), or its lease ran out.</summary>
        public static bool ShouldDrain(int held, bool holdingOn, bool live, bool flowing) => held > 0 && (!holdingOn || !live || !flowing);
    }

    /// <summary>
    /// Liquid networks L9 (rev 2 §3.4; owner card Q4: a hose into another faction's tank is allowed, as theft, priced like power
    /// theft, ruling #7: 2 goodwill a day, 12-cell notice). A COPY of Gimme Some Slack's Verse-free rule
    /// (src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs TheftSpotted / TheftGoodwillAccrue, POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK),
    /// so FlowWorks never references Gimme Some Slack. Keep the two in step.
    /// </summary>
    public static class RM_LiquidTheftMath
    {
        /// <summary>Does this witness catch the theft? Awake, not downed, not held by us, within sightRange cells, with line of sight.</summary>
        public static bool TheftSpotted(double dist, double sightRange, bool lineOfSight, bool awakeAndUp, bool heldByThief)
        {
            if (!(sightRange > 0) || double.IsNaN(dist) || heldByThief || !awakeAndUp || !lineOfSight) return false;
            return dist <= sightRange;
        }

        /// <summary>The steady leak: a caught theft accrues the ticks during which liquid was taken from (or put into) the tank;
        /// an idle tank accrues nothing. perDay goodwill per whole day, the remainder carried. Returns the change (0 or less).</summary>
        public static int TheftGoodwillAccrue(ref int drainTicks, int ticks, bool draining, int perDay, int ticksPerDay)
        {
            if (!draining || ticks <= 0 || ticksPerDay <= 0) return 0;
            drainTicks += ticks;
            int days = drainTicks / ticksPerDay;
            if (days <= 0) return 0;
            drainTicks -= days * ticksPerDay;
            return perDay > 0 ? -days * perDay : 0;
        }

        /// <summary>Was liquid taken from or put into the tank since the last look (its stock or its liquid changed)?</summary>
        public static bool Touched(int unitsBefore, object liquidBefore, int unitsNow, object liquidNow) => unitsBefore != unitsNow || !Equals(liquidBefore, liquidNow);
    }

    /// <summary>A pipe adapter's mode (rev 2 §3.10, build step L10): Send into the VE net, Take from it, or Shut.</summary>
    public enum RM_AdapterMode { Send, Take, Shut }

    public static class RM_AdapterRules
    {
        /// <summary>The saved keys to the mode: RM_adapterShut wins; else RM_adapterFeedNet true is Send, false Take.</summary>
        public static RM_AdapterMode ModeOf(bool feedNet, bool shut) => shut ? RM_AdapterMode.Shut : feedNet ? RM_AdapterMode.Send : RM_AdapterMode.Take;

        /// <summary>The gizmo's next mode: Send, Take, Shut, Send...</summary>
        public static RM_AdapterMode Next(RM_AdapterMode m) => (RM_AdapterMode)(((int)m + 1) % 3);

        /// <summary>A new build starts Shut (A16: two adapters cannot quietly churn a loop through a foreign net); an old save's
        /// adapter with no RM_adapterShut key keeps running.</summary>
        public static bool ShutOnSpawn(bool respawningAfterLoad, bool shut) => respawningAfterLoad ? shut : true;
    }

    public static class RM_LiquidNetKernel
    {
        /// <summary>The revision key: the map's bump counter with the two switches that change what conducts.</summary>
        public static long RevisionKey(int revision, bool pipesOn, bool hosesOn, bool foreignJoin = true) =>
            ((long)revision << 3) | (pipesOn ? 1L : 0L) | (hosesOn ? 2L : 0L) | (foreignJoin ? 4L : 0L);

        /// <summary>FNV-1a step over a link's identity (reel, inlet, far): RM_HoseLinks' backstop signature.</summary>
        public static ulong SigStep(ulong h, long reel, long inlet, long far)
        {
            h = (h ^ (ulong)reel) * 1099511628211UL;
            h = (h ^ (ulong)inlet) * 1099511628211UL;
            return (h ^ (ulong)far) * 1099511628211UL;
        }

        public const ulong SigSeed = 1469598103934665603UL;

        // ---------------------------------------------------------------- fill and draw plans (rev 2 §3.2, build step L3)
        /// <summary>Where <paramref name="units"/> go (rev 2 §3.2 fill order): the fullest tank that already holds the liquid and
        /// has room, then the next, then empty tanks; ties by lowest id. A level may be SPLIT across tanks (G8: 3 + 2 units of
        /// room take a 5-unit level). Returns (index into <paramref name="tanks"/>, units) parts, or null when the whole amount
        /// does not fit (a level is never part-placed). Depends only on stock and id, never on who asks or the list order.</summary>
        public static List<KeyValuePair<int, int>> FillPlan(IList<RM_TankView> tanks, int units)
        {
            if (units <= 0 || tanks == null) return null;
            var holders = new List<int>();
            var empties = new List<int>();
            for (int i = 0; i < tanks.Count; i++)
            {
                RM_TankView t = tanks[i];
                if (t.Cap <= 0) continue;
                if (t.Empty) empties.Add(i);
                else if (t.Holds && t.Units < t.Cap) holders.Add(i);
            }
            holders.Sort((a, b) =>
            {
                int f = tanks[b].Fraction.CompareTo(tanks[a].Fraction);
                return f != 0 ? f : tanks[a].Id.CompareTo(tanks[b].Id);
            });
            empties.Sort((a, b) => tanks[a].Id.CompareTo(tanks[b].Id));
            holders.AddRange(empties);
            return Take(holders, i => tanks[i].Cap - (tanks[i].Empty ? 0 : tanks[i].Units), units);
        }

        /// <summary>Where <paramref name="units"/> come from (rev 2 §3.2 draw order): the emptiest tank holding the liquid first,
        /// ties by lowest id, split across tanks. Null when the store holds fewer units than that.</summary>
        public static List<KeyValuePair<int, int>> DrawPlan(IList<RM_TankView> tanks, int units)
        {
            if (units <= 0 || tanks == null) return null;
            var holders = new List<int>();
            for (int i = 0; i < tanks.Count; i++) if (!tanks[i].Empty && tanks[i].Holds && tanks[i].Units > 0) holders.Add(i);
            holders.Sort((a, b) =>
            {
                int f = tanks[a].Fraction.CompareTo(tanks[b].Fraction);
                return f != 0 ? f : tanks[a].Id.CompareTo(tanks[b].Id);
            });
            return Take(holders, i => tanks[i].Units, units);
        }

        /// <summary>All the room the store has for the liquid (holders' room plus empty tanks).</summary>
        public static int FillRoom(IList<RM_TankView> tanks)
        {
            int r = 0;
            foreach (RM_TankView t in tanks) if (t.Cap > 0 && (t.Empty || t.Holds)) r += Math.Max(0, t.Cap - (t.Empty ? 0 : t.Units));
            return r;
        }

        /// <summary>All the units of the liquid the store holds.</summary>
        public static int DrawAvailable(IList<RM_TankView> tanks)
        {
            int r = 0;
            foreach (RM_TankView t in tanks) if (!t.Empty && t.Holds) r += Math.Max(0, t.Units);
            return r;
        }

        private static List<KeyValuePair<int, int>> Take(List<int> order, Func<int, int> room, int units)
        {
            var plan = new List<KeyValuePair<int, int>>();
            int left = units;
            foreach (int i in order)
            {
                int u = Math.Min(left, room(i));
                if (u <= 0) continue;
                plan.Add(new KeyValuePair<int, int>(i, u));
                left -= u;
                if (left == 0) return plan;
            }
            return null;
        }

        // ---------------------------------------------------------------- spills (rev 2 §3.7, build steps L7/L8)
        /// <summary>Pieces of spill filth for <paramref name="units"/> spilled: one per <paramref name="perFilth"/> units, rounded
        /// up, at least one for any spill (a spill is never invisible).</summary>
        public static int FilthCount(int units, int perFilth) => units <= 0 ? 0 : Math.Max(1, (units + Math.Max(1, perFilth) - 1) / Math.Max(1, perFilth));

        /// <summary>Units a Dump tank's slow drain sends out of one Outflow end this settle (rev 2 §3.5): a channel takes whole
        /// levels only (one pump level of <paramref name="level"/> units, when both the drain's budget <paramref name="left"/> and
        /// the stock allow it); dry ground takes whatever the budget and the stock allow. 0 = nothing.</summary>
        public static int DumpTake(int left, int stock, int level, bool channel) =>
            left <= 0 || stock <= 0 ? 0 : channel ? (left >= level && stock >= level && level > 0 ? level : 0) : Math.Min(left, stock);

        // ---------------------------------------------------------------- the pump as world mover (rev 2 §3.3, build step L6)
        /// <summary>A pump's next level (rev 2 §3.3): sources in order (its own reach first, then Intake ends by id), and for the
        /// first live source the destination is the first Outflow end, rotated by <paramref name="cycle"/>, that is not yet used
        /// this cycle and takes that source's liquid; else the tanks, when they take it; else the next source. False = nothing.
        /// <paramref name="outflow"/> = -1 means the tanks.</summary>
        public static bool PumpNext(int sources, Func<int, bool> sourceLive, int outflows, Func<int, int, bool> outflowTakes,
                                    ICollection<int> usedOutflows, Func<int, bool> tanksTake, int cycle, out int source, out int outflow)
        {
            source = outflow = -1;
            for (int s = 0; s < sources; s++)
            {
                if (!sourceLive(s)) continue;
                for (int k = 0; k < outflows; k++)
                {
                    int o = (((cycle + k) % outflows) + outflows) % outflows;
                    if (usedOutflows.Contains(o) || !outflowTakes(o, s)) continue;
                    source = s;
                    outflow = o;
                    return true;
                }
                if (tanksTake(s))
                {
                    source = s;
                    return true;
                }
            }
            return false;
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

        // ---------------------------------------------------------------- tank jobs: the settle (rev 2 §3.2, build step L4)
        /// <summary>PROVISIONAL (rev 2 §3.2): tank-to-tank units a tank sends or receives per settle (one per 250-tick cycle).</summary>
        public const int TankUnitsPerCycle = 10;

        /// <summary>One component's settle (rev 2 §3.2), planned from the stock at its START (G9: nothing received in this settle
        /// is sent on in it):
        ///   1. every Empty tank (by id) sends up to <paramref name="perCycle"/> to Fill tanks, then Store tanks, in fill order;
        ///   2. every Fill tank (by id) receives up to <paramref name="perCycle"/> from Empty tanks, then Store tanks, in draw order.
        /// Store tanks only buffer; Dump tanks never trade with tanks; a destination holds the same liquid or is empty. An empty
        /// Fill tank offered several liquids takes them in turn, one per cycle (<paramref name="cycle"/>), starting with the liquid
        /// of the lowest-id source. No tank sends, nor receives, more than <paramref name="perCycle"/> in one settle, steps
        /// together. Returns (source index, destination index, units) moves, in order.</summary>
        public static List<(int src, int dst, int units)> SettlePlan(IList<RM_SettleTank> tanks, int perCycle, int cycle)
        {
            var moves = new List<(int, int, int)>();
            int n = tanks?.Count ?? 0;
            if (n < 2 || perCycle <= 0) return moves;
            var units = new int[n];
            var liquid = new object[n];
            var sendable = new int[n];
            var sent = new int[n];
            var recv = new int[n];
            for (int i = 0; i < n; i++)
            {
                units[i] = Math.Max(0, tanks[i].Units);
                liquid[i] = units[i] > 0 ? tanks[i].Liquid : null;
                sendable[i] = units[i];
            }
            List<int> ById(RM_TankMode m) => Enumerable(n).Where(i => tanks[i].Mode == m).OrderBy(i => tanks[i].Id).ToList();
            double Frac(int i) => tanks[i].Cap > 0 ? units[i] / (double)tanks[i].Cap : 1.0;
            void Move(int s, int d, int u)
            {
                if (u <= 0) return;
                units[s] -= u;
                sendable[s] -= u;
                sent[s] += u;
                recv[d] += u;
                if (units[s] <= 0) liquid[s] = null;
                liquid[d] = liquid[d] ?? tanks[s].Liquid;
                units[d] += u;
                moves.Add((s, d, u));
            }
            // fill order among candidates for liquid l: holders (fullest first), then empties, ties by id
            List<int> FillOrder(IEnumerable<int> c, object l) => c.Where(i => liquid[i] == null || Equals(liquid[i], l))
                .Where(i => units[i] < tanks[i].Cap)
                .OrderBy(i => liquid[i] == null ? 1 : 0).ThenByDescending(i => liquid[i] == null ? 0 : Frac(i)).ThenBy(i => tanks[i].Id).ToList();
            List<int> DrawOrder(IEnumerable<int> c, object l) => c.Where(i => sendable[i] > 0 && liquid[i] != null && Equals(liquid[i], l))
                .OrderBy(i => Frac(i)).ThenBy(i => tanks[i].Id).ToList();
            List<int> empties = ById(RM_TankMode.Empty), fills = ById(RM_TankMode.Fill), stores = ById(RM_TankMode.Store);
            // 1. Empty tanks send
            foreach (int e in empties)
            {
                object l = liquid[e];
                int budget = Math.Min(perCycle - sent[e], sendable[e]);
                if (l == null || budget <= 0) continue;
                foreach (int d in FillOrder(fills, l).Concat(FillOrder(stores, l)))
                {
                    int u = Math.Min(Math.Min(budget, tanks[d].Cap - units[d]), perCycle - recv[d]);
                    Move(e, d, u);
                    budget -= Math.Max(0, u);
                    if (budget <= 0) break;
                }
            }
            // 2. Fill tanks receive
            foreach (int f in fills)
            {
                int budget = Math.Min(perCycle - recv[f], tanks[f].Cap - units[f]);
                if (budget <= 0) continue;
                object l = liquid[f];
                if (l == null)
                {
                    List<object> offered = empties.Concat(stores).Where(i => sendable[i] > 0 && liquid[i] != null)
                        .OrderBy(i => tanks[i].Id).Select(i => liquid[i]).Distinct().ToList();
                    if (offered.Count == 0) continue;
                    l = offered[((cycle % offered.Count) + offered.Count) % offered.Count];
                }
                foreach (int src in DrawOrder(empties, l).Concat(DrawOrder(stores, l)))
                {
                    int u = Math.Min(Math.Min(budget, sendable[src]), perCycle - sent[src]);
                    Move(src, f, u);
                    budget -= Math.Max(0, u);
                    if (budget <= 0) break;
                }
            }
            return moves;
        }

        private static IEnumerable<int> Enumerable(int n)
        {
            for (int i = 0; i < n; i++) yield return i;
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
