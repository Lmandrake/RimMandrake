using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Runtime side of the flexible hoses (design 3.4-3.5): ticks every reel's state machine from the flow providers,
    /// lays hoses lazily (planner + rope settle in HoseMath), and draws them every frame (a handful of meshes; a
    /// settled hose reuses its cached mesh and pose, a transitioning one is rebuilt once per tick, a winding one every frame). Kept OUT of the save
    /// (Patch_Map_ExposeComponents_SkipHoses): the reels hold everything that must persist.
    /// </summary>
    [StaticConstructorOnStartup]
    public class RM_MapComponent_Hoses : MapComponent
    {
        private readonly List<CompHoseReel> reels = new List<CompHoseReel>();
        private readonly Dictionary<CompHoseReel, Cached> meshes = new Dictionary<CompHoseReel, Cached>();
        private CordWorld world;
        private int worldTick = -1;
        /// <summary>HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED: bumped by every map change the snapshot reads (MapChanged), and
        /// the value the snapshot was built from; World() rebuilds when they differ, paused or not.</summary>
        private int mapVersion, worldVersion = -1;
        private bool mapEventsHooked;
        private bool drawErrorLogged;
        public static int Relays, LastLayMs, Retracts;
        /// <summary>Whole-map CordWorld snapshots built (World()), and corridor checks answered from the live map instead.</summary>
        public static int WorldBuilds, LiveCorridorChecks;

        private sealed class Cached
        {
            public string key;
            public Mesh flat, plump, shadow;
            /// <summary>The pose these meshes were built from (review 2026-10-22: a cache hit reuses it, no Pose per frame).</summary>
            public List<V2> pts;
            /// <summary>The drawn strand (pts trimmed at the outlet), what the over-draws below are cut from.</summary>
            public List<V2> rp;
            /// <summary>HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK: the stretches over walk-over buildings (arc spans on rp), redrawn
            /// above the building layer; rebuilt when the pose or the map's buildings change (overKey).</summary>
            public string overKey;
            public List<double[]> overSpans;
            public List<Mesh> overMeshes = new List<Mesh>();
            /// <summary>HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE: the stretches over hoses drawn beneath, and their crossing shadow.</summary>
            public string crossKey;
            public List<double[]> crossSpans;
            public Mesh crossShadow;
        }

        /// <summary>JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX: a coupling as the draw placed it (centre, axis, size, opaque band), by
        /// role: reel_end (laid hose on the nozzle), port_end (free end on a tank/pipe/pump port), relay_end, feed_nozzle (a port
        /// link into a stored reel's nozzle). The joint probe measures these, not the geometry that meant to place them.</summary>
        internal struct DrawnFitting
        {
            public V2 centre, dir;
            public double size, band;
        }

        internal readonly Dictionary<CompHoseReel, Dictionary<string, DrawnFitting>> drawnFittings = new Dictionary<CompHoseReel, Dictionary<string, DrawnFitting>>();

        /// <summary>State reads for the joint probe: the drawn strand and its over-building / crossing spans, as last drawn.</summary>
        internal List<V2> DrawnStrand(CompHoseReel r) => meshes.TryGetValue(r, out Cached c) ? c.rp : null;
        internal List<double[]> OverSpansOf(CompHoseReel r) => meshes.TryGetValue(r, out Cached c) ? c.overSpans : null;
        internal List<double[]> CrossSpansOf(CompHoseReel r) => meshes.TryGetValue(r, out Cached c) ? c.crossSpans : null;
        internal int RankOfReel(CompHoseReel r) => RankOf(r);

        /// <summary>PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE: a port-coupled hose's run on beneath the tank or machine to its centre,
        /// one cached mesh per reel, rebuilt only when the end, port footprint, width or band changes (compared field by
        /// field: no per-frame allocation).</summary>
        private sealed class StubCache
        {
            public IntVec3 cell;
            public int sx, sz;
            public CellRect rect;
            public float w, y;
            public Mesh mesh;
        }

        private readonly Dictionary<CompHoseReel, StubCache> stubMeshes = new Dictionary<CompHoseReel, StubCache>();
        /// <summary>State read: hose port stubs drawn last frame, and stub meshes built since load.</summary>
        public int lastPortStubs, portStubBuilds;

        public RM_MapComponent_Hoses(Map map) : base(map) { }

        /// <summary>FINAL §3.9 fallback: without the save-skip patch this component would be written into saves by class
        /// name, so MapComponentUpdate takes it off the map on its first frame (not here: see below); MapComponentTick is
        /// inert until then (hoses draw nothing; reels keep their saved ends). The one red
        /// line naming the missing patch is logged by RM_HoseEssentials.</summary>
        public override void FinalizeInit()
        {
            base.FinalizeInit();
            // not removed HERE: MapComponentUtility.FinalizeInit walks map.components by index, so removing self would skip
            // the next component's FinalizeInit. Inert (MapComponentTick) until the first frame's MapComponentUpdate removes it.
        }

        /// <summary>MAP_STATICS_PRUNE_GHOST_MAPS (as C5-F4 for the liquid surface): the cached strand, feed and carry meshes are
        /// Unity objects this component owns; destroy them with the map.</summary>
        public override void MapRemoved()
        {
            base.MapRemoved();
            UnhookMapEvents();
            foreach (Cached c in meshes.Values) DestroyMeshes(c);
            meshes.Clear();
            foreach (StubCache sc in stubMeshes.Values) if (sc.mesh != null) UnityEngine.Object.Destroy(sc.mesh);
            stubMeshes.Clear();
            foreach (CompHoseReel r in new List<CompHoseReel>(feeds.Keys)) DropFeed(r);
            foreach (CompHoseReel r in new List<CompHoseReel>(carryCache.Keys)) DropCarryCache(r);
            FlushFrameMeshes();
        }

        public IReadOnlyList<CompHoseReel> Reels => reels;

        public void Register(CompHoseReel r) { if (!reels.Contains(r)) reels.Add(r); RelayVersion++; }

        public void Deregister(CompHoseReel r)
        {
            reels.Remove(r);
            RelayVersion++;
            DropMeshes(r);
            DropFeed(r);
            DropCarryCache(r);
            seenCarry.Remove(r);
            lastDraw.Remove(r);
            lastDrawnLen.Remove(r);
            lastHand.Remove(r);
            totals.Remove(r);
            ends.Remove(r);
            placedKind.Remove(r);
            drawnFittings.Remove(r);
            ghosts.RemoveAll(g => g.reel == r);
        }

        // ------------------------------------------------------------------ world snapshot for hoses
        /// <summary>A hose's CordWorld: walls, rock, impassable buildings and fog block it; WATER does not (a hose
        /// floats, design 3.5: walkable at extra cost 3); trees cost a little; a reel or pump (walk-over) costs
        /// HoseMath.BuildingCrossCost so the hose goes round it (HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE), and so does any other
        /// walk-over building drawn above the hose (CostsAsBuilding, HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK). Cached for the tick it was taken.</summary>
        internal CordWorld World(int maxAge = 0)
        {
            HookMapEvents();
            int now = Find.TickManager.TicksGame;
            if (world != null && HoseLive.SnapshotFresh(now, worldTick, maxAge, worldVersion, mapVersion)) return world;
            int version = mapVersion;
            int w = map.Size.x, h = map.Size.z;
            WorldBuilds++;
            var cw = new CordWorld(w, h);
            CellIndices ci = map.cellIndices;
            for (int idx = 0; idx < w * h; idx++)
            {
                IntVec3 c = ci.IndexToCell(idx);
                var cell = new Cell(c.x, c.z);
                if (map.fogGrid.IsFogged(idx)) { cw.SetBlocked(cell, BlockKind.Rock); continue; }
                Building ed = map.edificeGrid[idx];
                if (ed is Building_Door) cw.SetDoor(cell);
                TerrainDef t = map.terrainGrid.TerrainAt(idx);
                if (map.pathing.Normal.pathGrid.WalkableFast(idx)) { if (CostsAsBuilding(ed)) cw.SetExtraCost(cell, HoseMath.BuildingCrossCost); continue; }
                if (ed == null && t != null && t.IsWater && !HasImpassableThing(c)) { cw.SetExtraCost(cell, 3f); continue; }
                if (ed != null && CompHoseReelOf(ed) != null) { cw.SetExtraCost(cell, HoseMath.BuildingCrossCost); continue; }
                cw.SetBlocked(cell, ed != null && ed.def.building != null && ed.def.building.isNaturalRock ? BlockKind.Rock : BlockKind.Wall);
            }
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                if (p.def.plant != null && p.def.plant.IsTree) cw.SetExtraCost(new Cell(p.Position.x, p.Position.z), 1.5f);
            RM_HoseBands.Apply(map, cw);   // PIPE_POLES phase 6: depth bands, ramp/ladder links (design §P5)
            world = cw;
            worldTick = now;
            worldVersion = version;
            return cw;
        }

        /// <summary>HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED: subscribe once to the map events that change what World() reads
        /// (edifices, reels and pumps via Building*, trees via Thing*, water via TerrainChanged, walkability and pit bands via
        /// PathCostRecalculate, fog via CellFog/MapFogged). A handler only bumps a counter; the rebuild waits for the next read.</summary>
        private void HookMapEvents()
        {
            if (mapEventsHooked || map?.events == null) return;
            mapEventsHooked = true;
            map.events.BuildingSpawned += OnBuilding;
            map.events.BuildingDespawned += OnBuilding;
            map.events.ThingSpawned += OnThing;
            map.events.ThingDespawned += OnThing;
            map.events.TerrainChanged += OnCell;
            map.events.PathCostRecalculate += OnCell;
            map.events.CellFogChanged += OnFog;
            map.events.MapFogged += MapChanged;
        }

        private void UnhookMapEvents()
        {
            if (!mapEventsHooked || map?.events == null) return;
            mapEventsHooked = false;
            map.events.BuildingSpawned -= OnBuilding;
            map.events.BuildingDespawned -= OnBuilding;
            map.events.ThingSpawned -= OnThing;
            map.events.ThingDespawned -= OnThing;
            map.events.TerrainChanged -= OnCell;
            map.events.PathCostRecalculate -= OnCell;
            map.events.CellFogChanged -= OnFog;
            map.events.MapFogged -= MapChanged;
        }

        private void OnBuilding(Building b) => MapChanged();
        private void OnThing(Thing t) { if (t is Plant p && p.def.plant != null && p.def.plant.IsTree) MapChanged(); }
        private void OnCell(IntVec3 c) => CellChanged(c);
        private void OnFog(IntVec3 c, bool fogged) => CellChanged(c);
        /// <summary>A per-cell event (path cost, terrain, fog) bumps the version only when the cell now reads differently from the
        /// snapshot (LiveCellSig, World()'s rule for one cell): snow and filth recalculate path costs all the time, and a bump per
        /// tick would rebuild the whole-map snapshot per tick for every World(60) reader.</summary>
        private void CellChanged(IntVec3 c)
        {
            if (world == null || worldVersion != mapVersion) return;   // already rebuilding on the next read
            var cell = new Cell(c.x, c.z);
            if (CordSig.CellSig(world, cell) != LiveCellSig(cell)) MapChanged();
        }
        private void MapChanged() => mapVersion++;

        /// <summary>
        /// CordSig.CellSig(World(), c) read off the LIVE map for one cell, without building the whole-map snapshot: the same
        /// per-cell rule as World() above (fog -> blocked; door; walkable, a reel, a pump or another walk-over building drawn above
        /// the hose costing BuildingCrossCost (CostsAsBuilding); free water costs 3; a reel's own edifice costs the same;
        /// else blocked) and its tree pass (a tree costs 1.5, over anything). 2026-10-11 live perf reading (full list, 23
        /// reels, 11 laid): the every-250-tick corridor check of each laid reel called World() at its OWN staggered tick, so
        /// the per-tick cache never hit and every laid reel paid a full 250x250 scan (~4 ms) per cycle: 0.152 ms/tick mean
        /// for the hose map component against the 0.05 budget (FINAL §3.5), growing with every laid hose. Probe verb
        /// "corridor" compares both hashes for every laid reel.
        /// </summary>
        internal ulong LiveCellSig(Cell cell)
        {
            var c = new IntVec3(cell.X, 0, cell.Z);
            if (!c.InBounds(map)) return SigOf(false, false, 0f);   // CordWorld: out of bounds is not walkable
            int idx = map.cellIndices.CellToIndex(c);
            bool walk = true, door = false;
            float extra = 0f;
            if (map.fogGrid.IsFogged(idx)) walk = false;
            else
            {
                Building ed = map.edificeGrid[idx];
                door = ed is Building_Door;
                TerrainDef t = map.terrainGrid.TerrainAt(idx);
                if (map.pathing.Normal.pathGrid.WalkableFast(idx)) { if (CostsAsBuilding(ed)) extra = HoseMath.BuildingCrossCost; }
                else if (ed == null && t != null && t.IsWater && !HasImpassableThing(c)) extra = 3f;
                else if (ed != null && CompHoseReelOf(ed) != null) extra = HoseMath.BuildingCrossCost;
                else walk = false;
                if (walk && RM_HoseBands.Closed(map, c)) walk = false;   // phase 7: a pit cover carries no hose (World(): RM_HoseBands.Apply)
            }
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++)
                if (l[i] is Plant p && p.def.plant != null && p.def.plant.IsTree) { extra = 1.5f; break; }
            // PIPE_POLES phase 6: the band and the ramp/ladder links, as World() writes them (RM_HoseBands), so a dug square
            // on a laid hose's corridor moves its hash and the 250-tick check re-plans or reels it in
            int band = RM_HoseBands.BandAt(map, c);
            return SigOf(walk, door, extra, band, RM_HoseBands.On && (band != 0 || AnyDugNeighbour(c)) ? RM_HoseBands.LinkMask(map, c, band) : 0);
        }

        private bool AnyDugNeighbour(IntVec3 c)
        {
            for (int r = 0; r < 4; r++)
                if (RM_HoseBands.BandAt(map, new IntVec3(c.x + CordWorld.CardX[r], 0, c.z + CordWorld.CardZ[r])) != 0) return true;
            return false;
        }

        /// <summary>CordSig.CellSig's formula (the same shared CordSig.Of, so the live read and the snapshot cannot drift).</summary>
        internal static ulong SigOf(bool walkable, bool door, float extra, int band = 0, int linkMask = 0) =>
            CordSig.Of(walkable, door, extra, band, linkMask);

        /// <summary>CorridorHash over the live map (LiveCellSig), equal to CorridorHash(World(), lay) while nothing changed.</summary>
        internal ulong CorridorHashLive(HoseLay lay)
        {
            LiveCorridorChecks++;
            return CorridorHash(lay, LiveCellSig);
        }

        private bool HasImpassableThing(IntVec3 c)
        {
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++) if (l[i].def.passability == Traversability.Impassable) return true;
            return false;
        }

        /// <summary>HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE: the hose rig's own walk-over machinery (a reel, a pump) costs
        /// <see cref="HoseMath.BuildingCrossCost"/>, so a hose goes round it on bare ground. HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK
        /// (audit F2, owner card 2026-10-23 "Keep over-ground"): so does every other walk-over building drawn above the hose
        /// (<see cref="DrawsOverHose"/>: a battery, a power connector, sandbags, furniture), which the hose used to price as bare
        /// ground and vanish beneath. Still a cost, never a block: the route search is bounded by LENGTH, not cost
        /// (RouteCells), and install judges the shortest route (costs off), so a hose with no other way still crosses -- and is
        /// then drawn over the building (DrawOverBuildings). Floor-level walk-over buildings (altitude at or below the hose's
        /// layer) draw beneath the hose anyway and stay free.</summary>
        private static bool CostsAsBuilding(Building ed) =>
            ed != null && (IsRig(ed) || DrawsOverHose(ed));

        /// <summary>A reel or a pump: the hose rig's own machinery, whose joints are drawn by their own rules.</summary>
        internal static bool IsRig(Building ed) =>
            ed != null && (CompHoseReelOf(ed) != null || ed is RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump);

        /// <summary>A walk-over (path-walkable) building, not a door and not the rig's own machinery, whose sprite draws above
        /// the hose's altitude layer (DrawOrder.LayerHose = Shadows): a hose lying across its cell would be painted under it.
        /// The caller has already checked walkability (World/LiveCellSig), or does so (OverBuildingCell).</summary>
        internal static bool DrawsOverHose(Building ed) =>
            ed != null && !(ed is Building_Door) && !IsRig(ed) && (int)ed.def.altitudeLayer > RimMandrake.Shared.Slack.DrawOrder.LayerHose;

        /// <summary>The cell holds a walk-over building drawn above the hose (<see cref="DrawsOverHose"/>).</summary>
        internal bool OverBuildingCell(Cell c)
        {
            var ic = new IntVec3(c.X, 0, c.Z);
            if (!ic.InBounds(map)) return false;
            int idx = map.cellIndices.CellToIndex(ic);
            Building ed = map.edificeGrid[idx];
            return ed != null && map.pathing.Normal.pathGrid.WalkableFast(idx) && DrawsOverHose(ed);
        }

        /// <summary>The cell holds a reel or pump (<see cref="IsRig"/>).</summary>
        internal Building RigAt(Cell c)
        {
            var ic = new IntVec3(c.X, 0, c.Z);
            if (!ic.InBounds(map)) return null;
            Building ed = map.edificeGrid[map.cellIndices.CellToIndex(ic)];
            return IsRig(ed) ? ed : null;
        }

        private static CompHoseReel CompHoseReelOf(Thing t) => (t as ThingWithComps)?.GetComp<CompHoseReel>();

        public string CheckInstall(CompHoseReel r, IntVec3 target)
        {
            if (!RM_HoseSettings.enabled) return "hoses are switched off in Mod Settings";
            var cell = new Cell(target.x, target.z);
            string why = HoseMath.CheckInstall(World(), r.Rect, cell, r.MaxLength);
            if (why != null) return why;
            // 2026-10-10 (GSS_HOSE_LAY_DIAGNOSE_FIFTEEN_NEW_REDS, RL3): HoseMath.CheckInstall judges the taut route, which does
            // not count the nozzle's straight lead-out (owner card 2026-10-06), so an order it accepted could still be refused at
            // lay time ("route too long (the laid hose, lead-out included ...)" / no room for the lead-out) -- the colonist
            // carried the hose out to a lay that never drew. The planned lay is the best case of any walked one, so it is the gate.
            CompHoseReel relay = RelayAt(r, cell);
            V2 end = cell.Centre;
            V2? inward = null;
            if (relay != null) { end = HoseRelay.DrawnEnd(relay.Rect, cell, HoseMaterials.LookOf(relay), relay.laid, out V2 d); inward = d; }
            HoseLay lay = LayFrom(r, end, inward, null);
            return lay.Ok ? null : (lay.Reason ?? "could not be laid");
        }

        // ------------------------------------------------------------------ relays (round 6, HoseRelay)
        // Review S1 (design FINAL §3.1 "Index", G1.17): the relay adjacency is built ONCE (HoseRelayIndex, O(reels)) and shared
        // by drawing, Loops, FeedersOf, the debug flow provider and RM_HoseLinks. It is rebuilt only when the topology
        // signature (each reel's id, footprint, laid end and debug flag) changes, so an end laid mid-tick is seen at once.
        private HoseRelayIndex relayIndex;
        private readonly List<CompHoseReel> relayOrder = new List<CompHoseReel>();
        private readonly Dictionary<CompHoseReel, int> relayPos = new Dictionary<CompHoseReel, int>();
        private ulong relaySig;
        private int relayVerSeen = -1, relayCheckTick = -1;
        /// <summary>Bumped by every writer of a reel's laid end, footprint registration or debug flag (review S1).</summary>
        public static int RelayVersion;
        /// <summary>State read: relay-index rebuilds this session (perf row).</summary>
        public static int RelayIndexBuilds;

        private ulong RelaySignature()
        {
            ulong h = 1469598103934665603UL ^ (ulong)reels.Count;
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel r = reels[i];
                Thing t = r.parent;
                IntVec3 p = t.Position;
                bool laidEnd = r.laid && r.far.IsValid;
                ulong v = (ulong)(uint)t.thingIDNumber;
                v = v * 31 + (ulong)(uint)(p.x * 73856093 ^ p.z * 19349663);
                v = v * 31 + (ulong)(uint)t.Rotation.AsInt;
                v = v * 31 + (laidEnd ? (ulong)(uint)(r.far.x * 83492791 ^ r.far.z * 2971215073L) + 1UL : 0UL);
                v = v * 2 + (r.debugFlowing ? 1UL : 0UL);
                h = (h ^ v) * 1099511628211UL;
            }
            return h;
        }

        /// <summary>The shared relay index and the reels in its (thing-id) order.</summary>
        internal HoseRelayIndex RelayIndex()
        {
            // fast path: nothing announced a change (RelayVersion) and the signature was already checked this tick. The once-per-
            // tick signature check (O(reels)) is the backstop for a writer that forgot to bump the version.
            int now = Find.TickManager?.TicksGame ?? 0;
            if (relayIndex != null && relayVerSeen == RelayVersion && relayCheckTick == now) return relayIndex;
            relayVerSeen = RelayVersion;
            relayCheckTick = now;
            ulong sig = RelaySignature();
            if (relayIndex != null && sig == relaySig) return relayIndex;
            relayOrder.Clear();
            relayOrder.AddRange(reels);
            relayOrder.Sort((a, b) => a.parent.thingIDNumber.CompareTo(b.parent.thingIDNumber));
            relayPos.Clear();
            var rects = new List<HoseReelRect>(relayOrder.Count);
            var far = new List<Cell?>(relayOrder.Count);
            var dbg = new List<bool>(relayOrder.Count);
            for (int i = 0; i < relayOrder.Count; i++)
            {
                CompHoseReel r = relayOrder[i];
                relayPos[r] = i;
                rects.Add(r.Rect);
                far.Add(r.laid && r.far.IsValid ? new Cell(r.far.x, r.far.z) : (Cell?)null);
                dbg.Add(r.debugFlowing);
            }
            relayIndex = new HoseRelayIndex(rects, far, dbg);
            relaySig = sig;
            RelayIndexBuilds++;
            return relayIndex;
        }

        private int PosOf(CompHoseReel r) => r != null && relayPos.TryGetValue(r, out int i) ? i : -1;

        private CompHoseReel At(int i) => i >= 0 && i < relayOrder.Count ? relayOrder[i] : null;

        /// <summary>The reel whose intake this reel's laid hose ends on (null = a free end).</summary>
        public CompHoseReel RelayOf(CompHoseReel r)
        {
            if (r == null || !r.laid || !r.far.IsValid) return null;
            HoseRelayIndex idx = RelayIndex();
            int i = PosOf(r);
            return At(i >= 0 ? idx.Next(i) : idx.RelayAt(new Cell(r.far.x, r.far.z), -1));
        }

        /// <summary>The reel (other than r) that has <paramref name="c"/> as an intake cell, or null.</summary>
        internal CompHoseReel RelayAt(CompHoseReel r, Cell c)
        {
            HoseRelayIndex idx = RelayIndex();
            return At(idx.RelayAt(c, PosOf(r)));
        }

        /// <summary>The reel whose FOOTPRINT holds the cell (other than r), or null: the player clicked onto a relay.</summary>
        public CompHoseReel ReelCovering(CompHoseReel r, IntVec3 c)
        {
            foreach (CompHoseReel o in reels) if (o != r && o.Rect.Contains(new Cell(c.x, c.z))) return o;
            return null;
        }

        /// <summary>Reels feeding r (their hose ends on r's intake), in thing-id order, loops excluded.</summary>
        public List<CompHoseReel> FeedersOf(CompHoseReel r)
        {
            HoseRelayIndex idx = RelayIndex();
            var o = new List<CompHoseReel>();
            foreach (int f in idx.Feeders(PosOf(r))) o.Add(relayOrder[f]);
            return o;
        }

        /// <summary>True when some reel's laid hose ends on r's intake (no list built).</summary>
        internal bool IsFed(CompHoseReel r) => RelayIndex().Feeders(PosOf(r)).Count > 0;

        /// <summary>The relay r's laid hose feeds, loops excluded (RM_HoseLinks' far end), or null.</summary>
        internal CompHoseReel FeedsInto(CompHoseReel r)
        {
            HoseRelayIndex idx = RelayIndex();
            int i = PosOf(r);
            return i < 0 || idx.OnLoop(i) ? null : At(idx.Next(i));
        }

        /// <summary>The reels in thing-id order (the index's order).</summary>
        internal IReadOnlyList<CompHoseReel> OrderedReels() { RelayIndex(); return relayOrder; }

        /// <summary>True when some reel on this map carries the debug-flow flag (from the shared index).</summary>
        internal bool AnyDebugFlowing() => RelayIndex().AnyDebug;

        /// <summary>The debug provider's chain read through the shared index (O(1) on a map with no debug flag).</summary>
        internal bool FedByDebug(CompHoseReel r)
        {
            HoseRelayIndex idx = RelayIndex();
            if (!idx.AnyDebug) return false;
            return idx.FedByDebug(PosOf(r), i => relayOrder[i].laid && relayOrder[i].lay != null);
        }

        /// <summary>Would a hose from <paramref name="from"/> into <paramref name="to"/> close a loop?</summary>
        public bool Loops(CompHoseReel from, CompHoseReel to, bool withPending = false)
        {
            HoseRelayIndex idx = RelayIndex();
            int iFrom = PosOf(from), iTo = PosOf(to);
            if (!withPending) return idx.WouldLoop(iFrom, iTo);
            return HoseRelay.WouldLoop(iFrom, iTo, i =>
            {
                CompHoseReel ri = relayOrder[i];
                // B10: a pending order's end counts too (the order check), so two orders cannot form a ring
                bool pend = (ri.pending == HosePendingOrder.Deploy || ri.pending == HosePendingOrder.Move) && ri.pendingAt.IsValid;
                int pn = pend ? idx.RelayAt(new Cell(ri.pendingAt.x, ri.pendingAt.z), i) : -1;
                return HoseRelay.IntendedNext(idx.Next(i), pend, pn);
            });
        }

        /// <summary>Where r's hose ends: on a relay, the drawn reel's inlet / outline at its intake side (HoseRelay.DrawnEnd,
        /// round 7), else its free-end cell's centre.</summary>
        internal V2 EndPoint(CompHoseReel r, out CompHoseReel relay) => EndPoint(r, out relay, out _);

        /// <summary>As EndPoint; <paramref name="inward"/> = the direction the hose's last stretch and coupling point
        /// into the relay (null at a free end).</summary>
        internal V2 EndPoint(CompHoseReel r, out CompHoseReel relay, out V2? inward)
        {
            relay = RelayOf(r);
            inward = null;
            IntVec3 ec = r.EndCell;   // S2: far while laid/dropped, the trail's last cell while carried or wound
            var far = new Cell(ec.x, ec.z);
            if (relay == null) return far.Centre;
            V2 e = HoseRelay.DrawnEnd(relay.Rect, far, HoseMaterials.LookOf(relay), relay.laid, out V2 d);
            inward = d;
            return e;
        }

        // ------------------------------------------------------------------ lay
        /// <summary>The hose leaves the reel at its drum's axis (HoseReelRect.Mouth, round 5), hidden by the sprite, so it shows
        /// coming off the drum; the deployed art paints no hose of its own.</summary>
        internal static V2 Start(CompHoseReel r) => r.Rect.Mouth;

        public HoseLay EnsureLay(CompHoseReel r)
        {
            if (!r.HoseOut) return null;
            V2 end = EndPoint(r, out CompHoseReel relay, out V2? inward);
            // HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 3: a laid end on a tank port is laid onto the port's axis (HoseMath.PortLay)
            V2? portAt = null;
            V2 portAxis = default(V2);
            if (relay == null && r.laid && PortEnd(r, out V2 pAt, out portAxis)) portAt = pAt;
            // the relay's look and art (stored / laid) move the drawn inlet, so they are part of the key; S2: so does the
            // walked trail (empty = the planned route, the key as before)
            // the reel's OWN look too: the nozzle (Mouth, where the hose starts) is measured per look, and "Choose style" restyles in place
            string key = r.parent.Position + "/" + HoseLook.LookOfThing(r.parent) + ">" + r.EndCell + (relay != null ? "R" + relay.parent.thingIDNumber + HoseMaterials.LookOf(relay) + (relay.laid ? "L" : "S") : "") + r.TrailKey() + "|" + RM_HoseSettings.ShapeFingerprint() + (IsFed(r) ? "|fed" : "")
                + (portAt.HasValue ? "|p" + portAt.Value.X.ToString("0.000") + "," + portAt.Value.Z.ToString("0.000") + "/" + portAxis.X + "," + portAxis.Z : "");
            if (r.layKey == key) return r.lay; // a failed lay is cached too (lay null); the 250-tick check clears layKey to retry
            var sw = System.Diagnostics.Stopwatch.StartNew();
            CordWorld w = World();
            IList<Cell> trail = r.TrailCells();
            HoseLay lay = HoseMath.PortLay((e1, in1) => LayFrom(r, e1, in1, trail), end, inward, portAt, portAxis);
            // owner decision by question card 2026-10-06 (straight lead-out): no clear lead-out from the nozzle = refused with
            // the reason (HoseMath.LeadOutBlocked); the old fallback laid it without the outlet
            LastLayMs = (int)sw.ElapsedMilliseconds;
            Relays++;
            // FINAL §3.2 lifecycle: a refused lay carries nothing, and a hose laid to a NEW end starts without the old lease
            if (!lay.Ok || r.layEnd != r.EndCell) r.EndLease();
            r.layEnd = r.EndCell;
            r.lay = lay.Ok ? lay : null;
            r.lastLayReason = lay.Ok ? null : (lay.Reason ?? "could not be laid");
            r.layKey = key;
            r.corridorHash = lay.Ok ? CorridorHash(w, lay) : 0;
            DropMeshes(r);
            return r.lay;
        }

        /// <summary>The lay of r's hose to <paramref name="end"/> (EnsureLay's, and CheckInstall's trial with an empty route).</summary>
        private HoseLay LayFrom(CompHoseReel r, V2 end, V2? inward, IList<Cell> route)
        {
            CordWorld w = World();
            HoseShapeParams sp = RM_HoseSettings.Shape();
            sp.MaxLength = r.MaxLength;
            // 2026-10-05: a nozzled reel's hose leaves through its west outlet, so for this lay its own footprint is solid: a
            // target behind the reel is reached round it, never by running back under the reel from the outlet
            var held = new List<KeyValuePair<Cell, BlockKind>>();
            // a relay reel's west nozzle is where the FEEDING hose couples (HoseRelay.DrawnEnd), so its own hose keeps the
            // pre-2026-10-05 start; flagged to the owner, not redesigned here
            V2? outward = !IsFed(r) ? r.Rect.Outward : null;
            if (outward.HasValue)
                for (int x = r.Rect.X0; x < r.Rect.X0 + r.Rect.W; x++)
                    for (int z = r.Rect.Z0; z < r.Rect.Z0 + r.Rect.H; z++)
                    {
                        var c = new Cell(x, z);
                        held.Add(new KeyValuePair<Cell, BlockKind>(c, w.BlockAt(c)));
                        w.SetBlocked(c, BlockKind.Device);
                    }
            try { return HoseMath.LayAlong(w, Start(r), route ?? new List<Cell>(), end, sp, r.Seed, inward, outward); }
            finally { foreach (var kv in held) w.SetBlocked(kv.Key, kv.Value); }
        }

        internal static ulong CorridorHash(CordWorld w, HoseLay lay) => CorridorHash(lay, c => CordSig.CellSig(w, c));

        internal static ulong CorridorHash(HoseLay lay, Func<Cell, ulong> sig)
        {
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            foreach (V2 p in lay.Flat) { Cell c = p.Floor; x0 = Math.Min(x0, c.X); z0 = Math.Min(z0, c.Z); x1 = Math.Max(x1, c.X); z1 = Math.Max(z1, c.Z); }
            ulong h = 1469598103934665603UL;
            for (int z = z0 - 2; z <= z1 + 2; z++)
                for (int x = x0 - 2; x <= x1 + 2; x++)
                {
                    var c = new Cell(x, z);
                    h = (h ^ sig(c)) * 1099511628211UL;   // B7: tree / water cost included
                }
            return h;
        }

        public static ulong GeometryHash(HoseLay lay)
        {
            ulong h = 1469598103934665603UL;
            if (lay == null) return 0;
            foreach (V2 p in lay.Flat)
            {
                h = (h ^ unchecked((ulong)(long)Math.Round(p.X * 1000))) * 1099511628211UL;
                h = (h ^ unchecked((ulong)(long)Math.Round(p.Z * 1000))) * 1099511628211UL;
            }
            return h;
        }

        // ------------------------------------------------------------------ tick: the state machines
        public override void MapComponentTick()
        {
            if (!RM_HoseEssentials.SaveSkipPatched) return;
            int now = Find.TickManager.TicksGame;
            HoseTuning t = RM_HoseSettings.Tuning();
            // review 2026-10-22: ghosts were pruned only by DrawGhosts (current map, hoses drawn), so a map nobody viewed kept
            // every auto reel-in's point list forever; the tick prunes them too (same rule as the draw)
            if (ghosts.Count > 0 && now % 60 == 0)
            {
                for (int gi = ghosts.Count - 1; gi >= 0; gi--)
                {
                    Ghost g = ghosts[gi];
                    if (HoseLive.AutoDone(now - g.start, g.len) || g.reel?.parent == null || !g.reel.parent.Spawned || g.reel.HoseOut) ghosts.RemoveAt(gi);
                }
            }
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel r = reels[i];
                Watch(r, now);
                // S2, design section 5 b: a carried / wound hose's holder is re-checked every 30 ticks (the RopingTick
                // pattern) so an end is never held by a pawn that stopped holding it
                if ((r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) && (now + r.parent.thingIDNumber) % 30 == 0)
                    r.HolderCheck();
                r.ResolveTint(now);
                // L8 (rev 2 §3.7): a hose holding liquid that no longer carries (switched off, not live, lease run out) empties
                // out of its open end; checked once per pump cycle per reel
                if (r.heldUnits > 0 && (now + r.parent.thingIDNumber) % RimMandrake.FlowWorks.RM_PumpMath.CycleTicks == 3
                    && RimMandrake.FlowWorks.Machinery.RM_HoseHold.ShouldDrain(r.heldUnits, RM_HoseSettings.hoseHoldsLiquid, RimMandrake.FlowWorks.Machinery.RM_HoseLinks.Eligible(r),
                        RimMandrake.FlowWorks.Machinery.RM_LiquidNetKernel.Flowing(r.flowUntil, now)))
                    RimMandrake.FlowWorks.Machinery.RM_LiquidSpill.DrainHeld(r, map, RimMandrake.FlowWorks.Machinery.RM_LiquidSpill.DrainCell(r, map));
                if (!r.laid) continue;
                bool sig = HoseFlow.Signal(r, now, out r.lastProvider);
                r.lastSignal = sig;
                HoseVis before = r.sm.State;
                r.sm.Update(now, sig, t);
                // the tint is how the strand last looked: kept through Draining, forgotten once Flat with no flow
                if (r.sm.State == HoseVis.Flat && !sig && r.tintLiquid != null) { r.tintLiquid = null; r.lastLiquid = null; }
                if (r.sm.State != before)
                {
                    r.history.Add(new KeyValuePair<int, HoseVis>(now, r.sm.State));
                    if (r.history.Count > 64) r.history.RemoveAt(0);
                }
                // an obstacle built or removed across the hose (checked every 250 ticks): HOSE_BLOCKED_REROUTE_RETRACT_1 --
                // re-route if a route within the hose's length remains, else wind it back onto the reel with an alert.
                // A failed lay is never left laid-but-invisible (no ghost hose).
                // GPT source read 2026-10-06 B1: the lay used to be made only by DrawAll (the CURRENT map, on screen), so a hose on
                // a map nobody was viewing was never validated, never retracted, and fed no relay. The tick lays it itself (cached
                // by key: a no-op when nothing changed), so the check below and the relay flow run on every map.
                if ((now + r.parent.thingIDNumber) % 250 == 0) EnsureLay(r);
                // HOSE_OFF_MEND_SLEEPWALKING_RETRACT (C7a-F4): hoses switched off in Mod Settings keep their ends (design: through
                // off/on) -- no obstacle reroute, trail deletion or automatic retraction runs on an invisible hose
                if (RM_HoseSettings.enabled && (now + r.parent.thingIDNumber) % 250 == 0 && r.layKey != null && (r.lay == null || CorridorHashLive(r.lay) != r.corridorHash))
                {
                    // S2, design section 8: a walked hose that an obstacle cut (or that will not lay) falls back to the
                    // planned route from the reel; the walked shape is lost, which is right: the obstacle moved it
                    if (r.trail.Count > 0 && (r.lay == null || !r.TrailWalkable(World())))
                    {
                        r.trail.Clear();
                        r.layKey = null;
                        continue;
                    }
                    string why = HoseMath.CheckReplan(World(), r.Rect, new Cell(r.far.x, r.far.z), r.MaxLength, r.lay == null, r.lastLayReason);
                    if (why != null)
                    {
                        // S4: the cut hose is seen winding back along where it lay (a drawn ghost, no state: the reel is
                        // already Stored, as ruled), not vanishing in one frame
                        if (r.lay != null && r.lay.Flat.Count >= 2)
                            ghosts.Add(new Ghost { reel = r, pts = new List<V2>(r.lay.Flat), start = now, len = Geo.Length(r.lay.Flat) });
                        r.Retract(why); Retracts++; continue;
                    }
                    r.layKey = null;
                }
            }
        }

        // ------------------------------------------------------------------ S4: free-end kind, events, reel art
        private readonly Dictionary<CompHoseReel, HoseCarryState> seenCarry = new Dictionary<CompHoseReel, HoseCarryState>();
        private readonly Dictionary<CompHoseReel, KeyValuePair<int, HoseFreeEnd>> ends = new Dictionary<CompHoseReel, KeyValuePair<int, HoseFreeEnd>>();

        /// <summary>DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 5: a drawbridge leaf moved; every cached free end is read again now
        /// (a hose lying on the leaf disconnects or rejoins without waiting out the 60-tick cache).</summary>
        public void InvalidateEnds()
        {
            ends.Clear();
            RelayVersion++;
        }
        private readonly Dictionary<CompHoseReel, HoseEndKind> placedKind = new Dictionary<CompHoseReel, HoseEndKind>();

        /// <summary>The reel's free end (design section 7), re-read at most every 60 ticks or when the end moved.</summary>
        public HoseFreeEnd FreeEndOf(CompHoseReel r)
        {
            int now = Find.TickManager?.TicksGame ?? 0;
            if (ends.TryGetValue(r, out var kv) && now - kv.Key < 60 && kv.Value.Cell == (r.laid ? r.far : IntVec3.Invalid)) return kv.Value;
            HoseFreeEnd e = HoseEnds.Read(r);
            ends[r] = new KeyValuePair<int, HoseFreeEnd>(now, e);
            return e;
        }

        /// <summary>Per tick: carry-state changes raise HoseEvents (section 10) and reprint the reel's art (the deployed drum
        /// shows from the moment the end leaves the reel, not only once it is laid).</summary>
        private void Watch(CompHoseReel r, int now)
        {
            HoseCarryState was = seenCarry.TryGetValue(r, out HoseCarryState s) ? s : r.carry;
            seenCarry[r] = r.carry;
            bool lying = HoseCarryLoad.IsLaid(r.carry);
            if (was != r.carry)
            {
                if ((was == HoseCarryState.Stored) != (r.carry == HoseCarryState.Stored) && r.parent.Spawned) r.parent.DirtyMapMesh(r.parent.Map);
                if (HoseCarryLoad.IsLaid(was) && r.carry == HoseCarryState.Carrying) { placedKind.Remove(r); HoseEvents.RaiseLifted(r); }
                if (!lying) placedKind.Remove(r);
            }
            if (!lying) return;
            bool look = was != r.carry || !placedKind.ContainsKey(r) || (now + r.parent.thingIDNumber) % 60 == 0;
            if (!look) return;
            HoseFreeEnd e = FreeEndOf(r);
            if (placedKind.TryGetValue(r, out HoseEndKind k) && k == e.Kind && was == r.carry) return;
            placedKind[r] = e.Kind;
            HoseEvents.RaisePlaced(r, e);
        }

        // ------------------------------------------------------------------ draw
        public override void MapComponentUpdate()
        {
            // Kept deliberately (re-review 2026-10-11): staying inert would let Map.ExposeComponents name this class in the save,
            // which is what the save-skip fallback exists to prevent; the cost is one skipped update for the next component, once.
            if (!RM_HoseEssentials.SaveSkipPatched) { UnhookMapEvents(); map.components.Remove(this); }
            if (!RM_HoseEssentials.SaveSkipPatched) return;
            HoseProbe.Service(map, this);
            // HOSE_DRAW_FIX_LEAKS_ONTO_WORLDMAP (owner 2026-10-23: "when I look at the worldmap, the hoses from the tile map show
            // anyway!!!"): Find.CurrentMap stays this map while the planet is shown, so Graphics.DrawMesh here drew over the globe
            if (!RM_HoseSettings.enabled || Find.CurrentMap != map || RimWorld.Planet.WorldRendererUtility.WorldRendered || reels.Count == 0) { FlushFrameMeshes(); return; }
            try { DrawAll(); }
            catch (Exception ex)
            {
                if (!drawErrorLogged) { drawErrorLogged = true; Log.Error("[FlowWorks] hose drawing failed, skipping it: " + ex); }
                FlushFrameMeshes();
            }
        }

        /// <summary>HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES (HoseJointProbe "joints"): the pose a laid hose's meshes were last
        /// built from -- what is on screen, ports and all (EndOnPort) -- or null when it has not been drawn.</summary>
        internal List<V2> DrawnPose(CompHoseReel r) => meshes.TryGetValue(r, out Cached c) ? c.pts : null;

        public struct PoseInfo
        {
            public double Blend, Eased, Visible;
            public int SinceChange;
            public bool Wobbling;
        }

        public static PoseInfo Info(CompHoseReel r)
        {
            int now = Find.TickManager.TicksGame;
            HoseTuning t = RM_HoseSettings.Tuning();
            double b = r.sm.Blend(now, t), e = HoseMath.Ease(b);
            int since = now - r.sm.Since;
            bool wob = RM_HoseSettings.fillWobble && r.sm.Transitions > 0 && HoseMath.WobbleActive(since, t.TransitionTicks);
            return new PoseInfo { Blend = b, Eased = e, Visible = HoseMath.VisibleWidth(e, RM_HoseSettings.plumpAmount), SinceChange = since, Wobbling = wob };
        }

        private void DrawAll()
        {
            float y0 = (float)RimMandrake.Shared.Slack.DrawOrder.Alt(RimMandrake.Shared.Slack.DrawOrder.LayerHose) + RimMandrake.Shared.Slack.DrawOrder.HoseBaseLift;
            lastWrapDraws = lastFeedDraws = lastReelEndHidden = lastRelayCouplings = 0;
            lastCarryDraws = lastClipDraws = lastGhostDraws = lastPortCouplings = 0;
            lastDepthDraws = 0;
            lastPortStubs = 0;
            lastMateJoins = 0;
            lastOverDraws = lastCrossShadowDraws = 0;
            RimMandrake.FlowWorks.Machinery.RM_UnderCouplers.ResetFrame();
            lastFar = Find.CameraDriver.CurrentZoom >= CameraZoomRange.Far;
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel r = reels[i];
                // B18: where hoses cross, one passes cleanly over the other, the same way every frame: each hose (and its
                // fittings) sits in its own altitude band, ordered by when the reel was built
                int rank = RankOf(r);
                float y = y0 + HoseMath.CrossLift(rank);
                if (drawnFittings.TryGetValue(r, out Dictionary<string, DrawnFitting> df)) df.Clear();   // this frame's record only
                DrawFeed(r, y0);
                // S4 (design section 6): a carried hose is drawn live along the walked trail to the carrier's hand
                if (r.carry == HoseCarryState.Carrying && r.trail.Count > 0) { DrawCarrying(r, y, lastFar); continue; }
                if (carryCache.Count > 0) DropCarryCache(r);
                HoseLay lay = EnsureLay(r);
                if (lay == null) { lastDraw[r] = "none"; continue; }
                PoseInfo pi = Info(r);
                double amt = RM_HoseSettings.plumpAmount;
                int T = RM_HoseSettings.Tuning().TransitionTicks;
                bool settled = !pi.Wobbling && (pi.Blend <= 0 || pi.Blend >= 1);
                // a transitioning pose depends only on the game tick, so it is cached per tick (a paused game stops re-meshing every frame)
                string key = (settled ? (pi.Blend >= 1 ? "P" : "F") : "T" + Find.TickManager.TicksGame) + r.layKey + "@" + RankOf(r);
                // HOSE_ENDS_FIX_MISSES_THE_PORTS: an end coupled to a tank's drawn port bends onto it (TankPortGeometry), so the
                // coupling DrawEnds puts half a cell past the end sits on the flange, not half a cell beside it
                V2 portAt = default(V2), portAxis = default(V2);
                bool onPort = r.laid && r.carry != HoseCarryState.Retracting && PortEnd(r, out portAt, out portAxis);
                if (onPort) key += "|p" + portAt.X.ToString("0.000") + "," + portAt.Z.ToString("0.000");
                // HOSE_SPLICE_BUILD_MATES_BY_SLOPE: an open end lying on another hose's open end couples to it face to face
                MateInfo mi = onPort ? null : MateFor(r);
                if (mi != null) key += "|m" + mi.key;
                // review 2026-10-22: the key is built first, so a cache hit reuses the pose its meshes were built from
                meshes.TryGetValue(r, out Cached c);
                List<V2> pts;
                if (r.carry != HoseCarryState.Retracting && c != null && c.pts != null && c.key == key) pts = c.pts;
                else
                {
                    // HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: one entry point (HoseMath.DrawnPose) for the pose and its port end, so the
                    // offline selftest (HoseCurveChecks) measures exactly what is drawn here. It stays inside this update, behind the
                    // world-map guard above (HOSE_DRAW_FIX_LEAKS_ONTO_WORLDMAP).
                    pts = HoseMath.DrawnPose(lay, pi.Eased, pi.Wobbling ? pi.SinceChange : int.MaxValue / 2, T, amt, onPort ? portAt : (V2?)null, portAxis);
                    if (mi != null) pts = Mated(r, mi, pts);
                }
                // rule 3: a joiner that would sit over a hose drawn beneath is left out (HoseMath.Layer)
                List<int> joints = Layered().Joints.TryGetValue(r.parent.thingIDNumber, out List<int> kept) ? kept : lay.Joints;
                // a mated end's re-shaped run carries no mid-hose joiner (its samples are new)
                if (mi != null && mateKept.TryGetValue(r, out int keptN)) joints = joints.FindAll(j => j < keptN - 2);
                // S4: winding in, the laid pose is cut at the wound fraction (rebuilt per frame only while winding)
                if (r.carry == HoseCarryState.Retracting)
                {
                    pts = HoseLive.ClipWound(pts, r.wound, TotalOf(r));
                    joints = HoseLive.JointsWithin(joints, pts.Count);
                    key = null;
                    lastClipDraws++;
                    lastDraw[r] = "clip";
                }
                else lastDraw[r] = "lay";
                lastDrawnLen[r] = Geo.Length(pts);
                float vis = (float)pi.Visible;
                float e = (float)pi.Eased;
                Mesh fm, pm, sm;
                if (c != null && key != null && c.key == key) { fm = c.flat; pm = c.plump; sm = c.shadow; }
                else
                {
                    // 2026-10-05: on a nozzled reel the strand starts inside the outlet coupling's wrap, not under the pump, so
                    // no bare hose shows alongside the coupling between the wrap and the nozzle
                    List<V2> rp = HoseMath.TrimStart(pts, OutletTrim(r, vis));
                    fm = e < 0.999f ? Ribbon(rp, (float)HoseMath.MeshWidthFlat(vis), y, 0.37) : null;
                    pm = e > 0.001f ? Ribbon(rp, (float)HoseMath.MeshWidthPlump(vis), y + 0.0004f, 0.37) : null;
                    var off = new V2(0.03 + 0.05 * e, -(0.03 + 0.06 * e));
                    var sp = new List<V2>(rp.Count);
                    foreach (V2 p in rp) sp.Add(p + off);
                    sm = Ribbon(sp, vis * (float)HoseMath.ShadowWidth(e), y - 0.0004f, 0.11);
                    if (key != null)
                    {
                        if (c != null) { DestroyMeshes(c); }
                        meshes[r] = new Cached { key = key, flat = fm, plump = pm, shadow = sm, pts = pts, rp = rp };
                    }
                    else { frameMeshes.Add(fm); frameMeshes.Add(pm); frameMeshes.Add(sm); }
                }
                Color tint = Tint(r);
                HoseLookMats hm = HoseMaterials.For(r);      // stage 3: the hose draws in its REEL's look
                if (sm != null) Graphics.DrawMesh(sm, Matrix4x4.identity, HoseMaterials.Shadow((float)HoseMath.ShadowAlpha(e)), 0);
                // depth pre-pass of the dominant pose only (a fading pose must stay see-through), so wall sun shadows skip the hose
                if (pm != null && (fm == null || e >= 0.5f)) DepthPass(pm, Matrix4x4.identity, hm.Plump(1f, tint));
                else if (fm != null) DepthPass(fm, Matrix4x4.identity, hm.Flat(1f));
                if (fm != null) Graphics.DrawMesh(fm, Matrix4x4.identity, hm.Flat(1f - e), 0);
                if (pm != null) Graphics.DrawMesh(pm, Matrix4x4.identity, hm.Plump(e, tint), 0);
                // a settled or per-tick cached pose (not one winding in, rebuilt per frame): its stretches over walk-over
                // buildings are redrawn above them, and where it passes over a hose drawn beneath it casts a crossing shadow
                if (key != null && meshes.TryGetValue(r, out Cached cur) && cur.key == key)
                {
                    DrawOverBuildings(cur, hm, tint, vis, e, rank);
                    DrawCrossShadow(r, cur, vis, e, y, rank);
                }
                DrawEnds(r, hm, joints, pts, vis, y + 0.001f, true);
            }
            DrawGhosts(y0);
            // a winding hose's, a carried tail's and a ghost's meshes live one frame (a transitioning pose is cached per tick)
            for (int k = 0; k < oldFrame.Count; k++) if (oldFrame[k] != null) UnityEngine.Object.Destroy(oldFrame[k]);
            oldFrame.Clear();
            oldFrame.AddRange(frameMeshes);
            frameMeshes.Clear();
        }

        // early exits and exceptions skip DrawAll's tail: destroy whatever transitioning meshes are pending
        private void FlushFrameMeshes()
        {
            if (frameMeshes.Count == 0 && oldFrame.Count == 0) return;
            for (int k = 0; k < oldFrame.Count; k++) if (oldFrame[k] != null) UnityEngine.Object.Destroy(oldFrame[k]);
            for (int k = 0; k < frameMeshes.Count; k++) if (frameMeshes[k] != null) UnityEngine.Object.Destroy(frameMeshes[k]);
            oldFrame.Clear(); frameMeshes.Clear();
        }

        private readonly List<Mesh> frameMeshes = new List<Mesh>(), oldFrame = new List<Mesh>();

        private void DropMeshes(CompHoseReel r)
        {
            if (meshes.TryGetValue(r, out Cached c)) { DestroyMeshes(c); meshes.Remove(r); }
            if (stubMeshes.TryGetValue(r, out StubCache sc)) { if (sc.mesh != null) UnityEngine.Object.Destroy(sc.mesh); stubMeshes.Remove(r); }
        }

        private static void DestroyMeshes(Cached c)
        {
            if (c.flat != null) UnityEngine.Object.Destroy(c.flat);
            if (c.plump != null) UnityEngine.Object.Destroy(c.plump);
            if (c.shadow != null) UnityEngine.Object.Destroy(c.shadow);
            DestroyOver(c);
            if (c.crossShadow != null) UnityEngine.Object.Destroy(c.crossShadow);
            c.crossShadow = null;
        }

        private static void DestroyOver(Cached c)
        {
            foreach (Mesh m in c.overMeshes) if (m != null) UnityEngine.Object.Destroy(m);
            c.overMeshes.Clear();
        }

        /// <summary>
        /// HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK (audit F2/D2, owner 2026-10-22: "the hose is going under the battery and
        /// wall"). The hose band sits just above the Shadows layer, so a hose across a battery, a power connector or sandbags
        /// was painted under the building's sprite. Its route now avoids such buildings (CostsAsBuilding); where it still must
        /// cross one, the stretch over that building's cells (HoseOverDraw.Spans, widened by BuildingMargin for the sprite's
        /// overhang) is drawn again -- shadow, flat and plump strands, same materials and texture phase -- in the hose's own
        /// crossing band on <see cref="HoseOverDraw.OverBuildingLayer"/> (BuildingOnTop): over the building, under items and pawns.
        /// Rebuilt only when the pose or the map's buildings change. The spans are recorded for the joint probe.
        /// </summary>
        private void DrawOverBuildings(Cached c, HoseLookMats hm, Color tint, float vis, float e, int rank)
        {
            if (c.rp == null || c.rp.Count < 2) return;
            string ok = c.key + "#" + mapVersion;
            if (c.overKey != ok)
            {
                DestroyOver(c);
                c.overKey = ok;
                c.overSpans = HoseOverDraw.Spans(c.rp, OverBuildingCell, HoseOverDraw.BuildingMargin);
                float yo = (float)(RimMandrake.Shared.Slack.DrawOrder.Alt(HoseOverDraw.OverBuildingLayer) + RimMandrake.Shared.Slack.DrawOrder.HoseBaseLift) + HoseMath.CrossLift(rank);
                float wf = (float)HoseMath.MeshWidthFlat(vis), wp = (float)HoseMath.MeshWidthPlump(vis), ws = vis * (float)HoseMath.ShadowWidth(e);
                var off = new V2(0.03 + 0.05 * e, -(0.03 + 0.06 * e));
                foreach (double[] sp in c.overSpans)
                {
                    List<V2> part = HoseOverDraw.Slice(c.rp, sp[0], sp[1]);
                    if (part.Count < 2) continue;
                    var sh = new List<V2>(part.Count);
                    foreach (V2 p in part) sh.Add(p + off);
                    // the texture phase carries on from the main strand (Ribbon: u = 4 s0 + arc / (4 width))
                    c.overMeshes.Add(Ribbon(sh, ws, yo - 0.0004f, 0.11 + sp[0] / (16.0 * ws)));
                    c.overMeshes.Add(e < 0.999f ? Ribbon(part, wf, yo, 0.37 + sp[0] / (16.0 * wf)) : null);
                    c.overMeshes.Add(e > 0.001f ? Ribbon(part, wp, yo + 0.0004f, 0.37 + sp[0] / (16.0 * wp)) : null);
                }
                OverBuilds++;
            }
            for (int i = 0; i + 2 < c.overMeshes.Count; i += 3)
            {
                if (c.overMeshes[i] != null) Graphics.DrawMesh(c.overMeshes[i], Matrix4x4.identity, HoseMaterials.Shadow((float)HoseMath.ShadowAlpha(e)), 0);
                if (c.overMeshes[i + 1] != null) Graphics.DrawMesh(c.overMeshes[i + 1], Matrix4x4.identity, hm.Flat(1f - e), 0);
                if (c.overMeshes[i + 2] != null) Graphics.DrawMesh(c.overMeshes[i + 2], Matrix4x4.identity, hm.Plump(e, tint), 0);
                lastOverDraws++;
            }
        }

        /// <summary>
        /// HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE (audit F8/D11: two laid hoses "cross flat, one painted over the other with no lift
        /// or shadow"). The upper hose of a crossing (B18 bands: it already draws over) casts a deeper shadow onto the hose
        /// beneath, offset further than its ground shadow, over the stretch where the two ribbons overlap (HoseOverDraw.CrossSpans
        /// against every lower-ranked hose's drawn strand) -- it reads as lifted over the other. Drawn at the upper hose's
        /// shadow step, which is above every band beneath it. Rebuilt when this pose or a lower hose's pose changes; the spans
        /// are recorded for the joint probe.
        /// </summary>
        private void DrawCrossShadow(CompHoseReel r, Cached c, float vis, float e, float y, int rank)
        {
            if (c.rp == null || c.rp.Count < 2) return;
            int h = c.key.GetHashCode();
            List<IList<V2>> lowers = null;
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel o = reels[i];
                if (o == r || !meshes.TryGetValue(o, out Cached oc) || oc.rp == null || RankOf(o) >= rank) continue;
                h = h * 31 + oc.key.GetHashCode();
                (lowers ?? (lowers = new List<IList<V2>>())).Add(oc.rp);
            }
            string ck = h.ToString();
            if (c.crossKey != ck)
            {
                c.crossKey = ck;
                if (c.crossShadow != null) UnityEngine.Object.Destroy(c.crossShadow);
                c.crossShadow = null;
                c.crossSpans = lowers == null ? new List<double[]>() : HoseOverDraw.CrossSpans(c.rp, lowers, vis, CrossShadowMargin);
                if (c.crossSpans.Count > 0)
                {
                    var off = new V2(CrossShadowOffset + 0.04 * e, -(CrossShadowOffset + 0.04 * e));
                    var all = new List<Vector3>();
                    var tris = new List<int>();
                    var uvs = new List<Vector2>();
                    foreach (double[] sp in c.crossSpans)
                    {
                        List<V2> part = HoseOverDraw.Slice(c.rp, sp[0], sp[1]);
                        if (part.Count < 2) continue;
                        var sh = new List<V2>(part.Count);
                        foreach (V2 p in part) sh.Add(p + off);
                        Mesh m = Ribbon(sh, vis * (float)HoseMath.ShadowWidth(e) * CrossShadowWiden, y - 0.0004f, 0.11);
                        if (m == null) continue;
                        int b = all.Count;
                        all.AddRange(m.vertices);
                        uvs.AddRange(m.uv);
                        foreach (int t in m.triangles) tris.Add(b + t);
                        UnityEngine.Object.Destroy(m);
                    }
                    if (tris.Count > 0)
                    {
                        c.crossShadow = new Mesh { name = "RM_HoseCrossShadow" };
                        c.crossShadow.SetVertices(all);
                        c.crossShadow.SetUVs(0, uvs);
                        c.crossShadow.SetTriangles(tris, 0);
                        c.crossShadow.RecalculateBounds();
                    }
                }
                CrossBuilds++;
            }
            if (c.crossShadow == null) return;
            Graphics.DrawMesh(c.crossShadow, Matrix4x4.identity, HoseMaterials.Shadow((float)HoseMath.ShadowAlpha(1)), 0);
            lastCrossShadowDraws++;
        }

        /// <summary>The crossing shadow: offset (cells, +x / -z, plus 0.04 when plump), widening over the ground shadow, and how
        /// far it runs past the overlap at each end.</summary>
        public const double CrossShadowOffset = 0.10, CrossShadowMargin = 0.25;
        public const float CrossShadowWiden = 1.15f;

        /// <summary>State reads: over-building / crossing-shadow draws last frame, and rebuilds since load.</summary>
        public int lastOverDraws, lastCrossShadowDraws;
        public static int OverBuilds, CrossBuilds;

        public static Color Tint(CompHoseReel r)
        {
            if (!RM_HoseSettings.tintByContents) return Color.white;
            // hose port step 6 (FINAL §3.4): the colour of the liquid the hose carries (LiquidDef.color, the registry's own),
            // or fresh water's for a hose plumped only by the dev flag; null-safe
            var liquid = r?.tintLiquid ?? RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater;
            Color fluid = liquid != null ? liquid.color : new Color(0.62f, 0.80f, 0.98f);
            // wet darkening by 15%, faintly coloured by what it carries (design 3.4)
            return Color.Lerp(Color.white, fluid, 0.25f) * 0.85f + new Color(0, 0, 0, 0.15f);
        }

        // Art geometry (128 px canvases, measured 2026-10-02): the hose band in the coupling/nozzle/cap art is ~40
        // px tall (0.31 canvas); the coupling's brass face is at +0.46 canvas along +X, the nozzle tip at +0.47,
        // the cap face at +0.29; the hose enters every piece from the canvas's -X edge.
        /// <summary>RE-MEASURED 2026-10-04 (owner review B8, "mismatched hose width"): the opaque hose band where the hose
        /// enters Coupling_Brass/EndCap is 32 px of 128 (0.25), not the 0.31 first assumed, so every fitting was drawn ~20%
        /// narrower than the hose. validation.py O6 re-measures these from the PNGs.</summary>
        public const float PieceBand = (float)HoseMath.PieceBand;
        /// <summary>The coupling's brass face, canvas units along +X (measured 2026-10-02: 0.46).</summary>
        public const double JoinerFace = HoseMath.JoinerFace, JoinerMesh = HoseMath.JoinerMesh;
        /// <summary>Widest opaque band of each fitting (canvas fraction of 128 px; measured 2026-10-04, validation.py O6
        /// re-measures): Coupling_Brass 65, Nozzle 48, EndCap 44.</summary>
        public const float CouplingMax = (float)HoseMath.CouplingMax, NozzleMax = 0.375f, EndCapMax = 0.344f;
        /// <summary>Binding.png (make_hose_binding.py, 82x40, wrap along +X): the wrap's widest band, 38 px of 40.</summary>
        public const float BindBand = 0.95f;
        /// <summary>The coupling at a tank/machine port is drawn this much larger than a mid-hose one. Was 1.5 (a reducer collar to
        /// meet the old ~0.3-cell port flanges); PUMP_COUPLING_SHRINK_STILL_SIZED_FOR_GIANTS (owner 2026-10-23: "connectors that
        /// match the more modern pipe and hose sizes"): every port flange is now <= 0.23 cell, so a plain 0.22 coupling meets it
        /// (selftest_hose_fittings.py caps the port coupling at 0.25).</summary>
        public const float PortCouplingWiden = 1f;

        private int RankOf(CompHoseReel r)
        {
            // MESSYCONDUIT_CABLE_PILE_LOOK_1 rule 3: reel-age order (B18), except a hose whose end fitting rests on another
            // hose draws beneath it (HoseMath.Layer)
            if (Layered().Rank.TryGetValue(r.parent.thingIDNumber, out int rank)) return rank;
            int k = 0;
            foreach (CompHoseReel o in reels) if (o.parent.thingIDNumber < r.parent.thingIDNumber) k++;
            return k;
        }

        private HoseMath.Layering layering;
        private string layeringKey;
        private int layeringFrame = -1;

        /// <summary>The crossing order and drawn joiners of every reel's hose, rebuilt only when a lay or the plump setting
        /// changes (the key holds every reel's id and layKey).</summary>
        private HoseMath.Layering Layered()
        {
            // the key is rebuilt at most once a frame (RankOf runs per reel per draw)
            if (layering != null && layeringFrame == Time.frameCount) return layering;
            layeringFrame = Time.frameCount;
            var sb = new System.Text.StringBuilder();
            foreach (CompHoseReel r in reels) sb.Append(r.parent.thingIDNumber).Append(':').Append(r.lay != null ? r.layKey : "-").Append('|');
            sb.Append(RM_HoseSettings.plumpAmount);
            string key = sb.ToString();
            if (layering != null && key == layeringKey) return layering;
            var hs = new List<HoseMath.LayeredHose>(reels.Count);
            foreach (CompHoseReel r in reels) hs.Add(new HoseMath.LayeredHose { Id = r.parent.thingIDNumber, Lay = r.lay ?? new HoseLay() });
            layering = HoseMath.Layer(hs, HoseMath.VisibleWidth(1, RM_HoseSettings.plumpAmount));
            layeringKey = key;
            return layering;
        }

        /// <summary>Rule 3 read live (probe): fittings drawing over another hose's body under the current layering.</summary>
        public int FittingsOnTopNow()
        {
            HoseMath.Layering L = Layered();
            var hs = new List<HoseMath.LayeredHose>(reels.Count);
            foreach (CompHoseReel r in reels) hs.Add(new HoseMath.LayeredHose { Id = r.parent.thingIDNumber, Lay = r.lay ?? new HoseLay() });
            return HoseMath.FittingsOnTop(hs, L.Rank, L.Joints, HoseMath.VisibleWidth(1, RM_HoseSettings.plumpAmount)).Count;
        }

        /// <summary>Both ends of every hose and both halves of every joiner (B22): a cloth binding wrap ~1.4 x the hose
        /// wide and 0.6 cell long covers the hose-to-fitting transition, then the fitting (sized never to read wider than
        /// the wrap) or, at an open free end, an edge-on lip (HoseMath.OpenEndLip). The wrap is drawn over the fitting's hose stub.</summary>
        private void DrawEnds(CompHoseReel r, HoseLookMats hm, IList<int> joints, List<V2> pts, float vis, float y, bool lying)
        {
            int n = pts.Count;
            Color wrapTint = Color.Lerp(Color.white, Tint(r), 0.5f);
            if (HoseStyles.AgedClothWrap(hm.look)) wrapTint *= new Color(0.86f, 0.80f, 0.70f, 1f);   // aged cloth, not white (Scrapper only)
            // reel end: a 1x1 reel's hose ends in a brass coupling whose face meets the reel, pointing into it. Round 5: the
            // 2x2 reel's hose runs on to the drum's axis under the opaque drum (HoseReelRect.Mouth), so nothing is drawn
            // there -- a coupling's body would reach back out past the drum into the gap above the base rail
            V2 d0 = (pts[0] - pts[Math.Min(3, n - 1)]).Norm();
            // the 2x2 reel: the coupling's face meets the brass outlet nozzle, pointing into it (against Outward: the reel turns)
            // 2026-10-05: only when the hose really leaves through the outlet; a hose that could not (a reel boxed in, a relay
            // reel whose nozzle takes the feeding hose, a carried hose) gets no coupling floating on an empty nozzle
            // REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH: drawn above the reel sprite where its nozzle is in view (HoseJoints.NozzleFittingOnTop)
            if (r.Rect.HasNozzle) { if (lying && r.lay != null && r.lay.Outlet) { V2 seat = HoseJoints.NozzleCoupling(r.Rect, out V2 inw); Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, seat, inw, vis, HoseJoints.NozzleFittingOnTop(r.Rect.Rot) ? NozzleTopY(y) : y, wrapTint, rec: r, role: "reel_end"); } }
            else Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[0], d0, vis, y, wrapTint);
            // joiners: only at real bends (B17), each two couplings face to face, screwed together (B9). Pose samples share
            // the lay's sample indices (equal-arc resamples of the same count).
            // round 4: the lay drew the hose dead straight over each joiner's run (HoseMath.StraightenAt), so the joiner's
            // axis is that run's chord, not the tangent at one sample
            double step = n > 1 ? Geo.Length(pts) / (n - 1) : 1;
            int m = Math.Max(1, (int)Math.Round(0.8 * HoseMath.JoinerHalf(vis) / Math.Max(1e-6, step)));
            foreach (int j0 in joints)
            {
                int j = Math.Min(n - 2, Math.Max(1, j0));
                V2 d = (pts[Math.Min(n - 1, j + m)] - pts[Math.Max(0, j - m)]).Norm();
                // 2026-10-05: each half's wrap runs up to the interlocked claws (HoseMath.JoinerWrapIn), no gap
                float js = (float)HoseMath.FittingSize(vis, PieceBand, CouplingMax);
                for (int half = 0; half < 2; half++)   // both halves, no per-joint array (review 2026-10-22: this runs every frame)
                {
                    V2 h = half == 0 ? d : -d;
                    Piece(hm.CouplingBare, pts[j] - h * (JoinerMesh * js), h, js, y);
                    Wrap(hm, pts[j] - h * (HoseMath.JoinerWrapIn * js + HoseMath.WrapLength / 2), h, vis, y + 0.0002f, wrapTint);
                }
            }
            // free end: open (default), nozzle or cap, pointing out along the hose
            V2 d1 = (pts[n - 1] - pts[Math.Max(0, n - 4)]).Norm();
            // S4 (section 7): a lying end beside a pipe or tank (any faction) couples to it, a brass coupling facing the port
            HoseFreeEnd fe = lying && r.laid && r.carry != HoseCarryState.Retracting ? FreeEndOf(r) : default(HoseFreeEnd);
            if (lying && r.carry != HoseCarryState.Retracting && mateKept.ContainsKey(r) && MateFor(r) != null)
            {
                // HOSE_SPLICE_BUILD_MATES_BY_SLOPE: two open ends coupled face to face draw ONE joiner, each hose its half (as a
                // mid-hose joiner, HoseMath.JoinerMesh), on the straight run HoseSpliceMath laid along the coupling axis
                float js = (float)HoseMath.FittingSize(vis, PieceBand, CouplingMax);
                V2 e = pts[n - 1];
                Piece(hm.CouplingBare, e - d1 * (JoinerMesh * js), d1, js, y);
                Wrap(hm, e - d1 * (HoseMath.JoinerWrapIn * js + HoseMath.WrapLength / 2), d1, vis, y + 0.0002f, wrapTint);
                lastMateJoins++;
            }
            else if (fe.Kind == HoseEndKind.Port)
            {
                V2 dp = fe.PortSide.X == 0 && fe.PortSide.Z == 0 ? d1 : new V2(fe.PortSide.X, fe.PortSide.Z);
                float widen = fe.PortKind == HosePortKind.Tank || fe.PortKind == HosePortKind.Machine ? PortCouplingWiden : 1f;
                // HOSE_LEADIN_FIX_STUB_IN_THE_CANAL: met from the side, the coupling is an elbow with no lead-in past the hose
                double size0 = HoseMath.FittingSize(vis, PieceBand, CouplingMax), portSize = size0 * widen;
                HoseMath.PortFitting(pts, pts[n - 1] + dp * 0.5, dp, ref portSize, vis, out V2 portFace, out double portWrap);
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, portFace, dp, vis, y, wrapTint, (float)(portSize / size0), portWrap, r, "port_end");
                // HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY: the pipe's own fitting under the coupling (saddle on it, flange beside it)
                RimMandrake.FlowWorks.Machinery.RM_LiquidJoins.DrawHosePortFitting(fe.Port, fe.PortSide.X, fe.PortSide.Z, y - 0.0006f);
                // HOSE UNDER-COUPLERS (owner ruling 2026-10-23: "have their art go UNDER the tank or pump or other fixture"): a
                // collar on the port point and a pipe on beneath the fixture to its centre line, in the hose band (under the
                // building layer); it replaces the hose's own stub ribbon there. A pipe port keeps the stub path.
                V2 portAtEdge = pts[n - 1] + dp * 0.5;
                if (!RimMandrake.FlowWorks.Machinery.RM_UnderCouplers.Draw(fe.Port, portAtEdge.X, portAtEdge.Z, fe.PortSide.X, fe.PortSide.Z, y - 0.001f))
                    DrawPortStub(r, fe, hm, vis, y - 0.001f);
                lastPortCouplings++;
            }
            else if (lying && r.carry != HoseCarryState.Retracting && RelayOf(r) != null)
            {
                // round 6: a hose feeding a relay reel ends in a brass coupling pointing into the relay. Round 7 (owner,
                // station 42: "pipe does NOT hook up properly to the next reel station"): its face sits ON the drawn reel
                // (the west brass inlet face to face, or the outline on the other sides; HoseRelay.DrawnEnd) and its axis
                // is the intake's, not the hose's last bend. Drawn in the hose band, under the reel sprite, so the reel's
                // own inlet overlaps the joint, never the other way round.
                EndPoint(r, out CompHoseReel relayR, out V2? inward);
                V2 dIn = inward ?? d1;
                // REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH: on the relay's nozzle it mates over the drawn tip (HoseJoints.RelayFittingOnTop)
                bool onTop = relayR != null && HoseJoints.RelayFittingOnTop(relayR.Rect, new Cell(r.EndCell.x, r.EndCell.z));
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[n - 1], dIn, vis, onTop ? NozzleTopY(y) : y, wrapTint, rec: r, role: "relay_end");
                lastRelayCouplings++;
            }
            else if (r.end == HoseEnd.Nozzle) Fitting(hm, hm.NozzleBare, NozzleMax, 0.05, -0.16, pts[n - 1], d1, vis, y, wrapTint);
            else if (r.end == HoseEnd.EndCap) Fitting(hm, hm.EndCapBare, EndCapMax, -0.10, -0.15, pts[n - 1], d1, vis, y, wrapTint);
            else
            {
                V2 e = pts[n - 1];
                // the wrap runs right to the cut (it hides the hose's square end); HOSE_MOUTH_FIX_FACE_ON_DISC (art brief C6): the
                // hose lies flat, so its opening faces along the ground and the Mouth piece is drawn edge-on, a lip line on the
                // wrap's outer face (HoseMath.OpenEndLip), never the squashed face-on disc that read as the end bent up
                Wrap(hm, e - d1 * (HoseMath.WrapLength / 2 - HoseMath.WrapOverCut), d1, vis, y + 0.0002f, wrapTint);
                HoseMath.OpenEndLip(vis, out double lipAlong, out double lipAcross, out double lipBack);
                PieceXZ(hm.Mouth, e - d1 * lipBack, d1, (float)lipAlong, (float)lipAcross, y + 0.0003f, Color.white);
            }
        }

        /// <summary>HOSE_ENDS_FIX_MISSES_THE_PORTS: the drawn port the reel's laid free end couples to (a 2x2 universal tank's
        /// west/east flange, or a lane moved onto the drawn body: TankPortGeometry.HosePort) and the axis into it; false = the shared
        /// edge's midpoint, as before.</summary>
        internal bool PortEnd(CompHoseReel r, out V2 port, out V2 axis)
        {
            port = axis = default(V2);
            HoseFreeEnd fe = FreeEndOf(r);
            if (fe.Kind != HoseEndKind.Port || fe.PortKind != HosePortKind.Tank || fe.Port == null || !fe.Port.Spawned) return false;
            CellRect rect = fe.Port.OccupiedRect();
            // RM_LiquidTank's measured flange, or a lane moved onto the drawn body (OFF_BODY_PORTS, TankPortGeometry.MovedAlong)
            if (!TankPortGeometry.HosePort(fe.Port.def.defName, RimMandrake.FlowWorks.Machinery.PipeLook.LookOfThing(fe.Port), rect.minX, rect.minZ, rect.Width, rect.Height,
                    fe.Cell.x, fe.Cell.z, fe.PortSide.X, fe.PortSide.Z, out port)) return false;
            axis = new V2(fe.PortSide.X, fe.PortSide.Z);
            return true;
        }

        /// <summary>
        /// PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (owner 2026-10-18: "draw pipes as though they are connected into the centers of all
        /// pipe-receiving items ... so that it appears to continue beneath them through any transparent boundaries"): a hose
        /// coupled to a tank or liquid machine beside its end runs on from the shared edge to the centre of the building's
        /// footprint (LiquidJoinRule.CentreStub), in the hose band -- below the building layer, so the building's opaque body
        /// hides it and its see-through margins show it. Pipes are the section layer's (SectionLayer_RM_PipeCentreStubs).
        /// </summary>
        private void DrawPortStub(CompHoseReel r, HoseFreeEnd fe, HoseLookMats hm, float vis, float y)
        {
            if (!RimMandrake.FlowWorks.Machinery.RM_MachinerySettings.pipesUnderToCentre) return;
            if (fe.Port == null || !fe.Port.Spawned || (fe.PortKind != HosePortKind.Tank && fe.PortKind != HosePortKind.Machine)) return;
            int sx = fe.PortSide.X, sz = fe.PortSide.Z;
            if (Math.Abs(sx) + Math.Abs(sz) != 1) return;
            CellRect rect = fe.Port.OccupiedRect();
            PoseInfo pi = Info(r);
            bool plump = pi.Eased >= 0.5;
            float w = plump ? (float)HoseMath.MeshWidthPlump(vis) : (float)HoseMath.MeshWidthFlat(vis);
            stubMeshes.TryGetValue(r, out StubCache sc);
            if (sc == null || sc.cell != fe.Cell || sc.sx != sx || sc.sz != sz || sc.rect != rect || sc.w != w || sc.y != y)
            {
                // a hose on a tank's drawn port runs on from the flange straight to the centre (it is on the centre line)
                double[] poly = PortEnd(r, out V2 pa, out _)
                    ? new[] { pa.X, pa.Z, rect.minX + rect.Width / 2.0, rect.minZ + rect.Height / 2.0 }
                    : RimMandrake.FlowWorks.Machinery.LiquidJoinRule.CentreStub(fe.Cell.x, fe.Cell.z, sx, sz, rect.minX, rect.minZ, rect.Width, rect.Height);
                if (sc == null) stubMeshes[r] = sc = new StubCache();
                if (sc.mesh != null) UnityEngine.Object.Destroy(sc.mesh);
                sc.mesh = null;
                if (poly != null)
                {
                    var pts = new List<V2>(poly.Length / 2);
                    for (int i = 0; i + 1 < poly.Length; i += 2) pts.Add(new V2(poly[i], poly[i + 1]));
                    sc.mesh = Ribbon(pts, w, y, 0.37);
                    portStubBuilds++;
                }
                sc.cell = fe.Cell; sc.sx = sx; sc.sz = sz; sc.rect = rect; sc.w = w; sc.y = y;
            }
            if (sc.mesh == null) return;
            Graphics.DrawMesh(sc.mesh, Matrix4x4.identity, plump ? hm.Plump(1f, Tint(r)) : hm.Flat(1f), 0);
            lastPortStubs++;
        }

        public int lastWrapDraws, lastFeedDraws, lastReelEndHidden, lastRelayCouplings;

        // ------------------------------------------------------------------ S4: live drawing (design section 6)
        /// <summary>State reads for the probe: how each reel's hose was drawn last frame (none / lay / carry / clip), its drawn
        /// length (cells), the carried hose's hand point, and per-frame counts.</summary>
        public readonly Dictionary<CompHoseReel, string> lastDraw = new Dictionary<CompHoseReel, string>();
        public readonly Dictionary<CompHoseReel, double> lastDrawnLen = new Dictionary<CompHoseReel, double>();
        internal readonly Dictionary<CompHoseReel, V2> lastHand = new Dictionary<CompHoseReel, V2>();
        public int lastCarryDraws, lastClipDraws, lastGhostDraws, lastPortCouplings, carryPrefixBuilds;

        // ------------------------------------------------------------------ HOSE_SPLICE_BUILD_MATES_BY_SLOPE
        /// <summary>A coupled pair: A = the lower thing id; the solve (axis, coupling point, each end's cached seed) and its key
        /// (both lays' keys, the stiffness and the girth), so a pair is solved once per layout.</summary>
        private sealed class MateInfo
        {
            public string key;
            public CompHoseReel A, B;
            public HoseSpliceMath.Mate mate;
        }
        private readonly Dictionary<CompHoseReel, MateInfo> mateOf = new Dictionary<CompHoseReel, MateInfo>();
        private readonly Dictionary<string, MateInfo> mateSolved = new Dictionary<string, MateInfo>();
        /// <summary>Per mated hose: how many leading samples of its drawn pose are the laid hose's own (joiners past it are dropped).</summary>
        private readonly Dictionary<CompHoseReel, int> mateKept = new Dictionary<CompHoseReel, int>();
        private int mateFrame = -1;
        /// <summary>Probe counters: joiner halves drawn last frame, pair solves (layout changes) this session.</summary>
        public int lastMateJoins, mateSolves;

        /// <summary>An end that can couple to another hose's end: laid and lying (not carried or winding in), an OPEN end (a
        /// nozzle or cap has no coupling), not already coupled to a relay reel or a port.</summary>
        private bool MateCandidate(CompHoseReel r)
        {
            if (r == null || !r.laid || r.lay == null || r.end != HoseEnd.Open) return false;
            if (r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) return false;
            HoseEndKind k = FreeEndOf(r).Kind;
            return k == HoseEndKind.Free || k == HoseEndKind.Water;
        }

        /// <summary>The pairs, re-read once per frame: two candidate ends on the same or 8-adjacent cells couple; each hose
        /// couples once, to the lowest-id partner in reach (A = the lower id).</summary>
        private void RefreshMates()
        {
            if (mateFrame == Time.frameCount) return;
            mateFrame = Time.frameCount;
            mateOf.Clear();
            var cands = new List<CompHoseReel>();
            foreach (CompHoseReel r in reels) if (MateCandidate(r)) cands.Add(r);
            if (cands.Count < 2) { mateKept.Clear(); return; }
            cands.Sort((a, b) => a.parent.thingIDNumber.CompareTo(b.parent.thingIDNumber));
            float vis = (float)HoseMath.VisibleWidth(1, RM_HoseSettings.plumpAmount);
            double kmax = 1 / Math.Max(0.45, RM_HoseSettings.Shape().MinBendRadius);
            for (int i = 0; i < cands.Count; i++)
            {
                CompHoseReel a = cands[i];
                if (mateOf.ContainsKey(a)) continue;
                for (int j = i + 1; j < cands.Count; j++)
                {
                    CompHoseReel b = cands[j];
                    if (mateOf.ContainsKey(b)) continue;
                    IntVec3 ea = a.EndCell, eb = b.EndCell;
                    if (Math.Max(Math.Abs(ea.x - eb.x), Math.Abs(ea.z - eb.z)) > 1) continue;
                    string key = a.layKey + "#" + b.layKey + "#" + kmax.ToString("0.###") + "#" + vis.ToString("0.###");
                    if (!mateSolved.TryGetValue(key, out MateInfo mi))
                    {
                        mateSolves++;
                        List<V2> A = a.lay.Flat, B = b.lay.Flat;
                        HoseSpliceMath.Mate m = A != null && B != null && A.Count > 2 && B.Count > 2
                            ? HoseSpliceMath.MatePair(A, B, A[A.Count - 1], kmax, vis, out _, out _, a.lay.Lead0, b.lay.Lead0) : null;
                        if (mateSolved.Count > 64) mateSolved.Clear();
                        mateSolved[key] = mi = new MateInfo { key = key.GetHashCode().ToString("x8"), A = a, B = b, mate = m };
                    }
                    if (mi.mate == null) continue;   // no gentle route: both drawn as laid
                    mateOf[a] = mateOf[b] = mi;
                    break;
                }
            }
            if (mateKept.Count > 0)
            {
                var gone = new List<CompHoseReel>();
                foreach (CompHoseReel r in mateKept.Keys) if (!mateOf.ContainsKey(r)) gone.Add(r);
                foreach (CompHoseReel r in gone) mateKept.Remove(r);
            }
        }

        private MateInfo MateFor(CompHoseReel r)
        {
            RefreshMates();
            return mateOf.TryGetValue(r, out MateInfo mi) ? mi : null;
        }

        /// <summary>r's drawn pose re-shaped onto the pair's coupling (HoseSpliceMath.MateTail with the pair's cached seed, so a
        /// fill transition re-lands one curve per tick); the pose as laid when the re-shape fails.</summary>
        private List<V2> Mated(CompHoseReel r, MateInfo mi, List<V2> pts)
        {
            bool isA = r == mi.A;
            double kmax = 1 / Math.Max(0.45, RM_HoseSettings.Shape().MinBendRadius);
            double vis = HoseMath.VisibleWidth(1, RM_HoseSettings.plumpAmount);
            List<V2> o = HoseSpliceMath.MateEnd(pts, mi.mate, isA, kmax, vis, r.lay?.Lead0 ?? 0);
            if (o == null) { mateKept.Remove(r); return pts; }
            int same = 0;
            while (same < o.Count && same < pts.Count && V2.Dist(o[same], pts[same]) < 1e-9) same++;
            mateKept[r] = same;
            return o;
        }

        /// <summary>Probe read: every coupled pair now (reel ids, coupling point, axis, cost) and the session's pair solves.</summary>
        public string MateReport()
        {
            RefreshMates();
            var seen = new HashSet<MateInfo>();
            var sb = new System.Text.StringBuilder();
            foreach (MateInfo mi in mateOf.Values)
            {
                if (!seen.Add(mi)) continue;
                sb.Append($"{mi.A.parent.thingIDNumber}+{mi.B.parent.thingIDNumber} at {mi.mate.C} axis {mi.mate.Axis} cost {mi.mate.Cost:0.00}; ");
            }
            return $"mates {seen.Count}: {sb}solves {mateSolves}, joiner halves drawn {lastMateJoins}";
        }
        public bool lastFar;

        private sealed class CarryCache
        {
            public string key;
            public List<V2> prefix;
            public V2 corner;
            public double len;
            public Mesh flat, shadow;
        }

        private readonly Dictionary<CompHoseReel, CarryCache> carryCache = new Dictionary<CompHoseReel, CarryCache>();
        private readonly Dictionary<CompHoseReel, KeyValuePair<string, double>> totals = new Dictionary<CompHoseReel, KeyValuePair<string, double>>();

        private void DropCarryCache(CompHoseReel r)
        {
            if (!carryCache.TryGetValue(r, out CarryCache c)) return;
            if (c.flat != null) UnityEngine.Object.Destroy(c.flat);
            if (c.shadow != null) UnityEngine.Object.Destroy(c.shadow);
            carryCache.Remove(r);
        }

        /// <summary>The trail's pulled length while winding (what WindBy measures `wound` against), cached per lay.</summary>
        private double TotalOf(CompHoseReel r)
        {
            string k = r.layKey ?? "";
            if (totals.TryGetValue(r, out var kv) && kv.Key == k) return kv.Value;
            double t = r.TrailLength();
            totals[r] = new KeyValuePair<string, double>(k, t);
            return t;
        }

        /// <summary>Where the carrier holds the end: his interpolated draw position a quarter cell ahead (the rope line's
        /// pawn.DrawPos, read every frame); the trail's last cell when he is gone (the holder check drops it next).</summary>
        private V2 Hand(Pawn p, V2 fallback)
        {
            if (p == null || !p.Spawned || p.Map != map) return fallback;
            Vector3 d = p.DrawPos;
            // a stale tween (ticks stepped with no frame between, measured live 2026-10-05: DrawPos stayed at the grab
            // cell while the pawn walked 15 cells) must not stretch the hose back across the map: hold it at his cell
            if (Mathf.Abs(d.x - (p.Position.x + 0.5f)) > 1.6f || Mathf.Abs(d.z - (p.Position.z + 0.5f)) > 1.6f) return fallback;
            IntVec3 f = p.Rotation.FacingCell;
            return new V2(d.x + 0.25 * f.x, d.z + 0.25 * f.z);
        }

        /// <summary>Section 6: the carried hose. The PREFIX (mouth -> walked trail pulled taut, corners rounded) is a cached
        /// mesh rebuilt only when the trail changes (about once per cell walked); the TAIL (round the last trail cell to the
        /// carrier's hand) is a few samples rebuilt each frame. Flat pose, no rope settle. LOD at far zoom: coarser samples,
        /// no shadow, no end piece.</summary>
        private void DrawCarrying(CompHoseReel r, float y, bool far)
        {
            HoseLookMats hm = HoseMaterials.For(r);
            float vis = (float)HoseMath.VisibleWidth(0, RM_HoseSettings.plumpAmount);
            float wf = (float)HoseMath.MeshWidthFlat(vis);
            double step = far ? HoseLive.SampleFar : HoseLive.SampleNear;
            string key = r.TrailKey() + (far ? "F" : "N") + "@" + RankOf(r) + "|" + RM_HoseSettings.ShapeFingerprint();
            carryCache.TryGetValue(r, out CarryCache cc);
            if (cc == null || cc.key != key)
            {
                DropCarryCache(r);
                var t = new HoseTrail(Start(r), double.PositiveInfinity);
                t.Cells.AddRange(r.TrailCells());
                // C7a-F6: the same 60-tick snapshot the carry step itself walks (CompHoseReel), never a whole-map rebuild per cell
                List<V2> pulled = t.Pulled(World(60));
                cc = new CarryCache { key = key };
                cc.prefix = HoseLive.Prefix(pulled, RM_HoseSettings.minBendRadius, step, out cc.corner);
                cc.len = Geo.Length(cc.prefix);
                if (cc.prefix.Count >= 2)
                {
                    cc.flat = Ribbon(cc.prefix, wf, y, 0.37);
                    if (!far) cc.shadow = Ribbon(Shifted(cc.prefix), vis * (float)HoseMath.ShadowWidth(0), y - 0.0004f, 0.11);
                }
                carryCache[r] = cc;
                carryPrefixBuilds++;
            }
            V2 hand = Hand(r.carrier, cc.corner);
            List<V2> tail = HoseLive.Tail(cc.prefix[cc.prefix.Count - 1], cc.corner, hand, step);
            Mesh tf = Ribbon(tail, wf, y, HoseLive.ContinueS0(0.37, cc.len, wf));
            Mesh ts = far ? null : Ribbon(Shifted(tail), vis * (float)HoseMath.ShadowWidth(0), y - 0.0004f, 0.11);
            frameMeshes.Add(tf);
            frameMeshes.Add(ts);
            Material flat = hm.Flat(1f), sh = HoseMaterials.Shadow((float)HoseMath.ShadowAlpha(0));
            if (!far)
            {
                if (cc.shadow != null) Graphics.DrawMesh(cc.shadow, Matrix4x4.identity, sh, 0);
                if (ts != null) Graphics.DrawMesh(ts, Matrix4x4.identity, sh, 0);
            }
            if (flat != null)
            {
                if (cc.flat != null) Solid(cc.flat, Matrix4x4.identity, flat);
                if (tf != null) Solid(tf, Matrix4x4.identity, flat);
            }
            var all = new List<V2>(cc.prefix.Count + tail.Count);
            all.AddRange(cc.prefix);
            for (int k = 1; k < tail.Count; k++) all.Add(tail[k]);
            if (!far && all.Count >= 2) DrawEnds(r, hm, NoJoints, all, vis, y + 0.001f, false);
            lastCarryDraws++;
            lastDraw[r] = "carry";
            lastDrawnLen[r] = Geo.Length(all);
            lastHand[r] = hand;
        }

        private static readonly List<int> NoJoints = new List<int>();

        /// <summary>Arc length of a nozzled reel's hose hidden from the strand mesh: Mouth to the seated nozzle tip, then the end
        /// coupling (JoinerFace + 0.03 sizes) and 0.30 cell into its wrap (DrawEnds' reel-end Fitting). 0 for a 1x1 reel.</summary>
        public static double OutletTrim(CompHoseReel r, float vis)
        {
            if (!r.Rect.HasNozzle || r.lay == null || !r.lay.Outlet) return 0;
            double size = HoseMath.FittingSize(vis, PieceBand, CouplingMax);
            return V2.Dist(r.Rect.Mouth, r.Rect.NozzleTip) - HoseReelRect.NozzleSeat + (JoinerFace + 0.03) * size + 0.30;
        }

        private static List<V2> Shifted(List<V2> pts)
        {
            var off = new V2(0.03, -0.03);
            var o = new List<V2>(pts.Count);
            foreach (V2 p in pts) o.Add(p + off);
            return o;
        }

        // A cut hose (HOSE_BLOCKED_REROUTE_RETRACT_1) winding back onto its reel: drawn state only, the reel is Stored.
        private sealed class Ghost
        {
            public CompHoseReel reel;
            public List<V2> pts;
            public int start;
            public double len;
        }

        private readonly List<Ghost> ghosts = new List<Ghost>();
        public int GhostCount => ghosts.Count;

        private void DrawGhosts(float y0)
        {
            if (ghosts.Count == 0) return;
            int now = Find.TickManager.TicksGame;
            float vis = (float)HoseMath.VisibleWidth(0, RM_HoseSettings.plumpAmount);
            for (int i = ghosts.Count - 1; i >= 0; i--)
            {
                Ghost g = ghosts[i];
                // done, or the reel's hose went out again (a new order): the ghost is gone
                if (HoseLive.AutoDone(now - g.start, g.len) || !g.reel.parent.Spawned || g.reel.HoseOut) { ghosts.RemoveAt(i); continue; }
                List<V2> pts = HoseLive.ClipWound(g.pts, HoseLive.AutoWound(now - g.start), g.len);
                float y = y0 + HoseMath.CrossLift(RankOf(g.reel));
                HoseLookMats hm = HoseMaterials.For(g.reel);
                Mesh m = Ribbon(pts, (float)HoseMath.MeshWidthFlat(vis), y, 0.37);
                frameMeshes.Add(m);
                if (m != null && hm.Flat(1f) != null) Graphics.DrawMesh(m, Matrix4x4.identity, hm.Flat(1f), 0);
                if (!lastFar && pts.Count >= 2) DrawEnds(g.reel, hm, NoJoints, pts, vis, y + 0.001f, false);
                lastGhostDraws++;
            }
        }

        /// <summary>C7a-F7: the feed ribbon of each reel, rebuilt only when its ends, width or band change (it used to be a new
        /// Mesh every rendered frame, paused included).</summary>
        private sealed class FeedCache
        {
            public V2 from, to;
            public int n;
            public float width, y;
            public Mesh mesh;
        }

        private readonly Dictionary<CompHoseReel, FeedCache> feeds = new Dictionary<CompHoseReel, FeedCache>();

        /// <summary>State read: feed meshes built this session (a settled reel builds one, then none per frame).</summary>
        public static int FeedBuilds;

        private void DropFeed(CompHoseReel r)
        {
            if (feeds.TryGetValue(r, out FeedCache f))
            {
                if (f.mesh != null) UnityEngine.Object.Destroy(f.mesh);
                feeds.Remove(r);
            }
        }

        /// <summary>Owner review round 2 (2026-10-04, station 16: "the crappy hose reel disconnected from the pipe"): a reel
        /// beside a pipe or tank (HosePorts / HosePortRule) shows a short flat feed hose from under the reel to the port,
        /// with a brass coupling on the shared edge. Drawn in the hose band, below buildings, so under a tank it vanishes
        /// beneath the sprite instead of stopping at its outline; on a pipe it ends on the pipe's centreline.</summary>
        private void DrawFeed(CompHoseReel r, float y)
        {
            if (r.Port() == null) { DropFeed(r); return; }
            // HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES: the link's geometry is HoseJoints.ReelFeed (one source of truth, the joint
            // check reads the same): into the nozzle's coupling when the port faces a stored reel's nozzle, else from the port's
            // centre line in under the reel to its centre. Never a coupling floating on the shared edge (audit D3/D5/D6/D7).
            bool deployedArt = !(r.carry == HoseCarryState.Stored && !r.laid);
            List<V2> path = HoseJoints.ReelFeed(r.Rect, r.portSide, r.portContact, deployedArt, out bool onNozzle, out V2 face, out V2 axis);
            float vis = (float)HoseMath.VisibleWidth(0, RM_HoseSettings.plumpAmount);
            HoseLookMats hm = HoseMaterials.For(r);
            Material m = hm.Flat(1f);
            if (m == null || path.Count < 2) return;
            V2 from = path[0], to = path[path.Count - 1];
            float width = (float)HoseMath.MeshWidthFlat(vis), fy = y - 0.0008f;
            feeds.TryGetValue(r, out FeedCache fc);
            if (fc == null || fc.mesh == null || fc.width != width || fc.y != fy || fc.from.X != from.X || fc.from.Z != from.Z
                || fc.to.X != to.X || fc.to.Z != to.Z || fc.n != path.Count)
            {
                DropFeed(r);
                fc = new FeedCache { from = from, to = to, n = path.Count, width = width, y = fy, mesh = Ribbon(Densify(path), width, fy, 0.37) };
                feeds[r] = fc;
                FeedBuilds++;
            }
            Mesh feed = fc.mesh;
            Solid(feed, Matrix4x4.identity, m);
            if (onNozzle && hm.CouplingBare != null)
            {
                Color wrapTint = Color.Lerp(Color.white, Tint(r), 0.5f);
                // REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH: on the drawn nozzle it rides over the tip, as the laid hose's coupling does
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, face, axis, vis, HoseJoints.NozzleFittingOnTop(r.Rect.Rot) ? NozzleTopY(y - 0.0006f) : y - 0.0006f, wrapTint, rec: r, role: "feed_nozzle");
            }
            lastFeedDraws++;
        }

        /// <summary>A square feed path as the ribbon wants it: a few samples per leg so its corners stay sharp.</summary>
        private static List<V2> Densify(List<V2> path)
        {
            var o = new List<V2> { path[0] };
            for (int i = 1; i < path.Count; i++)
            {
                V2 a = path[i - 1], b = path[i];
                int n = Math.Max(1, (int)Math.Ceiling(V2.Dist(a, b) / 0.25));
                for (int k = 1; k <= n; k++) o.Add(a + (b - a) * (k / (double)n));
            }
            return o;
        }

        /// <summary>Which reel art prints (B26, round 2): Graphic_HoseReel swaps stored/deployed on the map mesh (state read).</summary>
        public static string ReelGraphic(CompHoseReel r)
        {
            Graphic g = r.parent.Graphic;
            if (!(g is Graphic_HoseReel gr)) return "stored (graphic class is " + (g?.GetType().Name ?? "null") + ", not Graphic_HoseReel)";
            if (r.carry == HoseCarryState.Stored && !r.laid) return "stored";
            return gr.HasDeployed && gr.MatAt(Rot4.West, r.parent) != gr.MatSingle ? "deployed" : "stored (stand-in: Reel_Deployed art missing)";
        }

        /// <summary>A fitting whose working end is at <paramref name="end"/> pointing along <paramref name="d"/>: its centre
        /// sits <paramref name="centreOff"/> sizes from the end, its brass starts <paramref name="brassFrom"/> sizes from the
        /// centre; the wrap ends 0.05 cell over the brass start and runs back along the hose.</summary>
        /// <summary>The altitude a nozzle coupling draws at when it rides on the reel (HoseJoints.NozzleFittingAltitude), keeping
        /// the hose's own fitting lift above its band so the wrap still sits over the coupling.</summary>
        private static float NozzleTopY(float y) => (float)HoseJoints.NozzleFittingAltitude + (y - (float)RimMandrake.Shared.Slack.DrawOrder.Alt(RimMandrake.Shared.Slack.DrawOrder.LayerHose));

        private void Fitting(HoseLookMats hm, Material m, float maxBand, double centreOff, double brassFrom, V2 end, V2 d, float vis, float y, Color wrapTint, float widen = 1f,
            double wrapLen = HoseMath.WrapLength, CompHoseReel rec = null, string role = null)
        {
            float size = (float)HoseMath.FittingSize(vis, PieceBand, maxBand) * widen;
            V2 c = HoseJoints.FittingCentre(end, d, centreOff, size);
            Piece(m, c, d, size, y);
            // JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX: the piece just drawn, as drawn (only when the material exists: Piece drew it)
            if (rec != null && role != null && m != null)
            {
                if (!drawnFittings.TryGetValue(rec, out Dictionary<string, DrawnFitting> df)) drawnFittings[rec] = df = new Dictionary<string, DrawnFitting>();
                df[role] = new DrawnFitting { centre = c, dir = d, size = size, band = maxBand };
            }
            V2 brass = c + d * (brassFrom * size);
            if (wrapLen > 1e-3) Wrap(hm, brass + d * (0.05 - wrapLen / 2), d, vis, y + 0.0002f, wrapTint, wrapLen);
        }

        private void Wrap(HoseLookMats hm, V2 centre, V2 d, float vis, float y, Color tint, double len = HoseMath.WrapLength)
        {
            PieceXZ(hm.Binding, centre, d, (float)len, (float)HoseMath.WrapWidth(vis) / BindBand, y, tint);
            lastWrapDraws++;
        }

        private static void PieceXZ(Material m, V2 c, V2 dir, float sx, float sz, float y, Color tint)
        {
            if (m == null) return;
            float ang = Mathf.Atan2((float)dir.Z, (float)dir.X);
            if (tint != Color.white) m = HoseMaterials.Tinted(m, tint);
            Solid(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)c.X, y, (float)c.Z), Quaternion.Euler(0f, -ang * Mathf.Rad2Deg, 0f),
                new Vector3(sx, 1f, sz)), m);
        }

        private static void Piece(Material m, V2 c, V2 dir, float size, float y)
        {
            if (m == null) return;
            float ang = Mathf.Atan2((float)dir.Z, (float)dir.X);
            Solid(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)c.X, y, (float)c.Z), Quaternion.Euler(0f, -ang * Mathf.Rad2Deg, 0f),
                new Vector3(size, 1f, size)), m);
        }

        /// <summary>2026-10-05 (owner screenshot: hard rectangles across the hose): an opaque hose piece is drawn twice -- a
        /// Cutout pass that writes depth (vanilla's Custom/Cutout, ZWrite On), then its soft-edged Transparent self. Vanilla's
        /// sun and edge shadows (queues 3170 / 2950, ZTest LEqual, at the Shadows layer just below the hose) then fail the
        /// depth test on the hose, exactly as they do on items and pawns.</summary>
        private static void Solid(Mesh mesh, Matrix4x4 matrix, Material m)
        {
            if (m == null) return;
            DepthPass(mesh, matrix, m);
            Graphics.DrawMesh(mesh, matrix, m, 0);
        }

        private static void DepthPass(Mesh mesh, Matrix4x4 matrix, Material m)
        {
            Material d = HoseMaterials.Depth(m);
            if (d != null) Graphics.DrawMesh(mesh, matrix, d, 0);
            lastDepthDraws++;
        }

        /// <summary>State read for the probe: depth pre-pass draws last frame (reset per DrawAll).</summary>
        public static int lastDepthDraws;

        /// <summary>A strip along pts: u runs along it (tile = width x 4, the strips are 256x64), v across.</summary>
        internal static Mesh Ribbon(List<V2> pts, float width, float y, double s0)
        {
            if (pts.Count < 2 || width <= 0) return null;
            var v = new List<Vector3>(pts.Count * 2);
            var uv = new List<Vector2>(pts.Count * 2);
            var tr = new List<int>(pts.Count * 6);
            float hw = width / 2f;
            double tile = width * 4.0, u = s0 * 4.0;
            for (int i = 0; i < pts.Count; i++)
            {
                Geo.TanNorm(pts, i, out V2 t, out V2 n);
                if (i > 0) u += V2.Dist(pts[i - 1], pts[i]) / tile;
                V2 l = pts[i] + n * hw, r = pts[i] - n * hw;
                v.Add(new Vector3((float)l.X, y, (float)l.Z));
                v.Add(new Vector3((float)r.X, y, (float)r.Z));
                uv.Add(new Vector2((float)u, 1f));
                uv.Add(new Vector2((float)u, 0f));
                if (i == 0) continue;
                int a = 2 * (i - 1);
                tr.Add(a); tr.Add(a + 2); tr.Add(a + 3);
                tr.Add(a); tr.Add(a + 3); tr.Add(a + 1);
            }
            var m = new Mesh { name = "RM_Hose" };
            m.SetVertices(v);
            m.SetUVs(0, uv);
            m.SetTriangles(tr, 0);
            m.RecalculateBounds();
            return m;
        }
    }

    /// <summary>One look's hose materials (per-build style stage 3): strands, binding wrap, coupling, nozzle, end cap and open
    /// mouth from that look's folder (HoseStyles.PathFor); the strand shadow is shared. A piece missing from a look's
    /// folder falls back to Scrapper's and is listed in <see cref="HoseMaterials.Missing"/> (a config error, logged once).</summary>
    public sealed class HoseLookMats
    {
        public string look;
        public Texture2D flatTex, plumpTex;
        public Material Binding, Mouth, CouplingBare, NozzleBare, EndCapBare;
        /// <summary>State read: piece name -> the texture path actually loaded (a fallback reads as Scrapper's path).</summary>
        public readonly Dictionary<string, string> paths = new Dictionary<string, string>();
        internal readonly Dictionary<long, Material> pool = new Dictionary<long, Material>();

        public Material Flat(float alpha) => HoseMaterials.Get(this, flatTex, 1, alpha, Color.white);
        public Material Plump(float alpha, Color tint) => HoseMaterials.Get(this, plumpTex, 2, alpha, tint);
    }

    [StaticConstructorOnStartup]
    public static class HoseMaterials
    {
        private static readonly Texture2D shadowTex;
        private static readonly Dictionary<long, Material> shadowPool = new Dictionary<long, Material>();
        private static readonly Dictionary<string, HoseLookMats> byLook = new Dictionary<string, HoseLookMats>();
        /// <summary>State read: look/piece pairs whose art was missing (drawn with Scrapper's piece instead).</summary>
        public static readonly List<string> Missing = new List<string>();
        public static readonly int Queue;
        /// <summary>Scrapper's set: the fallback for any look that cannot be resolved.</summary>
        public static readonly HoseLookMats Scrapper;

        static HoseMaterials()
        {
            // M6: the base strand queue is derived in shared code from the Transparent shader (GSS derives its own from the
            // same rule), so the two mods agree on stacking (overhead > hose > cords) without reading each other.
            Queue = RimMandrake.Shared.Slack.DrawOrder.HoseQueue(
                RimMandrake.Shared.Slack.DrawOrder.BaseStrandQueue(ShaderDatabase.Transparent != null ? ShaderDatabase.Transparent.renderQueue : 0));
            shadowTex = Tiled(HoseStyles.PathFor(HoseStyles.Scrapper, HoseStyles.SharedShadow), true);
            Scrapper = Build(HoseStyles.Scrapper, null);
            foreach (string l in HoseStyles.Looks)
                if (l != HoseStyles.Scrapper) Build(l, Scrapper);
            foreach (string m in Missing) Log.Error("[FlowWorks] hose style art missing (Scrapper piece drawn instead): " + m);
        }

        private static HoseLookMats Build(string look, HoseLookMats fallback)
        {
            var s = new HoseLookMats { look = look };
            bool report = fallback == null;
            s.flatTex = TexOr(s, "Strand_Flat", true, report, fallback?.flatTex);
            s.plumpTex = TexOr(s, "Strand_Plump", true, report, fallback?.plumpTex);
            s.Binding = PieceOr(s, "Binding", report, fallback?.Binding);
            s.CouplingBare = PieceOr(s, "Coupling_Bare", report, fallback?.CouplingBare);
            s.NozzleBare = PieceOr(s, "Nozzle_Bare", report, fallback?.NozzleBare);
            s.EndCapBare = PieceOr(s, "EndCap_Bare", report, fallback?.EndCapBare);
            s.Mouth = PieceOr(s, "Mouth", report, fallback?.Mouth);
            byLook[look] = s;
            return s;
        }

        private static Texture2D TexOr(HoseLookMats s, string piece, bool tiled, bool report, Texture2D fb)
        {
            string p = HoseStyles.PathFor(s.look, piece);
            Texture2D t = tiled ? Tiled(p, report) : ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) { s.paths[piece] = p; return t; }
            if (fb != null) { Missing.Add(s.look + "/" + piece); s.paths[piece] = HoseStyles.PathFor(HoseStyles.Scrapper, piece); }
            return fb;
        }

        private static Material PieceOr(HoseLookMats s, string piece, bool report, Material fb)
        {
            string p = HoseStyles.PathFor(s.look, piece);
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) { s.paths[piece] = p; return MaterialPool.MatFrom(new MaterialRequest(t, ShaderDatabase.Transparent) { renderQueue = Queue }); }
            if (fb != null) { Missing.Add(s.look + "/" + piece); s.paths[piece] = HoseStyles.PathFor(HoseStyles.Scrapper, piece); }
            return fb;
        }

        /// <summary>The materials of one look (an unknown look draws Scrapper's).</summary>
        public static HoseLookMats For(string look) => look != null && byLook.TryGetValue(look, out HoseLookMats s) ? s : Scrapper;

        /// <summary>The look a reel's hose draws in: the reel's own (stored style, or the default look for a legacy reel).</summary>
        public static string LookOf(CompHoseReel r) =>
            HoseStyles.HoseLook(r?.parent == null ? null : HoseLook.LookOfThing(r.parent), HoseLook.DefaultLook);

        public static HoseLookMats For(CompHoseReel r) => For(LookOf(r));

        public static bool Installed => Scrapper?.flatTex != null && Scrapper.plumpTex != null;

        private static Texture2D Tiled(string p, bool report)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) t.wrapMode = TextureWrapMode.Repeat;
            return t;
        }

        private static readonly Dictionary<Material, Dictionary<int, Material>> tinted = new Dictionary<Material, Dictionary<int, Material>>();

        /// <summary>A piece material tinted (the binding takes half the hose's wet tint so it sits on any hose); pooled.</summary>
        public static Material Tinted(Material m, Color c)
        {
            int k = ((int)(c.r * 63) << 12) | ((int)(c.g * 63) << 6) | (int)(c.b * 63);
            if (!tinted.TryGetValue(m, out var byTint)) tinted[m] = byTint = new Dictionary<int, Material>();
            if (byTint.TryGetValue(k, out Material t)) return t;
            t = MaterialPool.MatFrom(new MaterialRequest((Texture2D)m.mainTexture, ShaderDatabase.Transparent, new Color(c.r, c.g, c.b, 1f)) { renderQueue = Queue });
            byTint[k] = t;
            return t;
        }

        /// <summary>Alpha quantised to 1/20 so the cross-fade reuses a handful of pooled materials (one pool per look).</summary>
        internal static Material Get(HoseLookMats s, Texture2D tex, int slot, float alpha, Color tint) =>
            Get(s?.pool ?? shadowPool, tex, slot, alpha, tint);

        private static Material Get(Dictionary<long, Material> pool, Texture2D tex, int slot, float alpha, Color tint)
        {
            if (tex == null) return null;
            int a = Mathf.Clamp(Mathf.RoundToInt(alpha * 20f), 0, 20);
            long key = ((long)slot << 40) ^ ((long)a << 32) ^ (long)(tint.r * 255) << 16 ^ (long)(tint.g * 255) << 8 ^ (long)(tint.b * 255);
            if (pool.TryGetValue(key, out Material m)) return m;
            m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, new Color(tint.r, tint.g, tint.b, a / 20f)) { renderQueue = Queue });
            pool[key] = m;
            return m;
        }

        // B18: every hose material shares ONE render queue, so altitude alone orders them: a crossing hose (its own
        // altitude band, HoseMath.CrossLift) and all its fittings draw over the hose beneath, never interleaved. Within a
        // hose the shadow / flat / plump / fittings order is kept by their small altitude steps.
        public static Material Shadow(float alpha) => Get(shadowPool, shadowTex, 3, alpha, Color.white);

        private static readonly Dictionary<Material, Material> depth = new Dictionary<Material, Material>();

        /// <summary>The Cutout twin of an opaque hose material (same texture and tint, full alpha): it writes depth so vanilla's
        /// sun / edge shadows skip the hose (see RM_MapComponent_Hoses.Solid). Pooled per source material.</summary>
        public static Material Depth(Material m)
        {
            if (m == null) return null;
            if (depth.TryGetValue(m, out Material d)) return d;
            Color c = m.color;
            d = m.mainTexture is Texture2D t ? MaterialPool.MatFrom(new MaterialRequest(t, ShaderDatabase.Cutout, new Color(c.r, c.g, c.b, 1f))) : null;
            depth[m] = d;
            return d;
        }
    }

    /// <summary>Keeps RM_MapComponent_Hoses out of the save (as the cord graph and aerial components): every
    /// MapComponent is written by class name, and a mod-less load of a save naming it logs "Could not find class".
    /// ESSENTIAL patch (FINAL §3.9): applied by RM_HoseEssentials outside PatchApplier's switch-off path, never by
    /// attribute; if it fails to apply, the hose map component removes itself from every map (hoses draw nothing).</summary>
    internal static class Patch_Map_ExposeComponents_SkipHoses
    {
        internal sealed class Held { public int Index; public MapComponent Comp; }

        internal static void Prefix(Map __instance, out Held __state)
        {
            __state = null;
            if (Scribe.mode != LoadSaveMode.Saving) return;
            List<MapComponent> list = __instance.components;
            int i = list.FindIndex(c => c is RM_MapComponent_Hoses);
            if (i < 0) return;
            __state = new Held { Index = i, Comp = list[i] };
            list.RemoveAt(i);
        }

        internal static Exception Finalizer(Map __instance, Exception __exception, Held __state)
        {
            if (__state != null)
            {
                List<MapComponent> list = __instance.components;
                list.RemoveAll(c => c is RM_MapComponent_Hoses);
                list.Insert(Math.Min(__state.Index, list.Count), __state.Comp);
            }
            return __exception;
        }
    }
}

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1's visible alert: reels whose hose was wound back in automatically in the last
    /// in-game day because no route within its length remained. Clears when the player lays the hose again.</summary>
    public class Alert_HoseRetracted : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_HoseRetracted()
        {
            defaultLabel = "Hose reeled in";
            defaultPriority = AlertPriority.Medium;
        }

        private List<Thing> Culprits()
        {
            culprits.Clear();
            int now = Find.TickManager.TicksGame;
            foreach (Map m in Find.Maps)
            {
                RM_MapComponent_Hoses c = m.GetComponent<RM_MapComponent_Hoses>();
                if (c == null) continue;
                foreach (CompHoseReel r in c.Reels)
                    if (!r.laid && r.lastRetractReason != null && r.lastRetractTick >= 0 && now - r.lastRetractTick < GenDate.TicksPerDay)
                        culprits.Add(r.parent);
            }
            return culprits;
        }

        public override TaggedString GetExplanation()
        {
            var sb = new System.Text.StringBuilder("An obstacle cut these hoses' routes and no other route fits within the hose's length, so they were wound back onto the reel:\n");
            foreach (Thing t in culprits)
            {
                CompHoseReel rc = t.TryGetComp<CompHoseReel>();
                sb.Append("\n  - ").Append(t.LabelShort).Append(": ").Append(rc?.Explain(rc.lastRetractReason, rc.lastRetractNeed));
            }
            sb.Append("\n\nClear the way or lay the hose to a nearer cell.");
            return sb.ToString();
        }

        public override AlertReport GetReport() => RM_HoseSettings.enabled ? AlertReport.CulpritsAre(Culprits()) : AlertReport.Inactive;
    }
}
