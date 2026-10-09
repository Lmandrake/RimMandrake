using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FLOOR_PAINT_1, spec §3.6 / §10 step 6.
    //
    // FLOORS have no comps, so this component owns a per-cell byte grid
    // `floorCoats` (Scribed, DataExposeUtility.LookByteArray). LIGHTS are
    // never saved (RM_DeepfireLightProxy is isSaveable=false): FinalizeInit
    // rebuilds every floor cluster from the grid, and coated Things re-register
    // from CompDeepfire.PostSpawnSetup, exactly as the engine rebuilds glowers.
    //
    // CLUSTERING: the map is tiled into fixed ClusterBlock x ClusterBlock
    // blocks (block = x / 3, z / 3). Inside one block, cells of the same KIND
    // (floor vs. 1x1 building), the same coat count and the same glow colour
    // share ONE proxy, placed on the group cell nearest the group's centroid,
    // radius = coat radius + ClusterRadiusBonus when the group holds 2+ cells.
    // A 6x6 floor whose corner sits on a multiple of 3 is therefore exactly
    // four proxies; an unaligned 6x6 straddles nine blocks and gets nine.
    // Floors and walls never merge (different kinds) so the floor proof's
    // proxy count is not disturbed by a painted wall around the room.
    public partial class MapComponent_DeepfireLights
    {
        private const byte KindFloor = DeepfireLightBook<Thing, Color>.KindFloor;
        private const byte KindBuilding = DeepfireLightBook<Thing, Color>.KindBuilding;

        // The light bookkeeping (floor grid, 3x3 blocks, anchors, own-vs-cluster routing) is the Verse-free kernel
        // Kernel/RM_DeepfireLightBook.cs; this component supplies the engine half through the delegates below.
        private DeepfireLightBook<Thing, Color> bookField;

        private DeepfireLightBook<Thing, Color> Book
        {
            get
            {
                if (bookField == null)
                {
                    bookField = new DeepfireLightBook<Thing, Color>(map.Size.x, map.Size.z,
                        () => LuminousPigmentSettings.clusterBlock,
                        coats => DeepfireColorUtility.RadiusForCoats(coats), DeepfirePaintDefaults.ClusterRadiusBonus,
                        FloorGlowAt, ThingViewOf,
                        (key, x, z, color, radius) => SetLight(key, new IntVec3(x, 0, z), color, radius),
                        key => RemoveLight(key),
                        (t, x, z, color, radius) => SetLight(t, new IntVec3(x, 0, z), color, radius),
                        t => RemoveLight(t));
                }
                return bookField;
            }
        }

        private DeepfireGlow<Color> FloorGlowAt(int x, int z, int coats)
        {
            Color glow = DeepfireColorUtility.GlowColorFor(FloorBaseColor(new IntVec3(x, 0, z)), coats);
            return new DeepfireGlow<Color> { Packed = PackColor(glow), Color = glow };
        }

        private DeepfireThingView<Color> ThingViewOf(Thing t)
        {
            var v = new DeepfireThingView<Color>();
            if (t == null || !t.Spawned || t.Map != map) return v;
            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            if (comp == null || comp.coats <= 0) return v;
            Color glow = DeepfireColorUtility.GlowColorFor(t.DrawColor, comp.coats);
            v.Live = true; v.Coats = comp.coats; v.X = t.Position.x; v.Z = t.Position.z;
            v.Glow = new DeepfireGlow<Color> { Packed = PackColor(glow), Color = glow };
            return v;
        }

        private static int PackColor(Color glow)
        {
            Color32 c32 = glow;
            return (c32.r << 24) | (c32.g << 16) | (c32.b << 8) | c32.a;
        }

        // ---- public floor API (designator, job, dev actions, Harmony hooks) ----

        public int CoatedFloorCellCount => bookField == null ? 0 : bookField.CoatedFloorCells;

        public int FloorCoatsAt(IntVec3 c)
        {
            return bookField == null ? 0 : bookField.FloorCoatsAt(c.x, c.z);
        }

        // Spec §3.3: "any floor cell with a floor terrain (TerrainDef.layerable
        // / IsFloor) with fewer than three coats in the floor grid".
        public static bool IsCoatableFloor(Map map, IntVec3 c)
        {
            if (map == null || !c.InBounds(map)) return false;
            TerrainDef top = map.terrainGrid.TopTerrainAt(c);
            return top != null && top.layerable;
        }

        // Spec §7 maxCoats ("the slider cannot exceed" the architecture ceiling) caps floors as it caps things.
        public static int FloorCoatCap => RM_DeepfireRules.CoatCap(CompDeepfire.MaxCoats, LuminousPigmentSettings.maxCoats);

        public bool CanAddFloorCoat(IntVec3 c)
        {
            return Book.CanAddFloorCoat(IsCoatableFloor(map, c), c.x, c.z, FloorCoatCap);
        }

        public bool AddFloorCoat(IntVec3 c)
        {
            if (!Book.AddFloorCoat(IsCoatableFloor(map, c), c.x, c.z, FloorCoatCap, out bool firstCoat)) return false;
            AfterFloorChanged(c);
            // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §5.2 "first coat on any
            // building/floor/item".
            if (firstCoat) DeepfireGodDeltas.OnFirstFloorCoat(map.terrainGrid.TopTerrainAt(c));
            return true;
        }

        // Spec §3.3 remove ("no refund") and §3.6 floor removed/replaced.
        public bool ClearFloorCoats(IntVec3 c)
        {
            if (bookField == null || !bookField.ClearFloorCoats(c.x, c.z)) return false;
            AfterFloorChanged(c);
            return true;
        }

        // SetTerrainColor postfix: recolour -> relight. A null ColorDef keeps
        // the coats; FloorBaseColor then falls back to the floor def's colour.
        public void Notify_FloorColorChanged(IntVec3 c)
        {
            if (FloorCoatsAt(c) <= 0) return;
            Book.NotifyFloorColorChanged(c.x, c.z);
        }

        // Glow colour source for a floor cell (spec §3.1: "Floors read
        // TerrainGrid.ColorAt(c)").
        public Color FloorBaseColor(IntVec3 c)
        {
            ColorDef cd = map.terrainGrid.ColorAt(c);
            if (cd != null) return cd.color;
            return map.terrainGrid.TopTerrainAt(c).DrawColor;
        }

        // Proof/diagnostic counters (dev actions read these).
        public int FloorLightCount => CountLights(KindFloor);
        public int ClusteredBuildingLightCount => CountLights(KindBuilding);
        public int TotalLightCount => entries.Count;

        public int CountCoatedFloorCells(IEnumerable<IntVec3> cells)
        {
            if (bookField == null) return 0;
            return bookField.CountCoated(CellsPacked(cells));
        }

        private static IEnumerable<long> CellsPacked(IEnumerable<IntVec3> cells)
        {
            foreach (IntVec3 c in cells) yield return DeepfireLightBook<Thing, Color>.Pack(c.x, c.z);
        }

        public List<string> DescribeFloorLights()
        {
            var list = new List<string>();
            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                if (!(kv.Key is DeepfireClusterKey k) || k.Kind != KindFloor) continue;
                CompGlower g = kv.Value.Proxy?.TryGetComp<CompGlower>();
                list.Add(string.Format("{0},{1} coats={2} radius={3:0.##} color={4}",
                    kv.Value.Cell.x, kv.Value.Cell.z, k.Coats, g?.GlowRadius ?? 0f,
                    g != null ? g.GlowColor.ToString() : "?"));
            }
            return list;
        }

        // DEEPFIRE_PROXY_BLOCKS_STORAGE_1 proof: the cells the floor proxies sit on.
        public List<IntVec3> FloorLightCells()
        {
            var list = new List<IntVec3>();
            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                if (kv.Key is DeepfireClusterKey k && k.Kind == KindFloor && kv.Value.Proxy != null && !kv.Value.Proxy.Destroyed)
                    list.Add(kv.Value.Proxy.Position);
            }
            return list;
        }

        // ---- building cluster membership ----

        private static bool IsClusterable(Thing t)
        {
            return DeepfireLightBook<Thing, Color>.Clusterable(LuminousPigmentSettings.clusterBlock,
                t.def.category == ThingCategory.Building, t.def.size.x, t.def.size.z);
        }

        private int CountLights(byte kind)
        {
            int n = 0;
            foreach (object key in entries.Keys)
            {
                if (key is DeepfireClusterKey k && k.Kind == kind) n++;
            }
            return n;
        }

        private void AfterFloorChanged(IntVec3 c)
        {
            // Room.GetStat caches until statsAndRoleDirty; a coat change is
            // not a terrain change, so the room must be told (RimSage:
            // Verse/Room.Notify_TerrainChanged sets statsAndRoleDirty).
            c.GetRoom(map)?.Notify_TerrainChanged();
        }

        private void ClearClusterState()
        {
            bookField?.ClearClusterState();
        }

        // DEEPFIRE_MOD_SETTINGS_1, spec §7 clusterBlock: block indices are
        // keyed off the block SIZE, so a live setting change leaves every
        // existing key stale. Rebuild every cluster from scratch -- the same
        // "floor grid + every coated Thing" FinalizeInit already does on map
        // load. Every coated building is re-routed (clustered at block size
        // above 1, a proxy of its own at 1) so none ends dark or double-lit.
        // Called from LuminousPigmentMod.ApplySettings() for every loaded map.
        public void RebuildAllClustering()
        {
            Book.RebuildAll(() =>
            {
                RegisterCoatedIn(map.listerBuildings.allBuildingsColonist);
                RegisterCoatedIn(map.listerBuildings.allBuildingsNonColonist);
            });
        }

        /// <summary>DEEPFIRE_SETTINGS_LIGHT_REFRESH_1: after a settings change, every light this mod owns on this map
        /// re-reads the current radius/intensity: building clusters (rebuilt), coated loose items, worn-gear proxies,
        /// and the RM_Deepfire stack glowers whose CompProperties_Glower ApplySettings mutates in place.</summary>
        public void RefreshAllLights()
        {
            RebuildAllClustering();
            List<Thing> haulables = map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver);
            for (int i = 0; i < haulables.Count; i++)
            {
                CompDeepfire comp = haulables[i].TryGetComp<CompDeepfire>();
                if (comp != null && comp.coats > 0 && haulables[i].Spawned) comp.RefreshLight();
            }
            tmpWornPawns.Clear();
            tmpWornPawns.AddRange(wornPawns.Keys);
            for (int i = 0; i < tmpWornPawns.Count; i++) RefreshWornPawn(tmpWornPawns[i]);
            wornSweptOnce = false; // next tick sweeps every pawn again (picks up gear that just became able to glow)
            ThingDef deepfire = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Deepfire");
            if (deepfire == null) return;
            List<Thing> stacks = map.listerThings.ThingsOfDef(deepfire);
            for (int i = 0; i < stacks.Count; i++)
            {
                CompGlower g = stacks[i].TryGetComp<CompGlower>();
                if (g != null && g.Glows && stacks[i].Spawned) g.ForceRegister(map); // only a lit glower is re-registered
            }
        }

        private void RegisterCoatedIn(List<Building> buildings)
        {
            if (buildings == null) return;
            for (int i = 0; i < buildings.Count; i++)
            {
                Thing t = buildings[i];
                CompDeepfire comp = t.TryGetComp<CompDeepfire>();
                if (comp == null || comp.coats <= 0) continue;
                comp.RefreshLight();
            }
        }

        // ---- persistence ----

        public override void ExposeData()
        {
            base.ExposeData();
            byte[] grid = bookField?.FloorGrid;
            DataExposeUtility.LookByteArray(ref grid, "rmDeepfireFloorCoats");
            if (Scribe.mode == LoadSaveMode.LoadingVars && grid != null) Book.FloorGrid = grid;
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (bookField != null && bookField.FloorGrid != null && bookField.FloorGrid.Length != map.cellIndices.NumGridCells)
            {
                Log.Warning("[LuminousPigment] Deepfire floor grid size does not match the map; coats dropped.");
            }
            // floor that vanished while we were not listening loses its coats; the ceiling clamps a hand-edited grid.
            Book.Finalize((x, z) => IsCoatableFloor(map, new IntVec3(x, 0, z)), CompDeepfire.MaxCoats);
        }
    }
}
