using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// The power-network adapter: copies what the cord model reads out of a live Map into a
    /// Verse-free CordWorld (design §8.1 "How it reads the network"). Kept apart from the planner
    /// and the drawer on purpose (power_poles_and_flexible_pipe_assessment_2026-10-02.md): a later
    /// hose or suspended-wire adapter fills the same CordWorld from its own grids.
    /// </summary>
    public static class CordWorldAdapter
    {
        internal static Cell C(IntVec3 c) => new Cell(c.x, c.z);
        internal static IntVec3 I(Cell c) => new IntVec3(c.X, 0, c.Z);

        internal static CordWorld Snapshot(Map map) => Snapshot(map, null);

        /// <summary>GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 2: with a cache, the per-cell base (fog, walls, doors, water,
        /// trees, busy cells) is the cache's copy patched at the cells dirtied since the last snapshot, instead of a whole-map
        /// scan (5.5 ms live on a 325x325 map with no conduits at all); the power part is read fresh either way.</summary>
        internal static CordWorld Snapshot(Map map, SnapshotCache cache)
        {
            long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
            CordWorld world = cache != null ? cache.Base(map).Clone() : FullBase(map);
            long t1 = System.Diagnostics.Stopwatch.GetTimestamp();
            FogGrid fog = map.fogGrid;
            AddPower(map, world, fog);
            if (cache != null)
            {
                cache.BaseMs = (t1 - t0) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
                cache.PowerMs = (System.Diagnostics.Stopwatch.GetTimestamp() - t1) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
            }
            return world;
        }

        /// <summary>The whole-map per-cell scan: everything of the snapshot that is not the power network.</summary>
        internal static CordWorld FullBase(Map map)
        {
            int w = map.Size.x, h = map.Size.z;
            var world = new CordWorld(w, h);
            PathGrid pg = map.pathing.Normal.pathGrid;
            CellIndices ci = map.cellIndices;
            FogGrid fog = map.fogGrid;
            for (int idx = 0; idx < w * h; idx++)
            {
                IntVec3 c = ci.IndexToCell(idx);
                var cell = new Cell(c.x, c.z);
                if (fog.IsFogged(idx)) { world.SetBlocked(cell, BlockKind.Rock); continue; }
                Building ed = map.edificeGrid[idx];
                if (ed is Building_Door) world.SetDoor(cell);
                // GSS_WATER_STUB_FIX_PASSED_LAST_WEEK: deep water is Water even when a swim mod (FlowWorks R12) makes the path grid walkable
                TerrainDef t = map.terrainGrid.TerrainAt(idx);
                BlockKind? k = SnapshotBlock.Of(pg.WalkableFast(idx), ed != null,
                    ed?.def.building != null && ed.def.building.isNaturalRock, ed != null && ed.TryGetComp<CompPower>() != null,
                    t != null && t.IsWater, t != null && t.passability == Traversability.Impassable);
                if (k.HasValue) world.SetBlocked(cell, k.Value);
            }
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                if (p.def.plant != null && p.def.plant.IsTree) world.SetExtraCost(C(p.Position), 1.5f);
            MarkBusy(map, world);
            return world;
        }

        /// <summary>One cell of FullBase, recomputed into a base world: false when the cell lost a door or a busy mark (a
        /// CordWorld can only set those), and the caller rescans the whole map instead.</summary>
        internal static bool PatchCell(Map map, CordWorld world, int idx)
        {
            IntVec3 c = map.cellIndices.IndexToCell(idx);
            var cell = new Cell(c.x, c.z);
            BlockKind? k;
            bool door = false;
            if (map.fogGrid.IsFogged(idx)) k = BlockKind.Rock;
            else
            {
                Building ed = map.edificeGrid[idx];
                door = ed is Building_Door;
                TerrainDef t = map.terrainGrid.TerrainAt(idx);
                k = SnapshotBlock.Of(map.pathing.Normal.pathGrid.WalkableFast(idx), ed != null,
                    ed?.def.building != null && ed.def.building.isNaturalRock, ed != null && ed.TryGetComp<CompPower>() != null,
                    t != null && t.IsWater, t != null && t.passability == Traversability.Impassable);
            }
            bool tree = false, linear = false;
            List<Thing> things = map.thingGrid.ThingsListAtFast(idx);
            for (int i = 0; i < things.Count; i++)
            {
                ThingDef d = things[i].def;
                if (d.category == ThingCategory.Plant && d.plant != null && d.plant.IsTree) tree = true;
                if (d.IsBuildingArtificial && IsLinear(d) && things[i].Spawned) linear = true;
            }
            bool busy = linear && !k.HasValue;
            if ((world.IsDoor(cell) && !door) || (world.IsBusy(cell) && !busy)) return false;
            world.SetBlocked(cell, k ?? BlockKind.None);
            if (door) world.SetDoor(cell);
            world.SetExtraCost(cell, tree ? 1.5f : 0f);
            if (busy) world.SetBusy(cell);
            return true;
        }

        /// <summary>Cells where two base worlds differ (block, door, route cost, busy): the cache's self-check.</summary>
        internal static int BaseDiff(CordWorld a, CordWorld b, out string first)
        {
            first = null;
            if (a.Width != b.Width || a.Height != b.Height) { first = "size"; return int.MaxValue; }
            int n = 0;
            for (int z = 0; z < a.Height; z++)
                for (int x = 0; x < a.Width; x++)
                {
                    var c = new Cell(x, z);
                    if (a.BlockAt(c) != b.BlockAt(c) || a.IsDoor(c) != b.IsDoor(c) || a.ExtraCost(c) != b.ExtraCost(c) || a.IsBusy(c) != b.IsBusy(c))
                    {
                        n++;
                        first ??= x + "," + z + ":" + a.BlockAt(c) + "/" + b.BlockAt(c);
                    }
                }
            return n;
        }

        private static void AddPower(Map map, CordWorld world, FogGrid fog)
        {
            var transmitterBuildings = new List<CompPower>();
            var transmitterMachines = new Dictionary<Thing, MachineInfo>();
            var connectors = new List<CompPower>();
            foreach (PowerNet net in map.powerNetManager.AllNetsListForReading)
            {
                foreach (CompPower t in net.transmitters)
                {
                    if (t?.parent == null || !t.parent.Spawned) continue;
                    ThingDef d = t.parent.def;
                    if (ConduitVisuals.IsTarget(d))
                    {
                        if (!fog.IsFogged(t.parent.Position)) world.SetConduit(C(t.parent.Position));
                    }
                    else if (ConduitVisuals.IsOtherConduit(d))
                    {
                        world.SetConduit(C(t.parent.Position));
                        world.SetForcedBuried(C(t.parent.Position));
                    }
                    else transmitterBuildings.Add(t);
                }
                foreach (CompPower c in net.connectors)
                    if (c?.parent != null && c.parent.Spawned) connectors.Add(c);
            }
            // transmitter buildings (batteries, switches): nodes hooked to every orthogonally
            // adjacent conduit cell around their footprint
            foreach (CompPower t in transmitterBuildings)
            {
                Thing th = t.parent;
                var m = new MachineInfo { Id = "t" + th.thingIDNumber, Kind = KindOf(t, true) };
                CellRect r = th.OccupiedRect();
                m.X0 = r.minX; m.Z0 = r.minZ; m.W = r.Width; m.H = r.Height;
                foreach (IntVec3 adj in GenAdj.CellsAdjacentCardinal(th))
                    if (world.IsConduit(C(adj)) && !m.Hookups.Contains(C(adj))) m.Hookups.Add(C(adj));
                SetWallHome(th, m);   // GPT source read 2026-10-06 A17: a wall-hung transmitter (the bracket) ends under its wall too
                transmitterMachines[th] = m;
                if (m.Hookups.Count > 0) world.Machines.Add(m);
            }
            // connectors (consumers, generators, lamps, batteries wired by a hookup)
            foreach (CompPower c in connectors)
            {
                CompPower parent = c.connectParent;
                // GPT source read 2026-10-06 B9 (owner decision by question card 2026-10-06: draw a cord like any other
                // connection): a device wired to our conduit hooks that conduit cell; a device wired straight
                // to a battery, switch or other transmitter building links to that building's node. Only an aerial anchor keeps
                // its drop wire (RM_MapComponent_Aerial.DrawLocalDrops), the same rule Patch_PrintWirePieceConnecting applies.
                Thing pt = parent?.parent;
                if (pt == null || !pt.Spawned) continue;
                HookupDraw how = ConduitVisuals.HookupTo(pt);
                if (how == HookupDraw.PatchCable) continue;
                Thing th = c.parent;
                var m = new MachineInfo { Id = "c" + th.thingIDNumber, Kind = KindOf(c, false) };
                CellRect r = th.OccupiedRect();
                m.X0 = r.minX; m.Z0 = r.minZ; m.W = r.Width; m.H = r.Height;
                ArtInsets(th.def, m);
                SetWallHome(th, m);
                PowerNet cnet = c.PowerNet;
                Cell? parentCell = how == HookupDraw.ConduitCell ? C(pt.Position) : (Cell?)null;
                List<Cell> near = HookupPick.Pick(world, m, parentCell,
                    cell => cnet != null && map.powerNetGrid.TransmittedPowerNetAt(I(cell)) == cnet);
                if (near != null)
                {
                    // GSS_CORD_SILENCE_PHANTOM_SPARK: a same-net conduit end beside the device is its one cord
                    foreach (Cell hk in near) if (world.IsConduit(hk) && !m.Hookups.Contains(hk)) m.Hookups.Add(hk);
                    world.Machines.Add(m);
                }
                else if (how == HookupDraw.ConduitCell)
                {
                    if (!world.IsConduit(C(pt.Position))) continue;     // a fogged conduit cell is not in the snapshot
                    m.Hookups.Add(C(pt.Position));
                    world.Machines.Add(m);
                }
                else if (transmitterMachines.TryGetValue(pt, out MachineInfo tm)) CordWorldLinks.LinkToMachine(world, m, tm);
            }
            AddTapNodes(map, world);
            // round 2: machines in id order, not power-net list order, so a net rebuilt in another order (a hypothesis for the
            // live far-dig re-reduce) leaves CordBuilder's graph inputs, and so the graph, unchanged. OrderBy is stable.
            List<MachineInfo> byId = world.Machines.OrderBy(m => m.Id, StringComparer.Ordinal).ToList();
            world.Machines.Clear();
            world.Machines.AddRange(byId);
        }

        /// <summary>CORD_LOOP_UNTANGLE_LASSOED_A_PIPE: every walkable, unfogged cell holding a drawn linear building (any linked
        /// graphic: pipes of any mod, power conduits of any net) is busy, so a cord's canned slack loop never lassoes it
        /// (CordLayer.Lassoes). Walls are linked too but already unwalkable; a hidden conduit draws nothing and is skipped.</summary>
        internal static void MarkBusy(Map map, CordWorld world)
        {
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
            {
                if (!IsLinear(t.def) || !t.Spawned) continue;
                foreach (IntVec3 c in t.OccupiedRect())
                {
                    Cell cell = C(c);
                    if (world.IsWalkable(cell)) world.SetBusy(cell);
                }
            }
        }

        /// <summary>A drawn linear building: its graphic links to its neighbours (pipes, conduits, fences).</summary>
        internal static bool IsLinear(ThingDef d) => d?.graphicData != null && d.graphicData.Linked && !ConduitVisuals.IsOtherConduit(d);

        /// <summary>Round 3 (owner 2026-10-04): "the power tap should be considered a Node that both power systems now must
        /// connect with their cables". The clamp is a connector of OUR net (its machine already hooks our conduit when it has a
        /// connectParent); here it also hooks the conduit cell it bites, or links the foreign transmitter building it bites,
        /// so THEIR cable runs into the clamp instead of ending beside it as a free sparking end. Draw-only: the power nets
        /// are untouched (the two grids never merge; CompPowerTap moves the energy).</summary>
        /// <summary>CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT: the machine ids (AddTapNodes' "c" + thingIDNumber) of every tap clamp. The
        /// clamp IS a drawn connector, so both cords keep the straight plug into its jaws (BuildOptions.StraightPlugIds).</summary>
        internal static HashSet<string> TapIds(Map map)
        {
            var ids = new HashSet<string>();
            if (Aerial.AerialDefOf.RM_PowerTapClamp == null) return ids;
            foreach (Thing th in map.listerThings.ThingsOfDef(Aerial.AerialDefOf.RM_PowerTapClamp)) ids.Add("c" + th.thingIDNumber);
            return ids;
        }

        private static void AddTapNodes(Map map, CordWorld world)
        {
            if (Aerial.AerialDefOf.RM_PowerTapClamp == null) return;
            foreach (Thing th in map.listerThings.ThingsOfDef(Aerial.AerialDefOf.RM_PowerTapClamp))
            {
                Aerial.CompPowerTap tap = th.TryGetComp<Aerial.CompPowerTap>();
                if (tap == null || !th.Spawned) continue;
                tap.VictimNet(out Thing victim);
                if (victim == null) continue;
                string id = "c" + th.thingIDNumber;
                MachineInfo m = world.Machines.Find(x => x.Id == id);
                bool add = m == null;
                if (add)
                {
                    m = new MachineInfo { Id = id, Kind = MachineKind.Consumer };
                    CellRect r = th.OccupiedRect();
                    m.X0 = r.minX; m.Z0 = r.minZ; m.W = r.Width; m.H = r.Height;
                }
                Cell vc = C(victim.Position);
                if (world.IsConduit(vc)) { if (!m.Hookups.Contains(vc)) m.Hookups.Add(vc); }
                else
                {
                    string vid = "t" + victim.thingIDNumber;
                    if (world.Machines.Exists(x => x.Id == vid) && !m.MachineLinks.Contains(vid)) m.MachineLinks.Add(vid);
                }
                if (add && (m.Hookups.Count > 0 || m.MachineLinks.Count > 0)) world.Machines.Add(m);
            }
        }

        /// <summary>Round 4: a wall-mounted device's cord ends under the wall it hangs on (MachineInfo.HasHome) -- the same wall
        /// vanilla's PowerConnectionMaker.TryConnectToAnyPowerNet measures a wall attachment's connection from.</summary>
        internal static void SetWallHome(Thing th, MachineInfo m)
        {
            if (th?.def?.building == null || !th.def.building.isAttachment || !th.Spawned) return;
            Thing wall = GenConstruct.GetWallAttachedTo(th);
            if (wall == null) return;
            m.HasHome = true; m.HomeX = wall.Position.x; m.HomeZ = wall.Position.z;
        }

        /// <summary>Where a machine's drawn art stands in from its footprint edge (owner review 2026-10-04 B10): the cord runs on
        /// that far under the art so it visibly plugs INTO the graphic. Measured from the shipped Core textures: the solar
        /// collector's panel stops 22 px of 256 above its bottom edge (only its legs reach the edge) = 0.34 cell of 4;
        /// +0.06 so the plug tucks under the panel. Unlisted machines: their art reaches the edge (0).</summary>
        public static readonly System.Collections.Generic.Dictionary<string, float[]> InsetsSNEW =
            new System.Collections.Generic.Dictionary<string, float[]> { { "SolarGenerator", new[] { 0.40f, 0f, 0f, 0f } } };

        private static void ArtInsets(ThingDef d, MachineInfo m)
        {
            if (d == null || !InsetsSNEW.TryGetValue(d.defName, out float[] v)) return;
            m.InsetS = v[0]; m.InsetN = v[1]; m.InsetE = v[2]; m.InsetW = v[3];
        }

        private static MachineKind KindOf(CompPower c, bool transmitter)
        {
            if (c is CompPowerPlant) return MachineKind.Source;
            if (c is CompPowerBattery) return MachineKind.Battery;
            if (transmitter) return MachineKind.Transmitter;
            return MachineKind.Consumer;
        }

        /// <summary>live = the net at that cell has an active power source (design §8.5).</summary>
        internal static bool IsLive(Map map, Cell c)
        {
            IntVec3 v = I(c);
            if (!v.InBounds(map)) return false;
            PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(v);
            return net != null && net.HasActivePowerSource;
        }
    }

    /// <summary>GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 2: the snapshot base (FullBase) kept between rebuilds and patched at
    /// the cells a map-mesh event dirtied (each with its 8 neighbours). Whole-map rescans happen on the first use, after
    /// Invalidate, past Overflow dirty cells, when a patch would have to clear a door or busy mark, and every CheckEvery
    /// uses, where the rescan is compared with the patched copy and any difference is counted in Mismatches.</summary>
    internal sealed class SnapshotCache
    {
        public const int Overflow = 4096, CheckEvery = 64;
        private CordWorld baseWorld;
        private readonly HashSet<int> dirty = new HashSet<int>();
        private bool overflow;
        private int sinceCheck;
        public int FullScans, Uses, LastPatched, Mismatches;
        public string LastFullWhy = "", LastMismatch = "";
        public double BaseMs, PowerMs;

        public void Invalidate(string why) { baseWorld = null; dirty.Clear(); overflow = false; LastFullWhy = why; }

        public void NoteCell(Map map, IntVec3 c)
        {
            if (baseWorld == null || overflow) return;
            for (int dz = -1; dz <= 1; dz++)
                for (int dx = -1; dx <= 1; dx++)
                {
                    var n = new IntVec3(c.x + dx, 0, c.z + dz);
                    if (n.InBounds(map)) dirty.Add(map.cellIndices.CellToIndex(n));
                }
            if (dirty.Count > Overflow) { overflow = true; dirty.Clear(); }
        }

        public CordWorld Base(Map map)
        {
            Uses++;
            LastPatched = 0;
            if (baseWorld != null && (baseWorld.Width != map.Size.x || baseWorld.Height != map.Size.z)) Invalidate("size");
            if (baseWorld != null && overflow) Invalidate("overflow");
            if (baseWorld != null)
            {
                foreach (int idx in dirty)
                {
                    if (!CordWorldAdapter.PatchCell(map, baseWorld, idx)) { Invalidate("cleared door/busy"); break; }
                    LastPatched++;
                }
            }
            dirty.Clear();
            if (baseWorld != null && ++sinceCheck >= CheckEvery)
            {
                sinceCheck = 0;
                CordWorld fresh = CordWorldAdapter.FullBase(map);
                FullScans++;
                int n = CordWorldAdapter.BaseDiff(baseWorld, fresh, out string first);
                if (n > 0) { Mismatches += n; LastMismatch = first; LastFullWhy = "check"; }
                baseWorld = fresh;
            }
            if (baseWorld == null)
            {
                baseWorld = CordWorldAdapter.FullBase(map);
                FullScans++;
                sinceCheck = 0;
            }
            return baseWorld;
        }
    }
}
