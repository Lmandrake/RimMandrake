using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// The power-network adapter: copies what the cord model reads out of a live Map into a
    /// Verse-free CordWorld (design §8.1 "How it reads the network"). Kept apart from the planner
    /// and the drawer on purpose (power_poles_and_flexible_pipe_assessment_2026-10-02.md): a later
    /// hose or suspended-wire adapter fills the same CordWorld from its own grids.
    /// </summary>
    public static class CordWorldAdapter
    {
        public static Cell C(IntVec3 c) => new Cell(c.x, c.z);
        public static IntVec3 I(Cell c) => new IntVec3(c.X, 0, c.Z);

        public static CordWorld Snapshot(Map map)
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
                if (pg.WalkableFast(idx)) continue;
                BlockKind k;
                if (ed != null)
                    k = ed.def.building != null && ed.def.building.isNaturalRock ? BlockKind.Rock :
                        ed.TryGetComp<CompPower>() != null ? BlockKind.Device : BlockKind.Wall;
                else
                {
                    TerrainDef t = map.terrainGrid.TerrainAt(idx);
                    k = t != null && t.IsWater ? BlockKind.Water : BlockKind.Wall;
                }
                world.SetBlocked(cell, k);
            }
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                if (p.def.plant != null && p.def.plant.IsTree) world.SetExtraCost(C(p.Position), 1.5f);

            var transmitterBuildings = new List<CompPower>();
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
                if (m.Hookups.Count > 0) world.Machines.Add(m);
            }
            // connectors (consumers, generators, lamps, batteries wired by a hookup)
            foreach (CompPower c in connectors)
            {
                CompPower parent = c.connectParent;
                if (parent?.parent == null || !ConduitVisuals.IsTarget(parent.parent.def)) continue;
                Thing th = c.parent;
                var m = new MachineInfo { Id = "c" + th.thingIDNumber, Kind = KindOf(c, false) };
                CellRect r = th.OccupiedRect();
                m.X0 = r.minX; m.Z0 = r.minZ; m.W = r.Width; m.H = r.Height;
                m.Hookups.Add(C(parent.parent.Position));
                world.Machines.Add(m);
            }
            return world;
        }

        private static MachineKind KindOf(CompPower c, bool transmitter)
        {
            if (c is CompPowerPlant) return MachineKind.Source;
            if (c is CompPowerBattery) return MachineKind.Battery;
            if (transmitter) return MachineKind.Transmitter;
            return MachineKind.Consumer;
        }

        /// <summary>live = the net at that cell has an active power source (design §8.5).</summary>
        public static bool IsLive(Map map, Cell c)
        {
            IntVec3 v = I(c);
            if (!v.InBounds(map)) return false;
            PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(v);
            return net != null && net.HasActivePowerSource;
        }
    }
}
