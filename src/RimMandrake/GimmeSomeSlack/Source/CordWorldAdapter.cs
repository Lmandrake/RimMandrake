using System.Collections.Generic;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using Verse;
using Verse.AI;

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
                if (how == HookupDraw.ConduitCell)
                {
                    if (!world.IsConduit(C(pt.Position))) continue;     // a fogged conduit cell is not in the snapshot
                    m.Hookups.Add(C(pt.Position));
                    world.Machines.Add(m);
                }
                else if (transmitterMachines.TryGetValue(pt, out MachineInfo tm)) CordWorldLinks.LinkToMachine(world, m, tm);
            }
            AddTapNodes(map, world);
            return world;
        }

        /// <summary>Round 3 (owner 2026-10-04): "the power tap should be considered a Node that both power systems now must
        /// connect with their cables". The clamp is a connector of OUR net (its machine already hooks our conduit when it has a
        /// connectParent); here it also hooks the conduit cell it bites, or links the foreign transmitter building it bites,
        /// so THEIR cable runs into the clamp instead of ending beside it as a free sparking end. Draw-only: the power nets
        /// are untouched (the two grids never merge; CompPowerTap moves the energy).</summary>
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
        public static void SetWallHome(Thing th, MachineInfo m)
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
        public static bool IsLive(Map map, Cell c)
        {
            IntVec3 v = I(c);
            if (!v.InBounds(map)) return false;
            PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(v);
            return net != null && net.HasActivePowerSource;
        }
    }
}
