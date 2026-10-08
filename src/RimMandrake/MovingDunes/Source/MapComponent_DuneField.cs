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
        public const int BatchIntervalTicks = RM_DuneKernel.BatchIntervalTicks;
        private const int BatchesPerDay = RM_DuneKernel.BatchesPerDay;

        /// <summary>Depth boundaries at which <c>WeatherBuildupUtility</c> changes
        /// movement category — every crossing costs a
        /// <c>RecalculatePerceivedPathCostAt</c>. Deposition is nudged clear of them
        /// (design §6.2: a front resting exactly on a boundary re-paths the colony
        /// forever as it jitters back and forth).</summary>
        private const float BoundaryHysteresis = RM_DuneKernel.BoundaryHysteresis;

        /// <summary>A cell this much deeper than its neighbour, within
        /// <c>shadowRange</c> upwind, shelters that neighbour from erosion.</summary>


        /// <summary>How much lower a downwind cell must be to catch a slab early.</summary>


        /// <summary>Windward band, in cells, that influx is sprinkled across.</summary>


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

        private static readonly string[] WindNames =
        { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };

        public MapComponent_DuneField(Map map) : base(map) { }

        /// <summary>The material skinning this map, or null if this map is not a dune
        /// field.</summary>
        public RM_DuneMaterialDef Material { get { return material; } }

        /// <summary>Unit vector the wind blows TOWARDS.</summary>
        public IntVec3 WindVector { get { return new IntVec3(RM_DuneKernel.WindDx[windDir & 7], 0, RM_DuneKernel.WindDz[windDir & 7]); } }

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
            ApplyWindLock();

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

            if (!ApplyWindLock() && now >= nextWindShiftTick)
            {
                ShiftWind();
            }

            float stormTransport, stormInflux;
            StormFactors(out stormTransport, out stormInflux);
            float driftMult = MovingDunesSettings.transportRateMultiplier;
            stormTransport *= driftMult;

            float lost = RunTransportBatch(stormTransport);
            RunInflux(lost, stormInflux, driftMult);
            RunPlantChoke(stormTransport);
        }

        // ------------------------------------------------------------------- wind

        /// <summary>STILLSAND_WIND_SUN_BEARING_1: on a biome that locks its wind to the
        /// sun, set the wind to the tile's bearing and report true (no shift runs).
        /// Re-applied every batch, so turning the setting back on snaps it home.</summary>
        private bool ApplyWindLock()
        {
            if (map.Biome == null || Find.WorldGrid == null || !map.Tile.Valid)
            {
                return false;
            }
            DuneFieldExtension ext = map.Biome.GetModExtension<DuneFieldExtension>();
            if (!WindLockApplies(MovingDunesSettings.windLockEnabled, ext))
            {
                return false;
            }
            Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
            float bearing = DuneWindBearing.SunBearingDegrees(longLat.y, longLat.x,
                ext.substellarLatitude, ext.substellarLongitude);
            windDir = DuneWindBearing.WindDirFromSunBearing(bearing, ext.windBlowsTowardSubstellar);
            return true;
        }

        /// <summary>MOVINGDUNES_COVERAGE_GAPS_1: the wind-lock gate as a pure function, so the proof
        /// hook reads the shipped decision (setting AND a biome that locks) for every combination.</summary>
        public static bool WindLockApplies(bool settingOn, DuneFieldExtension ext)
        {
            return RM_DuneKernel.WindLockApplies(settingOn, ext != null, ext != null && ext.lockBearingToSubstellar);
        }

        private void ScheduleNextWindShift()
        {
            nextWindShiftTick = RM_DuneKernel.NextWindShiftTick(Find.TickManager.TicksGame, Rand.Range(0.5f, 1.5f), material.windShiftMeanDays);
        }

        private void ShiftWind()
        {
            windDir = RM_DuneKernel.ShiftWind(windDir, Rand.Chance(material.windShiftBigChance), Rand.Bool);
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
            WeatherDef weather = map.weatherManager.curWeather;
            DuneWeatherExtension ext = weather != null
                ? weather.GetModExtension<DuneWeatherExtension>() : null;
            RM_DuneKernel.StormFactors(map.weatherManager.SandRate, ext != null, ext != null ? ext.transportFactor : -1f,
                ext != null ? ext.influxFactor : -1f, ext != null && ext.forceStormTransport, material.stormTransportFactor,
                material.weatherInfluxFactor, out transport, out influx);
        }

        // -------------------------------------------------------------- transport

        /// <summary>Slab attempts per batch: the material's K scaled by the storm factor (which already
        /// carries the drift-speed slider). Pure, so the proof hook reads the shipped scaling.</summary>
        public static int TransportAttempts(RM_DuneMaterialDef m, int numCells, float stormFactor)
        {
            return RM_DuneKernel.TransportAttempts(m.AttemptsPerBatch(numCells), stormFactor);
        }

        private static readonly TransportParamsCache ParamsCache = new TransportParamsCache();

        private sealed class TransportParamsCache
        {
            private RM_DuneMaterialDef of;
            private TransportParams cached;
            public TransportParams For(RM_DuneMaterialDef m)
            {
                if (of != m)
                {
                    of = m;
                    cached = new TransportParams
                    {
                        SlabSize = m.slabSize,
                        ErodeMinDepth = m.erodeMinDepth,
                        ShadowRange = m.shadowRange,
                        HopMin = m.hopRange.min,
                        HopMax = m.hopRange.max,
                    };
                }
                return cached;
            }
        }

        /// <summary>Runs one batch of slab attempts. Returns the total depth that left
        /// the map over the leeward edge - the sink half of source/sink.</summary>
        private float RunTransportBatch(float stormFactor)
        {
            float windSpeed = map.windManager.WindSpeed;
            if (windSpeed < material.windSpeedThreshold)
            {
                return 0f; // calm: nothing moves, and the batch costs one float compare
            }

            IntVec3 wind = WindVector;
            int attempts = TransportAttempts(material, map.cellIndices.NumGridCells, stormFactor);
            Batch batch = RM_DuneKernel.RunTransport(new MapDuneField(map), wind.x, wind.z, attempts, ParamsCache.For(material), BoundaryHysteresis,
                (lo, hi) => Rand.Range(lo, hi), (lo, hi) => Rand.RangeInclusive(lo, hi),
                (x, z, before, after) => OnDeposit(new IntVec3(x, 0, z), before, after));
            return batch.Lost;
        }

        private void OnDeposit(IntVec3 cell, float before, float after)
        {
            if (material.depositFilthDef != null && Rand.Chance(material.depositFilthChance))
            {
                FilthMaker.TryMakeFilth(cell, map, material.depositFilthDef);
            }

            if (RM_CacheKernel.CrossedBurial(before, after, material.burialDepth))
            {
                TryBuryAt(cell);
            }
        }

        // --------------------------------------------------------- source / sink

        /// <summary>
        /// The source half. Loss over the leeward edge is given back at the windward edge
        /// scaled by <c>influxLossRatio</c>, plus an absolute <c>influxPerDay</c> base —
        /// which is also the cold start, since a map holding no sand can lose none and so
        /// could otherwise never be given any. Both are multiplied by the weather's influx
        /// factor. The mass cap is binding (design §7.3 is UNRULED; cap-binding is the
        /// stated default until the owner rules).
        ///
        /// Fixed 2026-09-11 (DIRTY_CODE_REVIEW_STANDING_LOOP_1): <paramref name="lostDepth"/>
        /// already carries the player's drift-speed slider (MapComponentTick scales
        /// <c>stormTransport</c> by it before RunTransportBatch ever runs, and the attempt
        /// count -- hence how much left the map -- scales with that). Re-applying
        /// <c>driftMult</c> to the loss-derived term here on top of that (the old code
        /// folded it into <c>stormFactor</c> and multiplied the whole sum by it) squared the
        /// slider's effect on that one term, so cranking "Drift speed" made a map bury
        /// itself far faster than transport alone would explain -- exactly the ratio drift
        /// the mod-settings doc for this multiplier promises never happens. The weather-only
        /// factor still scales both terms (a storm's own influx boost is a separate, real
        /// knob); <paramref name="driftMult"/> now applies exactly once more, on the flat
        /// per-day baseline only, which has no other route to the slider.
        /// </summary>
        /// <summary>Debt added per batch: the loss term scales by the weather only (the drift slider
        /// already shaped lostDepth), the flat per-day baseline by weather AND the slider, once each.</summary>
        public static float InfluxDebtDelta(RM_DuneMaterialDef m, float lostDepth, float weather, float driftMult)
        {
            return RM_DuneKernel.InfluxDebtDelta(lostDepth, m.influxLossRatio, m.influxPerDay, weather, driftMult);
        }

        private void RunInflux(float lostDepth, float stormFactor, float driftMult)
        {
            IntVec3 wind = WindVector;
            RM_DuneKernel.RunInflux(new MapDuneField(map), ref influxDebt, lostDepth, stormFactor, driftMult, ParamsCache.For(material), material.influxLossRatio,
                material.influxPerDay, material.maxTotalMassFraction, material.AttemptsPerBatch(map.cellIndices.NumGridCells), wind.x, wind.z,
                BoundaryHysteresis, (lo, hi) => Rand.Range(lo, hi));
        }

        // ------------------------------------------------------------------ burial

        private void TryBuryAt(IntVec3 cell)
        {
            // mod option: buried caches disabled; at the cap: no NEW cache cells, existing ones still merge
            bool burialOn = MovingDunesSettings.burialEnabled;
            if (!RM_CacheKernel.BuryAllowed(burialOn, DuneBurialUtility.CacheAt(cell, map) != null,
                    burialOn ? CacheCount() : 0, material.maxCachesPerMap))
            {
                return;
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
        public static int ChokeSamples(RM_DuneMaterialDef m, int numCells, float stormFactor)
        {
            return RM_DuneKernel.ChokeSamples(m.AttemptsPerBatch(numCells), m.plantChokeSampleFraction, stormFactor);
        }

        /// <summary>Damage per visit, sized so a fully-buried plant dies in plantChokeDays.</summary>
        public static int ChokeDamage(float maxHitPoints, float chokeDays, float visitsPerDay)
        {
            return RM_DuneKernel.ChokeDamage(maxHitPoints, chokeDays, visitsPerDay);
        }

        /// <summary>Batches per in-game day, for the proof hook's visit-rate arithmetic.</summary>
        public const int BatchesPerGameDay = BatchesPerDay;

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
            int samples = ChokeSamples(material, cells, stormFactor);
            if (samples < 1)
            {
                return;
            }

            // Expected visits to any one cell per in-game day, from this very sample rate.
            float visitsPerDay = RM_DuneKernel.VisitsPerDay(samples, cells);
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
                int damage = ChokeDamage(plant.MaxHitPoints, material.plantChokeDays, visitsPerDay);
                plant.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, damage));
            }
        }

        // ------------------------------------------------------------------- debug

        /// <summary>Proof hook: the shipped burial gate (burialEnabled, cache cap, candidates) on one cell.</summary>
        public void ProofTryBuryAt(IntVec3 cell)
        {
            TryBuryAt(cell);
        }

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
            float driftMult = MovingDunesSettings.transportRateMultiplier;
            stormTransport *= driftMult;
            for (int i = 0; i < count; i++)
            {
                float lost = RunTransportBatch(stormTransport);
                RunInflux(lost, stormInflux, driftMult);
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
