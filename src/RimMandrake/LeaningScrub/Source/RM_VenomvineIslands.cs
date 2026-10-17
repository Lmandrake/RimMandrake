using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // VENOMVINE_BUILD_SCRUB_GROWS_TEETH — design/RimMandrake/venomvine_design_2026-10-16.md, §10 RULED (owner, cards
    // 2026-10-16):
    //   Q1 islands at about 15% of open ground (map step; 8-14 islands, scaled up to reach the share)
    //   Q3 its own slow creep downwind, capped (default 22%), OUTSIDE Explosive Growth
    //   Q4 the rarer forms live as rooms inside the islands
    // The map step (RM_GenStep_VenomvineIslands) and the creep (RM_MapComponent_VenomvineCreep) both run only on maps
    // whose biome carries RM_VenomvineIslandsExtension (RM_LeaningScrub), so nothing here reaches another biome.
    // Pure logic: Kernel/RM_IslandKernel.cs (offline-tested). Explosive Growth exemption: Defs/ExplosiveGrowth/
    // RM_LeaningScrub_ExplosiveGrowthExempt.xml (a roster def of our own; the engine unions every roster).
    // ════════════════════════════════════════════════════════════════════

    public class RM_IslandRoom
    {
        public ThingDef form;
        /// <summary>edge | interior | downwind</summary>
        public string role = "edge";
        public float weight = 1f;
        public IntRange cells = new IntRange(2, 5);

        public int Role => role == "interior" ? RM_IslandKernel.RoleInterior
            : role == "downwind" ? RM_IslandKernel.RoleDownwind : RM_IslandKernel.RoleEdge;
    }

    /// <summary>On a BiomeDef: this biome grows venomvine islands and lets them creep. All data; numbers the player tunes
    /// are Mod Settings (RM_LeaningScrubSettings.venomvine*).</summary>
    public class RM_VenomvineIslandsExtension : DefModExtension
    {
        public ThingDef thicketDef;
        public ThingDef crownDef;
        /// <summary>Every venomvine def that counts toward the share and the cap (the body and all forms).</summary>
        public List<ThingDef> countedForms = new List<ThingDef>();
        public List<RM_IslandRoom> rooms = new List<RM_IslandRoom>();
        public int minIslandCells = 40;
        /// <summary>Cells kept between two islands (Chebyshev), so corridors stay open.</summary>
        public int gap = 2;
        /// <summary>How much longer than wide an island is, along the Lean.</summary>
        public float stretch = 1.6f;
        public FloatRange bodyGrowth = new FloatRange(0.6f, 1f);
        /// <summary>A fresh runner's growth: under half grown it carries no venom (CompProperties_ContactVenom.minGrowth).</summary>
        public float runnerGrowth = 0.05f;
        public int maxRunnersPerSweep = 300;
        /// <summary>Open ground reachable from the start may shrink by the island's own cells plus this share of open
        /// ground before the island is refused as cutting the map apart.</summary>
        public float traversalSlack = 0.01f;
    }

    public static class RM_VenomvineIslandsUtil
    {
        public static RM_VenomvineIslandsExtension For(Map map) => map?.Biome?.GetModExtension<RM_VenomvineIslandsExtension>();

        public static HashSet<ThingDef> Counted(RM_VenomvineIslandsExtension ext)
        {
            var set = new HashSet<ThingDef>();
            if (ext == null) return set;
            if (ext.thicketDef != null) set.Add(ext.thicketDef);
            if (ext.crownDef != null) set.Add(ext.crownDef);
            foreach (ThingDef d in ext.countedForms) if (d != null) set.Add(d);
            foreach (RM_IslandRoom r in ext.rooms) if (r?.form != null) set.Add(r.form);
            return set;
        }

        /// <summary>Open ground: walkable, not water, not under a roof. The share and the cap are measured against it.</summary>
        public static bool Open(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            return t != null && !t.IsWater && c.Walkable(map) && !c.Roofed(map);
        }

        public static int CountOpen(Map map)
        {
            int n = 0;
            foreach (IntVec3 c in map.AllCells) if (Open(c, map)) n++;
            return n;
        }

        public static int CountVine(Map map, HashSet<ThingDef> vine)
        {
            int n = 0;
            List<Thing> plants = map.listerThings.ThingsInGroup(ThingRequestGroup.Plant);
            for (int i = 0; i < plants.Count; i++) if (vine.Contains(plants[i].def)) n++;
            return n;
        }

        /// <summary>Natural ground venomvine may take: not a floor, no floor laid over it, no building, no zone, not under
        /// a roof, and no tree, sown plant or venomvine already there (other wild plants are overgrown).</summary>
        public static bool NaturalFree(IntVec3 c, Map map, ThingDef plantDef, HashSet<ThingDef> vine)
        {
            if (!c.InBounds(map) || c.Roofed(map) || c.GetFirstBuilding(map) != null || c.GetZone(map) != null) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater || t.BuildableByPlayer || map.terrainGrid.UnderTerrainAt(c) != null) return false;
            Plant p = c.GetPlant(map);
            if (p != null && (p.def.plant == null || p.def.plant.IsTree || p.sown || vine.Contains(p.def))) return false;
            return plantDef.CanEverPlantAt(c, map, canWipePlantsExceptTree: true);
        }

        public static Plant Place(Map map, IntVec3 c, ThingDef def, float growth)
        {
            Plant old = c.GetPlant(map);
            if (old != null)
            {
                if (old.def.plant != null && old.def.plant.IsTree) return null;
                old.Destroy(DestroyMode.Vanish);
            }
            Plant p = (Plant)ThingMaker.MakeThing(def);
            p.Growth = Mathf.Clamp01(growth);
            GenSpawn.Spawn(p, c, map);
            return p;
        }
    }

    // ── the map step ──
    public class RM_GenStep_VenomvineIslands : GenStep
    {
        public override int SeedPart => 551902417;

        public override void Generate(Map map, GenStepParams parms)
        {
            RM_VenomvineIslandsExtension ext = RM_VenomvineIslandsUtil.For(map);
            if (ext?.thicketDef == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.venomvineIslandsEnabled))
            {
                return;
            }
            Lay(map, ext, MapGenerator.PlayerStartSpotValid ? MapGenerator.PlayerStartSpot : map.Center);
        }

        public class LayResult
        {
            public int open, target, planned, islands, planted, rooms, reachBefore, reachAfter;
        }

        /// <summary>The whole step on one map (the proof calls it on a live map with an explicit start).</summary>
        public static LayResult Lay(Map map, RM_VenomvineIslandsExtension ext, IntVec3 start)
        {
            var res = new LayResult();
            int w = map.Size.x, h = map.Size.z, n = w * h;
            HashSet<ThingDef> vine = RM_VenomvineIslandsUtil.Counted(ext);
            float clear = Mathf.Max(0f, RM_LeaningScrubSettings.venomvineStartClearance);
            List<CellRect> used = MapGenerator.UsedRects;

            var allowed = new bool[n];
            var passable = new bool[n];
            var owner = new int[n];
            int open = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                int i = c.z * w + c.x;
                owner[i] = -1;
                passable[i] = c.Walkable(map);
                if (!RM_VenomvineIslandsUtil.Open(c, map)) continue;
                open++;
                if (c.DistanceToSquared(start) < clear * clear) continue;
                if (InUsed(c, used) || NearBuilding(c, map)) continue;
                allowed[i] = RM_VenomvineIslandsUtil.NaturalFree(c, map, ext.thicketDef, vine);
            }

            int target = RM_IslandKernel.TargetCells(open, RM_LeaningScrubSettings.venomvineIslandShare);
            int lo = Mathf.Min(RM_LeaningScrubSettings.venomvineIslandsMin, RM_LeaningScrubSettings.venomvineIslandsMax);
            int hi = Mathf.Max(RM_LeaningScrubSettings.venomvineIslandsMin, RM_LeaningScrubSettings.venomvineIslandsMax);
            int count = RM_IslandKernel.IslandCount(target, Rand.RangeInclusive(lo, hi), ext.minIslandCells,
                RM_LeaningScrubSettings.venomvineIslandMaxCells);
            var sizes = new List<int>();
            RM_IslandKernel.SizeIslands(target, count, ext.minIslandCells, RM_LeaningScrubSettings.venomvineIslandMaxCells,
                () => Rand.Value, sizes);

            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            Vector2 wind = lean != null ? lean.Downwind : Vector2.zero;
            int startX = Mathf.Clamp(start.x, 0, w - 1), startZ = Mathf.Clamp(start.z, 0, h - 1);
            int reach = RM_IslandKernel.Reach(w, h, passable, owner, startX, startZ);
            res.reachBefore = reach;
            int slack = Mathf.RoundToInt(open * ext.traversalSlack);

            var candidates = new List<int>();
            for (int i = 0; i < n; i++) if (allowed[i]) candidates.Add(i);
            var islands = new List<List<int>>();
            var cells = new List<int>();
            int laid = 0;
            for (int k = 0; k < sizes.Count && candidates.Count > 0; k++)
            {
                int id = islands.Count;
                for (int attempt = 0; attempt < 12; attempt++)
                {
                    int seed = candidates[Rand.Range(0, candidates.Count)];
                    int got = RM_IslandKernel.Grow(w, h, allowed, owner, id, seed % w, seed / w, sizes[k], ext.gap,
                        wind.x, wind.y, ext.stretch, () => Rand.Value, cells);
                    if (got < Mathf.Min(ext.minIslandCells, sizes[k]) / 2)
                    {
                        RM_IslandKernel.Ungrow(owner, cells);
                        continue;
                    }
                    int island = 0;
                    for (int c = 0; c < cells.Count; c++) if (passable[cells[c]]) island++;
                    int after = RM_IslandKernel.Reach(w, h, passable, owner, startX, startZ);
                    if (!RM_IslandKernel.KeepsTraversable(reach, after, island, slack))
                    {
                        RM_IslandKernel.Ungrow(owner, cells);
                        continue;
                    }
                    reach = after;
                    islands.Add(new List<int>(cells));
                    laid += cells.Count;
                    break;
                }
            }

            // Body, then rooms.
            int planted = 0;
            foreach (List<int> isl in islands)
            {
                foreach (int i in isl)
                {
                    if (RM_VenomvineIslandsUtil.Place(map, new IntVec3(i % w, 0, i / w), ext.thicketDef, ext.bodyGrowth.RandomInRange) != null)
                    {
                        planted++;
                    }
                }
            }
            int rooms = 0;
            if (RM_LeaningScrubSettings.venomvineIslandRoomsEnabled)
            {
                rooms = PlaceRooms(map, ext, islands, owner, w, h, wind);
            }
            res.open = open; res.target = target; res.planned = count; res.islands = islands.Count;
            res.planted = planted; res.rooms = rooms; res.reachAfter = reach;
            Log.Message("[RM LeaningScrub] venomvine islands: " + islands.Count + " islands (" + count + " planned), "
                + planted + " cells of " + target + " target (" + open + " open, share "
                + RM_LeaningScrubSettings.venomvineIslandShare.ToString("0.00") + "), " + rooms + " rooms");
            return res;
        }

        private static bool InUsed(IntVec3 c, List<CellRect> used)
        {
            if (used == null) return false;
            for (int i = 0; i < used.Count; i++) if (used[i].Contains(c)) return true;
            return false;
        }

        private static bool NearBuilding(IntVec3 c, Map map)
        {
            for (int i = 0; i < 9; i++)
            {
                IntVec3 a = c + GenAdj.AdjacentCellsAndInside[i];
                if (a.InBounds(map) && a.GetFirstBuilding(map) != null) return true;
            }
            List<Thing> here = map.thingGrid.ThingsListAt(c);
            for (int i = 0; i < here.Count; i++)
            {
                ThingCategory cat = here[i].def.category;
                if (cat == ThingCategory.Item || cat == ThingCategory.Pawn) return true;
            }
            return false;
        }

        private static int PlaceRooms(Map map, RM_VenomvineIslandsExtension ext, List<List<int>> islands, int[] owner, int w, int h, Vector2 wind)
        {
            var table = new List<RM_IslandRoom>();
            foreach (RM_IslandRoom r in ext.rooms) if (r?.form != null && r.weight > 0f) table.Add(r);
            float[] weights = new float[table.Count];
            for (int i = 0; i < table.Count; i++) weights[i] = table[i].weight;
            var roomed = new HashSet<int>();
            int placed = 0;
            int biggest = -1;
            for (int k = 0; k < islands.Count; k++)
            {
                List<int> isl = islands[k];
                if (biggest < 0 || isl.Count > islands[biggest].Count) biggest = k;
                if (table.Count == 0) continue;
                double alongMin = double.MaxValue, alongMax = double.MinValue;
                foreach (int c in isl)
                {
                    double a = (c % w) * wind.x + (c / w) * wind.y;
                    if (a < alongMin) alongMin = a;
                    if (a > alongMax) alongMax = a;
                }
                int want = RM_IslandKernel.RoomCount(isl.Count, Rand.Value);
                for (int r = 0; r < want; r++)
                {
                    int row = RM_IslandKernel.PickWeighted(weights, Rand.Value);
                    if (row < 0) break;
                    RM_IslandRoom room = table[row];
                    int anchor = -1;
                    for (int t = 0; t < 40 && anchor < 0; t++)
                    {
                        int c = isl[Rand.Range(0, isl.Count)];
                        if (!roomed.Contains(c) && RM_IslandKernel.RoleFits(room.Role, w, h, owner, k, c, wind.x, wind.y, alongMin, alongMax))
                        {
                            anchor = c;
                        }
                    }
                    if (anchor < 0) continue;
                    int size = room.cells.RandomInRange;
                    var queue = new Queue<int>();
                    queue.Enqueue(anchor);
                    var seen = new HashSet<int> { anchor };
                    int done = 0;
                    while (queue.Count > 0 && done < size)
                    {
                        int c = queue.Dequeue();
                        if (roomed.Contains(c)) continue;
                        IntVec3 cell = new IntVec3(c % w, 0, c / w);
                        if (room.form.CanEverPlantAt(cell, map, canWipePlantsExceptTree: true)
                            && RM_VenomvineIslandsUtil.Place(map, cell, room.form, ext.bodyGrowth.RandomInRange) != null)
                        {
                            roomed.Add(c);
                            done++;
                        }
                        int cx = c % w, cz = c / w;
                        for (int d = 0; d < 4; d++)
                        {
                            int nx = cx + (d == 0 ? 1 : d == 1 ? -1 : 0), nz = cz + (d == 2 ? 1 : d == 3 ? -1 : 0);
                            if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                            int nb = nz * w + nx;
                            if (owner[nb] == k && seen.Add(nb)) queue.Enqueue(nb);
                        }
                    }
                    if (done > 0) placed++;
                }
            }
            // The Crown: the heart of the biggest island, one per map at most.
            if (ext.crownDef != null && biggest >= 0)
            {
                int heart = RM_IslandKernel.Heart(w, h, owner, biggest, islands[biggest]);
                if (heart >= 0 && !roomed.Contains(heart))
                {
                    IntVec3 cell = new IntVec3(heart % w, 0, heart / w);
                    if (ext.crownDef.CanEverPlantAt(cell, map, canWipePlantsExceptTree: true)
                        && RM_VenomvineIslandsUtil.Place(map, cell, ext.crownDef, 1f) != null)
                    {
                        placed++;
                    }
                }
            }
            return placed;
        }
    }

    // ── the creep ──
    public class RM_CompProperties_VenomvineCreep : CompProperties
    {
        public RM_CompProperties_VenomvineCreep()
        {
            compClass = typeof(RM_CompVenomvineCreep);
        }
    }

    /// <summary>Marks a venomvine form that creeps (puts thicket runners), and says so on inspect: the readable sign.</summary>
    public class RM_CompVenomvineCreep : ThingComp
    {
        public override string CompInspectStringExtra()
        {
            Map map = parent.Map;
            if (map == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.venomvineCreepEnabled)) return null;
            RM_MapComponent_VenomvineCreep creep = map.GetComponent<RM_MapComponent_VenomvineCreep>();
            if (creep == null || !creep.Applies) return null;
            string share = creep.ShareText();
            if (creep.AtCap)
            {
                return "Venomvine is at this map's cap (" + share + "): it spreads again when some is cut, burned or smothered.";
            }
            if (parent is Plant p && p.LifeStage != PlantLifeStage.Mature)
            {
                return "Spreads once fully grown. Venomvine covers " + share + ".";
            }
            return "Spreading: about one runner every " + RM_LeaningScrubSettings.venomvineCreepDays.ToString("0")
                + " days, mostly downwind. Venomvine covers " + share + ".";
        }
    }

    public class RM_MapComponent_VenomvineCreep : MapComponent
    {
        public const int SweepTicks = 15000; // six in-game hours (plants only tick every ~33 s)
        private const int OpenRecountSweeps = 4;

        private int openCells = -1;
        private int vineCells;
        private int sweepsSinceOpen;
        private bool? applies;
        private HashSet<ThingDef> vine;
        private static readonly int[] Dx = { 1, 1, 0, -1, -1, -1, 0, 1 };
        private static readonly int[] Dz = { 0, 1, 1, 1, 0, -1, -1, -1 };
        private readonly bool[] free = new bool[8];
        private readonly List<Plant> tmp = new List<Plant>();

        public RM_MapComponent_VenomvineCreep(Map map) : base(map)
        {
        }

        public bool Applies
        {
            get
            {
                if (!applies.HasValue) applies = RM_VenomvineIslandsUtil.For(map)?.thicketDef != null;
                return applies.Value;
            }
        }

        public int OpenCells => openCells;
        public int VineCells => vineCells;
        public bool AtCap => openCells > 0 && RM_IslandKernel.CapRoom(vineCells, openCells, RM_LeaningScrubSettings.venomvineCreepCap) == 0;

        public string ShareText()
        {
            if (openCells <= 0) Recount(true);
            float s = openCells > 0 ? vineCells / (float)openCells : 0f;
            return s.ToStringPercent("0") + " of open ground; it stops at " + RM_LeaningScrubSettings.venomvineCreepCap.ToStringPercent("0");
        }

        public override void MapComponentTick()
        {
            if (((Find.TickManager.TicksGame + map.uniqueID * 1777) % SweepTicks) != 0) return;
            TickSweep(SweepTicks, null);
        }

        /// <summary>The gated pass the tick runs: nothing when creep is off or (unless forced) on another biome.</summary>
        public int TickSweep(int sweepTicks, RM_VenomvineIslandsExtension forced, Plant only = null)
        {
            if ((forced == null && !Applies) || !RM_WindCalendar.On(RM_LeaningScrubSettings.venomvineCreepEnabled)) return 0;
            return Sweep(sweepTicks, forced, only);
        }

        private void Recount(bool open, RM_VenomvineIslandsExtension forced = null)
        {
            RM_VenomvineIslandsExtension ext = forced ?? RM_VenomvineIslandsUtil.For(map);
            if (vine == null) vine = RM_VenomvineIslandsUtil.Counted(ext);
            if (open || openCells < 0)
            {
                openCells = RM_VenomvineIslandsUtil.CountOpen(map);
                sweepsSinceOpen = 0;
            }
            vineCells = RM_VenomvineIslandsUtil.CountVine(map, vine);
        }

        /// <summary>One creep pass. sweepTicks sets the runner chance (a proof can pass a large value). Returns runners laid.
        /// only (proof use): offer just this stand. A proof's chance-1 sweep over a map that already holds hundreds of
        /// mature stands spends maxRunnersPerSweep on the first ones in list order and never reaches a freshly placed test
        /// stand (live walk 2026-10-17: laid=300, besideTestStand=0).</summary>
        public int Sweep(int sweepTicks, RM_VenomvineIslandsExtension forced = null, Plant only = null)
        {
            RM_VenomvineIslandsExtension ext = forced ?? RM_VenomvineIslandsUtil.For(map);
            if (ext?.thicketDef == null) return 0;
            Recount(++sweepsSinceOpen >= OpenRecountSweeps || openCells < 0, forced);
            int room = RM_IslandKernel.CapRoom(vineCells, openCells, RM_LeaningScrubSettings.venomvineCreepCap);
            room = Mathf.Min(room, Mathf.Max(0, ext.maxRunnersPerSweep));
            if (room <= 0) return 0;
            double chance = RM_IslandKernel.RunnerChance(sweepTicks, RM_LeaningScrubSettings.venomvineCreepDays);
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            Vector2 wind = lean != null ? lean.Downwind : Vector2.zero;

            tmp.Clear();
            List<Thing> plants = map.listerThings.ThingsInGroup(ThingRequestGroup.Plant);
            for (int i = 0; i < plants.Count; i++)
            {
                if (plants[i] is Plant p && (only == null || p == only) && p.Spawned && p.LifeStage == PlantLifeStage.Mature
                    && p.GetComp<RM_CompVenomvineCreep>() != null)
                {
                    RM_CompSmotherable sm = p.GetComp<RM_CompSmotherable>();
                    if (sm == null || !sm.Smothered) tmp.Add(p);
                }
            }
            int laid = 0;
            for (int i = 0; i < tmp.Count && laid < room; i++)
            {
                if (!Rand.Chance((float)chance)) continue;
                IntVec3 at = tmp[i].Position;
                for (int k = 0; k < 8; k++)
                {
                    free[k] = RM_VenomvineIslandsUtil.NaturalFree(new IntVec3(at.x + Dx[k], 0, at.z + Dz[k]), map, ext.thicketDef, vine);
                }
                int pick = RM_IslandKernel.PickNeighbour(Dx, Dz, free, 8, wind.x, wind.y,
                    RM_LeaningScrubSettings.venomvineCreepDownwindShare, Rand.Value, Rand.Value);
                if (pick < 0) continue;
                if (RM_VenomvineIslandsUtil.Place(map, new IntVec3(at.x + Dx[pick], 0, at.z + Dz[pick]), ext.thicketDef, ext.runnerGrowth) != null)
                {
                    laid++;
                    vineCells++;
                }
            }
            return laid;
        }
    }
    // ── proof hooks (validation.py chain "islands"; jawa/static_call) ──
    public static class RM_VenomvineIslandsProof
    {
        private static RM_VenomvineIslandsExtension ScrubExt(Map map)
        {
            return RM_VenomvineIslandsUtil.For(map)
                ?? DefDatabase<BiomeDef>.GetNamedSilentFail("RM_LeaningScrub")?.GetModExtension<RM_VenomvineIslandsExtension>();
        }

        /// <summary>Runs the SHIPPED map step on the current (disposable) map with the colonists' centre as the start and
        /// reads back: the laid share, that the start clearance holds, and that the start can still reach most open ground.</summary>
        public static string ProofIslands()
        {
            Map map = Find.CurrentMap;
            RM_VenomvineIslandsExtension ext = ScrubExt(map);
            if (map == null || ext?.thicketDef == null) return "UNMEASURED: no map or no RM_LeaningScrub island extension loaded";
            IntVec3 start = map.mapPawns.FreeColonistsSpawnedCount > 0 ? map.mapPawns.FreeColonistsSpawned[0].Position : map.Center;
            HashSet<ThingDef> vine = RM_VenomvineIslandsUtil.Counted(ext);
            int before = RM_VenomvineIslandsUtil.CountVine(map, vine);
            RM_GenStep_VenomvineIslands.LayResult r = RM_GenStep_VenomvineIslands.Lay(map, ext, start);
            int after = RM_VenomvineIslandsUtil.CountVine(map, vine);
            float clear = RM_LeaningScrubSettings.venomvineStartClearance;
            int inClear = 0;
            List<Thing> plants = map.listerThings.ThingsInGroup(ThingRequestGroup.Plant);
            for (int i = 0; i < plants.Count; i++)
            {
                if (vine.Contains(plants[i].def) && plants[i].Position.DistanceToSquared(start) < clear * clear * 0.81f) inClear++;
            }
            string data = "islands=" + r.islands + " planned=" + r.planned + " planted=" + r.planted + " target=" + r.target
                + " open=" + r.open + " rooms=" + r.rooms + " reach=" + r.reachBefore + "->" + r.reachAfter
                + " vine=" + before + "->" + after + " vineNearStart=" + inClear;
            if (r.target <= 0) return "UNMEASURED: no open ground measured " + data;
            if (r.planted < r.target * 0.5f) return "FAIL: laid under half the target share " + data;
            if (r.reachAfter < (r.reachBefore - r.planted) * 0.9f) return "FAIL: the islands cut the start off from open ground " + data;
            if (r.islands > 0 && r.rooms < 1 && RM_LeaningScrubSettings.venomvineIslandRoomsEnabled) return "FAIL: no room in any island " + data;
            return "PASS " + data;
        }

        /// <summary>mode on|off|cap. Plants one grown thicket on open natural ground, drives the gated creep pass with a
        /// sweep long enough that every grown stand rolls a runner, and reads back the runner (on), none (off: creep
        /// disabled; cap: cap set to the current share). The runner must be under half grown, so unarmed.</summary>
        public static string ProofCreep(string mode)
        {
            Map map = Find.CurrentMap;
            RM_VenomvineIslandsExtension ext = ScrubExt(map);
            if (map == null || ext?.thicketDef == null) return "UNMEASURED: no map or no island extension";
            RM_MapComponent_VenomvineCreep creep = map.GetComponent<RM_MapComponent_VenomvineCreep>();
            HashSet<ThingDef> vine = RM_VenomvineIslandsUtil.Counted(ext);
            IntVec3 site = IntVec3.Invalid;
            for (int t = 0; t < 400 && !site.IsValid; t++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                bool ok = !c.CloseToEdge(map, 3) && RM_VenomvineIslandsUtil.NaturalFree(c, map, ext.thicketDef, vine);
                for (int k = 0; ok && k < 8; k++) ok = RM_VenomvineIslandsUtil.NaturalFree(c + GenAdj.AdjacentCells[k], map, ext.thicketDef, vine);
                if (ok) site = c;
            }
            if (!site.IsValid) return "UNMEASURED: no open natural ground with eight free neighbours";
            bool sOn = RM_LeaningScrubSettings.venomvineCreepEnabled;
            float sCap = RM_LeaningScrubSettings.venomvineCreepCap;
            Plant mother = RM_VenomvineIslandsUtil.Place(map, site, ext.thicketDef, 1f);
            var runners = new List<Plant>();
            try
            {
                if (mother == null || mother.LifeStage != PlantLifeStage.Mature) return "UNMEASURED: the test stand is not mature";
                RM_LeaningScrubSettings.venomvineCreepEnabled = mode != "off";
                if (mode == "cap")
                {
                    int open = RM_VenomvineIslandsUtil.CountOpen(map), now = RM_VenomvineIslandsUtil.CountVine(map, vine);
                    RM_LeaningScrubSettings.venomvineCreepCap = open > 0 ? now / (float)open : 0f;
                }
                // a sweep 1000 x the runner interval: chance 1 per stand; one runner per stand per pass
                int laid = creep.TickSweep(RM_MapComponent_VenomvineCreep.SweepTicks * 4000, ext, mother);
                for (int k = 0; k < 8; k++)
                {
                    Plant p = (site + GenAdj.AdjacentCells[k]).GetPlant(map);
                    if (p != null && p.def == ext.thicketDef) runners.Add(p);
                }
                string data = "mode=" + mode + " laid=" + laid + " besideTestStand=" + runners.Count
                    + (runners.Count > 0 ? " runnerGrowth=" + runners[0].Growth.ToString("0.00") : "");
                if (mode == "on")
                {
                    if (runners.Count < 1) return "FAIL: a grown stand put no runner " + data;
                    if (runners[0].Growth >= 0.5f) return "FAIL: the runner is armed (growth >= 0.5) " + data;
                    return "PASS " + data;
                }
                return laid == 0 && runners.Count == 0 ? "PASS " + data : "FAIL: creep ran with " + mode + " " + data;
            }
            finally
            {
                RM_LeaningScrubSettings.venomvineCreepEnabled = sOn;
                RM_LeaningScrubSettings.venomvineCreepCap = sCap;
                for (int i = 0; i < runners.Count; i++) if (runners[i].Spawned) runners[i].Destroy(DestroyMode.Vanish);
                if (mother != null && mother.Spawned) mother.Destroy(DestroyMode.Vanish);
            }
        }

        /// <summary>Explosive Growth leaves venomvine alone: our roster def is loaded (when the engine is).</summary>
        public static string ProofExempt()
        {
            System.Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef");
            if (t == null) return "UNMEASURED: Explosive Growth is not loaded";
            Def d = GenDefDatabase.GetDefSilentFail(t, "RM_LeaningScrub_VenomvineExempt", false);
            return d != null ? "PASS roster RM_LeaningScrub_VenomvineExempt loaded" : "FAIL: the venomvine exemption roster did not load";
        }
    }
}
