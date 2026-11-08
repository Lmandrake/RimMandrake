// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Orchestration of nodal.build_nodal for phase 1a: reduce -> plan -> lay, cached per edge.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public enum DecalKind { Plug, JunctionTape, JunctionTin, StubWall, StubRock, PowerStrip, FrayDead, FrayLive, PowerStripDark }

    /// <summary>A decal's drawn height over its width. The power strip's art is 64x32 lit AND dark (GPT source read 2026-10-06
    /// A19: the dark strip drew at aspect 1, twice as tall as the lit one).</summary>
    public static class DecalAspect
    {
        public static float Of(DecalKind k) => k == DecalKind.PowerStrip || k == DecalKind.PowerStripDark ? 0.5f : 1f;
    }

    /// <summary>What a pile (tangle) and a device stub are built from (owner review 2026-10-04 B1/B2/B13/B15): power strips
    /// only for the modern extension-cord look; every other look plugs its cables into many + and T junction boxes.</summary>
    public enum PileArt { Junctions, Strips }

    public struct CordDecal
    {
        public DecalKind Kind;
        internal V2 Pos;
        /// <summary>Radians, 0 = +X; the art's long axis points along it.</summary>
        public double Angle;
        public double Scale;
        /// <summary>Extra scale along the art's own X axis (0 = none): the rock-entry hole is foreshortened as if cut
        /// into an angled face (owner review 2026-10-04 B4).</summary>
        public double Squash;
        /// <summary>A live fray that rides the whipping tail: printed statically only with whip off.</summary>
        public bool OnWhip;
        /// <summary>The fray on a wall end's hanging tail: it sways with that tail, so while the tail sways the component draws it, not the section.</summary>
        public bool OnSwayTail;
        /// <summary>Round 4: the art sub-rectangle printed (u along art X, v along art Z); U1 = 0 means the whole canvas. A wall
        /// plate prints only its plate, never the art's own curl of cord (WallMount).</summary>
        public double U0, U1, V0, V1;
        internal CordDecal(DecalKind k, V2 p, double a, double s) { Kind = k; Pos = p; Angle = a; Scale = s; OnWhip = false; Squash = 0; U0 = U1 = V0 = V1 = 0; }
        public bool Cropped => U1 > 0;
        public double ScaleX => Scale * (Squash > 0 ? Squash : 1);
    }

    public sealed class CordStrand
    {
        internal List<V2> Pts;
        /// <summary>0..1 texture phase so parallel cords do not show the same wear.</summary>
        public double S0;
        /// <summary>A hanging wall-terminal tail: drawn over the wall face, exempt from the floor rule.</summary>
        public bool OverFace;
        /// <summary>The slack could not be laid clear of obstacles; this is the planned centreline.</summary>
        public bool FellBack;
        /// <summary>Times this strand goes under a door its route does not run through (<see cref="CordShape.DoorStrays"/>). Laying avoids it; the probe reads what is left.</summary>
        public int DoorStrays;
        /// <summary>Points at the start / end of Pts that form a live terminal's whipping tail (phase 1b
        /// B3): the section layer leaves them out of the static mesh while whipping is on, and the map
        /// component draws them bent per frame. 0 = no tail.</summary>
        public int WhipA, WhipB;
        /// <summary>A lifted piece (wall-hanging tail): sways in the wind, weight per point (0 at the pin).</summary>
        public bool Lifted;
        public double[] SwayW;
        /// <summary>Rope-settle diagnostics (phase 1b B1); null when the strand was not settled.</summary>
        internal SettleStats Settle;
        /// <summary>Dive-through: this strand's start (DiveA) / end (DiveB) is where the cord dives under a barrier or comes
        /// back up, not one of its edge's ends. End art (plugs, frays, whip tails) never goes there.</summary>
        public bool DiveA, DiveB;
    }

    /// <summary>A conduit end that reads live or dead: where sparks go (design §8.5).</summary>
    public sealed class CordEnd
    {
        internal V2 Tip;
        internal V2 Dir;
        internal Cell NetCell;
        public bool Wall;
    }

    public sealed class LaidPiece
    {
        public string Key;
        internal Cell Owner;
        public List<CordStrand> Strands = new List<CordStrand>();
        public List<CordDecal> Decals = new List<CordDecal>();
        public List<CordEnd> Ends = new List<CordEnd>();
        /// <summary>Net cells whose live flag this piece's LOOK depends on beyond its Ends (tangle and
        /// device-strip LEDs): the component's live poll re-prints the piece when one flips.</summary>
        internal List<Cell> LiveKeys = new List<Cell>();
        public bool Unroutable;
        /// <summary>Barrier crossings the cord dives through (dive-through, owner 2026-10-06); 0 = an all-surface cord.</summary>
        public int Dives;
        public double PathLen, LaidRatio;
        /// <summary>Corridor rect and the walkability hash it was planned on (§8.2.7).</summary>
        public int CX0, CZ0, CX1, CZ1;
        public ulong CorridorHash;
        /// <summary>What LayEdge reads from the graph beyond the cache key: the parallel flag (a pair joined by
        /// more than one edge routes through its chain's middle cell) and the spur knots. A cached piece is reused
        /// only when this matches too (lane F 2026-10-02: a ring split by a connector kept its parallel route).</summary>
        public string LaySig;
        public string EndA, EndB;   // oracle-style "type:x,z"
        /// <summary>GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG: the cell box everything this piece draws or was planned on covers
        /// (corridor, owner, strand points, decals, end tips), filled once by CordReach.BoxOf; a reused piece keeps it.</summary>
        internal int[] ReachBox;
        /// <summary>GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS: memos the component's rebuild tail fills once per piece object on the
        /// main thread after publish (RebuildTail): net tokens, and the key+geometry part of its section signature.</summary>
        internal string NetTokA, NetTokB;
        internal ulong SigMemo;
        internal bool SigMemoSet;

        public ulong GeometryHash()
        {
            ulong h = 1469598103934665603UL;
            foreach (CordStrand s in Strands)
                foreach (V2 p in s.Pts)
                {
                    h = (h ^ unchecked((ulong)(long)Math.Round(p.X * 1000))) * 1099511628211UL;
                    h = (h ^ unchecked((ulong)(long)Math.Round(p.Z * 1000))) * 1099511628211UL;
                }
            return h;
        }
    }

    public sealed class BuildOptions
    {
        internal LayParams Lay = new LayParams { FillFlats = true, SoftPins = true, RoundExcursions = true, RoundLoops = true, ShortBow = true, FairBends = true };
        public bool Tangles = true;
        public bool NeedlessLoops = true;
        public ulong Seed = 1;
        /// <summary>Messiness: dense fields of at least this many cells become a tangle (setting, 6-20).</summary>
        public int TangleMin = CordGraph.TangleMin;
        /// <summary>Strips (ExtensionCord) or junction boxes (every other style) in piles and at device stubs.</summary>
        public PileArt Pile = PileArt.Junctions;
        /// <summary>Per-build style stage 2: the pile art of the RUN at a cell (strips in a Modern run, junction boxes in every
        /// other), null where the cell stores no style (then <see cref="Pile"/>, the default look's).</summary>
        internal Func<Cell, PileArt?> PileAt;

        internal PileArt PileFor(Cell c) => PileAt?.Invoke(c) ?? Pile;
        /// <summary>Dive-through (owner 2026-10-06: cords dive through walls and water; setting, default on): a lead with no
        /// walkable route dives at the barrier it meets and resurfaces beyond it, instead of being drawn unroutable.</summary>
        public bool DiveThrough = true;
        /// <summary>CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT (owner 2026-10-23: "It should favor diagonal approaches sliding underneath,
        /// to avoid confusion."; setting, default on): a cord into a building comes in at a diagonal, off every cell-edge
        /// midpoint (where pipe and hose ports sit), and slides under the art to the centroid.</summary>
        public bool SlideUnder = true;
        /// <summary>Machines whose art draws a real power connector where the cord meets it (the tap clamp's jaws): they keep the
        /// straight, square plug under SlideUnder.</summary>
        public HashSet<string> StraightPlugIds = new HashSet<string>();
        /// <summary>GSS_PLAN_FIX_SECOND_PER_FULL_BUILD (live round 4: a planned build of 248 edges took ~1 s in one frame, 97%
        /// of it the per-strand settle): the ms one Build may run before it stops laying edges (counted from the Build's start,
        /// so the graph reduce and keys spend it too); 0 = unlimited (every selftest). Over budget
        /// (after at least one lay, so a run of Builds always converges) an edge shows its previous piece, or nothing, and
        /// counts in <see cref="CordBuilder.LastPending"/>; the next Build lays it. Each edge is laid alone and
        /// deterministically, so a run of budgeted Builds ends bit-identical to one unbudgeted Build.</summary>
        public double LayBudgetMs;
        /// <summary>GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET (live r3 2026-10-26: one LayEdge costs 6.3 ms mean, 28 ms max on Mono,
        /// so a budget checked between edges still held slices of 42 ms): the caller lays NO edge. A missed edge is laid on a
        /// worker thread (one batch per builder, the hose's HoseLayQueue pattern) against this Build's world and graph, which
        /// nothing writes after the Build; it shows its previous piece, or nothing, and counts in LastPending until a later
        /// Build takes the landed piece (checked against that Build's world exactly as a cache hit is). LayEdge is a pure
        /// function of its inputs, so a run of async Builds ends bit-identical to one unbudgeted Build. LayBudgetMs is not
        /// used for an async Build (except for an edge whose worker lay threw: that one lays on the caller and throws there).</summary>
        public bool AsyncLay;
    }

    /// <summary>
    /// Builds every cord piece of a map. Holds the per-edge cache: an edge whose endpoints, chain,
    /// live flags and corridor walkability are unchanged re-emits its cached polylines bit-identically
    /// and costs no planning (§8.2.7).
    /// </summary>
    public sealed class CordBuilder
    {
        private Dictionary<string, LaidPiece> cache = new Dictionary<string, LaidPiece>(), spareCache = new Dictionary<string, LaidPiece>();
        public int LastPlanned, LastReused;
        /// <summary>Edges the last Build left to a later Build because <see cref="BuildOptions.LayBudgetMs"/> ran out.</summary>
        public int LastPending;

        /// <summary>GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET (see <see cref="BuildOptions.AsyncLay"/>): edges the last Build took
        /// from the worker (counted in LastPlanned too); edges it laid on the caller (an async Build lays none); worker
        /// batches started; the last worker lay's exception text; isLive asks a worker lay made outside the two endpoints
        /// (answered false: must stay 0, SelfTest).</summary>
        public int LastLanded, LastLaidOnCaller, LayBatches;
        public string LastLayFault;
        /// <summary>Selftest seam only (never set by the game): called on the worker with the edge key before each lay, so a test can make a worker lay throw.</summary>
        internal Action<string> WorkerLayHook;
        /// <summary>Selftest seam only (never set by the game): called on the graph worker before each reduce.</summary>
        internal Action GraphJobHook;
        internal static int LiveMisses;

        private sealed class LayJob { public EdgePlan Ep; public string Fk; public bool LiveA, LiveB; }

        // under layLock: the worker's output and the keys still worth laying; the main thread owns inFlight and layFaulted
        private readonly object layLock = new object();
        private Dictionary<string, LaidPiece> landed = new Dictionary<string, LaidPiece>();
        private readonly Dictionary<string, string> layFaults = new Dictionary<string, string>();
        private HashSet<string> layWanted = new HashSet<string>();
        private bool layRunning;
        private readonly HashSet<string> inFlight = new HashSet<string>(), layFaulted = new HashSet<string>();

        /// <summary>A Build has something new to take, or nothing laying: the caller's next budgeted Build is worth running.
        /// While a graph job runs with nothing landed a Build could only show the last pieces again, so it is not.</summary>
        public bool LayReady
        {
            get
            {
                lock (layLock)
                {
                    if (graphLanded != null || graphFault != null) return true;
                    if (graphRunning) return false;
                    return landed.Count > 0 || !layRunning;
                }
            }
        }
        /// <summary>GSS round 9 (live round 8: 40-50 frame rebuilds a second while the worker landed pieces, each one a
        /// whole-map snapshot copy, a Build and the publish tail; the slowest slices were pauses no phase owned, so the
        /// lever is fewer slices, not a faster one). <see cref="LayReady"/> held until the landed pieces are worth a
        /// rebuild: a graph landed or faulted, the lay batch ended, at least <see cref="CoalescePieces"/> landed, or the
        /// oldest landed piece is <see cref="CoalesceMs"/> old (so a slow batch still shows within that). nowTs: Stopwatch
        /// ticks (a parameter so the SelfTest drives the clock).</summary>
        public bool LayReadyCoalesced(long nowTs)
        {
            lock (layLock)
            {
                if (graphLanded != null || graphFault != null) return true;
                if (graphRunning) return false;
                if (!layRunning) return true;
                if (landed.Count == 0) return false;
                if (landed.Count >= CoalescePieces) return true;
                return (nowTs - firstLandTs) * 1000.0 / System.Diagnostics.Stopwatch.Frequency >= CoalesceMs;
            }
        }
        public int CoalescePieces = 64;
        public double CoalesceMs = 100.0;
        /// <summary>Stopwatch ticks when the first piece of the current landed set landed (under layLock).</summary>
        private long firstLandTs;
        /// <summary>The lay worker is running a batch / the graph worker a job (the round 9 slice record's worker flags).</summary>
        public bool LayWorkerBusy { get { lock (layLock) return layRunning; } }
        public bool GraphWorkerBusy { get { lock (layLock) return graphRunning; } }
        /// <summary>A worker batch (lays or a graph job) is still running (SelfTest waits on it).</summary>
        public bool LayRunning { get { lock (layLock) return layRunning || graphRunning; } }

        /// <summary>GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS: the graph worker. One job at a time reduces a changed graph off the
        /// caller (CordGraph.Reduce, PlanEdges, the node order and junction decals: every whole-map step of a graph change) for
        /// the inputs of the Build that started it; a later Build adopts it only when its own inputs are equal, compared
        /// exactly. LastGraphPending: the last Build waited on it (showed the previous pieces). GraphJobs started, graphs
        /// adopted; the last job's exception text (after one, this builder reduces on the caller, where it throws).</summary>
        public bool LastGraphPending;
        public int GraphJobs, GraphLanded;
        public string LastGraphFault;

        private sealed class GraphJob
        {
            public InputBuf In;
            public CordGraph G;
            public List<EdgePlan> Plan;
            public List<KeyValuePair<VId, CordNode>> NodeOrder;
            public Dictionary<VId, LaidPiece> Junctions;
        }

        // under layLock: the worlds a running worker reads (the lay batch's Build world and its graph's world; the graph job's)
        private CordWorld layWorld, layGraphWorld, graphWorld;

        /// <summary>GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS round 10 (SnapshotPool): adds every world this builder may still read
        /// after its Build returned -- the current graph's, the plan's and junctions' graphs', a landed graph's, and a running
        /// lay batch's or graph job's -- so a pooled snapshot is never refilled under a reader. Null entries are skipped.</summary>
        internal void HeldWorlds(List<CordWorld> into)
        {
            void Add(CordWorld w) { if (w != null) into.Add(w); }
            Add(Graph?.World); Add(planFor?.World); Add(junctionsFor?.World);
            lock (layLock)
            {
                Add(graphLanded?.G?.World);
                if (graphRunning) Add(graphWorld);
                if (layRunning) { Add(layWorld); Add(layGraphWorld); }
            }
        }

        // under layLock: the graph worker's output, fault and running flag; graphFaulted is the caller's
        private GraphJob graphLanded;
        private string graphFault;
        private bool graphRunning, graphFaulted;
        private List<LaidPiece> lastOut = new List<LaidPiece>();

        /// <summary>GSS_PLAN_FIX_SECOND_PER_FULL_BUILD: a graph's exact inputs, the numbers and the machine ids and links, in
        /// buffers kept across Builds. A Build compares them, it does not keep them: on the live scene they cost 76 KB of frame
        /// allocation per hand-off (selftest AllocBudget), and an allocation that size on the frame pays Unity's incremental collector by its size
        /// (a 25.8 ms slice, 21.6 of it in the two allocating steps of a hand-off that usually costs under 0.3 ms).</summary>
        private sealed class InputBuf
        {
            public const int Floor = 16384;
            public readonly List<long> Nums = new List<long>(Floor);
            private char[] ids = new char[Floor];
            private int n;
            public int IdLength => n;
            public void Clear() { Nums.Clear(); n = 0; }
            public void Add(char c)
            {
                if (n == ids.Length) Array.Resize(ref ids, n * 2);
                ids[n++] = c;
            }
            public void Add(string t)
            {
                if (n + t.Length > ids.Length) Array.Resize(ref ids, Math.Max(n + t.Length, ids.Length * 2));
                t.CopyTo(0, ids, n, t.Length);
                n += t.Length;
            }
            public bool SameIds(InputBuf o)
            {
                if (n != o.n) return false;
                for (int i = 0; i < n; i++) if (ids[i] != o.ids[i]) return false;
                return true;
            }
            public void CopyFrom(InputBuf o)
            {
                Nums.Clear();
                Nums.AddRange(o.Nums);
                if (ids.Length < o.n) ids = new char[o.ids.Length];
                Array.Copy(o.ids, ids, o.n);
                n = o.n;
            }
        }
        /// <summary>Input buffers of finished graph jobs (caller only; a job holds at most one running and one landed).</summary>
        private readonly Stack<InputBuf> freeBufs = new Stack<InputBuf>();

        private void StartGraph(CordWorld w, BuildOptions opt, int tangleMin, int spurMax, InputBuf inputs)
        {
            lock (layLock)
            {
                if (graphRunning) return;
                graphRunning = true;
                graphWorld = w;
            }
            GraphJobs++;
            InputBuf held = freeBufs.Count > 0 ? freeBufs.Pop() : new InputBuf();
            held.CopyFrom(inputs);
            var job = new GraphJob { In = held };
            ulong seed = opt.Seed;
            bool slide = opt.SlideUnder;
            HashSet<string> plugs = opt.StraightPlugIds;
            System.Threading.ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    GraphJobHook?.Invoke();
                    CordGraph g = CordGraph.Reduce(w, seed, tangleMin, spurMax, slide, plugs);
                    job.G = g;
                    job.Plan = PlanEdges(g);
                    job.NodeOrder = g.Nodes.OrderBy(k => k.Key).ToList();
                    job.Junctions = new Dictionary<VId, LaidPiece>();
                    foreach (var kv in job.NodeOrder)
                        if (kv.Value.Type == NodeType.Junction) job.Junctions[kv.Key] = JunctionPiece(g, kv.Key, kv.Value, seed);
                    lock (layLock) { graphLanded = job; graphRunning = false; graphWorld = null; }
                }
                catch (Exception ex)
                {
                    lock (layLock) { graphFault = ex.ToString(); graphRunning = false; graphWorld = null; }
                }
            });
        }

        /// <summary>A junction's decal piece: reads only the graph and the seed (round 2), so the caller and the graph worker
        /// make the same one.</summary>
        private static LaidPiece JunctionPiece(CordGraph g, VId v, CordNode nd, ulong seed)
        {
            var p = new LaidPiece { Key = "node:" + v, Owner = nd.Cell };
            JunctionPose jp = PoseJunction(g, v, seed);
            p.Decals.Add(new CordDecal(jp.Kind, jp.Centre, jp.Angle, JunctionScale));
            return p;
        }

        /// <summary>A Modern junction's long power strip, its LEDs reading the net. The key carries the LED state, so a flip repaints.</summary>
        private static LaidPiece StripPiece(CordGraph g, VId v, CordNode nd, ulong seed, bool lit)
        {
            var p = new LaidPiece { Key = "node:" + v + (lit ? ":lit" : ":dark"), Owner = nd.Cell };
            StripPose sp = PoseStrip(g, v, seed);
            p.Decals.Add(new CordDecal(lit ? DecalKind.PowerStrip : DecalKind.PowerStripDark, sp.Centre, sp.Angle, JunctionStripScale));
            p.LiveKeys.Add(nd.Cell);
            return p;
        }

        /// <summary>Publishes the keys this Build still misses (the worker skips any other) and, with no batch running, starts
        /// one on the thread pool for the queued edges. The world and graph are this Build's: the adapter snapshots a fresh
        /// world per rebuild and nothing writes it or a reduced graph afterwards, so the worker only reads them.</summary>
        private void StartLays(CordWorld w, CordGraph g, BuildOptions opt, HashSet<string> wantNow, List<LayJob> queue)
        {
            lock (layLock)
            {
                layWanted = wantNow;
                if (layRunning || queue.Count == 0) return;
                layRunning = true;
                layWorld = w; layGraphWorld = g.World;
            }
            foreach (LayJob j in queue) inFlight.Add(j.Fk);
            LayBatches++;
            System.Threading.ThreadPool.QueueUserWorkItem(_ => RunLays(w, g, opt, queue));
        }

        private void RunLays(CordWorld w, CordGraph g, BuildOptions opt, List<LayJob> jobs)
        {
            try
            {
                foreach (LayJob j in jobs)
                {
                    lock (layLock) if (!layWanted.Contains(j.Fk)) continue;
                    try
                    {
                        WorkerLayHook?.Invoke(j.Fk);
                        Cell ca = j.Ep.CellA, cb = j.Ep.CellB;
                        bool la = j.LiveA, lb = j.LiveB;
                        Func<Cell, bool> live = c =>
                        {
                            if (c == ca) return la;
                            if (c == cb) return lb;
                            System.Threading.Interlocked.Increment(ref LiveMisses);
                            return false;
                        };
                        LaidPiece lp = LayEdge(w, g, j.Ep.Edge, j.Ep.EKey, j.Ep.Parallel, opt, live);
                        lp.Key = j.Fk;
                        lp.LaySig = j.Ep.Sig;
                        lp.CorridorHash = CorridorHash(w, lp);
                        lock (layLock)
                        {
                            if (landed.Count == 0) firstLandTs = System.Diagnostics.Stopwatch.GetTimestamp();
                            landed[j.Fk] = lp;
                        }
                    }
                    catch (Exception ex)
                    {
                        lock (layLock) layFaults[j.Fk] = ex.ToString();
                    }
                }
            }
            finally
            {
                lock (layLock) { layRunning = false; layWorld = layGraphWorld = null; }
            }
        }
        /// <summary>Heap pieces by <see cref="TangleKey"/>: the last Build's, and this one's.</summary>
        private Dictionary<string, LaidPiece> tangleCache = new Dictionary<string, LaidPiece>(), tangleNext = new Dictionary<string, LaidPiece>();

        /// <summary>All a heap's piece reads: its cells, the seed, its look and live flag, the lay options, and every cell two round it (walkable, door, cost, busy,
        /// furniture, conduit, machine), which its connectors and the ground its cables walk are made of.</summary>
        private static string TangleKey(CordWorld w, CordNode nd, BuildOptions opt, Func<Cell, bool> isLive)
        {
            List<Cell> comp = nd.Cells;
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            ulong h = 1469598103934665603UL;
            foreach (Cell c in comp.OrderBy(c => c))
            {
                h = (h ^ (ulong)(uint)(c.X * 73856093 ^ c.Z * 19349663)) * 1099511628211UL;
                x0 = Math.Min(x0, c.X - 2); z0 = Math.Min(z0, c.Z - 2); x1 = Math.Max(x1, c.X + 2); z1 = Math.Max(z1, c.Z + 2);
            }
            var machine = new HashSet<Cell>();
            foreach (MachineInfo m in w.Machines)
                if (m.X0 <= x1 && m.X0 + m.W > x0 && m.Z0 <= z1 && m.Z0 + m.H > z0)
                    for (int x = m.X0; x < m.X0 + m.W; x++)
                        for (int z = m.Z0; z < m.Z0 + m.H; z++) machine.Add(new Cell(x, z));
            for (int x = x0; x <= x1; x++)
                for (int z = z0; z <= z1; z++)
                {
                    var c = new Cell(x, z);
                    h = (h ^ CellSig(w, c) ^ (w.IsConduit(c) ? 1UL << 60 : 0UL) ^ (machine.Contains(c) ? 1UL << 59 : 0UL)) * 1099511628211UL;
                }
            return nd.Cell + "|" + h + "|" + opt.Seed + "|" + opt.PileFor(nd.Cell) + "|" + (isLive(nd.Cell) ? 'L' : 'D') + "|" + (opt.Lay.FairBends ? 'F' : '-') + "|" + comp.Count;
        }

        /// <summary>The piece each edge (by endpoint key) last showed: what a deferred edge keeps showing.</summary>
        private Dictionary<string, LaidPiece> shown = new Dictionary<string, LaidPiece>(), shownNext = new Dictionary<string, LaidPiece>();
        public CordGraph Graph { get; private set; }

        /// <summary>GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG (live 2026-10-26: CordBuilder.Build 15.3 ms at E=206 with every edge
        /// reused; offline the graph reduce was about 70% of that). The graph is a pure function of the conduit cells, their
        /// buried kind, the machines and the reduce options (CordGraph reads nothing else of the world), so when those inputs
        /// are equal to the last Build's -- compared exactly, not hashed -- the last graph is reused instead of re-reduced.</summary>
        public bool LastGraphReused;
        public int GraphReuses;
        /// <summary>GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 2: the last Build's phase split in ms (graph inputs, reduce or
        /// reuse, edge keys + cache checks + lays, node pieces, reach), so the live probe names where a rebuild's time goes.</summary>
        public double PhInputsMs, PhReduceMs, PhEdgesMs, PhNodesMs, PhReachMs, PhKeyMs, PhCorridorMs;
        private static double Ms(long a, long b) => (b - a) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
        private InputBuf graphIn = new InputBuf(), graphInNext = new InputBuf();
        /// <summary>graphIn holds a Build's inputs a later Build may reuse (a LinkAllowed world's never match).</summary>
        private bool graphInComparable;

        /// <summary>Where a terrain or roof change could alter the next Build (see CordReach); null before the first Build.</summary>
        internal CordReach Reach { get; private set; }

        internal List<LaidPiece> Build(CordWorld w, BuildOptions opt, Func<Cell, bool> isLive)
        {
            int tangleMin = opt.Tangles ? opt.TangleMin : int.MaxValue, spurMax = opt.NeedlessLoops ? CordGraph.SpurMax : 0;
            long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
            GraphInputs(w, opt, tangleMin, spurMax, graphInNext);
            long t1 = System.Diagnostics.Stopwatch.GetTimestamp();
            CordGraph g;
            LastGraphPending = false;
            // a LinkAllowed callback (selftest bands only; the game adapter never sets one) is opaque: always re-reduce
            bool reuse = Graph != null && w.LinkAllowed == null && graphInComparable && graphIn.SameIds(graphInNext) && SameInputs(graphIn.Nums, graphInNext.Nums);
            GraphJob adopt = null, gotGraph;
            // every Build takes the graph worker's output (a job that no Build adopts is dropped, so LayReady goes quiet)
            lock (layLock)
            {
                gotGraph = graphLanded;
                graphLanded = null;
                if (graphFault != null) { LastGraphFault = graphFault; graphFault = null; graphFaulted = true; }
            }
            if (!reuse && opt.AsyncLay && w.LinkAllowed == null && !graphFaulted)
            {
                // GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS: a changed graph is reduced, planned and its junctions posed on a worker
                // (whole-map work: 142 of a 188 ms frame at 8 lattices offline). The frame takes a landed graph only when its
                // inputs equal this Build's exactly (then it is the graph this Build would reduce); otherwise it starts a job
                // for this Build's inputs and shows the last pieces, touching nothing else of the builder.
                if (gotGraph != null && gotGraph.In.SameIds(graphInNext) && SameInputs(gotGraph.In.Nums, graphInNext.Nums)) adopt = gotGraph;
                else if (!graphFaulted)
                {
                    if (gotGraph != null) freeBufs.Push(gotGraph.In);
                    gotGraph = null;
                    StartGraph(w, opt, tangleMin, spurMax, graphInNext);
                    LastGraphPending = true;
                    LastPlanned = LastReused = LastLanded = LastLaidOnCaller = 0;
                    LastPending = Math.Max(1, LastPending);
                    long tw = System.Diagnostics.Stopwatch.GetTimestamp();
                    PhInputsMs = Ms(t0, t1); PhReduceMs = Ms(t1, tw); PhEdgesMs = PhNodesMs = PhReachMs = PhKeyMs = PhCorridorMs = 0;
                    // the very list the last full Build returned (nothing writes a returned list): no copy on the frame
                    return lastOut;
                }
            }
            if (gotGraph != null) freeBufs.Push(gotGraph.In);
            if (reuse)
            {
                g = Graph;
                LastGraphReused = true;
                GraphReuses++;
            }
            else if (adopt != null)
            {
                LastReduceWhy = ReduceWhy(w) + " (worker)";
                g = adopt.G;
                plan = adopt.Plan; planFor = g;
                junctions = adopt.Junctions; nodeOrder = adopt.NodeOrder; junctionsFor = g; junctionSeed = opt.Seed;
                LastGraphReused = false;
                GraphLanded++;
            }
            else
            {
                LastReduceWhy = ReduceWhy(w);
                g = CordGraph.Reduce(w, opt.Seed, tangleMin, spurMax, opt.SlideUnder, opt.StraightPlugIds);
                LastGraphReused = false;
            }
            (graphIn, graphInNext) = (graphInNext, graphIn);
            graphInComparable = w.LinkAllowed == null;
            Graph = g;
            long t2 = System.Diagnostics.Stopwatch.GetTimestamp();
            // the last cache's dictionary, retired below, is this one (a whole-map dictionary per frame was the Build's largest block)
            Dictionary<string, LaidPiece> next = spareCache;
            next.Clear();
            // sized once: growing it by doubling allocated about twice its final size
            var outp = new List<LaidPiece>(lastOut.Count + 16);
            LastPlanned = LastReused = LastPending = LastLanded = LastLaidOnCaller = 0;
            shownNext.Clear();
            // the worker's landed pieces (taken whatever this Build's mode: a landed piece is exactly what the caller would lay)
            Dictionary<string, LaidPiece> took = null;
            lock (layLock)
            {
                if (landed.Count > 0) { took = landed; landed = new Dictionary<string, LaidPiece>(); }
                if (!layRunning) inFlight.Clear();
                foreach (var kv in layFaults) { layFaulted.Add(kv.Key); LastLayFault = kv.Value; }
                layFaults.Clear();
            }
            var wantNow = new HashSet<string>();
            var queue = new List<LayJob>();
            long layUntil = opt.LayBudgetMs > 0 ? t0 + (long)(opt.LayBudgetMs * System.Diagnostics.Stopwatch.Frequency / 1000.0) : long.MaxValue;
            // GPT deep review 2026-10-22 #11: a diving piece's corridor is the whole map; hash it ONCE per Build, not once per
            // cached diving edge (D x map cells). The world is only read during a Build, so the memo is exact.
            ulong? wholeMapSig = null;
            ulong Corridor(LaidPiece p) =>
                p.CX0 == 0 && p.CZ0 == 0 && p.CX1 == w.Width - 1 && p.CZ1 == w.Height - 1
                    ? (wholeMapSig ??= CorridorHash(w, p)) : CorridorHash(w, p);
            // round 2 (live 13.4 ms all-reused on Mono): everything in an edge's cache key that comes from the graph alone (endpoint
            // key, chain, node look, homes, tangle cells, lay signature) is formatted once per graph, not once per Build: the
            // per-edge double/enum formatting was most of an all-reused Build. The key string is unchanged, char for char.
            if (!ReferenceEquals(planFor, g)) { plan = PlanEdges(g); planFor = g; }
            string fingerprint = opt.Lay.Fingerprint();
            string optTail = (opt.DiveThrough ? "V" : "") + (opt.SlideUnder ? "U" : "");
            long tKey = 0, tCorr = 0;
            foreach (EdgePlan ep in plan)
            {
                long k0 = System.Diagnostics.Stopwatch.GetTimestamp();
                CordEdge e = ep.Edge;
                bool parallel = ep.Parallel;
                string ekey = ep.EKey;
                string fk = ep.Key(isLive, fingerprint, PileName(opt.PileFor(ep.CellA)), PileName(opt.PileFor(ep.CellB)), optTail, keyText);
                string sig = ep.Sig;
                long k1 = System.Diagnostics.Stopwatch.GetTimestamp();
                tKey += k1 - k0;
                bool hit = cache.TryGetValue(fk, out LaidPiece old) && old.LaySig == sig && Corridor(old) == old.CorridorHash;
                tCorr += System.Diagnostics.Stopwatch.GetTimestamp() - k1;
                if (hit)
                {
                    next[fk] = old;
                    outp.Add(old);
                    shownNext[ekey] = old;
                    LastReused++;
                    continue;
                }
                if (took != null && took.TryGetValue(fk, out LaidPiece got) && got.LaySig == sig && Corridor(got) == got.CorridorHash)
                {
                    // laid by the worker under this very key against a world whose corridor still matches: a cache hit
                    next[fk] = got;
                    outp.Add(got);
                    shownNext[ekey] = got;
                    LastPlanned++;
                    LastLanded++;
                    continue;
                }
                if (opt.AsyncLay && !layFaulted.Contains(fk))
                {
                    wantNow.Add(fk);
                    if (!inFlight.Contains(fk))
                        queue.Add(new LayJob { Ep = ep, Fk = fk, LiveA = isLive(ep.CellA), LiveB = isLive(ep.CellB) });
                    if (shown.TryGetValue(ekey, out LaidPiece prev)) { outp.Add(prev); shownNext[ekey] = prev; }
                    LastPending++;
                    continue;
                }
                if (LastLaidOnCaller > 0 && System.Diagnostics.Stopwatch.GetTimestamp() >= layUntil)
                {
                    // over the lay budget: keep showing this edge's previous piece (not cached under the new key) until a later Build
                    if (shown.TryGetValue(ekey, out LaidPiece prev)) { outp.Add(prev); shownNext[ekey] = prev; }
                    LastPending++;
                    continue;
                }
                LaidPiece lp = LayEdge(w, g, e, ekey, parallel, opt, isLive);
                LastLaidOnCaller++;
                lp.Key = fk;
                lp.LaySig = sig;
                lp.CorridorHash = Corridor(lp);
                next[fk] = lp;
                outp.Add(lp);
                shownNext[ekey] = lp;
                LastPlanned++;
            }
            (shown, shownNext) = (shownNext, shown);
            if (opt.AsyncLay) StartLays(w, g, opt, wantNow, queue);
            long t3 = System.Diagnostics.Stopwatch.GetTimestamp();
            if (!ReferenceEquals(junctionsFor, g) || junctionSeed != opt.Seed)
            {
                junctions = new Dictionary<VId, LaidPiece>();
                junctionsFor = g;
                junctionSeed = opt.Seed;
                nodeOrder = g.Nodes.OrderBy(k => k.Key).ToList();
            }
            if (!ReferenceEquals(stripsFor, g) || stripSeed != opt.Seed)
            {
                litStrips.Clear();
                darkStrips.Clear();
                stripsFor = g;
                stripSeed = opt.Seed;
            }
            // node pieces: junction decals (kept with the graph), tangles (cheap, never cached)
            foreach (var kv in nodeOrder)
            {
                CordNode nd = kv.Value;
                if (nd.Type == NodeType.Junction && opt.PileFor(nd.Cell) == PileArt.Strips)
                {
                    // d_modern_junction_strip: a Modern junction draws the long strip. Its look and LEDs can change on a kept
                    // graph, so both forms are kept with the graph and the cell's current look and net pick one
                    Dictionary<VId, LaidPiece> forms = isLive(nd.Cell) ? litStrips : darkStrips;
                    if (!forms.TryGetValue(kv.Key, out LaidPiece p)) forms[kv.Key] = p = StripPiece(g, kv.Key, nd, opt.Seed, ReferenceEquals(forms, litStrips));
                    outp.Add(p);
                }
                else if (nd.Type == NodeType.Junction)
                {
                    // a junction decal reads only the graph and the seed: kept with the graph (round 2)
                    if (!junctions.TryGetValue(kv.Key, out LaidPiece p)) junctions[kv.Key] = p = JunctionPiece(g, kv.Key, nd, opt.Seed);
                    outp.Add(p);
                }
                else if (nd.Type == NodeType.Tangle)
                {
                    // a heap's cables are walked out over its whole ground (pass 17: 16 ms a Build for the Scrapper colony's heap): kept while nothing in or round it changes
                    string tk = TangleKey(w, nd, opt, isLive);
                    if (!tangleCache.TryGetValue(tk, out LaidPiece tp)) tp = TanglePiece(w, nd, opt, isLive);
                    tangleNext[tk] = tp;
                    outp.Add(tp);
                }
            }
            foreach (var sk in g.SpurKnots)
            {
                if (!g.Nodes.TryGetValue(sk.Key, out CordNode j) || j.Type != NodeType.Junction) continue;
                var p = new LaidPiece { Key = "coil:" + sk.Key, Owner = j.Cell };
                CordRng r = CordRng.Of(opt.Seed, "spurcoil", j.Cell.X, j.Cell.Z);
                // a power strip's needless spur is the socket left empty: no spare cord across its sockets
                if (opt.PileFor(j.Cell) == PileArt.Strips) { outp.Add(p); continue; }
                // the spare cord as a loose loop out of a side of the box no cord leaves by, clear of the boxes round it (SpurHank); where none fits, the small curl on the box
                List<V2> coil = SpurHank(w, g, sk.Key, j, sk.Value, r);
                if (coil == null)
                {
                    coil = CordLayer.Loop(j.Pos, new V2(1, 0), new V2(0, 1), 0.22, r.Sign());
                    CordLayer.ProjectOut(w, coil);
                }
                if (coil.All(q => w.IsWalkable(q.Floor))) p.Strands.Add(new CordStrand { Pts = coil, S0 = r.Value() });
                outp.Add(p);
            }
            (tangleCache, tangleNext) = (tangleNext, tangleCache);
            tangleNext.Clear();
            spareCache = cache;
            cache = next;
            lastOut = outp;
            long t4 = System.Diagnostics.Stopwatch.GetTimestamp();
            Reach = CordReach.Of(w, g, outp);
            long t5 = System.Diagnostics.Stopwatch.GetTimestamp();
            PhInputsMs = Ms(t0, t1); PhReduceMs = Ms(t1, t2); PhEdgesMs = Ms(t2, t3); PhNodesMs = Ms(t3, t4); PhReachMs = Ms(t4, t5); PhKeyMs = Ms(0, tKey); PhCorridorMs = Ms(0, tCorr);
            return outp;
        }

        /// <summary>One cord edge's graph-only key parts (round 2): PartA + live flags + PartB + options = the cache key.</summary>
        private sealed class EdgePlan
        {
            public CordEdge Edge;
            public string EKey, PartA, PartB, Sig;
            public bool Parallel;
            public Cell[] LiveCells;
            public bool[] LiveSeam;
            public Cell CellA, CellB;
            // GSS_PLAN_FIX_SECOND_PER_FULL_BUILD: the key this edge last made and what it was made of. An all-reused Build formatted
            // a fresh key per edge, most of the 625 KB it allocated per frame at E=980; an unchanged edge now returns the same
            // string. Caller only (the worker reads the fields above and a job's own Fk).
            private string memoKey, memoFingerprint, memoPileA, memoPileB, memoTail;
            private bool[] memoLive;

            public string Key(Func<Cell, bool> isLive, string fingerprint, string pileA, string pileB, string tail, StringBuilder text)
            {
                bool same = memoKey != null && memoFingerprint == fingerprint && memoPileA == pileA && memoPileB == pileB && memoTail == tail;
                memoLive ??= new bool[LiveCells.Length];
                for (int i = 0; i < LiveCells.Length; i++)
                {
                    bool l = isLive(LiveCells[i]);
                    if (memoLive[i] != l) { memoLive[i] = l; same = false; }
                }
                if (same) return memoKey;
                text.Clear().Append(PartA);
                for (int i = 0; i < LiveCells.Length; i++)
                    text.Append(memoLive[i] ? 'L' : 'D').Append(LiveSeam[i] ? "S" : "");
                text.Append(PartB).Append('#').Append(fingerprint).Append('#').Append(pileA).Append(pileB).Append(tail);
                memoFingerprint = fingerprint; memoPileA = pileA; memoPileB = pileB; memoTail = tail;
                return memoKey = text.ToString();
            }
        }

        private List<EdgePlan> plan = new List<EdgePlan>();
        private readonly StringBuilder keyText = new StringBuilder();
        private CordGraph planFor, junctionsFor;
        private ulong junctionSeed;
        private Dictionary<VId, LaidPiece> junctions = new Dictionary<VId, LaidPiece>();
        private readonly Dictionary<VId, LaidPiece> litStrips = new Dictionary<VId, LaidPiece>(), darkStrips = new Dictionary<VId, LaidPiece>();
        private CordGraph stripsFor;
        private ulong stripSeed;
        private List<KeyValuePair<VId, CordNode>> nodeOrder = new List<KeyValuePair<VId, CordNode>>();

        private static string PileName(PileArt p) => p == PileArt.Strips ? "Strips" : p == PileArt.Junctions ? "Junctions" : p.ToString();

        /// <summary>The per-edge key parts, formatted exactly as the pre-round-2 per-Build loop did.</summary>
        private static List<EdgePlan> PlanEdges(CordGraph g)
        {
            var res = new List<EdgePlan>();
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            List<CordEdge> cordEdges = g.CordEdges().ToList();
            var pairTotal = new Dictionary<string, int>();
            foreach (CordEdge x in cordEdges)
            {
                string k = PairKey(x.A, x.B);
                pairTotal.TryGetValue(k, out int tot);
                pairTotal[k] = tot + 1;
            }
            var pairCount = new Dictionary<string, int>();
            foreach (CordEdge e in cordEdges)
            {
                string pk = PairKey(e.A, e.B);
                pairCount.TryGetValue(pk, out int mult);
                pairCount[pk] = mult + 1;
                bool parallel = pairTotal[pk] > 1 || e.A == e.B;
                string ekey = EdgeKey(g, e, mult);
                var full = new StringBuilder(ekey).Append('#');
                foreach (VId v in e.Chain()) full.Append(v.ToString()).Append(';');
                foreach (VId v in new[] { e.A, e.B })
                {
                    // everything LayEdge/EndDecor read off the node beyond its type: whether a buried run ends inside the wall (a
                    // wall terminal), the open side of a dead end, the stub's direction and face. Without these a conduit removed
                    // behind a stub left its cached piece standing in the old look (gss fuzz seed 81: incremental != fresh).
                    CordNode nn = g.Nodes[v];
                    full.Append(nn.Type).Append(nn.WallTerminal ? "W" : "").Append(nn.Gap ? "G" : "")
                        .Append(nn.Cls).Append(nn.Out.X).Append('/').Append(nn.Out.Z)
                        .Append(nn.Into.X.ToString("0.00", inv)).Append('/').Append(nn.Into.Z.ToString("0.00", inv))
                        .Append(nn.Face.X.ToString("0.00", inv)).Append('/').Append(nn.Face.Z.ToString("0.00", inv)).Append(',');
                }
                var liveCells = new List<Cell>();
                var liveSeam = new List<bool>();
                foreach (VId v in new[] { e.A, e.B })
                    if (g.Nodes[v].Type == NodeType.Terminal || g.Nodes[v].WallTerminal || g.Nodes[v].Type == NodeType.StubDevice)
                    {
                        liveCells.Add(g.Nodes[v].Cell);
                        liveSeam.Add(g.Nodes[v].Seam);
                    }
                // GSS pre-release A7: IntoArt runs a wall device's lead on to its HOME (the wall it hangs on), so the home is
                // part of the key: a re-hung device used to keep a lead ending under its old wall
                var partB = new StringBuilder();
                foreach (VId v in new[] { e.A, e.B })
                {
                    MachineInfo hm = g.Nodes[v].IsMachine ? g.Nodes[v].Machine : null;
                    if (hm != null && hm.HasHome) partB.Append('H').Append(hm.HomeX).Append(',').Append(hm.HomeZ);
                }
                foreach (VId v in new[] { e.A, e.B })
                    if (g.Nodes[v].Type == NodeType.Tangle && g.Nodes[v].Cells != null)
                    {
                        partB.Append("T").Append(g.Nodes[v].Cells.Count);   // round 5: the entry port follows the pile's connectors
                        foreach (Cell c in g.Nodes[v].Cells) partB.Append(';').Append(c.X).Append(',').Append(c.Z);
                    }
                // the boxes, cut ends and plates round it: a cord laid again keeps off them (OtherBoxes), so one appearing re-lays it
                full.Append('N');
                foreach (KeyValuePair<VId, CordNode> kv in NearNodes(g, e))
                    full.Append(kv.Key.ToString()).Append(kv.Value.Type).Append(kv.Value.Pos.X.ToString("0.00", inv)).Append('/').Append(kv.Value.Pos.Z.ToString("0.00", inv)).Append(';');
                res.Add(new EdgePlan
                {
                    Edge = e, EKey = ekey, PartA = full.ToString(), PartB = partB.ToString(), Sig = LaySignature(e, parallel),
                    Parallel = parallel, LiveCells = liveCells.ToArray(), LiveSeam = liveSeam.ToArray(),
                    CellA = g.Nodes[e.A].Cell, CellB = g.Nodes[e.B].Cell
                });
            }
            return res;
        }

        /// <summary>Everything CordGraph.Reduce reads, in its reading order: the map size, the reduce options, every conduit cell
        /// with its buried kind, the ground around a buried hookup (IsBuried / BuriedKind are the only per-cell world reads), and every machine field.</summary>
        private static void GraphInputs(CordWorld w, BuildOptions opt, int tangleMin, int spurMax, InputBuf into)
        {
            into.Clear();
            List<long> nums = into.Nums;
            nums.Add(w.Width); nums.Add(w.Height);
            nums.Add(unchecked((long)opt.Seed)); nums.Add(tangleMin); nums.Add(spurMax); nums.Add(opt.SlideUnder ? 1 : 0);
            foreach (Cell c in w.ConduitCells())
                nums.Add(((long)c.X << 32) | ((long)(uint)c.Z << 8) | (long)(byte)w.BuriedKind(c));
            if (opt.StraightPlugIds != null && opt.StraightPlugIds.Count > 0)
            {
                var ids = opt.StraightPlugIds.ToList();
                ids.Sort(string.CompareOrdinal);
                foreach (string id in ids) { into.Add(id); into.Add('\u0001'); }
            }
            into.Add('\u0002');
            // round 2: the machines' numbers go into the exact long list (no per-Build double/int formatting); the ids and links
            // go to the id buffer. -1 separates the machines' variable-length hookup lists.
            foreach (MachineInfo m in w.Machines)
            {
                into.Add(m.Id); into.Add('\u0001');
                foreach (string l in m.MachineLinks) { into.Add(l); into.Add('\u0001'); }
                into.Add('\u0002');
                nums.Add(-1L); nums.Add((long)m.Kind); nums.Add(m.X0); nums.Add(m.Z0); nums.Add(m.W); nums.Add(m.H);
                nums.Add(m.Hookups.Count);
                foreach (Cell h in m.Hookups)
                {
                    nums.Add(((long)h.X << 32) | (uint)h.Z);
                    if (!w.IsBuried(h)) continue;
                    // CordGraph.FaceFor reads the ground around a buried hookup for the face its cord comes out of
                    long around = 0;
                    for (int dz = -3; dz <= 3; dz++)
                        for (int dx = -3; dx <= 3; dx++)
                            around = (around << 1) | (w.IsBuried(new Cell(h.X + dx, h.Z + dz)) ? 1L : 0L);
                    nums.Add(around);
                }
                nums.Add(BitConverter.DoubleToInt64Bits(m.InsetS)); nums.Add(BitConverter.DoubleToInt64Bits(m.InsetN));
                nums.Add(BitConverter.DoubleToInt64Bits(m.InsetE)); nums.Add(BitConverter.DoubleToInt64Bits(m.InsetW));
                if (m.HasHome) { nums.Add(1); nums.Add(m.HomeX); nums.Add(m.HomeZ); } else nums.Add(0);
            }
        }

        /// <summary>Why the last re-reduce could not reuse the graph (round 2: the live probe names what a far dig changed).</summary>
        public string LastReduceWhy = "";

        private string ReduceWhy(CordWorld w)
        {
            if (Graph == null) return "first";
            if (w.LinkAllowed != null) return "linkAllowed";
            if (!graphInComparable || !graphIn.SameIds(graphInNext)) return "machine ids/links";
            List<long> was = graphIn.Nums, now = graphInNext.Nums;
            int n = Math.Min(was.Count, now.Count), i = 0;
            while (i < n && was[i] == now[i]) i++;
            if (i < 6) return "size/options";
            int sep = now.IndexOf(-1L);
            string part = sep < 0 || i < sep ? "conduit cells" : "machine numbers";
            return part + " @" + i + " (" + was.Count + "->" + now.Count + ")";
        }

        private static bool SameInputs(List<long> a, List<long> b)
        {
            if (a.Count != b.Count) return false;
            for (int i = 0; i < a.Count; i++) if (a[i] != b[i]) return false;
            return true;
        }

        /// <summary>Everything LayEdge takes from the graph that the cache key (endpoints, chain, live flags, lay
        /// fingerprint) does not already pin: the parallel flag and the knot points.</summary>
        private static string LaySignature(CordEdge e, bool parallel)
        {
            var sb = new StringBuilder(parallel ? "P" : "S");
            foreach (V2 k in e.Knots)
                sb.Append(';').Append(k.X.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture))
                  .Append(',').Append(k.Z.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
            return sb.ToString();
        }

        private static string PairKey(VId a, VId b) => a.CompareTo(b) <= 0 ? a + "|" + b : b + "|" + a;

        /// <summary>Seed from the two endpoint cells, their node types and positions, plus the index
        /// among parallel edges: an unrelated edit never reshuffles a cord (§8.2.5).</summary>
        public static string EdgeKey(CordGraph g, CordEdge e, int mult)
        {
            string Ka(VId v, V2 p) => v.T + ":" + g.Nodes[v].Cell.X + "," + g.Nodes[v].Cell.Z + ":" +
                                     p.X.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + "," +
                                     p.Z.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
            string a = Ka(e.A, e.PA), b = Ka(e.B, e.PB);
            return (string.CompareOrdinal(a, b) <= 0 ? a + "|" + b : b + "|" + a) + "|" + mult;
        }

        private static ulong CorridorHash(CordWorld w, LaidPiece p)
        {
            ulong h = 1469598103934665603UL;
            for (int z = p.CZ0; z <= p.CZ1; z++)
                for (int x = p.CX0; x <= p.CX1; x++)
                {
                    var c = new Cell(x, z);
                    h = (h ^ CellSig(w, c)) * 1099511628211UL;
                }
            return h;
        }

        /// <summary>One cell's part of a corridor hash: walkable, door, and (GPT source read 2026-10-06 B7/A13) the route cost
        /// (trees 1.5, water 3), so a tree cut or planted re-plans the cords and hoses through it instead of leaving the old
        /// route standing until a reload. CORD_LOOP_UNTANGLE_LASSOED_A_PIPE: a busy cell (a pipe or conduit laid there) is folded
        /// in too, so building a pipe beside a cord re-lays the loops that would now lasso it (the hose world has no busy
        /// cells, so its shared CordSig.CellSig formula is untouched).</summary>
        internal static ulong CellSig(CordWorld w, Cell c) => CordSig.CellSig(w, c) ^ (w.IsBusy(c) ? 1UL << 62 : 0UL) ^ (w.IsFurniture(c) ? 1UL << 61 : 0UL);

        /// <summary>An edge with a machine at either end is that device's lead: one cord (round 3).</summary>
        public static bool DeviceLead(CordNode a, CordNode b) => (a.IsMachine && a.Machine != null) || (b.IsMachine && b.Machine != null);

        private static LaidPiece LayEdge(CordWorld w, CordGraph g, CordEdge e, string key, bool parallel, BuildOptions opt,
                                         Func<Cell, bool> isLive)
        {
            LayParams prm = opt.Lay;
            CordNode na = g.Nodes[e.A], nb = g.Nodes[e.B];
            // a cord to a cut end keeps its length for the end's limp curl or writhing tail
            if ((na.Type == NodeType.Terminal && !na.Seam) || (nb.Type == NodeType.Terminal && !nb.Seam)) prm = prm.WithoutShortBow();
            var piece = new LaidPiece
            {
                Owner = na.Cell.CompareTo(nb.Cell) <= 0 ? na.Cell : nb.Cell,
                EndA = na.OracleName + ":" + na.Cell.X + "," + na.Cell.Z,
                EndB = nb.OracleName + ":" + nb.Cell.X + "," + nb.Cell.Z
            };
            CordRng rr = CordRng.Of(opt.Seed, "cord", key);
            var mids = new List<KeyValuePair<V2, WaypointKind>>();
            foreach (V2 k in e.Knots) mids.Add(new KeyValuePair<V2, WaypointKind>(k, WaypointKind.Knot));
            if (parallel && e.Via.Count > 0)
            {
                VId mid = e.Via[e.Via.Count / 2];
                if (mid.T == 'c') mids.Add(new KeyValuePair<V2, WaypointKind>(mid.A.Centre, WaypointKind.Via));
            }
            MachineInfo ma = na.IsMachine ? na.Machine : null, mb = nb.IsMachine ? nb.Machine : null;
            Func<Cell, bool> exempt = c => (ma != null && ma.Contains(c)) || (mb != null && mb.Contains(c));
            CordPlan pl = CordPlanner.Plan(w, e.PA, e.PB, mids, opt.DiveThrough, exempt, diveShort: true);
            piece.Unroutable = !pl.Ok;
            if (pl.Ok && pl.Dives.Count > 0) return LayDiving(w, g, e, key, opt, isLive, piece, pl, na, nb);
            List<V2> C = CordPlanner.RoundCorners(pl.Points);
            CordLayer.ProjectOut(w, C);
            double L = Geo.Length(C);
            int n = rr.Int(prm.CordsMin, Math.Max(prm.CordsMin, prm.CordsMax));
            // round 3 (owner 2026-10-04, station 9: "very odd triple cords going a short distance from the wall to a lamp.
            // Should just be one cord"): a device's own lead is ONE cord into its one plug; bundles stay between junctions,
            // stubs and conduit ends. The draw above still runs, so every later seeded value is unchanged.
            if (DeviceLead(na, nb)) n = 1;
            double slack = rr.Range(prm.SlackLo, prm.SlackHi) * prm.SlackScale;
            double maxExtra = prm.SlackScale <= 0 ? 0 : Math.Min(Math.Max(slack * L, prm.MinExtra * Math.Min(1, prm.SlackScale)), prm.MaxExtra);
            int limpSideA = CordRng.Of(opt.Seed, "limp", na.Cell.X, na.Cell.Z).Sign();
            int limpSideB = CordRng.Of(opt.Seed, "limp", nb.Cell.X, nb.Cell.Z).Sign();
            double laid = 0;
            List<V2> nub = StripNub(g, e, opt) ?? (prm.FairBends ? BoxNub(w, g, e, opt) : null);
            if (nub != null) n = 1;
            for (int i = 0; i < n; i++)
            {
                if (nub != null)
                {
                    piece.Strands.Add(new CordStrand { Pts = nub, S0 = rr.Value() });
                    laid += Geo.Length(nub);
                    continue;
                }
                double lat = n == 1 ? 0 : (i - (n - 1) / 2.0) * 0.1;
                double[] cl = Geo.CumLen(C);
                var P = new List<V2>(C.Count);
                for (int k = 0; k < C.Count; k++)
                {
                    Geo.TanNorm(C, k, out V2 t, out V2 nn);
                    double ramp = Math.Min(1, Math.Min(cl[k], L - cl[k]) / 0.3) * 0.6 + 0.4;
                    P.Add(C[k] + nn * (lat * ramp));
                }
                SettleStats settle = null;
                if (pl.Ok && L > 1.2 && prm.SlackScale > 0)
                    P = SprawlOnce(w, P, C, prm, slack, maxExtra, opt.Seed, key, i, n, null, out settle);
                else
                {
                    int sgn = rr.Sign();
                    for (int k = 0; k < P.Count; k++)
                    {
                        Geo.TanNorm(C, k, out V2 t, out V2 nn);
                        P[k] = P[k] + nn * (0.12 * Math.Sin(Math.PI * cl[k] / Math.Max(L, 1e-6)) * sgn);
                    }
                    CordLayer.ProjectOut(w, P);
                }
                for (int k = 0; k < e.Knots.Count; k++)
                    P = CordLayer.SpliceLoop(w, P, e.Knots[k], CordRng.Of(opt.Seed, "knot", key, i, k), (prm.FairBends ? 0.5 : 0.28) + 0.06 * i);
                // every end arrives the way its art expects (junction arm, plug, stub, conduit end)
                P = AttachEnd(w, g, e, true, P, i, n, opt);
                P = AttachEnd(w, g, e, false, P, i, n, opt);
                // terminal ends: dead = limp curl; live = straight (sparks come from the registry)
                if (na.Type == NodeType.Terminal && !na.Seam && !isLive(na.Cell)) CordLayer.LimpTail(w, P, false, limpSideA, i);
                if (nb.Type == NodeType.Terminal && !nb.Seam && !isLive(nb.Cell)) CordLayer.LimpTail(w, P, true, limpSideB, i);
                // the floor rule (risk register row 2): if anything still sits in an unwalkable cell,
                // fall back to the planned centreline rather than draw a cord through a wall
                bool fell = false;
                if (P.Skip(1).Take(Math.Max(0, P.Count - 2)).Any(q => !w.IsWalkable(q.Floor)))
                {
                    P = new List<V2>(C);
                    fell = true;
                }
                // the loops and the settle leave folds a cord cannot make: its ribbon spikes there (live, a real colony: 2.9 a strand)
                if (!fell) P = CordShape.Unfold(w, P, LimpSkip(na, nb, isLive));
                // a cord to a cut end keeps its old lay, as it keeps its length (ShortBow): its live run, limp curl and writhing tail are break_live_and_dead_ends_differ's art
                bool cutEnd = (na.Type == NodeType.Terminal && !na.Seam) || (nb.Type == NodeType.Terminal && !nb.Seam);
                if (!fell && prm.FairBends && !cutEnd) P = CordShape.Fair(w, P, FairPin(na, isLive), FairPin(nb, isLive), CordShapeAudit.OwnMachines(w, piece.EndA, piece.EndB));
                // a machine whose art stops short of its footprint edge (solar panel legs): run the cord on under the
                // art so it visibly goes INTO the graphic (owner review 2026-10-04 B10). Appended after the floor rule:
                // these points lie inside the machine's own footprint by design.
                if (na.IsMachine && na.Machine != null) P = IntoArt(P, true, na.Machine, g.Slides(na.Machine));
                if (nb.IsMachine && nb.Machine != null) P = IntoArt(P, false, nb.Machine, g.Slides(nb.Machine));
                // round 4: a cord into a wall/rock face runs on under the wall to just past the face line, so it meets the
                // plate (drawn inside the wall from the face, WallMount) with no strip of bare floor between; the wall hides
                // the overrun. Appended after the floor rule like IntoArt: these points lie in the wall cell by design.
                P = PastFace(P, true, na);
                P = PastFace(P, false, nb);
                // a short cord that still bends sharp where nothing makes it (never_taut_straight_cord) is laid again whole, fitting to fitting; a cord that passes keeps its lay
                if (!fell && prm.FairBends && !cutEnd && n == 1 && L <= HopMaxPath && (CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, P) > 0 || CordShapeAudit.FittingsForce(P)))
                    P = HopWhole(w, g, e, C, opt, piece, key, isLive) ?? P;
                // any cord the bar still counts against: each sharp bend re-laid round, its window of cord either side laid again as a Dubins path (a hairpin becomes a round loop)
                if (!fell && prm.FairBends) P = SmoothBends(w, g, e, piece, P, na, nb, isLive);
                piece.Strands.Add(new CordStrand { Pts = P, S0 = rr.Value(), FellBack = fell, Settle = settle, DoorStrays = CordShape.DoorStrays(w, P, C) });
                laid += Geo.Length(P);
            }
            piece.PathLen = L;
            piece.LaidRatio = n > 0 ? laid / n / Math.Max(L, 1e-6) : 0;
            EndDecor(w, g, e, e.A, na, piece, true, opt, isLive);
            EndDecor(w, g, e, e.B, nb, piece, false, opt, isLive);
            // corridor: path bounding box expanded by 3 cells (§8.2.7)
            double x0 = double.MaxValue, z0 = double.MaxValue, x1 = double.MinValue, z1 = double.MinValue;
            foreach (CordStrand s in piece.Strands)
                foreach (V2 p in s.Pts) { x0 = Math.Min(x0, p.X); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); z1 = Math.Max(z1, p.Z); }
            if (x0 > x1) { x0 = x1 = e.PA.X; z0 = z1 = e.PA.Z; }
            piece.CX0 = Math.Max(0, (int)Math.Floor(x0) - 3);
            piece.CZ0 = Math.Max(0, (int)Math.Floor(z0) - 3);
            piece.CX1 = Math.Min(w.Width - 1, (int)Math.Floor(x1) + 3);
            piece.CZ1 = Math.Min(w.Height - 1, (int)Math.Floor(z1) + 3);
            return piece;
        }

        /// <summary>
        /// A spur's spare cord as one loose loop out of its junction box: it leaves the box's middle (under the art) and comes back to it, the loop lying off a side of the box no
        /// cord leaves by (the spur's own side first, where the needless conduit ran), a little oval or a narrow lobe (<see cref="SpurHankR"/>, past the bar's 0.45 loop radius, so not a tight
        /// pigtail), on open floor and <see cref="SpurKeepOff"/> off every other box, strip, plate and cut end. Pass 18's broad ring left by any side: it hung across a neighbouring
        /// strip or box and shared the box's fitting with a real lead (blind judge p18b, every look). Null when no side has room: the caller lays the small curl on the box.
        /// </summary>
        private static List<V2> SpurHank(CordWorld w, CordGraph g, VId v, CordNode j, List<Cell> spur, CordRng r)
        {
            if (j.IsBlob || spur == null || spur.Count == 0) return null;
            Cell c = j.Cell;
            var used = new List<V2>();
            foreach (CordEdge e in g.Edges)
            {
                if (e.A.Equals(v)) used.Add(ArmDir(g, e, true));
                if (e.B.Equals(v)) used.Add(ArmDir(g, e, false));
            }
            Cell near = spur.OrderBy(q => Math.Abs(q.X - c.X) + Math.Abs(q.Z - c.Z)).First();
            V2 own = Snap4(new V2(near.X - c.X, near.Z - c.Z));
            var sides = new List<V2> { own };
            foreach (V2 d in new[] { new V2(1, 0), new V2(0, 1), new V2(-1, 0), new V2(0, -1) }) if (V2.Dist(d, own) > 0.1) sides.Add(d);
            var others = new List<V2>();
            foreach (KeyValuePair<VId, CordNode> kv in g.NodesNear(c.X - 3, c.Z - 3, c.X + 3, c.Z + 3))
            {
                if (kv.Key.Equals(v)) continue;
                if (kv.Value.Type == NodeType.Tangle && kv.Value.Cells != null) foreach (Cell q in kv.Value.Cells) others.Add(q.Centre);
                else others.Add(kv.Value.Pos);
            }
            bool Ok(V2 q)
            {
                Cell f = q.Floor;
                if (!w.IsWalkable(f) || w.IsFurniture(f) || w.IsDoor(f) || w.Clearance(q) < LayParams.RC) return false;
                foreach (MachineInfo m in w.Machines) if (m.Contains(f) || UnderLampArt(m, f)) return false;
                foreach (V2 o in others) if (V2.Dist(q, o) < SpurKeepOff) return false;
                return true;
            }
            int sg = r.Sign();
            double squash = r.Range(0.86, 1.0), drift = r.Range(0.02, 0.05);
            foreach (var (wide, deep) in SpurHankR)
                foreach (V2 n in sides)
                {
                    if (used.Any(u => V2.Dist(u, n) < 0.1)) continue;
                    foreach (int side in new[] { sg, -sg })
                    {
                        V2 t = n.Perp * side;
                        double rt = wide == deep ? wide / squash : wide, rn = wide == deep ? deep * squash : deep;
                        var o = new List<V2>(64);
                        for (int i = 0; i < 64; i++)
                        {
                            double th = 2 * Math.PI * i / 63.0;
                            o.Add(j.Pos + t * (rt * Math.Sin(th) + drift * th) + n * (rn * (1 - Math.Cos(th))));
                        }
                        // the stretch under the box's art is hidden: only the loop out past it must lie clear
                        if (o.Where(q => V2.Dist(q, j.Pos) > 0.42).All(Ok)) return o;
                        if (HopWhy != null)
                        {
                            V2 bad = o.Where(q => V2.Dist(q, j.Pos) > 0.42).First(q => !Ok(q));
                            Cell f = bad.Floor;
                            HopWhy("spur " + c + " n " + n + " side " + side + " r " + wide + "x" + deep + " at " + bad + " walk " + w.IsWalkable(f) + " furn " + w.IsFurniture(f) + " door " + w.IsDoor(f) + " clr " + w.Clearance(bad).ToString("0.00")
                                   + " mach " + w.Machines.Any(m => m.Contains(f)) + " box " + others.Any(o2 => V2.Dist(bad, o2) < SpurKeepOff) + " used " + string.Join(";", used));
                        }
                    }
                }
            return null;
        }

        /// <summary>The loops a spur tries, half-width across the side then half-depth out from it (cells), roundest first: a round loop a little oval, then a lobe narrow enough
        /// to hang between a neighbouring box and a machine. Each averages past the bar's 0.45 loop radius.</summary>
        private static readonly (double, double)[] SpurHankR = { (0.52, 0.52), (0.48, 0.48), (0.42, 0.58), (0.36, 0.62) };
        /// <summary>How far a spur's loop keeps off another box, strip, plate or cut end, cells.</summary>
        private const double SpurKeepOff = 0.6;

        /// <summary>
        /// Each bend the bar counts against a laid strand (<see cref="CordShapeAudit.Unforced"/>), re-laid round: the cord from a little before it to a little after is laid again as
        /// a Dubins path between its own poses there, no tighter than <see cref="HeapTurnR"/>, so a hairpin or a squashed double-back becomes a smooth bend or a whole round loop
        /// (the north star's loop, which the bar does not count). A window keeps clear of walls, furniture, machines and doors the cord did not go through, never reaches into an end's
        /// fitting (a cut end's live run, limp curl and writhing tail least of all), and is kept only when the strand's count drops and it draws no straight rod. Live pass 18: a
        /// generator's long lead hooked a cell short of its plug, a wall plate's cord doubled back flat beside its loops.
        /// </summary>
        private static List<V2> SmoothBends(CordWorld w, CordGraph g, CordEdge e, LaidPiece piece, List<V2> P, CordNode na, CordNode nb, Func<Cell, bool> isLive)
        {
            int bad = CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, P);
            if (bad == 0 || P.Count < 8) return P;
            var doors = new HashSet<Cell>();
            foreach (V2 q in P) if (w.IsDoor(q.Floor)) doors.Add(q.Floor);
            List<V2> boxes = OtherBoxes(g, e);
            MachineInfo ownA = na.IsMachine ? na.Machine : null, ownB = nb.IsMachine ? nb.Machine : null;
            Func<V2, bool> clear = q =>
            {
                Cell c = q.Floor;
                if (!w.IsWalkable(c) || w.IsFurniture(c) || (w.IsDoor(c) && !doors.Contains(c))) return false;
                foreach (MachineInfo m in w.Machines) if (m.Contains(c) || (m != ownA && m != ownB && UnderLampArt(m, c))) return false;
                foreach (V2 bx in boxes) if (V2.Dist(q, bx) < BoxKeepOff) return false;
                return w.Clearance(q) >= LayParams.RC;
            };
            // where each end's fitting is along the strand: a machine's plug point (its run on under the art left alone), a wall plate's face, else the strand's end
            int FitIndex(CordNode nd, bool first)
            {
                MachineInfo m = nd.IsMachine ? nd.Machine : null;
                bool Inside(V2 q) => (m != null && m.Contains(q.Floor)) || !w.IsWalkable(q.Floor);
                int k = first ? 0 : P.Count - 1;
                if (first) while (k < P.Count - 1 && Inside(P[k])) k++;
                else while (k > 0 && Inside(P[k])) k--;
                return k;
            }
            bool cutA = na.Type == NodeType.Terminal && !na.Seam, cutB = nb.Type == NodeType.Terminal && !nb.Seam;
            bool machA = na.IsMachine && na.Machine != null, machB = nb.IsMachine && nb.Machine != null;
            double rodNow = CordShapeAudit.LongestRod(P, out _);
            for (int round = 0; round < SmoothRounds && bad > 0; round++)
            {
                double[] cum = Geo.CumLen(P);
                double L = cum[cum.Length - 1];
                int fa = FitIndex(na, true), fb = FitIndex(nb, false);
                if (fb - fa < 6) break;
                // a cut end's live run, limp curl and writhing tail are never laid again; a fitting's straight bit (a plug's: none, it goes on under the art) is its own
                double lo = cum[fa] + (cutA ? 1.6 : machA ? 0 : FitStraight), hi = cum[fb] - (cutB ? 1.6 : machB ? 0 : FitStraight);
                CordShapeAudit.Bend? worst = null;
                foreach (CordShapeAudit.Bend b in CordShapeAudit.Bends(P))
                    if (CordShapeAudit.Why(w, piece.EndA, piece.EndB, P, b) == "unforced") { worst = b; break; }
                if (worst == null) break;
                double S = worst.Value.S;
                // a re-lay stays by the cord it replaces: it may round a bend off, not go somewhere new (a ring out over the mast's wires, a loop
                // round a post or across a neighbour's cord: blind judge p18b, every look)
                var by = new PtGrid(P, SmoothStray);
                List<V2> best = null;
                int bestBad = bad;
                var why = HopWhy == null ? null : new Dictionary<string, int>();
                void No(string t) { if (why != null) why[t] = why.TryGetValue(t, out int k) ? k + 1 : 1; }
                double bestCost = double.MaxValue;
                foreach (var (wa, wb) in SmoothWindows)
                {
                    double s0 = S - wa, s1 = S + wb;
                    // a window that would reach into a fitting starts (ends) at it instead, unless that is a cut end's
                    if (s0 < lo && !cutA) s0 = lo;
                    if (s1 > hi && !cutB) s1 = hi;
                    if (s0 < lo - 1e-9 || s1 > hi + 1e-9 || s1 - s0 < 0.3) { No("guard"); continue; }
                    int j0 = Array.BinarySearch(cum, s0), j1 = Array.BinarySearch(cum, s1);
                    if (j0 < 0) j0 = ~j0;
                    if (j1 < 0) j1 = ~j1;
                    j0 = Math.Max(fa, Math.Min(j0, P.Count - 3));
                    j1 = Math.Max(j0 + 2, Math.Min(j1, fb));
                    if (j0 < 1 || j1 > P.Count - 2) { No("guard"); continue; }
                    V2 a = P[j0], b = P[j1], ta = P[j0 + 1] - P[j0 - 1], tb = P[j1 + 1] - P[j1 - 1];
                    // at a fitting the heading is the fitting's: out of (into) a plug along its run under the art, along a junction arm's or a plate's straight bit
                    if (j0 <= fa + 1 && machA) ta = P[j0] - P[Math.Max(0, j0 - 2)];
                    else if (cum[j0] <= cum[fa] + FitStraight + 0.05) ta = P[j0] - P[fa];
                    if (j1 >= fb - 1 && machB) tb = P[Math.Min(P.Count - 1, j1 + 2)] - P[j1];
                    else if (cum[j1] >= cum[fb] - FitStraight - 0.05) tb = P[fb] - P[j1];
                    if (ta.Len < 1e-9 || tb.Len < 1e-9) continue;
                    double ha = Math.Atan2(ta.Z, ta.X), hb = Math.Atan2(tb.Z, tb.X), old = cum[j1] - cum[j0];
                    // never a whole ring where there was none: the round bend turns about as far as the old one did
                    double turnCap = Math.Max(SmoothTurnMin, CordShapeAudit.TotalTurn(P, j0, j1) + SmoothTurnSpare);
                    int oldX = CrossingsOf(P, j0, j1);
                    foreach (double rad in SmoothRadii)
                        foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(a, ha, b, hb, rad))
                        {
                            // no arc of it comes round near a whole ring (the round loop the judge read as a "perfect circle")
                            if (dp.Turning > turnCap || Math.Max(dp.T, Math.Max(dp.Q, dp.Word >= 4 ? dp.P : 0)) > SmoothArcMax || dp.Len > old + 5.0) { No("turn/len"); continue; }
                            List<V2> arc = CordShape.Dubins.Sample(a, ha, dp, 0.05);
                            if (arc.Count == 0 || !arc.All(clear)) { No("ground"); continue; }
                            if (!arc.All(by.Near)) { No("stray"); continue; }
                            var Q = new List<V2>(P.Count + arc.Count);
                            for (int k = 0; k <= j0; k++) Q.Add(P[k]);
                            Q.AddRange(arc);
                            for (int k = j1 + 1; k < P.Count; k++) Q.Add(P[k]);
                            if (CrossingsOf(Q, j0, j0 + arc.Count) > oldX) { No("cross"); continue; }
                            int nb2 = CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, Q);
                            if (nb2 >= bad) { No("still" + nb2); continue; }
                            if (CordShapeAudit.LongestRod(Q, out _) >= Math.Max(rodNow, CordShapeAudit.RodLen)) { No("rod"); continue; }
                            double cost = nb2 * 10 + Math.Abs(dp.Len - old) * 0.3 + dp.Turning * 0.05;
                            if (cost < bestCost) { best = Q; bestCost = cost; bestBad = nb2; }
                        }
                }
                if (why != null) HopWhy("smooth " + piece.EndA + "|" + piece.EndB + " at " + worst.Value.Apex.X.ToString("0.00") + "," + worst.Value.Apex.Z.ToString("0.00") + " S " + S.ToString("0.00") + "/" + L.ToString("0.00")
                                        + (best != null ? " -> " + bestBad : " none") + " " + string.Join(" ", why.Select(kv => kv.Key + ":" + kv.Value)));
                if (best == null) break;
                P = best;
                bad = bestBad;
            }
            return P;
        }

        /// <summary>The junctions, strips, heaps, cut ends and plates near a cord that are not its own ends: a cord laid again whole or round a bend keeps <see cref="BoxKeepOff"/> off
        /// them, so it never runs over a box or lays its body under another cord's end there (pile look rule 2).</summary>
        private static List<V2> OtherBoxes(CordGraph g, CordEdge e)
        {
            var o = new List<V2>();
            foreach (KeyValuePair<VId, CordNode> kv in NearNodes(g, e))
            {
                CordNode nd = kv.Value;
                if (nd.Type == NodeType.Tangle && nd.Cells != null) foreach (Cell c in nd.Cells) o.Add(c.Centre);
                else o.Add(nd.Pos);
            }
            return o;
        }

        /// <summary>The nodes (<see cref="CordGraph.NodesNear"/>) within <see cref="NearReach"/> of an edge's own chain of cells, its two ends left out. Read off the graph alone, so the
        /// edge's key carries them (<see cref="PlanEdges"/>).</summary>
        internal static List<KeyValuePair<VId, CordNode>> NearNodes(CordGraph g, CordEdge e)
        {
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            foreach (VId v in e.Chain())
            {
                Cell c = g.Nodes.TryGetValue(v, out CordNode nd) ? nd.Cell : v.A;
                x0 = Math.Min(x0, c.X); z0 = Math.Min(z0, c.Z); x1 = Math.Max(x1, c.X); z1 = Math.Max(z1, c.Z);
            }
            return g.NodesNear(x0 - NearReach, z0 - NearReach, x1 + NearReach, z1 + NearReach).Where(kv => !kv.Key.Equals(e.A) && !kv.Key.Equals(e.B)).ToList();
        }

        /// <summary>A standing lamp's art stands a cell tall: the cell above its footprint is under the art, so a cord laid there reads as going in at the lamp's foot
        /// and out at its top (blind judge p18b, Modern_t11).</summary>
        internal static bool UnderLampArt(MachineInfo m, Cell c) => m.Kind == MachineKind.Lamp && c.X >= m.X0 && c.X < m.X0 + m.W && c.Z == m.Z0 + m.H;

        /// <summary>How many times the stretch Q[i0..i1] crosses the rest of the strand or itself; neighbouring segments are left out.</summary>
        internal static int CrossingsOf(List<V2> Q, int i0, int i1)
        {
            i0 = Math.Max(0, i0); i1 = Math.Min(Q.Count - 1, i1);
            if (i1 - i0 < 1) return 0;
            double x0 = double.MaxValue, z0 = double.MaxValue, x1 = double.MinValue, z1 = double.MinValue;
            for (int i = i0; i <= i1; i++) { x0 = Math.Min(x0, Q[i].X); z0 = Math.Min(z0, Q[i].Z); x1 = Math.Max(x1, Q[i].X); z1 = Math.Max(z1, Q[i].Z); }
            int n = 0;
            for (int j = 0; j < Q.Count - 1; j++)
            {
                V2 c = Q[j], d = Q[j + 1];
                if (Math.Max(c.X, d.X) < x0 || Math.Min(c.X, d.X) > x1 || Math.Max(c.Z, d.Z) < z0 || Math.Min(c.Z, d.Z) > z1) continue;
                for (int i = i0; i < i1; i++)
                {
                    if (Math.Abs(i - j) < 3 || (j >= i0 && j < i1 && j < i)) continue;   // a pair inside the stretch is counted once
                    if (SegCross(Q[i], Q[i + 1], c, d)) n++;
                }
            }
            return n;
        }

        private static bool SegCross(V2 a, V2 b, V2 c, V2 d)
        {
            double rx = b.X - a.X, rz = b.Z - a.Z, sx = d.X - c.X, sz = d.Z - c.Z, den = rx * sz - rz * sx;
            if (Math.Abs(den) < 1e-12) return false;
            double t = ((c.X - a.X) * sz - (c.Z - a.Z) * sx) / den, u = ((c.X - a.X) * rz - (c.Z - a.Z) * rx) / den;
            return t >= 0 && t < 1 && u >= 0 && u < 1;
        }

        /// <summary>Points of a strand bucketed on a grid, to ask whether a point lies within a reach of any of them.</summary>
        private sealed class PtGrid
        {
            private readonly Dictionary<long, List<V2>> cells = new Dictionary<long, List<V2>>();
            private readonly double r, r2;
            private static long K(int x, int z) => ((long)x << 32) ^ (uint)z;
            internal PtGrid(List<V2> pts, double reach)
            {
                r = reach; r2 = reach * reach;
                foreach (V2 p in pts)
                {
                    long k = K((int)Math.Floor(p.X / r), (int)Math.Floor(p.Z / r));
                    if (!cells.TryGetValue(k, out List<V2> l)) cells[k] = l = new List<V2>();
                    l.Add(p);
                }
            }
            internal bool Near(V2 q)
            {
                int cx = (int)Math.Floor(q.X / r), cz = (int)Math.Floor(q.Z / r);
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                        if (cells.TryGetValue(K(cx + dx, cz + dz), out List<V2> l))
                            foreach (V2 p in l) { double ex = p.X - q.X, ez = p.Z - q.Z; if (ex * ex + ez * ez <= r2) return true; }
                return false;
            }
        }

        /// <summary>How far (cells) a re-laid bend may stray from the cord it replaces.</summary>
        private const double SmoothStray = 0.8;
        /// <summary>A re-laid bend turns no further than the stretch it replaces did plus <see cref="SmoothTurnSpare"/>, and may always turn <see cref="SmoothTurnMin"/> (a round U).</summary>
        private const double SmoothTurnMin = 1.3 * Math.PI, SmoothTurnSpare = 0.45 * Math.PI;
        /// <summary>The furthest one arc of a re-laid bend may come round, radians: a U and a little, never most of a ring.</summary>
        private const double SmoothArcMax = 1.3 * Math.PI;
        /// <summary><see cref="SmoothBends"/>' radii (cells): the bar's own (a quarter turn in a whole cell is 0.64) and wider.</summary>
        private static readonly double[] SmoothRadii = { 0.66, HeapTurnR, 0.85, 1.0 };

        /// <summary>How far round an edge's chain of cells its re-lay looks for other boxes, cells.</summary>
        private const int NearReach = 4;

        /// <summary>How far a re-laid cord keeps off another junction box's middle, cells (a box's art is about 0.9 across).</summary>
        private const double BoxKeepOff = 0.55;

        private const int SmoothRounds = 6;
        /// <summary>The straight bit a fitted end keeps (cells): a junction arm's or a plug's, the shortest an end is laid with.</summary>
        private const double FitStraight = 0.15;
        /// <summary>How much cord before and after a bend <see cref="SmoothBends"/> lays again, cells, in the order tried.</summary>
        private static readonly (double, double)[] SmoothWindows = { (0.5, 0.5), (0.8, 0.8), (0.6, 1.1), (1.1, 0.6), (1.2, 1.2), (1.7, 1.7), (1.2, 2.2), (2.2, 1.2), (2.2, 2.2), (2.8, 2.8) };

        /// <summary>The longest planned path (cells) <see cref="HopWhole"/> may lay again.</summary>
        public const double HopMaxPath = 4.5;

        private struct HopEnd
        {
            public V2 T, Arrive;
            public double Straight;
            public Func<V2, bool> Clear;
        }

        /// <summary>The fittings one end of an edge may take a whole-laid cord at (<see cref="EndPose"/>; a one-cell machine with no wall home on any open side). Empty when the end has no
        /// fitting or a strip's socket wants the cord swung round the strip first.</summary>
        private static List<HopEnd> HopEnds(CordWorld w, CordGraph g, CordEdge e, bool atA, List<V2> C, BuildOptions opt)
        {
            var o = new List<HopEnd>();
            CordNode nd = g.Nodes[atA ? e.A : e.B];
            if (!EndPose(w, g, e, atA, C, 0, 1, opt, out V2 target, out V2 arrive, out double straight, out _, out int swing) || swing != 0) return o;
            MachineInfo m = nd.IsMachine ? nd.Machine : null;
            o.Add(new HopEnd { T = target, Arrive = arrive.Norm(), Straight = straight, Clear = ArriveClear(w, C, target, m) });
            if (m != null && m.W == 1 && m.H == 1 && !m.HasHome)
                foreach (Cell side in new[] { new Cell(m.X0, m.Z0 + 1), new Cell(m.X0 + 1, m.Z0), new Cell(m.X0, m.Z0 - 1), new Cell(m.X0 - 1, m.Z0) })
                {
                    V2 t2 = m.Kind == MachineKind.Lamp ? LampEntry(m, side.Centre) : CordGraph.PlugPoint(m, side, g.Slides(m));
                    if (V2.Dist(t2, target) < 0.05 || !w.IsWalkable(t2.Floor)) continue;
                    V2 a2 = IntoMachine(m, t2);
                    if (g.Slides(m)) a2 = CordGraph.SlideArrive(m, t2, a2);
                    o.Add(new HopEnd { T = t2, Arrive = a2.Norm(), Straight = straight, Clear = ArriveClear(w, C, t2, m) });
                }
            return o;
        }

        /// <summary>
        /// A short cord laid again whole, from one fitting's straight bit to the other's: the Dubins path between the two poses at <see cref="HopRadii"/> (no tighter than a heap
        /// cable's turn), bowed off to a side in one lazy C or S for its slack, flat where it leaves and meets each straight bit. The laid cord's ends were each come round to on their
        /// own, so a junction box a cell or two from its machine sent a "&lt;" or a hook into one of them (live, every look, pass 18). Of the draws the bar counts clean, on clear ground and
        /// with no straight rod, the one whose length lies nearest a loose cord's (a drawn multiple of the gap round <see cref="HopSlack"/>) is kept; null when none is clean.
        /// </summary>
        private static List<V2> HopWhole(CordWorld w, CordGraph g, CordEdge e, List<V2> C, BuildOptions opt, LaidPiece piece, string key, Func<Cell, bool> isLive)
        {
            List<HopEnd> endsA = HopEnds(w, g, e, true, C, opt), endsB = HopEnds(w, g, e, false, C, opt);
            if (endsA.Count == 0 || endsB.Count == 0) { HopWhy?.Invoke(piece.EndA + "|" + piece.EndB + " no ends " + endsA.Count + "/" + endsB.Count); return null; }
            var why = HopWhy == null ? null : new Dictionary<string, int>();
            void No(string t) { if (why != null) why[t] = why.TryGetValue(t, out int k) ? k + 1 : 1; }
            CordNode na = g.Nodes[e.A], nb = g.Nodes[e.B];
            CordRng r = CordRng.Of(opt.Seed, "hop", key);
            List<V2> boxes = OtherBoxes(g, e);
            int sg = r.Sign();
            double aim = r.Range(HopSlack - 0.1, HopSlack + 0.12), sBias = r.Range(-0.08, 0.08);
            List<V2> best = null;
            double bestCost = double.MaxValue;
            foreach (HopEnd A in endsA)
                foreach (HopEnd B in endsB)
                {
                    if (best == null) best = FitCorner(w, g, e, A, B, boxes, piece, na, nb);   // two fittings too close to come round between: one clean small turn, not a hook
                    if (best != null) { bestCost = 0; break; }
                }
            if (best != null) { HopWhy?.Invoke(piece.EndA + "|" + piece.EndB + " CORNER"); return best; }
            foreach (HopEnd A in endsA)
                foreach (HopEnd B in endsB)
                {
                    V2 ea = A.T - A.Arrive * A.Straight, eb = B.T - B.Arrive * B.Straight;
                    double gap = Math.Max(V2.Dist(A.T, B.T), 0.3);
                    double ha = Math.Atan2(-A.Arrive.Z, -A.Arrive.X), hb = Math.Atan2(B.Arrive.Z, B.Arrive.X);
                    HopEnd a0 = A, b0 = B;
                    Func<V2, bool> clear = q => V2.Dist(q, a0.T) < 0.3 || V2.Dist(q, b0.T) < 0.3 || (a0.Clear(q) && b0.Clear(q) && !boxes.Any(bx => V2.Dist(q, bx) < BoxKeepOff));
                    foreach (double rad in HopRadii)
                        foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(ea, ha, eb, hb, rad).OrderBy(d => d.Len).Take(2))
                        {
                            if (dp.Turning > Math.PI) { No("turns"); continue; }
                            var basePts = new List<V2> { ea };
                            basePts.AddRange(CordShape.Dubins.Sample(ea, ha, dp, 0.05));
                            if (basePts.Count < 3) { No("short"); continue; }
                            double[] cl = Geo.CumLen(basePts);
                            double Lb = cl[cl.Length - 1];
                            var nrm = new V2[basePts.Count];
                            for (int k = 0; k < basePts.Count; k++) { Geo.TanNorm(basePts, k, out _, out V2 nn); nrm[k] = nn; }
                            for (int shape = 0; shape < 2; shape++)
                                foreach (double f in HopDepths)
                                    foreach (int side in new[] { sg, -sg })
                                    {
                                        if (f == 0 && (side != sg || shape == 1)) continue;
                                        double D = side * f * Lb;
                                        var mid = new List<V2>(basePts.Count);
                                        bool ok = true;
                                        for (int k = 0; k < basePts.Count && ok; k++)
                                        {
                                            double u = cl[k] / Lb, s1 = Math.Sin(Math.PI * u);
                                            double y = shape == 0 ? s1 * s1 : Math.Sin(2 * Math.PI * u) * s1 * 1.3;
                                            V2 q = basePts[k] + nrm[k] * (D * y);
                                            if (!clear(q)) ok = false;
                                            mid.Add(q);
                                        }
                                        if (!ok) { No("ground"); continue; }
                                        var P = new List<V2>();
                                        int na2 = Math.Max(1, (int)Math.Round(A.Straight / 0.05)), nb2 = Math.Max(1, (int)Math.Round(B.Straight / 0.05));
                                        for (int q = 0; q < na2; q++) P.Add(A.T - A.Arrive * (A.Straight * q / na2));
                                        P.AddRange(mid);
                                        for (int q = 1; q <= nb2; q++) P.Add(eb + B.Arrive * (B.Straight * q / nb2));
                                        P[P.Count - 1] = B.T;
                                        double ratio = Geo.Length(P) / gap;
                                        if (ratio > HopMaxRatio) { No("long"); continue; }
                                        bool rod = CordShapeAudit.LongestRod(P, out _) >= CordShapeAudit.RodLen;
                                        if (na.IsMachine && na.Machine != null) P = IntoArt(P, true, na.Machine, g.Slides(na.Machine));
                                        if (nb.IsMachine && nb.Machine != null) P = IntoArt(P, false, nb.Machine, g.Slides(nb.Machine));
                                        P = PastFace(P, true, na);
                                        P = PastFace(P, false, nb);
                                        if (CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, P) > 0) { No("bends"); continue; }
                                        // a loose cord, not a taut one: short of the slack census's 1.15 it costs, a straight rod costs more
                                        double cost = Math.Abs(ratio - aim) + (ratio < 1.15 ? 0.4 : 0) + (rod ? 1 : 0) + (shape == 1 ? 0.04 + sBias : 0) + 0.01 * (rad - HopRadii[0]);
                                        if (cost < bestCost) { best = P; bestCost = cost; }
                                    }
                        }
                }
            if (why != null) HopWhy(piece.EndA + "|" + piece.EndB + (best != null ? " LAID " + bestCost.ToString("0.00") : " none") + " ends " + endsA.Count + "/" + endsB.Count + " " + string.Join(" ", why.Select(kv => kv.Key + ":" + kv.Value))
                                    + " A " + string.Join(";", endsA.Select(h => h.T + "<" + h.Arrive + "/" + h.Straight.ToString("0.00"))) + " B " + string.Join(";", endsB.Select(h => h.T + "<" + h.Arrive + "/" + h.Straight.ToString("0.00"))));
            return best;
        }

        /// <summary>
        /// A lead between two fittings that face across a corner too close to come round at the bar's radius (<see cref="CordShapeAudit.FittingsForce"/>: a box on a mast's pole and
        /// the wall plate beside it, a box and the box a diagonal cell off): the plain Dubins path between their straight bits at the widest of <see cref="FitRadii"/> that turns no
        /// further than the facings ask, so the cord makes one clean small turn. Laid by the grid it hooked past the corner and back (live, every look's mast foot), and
        /// <see cref="SmoothBends"/> threw a ring there (blind judge p18b). Null when the fittings do not force a bend or no clean turn lies on clear ground.
        /// </summary>
        private static List<V2> FitCorner(CordWorld w, CordGraph g, CordEdge e, HopEnd A, HopEnd B, List<V2> boxes, LaidPiece piece, CordNode na, CordNode nb)
        {
            if (na.IsMachine || nb.IsMachine) return null;
            V2 ea = A.T - A.Arrive * A.Straight, eb = B.T - B.Arrive * B.Straight;
            double ha = Math.Atan2(-A.Arrive.Z, -A.Arrive.X), hb = Math.Atan2(B.Arrive.Z, B.Arrive.X);
            var probe = new List<V2> { A.T, ea, eb, B.T };
            if (V2.Dist(ea, eb) > CordShapeAudit.FitForceLen) return null;
            foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(ea, ha, eb, hb, CordShapeAudit.FitForceR))
                if (dp.Turning <= CordShapeAudit.FitForceTurn) return null;
            double need = Math.Abs(Wrap(hb - ha));
            Func<V2, bool> clear = q => V2.Dist(q, A.T) < 0.3 || V2.Dist(q, B.T) < 0.3 || (A.Clear(q) && B.Clear(q) && !boxes.Any(bx => V2.Dist(q, bx) < BoxKeepOff));
            foreach (double rad in FitRadii)
                foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(ea, ha, eb, hb, rad).OrderBy(d => d.Turning))
                {
                    if (dp.Turning > Math.Max(need + FitTurnSpare, Math.PI)) break;   // a corner or a lazy S, never a loop
                    List<V2> arc = CordShape.Dubins.Sample(ea, ha, dp, 0.05);
                    if (arc.Count == 0 || !arc.All(clear)) continue;
                    var P = new List<V2>();
                    int na2 = Math.Max(1, (int)Math.Round(A.Straight / 0.05)), nb2 = Math.Max(1, (int)Math.Round(B.Straight / 0.05));
                    for (int q = 0; q < na2; q++) P.Add(A.T - A.Arrive * (A.Straight * q / na2));
                    P.Add(ea);
                    P.AddRange(arc);
                    for (int q = 1; q <= nb2; q++) P.Add(eb + B.Arrive * (B.Straight * q / nb2));
                    P[P.Count - 1] = B.T;
                    P = PastFace(P, true, na);
                    P = PastFace(P, false, nb);
                    if (CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, P) > 0) continue;
                    return P;
                }
            return null;
        }

        /// <summary><see cref="FitCorner"/>'s radii, widest first (cells).</summary>
        private static readonly double[] FitRadii = { 0.6, 0.52, 0.45, 0.38, 0.32 };
        /// <summary>How much further than the two facings ask <see cref="FitCorner"/>'s turn may go, radians.</summary>
        private const double FitTurnSpare = 0.3;

        /// <summary>Lab trace of <see cref="HopWhole"/>: what each cord laid again whole met.</summary>
        internal static Action<string> HopWhy;

        /// <summary>A whole-laid short cord's Dubins radii (cells): a heap cable's turn and wider.</summary>
        private static readonly double[] HopRadii = { HeapTurnR, 0.85, 1.0 };
        /// <summary>How deep a whole-laid short cord's bow is, as a share of its path; 0 is the plain Dubins path.</summary>
        private static readonly double[] HopDepths = { 0.3, 0.22, 0.15, 0.08, 0 };
        /// <summary>The length a whole-laid short cord aims at, as a multiple of the gap; it never takes one longer than <see cref="HopMaxRatio"/>.</summary>
        private const double HopSlack = 1.3, HopMaxRatio = 2.4;

        /// <summary>A strip right beside a machine points its lead at it, so that lead is a short straight nub off the strip's end and on under the machine's art. Sent to the machine's sliding plug point, off to
        /// one side, it doubled back round the strip's end in a flat hook (blind judge's "two short cords to one machine"; shape lab). Null when this edge is no such lead, or the line misses the machine.</summary>
        private static List<V2> StripNub(CordGraph g, CordEdge e, BuildOptions opt)
        {
            foreach (bool atA in new[] { true, false })
            {
                VId v = atA ? e.A : e.B;
                CordNode nd = g.Nodes[v], far = g.Nodes[atA ? e.B : e.A];
                if (nd.Type != NodeType.Junction || !far.IsMachine || far.Machine == null || opt.PileFor(nd.Cell) != PileArt.Strips) continue;
                V2 ad = ArmDir(g, e, atA);
                var arm = new Cell((int)ad.X, (int)ad.Z);
                if (!g.MachineArmsOf(v).Contains(arm)) continue;
                StripPose sp = PoseStrip(g, v, opt.Seed);
                if (sp.SocketFor(arm) >= 0) continue;
                var line = new List<V2>();
                double reached = -1;
                for (double t = 0; t <= StripNubReach; t += 0.05)
                {
                    V2 q = sp.LeadTip + sp.Along * t;
                    line.Add(q);
                    if (reached < 0 && far.Machine.Contains(q.Floor)) reached = t;
                    if (reached >= 0 && t >= reached + StripNubUnder) break;
                }
                if (reached < 0) continue;
                // still a cord, not a rod: a slight belly on what shows
                int sgn = CordRng.Of(opt.Seed, "nub", nd.Cell.X, nd.Cell.Z).Sign();
                for (int i = 0; i < line.Count; i++)
                    line[i] = line[i] + sp.Side * (sgn * StripNubBelly * reached * Math.Sin(Math.PI * Math.Min(1, i * 0.05 / Math.Max(reached, 0.05))));
                if (!atA) return line;
                line.Reverse();
                return line;
            }
            return null;
        }

        private const double StripNubReach = 1.8, StripNubUnder = 0.3, StripNubBelly = 0.12;

        /// <summary>A junction box right beside a machine, its arm pointing at it: the lead is the arm's own short plug on straight under the machine's art. Laid to the machine's plug
        /// point, which sits at or behind the arm's tip, it swung out sideways and hooked back in a 140-degree V beside the box (live, every look: a lamp over its box, a battery on
        /// its run). Null when this edge is no such lead, the box is a blob or a strip, or the arm's line misses the machine within <see cref="BoxNubReach"/>.</summary>
        private static List<V2> BoxNub(CordWorld w, CordGraph g, CordEdge e, BuildOptions opt)
        {
            foreach (bool atA in new[] { true, false })
            {
                VId v = atA ? e.A : e.B;
                CordNode nd = g.Nodes[v], far = g.Nodes[atA ? e.B : e.A];
                if (nd.Type != NodeType.Junction || nd.IsBlob || !v.IsCellish || !far.IsMachine || far.Machine == null || opt.PileFor(nd.Cell) == PileArt.Strips) continue;
                V2 a = ArmDir(g, e, atA);
                if (!g.MachineArmsOf(v).Contains(new Cell((int)a.X, (int)a.Z))) continue;
                MachineInfo m = far.Machine;
                if (m.Contains(nd.Cell)) continue;
                double under = StripNubUnder + ArtInset(m, a);
                V2 tip = nd.Pos + a * (ArmTuck * JunctionScale);
                double reached = -1;
                for (double t = 0; t <= BoxNubReach; t += 0.05)
                    if (m.Contains((tip + a * t).Floor)) { reached = t; break; }
                if (reached < 0) continue;
                // a cord, not a rod: one smooth bow to a side, flat where it leaves the arm and where it goes in under the art (sin squared), deeper the longer the gap.
                // Under BowTurn a cell its heading never turns past the bar's 90 degrees (its widest swing is 2 atan(pi depth / gap))
                CordRng r = CordRng.Of(opt.Seed, "nub", nd.Cell.X, nd.Cell.Z);
                int sgn = r.Sign();
                double gap = reached + 0.05, depth = Math.Min(gap * Math.Tan(BowTurn / 2) / Math.PI, StripNubBelly * reached + (reached > 0.4 ? r.Range(0.1, 0.22) * gap : 0));
                V2 side = new V2(-a.Z, a.X);
                var line = new List<V2>();
                bool clear = true;
                for (double t = 0; t <= reached + 1e-6; t += 0.05)
                {
                    double u = Math.Min(1, t / gap), b = Math.Sin(Math.PI * u);
                    V2 q = tip + a * t + side * (sgn * depth * b * b);
                    if (t < reached && !NubGround(w, m, q)) { clear = false; break; }
                    line.Add(q);
                }
                if (!clear) continue;
                if (line.Count < 2) line.Add(tip + a * 0.05);
                // on under the art to the centroid, as every machine end goes
                line = IntoArt(line, false, m, g.Slides(m));
                if (atA) return line;
                line.Reverse();
                return line;
            }
            return null;
        }

        /// <summary>How far past its arm's tip a junction box's machine may begin for the arm to plug straight into it, cells: the box beside it, or one cell between.</summary>
        private const double BoxNubReach = 1.6;
        /// <summary>The most a box's bowed lead swings its heading, radians (well under the bar's 90 degrees).</summary>
        private const double BowTurn = 70 * Math.PI / 180;

        /// <summary>Ground a box's lead may cross before its machine: walkable, no furniture, no other machine.</summary>
        private static bool NubGround(CordWorld w, MachineInfo own, V2 q)
        {
            Cell c = q.Floor;
            if (!w.IsWalkable(c) || w.IsFurniture(c) || w.IsDoor(c)) return false;
            foreach (MachineInfo o in w.Machines)
                if (o.Contains(c) && !(o.X0 == own.X0 && o.Z0 == own.Z0 && o.W == own.W && o.H == own.H)) return false;
            return true;
        }

        /// <summary>How far a diving cord runs on past the face into a wall, rock or building (hidden by it), cells. Water: 0,
        /// the cord meets the water's edge like a conduit stub into water.</summary>
        internal static double DiveOverrun(BlockKind k) => k == BlockKind.Water ? 0 : PastFaceDepth;

        /// <summary>The plate drawn where a cord dives into / comes out of a barrier: a wall plate on a wall, a hole in rock,
        /// nothing for water or a building (the building's own art hides the cord; water has no plate art).</summary>
        internal static DecalKind? DivePlate(BlockKind k) => k == BlockKind.Wall ? DecalKind.StubWall : k == BlockKind.Rock ? DecalKind.StubRock : (DecalKind?)null;

        /// <summary>Dive-through lay (owner 2026-10-06): the plan's surface sections are laid as separate strands, each ending
        /// square on its dive face (straight in along the face normal, on just past the face) with a plate on each wall/rock
        /// face; the edge's own end art goes only on the first section's start and the last section's end.</summary>
        private static LaidPiece LayDiving(CordWorld w, CordGraph g, CordEdge e, string key, BuildOptions opt, Func<Cell, bool> isLive,
                                           LaidPiece piece, CordPlan pl, CordNode na, CordNode nb)
        {
            LayParams prm = opt.Lay;
            if ((na.Type == NodeType.Terminal && !na.Seam) || (nb.Type == NodeType.Terminal && !nb.Seam)) prm = prm.WithoutShortBow();
            CordRng rr = CordRng.Of(opt.Seed, "cord", key, "dive");
            int nsec = pl.Dives.Count + 1;
            var secC = new List<List<V2>>();
            for (int si = 0; si < nsec; si++)
            {
                int a = si == 0 ? 0 : pl.Dives[si - 1].Index + 1, b = si == nsec - 1 ? pl.Points.Count - 1 : pl.Dives[si].Index;
                List<V2> C = CordPlanner.RoundCorners(pl.Points.GetRange(a, b - a + 1));
                CordLayer.ProjectOut(w, C);
                secC.Add(C);
            }
            int n = rr.Int(prm.CordsMin, Math.Max(prm.CordsMin, prm.CordsMax));
            if (DeviceLead(na, nb)) n = 1;
            double slack = rr.Range(prm.SlackLo, prm.SlackHi) * prm.SlackScale;
            int limpSideA = CordRng.Of(opt.Seed, "limp", na.Cell.X, na.Cell.Z).Sign();
            int limpSideB = CordRng.Of(opt.Seed, "limp", nb.Cell.X, nb.Cell.Z).Sign();
            double laid = 0, Ltot = 0;
            foreach (List<V2> C in secC) Ltot += Geo.Length(C);
            for (int i = 0; i < n; i++)
            {
                double lat = n == 1 ? 0 : (i - (n - 1) / 2.0) * 0.1;
                for (int si = 0; si < nsec; si++)
                {
                    List<V2> C = secC[si];
                    double L = Geo.Length(C);
                    double[] cl = Geo.CumLen(C);
                    var P = new List<V2>(C.Count);
                    for (int k = 0; k < C.Count; k++)
                    {
                        Geo.TanNorm(C, k, out V2 t, out V2 nn);
                        double ramp = Math.Min(1, Math.Min(cl[k], L - cl[k]) / 0.3) * 0.6 + 0.4;
                        P.Add(C[k] + nn * (lat * ramp));
                    }
                    double maxExtra = prm.SlackScale <= 0 ? 0 : Math.Min(Math.Max(slack * L, prm.MinExtra * Math.Min(1, prm.SlackScale)), prm.MaxExtra);
                    SettleStats settle = null;
                    if (L > 1.2 && prm.SlackScale > 0)
                        P = SprawlOnce(w, P, C, prm, slack, maxExtra, opt.Seed, key, i, n, si, out settle);
                    bool diveA = si > 0, diveB = si < nsec - 1;
                    if (!diveA) P = AttachEnd(w, g, e, true, P, i, n, opt);
                    if (!diveB) P = AttachEnd(w, g, e, false, P, i, n, opt);
                    // each dive end arrives square on its face, straight in along the face normal
                    if (diveA) { DiveSpan d = pl.Dives[si - 1]; P = CordLayer.Approach(w, P, false, d.OutFace, d.OutInto, 0.15); }
                    if (diveB) { DiveSpan d = pl.Dives[si]; P = CordLayer.Approach(w, P, true, d.InFace, d.InInto, 0.15); }
                    if (!diveA && na.Type == NodeType.Terminal && !na.Seam && !isLive(na.Cell)) CordLayer.LimpTail(w, P, false, limpSideA, i);
                    if (!diveB && nb.Type == NodeType.Terminal && !nb.Seam && !isLive(nb.Cell)) CordLayer.LimpTail(w, P, true, limpSideB, i);
                    bool fell = false;
                    if (P.Skip(1).Take(Math.Max(0, P.Count - 2)).Any(q => !w.IsWalkable(q.Floor)))
                    {
                        P = new List<V2>(C);
                        fell = true;
                    }
                    if (!fell && prm.FairBends) P = CordShape.Fair(w, P, diveA ? 0.2 : FairPin(na, isLive), diveB ? 0.2 : FairPin(nb, isLive), CordShapeAudit.OwnMachines(w, piece.EndA, piece.EndB));
                    if (!diveA && na.IsMachine && na.Machine != null) P = IntoArt(P, true, na.Machine, g.Slides(na.Machine));
                    if (!diveB && nb.IsMachine && nb.Machine != null) P = IntoArt(P, false, nb.Machine, g.Slides(nb.Machine));
                    if (!diveA) P = PastFace(P, true, na);
                    if (!diveB) P = PastFace(P, false, nb);
                    if (diveA) { DiveSpan d = pl.Dives[si - 1]; P = Overrun(P, true, d.OutFace, d.OutInto, DiveOverrun(d.OutKind)); }
                    if (diveB) { DiveSpan d = pl.Dives[si]; P = Overrun(P, false, d.InFace, d.InInto, DiveOverrun(d.InKind)); }
                    if (!fell) P = CordShape.Unfold(w, P, LimpSkip(na, nb, isLive));
                    piece.Strands.Add(new CordStrand { Pts = P, S0 = rr.Value(), FellBack = fell, Settle = settle, DiveA = diveA, DiveB = diveB, DoorStrays = CordShape.DoorStrays(w, P, C) });
                    laid += Geo.Length(P);
                }
            }
            foreach (DiveSpan d in pl.Dives)
            {
                DecalKind? kin = DivePlate(d.InKind), kout = DivePlate(d.OutKind);
                if (kin.HasValue) piece.Decals.Add(WallMount.EntryDecal(kin.Value, d.InFace, d.InInto));
                if (kout.HasValue) piece.Decals.Add(WallMount.EntryDecal(kout.Value, d.OutFace, d.OutInto));
            }
            piece.Dives = pl.Dives.Count;
            piece.PathLen = Ltot;
            piece.LaidRatio = n > 0 ? laid / n / Math.Max(Ltot, 1e-6) : 0;
            EndDecor(w, g, e, e.A, na, piece, true, opt, isLive);
            EndDecor(w, g, e, e.B, nb, piece, false, opt, isLive);
            // a dived cord's route depends on walls anywhere (a door opened far off may give it a surface route): its corridor
            // is the whole map, so any walkability change re-plans it
            piece.CX0 = 0; piece.CZ0 = 0; piece.CX1 = w.Width - 1; piece.CZ1 = w.Height - 1;
            return piece;
        }

        /// <summary>Run one end of P on from the face along into, to just past the face (the barrier hides the overrun).</summary>
        private static List<V2> Overrun(List<V2> P, bool atStart, V2 face, V2 into, double depth)
        {
            if (P.Count < 2) return P;
            V2 tip = atStart ? P[0] : P[P.Count - 1];
            V2 to = face + into * depth;
            double along = (to.X - tip.X) * into.X + (to.Z - tip.Z) * into.Z;
            if (along <= 0.005) return P;
            var o = new List<V2>(P);
            int k = Math.Max(1, (int)Math.Ceiling(along / 0.04));
            var ext = new List<V2>();
            for (int i = 1; i <= k; i++) ext.Add(tip + into * (along * i / k));
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); } else o.AddRange(ext);
            return o;
        }

        // ---------------------------------------------------------------- art fit (polish pass 2026-10-02)
        // Geometry of the shipped art, measured from the PNGs in canvas units (1 = the decal's side):
        // Junction_Tape is a T whose arms (art +X, -X, -Z) meet 0.152 above the canvas centre;
        // Junction_Tin is a centred 4-arm cross. Wall plates and rock holes: WallMount (round 4).
        // Round 5 (owner 2026-10-04, station 4: "T and + power junctions look very poor quality: need to make the wires thinner,
        // and ensure the junction box connectors are thicker to cover them. Make + and T connectors be relatively the same
        // central size/center"): the boxes are drawn 1.15x (round-5 brick art, af013af66: arms 18-28 px of 128 -> 0.16-0.25
        // cells thick over a 0.08 wire), T and + at the SAME scale with their arm-meeting point on the node; the art draws
        // both as one brick, same size and centre (T = the X shifted up TapeAnchorZ).
        public const double JunctionScale = 1.15, TapeAnchorZ = 0.152, ArmTuck = 0.40;
        public const double PlugScale = 0.55, PlugInset = 0.05;

        public struct JunctionPose
        {
            public DecalKind Kind;
            public double Angle;
            internal V2 Centre;
            public int Arms;
        }

        internal static V2 Snap4(V2 d)
        {
            if (Math.Abs(d.X) >= Math.Abs(d.Z)) return new V2(d.X < 0 ? -1 : 1, 0);
            return new V2(0, d.Z < 0 ? -1 : 1);
        }

        /// <summary>The cardinal direction an edge leaves a cell node in: toward the next cell of its chain. A blob junction
        /// reads it from the blob's middle, not from one of its cells.</summary>
        internal static V2 ArmDir(CordGraph g, CordEdge e, bool atA)
        {
            VId v = atA ? e.A : e.B;
            VId nxt = e.Via.Count > 0 ? (atA ? e.Via[0] : e.Via[e.Via.Count - 1]) : (atA ? e.B : e.A);
            Cell c = g.Nodes[v].Cell;
            V2 d;
            if (g.Nodes[v].IsBlob)
            {
                V2 toward = nxt.IsCellish ? nxt.A.Centre : (atA ? e.PB : e.PA);
                return Snap4(toward - g.Nodes[v].Pos);
            }
            if (nxt.IsCellish) d = new V2(nxt.A.X - c.X, nxt.A.Z - c.Z);
            else if (nxt.T == 's') d = nxt.A == c ? new V2(nxt.B.X - c.X, nxt.B.Z - c.Z) : new V2(nxt.A.X - c.X, nxt.A.Z - c.Z);
            else d = (atA ? e.PB : e.PA) - g.Nodes[v].Pos;
            return Snap4(d);
        }

        /// <summary>Which junction piece and how it is turned so an arm lies along every arriving cord:
        /// four directions take the tin cross, fewer the taped T with its missing arm where no cord comes.</summary>
        public static JunctionPose PoseJunction(CordGraph g, VId v, ulong seed)
        {
            CordNode nd = g.Nodes[v];
            CordRng r = CordRng.Of(seed, "jdecal", nd.Cell.X, nd.Cell.Z);
            if (nd.IsBlob || !v.IsCellish)
                return new JunctionPose { Kind = DecalKind.JunctionTin, Angle = 0, Centre = nd.Pos, Arms = 4 };
            HashSet<Cell> dirs = g.ArmsOf(v);
            if (dirs.Count >= 4)
                return new JunctionPose { Kind = DecalKind.JunctionTin, Angle = r.Int(0, 3) * Math.PI / 2, Centre = nd.Pos, Arms = 4 };
            var order = new[] { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
            List<Cell> missing = order.Where(c => !dirs.Contains(c)).ToList();
            Cell m = missing[r.Int(0, missing.Count - 1)];
            double angle = Math.Atan2(m.Z, m.X) - Math.PI / 2;           // the art's missing arm is its +Z
            V2 anchor = new V2(0, TapeAnchorZ * JunctionScale);
            V2 rot = new V2(anchor.X * Math.Cos(angle) - anchor.Z * Math.Sin(angle), anchor.X * Math.Sin(angle) + anchor.Z * Math.Cos(angle));
            return new JunctionPose { Kind = DecalKind.JunctionTape, Angle = angle, Centre = nd.Pos - rot, Arms = 3 };
        }

        // ---------------------------------------------------------------- the Modern junction strip (d_modern_junction_strip)
        // PowerStrip.png (64x32), read off the PNG in canvas widths from its centre: four plugs on art +Z, their heads at these X
        // and StripHeadZ; the strip's own lead leaves its +X end at (StripLeadX, StripLeadZ).
        public const double JunctionStripScale = 0.9, StripHeadZ = -0.03, StripLeadX = 0.46, StripLeadZ = -0.04;
        public static readonly double[] StripHeads = { -0.34, -0.14, 0.06, 0.26 };
        /// <summary>How far off square a junction strip lies, radians: dropped on the floor, not installed.</summary>
        public const double StripSkew = 0.22;
        /// <summary>How far past the strip's free end a cord from behind swings to come round to the sockets.</summary>
        public const double StripWrap = 0.45;
        /// <summary>How far out from its socket a cord coming in from the side has straightened up to arrive square.</summary>
        public const double StripSwing = 0.3;
        /// <summary>How far a strip plugged into the wall beside it stands back from the wall, cells.</summary>
        public const double StripWallGap = 0.3;

        public struct StripPose
        {
            internal V2 Centre, Along, Side;
            public double Angle;
            /// <summary>The arm the strip's own lead takes; every other arm plugs into a socket.</summary>
            internal Cell LeadArm;
            internal Cell SocketArm, FreeArm, BackArm;
            /// <summary>The socket each arm plugs into, or -1 (no such arm).</summary>
            public int SocketOfSocketArm, SocketOfFreeArm, SocketOfBackArm;

            internal V2 At(double x, double z) => Centre + Along * (x * JunctionStripScale) + Side * (z * JunctionStripScale);
            /// <summary>Where a cord plugged into socket k ends: the plug's own centre, its head on the socket.</summary>
            internal V2 Tip(int k) => At(StripHeads[k], StripHeadZ) + Side * (0.46 * PilePlugScale);
            internal V2 LeadTip => At(StripLeadX, StripLeadZ);

            internal int SocketFor(Cell arm) =>
                arm == SocketArm ? SocketOfSocketArm : arm == FreeArm ? SocketOfFreeArm : arm == BackArm ? SocketOfBackArm : -1;
        }

        private static Cell Turn(Cell d) => new Cell(-d.Z, d.X);                         // +90 degrees
        private static V2 AsV2(Cell d) => new V2(d.X, d.Z);

        /// <summary>How a Modern junction's strip lies. The art is fixed: looking at the sockets, the lead leaves to the right. So
        /// the sockets face the T's stem (a 4-way picks a side from the seed), the lead takes the arm to their right, the arm to
        /// their left comes in over the free end, and a 4-way's back arm swings round that end, inside it, so the two never cross.
        /// A pure function of the graph and the seed, so the strip and the cords that plug into it agree.</summary>
        public static StripPose PoseStrip(CordGraph g, VId v, ulong seed)
        {
            CordNode nd = g.Nodes[v];
            CordRng r = CordRng.Of(seed, "jstrip", nd.Cell.X, nd.Cell.Z);
            HashSet<Cell> arms = g.ArmsOf(v);
            var order = new[] { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
            // the sockets' side: opposite the arm a T lacks; a 4-way (or a blob with every side taken) any side; never empty-handed
            List<Cell> missing = order.Where(c => !arms.Contains(c)).ToList();
            Cell faces = missing.Count > 0 ? new Cell(-missing[0].X, -missing[0].Z) : order[r.Int(0, 3)];
            if (missing.Count > 1)
            {
                // fewer than three arms: keep the sockets on a side a cord really arrives from, and the lead on its own arm
                foreach (Cell c in order) if (arms.Contains(c) && arms.Contains(new Cell(c.Z, -c.X))) { faces = c; break; }
            }
            // a machine right beside the strip takes the strip's own lead: with the sockets facing it, a through cord plugging in ran along
            // the machine's edge and read as a second cord into it (blind judge; owner 2026-11-07, "multiple cables for no reason")
            bool beside = false;
            foreach (Cell c in order)
                if (g.MachineArmsOf(v).Contains(c)) { faces = new Cell(-c.Z, c.X); beside = true; break; }
            // and a strip right beside a wall outlet is plugged into it by its own lead: with the sockets facing the wall, the cords to its
            // other arms plugged in beside the outlet and read as two or three cables going into the one outlet (owner 2026-11-07)
            bool toWall = false;
            if (!beside)
                foreach (Cell c in order)
                    if (g.WallArmsOf(v).Contains(c)) { faces = new Cell(-c.Z, c.X); toWall = true; break; }
            Cell lead = new Cell(faces.Z, -faces.X);                                         // -90 degrees from the sockets
            Cell free = new Cell(-lead.X, -lead.Z), back = new Cell(-faces.X, -faces.Z);
            bool hasBack = arms.Contains(back), hasFree = arms.Contains(free), hasFace = arms.Contains(faces);
            double skew = r.Range(-StripSkew, StripSkew);
            V2 along = CordAudit.Rot(AsV2(lead), skew), side = CordAudit.Rot(AsV2(faces), skew);
            return new StripPose
            {
                // the plugs stand out on the sockets' side: the strip sits back a little, so strip and plugs centre on the node
                // one plugged into the wall stands back from it a little, so its lead is a short cord and not its nub pressed on the outlet
                Centre = nd.Pos - side * 0.06 - along * (toWall ? StripWallGap : 0),
                Along = along, Side = side, Angle = Math.Atan2(along.Z, along.X),
                LeadArm = lead, SocketArm = faces, FreeArm = free, BackArm = back,
                SocketOfBackArm = hasBack ? 0 : -1,
                SocketOfFreeArm = hasFree ? (hasBack ? 1 : 0) : -1,
                SocketOfSocketArm = hasFace ? 2 : -1,
            };
        }

        /// <summary>The cardinal direction from a point just outside a machine's footprint into it.</summary>
        internal static V2 IntoMachine(MachineInfo m, V2 p)
        {
            double l = m.X0 - p.X, rgt = p.X - (m.X0 + m.W), b = m.Z0 - p.Z, t = p.Z - (m.Z0 + m.H);
            double best = Math.Max(Math.Max(l, rgt), Math.Max(b, t));
            if (best == l) return new V2(1, 0);
            if (best == rgt) return new V2(-1, 0);
            if (best == b) return new V2(0, 1);
            return new V2(0, -1);
        }

        /// <summary>The lateral spread axis for parallel strands, the same whichever way the cord runs,
        /// so a strand keeps its side from one end of a short cord to the other.</summary>
        private static V2 Side(V2 a) => new V2(Math.Abs(a.Z), Math.Abs(a.X)).Norm();

        /// <summary>Reshape one end of a laid strand so it arrives where and how the end's art expects:
        /// into a junction arm's tip along the arm, onto the plug point heading into the machine, onto
        /// a stub face heading into it, or straight out of a conduit end.</summary>
        /// <summary>How an end's fitting takes the cord: the point it plugs in at (<paramref name="target"/>), the way it goes in there, the straight bit before it, how roomy the old
        /// approach may be, and for a strip socket whether the cord must first swing round the strip (1 from behind, 2 past its free end). False for an end with no fitting.</summary>
        private static bool EndPose(CordWorld w, CordGraph g, CordEdge e, bool atA, List<V2> P, int i, int n, BuildOptions opt, out V2 target, out V2 arrive, out double straight, out double roomy, out int swing)
        {
            VId v = atA ? e.A : e.B;
            CordNode nd = g.Nodes[v];
            double lat = n == 1 ? 0 : (i - (n - 1) / 2.0);
            target = arrive = default(V2);
            straight = 0.15; roomy = 0; swing = 0;
            if (nd.Type == NodeType.Junction && opt.PileFor(nd.Cell) == PileArt.Strips)
            {
                StripPose sp = PoseStrip(g, v, opt.Seed);
                V2 ad = ArmDir(g, e, atA);
                var arm = new Cell((int)ad.X, (int)ad.Z);
                int socket = sp.SocketFor(arm);
                if (socket < 0)
                {
                    // the strip's own lead: into the nub at its end, no plug
                    target = sp.LeadTip + sp.Side * (lat * 0.015);
                    arrive = -sp.Along;
                    straight = 0.1;
                }
                else
                {
                    // a bundle shares one plug, as a device lead does: its strands close up to the socket
                    target = sp.Tip(socket);
                    arrive = -sp.Side;
                    straight = 0.22;
                    roomy = 1.2;
                    swing = arm == sp.BackArm ? 1 : arm == sp.FreeArm ? 2 : 0;
                }
            }
            else if (nd.Type == NodeType.Junction)
            {
                V2 a = ArmDir(g, e, atA);
                // the bigger round-5 box: tuck out along the arm, but never past the far node (or the middle, when the far node is a junction that tucks too); never shorter than before
                CordNode far = g.Nodes[atA ? e.B : e.A];
                double fd = V2.Dist(nd.Pos, far.Pos), limit = far.Type == NodeType.Junction && !far.IsBlob ? 0.46 * fd : fd - 0.05;
                double tuck = Math.Min(ArmTuck * JunctionScale, Math.Max(ArmTuck, limit));
                target = nd.Pos + a * tuck + Side(a) * (lat * 0.03);
                arrive = -a;
            }
            else if (nd.IsMachine && nd.Machine != null)
            {
                target = atA ? e.PA : e.PB;
                // a standing lamp takes its cord on the side the cord comes from: its plug point is the top of its cell, so a cord laid in from below
                // or beside ran past the lamp and hooked back over it (blind judge p15a, every look: "the lamp lead overshoots and hairpins back"). The run
                // under the lamp's art to its centre hides which side it went in by
                if (nd.Machine.Kind == MachineKind.Lamp && nd.Machine.W == 1 && nd.Machine.H == 1) target = LampEntry(nd.Machine, BackAlong(P, !atA, LampLook));
                arrive = IntoMachine(nd.Machine, target);
                if (g.Slides(nd.Machine)) arrive = CordGraph.SlideArrive(nd.Machine, target, arrive);
            }
            else if (nd.IsStub && nd.Into.Len > 0.5)
            {
                // a junction in the same cell (the run ends one cell into the wall right at a T): line
                // the stub up with the junction's arm, which starts on the junction's own (jittered) point
                CordNode other = g.Nodes[atA ? e.B : e.A];
                V2 basePos = nd.Pos;
                if (other.Type == NodeType.Junction && other.Cell == nd.Cell)
                {
                    V2 d = nd.Pos - other.Pos;
                    basePos = other.Pos + nd.Into * (d.X * nd.Into.X + d.Z * nd.Into.Z);
                }
                target = basePos + Side(nd.Into) * (lat * 0.03);
                arrive = nd.Into;
            }
            else if (nd.Type == NodeType.Tangle && nd.Cells != null)
            {
                // round 5: the cord runs on into the pile and plugs into one of its connectors' ports, along that port
                List<PilePort> ports = PortsOf(PileConnectors(w, nd, opt, true));
                if (ports.Count == 0) return false;
                PilePort q = EntryPort(ports, atA ? e.PA : e.PB);
                target = q.Tip + Side(q.Out) * (lat * 0.02);
                arrive = -q.Out;
                straight = 0.22;
            }
            else if (nd.Type == NodeType.Terminal && !nd.Seam)
            {
                V2 o = new V2(nd.Out.X, nd.Out.Z).Norm();
                target = nd.Pos + Side(o) * (lat * 0.03);
                arrive = o;
                straight = 0.6;
            }
            else return false;
            return true;
        }

        private static List<V2> AttachEnd(CordWorld w, CordGraph g, CordEdge e, bool atA, List<V2> P, int i, int n, BuildOptions opt)
        {
            VId v = atA ? e.A : e.B;
            CordNode nd = g.Nodes[v];
            if (!EndPose(w, g, e, atA, P, i, n, opt, out V2 target, out V2 arrive, out double straight, out double roomy, out int swing)) return P;
            if (swing != 0)
            {
                StripPose sp = PoseStrip(g, v, opt.Seed);
                V2 onSide = target + sp.Side * StripSwing;
                // from behind: first out past the free end, so the cord comes round the strip instead of under it
                if (swing == 1) P = SwingIn(w, P, !atA, sp.Centre, sp.At(StripHeads[0], 0) - sp.Along * StripWrap, onSide - sp.Along * 0.15);
                else P = SwingIn(w, P, !atA, sp.Centre, onSide - sp.Along * 0.5 + sp.Side * 0.25, onSide - sp.Along * 0.1 + sp.Side * 0.2);
            }
            // a cut end keeps the old approach: its live end runs straight out of the conduit end and its dead end curls limp (break_live_and_dead_ends_differ)
            CordNode farEnd = g.Nodes[atA ? e.B : e.A];
            if (opt.Lay.FairBends && !(nd.Type == NodeType.Terminal && !nd.Seam) && !(farEnd.Type == NodeType.Terminal && !farEnd.Seam))
            {
                Func<V2, bool> clear = ArriveClear(w, P, target, nd.IsMachine ? nd.Machine : null);
                CordNode farNd = g.Nodes[atA ? e.B : e.A];
                double keepFar = farNd.Type == NodeType.Terminal && !farNd.Seam ? 1.2 : 0.5;
                List<V2> round = CordShape.ArriveRound(P, !atA, target, arrive, straight, clear, out double turned, keepFar);
                // a one-cell machine takes its plug on whichever side the cord comes round to with the least turn (the side that faces vanilla's hookup cell
                // made a cord laid in from beside or below run past a standing lamp and hook back over its top: blind judge p15a, every look)
                MachineInfo m = nd.IsMachine ? nd.Machine : null;
                if (m != null && m.W == 1 && m.H == 1 && !m.HasHome)
                    foreach (Cell side in new[] { new Cell(m.X0, m.Z0 + 1), new Cell(m.X0 + 1, m.Z0), new Cell(m.X0, m.Z0 - 1), new Cell(m.X0 - 1, m.Z0) })
                    {
                        V2 t2 = m.Kind == MachineKind.Lamp ? LampEntry(m, side.Centre) : CordGraph.PlugPoint(m, side, g.Slides(m));
                        if (V2.Dist(t2, target) < 0.05 || !w.IsWalkable(t2.Floor)) continue;
                        V2 a2 = IntoMachine(m, t2);
                        if (g.Slides(m)) a2 = CordGraph.SlideArrive(m, t2, a2);
                        List<V2> r2 = CordShape.ArriveRound(P, !atA, t2, a2, straight, ArriveClear(w, P, t2, m), out double turned2, keepFar);
                        if (r2 != null && turned2 < turned - SideSwitchGain) { round = r2; turned = turned2; }
                    }
                if (round != null) return round;
            }
            return CordLayer.Approach(w, P, !atA, target, arrive, straight, roomy);
        }

        /// <summary>A one-cell machine moves its plug to another side only for this much less turn (radians): where the hookup's own side comes round well, it stays.</summary>
        private const double SideSwitchGain = 0.35;

        /// <summary>Where a cord coming round to its fitting may lie: walkable ground clear of walls, not in under furniture, another machine or a door it did not already go through.
        /// The last 0.3 cell before the fitting is the fitting's own ground (a wall plate sits at the face, a plug just off the art).</summary>
        private static Func<V2, bool> ArriveClear(CordWorld w, List<V2> P, V2 target, MachineInfo own)
        {
            var doors = new HashSet<Cell>();
            foreach (V2 q in P) if (w.IsDoor(q.Floor)) doors.Add(q.Floor);
            // the other machines' cells within reach of this end (an end comes round inside three cells of its fitting)
            var machine = new HashSet<Cell>();
            foreach (MachineInfo m in w.Machines)
            {
                // by footprint, not reference: a graph reduced from an earlier copy of the world holds that copy's machine infos (the sliced lay laid a lamp's cord round its own cell)
                if ((own != null && m.X0 == own.X0 && m.Z0 == own.Z0 && m.W == own.W && m.H == own.H) || m.X0 > target.X + 4 || m.X0 + m.W < target.X - 4 || m.Z0 > target.Z + 4 || m.Z0 + m.H < target.Z - 4) continue;
                for (int x = m.X0; x < m.X0 + m.W; x++)
                    for (int z = m.Z0; z < m.Z0 + m.H; z++) machine.Add(new Cell(x, z));
            }
            return q =>
            {
                Cell c = q.Floor;
                if (!w.IsWalkable(c)) return own != null && own.Contains(c) && V2.Dist(q, target) < 0.3;
                if (V2.Dist(q, target) < 0.3) return true;
                if (w.IsFurniture(c) || (w.IsDoor(c) && !doors.Contains(c)) || machine.Contains(c)) return false;
                return w.Clearance(q) >= LayParams.RC;
            };
        }

        /// <summary>Bend a cord that does not arrive from the sockets' side out through the given points, so it comes round to its
        /// socket in a loose curve instead of a hairpin under the plug. Unchanged if that ground is not open.</summary>
        private static List<V2> SwingIn(CordWorld w, List<V2> P, bool atEnd, V2 centre, params V2[] via)
        {
            if (P.Count < 4 || via.Any(q => !w.IsWalkable(q.Floor))) return P;
            var Q = new List<V2>(P);
            if (!atEnd) Q.Reverse();
            int j = Q.Count - 1;
            while (j > 1 && V2.Dist(Q[j], centre) < 0.85) j--;
            if (j < 1) return P;
            var stops = new List<V2> { Q[j - 1], Q[j] };
            stops.AddRange(via);
            List<V2> bend = Geo.Resample(Geo.Catmull(stops, 10), 0.05);
            if (bend.Any(q => !w.IsWalkable(q.Floor))) return P;
            var round = new List<V2>(Q.GetRange(0, j + 1));
            int from = bend.FindIndex(q => V2.Dist(q, Q[j]) < 0.03);
            round.AddRange(from < 0 ? bend : bend.GetRange(from + 1, bend.Count - from - 1));
            if (!atEnd) round.Reverse();
            return round;
        }


        /// <summary>How far back along a cord (cells) <see cref="LampEntry"/> looks to see which side of a lamp it comes from.</summary>
        public const double LampLook = 1.1;

        /// <summary>The point just outside a one-cell lamp on the side facing <paramref name="from"/>: the top edge, as before, for a cord from above.</summary>
        internal static V2 LampEntry(MachineInfo m, V2 from)
        {
            double cx = m.X0 + 0.5, cz = m.Z0 + 0.5, dx = from.X - cx, dz = from.Z - cz;
            if (dz >= Math.Abs(dx) * 0.6) return new V2(cx, m.Z0 + 1.02);
            if (Math.Abs(dx) >= Math.Abs(dz)) return new V2(dx > 0 ? m.X0 + 1.08 : m.X0 - 0.08, cz - 0.1);
            return new V2(cx, m.Z0 - 0.08);
        }

        /// <summary>The point <paramref name="d"/> cells of arc back from one end of a laid cord (the far end if it is shorter).</summary>
        private static V2 BackAlong(List<V2> P, bool atEnd, double d)
        {
            double run = 0;
            int n = P.Count;
            for (int k = 1; k < n; k++)
            {
                V2 a = atEnd ? P[n - k] : P[k - 1], b = atEnd ? P[n - k - 1] : P[k];
                run += V2.Dist(a, b);
                if (run >= d) return b;
            }
            return atEnd ? P[0] : P[n - 1];
        }

        /// <summary>The art inset (cells) on the footprint side a cord enters through.</summary>
        internal static double ArtInset(MachineInfo m, V2 into)
        {
            if (into.X > 0.5) return m.InsetW;
            if (into.X < -0.5) return m.InsetE;
            if (into.Z > 0.5) return m.InsetS;
            return m.InsetN;
        }

        /// <summary>Owner round 2 (2026-10-04, station 4: "connectors not properly meeting the lightbulbs ... just go to the
        /// centroid of a building and be beneath them on the drawstack"): every cord into a machine runs on under its art to
        /// the footprint CENTROID, the last <see cref="CentroidApproach"/> cell straight along the way in (so the plug sits
        /// square at the end). The cord is printed at Conduits altitude, below every building, so the art hides the run and
        /// no art inset or misalignment can show. Points are inside the machine's own footprint by design.</summary>
        public const double CentroidApproach = 0.2;

        internal static V2 Centroid(MachineInfo m) => new V2(m.X0 + m.W / 2.0, m.Z0 + m.H / 2.0);

        /// <summary>Where a machine's cord ends: its wall cell's centre for a wall-mounted device (round 4), else the centroid.</summary>
        internal static V2 Home(MachineInfo m) => m.HasHome ? new V2(m.HomeX + 0.5, m.HomeZ + 0.5) : Centroid(m);

        /// <summary>How far a sliding cord (BuildOptions.SlideUnder) keeps its diagonal past the plug point before it turns for
        /// the centroid: far enough that it crosses the footprint edge on the diagonal, clear of the side's port midpoints.</summary>
        public const double SlideCarry = 0.3;

        private static List<V2> IntoArt(List<V2> P, bool atStart, MachineInfo m, bool slide = false)
        {
            if (P.Count < 2) return P;
            V2 tip = atStart ? P[0] : P[P.Count - 1];
            V2 into = IntoMachine(m, tip);
            V2 c = Centroid(m), pre = c - into * CentroidApproach;
            var ext = new List<V2>();
            if (slide)
            {
                // carry the diagonal arrival on under the edge, then turn for the centroid
                V2 dia = CordGraph.SlideArrive(m, tip, into), mid = tip + dia * SlideCarry;
                int k0 = Math.Max(1, (int)Math.Ceiling(SlideCarry / 0.05));
                for (int i = 1; i <= k0; i++) ext.Add(tip + (mid - tip) * (i / (double)k0));
                tip = mid;
            }
            double d1 = V2.Dist(tip, pre);
            int k1 = Math.Max(1, (int)Math.Ceiling(d1 / 0.05));
            for (int i = 1; i <= k1; i++) ext.Add(tip + (pre - tip) * (i / (double)k1));
            for (double d = 0.05; d < CentroidApproach - 0.02; d += 0.05) ext.Add(pre + into * d);
            ext.Add(c);
            if (m.HasHome)
            {
                // on from the device's own cell straight into its wall, ending under the wall's centre
                V2 h = Home(m);
                double d2 = V2.Dist(c, h);
                int k2 = Math.Max(1, (int)Math.Ceiling(d2 / 0.05));
                for (int i = 1; i <= k2; i++) ext.Add(c + (h - c) * (i / (double)k2));
            }
            var o = new List<V2>(P);
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); }
            else o.AddRange(ext);
            return o;
        }

        public const double PastFaceDepth = 0.03;

        private static List<V2> PastFace(List<V2> P, bool atStart, CordNode nd)
        {
            if (P.Count < 2 || !(nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock) || nd.Into.Len < 0.5) return P;
            V2 tip = atStart ? P[0] : P[P.Count - 1];
            V2 to = nd.Face + nd.Into * PastFaceDepth;
            double along = (to.X - tip.X) * nd.Into.X + (to.Z - tip.Z) * nd.Into.Z;
            if (along <= 0.005) return P;
            var o = new List<V2>(P);
            int k = Math.Max(1, (int)Math.Ceiling(along / 0.04));
            var ext = new List<V2>();
            for (int i = 1; i <= k; i++) ext.Add(tip + nd.Into * (along * i / k));
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); } else o.AddRange(ext);
            return o;
        }

        /// <summary>Points from one end of P whose arc length stays within len (at least 3), never more than half the strand.</summary>
        internal static int TailCount(List<V2> P, bool atStart, double len)
        {
            int n = P.Count;
            if (n < 6) return 0;
            double acc = 0;
            int c = 1;
            for (int k = 1; k < n / 2; k++)
            {
                int i = atStart ? k : n - 1 - k, j = atStart ? k - 1 : n - k;
                acc += V2.Dist(P[i], P[j]);
                if (acc > len) break;
                c++;
            }
            return c >= 3 ? c : 0;
        }

        private static double EndAngle(List<V2> P, bool atStart)
        {
            V2 a, b;
            if (P.Count < 2) return 0;
            if (atStart) { a = P[Math.Min(3, P.Count - 1)]; b = P[0]; }
            else { a = P[Math.Max(0, P.Count - 4)]; b = P[P.Count - 1]; }
            V2 d = b - a;
            return Math.Atan2(d.Z, d.X);
        }

        private static void EndDecor(CordWorld w, CordGraph g, CordEdge e, VId v, CordNode nd, LaidPiece piece, bool atStart, BuildOptions opt,
                                     Func<Cell, bool> isLive)
        {
            if (piece.Strands.Count == 0) return;
            List<V2> first = (piece.Strands.FirstOrDefault(s => !(atStart ? s.DiveA : s.DiveB)) ?? piece.Strands[0]).Pts;
            V2 tip = atStart ? first[0] : first[first.Count - 1];
            if (nd.IsMachine)
            {
                // one plug per end, at the footprint centroid where every strand converges (round 2), its head pointing
                // INTO the machine along the cord's last straight run; drawn under the building like the cord
                V2 a = atStart ? first[Math.Min(first.Count - 1, 1)] : first[Math.Max(0, first.Count - 2)];
                V2 into = Snap4(tip - a);
                piece.Decals.Add(new CordDecal(DecalKind.Plug, tip - into * (PlugScale * 0.25), Math.Atan2(into.Z, into.X), PlugScale));
            }
            else if (nd.Type == NodeType.Junction && opt.PileFor(nd.Cell) == PileArt.Strips)
            {
                // a cord into a junction strip plugs into its socket; the strip's own lead wears no plug
                StripPose sp = PoseStrip(g, v, opt.Seed);
                V2 ad = ArmDir(g, e, atStart);
                int socket = sp.SocketFor(new Cell((int)ad.X, (int)ad.Z));
                // square onto the socket whatever the bundle's last point did: one plug, on the art's own plug
                if (socket >= 0) piece.Decals.Add(new CordDecal(DecalKind.Plug, sp.Tip(socket), Math.Atan2(-sp.Side.Z, -sp.Side.X), PilePlugScale));
            }
            else if (nd.Type == NodeType.Tangle && opt.PileFor(nd.Cell) == PileArt.Strips)
            {
                // round 5: a cord entering a strip pile plugs into its socket like the pile's own cables
                foreach (CordStrand s in piece.Strands)
                {
                    if (atStart ? s.DiveA : s.DiveB) continue;
                    V2 t = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    V2 a = atStart ? s.Pts[Math.Min(s.Pts.Count - 1, 1)] : s.Pts[Math.Max(0, s.Pts.Count - 2)];
                    V2 into = (t - a).Norm();
                    piece.Decals.Add(new CordDecal(DecalKind.Plug, t, Math.Atan2(into.Z, into.X), PilePlugScale));
                }
            }
            else if (nd.Type == NodeType.Terminal && !nd.Seam)      // A3: a ring's seam is not an end
            {
                bool liveEnd = isLive(nd.Cell);
                foreach (CordStrand s in piece.Strands)
                {
                    if (atStart ? s.DiveA : s.DiveB) continue;
                    V2 t = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    var fd = new CordDecal(liveEnd ? DecalKind.FrayLive : DecalKind.FrayDead, t, EndAngle(s.Pts, atStart), 0.5);
                    if (liveEnd && !s.OverFace)
                    {
                        int cnt = TailCount(s.Pts, atStart, CordMotion.WhipLen);
                        if (atStart) s.WhipA = cnt; else s.WhipB = cnt;
                        fd.OnWhip = cnt > 0;
                    }
                    piece.Decals.Add(fd);
                }
                piece.Ends.Add(new CordEnd { Tip = tip, Dir = new V2(nd.Out.X, nd.Out.Z), NetCell = nd.Cell, Wall = false });
            }
            else if (nd.IsStub)
            {
                double ang = Math.Atan2(nd.Into.Z, nd.Into.X);
                V2 hole = nd.Face + nd.Into * 0.04;
                // round 4 (owner 2026-10-04: "They should look mounted ON the wall"): the plate / hole is drawn INSIDE the wall
                // cell, on the face it belongs to, cropped to the plate (WallMount): the visible south face shows it whole in
                // its band; an edge-on side face or the hidden north face shows a thin strip. Nothing lands on the open floor.
                if (nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock)
                {
                    CordDecal plate = WallMount.EntryDecal(nd.Type == NodeType.StubWall ? DecalKind.StubWall : DecalKind.StubRock, nd.Face, nd.Into);
                    piece.Decals.Add(plate);
                    hole = WallMount.Socket(plate);
                }
                else if (nd.Type == NodeType.StubDevice && opt.PileFor(nd.Cell) == PileArt.Strips)
                {
                    // the strip's LEDs read the net (phase 1b B6): lit when live, dark when not
                    piece.Decals.Add(new CordDecal(isLive(nd.Cell) ? DecalKind.PowerStrip : DecalKind.PowerStripDark, nd.Face - nd.Into * 0.2, ang + Math.PI / 2, 0.8));
                    piece.LiveKeys.Add(nd.Cell);
                }
                else if (nd.Type == NodeType.StubDevice)
                    // no strips outside the modern look (B1/B15): the cord ends in a small junction box, an arm along it
                    piece.Decals.Add(new CordDecal(DecalKind.JunctionTin, nd.Face - nd.Into * 0.2, ang, 0.6));
                if (nd.WallTerminal)
                {
                    var tail = WallMount.LooseWire(hole, nd.Face, nd.Into);
                    var sw = new double[tail.Count];
                    for (int k = 0; k < sw.Length; k++) sw[k] = Math.Pow(k / (double)(sw.Length - 1), 1.3);
                    piece.Strands.Add(new CordStrand { Pts = tail, OverFace = true, S0 = 0.3, Lifted = true, SwayW = sw });
                    V2 tt = tail[tail.Count - 1];
                    piece.Decals.Add(new CordDecal(isLive(nd.Cell) ? DecalKind.FrayLive : DecalKind.FrayDead, tt, -Math.PI / 2, 0.5) { OnSwayTail = true });
                    piece.Ends.Add(new CordEnd { Tip = tt, Dir = new V2(0, -1), NetCell = nd.Cell, Wall = true });
                }
            }
        }

        /// <summary>Lay a strand's slack; if it comes out running back alongside itself (<see cref="CordShape.Doubled"/>), so that one cord reads as three, or goes under a door its route
        /// does not run through (<see cref="CordShape.DoorStrays"/>), so that it reads as more cables out of that doorway, or under a machine or furniture it does not need to cross, lay it again on the next draw with a little less slack, and keep
        /// the first that reads as one cord, or the least wrong, a stray door counting first. Try 0 is the old draw, so a cord that was fine has not moved. <paramref name="section"/> is a diving cord's surface section.</summary>
        private static List<V2> SprawlOnce(CordWorld w, List<V2> P, List<V2> plan, LayParams prm, double slack, double maxExtra, ulong seed, string key, int i, int n, int? section, out SettleStats settle)
        {
            List<V2> best = null;
            SettleStats bestSettle = null;
            int bestStrays = int.MaxValue;
            double bestD = double.MaxValue;
            for (int t = 0; t < SlackRetries; t++)
            {
                double k = 1 - 0.1 * t;
                CordRng bundle = section.HasValue ? (t == 0 ? CordRng.Of(seed, "bundle", key, section.Value) : CordRng.Of(seed, "bundle", key, section.Value, t))
                    : (t == 0 ? CordRng.Of(seed, "bundle", key) : CordRng.Of(seed, "bundle", key, t));
                CordRng strand = section.HasValue ? (t == 0 ? CordRng.Of(seed, "strand", key, i, section.Value) : CordRng.Of(seed, "strand", key, i, section.Value, t))
                    : (t == 0 ? CordRng.Of(seed, "strand", key, i) : CordRng.Of(seed, "strand", key, i, t));
                List<V2> Q = CordLayer.Sprawl(w, P, prm, slack * k, maxExtra * k, bundle, strand, n, out SettleStats st);
                double d = CordShape.Doubled(Q);
                int rings = CordShape.RingReturns(w, Q, out int atDoors), hard = CordShape.DoorStrays(w, Q, plan) + CordShape.MachineStrays(w, Q, plan) + CordShape.FurnitureStrays(w, Q, plan) + atDoors, strays = hard + rings - atDoors;
                if (strays < bestStrays || (strays == bestStrays && d < bestD)) { best = Q; bestStrays = strays; bestD = d; bestSettle = st; }
                if (strays == 0 && d <= CordShape.DoubledMax) break;
                // on a long cord a coil at its own end is worth a few more draws, not six: each is a settle, and a long one is what a frame's budget feels. A coil at a door gets all six
                if (t + 1 >= SoftRetries && hard == 0 && d <= CordShape.DoubledMax && Q.Count > SoftRetryPoints) break;
            }
            settle = bestSettle;
            return best;
        }

        private const int SlackRetries = 6, SoftRetries = 3, SoftRetryPoints = 500;

        /// <summary>How far from its ends a strand's corners are left alone: a dead end's limp curl is a corner on purpose, and a live end sticks straight out.</summary>
        /// <summary>How much of a strand's end <see cref="CordShape.Fair"/> leaves as laid: a cut end's whole straight run or limp curl, else the fitting's own straight bit.</summary>
        private static double FairPin(CordNode nd, Func<Cell, bool> isLive) =>
            nd.Type == NodeType.Terminal && !nd.Seam ? (isLive(nd.Cell) ? 0.6 : 1.0) : 0.2;

        private static double LimpSkip(CordNode na, CordNode nb, Func<Cell, bool> isLive) =>
            (na.Type == NodeType.Terminal && !na.Seam) || (nb.Type == NodeType.Terminal && !nb.Seam) ? 1.0 : 0.25;

        /// <summary>A place a pile cable plugs in: the point its end lands on and the direction it leaves in.</summary>
        public struct PilePort
        {
            internal V2 Tip, Out;
            public int Connector;
        }

        // PowerStrip art (64x32, drawn 0.9 x 0.45): four sockets along its long axis. PROVISIONAL, read off the PNG.
        public static readonly double[] StripSockets = { -0.22, -0.08, 0.06, 0.20 };
        public const double StripScale = 0.9, PilePlugScale = 0.42;

        /// <summary>The ports of every connector decal in a pile (junction arms, strip sockets), in decal order.</summary>
        public static List<PilePort> PortsOf(List<CordDecal> ds)
        {
            var ports = new List<PilePort>();
            for (int i = 0; i < ds.Count; i++)
            {
                CordDecal d = ds[i];
                if (d.Kind == DecalKind.JunctionTin || d.Kind == DecalKind.JunctionTape)
                {
                    bool tape = d.Kind == DecalKind.JunctionTape;
                    V2 jp = d.Pos + CordAudit.Rot(new V2(0, tape ? TapeAnchorZ * d.Scale : 0), d.Angle);
                    double[] arms = tape ? new[] { 0, Math.PI, -Math.PI / 2 } : new[] { 0, Math.PI / 2, Math.PI, -Math.PI / 2 };
                    foreach (double a in arms)
                    {
                        V2 o = CordAudit.Dir(a + d.Angle);
                        ports.Add(new PilePort { Tip = jp + o * (ArmTuck * d.Scale), Out = o, Connector = i });
                    }
                }
                else if (d.Kind == DecalKind.PowerStrip || d.Kind == DecalKind.PowerStripDark)
                {
                    V2 along = CordAudit.Dir(d.Angle), side = along.Perp;
                    for (int k = 0; k < StripSockets.Length; k++)
                    {
                        V2 o = k % 2 == 0 ? side : -side;
                        // the plug's head face sits on the socket; the cable leaves the plug's tail
                        V2 socket = d.Pos + along * (StripSockets[k] * d.Scale) + o * (0.1 * d.Scale);
                        ports.Add(new PilePort { Tip = socket + o * (0.46 * PilePlugScale), Out = o, Connector = i });
                    }
                }
            }
            return ports;
        }

        /// <summary>Pile connector box scale (round 5: thicker boxes over thinner wires) and the jitter that breaks the grid
        /// (owner 2026-10-04: "an unwelcome grid-like nature to the joining boxes sitting on the pile. Should be more randomly
        /// aligned"): each box is moved up to <see cref="PileJitter"/> off its cell centre, turned to any angle and scaled
        /// within <see cref="PileScaleLo"/>..<see cref="PileScaleHi"/> of <see cref="PileJunctionScale"/>.</summary>
        public const double PileJunctionScale = 1.05, PileJitter = 0.32, PileScaleLo = 0.82, PileScaleHi = 1.12;

        /// <summary>The most cables a pile draws (each joins two connector ports).</summary>
        public const int MaxPileCables = 24;

        /// <summary>The connectors (junction boxes or strips) of a pile, deterministic from the seed and the pile's cells. Shared
        /// by <see cref="TanglePiece"/> and the cords that enter the pile (they plug into one of these ports, round 5).</summary>

        internal static List<CordDecal> PileConnectors(CordWorld w, CordNode nd, BuildOptions opt, bool lit)
        {
            List<Cell> comp = nd.Cells;
            bool strips = opt.PileFor(nd.Cell) == PileArt.Strips;
            CordRng rc = CordRng.Of(opt.Seed, "pilecon", nd.Cell.X, nd.Cell.Z);
            var cells = new List<Cell>(comp);
            for (int i = cells.Count - 1; i > 0; i--) { int j = rc.Int(0, i); Cell t = cells[i]; cells[i] = cells[j]; cells[j] = t; }
            // a strip every four cells: at one in seven the Modern heap was a thin net of a few cords between four strips beside the junction looks' dense
            // boxes (dense_grid_reads_as_tangle; the owner: "a huge tangle of nasty wires and power strips all swirled together terribly")
            int want = strips ? Math.Max(1, 1 + comp.Count / 4) : Math.Max(3, 1 + comp.Count / 2);
            var cons = new List<CordDecal>();
            int portsSoFar = 0;
            foreach (Cell c in cells)
            {
                if (cons.Count >= want) break;
                // irregular, never a grid: off-centre, any angle, a little bigger or smaller (round 5)
                V2 at = c.Centre + new V2(rc.Range(-PileJitter, PileJitter), rc.Range(-PileJitter, PileJitter));
                double ang = rc.Range(0, 2 * Math.PI), sc = rc.Range(PileScaleLo, PileScaleHi);
                CordDecal d;
                if (strips) d = new CordDecal(lit ? DecalKind.PowerStrip : DecalKind.PowerStripDark, at, ang, StripScale * sc);
                else d = new CordDecal(rc.Chance(0.5) ? DecalKind.JunctionTin : DecalKind.JunctionTape, at, ang, PileJunctionScale * sc);
                var one = new List<CordDecal> { d };
                List<PilePort> mine = PortsOf(one);
                if (mine.Any(q => !w.IsWalkable(q.Tip.Floor))) continue;
                // keep boxes apart: a box whose centre lands within 0.45 of another reads as a stack, not a scatter
                if (cons.Any(o => V2.Dist(o.Pos, at) < 0.45)) continue;
                // GSS pre-release A2: never more ports than MaxPileCables cables can fill (two ports each), so a big pile
                // has no idle junction boxes; the first connectors always stand (a small pile is unchanged)
                if (cons.Count >= 2 && portsSoFar + mine.Count > 2 * MaxPileCables) break;
                portsSoFar += mine.Count;
                cons.Add(d);
            }
            return cons;
        }

        /// <summary>The pile port a cord ENTERING the pile plugs into (round 5, station 1: "the cable entering the mass does not
        /// join with the rest"): the port whose lead-out point (tip + out x 0.22) is nearest the cord's arrival point.</summary>
        internal static PilePort EntryPort(List<PilePort> ports, V2 from)
        {
            PilePort best = ports[0];
            double bd = double.MaxValue;
            foreach (PilePort q in ports)
            {
                double d = V2.Dist(q.Tip + q.Out * 0.22, from);
                if (d < bd) { bd = d; best = q; }
            }
            return best;
        }

        /// <summary>
        /// A strip pile's cable from port <paramref name="pa"/> to <paramref name="pb"/> as a swirled cord: out of the socket, then its heading bends by
        /// curvature waves tight enough to curl (a third to two thirds of a cell across) and drifts toward the far socket, held home over its last third,
        /// 2.2-3x the distance between them; the whole is turned and scaled about its start to end exactly at the far socket's lead. Every point stays
        /// on the heap's own walkable cells. Null when ten draws all leave the heap: the caller keeps its spline.
        /// </summary>
        private static List<V2> Swirl(CordWorld w, HashSet<Cell> comp, PilePort pa, PilePort pb, CordRng r)
        {
            V2 s = pa.Tip + pa.Out * 0.22, e = pb.Tip + pb.Out * 0.22;
            double dist = V2.Dist(s, e);
            if (dist < 0.3) return null;
            const double ds = 0.05;
            double baseA = Math.Atan2(e.Z - s.Z, e.X - s.X);
            for (int attempt = 0; attempt < 10; attempt++)
            {
                double A = r.Range(1.6, 2.6) * r.Sign(), l1 = r.Range(1.4, 2.4), l2 = r.Range(2.8, 4.6), p1 = r.Range(0, 6.283), p2 = r.Range(0, 6.283);
                double want = Math.Max(dist * r.Range(2.2, 3.0), dist + 2.5);
                double h = Math.Atan2(pa.Out.Z, pa.Out.X), x = s.X, z = s.Z, L = 0;
                var pts = new List<V2> { s };
                while (L < want)
                {
                    double u = L / want, err = Math.Atan2(e.Z - z, e.X - x) - h;
                    while (err > Math.PI) err -= 2 * Math.PI;
                    while (err < -Math.PI) err += 2 * Math.PI;
                    double home = u < 0.65 ? 0.25 : 0.25 + 9 * (u - 0.65);
                    h += (A * (0.65 * Math.Sin(6.283 * L / l1 + p1) + 0.35 * Math.Sin(6.283 * L / l2 + p2)) * (1 - 0.7 * Math.Max(0, u - 0.65) / 0.35) + home * err) * ds;
                    x += ds * Math.Cos(h); z += ds * Math.Sin(h); L += ds;
                    pts.Add(new V2(x, z));
                }
                double ex = x - s.X, ez = z - s.Z, el = Math.Sqrt(ex * ex + ez * ez);
                if (el < 1e-6) continue;
                double sc = dist / el;
                if (sc < 0.7 || sc > 1.45) continue;
                double rot = baseA - Math.Atan2(ez, ex), c = Math.Cos(rot), sn = Math.Sin(rot);
                var o = new List<V2>(pts.Count + 2) { pa.Tip };
                bool ok = true;
                for (int i = 0; i < pts.Count && ok; i++)
                {
                    double px = pts[i].X - s.X, pz = pts[i].Z - s.Z;
                    V2 q = i == pts.Count - 1 ? e : new V2(s.X + sc * (px * c - pz * sn), s.Z + sc * (px * sn + pz * c));
                    ok = comp.Contains(q.Floor) && w.IsWalkable(q.Floor);
                    o.Add(q);
                }
                if (!ok) continue;
                o.Add(pb.Tip);
                return Geo.Resample(o, 0.05);
            }
            return null;
        }

        /// <summary>The tightest a heap's cable turns outside a whole coil (cells). Over one cell of cord it then turns at most 80 degrees, never the sharp bend never_taut_straight_cord
        /// counts; a spline through random points in the heap folded back on itself wherever two came one behind the other (pass 17: every fold of the self-test's 123 strands was a heap's).</summary>
        public const double HeapTurnR = 0.72;
        /// <summary>A heap cable's coils: whole loops, one way round, this wide (cells). The north star's own loops; a cable crammed in a heap coils, it does not fold.</summary>
        public const double HeapCoilLo = 0.48, HeapCoilHi = 0.62;
        /// <summary>How far a heap reaches from each of its conduit cells' middles (cells), drawn per cell: their union is a lumpy round outline, not the block's square.</summary>
        public const double HeapReachLo = 0.95, HeapReachHi = 1.4;
        /// <summary>The disc round a heap port's lead that counts as the heap's own ground (radius, cells): room for a cable to come out of an outward arm and round.</summary>
        public const double PortBulge = 0.8;
        /// <summary>Heap cables laid by the old spline because no walk came round on the heap's ground (the self-test reads it).</summary>
        internal static int HeapWalkMisses, HeapWalkOff, HeapWalkLong;
        /// <summary>Self-test hook: each walk attempt's points, its stops, whether it came round, and the heap's ground test.</summary>
        internal static Action<List<V2>, List<V2>, bool, Func<V2, bool>> HeapWalkTrace;
        internal static Action<string> HeapWalkWhy;

        /// <summary>Where a heap's cable may lie: on the heap's ground cells (<see cref="PileGround"/>) and within its own reach of one of its conduit cells, or round a port's lead.
        /// Sampled once on a 0.1-cell grid over the heap's box: the walk asks it a few hundred times a step.</summary>
        internal static Func<V2, bool> HeapGround(HashSet<Cell> ground, List<Cell> comp, ulong seed, List<PilePort> ports)
        {
            var reach = new Dictionary<Cell, double>();
            foreach (Cell c in comp) reach[c] = CordRng.Of(seed, "heapreach", c.X, c.Z).Range(HeapReachLo, HeapReachHi);
            // round every port's lead too: a box at the heap's edge with an arm pointing out sends its cable out and round, a bulge, where it could not turn back inside
            var bulge = ports.Select(q => q.Tip + q.Out * (0.22 + PortBulge)).ToList();
            bool At(V2 q)
            {
                if (!ground.Contains(q.Floor)) return false;
                foreach (V2 b in bulge) if (V2.Dist(q, b) <= PortBulge + 0.05) return true;
                int fx = (int)Math.Floor(q.X), fz = (int)Math.Floor(q.Z);
                for (int dx = -2; dx <= 2; dx++)
                    for (int dz = -2; dz <= 2; dz++)
                        if (reach.TryGetValue(new Cell(fx + dx, fz + dz), out double rr) && V2.Dist(q, new Cell(fx + dx, fz + dz).Centre) <= rr) return true;
                return false;
            }
            const int per = 10;   // grid steps a cell
            int x0 = ground.Min(c => c.X), z0 = ground.Min(c => c.Z), nx = (ground.Max(c => c.X) - x0 + 1) * per, nz = (ground.Max(c => c.Z) - z0 + 1) * per;
            var grid = new bool[nx * nz];
            for (int i = 0; i < nx; i++)
                for (int j = 0; j < nz; j++) grid[i * nz + j] = At(new V2(x0 + (i + 0.5) / per, z0 + (j + 0.5) / per));
            return q =>
            {
                int i = (int)Math.Floor((q.X - x0) * per), j = (int)Math.Floor((q.Z - z0) * per);
                return i >= 0 && j >= 0 && i < nx && j < nz && grid[i * nz + j];
            };
        }

        private static double Wrap(double a)
        {
            while (a > Math.PI) a -= 2 * Math.PI;
            while (a < -Math.PI) a += 2 * Math.PI;
            return a;
        }

        /// <summary>The tightest a heap cable turns right out of its plug (cells), over at most <see cref="HeapPlugReach"/> of cord: a socket's forced bend.</summary>
        private const double HeapPlugR = 0.3, HeapPlugReach = 0.45;

        /// <summary>Whether a heap cable can turn here: the heap's ground all round within 0.4 cell.</summary>
        private static bool HeapRoomy(Func<V2, bool> onGround, V2 q)
        {
            if (!onGround(q)) return false;
            for (int a = 0; a < 8; a++) if (!onGround(q + CordAudit.Dir(a * Math.PI / 4) * 0.4)) return false;
            return true;
        }

        /// <summary>The arc points from a pose turning at curvature <paramref name="k"/> for <paramref name="len"/> cells (the start left out); the end pose out.</summary>
        private static List<V2> Arc(V2 a, double h, double k, double len, out V2 end, out double hEnd)
        {
            var o = new List<V2>();
            int m = Math.Max(1, (int)Math.Ceiling(len / 0.05));
            double ds = len / m, x = a.X, z = a.Z;
            for (int i = 0; i < m; i++)
            {
                double hm = h + k * ds / 2;
                x += Math.Cos(hm) * ds; z += Math.Sin(hm) * ds;
                h += k * ds;
                o.Add(new V2(x, z));
            }
            end = new V2(x, z); hEnd = h;
            return o;
        }

        /// <summary>How a heap cable leaves its plug: straight on, or an arc at <see cref="HeapTurnR"/> or wider, to the first roomy spot; only where none stays on the heap, an arc as tight
        /// as <see cref="HeapPlugR"/> over at most <see cref="HeapPlugReach"/> cell (the plug's own forced bend: a box at the heap's edge with an arm pointing out or into a pocket). Null if
        /// nothing gets out.</summary>
        private static List<V2> HeapEscape(Func<V2, bool> onGround, V2 mid, V2 a, double h, CordRng r, out V2 end, out double hEnd)
        {
            // out where it can go on: roomy, headed back into the heap (toward its middle), clear ground a cell on
            bool Out(V2 e, double he) => HeapRoomy(onGround, e) && Math.Abs(Wrap(Math.Atan2(mid.Z - e.Z, mid.X - e.X) - he)) < 1.3
                                         && onGround(e + CordAudit.Dir(he) * 0.5) && onGround(e + CordAudit.Dir(he) * 1.0);
            end = a; hEnd = h;
            double kMax = 1 / HeapTurnR, kPlug = 1 / HeapPlugR;
            int sg = r.Sign();
            var tries = new List<(double k, double maxLen)> { (0, 1.2), (sg * kMax / 2, 1.6), (-sg * kMax / 2, 1.6), (sg * kMax, 2.2), (-sg * kMax, 2.2) };
            // a retry escapes another way: the gentle tries in a drawn order
            for (int i = tries.Count - 1; i > 0; i--) { int j = r.Int(0, i); var t = tries[i]; tries[i] = tries[j]; tries[j] = t; }
            foreach (double kp in new[] { 1 / 0.5, kPlug }) { tries.Add((sg * kp, HeapPlugReach)); tries.Add((-sg * kp, HeapPlugReach)); }
            // first out where it can go on; where no way gets there, out anywhere roomy
            for (int pass = 0; pass < 2; pass++)
                foreach (var (k, maxLen) in tries)
                    for (double len = 0.2; len <= maxLen + 1e-9; len += 0.1)
                    {
                        List<V2> arc = Arc(a, h, k, len, out V2 e, out double he);
                        if (!arc.All(onGround)) break;
                        if (Math.Abs(k) > kMax)
                        {
                            // a tight plug bend, then on at the cord's own radius, either way round, to where it can go on
                            foreach (double k2 in new[] { Math.Sign(k) * kMax, 0, -Math.Sign(k) * kMax })
                                for (double l2 = 0.3; l2 <= 1.6 + 1e-9; l2 += 0.1)
                                {
                                    List<V2> on = Arc(e, he, k2, l2, out V2 e2, out double he2);
                                    if (!on.All(onGround)) break;
                                    if (pass == 0 ? Out(e2, he2) : HeapRoomy(onGround, e2)) { arc.AddRange(on); end = e2; hEnd = he2; return arc; }
                                }
                            continue;
                        }
                        if (pass == 0 ? Out(e, he) : HeapRoomy(onGround, e) && onGround(e + CordAudit.Dir(he) * 0.5)) { end = e; hEnd = he; return arc; }
                    }
            return null;
        }

        /// <summary>A Dubins path between two poses on the heap at a radius from <see cref="HeapTurnR"/> up (the order drawn), no more than one and a half turns, its straight part
        /// bowed (<see cref="Bowed"/>: a heap of straight strokes was the blind judge's "scribble of straight strokes inside a square"); null if none stays on.</summary>
        private static List<V2> HeapLeg(Func<V2, bool> onGround, V2 a, double ha, V2 b, double hb, CordRng r)
        {
            var radii = new List<double> { HeapTurnR, 0.85, 1.0, 1.25 };
            for (int i = radii.Count - 1; i > 0; i--) { int j = r.Int(0, i); double t = radii[i]; radii[i] = radii[j]; radii[j] = t; }
            int sg = r.Sign();
            double amp = r.Range(0.15, 0.28);
            foreach (double rr in radii)
                foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(a, ha, b, hb, rr).OrderBy(d => d.Len))
                {
                    if (dp.Turning > 1.5 * Math.PI) continue;
                    if (dp.Word >= 4)
                    {
                        List<V2> pts = CordShape.Dubins.Sample(a, ha, dp, 0.05);
                        if (pts.All(onGround)) return pts;
                        continue;
                    }
                    // LSL, LSR, RSL, RSR: an arc, a straight, an arc
                    double k1 = (dp.Word <= 1 ? 1 : -1) / rr, k3 = (dp.Word == 0 || dp.Word == 2 ? 1 : -1) / rr;
                    var o = new List<V2>();
                    V2 a1 = a;
                    double h1 = ha;
                    if (dp.T * rr > 1e-6) o.AddRange(Arc(a, ha, k1, dp.T * rr, out a1, out h1));
                    double ls = dp.P * rr;
                    List<V2> mid = null;
                    foreach (int side in new[] { sg, -sg, 0 })
                    {
                        mid = Bowed(a1, h1, ls, side * amp);
                        if (mid.All(onGround)) break;
                        mid = null;
                    }
                    if (mid == null) continue;
                    o.AddRange(mid);
                    V2 sEnd = a1 + CordAudit.Dir(h1) * ls;
                    if (dp.Q * rr > 1e-6) o.AddRange(Arc(sEnd, h1, k3, dp.Q * rr, out _, out _));
                    if (o.All(onGround)) return o;
                }
            return null;
        }

        /// <summary>A straight from a pose bowed off its line in one lazy wave per <see cref="BowWave"/> cells (offset sin^3: flat and unbent at both ends, so it meets the arcs either
        /// side of it without a corner or a tighter turn), at most <paramref name="amp"/> cells (sign = side) and never bending tighter than a <see cref="BowMinR"/>-cell radius, so a short
        /// straight stays nearly straight. The start left out; its end is the straight's own end.</summary>
        private static List<V2> Bowed(V2 a, double h, double len, double amp)
        {
            var o = new List<V2>();
            if (len < 1e-6) return o;
            int m = Math.Max(1, (int)Math.Ceiling(len / 0.05)), n = Math.Max(1, (int)Math.Round(len / BowWave));
            double wave = len / n, cap = wave * wave / (2.1 * Math.PI * Math.PI * BowMinR);   // |offset''| <= ~2.1 pi^2 amp / wave^2
            amp = Math.Sign(amp) * Math.Min(Math.Abs(amp), cap);
            V2 d = CordAudit.Dir(h), nn = d.Perp;
            for (int i = 1; i <= m; i++)
            {
                double t = i / (double)m, sn = Math.Sin(n * Math.PI * t);
                o.Add(a + d * (len * t) + nn * (amp * sn * sn * sn));
            }
            return o;
        }
        private const double BowWave = 2.2, BowMinR = 2.0;

        /// <summary>
        /// A heap's cable from port <paramref name="pa"/> to <paramref name="pb"/>, laid like a cord pushed into a pile: out of each plug (<see cref="HeapEscape"/>), then from stop to
        /// stop of <paramref name="stops"/> (the roomy ones) along Dubins paths at <see cref="HeapTurnR"/> or wider, each stop crossed at a heading drawn round the way on, now and then a
        /// whole coil where one fits. It never turns tighter than that radius outside a coil or its plugs' own bends, so it never folds (never_taut_straight_cord). Null when no draw stays on the heap.
        /// </summary>
        private static List<V2> HeapWalk(Func<V2, bool> onGround, V2 mid, List<V2> stops, PilePort pa, PilePort pb, CordRng r)
        {
            const double lead = 0.22;
            var via = stops.Where(q => HeapRoomy(onGround, q)).ToList();
            V2 sb = pb.Tip + pb.Out * lead;
            for (int attempt = 0; attempt < 6; attempt++)
            {
                var all = new List<V2> { pa.Tip };
                for (int q = 1; q <= 4; q++) all.Add(pa.Tip + pa.Out * (lead * q / 4));
                List<V2> ea = HeapEscape(onGround, mid, all[all.Count - 1], Math.Atan2(pa.Out.Z, pa.Out.X), r, out V2 a, out double ha);
                List<V2> eb = HeapEscape(onGround, mid, sb, Math.Atan2(pb.Out.Z, pb.Out.X), r, out V2 b, out double hb);
                if (ea == null || eb == null) { HeapWalkWhy?.Invoke("no escape " + (ea == null ? "A" : "B")); return null; }
                all.AddRange(ea);
                int coils = r.Int(0, 2);
                List<V2> last = null;
                for (int i = 0; i < via.Count && last == null; i++)
                {
                    V2 to = via[i];
                    bool final = i == via.Count - 1;
                    List<V2> leg = null;
                    double hTo = 0;
                    for (int t = 0; t < (final ? 16 : 8); t++)
                    {
                        V2 next = i + 1 < via.Count ? via[i + 1] : b;
                        hTo = Math.Atan2(next.Z - to.Z, next.X - to.X) + (final ? (t / 16.0 - 0.5) * 2 * Math.PI * 0.9 : r.Range(-1.3, 1.3));
                        leg = HeapLeg(onGround, a, ha, to, hTo, r);
                        // the last stop's heading must also let the cord come round to the far plug's way out
                        if (leg != null && final && (last = HeapLeg(onGround, to, hTo, b, hb + Math.PI, r)) == null) leg = null;
                        if (leg != null) break;
                    }
                    if (leg == null) continue;   // a stop it cannot come by is let go
                    all.AddRange(leg);
                    a = to; ha = hTo;
                    if (!final && coils > 0 && r.Chance(0.6))
                    {
                        // a whole coil where it fits
                        int sg = r.Sign();
                        double rc = r.Range(HeapCoilLo, HeapCoilHi);
                        V2 cc = a + CordAudit.Dir(ha + sg * Math.PI / 2) * rc;
                        List<V2> coil = Arc(a, ha, sg / rc, 2 * Math.PI * rc, out V2 ce, out double ch);
                        if (coil.All(q => onGround(q) && onGround(q + (q - cc).Norm() * 0.06))) { all.AddRange(coil); coils--; }
                    }
                }
                last ??= HeapLeg(onGround, a, ha, b, hb + Math.PI, r);
                HeapWalkTrace?.Invoke(all, via, last != null, onGround);
                if (last == null) { System.Threading.Interlocked.Increment(ref HeapWalkLong); HeapWalkWhy?.Invoke("last leg"); continue; }
                all.AddRange(last);
                eb.Reverse();
                all.AddRange(eb.Skip(1));
                all.Add(sb);
                for (int q = 3; q >= 0; q--) all.Add(pb.Tip + pb.Out * (lead * q / 4));
                return Geo.Resample(all, 0.05);
            }
            return null;
        }

        /// <summary>How far past the middle of its cell a heap's cable may wander, as a multiple of the old 0.3 cell (so up to 0.6 past the middle).</summary>
        public const double PileSpill = 2.0;

        /// <summary>The ground a heap's cables may lie on: its own conduit cells and the open floor a cell round them (8-way), never a door, wall,
        /// furniture, another conduit or pipe, or a machine.</summary>
        internal static HashSet<Cell> PileGround(CordWorld w, List<Cell> comp)
        {
            var g = new HashSet<Cell>(comp);
            foreach (Cell c in comp)
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        var q = new Cell(c.X + dx, c.Z + dz);
                        if (g.Contains(q) || !w.IsWalkable(q) || w.IsDoor(q) || w.IsFurniture(q) || w.IsBusy(q) || w.IsConduit(q)) continue;
                        if (w.Machines.Any(m => m.Contains(q))) continue;
                        g.Add(q);
                    }
            return g;
        }

        /// <summary>
        /// A pile (owner review 2026-10-04 B2/B13): a mass of cables PLUGGED INTO each other. Every cable of the heap
        /// starts and ends on a connector's port, so no connector lies unused and no cable end lies loose. Star Wars,
        /// Jawa and Cybertek piles use many + and T junction boxes (the praised T junction art); the modern
        /// extension-cord pile uses power strips with a plug in their sockets.
        /// </summary>
        private static LaidPiece TanglePiece(CordWorld w, CordNode nd, BuildOptions opt, Func<Cell, bool> isLive)
        {
            var p = new LaidPiece { Key = "tangle:" + nd.Cell, Owner = nd.Cell };
            List<Cell> comp = nd.Cells;
            bool lit = isLive(nd.Cell);
            p.LiveKeys.Add(nd.Cell);
            bool strips = opt.PileFor(nd.Cell) == PileArt.Strips;
            List<CordDecal> cons = PileConnectors(w, nd, opt, lit);
            List<PilePort> ports = PortsOf(cons);
            // ---- cables: each runs port to port; cable i pairs port i with the port half the list away (another connector),
            // so the first ports/2 cables already fill every port: no socket or arm is left empty
            int n = Math.Min(MaxPileCables, Math.Max(Math.Min(14, 4 + comp.Count / 3), (ports.Count + 1) / 2));
            var used = new HashSet<int>();
            // the heap may spill a cell past its conduit onto open floor: kept to the conduit's own cells, its cables drew the block's square
            // outline with straight sides (blind judge p14a/p15a, every look: "squared heaps with straight strokes")
            HashSet<Cell> compSet = PileGround(w, comp);
            Func<V2, bool> onGround = null;
            V2 mid = new V2(comp.Average(c => c.X + 0.5), comp.Average(c => c.Z + 0.5));
            for (int i = 0; i < n && ports.Count >= 2; i++)
            {
                CordRng r = CordRng.Of(opt.Seed, "tangle", nd.Cell.X, nd.Cell.Z, i);
                int a = i % ports.Count, b = (i + ports.Count / 2) % ports.Count;
                for (int k = 0; k < ports.Count && cons.Count > 1 && ports[b].Connector == ports[a].Connector; k++) b = (b + 1) % ports.Count;
                if (a == b) continue;
                PilePort pa = ports[a], pb = ports[b];
                if (opt.Lay.FairBends)
                {
                    // a cable pushed into the pile: it wanders and coils, never folds (never_taut_straight_cord), over a lumpy round heap (not the block's square)
                    if (onGround == null)
                    {
                        // the walk may also cross the first cell of a conduit run leaving the heap: a port facing it bends its cable away there, as the run's own cord leaves
                        var walkCells = new HashSet<Cell>(compSet);
                        foreach (Cell c in comp)
                            for (int dx = -1; dx <= 1; dx++)
                                for (int dz = -1; dz <= 1; dz++)
                                {
                                    var q = new Cell(c.X + dx, c.Z + dz);
                                    if (w.IsConduit(q) && w.IsWalkable(q) && !w.IsDoor(q) && !w.IsFurniture(q) && !w.Machines.Any(m => m.Contains(q))) walkCells.Add(q);
                                }
                        onGround = HeapGround(walkCells, comp, opt.Seed, ports);
                    }
                    CordRng rw = CordRng.Of(opt.Seed, "heapwalk", nd.Cell.X, nd.Cell.Z, i);
                    var via = new List<V2>();
                    int nv = rw.Int(3, 5);
                    for (int k = 0; k < nv; k++)
                        for (int t = 0; t < 8; t++)
                        {
                            V2 q = comp[rw.Int(0, comp.Count - 1)].Centre + CordAudit.Dir(rw.Range(0, 2 * Math.PI)) * rw.Range(0, 1.1);
                            if (onGround(q)) { via.Add(q); break; }
                        }
                    List<V2> walk = HeapWalk(onGround, mid, via, pa, pb, rw);
                    if (walk != null)
                    {
                        p.Strands.Add(new CordStrand { Pts = walk, S0 = rw.Value() });
                        used.Add(a); used.Add(b);
                        continue;
                    }
                    System.Threading.Interlocked.Increment(ref HeapWalkMisses);
                }
                var stops = new List<V2> { pa.Tip, pa.Tip + pa.Out * 0.22 };
                int ns = r.Int(2, 4);
                for (int k = 0; k < ns; k++)
                    stops.Add(comp[r.Int(0, comp.Count - 1)].Centre + new V2(r.Range(-0.3, 0.3), r.Range(-0.3, 0.3)) * PileSpill);
                stops.Add(pb.Tip + pb.Out * 0.22);
                stops.Add(pb.Tip);
                List<V2> P = Geo.Resample(Geo.Catmull(stops, 10), 0.05);
                // a strip pile's cables are far apart (a strip every 7 cells), so a spline through a few cells of the heap drew
                // long strokes corner to corner, a net (blind judge, pass 12-14): they swirl instead (owner: "a huge tangle of nasty wires and power strips all swirled together terribly")
                List<V2> swirl = strips ? Swirl(w, compSet, pa, pb, CordRng.Of(opt.Seed, "swirl", nd.Cell.X, nd.Cell.Z, i)) : null;
                if (swirl != null) P = swirl;
                int heaps = swirl != null ? r.Int(0, 1) : r.Int(1, 2);
                for (int k = 0; k < heaps && P.Count > 24; k++)
                {
                    int j = r.Int(P.Count / 3, 2 * P.Count / 3);
                    var win = P.GetRange(Math.Max(0, j - 2), Math.Min(P.Count, j + 3) - Math.Max(0, j - 2));
                    Geo.TanNorm(win, win.Count / 2, out V2 t, out V2 nn);
                    // with FairBends a heap's spare turns are loose and broad (the owner: "what they avoid are sharp curves"), not a tight spring reversing at every turn
                    var hp = opt.Lay.FairBends ? CordLayer.LooseHeap(P[j], t, nn, r.Range(CordLayer.RoundLoopMinR, 0.7), r.Sign(), r) : CordLayer.Heap(P[j], t, nn, r.Range(0.2, 0.4), r.Sign(), r);
                    // a broad turn that would leave the heap's ground is left out, not the whole cable (a strip lost a plugged cable: B13, pile look rule 1)
                    if (opt.Lay.FairBends && !hp.All(q => compSet.Contains(q.Floor))) continue;
                    var o = new List<V2>(P.GetRange(0, j));
                    o.AddRange(hp);
                    o.AddRange(P.GetRange(j + 1, P.Count - j - 1));
                    P = o;
                }
                P = Geo.Resample(P, 0.05);
                CordLayer.Smooth(w, P, 3);
                P[0] = pa.Tip; P[P.Count - 1] = pb.Tip;
                P = CordShape.Unfold(w, P);
                if (opt.Lay.FairBends) P = CordShape.Fair(w, P, 0.22, 0.22, null, compSet, cutLoops: false);
                if (!P.All(q => compSet.Contains(q.Floor))) continue;
                p.Strands.Add(new CordStrand { Pts = P, S0 = r.Value() });
                used.Add(a); used.Add(b);
            }
            // ---- connectors are printed over the cables; a strip gets a plug in every socket a cable uses
            p.Decals.AddRange(cons);
            if (strips)
                foreach (int k in used.OrderBy(x => x))
                {
                    PilePort q = ports[k];
                    p.Decals.Add(new CordDecal(DecalKind.Plug, q.Tip, Math.Atan2(-q.Out.Z, -q.Out.X), PilePlugScale));
                }
            return p;
        }
    }
}
