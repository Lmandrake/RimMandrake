using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// The engine — MOVING_DUNES_DESIGN.md §2 "Transport rule" and "The edge condition".
    ///
    /// Vanilla has wind SPEED only: <c>WindManager</c> is one Perlin-driven float and no
    /// direction exists anywhere in the game. This component owns the map's prevailing
    /// direction (8-way, random-walking on a multi-day timescale, saved), which is what
    /// makes wind SHIFTS — and therefore the reveal mechanic — possible at all.
    ///
    /// Each batch (every 250 ticks, the Pyrelands ashfall cadence) it runs K Werner-style
    /// slab attempts on random unroofed cells: erode a cell that is deep enough, not wind
    /// -shadowed, and under a strong enough wind; hop a slab of <c>slabSize</c> depth 2-6
    /// cells downwind; deposit at the first candidate that is shadowed or lower than the
    /// source. Deposition preferring low cells is why dug pits and cleared lanes refill
    /// from the rule itself — the owner's pit mechanic is a corollary, not a feature.
    ///
    /// Edges are SOURCE/SINK, not toroidal (RULED, design §2): a slab hopping off the
    /// leeward edge is gone, and a windward influx budget puts new sand in. The map is a
    /// window onto an endless desert; supply is a knob, so a violent windstorm can bring
    /// MORE sand than the map started with.
    /// </summary>
    public class MapComponent_DuneField : MapComponent
    {
        /// <summary>Batch cadence. 240 batches per in-game day.</summary>
        public const int BatchIntervalTicks = 250;
        private const int BatchesPerDay = GenDate.TicksPerDay / BatchIntervalTicks;

        /// <summary>Depth boundaries at which <c>WeatherBuildupUtility</c> changes
        /// movement category — every crossing costs a
        /// <c>RecalculatePerceivedPathCostAt</c>. Deposition is nudged clear of them
        /// (design §6.2: a front resting exactly on a boundary re-paths the colony
        /// forever as it jitters back and forth).</summary>
        private static readonly float[] CategoryBoundaries = { 0.03f, 0.25f, 0.5f, 0.75f };
        private const float BoundaryHysteresis = 0.012f;

        /// <summary>A cell this much deeper than its neighbour, within
        /// <c>shadowRange</c> upwind, shelters that neighbour from erosion.</summary>
        private const float ShadowDepthMargin = 0.15f;

        /// <summary>How much lower a downwind cell must be to catch a slab early.</summary>
        private const float LowCellMargin = 0.02f;

        /// <summary>Windward band, in cells, that influx is sprinkled across.</summary>
        private const int InfluxBandWidth = 6;

        // ------------------------------------------------------------- saved state

        private RM_DuneMaterialDef material;
        private int windDir = 4;              // 0 = north, clockwise, 8-way
        private int nextWindShiftTick = -1;
        private float influxDebt;

        // ------------------------------------------------------ unsaved / derived

        private int cachedCacheCount = -1;
        private int cacheCountValidTick = -1;
        private bool armed;
        private bool inertReported;
        private readonly List<Thing> tmpThings = new List<Thing>();
        private readonly List<Thing> tmpBury = new List<Thing>();

        /// <summary>The 8 compass directions, index 0 = north, clockwise.</summary>
        private static readonly IntVec3[] WindVectors =
        {
            new IntVec3(0, 0, 1),   // N
            new IntVec3(1, 0, 1),   // NE
            new IntVec3(1, 0, 0),   // E
            new IntVec3(1, 0, -1),  // SE
            new IntVec3(0, 0, -1),  // S
            new IntVec3(-1, 0, -1), // SW
            new IntVec3(-1, 0, 0),  // W
            new IntVec3(-1, 0, 1),  // NW
        };

        private static readonly string[] WindNames =
        { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };

        public MapComponent_DuneField(Map map) : base(map) { }

        /// <summary>The material skinning this map, or null if this map is not a dune
        /// field.</summary>
        public RM_DuneMaterialDef Material { get { return material; } }

        /// <summary>Unit vector the wind blows TOWARDS.</summary>
        public IntVec3 WindVector { get { return WindVectors[windDir & 7]; } }

        public string WindName { get { return WindNames[windDir & 7]; } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref material, "material");
            Scribe_Values.Look(ref windDir, "windDir", 4);
            Scribe_Values.Look(ref nextWindShiftTick, "nextWindShiftTick", -1);
            Scribe_Values.Look(ref influxDebt, "influxDebt", 0f);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Resolve();
        }

        public override void MapGenerated()
        {
            base.MapGenerated();
            Resolve();
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            DuneFieldRegistry.Deregister(map);
            armed = false;
        }

        /// <summary>
        /// Decides once whether this map is a dune field, and says so in the log either
        /// way. Everything downstream — both sand-grid patches, the skinned renderer,
        /// the burial sweep — keys off the registry entry this writes.
        /// </summary>
        private void Resolve()
        {
            if (armed)
            {
                return;
            }

            // A saved material wins: a map keeps the material it was created with even if
            // the biome's binding is later changed or the data pack that bound it is gone.
            if (material == null && map.Biome != null)
            {
                DuneFieldExtension ext = map.Biome.GetModExtension<DuneFieldExtension>();
                if (ext != null)
                {
                    material = ext.material;
                }
            }
            if (material == null)
            {
                return; // ordinary map — every patch in this assembly falls straight through
            }

            if (!ModsConfig.OdysseyActive)
            {
                if (!inertReported)
                {
                    inertReported = true;
                    Log.Warning(MovingDunesMod.LogPrefix + "biome " + map.Biome.defName + " binds dune "
                                + "material " + material.defName + ", but Odyssey is not active. "
                                + "SandGrid never allocates its grid without Odyssey, so this map "
                                + "drifts nothing. This is the documented soft-dependency, not a bug.");
                }
                return;
            }

            if (!MovingDunesMod.CanHaveSandPatchArmed)
            {
                Log.Error(MovingDunesMod.LogPrefix + "dune field on " + map.Biome.defName + " is "
                          + "DECORATIVE: the CanHaveSand rule failed to arm, so sand and soft-sand "
                          + "terrain still refuse to hold depth and a desert map has almost nowhere "
                          + "to drift. Fix that patch before trusting anything you see here.");
            }
            if (!MovingDunesMod.DecaySuppressionArmed && material.ambientDecayFactor <= 0f)
            {
                Log.Error(MovingDunesMod.LogPrefix + "dune field on " + map.Biome.defName + " asks for "
                          + "suppressed ambient decay, but the AddDepth rule failed to arm. Drifts "
                          + "will evaporate in about five clear-weather days.");
            }

            if (nextWindShiftTick < 0)
            {
                windDir = Rand.RangeInclusive(0, 7);
                ScheduleNextWindShift();
            }

            armed = true;
            DuneFieldRegistry.Register(map, this);
            Log.Message(MovingDunesMod.LogPrefix + "dune field armed on " + map.Biome.defName
                        + " with material " + material.defName + "; wind " + WindName
                        + ", K=" + material.AttemptsPerBatch(map.cellIndices.NumGridCells)
                        + " attempts/batch over " + map.cellIndices.NumGridCells + " cells.");
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!armed || material == null)
            {
                return;
            }
            if (!MovingDunesSettings.duneEngineEnabled)
            {
                return; // mod option: dune drift disabled — the map sits still
            }
            int now = Find.TickManager.TicksGame;
            if (now % BatchIntervalTicks != 0)
            {
                return;
            }

            if (now >= nextWindShiftTick)
            {
                ShiftWind();
            }

            float stormTransport, stormInflux;
            StormFactors(out stormTransport, out stormInflux);
            stormTransport *= MovingDunesSettings.transportRateMultiplier;
            stormInflux *= MovingDunesSettings.transportRateMultiplier;

            float lost = RunTransportBatch(stormTransport);
            RunInflux(lost, stormInflux);
            RunPlantChoke(stormTransport);
        }

        // ------------------------------------------------------------------- wind

        private void ScheduleNextWindShift()
        {
            float days = Rand.Range(0.5f, 1.5f) * Mathf.Max(0.05f, material.windShiftMeanDays);
            nextWindShiftTick = Find.TickManager.TicksGame + Mathf.RoundToInt(days * GenDate.TicksPerDay);
        }

        private void ShiftWind()
        {
            int step = Rand.Chance(material.windShiftBigChance) ? 2 : 1;
            if (Rand.Bool)
            {
                step = -step;
            }
            windDir = (windDir + step + 8) & 7;
            ScheduleNextWindShift();
        }

        /// <summary>
        /// The two storm multipliers for the weather running right now. A WeatherDef may
        /// override either with <see cref="DuneWeatherExtension"/>; otherwise any weather
        /// actually carrying sand (<c>SandRate</c> above vanilla's own 0.001 threshold)
        /// gets the material's factors.
        /// </summary>
        private void StormFactors(out float transport, out float influx)
        {
            transport = 1f;
            influx = 1f;
            WeatherDef weather = map.weatherManager.curWeather;
            DuneWeatherExtension ext = weather != null
                ? weather.GetModExtension<DuneWeatherExtension>() : null;
            bool storming = map.weatherManager.SandRate > 0.001f
                            || (ext != null && ext.forceStormTransport);
            if (!storming)
            {
                return;
            }
            transport = ext != null && ext.transportFactor >= 0f
                ? ext.transportFactor : material.stormTransportFactor;
            influx = ext != null && ext.influxFactor >= 0f
                ? ext.influxFactor : material.weatherInfluxFactor;
        }

        // -------------------------------------------------------------- transport

        /// <summary>Runs one batch of slab attempts. Returns the total depth that left
        /// the map over the leeward edge — the sink half of source/sink.</summary>
        private float RunTransportBatch(float stormFactor)
        {
            float windSpeed = map.windManager.WindSpeed;
            if (windSpeed < material.windSpeedThreshold)
            {
                return 0f; // calm: nothing moves, and the batch costs one float compare
            }

            SandGrid grid = map.sandGrid;
            IntVec3 wind = WindVector;
            int attempts = Mathf.RoundToInt(
                material.AttemptsPerBatch(map.cellIndices.NumGridCells) * Mathf.Max(0.01f, stormFactor));
            float q = material.slabSize;
            float lost = 0f;

            for (int i = 0; i < attempts; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                float here = grid.GetDepth(c);
                if (here < material.erodeMinDepth)
                {
                    continue;
                }
                if (map.roofGrid.Roofed(c))
                {
                    continue; // roofed cells are out of the wind entirely
                }
                if (IsWindShadowed(c, wind, here, grid))
                {
                    continue;
                }

                float slab = Mathf.Min(q, here);
                int hop = material.hopRange.RandomInRange;
                IntVec3 landing = IntVec3.Invalid;
                IntVec3 prev = c;
                bool offMap = false;

                for (int s = 1; s <= hop; s++)
                {
                    IntVec3 n = c + wind * s;
                    if (!n.InBounds(map))
                    {
                        offMap = true;
                        break;
                    }
                    if (map.roofGrid.Roofed(n))
                    {
                        landing = prev; // banks at the lip of a roof
                        break;
                    }
                    Building edifice = n.GetEdifice(map);
                    if (edifice != null && !SandGrid.CanCoexistWithSand(edifice.def))
                    {
                        landing = prev; // the snowdrift-behind-a-fence tail, for free
                        break;
                    }
                    if (grid.GetDepth(n) < here - LowCellMargin)
                    {
                        landing = n;   // deposition prefers low: pits and lanes refill
                        break;
                    }
                    prev = n;
                }

                SetDepthHysteretic(grid, c, here - slab);

                if (offMap)
                {
                    lost += slab;
                    continue;
                }
                if (!landing.IsValid)
                {
                    landing = prev;
                }
                if (landing == c)
                {
                    // Erode-and-replace-in-place is a no-op that still costs a mesh
                    // dirty; put the slab back and move on.
                    SetDepthHysteretic(grid, c, here);
                    continue;
                }
                Deposit(grid, landing, slab);
            }

            return lost;
        }

        /// <summary>A cell is sheltered if something upwind of it, within
        /// <c>shadowRange</c>, blocks or out-tops the wind.</summary>
        private bool IsWindShadowed(IntVec3 c, IntVec3 wind, float here, SandGrid grid)
        {
            for (int s = 1; s <= material.shadowRange; s++)
            {
                IntVec3 up = c - wind * s;
                if (!up.InBounds(map))
                {
                    return false; // open desert upwind
                }
                Building edifice = up.GetEdifice(map);
                if (edifice != null && !SandGrid.CanCoexistWithSand(edifice.def))
                {
                    return true;
                }
                if (grid.GetDepth(up) > here + ShadowDepthMargin)
                {
                    return true;
                }
            }
            return false;
        }

        private void Deposit(SandGrid grid, IntVec3 cell, float slab)
        {
            float before = grid.GetDepth(cell);
            SetDepthHysteretic(grid, cell, before + slab);
            float after = grid.GetDepth(cell);

            if (material.depositFilthDef != null && Rand.Chance(material.depositFilthChance))
            {
                FilthMaker.TryMakeFilth(cell, map, material.depositFilthDef);
            }

            if (after >= material.burialDepth && before < material.burialDepth)
            {
                TryBuryAt(cell);
            }
        }

        /// <summary>
        /// Writes a depth, nudged clear of the movement-category boundaries. Design §6.2:
        /// a dune front resting exactly on a boundary re-paths the whole colony every
        /// time it jitters across, so the engine never leaves a cell there.
        /// </summary>
        private void SetDepthHysteretic(SandGrid grid, IntVec3 cell, float target)
        {
            target = Mathf.Clamp(target, 0f, SandGrid.MaxDepth);
            if (target > 0f)
            {
                for (int i = 0; i < CategoryBoundaries.Length; i++)
                {
                    float b = CategoryBoundaries[i];
                    if (Mathf.Abs(target - b) < BoundaryHysteresis)
                    {
                        target = target >= b ? b + BoundaryHysteresis : b - BoundaryHysteresis;
                        break;
                    }
                }
                target = Mathf.Clamp(target, 0f, SandGrid.MaxDepth);
            }
            grid.SetDepth(cell, target);
        }

        // --------------------------------------------------------- source / sink

        /// <summary>
        /// The source half. Loss over the leeward edge is given back at the windward edge
        /// scaled by <c>influxLossRatio</c>, plus an absolute <c>influxPerDay</c> base —
        /// which is also the cold start, since a map holding no sand can lose none and so
        /// could otherwise never be given any. Both are multiplied by the weather's influx
        /// factor. The mass cap is binding (design §7.3 is UNRULED; cap-binding is the
        /// stated default until the owner rules).
        /// </summary>
        private void RunInflux(float lostDepth, float stormFactor)
        {
            int cells = map.cellIndices.NumGridCells;
            float cap = material.maxTotalMassFraction * cells * SandGrid.MaxDepth;
            SandGrid grid = map.sandGrid;
            if (grid.TotalDepth >= cap)
            {
                influxDebt = 0f;
                return;
            }

            influxDebt += (lostDepth * material.influxLossRatio
                           + material.influxPerDay / BatchesPerDay) * Mathf.Max(0f, stormFactor);
            if (influxDebt <= 0f)
            {
                return;
            }

            float q = material.slabSize;
            IntVec3 wind = WindVector;
            int placed = 0;
            int budget = Mathf.CeilToInt(influxDebt / q);
            // Bounded work per batch: a huge debt spends down over several batches rather
            // than stalling one tick. 4x the batch's own K is generous and still cheap.
            int maxPlacements = Mathf.Max(16, material.AttemptsPerBatch(cells) * 4);
            int tries = 0;
            int maxTries = maxPlacements * 4;

            while (placed < budget && placed < maxPlacements && tries < maxTries
                   && grid.TotalDepth < cap)
            {
                tries++;
                IntVec3 c = RandomWindwardCell(wind);
                if (!c.InBounds(map) || map.roofGrid.Roofed(c))
                {
                    continue;
                }
                float before = grid.GetDepth(c);
                if (before >= SandGrid.MaxDepth - 0.001f)
                {
                    continue;
                }
                SetDepthHysteretic(grid, c, before + q);
                if (grid.GetDepth(c) <= before)
                {
                    continue; // cell refused the sand (water, wall) — do not spend the debt
                }
                placed++;
                influxDebt -= q;
            }

            if (influxDebt < 0f)
            {
                influxDebt = 0f;
            }
        }

        /// <summary>A random cell in the band along the edge(s) the wind comes FROM.</summary>
        private IntVec3 RandomWindwardCell(IntVec3 wind)
        {
            int sizeX = map.Size.x;
            int sizeZ = map.Size.z;
            int band = Mathf.Min(InfluxBandWidth, Mathf.Min(sizeX, sizeZ) / 2);
            if (band < 1)
            {
                band = 1;
            }

            int x = wind.x > 0 ? Rand.Range(0, band)
                  : wind.x < 0 ? Rand.Range(sizeX - band, sizeX)
                  : Rand.Range(0, sizeX);
            int z = wind.z > 0 ? Rand.Range(0, band)
                  : wind.z < 0 ? Rand.Range(sizeZ - band, sizeZ)
                  : Rand.Range(0, sizeZ);
            return new IntVec3(Mathf.Clamp(x, 0, sizeX - 1), 0, Mathf.Clamp(z, 0, sizeZ - 1));
        }

        // ------------------------------------------------------------------ burial

        private void TryBuryAt(IntVec3 cell)
        {
            if (!MovingDunesSettings.burialEnabled)
            {
                return; // mod option: buried caches disabled
            }
            if (DuneBurialUtility.CacheAt(cell, map) == null && CacheCount() >= material.maxCachesPerMap)
            {
                return; // at the cap: no NEW cache cells, existing ones still merge
            }

            tmpThings.Clear();
            tmpThings.AddRange(map.thingGrid.ThingsListAtFast(cell));
            tmpBury.Clear();
            for (int i = 0; i < tmpThings.Count; i++)
            {
                if (DuneBurialUtility.IsBurialCandidate(tmpThings[i], map, material.minBurialMarketValue))
                {
                    tmpBury.Add(tmpThings[i]);
                }
            }
            tmpThings.Clear();
            if (tmpBury.Count == 0)
            {
                return;
            }

            DuneBurialUtility.BuryThingsAt(cell, map, tmpBury);
            tmpBury.Clear();
            cacheCountValidTick = -1;
        }

        /// <summary>Cached per batch: the cap check would otherwise walk the whole
        /// thing list on every deposition that crosses the burial depth.</summary>
        private int CacheCount()
        {
            int now = Find.TickManager.TicksGame;
            if (cacheCountValidTick == now && cachedCacheCount >= 0)
            {
                return cachedCacheCount;
            }
            List<Thing> list = map.listerThings.ThingsOfDef(MovingDunesDefOf.RM_Dunes_BuriedCache);
            cachedCacheCount = list != null ? list.Count : 0;
            cacheCountValidTick = now;
            return cachedCacheCount;
        }

        // ------------------------------------------------------------ plant choke

        /// <summary>
        /// Design §3: vanilla already blocks sowing and wild spawns at depth 0.2
        /// (<c>PlantUtility.SandAllowsPlanting</c>); this adds the kill. Damage per visit
        /// is sized from the sampled visit rate so a fully-buried plant takes
        /// <c>plantChokeDays</c> to die whatever K is tuned to — an advancing front
        /// leaves a dead strip, legible and slow.
        /// </summary>
        private void RunPlantChoke(float stormFactor)
        {
            if (!MovingDunesSettings.plantChokeEnabled)
            {
                return; // mod option: sand-choke disabled
            }
            if (material.plantChokeSampleFraction <= 0f)
            {
                return;
            }
            int cells = map.cellIndices.NumGridCells;
            int samples = Mathf.RoundToInt(
                material.AttemptsPerBatch(cells) * material.plantChokeSampleFraction
                * Mathf.Max(0.01f, stormFactor));
            if (samples < 1)
            {
                return;
            }

            // Expected visits to any one cell per in-game day, from this very sample rate.
            float visitsPerDay = (float)samples * BatchesPerDay / cells;
            if (visitsPerDay <= 0f)
            {
                return;
            }

            SandGrid grid = map.sandGrid;
            for (int i = 0; i < samples; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (grid.GetDepth(c) < material.plantChokeDepth)
                {
                    continue;
                }
                Plant plant = c.GetPlant(map);
                if (plant == null || plant.Destroyed)
                {
                    continue;
                }
                int damage = Mathf.Max(1, Mathf.RoundToInt(
                    plant.MaxHitPoints / (material.plantChokeDays * visitsPerDay)));
                plant.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, damage));
            }
        }

        // ------------------------------------------------------------------- debug

        /// <summary>Dev only: turn the wind now, without waiting out the schedule.</summary>
        public void DebugShiftWind()
        {
            if (armed && material != null)
            {
                ShiftWind();
            }
        }

        /// <summary>Dev only: run N transport batches back to back. The engine's whole
        /// behaviour is on a multi-day timescale by design, so this is the only way to
        /// SEE whether transport works without waiting a season. Wind speed still gates
        /// it — a calm map moves nothing however many batches are forced.</summary>
        public void DebugRunBatches(int count)
        {
            if (!armed || material == null)
            {
                return;
            }
            float stormTransport, stormInflux;
            StormFactors(out stormTransport, out stormInflux);
            for (int i = 0; i < count; i++)
            {
                float lost = RunTransportBatch(stormTransport);
                RunInflux(lost, stormInflux);
            }
        }

        public string DebugString()
        {
            if (!armed || material == null)
            {
                return "not a dune field";
            }
            return "material=" + material.defName
                 + " wind=" + WindName
                 + " nextShift=" + nextWindShiftTick
                 + " influxDebt=" + influxDebt.ToString("F3")
                 + " totalDepth=" + map.sandGrid.TotalDepth.ToString("F1")
                 + " cap=" + (material.maxTotalMassFraction * map.cellIndices.NumGridCells).ToString("F1")
                 + " caches=" + CacheCount();
        }
    }
}
