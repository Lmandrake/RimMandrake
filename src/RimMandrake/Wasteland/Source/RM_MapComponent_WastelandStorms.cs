using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    /// <summary>
    /// WASTELAND_MECHANICS_BUILD_1 §4 — the storm layer. While a weather carrying
    /// <see cref="RM_WeatherDoseExtension"/> runs on an opted-in biome's map:
    ///   * every ToxicUtility.CheckInterval ticks, unroofed pawns take the vanilla
    ///     airborne toxic dose scaled by the weather's factor (the dose layer);
    ///   * every 250 ticks, fall lands on random unroofed cells — Biotech-polluted
    ///     where the terrain can be, and remembered as fresh fall;
    ///   * when that weather ENDS, a fraction of its fresh fall germinates the
    ///     aftermath plant (the Cinderfelt, which then dies in ~8 days by its own
    ///     growDays x lifespanDaysPerGrowDays).
    ///
    /// Terrain re-deal / exhumation is NOT here: it rides MovingDunes (owner-ruled),
    /// bound by Patches/RM_Wasteland_MovingDunesBinding.xml.
    ///
    /// 🔴 Biome gate: this component exists on every map; it returns at once unless
    /// the map's BiomeDef carries <see cref="RM_WastelandStormBiomeExtension"/>.
    /// </summary>
    public class RM_MapComponent_WastelandStorms : MapComponent
    {
        private const int FallIntervalTicks = 250;
        private const int MaxFreshFall = 4000;
        private const float ReferenceMapCells = 250f * 250f;

        private List<IntVec3> freshFall = new List<IntVec3>();
        private WeatherDef trackedWeather;

        private int optInCacheState = -1; // -1 unknown, 0 no, 1 yes (unsaved)

        public RM_MapComponent_WastelandStorms(Map map) : base(map) { }

        /// <summary>Fresh-fall cells remembered for the current/last storm (debug read).</summary>
        public int FreshFallCount { get { return freshFall.Count; } }

        private bool OptedIn
        {
            get
            {
                if (optInCacheState < 0)
                {
                    optInCacheState = map.Biome != null
                        && map.Biome.GetModExtension<RM_WastelandStormBiomeExtension>() != null ? 1 : 0;
                }
                return optInCacheState == 1;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref freshFall, "freshFall", LookMode.Value);
            Scribe_Defs.Look(ref trackedWeather, "trackedWeather");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && freshFall == null)
            {
                freshFall = new List<IntVec3>();
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!RM_WastelandSettings.wastelandEnabled || !OptedIn)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            bool doseTick = now % ToxicUtility.CheckInterval == 0;
            bool fallTick = now % FallIntervalTicks == 0;
            if (!doseTick && !fallTick)
            {
                return;
            }

            WeatherDef cur = map.weatherManager.curWeather;
            if (fallTick && cur != trackedWeather)
            {
                OnWeatherChanged(trackedWeather);
                trackedWeather = cur;
            }

            RM_WeatherDoseExtension ext = cur != null ? cur.GetModExtension<RM_WeatherDoseExtension>() : null;
            if (ext == null)
            {
                return;
            }
            if (doseTick)
            {
                DoStormDose(ext);
            }
            if (fallTick)
            {
                DoFall(ext);
            }
        }

        // ------------------------------------------------------------------ dose

        private void DoStormDose(RM_WeatherDoseExtension ext)
        {
            if (!RM_WastelandSettings.stormDoseEnabled || ext.airborneToxicFactor <= 0f)
            {
                return;
            }
            float factor = ext.airborneToxicFactor * RM_WastelandSettings.stormDoseMultiplier;
            if (factor <= 0f)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.kindDef != null && p.kindDef.immuneToGameConditionEffects)
                {
                    continue;
                }
                ToxicUtility.DoAirbornePawnToxicDamage(p, factor);
            }
        }

        // ------------------------------------------------------------------ fall

        private void DoFall(RM_WeatherDoseExtension ext)
        {
            if (ext.fallCellsPerDay <= 0f)
            {
                return;
            }
            bool pollute = RM_WastelandSettings.ashFallPollutionEnabled && ModsConfig.BiotechActive;
            bool remember = RM_WastelandSettings.cinderfeltGerminationEnabled && ext.aftermathPlant != null;
            if (!pollute && !remember)
            {
                return;
            }
            float perBatch = ext.fallCellsPerDay * FallIntervalTicks / (float)GenDate.TicksPerDay
                             * (map.cellIndices.NumGridCells / ReferenceMapCells);
            int count = GenMath.RoundRandom(perBatch);
            for (int i = 0; i < count; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.Roofed(map) || !map.pollutionGrid.EverPollutable(c))
                {
                    continue;
                }
                if (pollute && map.pollutionGrid.CanPollute(c))
                {
                    // silent: fall is many cells a day; the per-cell pollution effecter
                    // would be pure spam and the weather overlay already shows the storm.
                    map.pollutionGrid.SetPolluted(c, true, silent: true);
                }
                if (remember)
                {
                    if (freshFall.Count < MaxFreshFall)
                    {
                        freshFall.Add(c);
                    }
                    else
                    {
                        freshFall[Rand.Range(0, freshFall.Count)] = c;
                    }
                }
            }
        }

        // ------------------------------------------------------------- aftermath

        private void OnWeatherChanged(WeatherDef ended)
        {
            RM_WeatherDoseExtension ext = ended != null ? ended.GetModExtension<RM_WeatherDoseExtension>() : null;
            if (ext != null && ext.aftermathPlant != null && RM_WastelandSettings.cinderfeltGerminationEnabled)
            {
                Germinate(ext);
            }
            freshFall.Clear();
        }

        /// <summary>Spawns the aftermath plant on a fraction of the remembered fresh
        /// fall. Public so a debug action / bridge state-read can drive it.</summary>
        public int Germinate(RM_WeatherDoseExtension ext)
        {
            if (freshFall.Count == 0)
            {
                return 0;
            }
            ThingDef plantDef = ext.aftermathPlant;
            int wanted = GenMath.RoundRandom(freshFall.Count * ext.aftermathSeedFraction);
            int spawned = 0;
            for (int i = 0; i < wanted; i++)
            {
                IntVec3 c = freshFall[Rand.Range(0, freshFall.Count)];
                if (!c.InBounds(map) || c.GetPlant(map) != null || c.GetEdifice(map) != null)
                {
                    continue;
                }
                if (!plantDef.CanEverPlantAt(c, map))
                {
                    continue;
                }
                Plant plant = (Plant)ThingMaker.MakeThing(plantDef);
                plant.Growth = Rand.Range(0.05f, 0.3f);
                GenSpawn.Spawn(plant, c, map);
                spawned++;
            }
            return spawned;
        }
    }
}
