// HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS: the replay engine. It drives the REAL Verse-free cores (HoseWorldPatch, HoseWorldDirty,
// HoseMath.RoutePulled / CheckReplan, CordSig, RM_NetComponents, RM_NetTopologyCache, RM_LiquidNetKernel.SettlePlan / RouteLive,
// RM_LiquidTransfer.Move) on the schedule the game drives them, with every mirrored line citing the production line it copies.
//
// THE MIRROR IS THE DRIFT RISK. The schedule itself (which call happens at which tick) lives in RM_MapComponent_Hoses (Verse) and
// RM_LiquidNet (Verse); this file copies it. When either changes its schedule, change the matching block here in the same commit.
// The cure is the follow-up that moves the schedule into a Verse-free class both the game and this replay compile.
//
// Simplifications (each one says what the replay can therefore NOT see):
// - Cell rule: the trace chars stand in for LiveRule (fog, rigs, ladders, bands and climb masks are absent; bands are off).
// - Liquid graph: tanks, relays and hose links only (no pipes, machines, ports or dumps; theft off). A tank does not conduct
//   (RM_NetComponents.Conducts), so two tanks share a network only through one link or through relays.
// - A link is live while its reel is laid (RM_HoseLinks.Live also reads the lay's eligibility; a failed lay stays live here).
// - The draw-time EnsureLay is modelled as "every laid reel without a lay key is laid this tick" (the game lays it on the next
//   frame that draws it; a settings flip with every hose on screen is that worst case).
// - The trail check in TickRecheckBody is not mirrored.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Replay
{
    /// <summary>Faults injected on purpose, each of which must turn its gate red (selftest_hose_replay.py proves it).</summary>
    [Flags]
    internal enum Fault
    {
        None = 0,
        CutNoRoute = 1,     // a cut neither bumps the topology revision nor is caught by RouteLive: flow crosses the cut  -> noflow
        Leak = 2,           // the destination leg books one unit fewer than it was given                                -> conserve
        PatchSkip = 4,      // every second patch is skipped (the dirty list is dropped unpatched)                           -> patch
        Nondet = 8,         // the settle budget reads a process-wide counter, so run 2 differs from run 1                   -> determinism
        Alloc = 16,         // the cell rule allocates per cell                                                              -> alloc
        StaleComps = 32,    // a (re)lay does not bump the topology revision: the cached components miss the new link        -> comps
        DoubleWork = 64,    // every recheck hashes its corridor and checks its replan twice                                 -> ceiling
    }

    internal sealed class ReplayRule : IHoseCellRule
    {
        public readonly char[] Cells;
        public readonly int W;
        public bool Alloc;
        public object Sink;

        public ReplayRule(char[] cells, int w) { Cells = cells; W = w; }

        public bool BandsActive => false;
        public bool Linked(Cell a, Cell b, int ba, int bb) => false;

        public void WriteCell(CordWorld w, Cell c)
        {
            if (Alloc) Sink = new int[4];
            Write(w, c, Cells[c.Z * W + c.X]);
        }

        /// <summary>The trace's stand-in for RM_MapComponent_Hoses.LiveRule on a cleared cell: walls and rock block, a door is a door,
        /// free water costs 3, a tree 1.5, a puddle 0.5 (an invented cost so a rain burst changes the signature).</summary>
        public static void Write(CordWorld w, Cell c, char ch)
        {
            switch (ch)
            {
                case '#': w.SetBlocked(c, BlockKind.Wall); break;
                case 'r': w.SetBlocked(c, BlockKind.Rock); break;
                case '~': w.SetExtraCost(c, 3f); break;
                case 'd': w.SetDoor(c); break;
                case 't': w.SetExtraCost(c, 1.5f); break;
                case 'p': w.SetExtraCost(c, 0.5f); break;
            }
        }
    }

    internal sealed class RTank
    {
        public int Id, Units, Cap;
        public object Liquid;
        public RM_TankMode Mode;
        public override string ToString() => "T" + Id;
    }

    internal sealed class RRelay
    {
        public int Id;
        public override string ToString() => "R" + Id;
    }

    internal sealed class RReel
    {
        public TraceReel T;
        public HoseReelRect Rect;
        public Cell Far;
        public bool Laid = true;
        public bool HasKey;          // RM_MapComponent_Hoses: r.layKey != null
        public List<V2> Lay;         // r.lay (the pulled polyline stands in for the HoseLay's Flat points)
        public ulong CorridorHash, GeomHash;
        public string LastLayReason;
        public int LayEpoch;
        public RM_NetLink Link;
        public override string ToString() => "reel" + T.Id;
    }

    internal sealed class ReplayGraph : IRM_NetGraph
    {
        private static readonly object[] None = new object[0];
        public readonly Dictionary<object, List<RM_NetLink>> At = new Dictionary<object, List<RM_NetLink>>();
        public Func<RM_NetLink, bool> Live;

        public void Add(RM_NetLink l)
        {
            foreach (object end in new[] { l.A, l.B })
            {
                if (!At.TryGetValue(end, out List<RM_NetLink> list)) At[end] = list = new List<RM_NetLink>();
                list.Add(l);
            }
        }

        public RM_NetRole RoleOf(object v) => v is RTank ? RM_NetRole.Tank : v is RRelay ? RM_NetRole.Relay : RM_NetRole.None;
        public IEnumerable<object> OriginTanks(object member) => None;
        public IEnumerable<object> OriginPipeCells(object member) => None;
        public IEnumerable<object> PipeTanks(object pipeCell) => None;
        public IEnumerable<object> PipeMachines(object pipeCell) => None;
        public IEnumerable<object> PipeNeighbours(object pipeCell) => None;
        public bool PipesEnabled => false;
        public int Order(object m) => m is RTank t ? t.Id : m is RRelay r ? 100000 + r.Id : 0;

        public IList<RM_NetLink> LinksAt(object v)
        {
            var l = new List<RM_NetLink>();
            if (v != null && At.TryGetValue(v, out List<RM_NetLink> all))
                foreach (RM_NetLink x in all) if (Live(x)) l.Add(x);
            return l;
        }
    }

    internal sealed class ReplayResult
    {
        public string Scenario;
        public Counters C;
        public ulong[] Fingerprints;
        public readonly List<string> Failures = new List<string>();
        public readonly Dictionary<string, int> GateFails = new Dictionary<string, int>();
        public int OracleChecks, PatchChecks, CompChecks, NoCompMoves;
        /// <summary>Trace events never applied: a tick outside 0..Ticks-1 or a phase other than 0..2 (a blind replay otherwise).</summary>
        public int DroppedEvents;

        public void Fail(string gate, int tick, string detail)
        {
            GateFails.TryGetValue(gate, out int n);
            GateFails[gate] = n + 1;
            if (n < 5) Failures.Add(gate + " @" + tick + ": " + detail);
        }
    }

    internal sealed class ReplayTick
    {
        // RM_MapComponent_Hoses.cs (HEAD 2026-10-28): LayWorldMaxAge = 60; dirty = new HoseWorldDirty(16384); recheck every 250 ticks
        internal const int LayWorldMaxAge = 60, DirtyCapacity = 16384, RecheckTicks = 250;
        private static int runsInProcess;   // only the Nondet fault reads it

        private readonly Trace trace;
        private readonly Fault fault;
        private readonly bool oracle;
        private readonly int W, H;
        private readonly char[] cells;
        private readonly ReplayRule rule;
        private readonly CordWorld truth, oracleWorld;
        private readonly HoseWorldDirty dirty = new HoseWorldDirty(DirtyCapacity);
        private CordWorld world, spare;
        private int mapVersion, worldVersion = -1, spareTick = -1, patchCalls, now;

        private readonly List<RTank> tanks = new List<RTank>();
        private readonly Dictionary<int, RTank> tankById = new Dictionary<int, RTank>();
        private readonly List<RRelay> relays = new List<RRelay>();
        private readonly List<RReel> reels = new List<RReel>();
        private readonly Dictionary<int, RReel> reelById = new Dictionary<int, RReel>();
        private readonly Dictionary<RM_NetLink, RReel> reelOfLink = new Dictionary<RM_NetLink, RReel>();
        private readonly ReplayGraph graph = new ReplayGraph();
        private readonly RM_NetTopologyCache topo = new RM_NetTopologyCache();
        private int revision, liveSerial, ufSerial = -1;
        private int[] uf;
        private long totalUnits;
        private readonly object[] liquids = { "Water", "Oil", "Brine", "Acid" };
        private readonly Counters C;
        private readonly ReplayResult R;

        public ReplayTick(Trace t, Fault fault, bool oracle)
        {
            trace = t;
            this.fault = fault;
            this.oracle = oracle;
            W = t.Width;
            H = t.Height;
            cells = (char[])t.Cells.Clone();
            rule = new ReplayRule(cells, W) { Alloc = (fault & Fault.Alloc) != 0 };
            truth = new CordWorld(W, H);
            HoseWorldPatch.Full(truth, new ReplayRule(cells, W));
            if (oracle) oracleWorld = new CordWorld(W, H);
            graph.Live = l => reelOfLink[l].Laid;
            foreach (TraceTank tt in t.Tanks)
            {
                var k = new RTank { Id = tt.Id, Units = tt.Units, Cap = tt.Cap, Mode = tt.Mode, Liquid = tt.Units > 0 ? liquids[tt.Liquid % liquids.Length] : null };
                tanks.Add(k);
                tankById[k.Id] = k;
                totalUnits += k.Units;
            }
            tanks.Sort((a, b) => a.Id.CompareTo(b.Id));
            var relayById = new Dictionary<int, RRelay>();
            foreach (TraceReel tr in t.Reels)
            {
                var r = new RReel { T = tr, Rect = new HoseReelRect(tr.X0, tr.Z0, 2, 2), Far = new Cell(tr.FarX, tr.FarZ) };
                object b;
                if (tr.TankB >= 0) b = tankById[tr.TankB];
                else
                {
                    int rid = -tr.TankB - 1;
                    if (!relayById.TryGetValue(rid, out RRelay rel)) { relayById[rid] = rel = new RRelay { Id = rid }; relays.Add(rel); }
                    b = rel;
                }
                r.Link = new RM_NetLink { Id = tr.Id, A = tankById[tr.TankA], B = b, Reel = r };
                reelOfLink[r.Link] = r;
                graph.Add(r.Link);
                reels.Add(r);
                reelById[tr.Id] = r;
            }
            reels.Sort((a, b) => a.T.Id.CompareTo(b.T.Id));
            C = new Counters(t.Ticks);
            R = new ReplayResult { Scenario = t.Name, C = C, Fingerprints = new ulong[t.Ticks] };
        }

        public ReplayResult Run()
        {
            runsInProcess++;
            int ev = 0;
            List<TraceEvent> events = trace.Events;
            for (now = 0; now < trace.Ticks; now++)
            {
                C.Tick = now;
                ev = Phase(events, ev, 0);
                HoseTick();
                ev = Phase(events, ev, 1);
                // RM_LiquidNet: the tank settle runs once per RM_PumpMath.CycleTicks
                if (now % RM_PumpMath.CycleTicks == 0) Settle();
                ev = Phase(events, ev, 2);
                Conservation();
                R.Fingerprints[now] = Fingerprint();
            }
            R.DroppedEvents += events.Count - ev;
            return R;
        }

        private int Phase(List<TraceEvent> events, int ev, int phase)
        {
            while (ev < events.Count && events[ev].Tick < now) { ev++; R.DroppedEvents++; }   // before 0 or a phase past 2: counted, never silent
            while (ev < events.Count && events[ev].Tick == now && events[ev].Phase == phase) Apply(events[ev++]);
            return ev;
        }

        // ---------------------------------------------------------------- hose world (RM_MapComponent_Hoses.cs World/PatchWorld/BuildWorld/MarkDirty)

        /// <summary>RM_MapComponent_Hoses.World (non-legacy frame): patch the dirty cells into a version-valid snapshot, else rebuild whole.</summary>
        private CordWorld World(int maxAge = 0)
        {
            if (world != null && worldVersion == mapVersion && dirty.Count > 0) PatchWorld();
            if (world != null && worldVersion == mapVersion) return world;
            return BuildWorld();
        }

        private void PatchWorld()
        {
            C.Begin(Sys.World);
            C.Add(Work.Patches);
            C.Add(Work.CellsPatched, dirty.Count);
            bool skip = (fault & Fault.PatchSkip) != 0 && (patchCalls & 1) == 1;
            if (!skip)
            {
                long b0 = GC.GetAllocatedBytesForCurrentThread();
                HoseWorldPatch.Patch(world, dirty, rule);
                long db = GC.GetAllocatedBytesForCurrentThread() - b0;
                if (patchCalls > 0) { C.PatchBytesWarm += db; C.PatchCallsWarm++; }
            }
            patchCalls++;
            dirty.Clear();
            C.End();
            if (oracle) CheckPatch();
        }

        /// <summary>RM_MapComponent_Hoses.BuildWorld: reuse the spare snapshot unless it was handed out this tick, fill it whole.</summary>
        private CordWorld BuildWorld()
        {
            C.Begin(Sys.World);
            C.Add(Work.WholeRebuilds);
            int version = mapVersion;
            CordWorld cw = spare;
            spare = null;
            if (cw != null && spareTick != now) cw.Reset();
            else cw = new CordWorld(W, H);
            if (world != null) { spare = world; spareTick = now; }
            HoseWorldPatch.Full(cw, rule);
            dirty.Ensure(W, H);
            dirty.Clear();
            world = cw;
            worldVersion = version;
            C.End();
            if (oracle) CheckPatch();   // a reused spare snapshot must come out equal to a fresh Full too (GPT review 2026-10-28)
            return cw;
        }

        private void MapChanged() => mapVersion++;

        /// <summary>RM_MapComponent_Hoses.CellChanged (line 422) after the cell changed on the live map.</summary>
        private void SetCell(int x, int z, char ch)
        {
            if (x < 0 || z < 0 || x >= W || z >= H) return;
            int i = z * W + x;
            if (cells[i] == ch) return;
            cells[i] = ch;
            var c = new Cell(x, z);
            truth.ClearCell(c);
            ReplayRule.Write(truth, c, ch);
            if (world == null || worldVersion != mapVersion) return;
            if (CordSig.CellSig(world, c) != CordSig.CellSig(truth, c) && !MarkDirty(x, z)) MapChanged();
        }

        /// <summary>RM_MapComponent_Hoses.MarkDirty: past the capacity the list is dropped and the caller bumps the map version.</summary>
        private bool MarkDirty(int x, int z)
        {
            C.Add(Work.CellsMarked);
            dirty.Ensure(W, H);
            dirty.Mark(x, z);
            if (!dirty.Overflow) return true;
            dirty.Clear();
            C.Add(Work.Overflows);
            return false;
        }

        private void CheckPatch()
        {
            R.OracleChecks++;
            R.PatchChecks++;
            HoseWorldPatch.Full(oracleWorld, new ReplayRule(cells, W));
            for (int z = 0; z < H; z++)
                for (int x = 0; x < W; x++)
                {
                    var c = new Cell(x, z);
                    if (CordSig.CellSig(world, c) != CordSig.CellSig(oracleWorld, c) || world.BlockAt(c) != oracleWorld.BlockAt(c))
                    {
                        R.Fail("patch", now, "patched world differs from Full() at " + x + "," + z + " (char '" + cells[z * W + x] + "')");
                        return;
                    }
                }
        }

        // ---------------------------------------------------------------- reels (RM_MapComponent_Hoses.TickBody / TickRecheckBody / EnsureLay)

        private void HoseTick()
        {
            // TickBody: for each reel, if ((now + r.parent.thingIDNumber) % 250 == 0) TickRecheck(r, now)
            foreach (RReel r in reels)
                if (r.Laid && (now + r.T.Id) % RecheckTicks == 0) Recheck(r);
            // the draw-time EnsureLay (see the header): a laid reel without a lay key is laid now
            foreach (RReel r in reels)
                if (r.Laid && !r.HasKey) EnsureLay(r);
        }

        /// <summary>TickRecheckBody: EnsureLay, then if the live corridor hash moved, CheckReplan on the version-valid snapshot:
        /// retract on a reason, else drop the lay key (re-laid next draw).</summary>
        private void Recheck(RReel r)
        {
            C.Begin(Sys.Recheck);
            C.Add(Work.Rechecks);
            EnsureLay(r);
            bool twice = (fault & Fault.DoubleWork) != 0;
            if (r.HasKey && (r.Lay == null || CorridorHashLive(r.Lay) != r.CorridorHash | (twice && CorridorHashLive(r.Lay) != r.CorridorHash)))
            {
                CordWorld w = World(LayWorldMaxAge);
                C.Add(Work.CheckReplans);
                string why = HoseMath.CheckReplan(w, r.Rect, r.Far, r.T.MaxLength, r.Lay == null, r.LastLayReason);
                if (twice) { C.Add(Work.CheckReplans); HoseMath.CheckReplan(w, r.Rect, r.Far, r.T.MaxLength, r.Lay == null, r.LastLayReason); }
                if (why != null) Retract(r);
                else { r.HasKey = false; r.LayEpoch++; }
            }
            C.End();
        }

        private void EnsureLay(RReel r)
        {
            if (!r.Laid || r.HasKey) return;
            C.Begin(Sys.Lay);
            C.Add(Work.Lays);
            CordWorld w = World(LayWorldMaxAge);
            List<V2> lay = HoseMath.RoutePulled(w, r.Rect, r.Far, r.T.MaxLength);
            r.HasKey = true;
            if (lay == null || lay.Count < 2)
            {
                r.Lay = null;
                r.LastLayReason = "noroute";
                r.GeomHash = 0;
                C.Add(Work.LayFails);
            }
            else
            {
                r.Lay = lay;
                r.LastLayReason = null;
                r.CorridorHash = CorridorHash(lay, w);
                r.GeomHash = GeometryHash(lay);
            }
            C.End();
        }

        private ulong CorridorHashLive(List<V2> lay) => CorridorHash(lay, truth);

        /// <summary>RM_MapComponent_Hoses.CorridorHash (line ~946): FNV over CellSig of the lay's bounding box padded by 2.</summary>
        private ulong CorridorHash(List<V2> lay, CordWorld sigOf)
        {
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            foreach (V2 p in lay) { Cell c = p.Floor; x0 = Math.Min(x0, c.X); z0 = Math.Min(z0, c.Z); x1 = Math.Max(x1, c.X); z1 = Math.Max(z1, c.Z); }
            ulong h = 1469598103934665603UL;
            for (int z = z0 - 2; z <= z1 + 2; z++)
                for (int x = x0 - 2; x <= x1 + 2; x++)
                    h = (h ^ CordSig.CellSig(sigOf, new Cell(x, z))) * 1099511628211UL;
            C.Add(Work.CorridorCells, (long)(x1 - x0 + 5) * (z1 - z0 + 5));
            return h;
        }

        private static ulong GeometryHash(List<V2> lay)
        {
            ulong h = 1469598103934665603UL;
            foreach (V2 p in lay)
            {
                // exact bits, not rounded: 0.9999 and 1.0001 floor to different cells (GPT review 2026-10-28)
                h = (h ^ unchecked((ulong)BitConverter.DoubleToInt64Bits(p.X))) * 1099511628211UL;
                h = (h ^ unchecked((ulong)BitConverter.DoubleToInt64Bits(p.Z))) * 1099511628211UL;
            }
            return h;
        }

        private void Retract(RReel r)
        {
            C.Add(Work.Retracts);
            Unlay(r, bump: true);
        }

        private void Unlay(RReel r, bool bump)
        {
            r.Laid = false;
            r.HasKey = false;
            r.Lay = null;
            r.GeomHash = 0;
            liveSerial++;
            if (bump) revision++;
        }

        // ---------------------------------------------------------------- events

        private void Apply(TraceEvent e)
        {
            int[] a = e.A;
            switch (e.Kind)
            {
                case "cell":
                    C.Begin(Sys.World);
                    SetCell(a[0], a[1], e.C);
                    C.End();
                    break;
                case "rect":
                    C.Begin(Sys.World);
                    // a wall is never built on natural rock: in the game rock->wall is two events (mined to floor, then built),
                    // and CellChanged's CellSig test cannot see a direct Rock->Wall swap (CellSig omits BlockKind; lesson
                    // hose-cellsig-omits-blockkind). Writing one here would only measure a change the game never makes.
                    for (int z = a[1]; z <= a[3]; z++)
                        for (int x = a[0]; x <= a[2]; x++)
                            if (!(e.C == '#' && x >= 0 && z >= 0 && x < W && z < H && cells[z * W + x] == 'r')) SetCell(x, z, e.C);
                    C.End();
                    break;
                case "rain":
                    C.Begin(Sys.World);
                    Rain(a[0], a[1]);
                    C.End();
                    break;
                case "cut":
                    if (reelById.TryGetValue(a[0], out RReel cut) && cut.Laid) Unlay(cut, bump: (fault & Fault.CutNoRoute) == 0);
                    break;
                case "lay":
                    if (reelById.TryGetValue(a[0], out RReel lay) && !lay.Laid)
                    {
                        lay.Laid = true;
                        lay.HasKey = false;
                        liveSerial++;
                        if ((fault & Fault.StaleComps) == 0) revision++;
                    }
                    break;
                case "settings":
                    // a settings change touching every hose: version bump, every lay key dropped (each reel re-lays)
                    MapChanged();
                    foreach (RReel r in reels) if (r.Laid) r.HasKey = false;
                    break;
                case "version":
                    MapChanged();
                    break;
                case "read":
                    World();
                    break;
                case "move":
                    MoveRequest(a[0], a[1], a[2]);
                    break;
                default:
                    throw new InvalidOperationException("unknown event kind '" + e.Kind + "'");
            }
        }

        /// <summary>n distinct walkable cells flip puddle &lt;-&gt; dry, visited in a fixed stride permutation of the map from salt.</summary>
        private void Rain(int n, int salt)
        {
            int total = W * H, stride = Stride(total), done = 0;
            for (int k = 0; k < total && done < n; k++)
            {
                int i = (int)(((long)k * stride + salt) % total);
                char ch = cells[i];
                if (ch != '.' && ch != 'p') continue;
                SetCell(i % W, i / W, ch == '.' ? 'p' : '.');
                done++;
            }
        }

        internal static int Stride(int total)
        {
            int s = 7919;
            while (Gcd(s, total) != 1) s += 2;
            return s;
        }

        private static int Gcd(int a, int b) { while (b != 0) { int t = a % b; a = b; b = t; } return a; }

        // ---------------------------------------------------------------- liquid (RM_LiquidNet.Components / settle / RouteDeadBump)

        /// <summary>RM_LiquidNet.Components: RM_NetTopologyCache.Get(RevisionKey(revision, pipesOn, hosesOn, theft), new RM_NetComponents(graph)).</summary>
        private RM_NetComponents Components()
        {
            int before = topo.Revisions;
            RM_NetComponents comps = topo.Get(RM_LiquidNetKernel.RevisionKey(revision, false, true, false), () => new RM_NetComponents(graph));
            if (topo.Revisions != before) C.Add(Work.CompRevisions);
            return comps;
        }

        /// <summary>RM_LiquidNet settle (Machinery/RM_LiquidNet.cs ~760-825): movers are Fill/Empty tanks; for every component of a
        /// mover not yet settled this cycle, SettlePlan over its tanks with one shared per-tank budget, then each planned move
        /// checks its route live (RouteDeadBump) before RM_LiquidTransfer.Move with two store legs.</summary>
        private void Settle()
        {
            C.Begin(Sys.Settle);
            var movers = new List<RTank>();
            foreach (RTank t in tanks) if (t.Mode == RM_TankMode.Fill || t.Mode == RM_TankMode.Empty) movers.Add(t);
            if (movers.Count == 0) { C.End(); return; }
            RM_NetComponents comps = Components();
            int builds0 = comps.Builds;
            var done = new HashSet<RM_NetComponent>();
            var sentById = new Dictionary<int, int>();
            var recvById = new Dictionary<int, int>();
            int cycle = now / RM_PumpMath.CycleTicks;
            int per = Math.Max(1, RM_LiquidNetKernel.TankUnitsPerCycle);
            if ((fault & Fault.Nondet) != 0) per += runsInProcess % 2;
            foreach (RTank mover in movers)
            {
                foreach (RM_NetComponent c in comps.ComponentsOf(mover))
                {
                    if (c.Refused || !done.Add(c)) continue;
                    var ts = new List<RTank>();
                    foreach (object o in c.Tanks) if (o is RTank t) ts.Add(t);
                    var view = new List<RM_SettleTank>(ts.Count);
                    foreach (RTank t in ts) view.Add(new RM_SettleTank(t.Id, t.Units, t.Cap, t.Liquid, t.Mode));
                    C.Add(Work.CompSize, c.Size);
                    foreach ((int si, int di, int n) in RM_LiquidNetKernel.SettlePlan(view, per, cycle, sentById, recvById))
                    {
                        C.Add(Work.SettleMoves);
                        RTank src = ts[si], dst = ts[di];
                        int moved = Transfer(comps, c, src, dst, n);
                        if (moved <= 0) continue;
                        C.Add(Work.UnitsSettled, moved);
                        sentById[src.Id] = (sentById.TryGetValue(src.Id, out int s0) ? s0 : 0) + moved;
                        recvById[dst.Id] = (recvById.TryGetValue(dst.Id, out int r0) ? r0 : 0) + moved;
                    }
                }
            }
            C.Add(Work.CompBuilds, comps.Builds - builds0);
            C.End();
            if (oracle) CheckComponents(comps);
        }

        /// <summary>A trace "move a b units": the first live component holding both tanks carries it (a pump or player order).</summary>
        private void MoveRequest(int a, int b, int units)
        {
            if (!tankById.TryGetValue(a, out RTank src) || !tankById.TryGetValue(b, out RTank dst)) return;
            C.Begin(Sys.Settle);
            RM_NetComponents comps = Components();
            int builds0 = comps.Builds;
            RM_NetComponent via = null;
            foreach (RM_NetComponent c in comps.ComponentsOf(src))
                if (!c.Refused && c.Tanks.Contains(dst)) { via = c; break; }
            if (via == null) R.NoCompMoves++;
            else Transfer(comps, via, src, dst, units);
            C.Add(Work.CompBuilds, comps.Builds - builds0);
            C.End();
            if (oracle) CheckComponents(comps);   // the components a move used, not only those Settle used (GPT review 2026-10-28)
        }

        private int Transfer(RM_NetComponents comps, RM_NetComponent c, RTank src, RTank dst, int n)
        {
            C.Begin(Sys.Move);
            List<RM_NetLink> route = comps.RouteIn(c, src, dst);
            // RouteDeadBump (RM_LiquidNet.cs:394): an empty or null route passes; a route over a dead link bumps the revision
            if ((fault & Fault.CutNoRoute) == 0 && route != null && route.Count > 0 && !RM_LiquidNetKernel.RouteLive(route, graph.Live))
            {
                revision++;
                C.Add(Work.RouteDead);
                C.End();
                return 0;
            }
            object liquid = src.Liquid;
            bool leak = (fault & Fault.Leak) != 0;
            int moved = RM_LiquidTransfer.Move(n,
                RM_TransferLeg.Store(k => src.Units >= k, k => Remove(src, k), k => Add(src, liquid, k, false)),
                RM_TransferLeg.Store(k => CanAccept(dst, liquid, k), k => Add(dst, liquid, k, leak), k => Remove(dst, k)),
                out RM_MoveOutcome mv);
            if (moved > 0)
            {
                C.Add(Work.Transfers);
                if (!Connected(src, dst)) R.Fail("noflow", now, moved + " units moved T" + src.Id + "->T" + dst.Id + " with no live hose path between them");
            }
            else C.Add(Work.TransferRefused);
            C.End();
            return moved;
        }

        private static bool Remove(RTank t, int k)
        {
            if (k <= 0 || t.Units < k) return false;
            t.Units -= k;
            if (t.Units == 0) t.Liquid = null;
            return true;
        }

        private static bool CanAccept(RTank t, object liquid, int k) => k > 0 && liquid != null && t.Units + k <= t.Cap && (t.Units == 0 || Equals(t.Liquid, liquid));

        private static bool Add(RTank t, object liquid, int k, bool leak)
        {
            if (!CanAccept(t, liquid, k)) return false;
            t.Units += leak && k > 1 ? k - 1 : k;
            t.Liquid = liquid;
            return true;
        }

        // ---------------------------------------------------------------- oracles and gates

        /// <summary>An independent union-find over live links and relays (a tank never conducts), rebuilt when liveness changes.</summary>
        private int Root(int i) { while (uf[i] != i) { uf[i] = uf[uf[i]]; i = uf[i]; } return i; }

        private void EnsureUf()
        {
            if (ufSerial == liveSerial && uf != null) return;
            ufSerial = liveSerial;
            int nl = reels.Count;
            if (uf == null) uf = new int[nl + relays.Count];
            for (int i = 0; i < uf.Length; i++) uf[i] = i;
            for (int i = 0; i < nl; i++)
            {
                RReel r = reels[i];
                if (!r.Laid) continue;
                if (r.Link.B is RRelay rel) { int a = Root(i), b = Root(nl + relays.IndexOf(rel)); if (a != b) uf[a] = b; }
            }
        }

        private int LinkIndex(RM_NetLink l) => reels.IndexOf(reelOfLink[l]);

        private bool Connected(RTank a, RTank b)
        {
            EnsureUf();
            if (!graph.At.TryGetValue(a, out List<RM_NetLink> la) || !graph.At.TryGetValue(b, out List<RM_NetLink> lb)) return false;
            foreach (RM_NetLink x in la)
            {
                if (!reelOfLink[x].Laid) continue;
                int rx = Root(LinkIndex(x));
                foreach (RM_NetLink y in lb) if (reelOfLink[y].Laid && Root(LinkIndex(y)) == rx) return true;
            }
            return false;
        }

        private void CheckComponents(RM_NetComponents comps)
        {
            R.OracleChecks++;
            R.CompChecks++;
            EnsureUf();
            var size = new Dictionary<int, int>();
            for (int i = 0; i < reels.Count; i++) if (reels[i].Laid) { int r = Root(i); size[r] = (size.TryGetValue(r, out int n) ? n : 0) + 1; }
            foreach (RM_NetComponent c in comps.Built)
            {
                // the replay has ~320 members, far under MaxConductors: a refusal here is a defect, not policy
                if (c.Refused && c.Size <= RM_NetComponents.MaxConductors) { R.Fail("comps", now, "component " + c.Id + " refused at size " + c.Size); return; }
                if (c.Refused || c.Links.Count == 0) continue;
                int root = -1;
                foreach (RM_NetLink l in c.Links)
                {
                    if (!reelOfLink[l].Laid) { R.Fail("comps", now, "component " + c.Id + " holds dead link " + l.Id); return; }
                    int r = Root(LinkIndex(l));
                    if (root < 0) root = r;
                    else if (r != root) { R.Fail("comps", now, "component " + c.Id + " joins two union-find classes"); return; }
                }
                if (size[root] != c.Links.Count) { R.Fail("comps", now, "component " + c.Id + " has " + c.Links.Count + " links, union-find class has " + size[root]); return; }
                // its tanks are exactly the tanks at its links' ends (a tank attaches only by hose here): a stale or extra tank
                // would let MoveRequest pick it as a carrier
                var want = new HashSet<RTank>();
                foreach (RM_NetLink l in c.Links) { if (l.A is RTank ta) want.Add(ta); if (l.B is RTank tb) want.Add(tb); }
                var have = new HashSet<RTank>();
                foreach (object o in c.Tanks) if (o is RTank t) have.Add(t);
                if (!want.SetEquals(have)) { R.Fail("comps", now, "component " + c.Id + " holds " + have.Count + " tanks, its links reach " + want.Count); return; }
            }
            // every live link at a mover is in one of the mover's components
            foreach (RTank t in tanks)
            {
                if (t.Mode != RM_TankMode.Fill && t.Mode != RM_TankMode.Empty) continue;
                if (!graph.At.TryGetValue(t, out List<RM_NetLink> ls)) continue;
                IReadOnlyList<RM_NetComponent> mine = comps.ComponentsOf(t);
                foreach (RM_NetLink l in ls)
                {
                    if (!reelOfLink[l].Laid) continue;
                    bool found = false;
                    foreach (RM_NetComponent c in mine) if (c.Links.Contains(l)) { found = true; break; }
                    if (!found) { R.Fail("comps", now, "live link " + l.Id + " at T" + t.Id + " is in none of its components"); return; }
                }
            }
        }

        private void Conservation()
        {
            long sum = 0;
            foreach (RTank t in tanks) sum += t.Units;
            if (sum != totalUnits) { R.Fail("conserve", now, "tank units " + sum + " != " + totalUnits); totalUnits = sum; }
        }

        private ulong Fingerprint()
        {
            ulong h = 1469598103934665603UL;
            foreach (RTank t in tanks) h = (h ^ (ulong)(uint)t.Units ^ ((ulong)(t.Liquid == null ? 0 : Array.IndexOf(liquids, t.Liquid) + 1) << 40)) * 1099511628211UL;
            foreach (RReel r in reels)
            {
                h = (h ^ (r.Laid ? 1UL : 0UL) ^ (r.HasKey ? 2UL : 0UL) ^ (r.LastLayReason != null ? 4UL : 0UL) ^ r.GeomHash) * 1099511628211UL;
                h = (h ^ r.CorridorHash ^ ((ulong)(uint)r.LayEpoch << 32)) * 1099511628211UL;   // state the next recheck branches on
            }
            h = (h ^ (ulong)(uint)mapVersion ^ ((ulong)(uint)revision << 32)) * 1099511628211UL;
            return h;
        }
    }
}
