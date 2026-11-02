using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.TileFeatures
{
    // VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY (design/RimMandrake/vee_port_plan_2026-10-22.md group L): the map-shaping
    // workers for the landform tile features ported from Vanilla Exploration Expanded. Rebuilt from VEE's def fields and
    // descriptions and from vanilla 1.6 workers; no VEE C# was read. Every number lives in the def's RM_LandformExtension,
    // so one worker serves several rows. Geometry is in RM_LandformGeometry (unit-tested in SelfTest/).

    public class RM_TerrainSwap
    {
        public TerrainDef from;
        public TerrainDef to;
    }

    public class RM_LandformExtension : DefModExtension
    {
        // what the tile falls back to when the landforms switch is off (null = no worker): a river or coast port must keep
        // its river or coast, because the port displaced vanilla's own river/coast mutator on that tile
        public Type offWorkerClass;

        // terrains, read by whichever worker uses them
        public TerrainDef deepTerrain;     // lake deep water / crater pool core / scatter disc core
        public TerrainDef shallowTerrain;  // lake shallow water / crater pool edge / river moving water
        public TerrainDef shoreTerrain;    // lake shore band
        public TerrainDef outerTerrain;    // a wider band around a lake (dust bowl, salt plains)
        public float outerThreshold = 0.35f;
        public TerrainDef floorTerrain;    // crater basin / carved canyon floor
        public TerrainDef lipTerrain;      // scatter disc lip
        public TerrainDef bankTerrain;     // widened river bank
        public List<RM_TerrainSwap> swaps = new List<RM_TerrainSwap>();

        // lake
        public float lakeRadius = 0.6f;
        public bool deepWater = true;

        // river: extra bank band (cells) laid with bankTerrain beyond vanilla's own bank
        public int bankWidth;

        // crater
        public FloatRange radiusFraction = new FloatRange(0.22f, 0.3f);
        public float rimWidth = 0.2f;
        public float poolFraction;
        public float domeFraction;
        public int rimBreaches = 2;
        public float breachHalfWidth = 0.12f; // radians

        // lines (ridges, jagged rocks, canyons)
        public IntRange lineCount = new IntRange(1, 1);
        public FloatRange lineHalfWidth = new FloatRange(3f, 4f);
        public FloatRange meanderAmplitude = new FloatRange(6f, 14f);
        public FloatRange meanderWaves = new FloatRange(1f, 2f);
        public float lineElevation = 1f;     // 1 raises rock, 0 carves it out
        public float baseElevation = -1f;    // >= 0: the whole map is set to this first (canyons: solid mountain)
        public int gapLength;                // cells of open ground left in each line (a pass through a ridge)

        // scatter (cenotes, sinkholes, spires)
        public FloatRange discsPer10kCells = new FloatRange(1f, 4f);
        public IntRange discRadius = new IntRange(2, 4);
        public int discSpacing = 4;
        public int discLip = 1;
        public float discElevation = -1f;    // >= 0: the disc is raised (spires) instead of laid with terrain

        // things spawned on a terrain after generation (radioactive barrels)
        public ThingDef thingToSpawn;
        public IntRange thingToSpawnAmount = IntRange.Zero;
        public TerrainDef thingTerrain;

        // snow laid at the end of generation on unroofed land (deep snow)
        public float snowDepth = -1f;

        public static RM_LandformExtension Of(TileMutatorDef def)
        {
            return def?.GetModExtension<RM_LandformExtension>();
        }
    }

    public static class RM_LandformUtil
    {
        public static bool HasRivers(Map map)
        {
            return map?.TileInfo is SurfaceTile st && st.Rivers != null && st.Rivers.Count > 0;
        }

        public static bool IsOpenLand(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            return t != null && !t.IsWater && t.categoryType != TerrainDef.TerrainCategoryType.Stone && c.GetEdifice(map) == null;
        }

        /// <summary>Spawns ext.thingToSpawn on random open cells of ext.thingTerrain (VEE's contaminated barrels).</summary>
        public static void ScatterThings(Map map, RM_LandformExtension ext)
        {
            if (ext?.thingToSpawn == null || ext.thingToSpawnAmount.max <= 0) return;
            List<IntVec3> cells = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
                if ((ext.thingTerrain == null || c.GetTerrain(map) == ext.thingTerrain) && c.Standable(map)
                    && c.GetFirstItem(map) == null && c.GetEdifice(map) == null)
                    cells.Add(c);
            cells.Shuffle();
            int n = Math.Min(cells.Count, ext.thingToSpawnAmount.RandomInRange);
            for (int i = 0; i < n; i++)
                GenSpawn.Spawn(ThingMaker.MakeThing(ext.thingToSpawn), cells[i], map);
        }

        /// <summary>After vanilla's river pass: cells that became moving water get the port's water, and with bankWidth the
        /// bank is widened with bankTerrain over open natural land.</summary>
        public static void RemapRiver(Map map, TerrainDef[] before, RM_LandformExtension ext)
        {
            if (ext == null) return;
            List<IntVec3> water = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef now = c.GetTerrain(map);
                int i = map.cellIndices.CellToIndex(c);
                if (now == before[i] || now == null || !now.IsRiver) continue;
                water.Add(c);
                bool deep = now == MapGenUtility.DeepMovingWaterTerrainAt(c, map);
                TerrainDef to = deep ? (ext.deepTerrain ?? ext.shallowTerrain) : ext.shallowTerrain;
                if (to != null) map.terrainGrid.SetTerrain(c, to);
            }
            if (ext.bankWidth <= 0 || ext.bankTerrain == null || water.Count == 0) return;
            Map m = map;
            HashSet<IntVec3> seen = new HashSet<IntVec3>(water);
            List<IntVec3> frontier = water;
            for (int step = 0; step < ext.bankWidth && frontier.Count > 0; step++)
            {
                List<IntVec3> next = new List<IntVec3>();
                foreach (IntVec3 c in frontier)
                    foreach (IntVec3 d in GenAdj.CardinalDirections)
                    {
                        IntVec3 n = c + d;
                        if (!n.InBounds(m) || !seen.Add(n)) continue;
                        TerrainDef t = n.GetTerrain(m);
                        if (t == null || !t.natural || t.IsWater || t.categoryType == TerrainDef.TerrainCategoryType.Stone) continue;
                        if (n.GetEdifice(m) != null) continue;
                        m.terrainGrid.SetTerrain(n, ext.bankTerrain);
                        next.Add(n);
                    }
                frontier = next;
            }
        }

        public static TerrainDef[] Snapshot(Map map)
        {
            TerrainDef[] arr = new TerrainDef[map.cellIndices.NumGridCells];
            foreach (IntVec3 c in map.AllCells) arr[map.cellIndices.CellToIndex(c)] = c.GetTerrain(map);
            return arr;
        }

        public static float[] Harmonics(int n, float maxAmp)
        {
            float[] a = new float[n];
            for (int i = 0; i < n; i++) a[i] = Rand.Range(0f, maxAmp / n);
            return a;
        }

        public static float[] Phases(int n)
        {
            float[] p = new float[n];
            for (int i = 0; i < n; i++) p[i] = Rand.Range(0f, RM_LandformGeometry.TwoPi);
            return p;
        }
    }

    /// <summary>Lake-category ports (salt plains, dust bowl, sulfuric lake, contaminated reservoir): vanilla's lake shape,
    /// our terrains.</summary>
    public class RM_TileMutatorWorker_LandformLake : TileMutatorWorker_Lake
    {
        public RM_TileMutatorWorker_LandformLake(TileMutatorDef def) : base(def)
        {
        }

        private RM_LandformExtension Ext => RM_LandformExtension.Of(def);

        protected override float LakeRadius => Ext?.lakeRadius ?? 0.6f;

        protected override bool GenerateDeepWater => Ext?.deepWater ?? true;

        protected override void ProcessCell(IntVec3 cell, Map map)
        {
            RM_LandformExtension ext = Ext;
            if (ext == null) { base.ProcessCell(cell, map); return; }
            float v = GetValAt(cell, map);
            TerrainDef to = null;
            if (GenerateDeepWater && v > DeepWaterThreshold) to = ext.deepTerrain;
            else if (v > WaterThreshold) to = ext.shallowTerrain;
            else if (v > BeachThreshold) to = ext.shoreTerrain;
            else if (ext.outerTerrain != null && v > ext.outerThreshold && RM_LandformUtil.IsOpenLand(cell, map)) to = ext.outerTerrain;
            if (to != null) map.terrainGrid.SetTerrain(cell, to);
        }

        public override void GenerateNonCriticalStructures(Map map)
        {
            RM_LandformUtil.ScatterThings(map, Ext);
        }
    }

    /// <summary>River-category ports (dry river, stagnant rivulet, flood plains, sulfuric and contaminated rivers): vanilla
    /// lays the river from the world's river link, then its water is remapped to ours. The bank terrain is the def's own
    /// overrideRiverbankTerrain, which vanilla honours. A tile with no river is left alone.</summary>
    public class RM_TileMutatorWorker_LandformRiver : TileMutatorWorker_River
    {
        public RM_TileMutatorWorker_LandformRiver(TileMutatorDef def) : base(def)
        {
        }

        public override string GetLabel(PlanetTile tile)
        {
            return def.label;
        }

        public override void GeneratePostTerrain(Map map)
        {
            if (!RM_LandformUtil.HasRivers(map))
            {
                if (Prefs.DevMode) Log.Message("[RM TileFeatures] " + def.defName + ": tile has no river; nothing to reshape.");
                return;
            }
            TerrainDef[] before = RM_LandformUtil.Snapshot(map);
            base.GeneratePostTerrain(map);
            RM_LandformUtil.RemapRiver(map, before, RM_LandformExtension.Of(def));
        }

        public override void GeneratePostFog(Map map)
        {
            if (RM_LandformUtil.HasRivers(map)) base.GeneratePostFog(map);
        }

        public override void GenerateNonCriticalStructures(Map map)
        {
            RM_LandformUtil.ScatterThings(map, RM_LandformExtension.Of(def));
        }
    }

    /// <summary>Delta ports (relict delta, alluvial fan): vanilla's river delta, then remapped like the rivers. Needs a river
    /// and a coast, as vanilla's delta does; without them nothing is drawn.</summary>
    public class RM_TileMutatorWorker_LandformDelta : TileMutatorWorker_RiverDelta
    {
        public RM_TileMutatorWorker_LandformDelta(TileMutatorDef def) : base(def)
        {
        }

        private static bool CanDelta(Map map)
        {
            if (!RM_LandformUtil.HasRivers(map)) return false;
            return Find.World.CoastAngleAt(map.Tile, BiomeDefOf.Ocean).HasValue || Find.World.CoastAngleAt(map.Tile, BiomeDefOf.Lake).HasValue;
        }

        public override void GeneratePostTerrain(Map map)
        {
            if (!CanDelta(map))
            {
                if (Prefs.DevMode) Log.Message("[RM TileFeatures] " + def.defName + ": tile has no river or no coast; no delta drawn.");
                return;
            }
            TerrainDef[] before = RM_LandformUtil.Snapshot(map);
            base.GeneratePostTerrain(map);
            RM_LandformUtil.RemapRiver(map, before, RM_LandformExtension.Of(def));
        }

        public override void GeneratePostFog(Map map)
        {
            if (CanDelta(map)) base.GeneratePostFog(map);
        }
    }

    /// <summary>Ring-walled craters (meteor crater, resurgent caldera, toxic crater): a wobbly rock rim with breaches, a flat
    /// basin floor, and optionally a central rock dome or a pool.</summary>
    public class RM_TileMutatorWorker_Crater : TileMutatorWorker
    {
        private IntVec3 center;
        private float radius;
        private float[] amps, phases, breaches;

        public RM_TileMutatorWorker_Crater(TileMutatorDef def) : base(def)
        {
        }

        public override void Init(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            int size = Math.Min(map.Size.x, map.Size.z);
            center = new IntVec3(map.Center.x + Rand.RangeInclusive(-size / 10, size / 10), 0, map.Center.z + Rand.RangeInclusive(-size / 10, size / 10));
            radius = size * ext.radiusFraction.RandomInRange;
            amps = RM_LandformUtil.Harmonics(3, 0.12f);
            phases = RM_LandformUtil.Phases(3);
            breaches = new float[Math.Max(0, ext.rimBreaches)];
            for (int i = 0; i < breaches.Length; i++) breaches[i] = Rand.Range(0f, RM_LandformGeometry.TwoPi);
        }

        private RM_CraterZone ZoneAt(IntVec3 c, RM_LandformExtension ext)
        {
            float dx = c.x - center.x, dz = c.z - center.z;
            float angle = (float)Math.Atan2(dz, dx);
            float r = RM_LandformGeometry.WobbledRadius(radius, angle, amps, phases);
            return RM_LandformGeometry.CraterZone((float)Math.Sqrt(dx * dx + dz * dz), r, ext.rimWidth, ext.poolFraction,
                ext.domeFraction, angle, breaches, ext.breachHalfWidth);
        }

        public override void GeneratePostElevationFertility(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            foreach (IntVec3 c in map.AllCells)
            {
                switch (ZoneAt(c, ext))
                {
                    case RM_CraterZone.Rim:
                    case RM_CraterZone.Dome:
                        elevation[c] = 1f;
                        break;
                    case RM_CraterZone.Basin:
                    case RM_CraterZone.Pool:
                        elevation[c] = 0f;
                        break;
                }
            }
        }

        public override void GeneratePostTerrain(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            if (ext == null) return;
            foreach (IntVec3 c in map.AllCells)
            {
                RM_CraterZone z = ZoneAt(c, ext);
                if (z == RM_CraterZone.Pool)
                {
                    float d = c.DistanceTo(center);
                    TerrainDef t = d < radius * ext.poolFraction * 0.6f ? (ext.deepTerrain ?? ext.shallowTerrain) : ext.shallowTerrain;
                    if (t != null) map.terrainGrid.SetTerrain(c, t);
                }
                else if (z == RM_CraterZone.Basin && ext.floorTerrain != null && RM_LandformUtil.IsOpenLand(c, map))
                    map.terrainGrid.SetTerrain(c, ext.floorTerrain);
            }
        }
    }

    /// <summary>LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT: one rock mountain rising from an open plain near the map's
    /// centre (Geological Landforms' "lone mountain", rebuilt from its shape, no GL code). The whole map's elevation is
    /// replaced, so no other rock stands on the map; the mountain is shrunk if its farthest possible rock would come within
    /// EdgeMargin cells of a map edge, so every edge stays walkable.</summary>
    public class RM_TileMutatorWorker_LoneMountain : TileMutatorWorker
    {
        public const int EdgeMargin = 6;
        private IntVec3 center;
        private float radius;
        private float[] amps, phases;
        private Verse.Noise.Perlin noise;

        public RM_TileMutatorWorker_LoneMountain(TileMutatorDef def) : base(def)
        {
        }

        public override void Init(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            int size = Math.Min(map.Size.x, map.Size.z);
            center = new IntVec3(map.Center.x + Rand.RangeInclusive(-size / 10, size / 10), 0, map.Center.z + Rand.RangeInclusive(-size / 10, size / 10));
            amps = RM_LandformUtil.Harmonics(3, 0.12f);
            phases = RM_LandformUtil.Phases(3);
            radius = size * ext.radiusFraction.RandomInRange;
            int room = Math.Min(Math.Min(center.x, map.Size.x - 1 - center.x), Math.Min(center.z, map.Size.z - 1 - center.z)) - EdgeMargin;
            radius = RM_LandformGeometry.LoneMountainFit(radius, amps, room);
            noise = new Verse.Noise.Perlin(0.021, 2.0, 0.5, 6, Rand.Range(0, int.MaxValue), Verse.Noise.QualityMode.Medium);
        }

        public override void GeneratePostElevationFertility(Map map)
        {
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            foreach (IntVec3 c in map.AllCells)
            {
                float dx = c.x - center.x, dz = c.z - center.z;
                float r = RM_LandformGeometry.WobbledRadius(radius, (float)Math.Atan2(dz, dx), amps, phases);
                elevation[c] = RM_LandformGeometry.LoneMountainElevation((float)Math.Sqrt(dx * dx + dz * dz), r,
                    (float)noise.GetValue(c.x, 0.0, c.z));
            }
        }
    }

    /// <summary>Line landforms (rock ridge, jagged rocks, serpentine canyons): meandering bands across the map that raise
    /// rock or carve it out, each optionally with a gap left open.</summary>
    public class RM_TileMutatorWorker_Lines : TileMutatorWorker
    {
        private struct Line
        {
            public float[] xs, zs;
            public float halfWidth, gapStart, gapEnd;
        }

        private List<Line> lines = new List<Line>();

        public RM_TileMutatorWorker_Lines(TileMutatorDef def) : base(def)
        {
        }

        public override void Init(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            lines = new List<Line>();
            float diag = (float)Math.Sqrt(map.Size.x * map.Size.x + map.Size.z * map.Size.z);
            int n = ext.lineCount.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                float cx = map.Size.x * Rand.Range(0.3f, 0.7f), cz = map.Size.z * Rand.Range(0.3f, 0.7f);
                RM_LandformGeometry.Meander(cx, cz, Rand.Range(0f, RM_LandformGeometry.TwoPi), diag * 0.6f, 48,
                    ext.meanderAmplitude.RandomInRange, ext.meanderWaves.RandomInRange, Rand.Range(0f, RM_LandformGeometry.TwoPi),
                    out float[] xs, out float[] zs);
                float len = RM_LandformGeometry.PolylineLength(xs, zs);
                // the gap sits on the stretch that crosses the map's middle (the line's middle third)
                float gs = ext.gapLength > 0 ? Rand.Range(len * 0.4f, len * 0.6f - ext.gapLength) : -1f;
                lines.Add(new Line { xs = xs, zs = zs, halfWidth = ext.lineHalfWidth.RandomInRange, gapStart = gs, gapEnd = gs + ext.gapLength });
            }
        }

        private bool OnLine(IntVec3 c)
        {
            foreach (Line l in lines)
                if (RM_LandformGeometry.OnBand(c.x, c.z, l.xs, l.zs, l.halfWidth, l.gapStart, l.gapEnd)) return true;
            return false;
        }

        public override void GeneratePostElevationFertility(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            foreach (IntVec3 c in map.AllCells)
            {
                if (ext.baseElevation >= 0f) elevation[c] = ext.baseElevation;
                if (OnLine(c)) elevation[c] = ext.lineElevation;
            }
        }

        public override void GeneratePostTerrain(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            if (ext?.floorTerrain == null || ext.lineElevation > 0.5f) return;
            foreach (IntVec3 c in map.AllCells)
                if (OnLine(c) && RM_LandformUtil.IsOpenLand(c, map))
                    map.terrainGrid.SetTerrain(c, ext.floorTerrain);
        }
    }

    /// <summary>Scattered discs (cenotes, sinkholes, stone-forest spires): each disc is either raised to rock (spires) or
    /// laid with a core terrain and a lip.</summary>
    public class RM_TileMutatorWorker_Scatter : TileMutatorWorker
    {
        private List<RM_Disc> discs = new List<RM_Disc>();

        public RM_TileMutatorWorker_Scatter(TileMutatorDef def) : base(def)
        {
        }

        public override void Init(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def) ?? new RM_LandformExtension();
            int count = Math.Max(0, (int)Math.Round(ext.discsPer10kCells.RandomInRange * map.Area / 10000f));
            discs = RM_LandformGeometry.PlaceDiscs(map.Size.x, map.Size.z, count, ext.discRadius.min, ext.discRadius.max,
                6, ext.discSpacing, new Random(Rand.Int));
        }

        private IEnumerable<IntVec3> DiscCells(Map map, RM_Disc d, int extra)
        {
            int R = d.r + extra;
            for (int x = d.x - R; x <= d.x + R; x++)
                for (int z = d.z - R; z <= d.z + R; z++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (c.InBounds(map) && (x - d.x) * (x - d.x) + (z - d.z) * (z - d.z) <= R * R + R) yield return c;
                }
        }

        public override void GeneratePostElevationFertility(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            if (ext == null || ext.discElevation < 0f) return;
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            foreach (RM_Disc d in discs)
                foreach (IntVec3 c in DiscCells(map, d, 0))
                    elevation[c] = ext.discElevation;
        }

        public override void GeneratePostTerrain(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            if (ext == null || ext.discElevation >= 0f) return;
            foreach (RM_Disc d in discs)
            {
                // a disc that lands on rock or water is skipped whole: half a cenote in a cliff reads as a bug
                bool ok = true;
                foreach (IntVec3 c in DiscCells(map, d, ext.discLip))
                    if (!RM_LandformUtil.IsOpenLand(c, map)) { ok = false; break; }
                if (!ok) continue;
                if (ext.lipTerrain != null)
                    foreach (IntVec3 c in DiscCells(map, d, ext.discLip)) map.terrainGrid.SetTerrain(c, ext.lipTerrain);
                foreach (IntVec3 c in DiscCells(map, d, 0))
                {
                    bool core = c.DistanceTo(new IntVec3(d.x, 0, d.z)) <= d.r * 0.6f + 0.5f;
                    TerrainDef t = core || ext.shallowTerrain == null ? ext.deepTerrain : ext.shallowTerrain;
                    if (t != null) map.terrainGrid.SetTerrain(c, t);
                }
            }
        }
    }

    /// <summary>Terrain swaps over the whole map after the terrain pass (red desert: sand to red sand).</summary>
    public class RM_TileMutatorWorker_TerrainSwap : TileMutatorWorker
    {
        public RM_TileMutatorWorker_TerrainSwap(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostTerrain(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            if (ext == null || ext.swaps.NullOrEmpty()) return;
            Dictionary<TerrainDef, TerrainDef> map2 = new Dictionary<TerrainDef, TerrainDef>();
            foreach (RM_TerrainSwap s in ext.swaps)
                if (s?.from != null && s.to != null) map2[s.from] = s.to;
            foreach (IntVec3 c in map.AllCells)
                if (map2.TryGetValue(c.GetTerrain(map), out TerrainDef to))
                    map.terrainGrid.SetTerrain(c, to);
        }
    }

    /// <summary>Deep snow: the map starts under a full, packed snow cover on every unroofed land cell; it melts by vanilla
    /// rules if the weather turns warm.</summary>
    public class RM_TileMutatorWorker_DeepSnow : TileMutatorWorker
    {
        public RM_TileMutatorWorker_DeepSnow(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostFog(Map map)
        {
            RM_LandformExtension ext = RM_LandformExtension.Of(def);
            float depth = ext == null || ext.snowDepth < 0f ? 1f : ext.snowDepth;
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.IsWater || map.roofGrid.Roofed(c)) continue;
                map.snowGrid.SetDepth(c, depth);
            }
        }
    }

    /// <summary>Quicksand dunes: vanilla's dunes, then the def's terrainPatchMakers lay quicksand pools between them. The
    /// def sets preventPatches (it keeps other patch features off this barren tile), so the patches are run here.</summary>
    public class RM_TileMutatorWorker_QuicksandDunes : TileMutatorWorker_Dunes
    {
        public RM_TileMutatorWorker_QuicksandDunes(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostTerrain(Map map)
        {
            base.GeneratePostTerrain(map);
            if (def.terrainPatchMakers.NullOrEmpty()) return;
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.IsWater || t.categoryType == TerrainDef.TerrainCategoryType.Stone) continue;
                foreach (TerrainPatchMaker pm in def.terrainPatchMakers)
                {
                    TerrainDef to = pm.TerrainAt(c, map, c.GetFertility(map));
                    if (to != null) map.terrainGrid.SetTerrain(c, to);
                }
            }
            foreach (TerrainPatchMaker pm in def.terrainPatchMakers) pm.Cleanup();
        }
    }
}
