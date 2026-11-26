using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 6: ambient heat is vanilla AIR temperature.
    //
    // Owner card 2026-10-19 on volcanic, steam and hot-fog heat: "Hotter air on the thermometer". A biome whose air
    // is hot (the Forge, the Scald, the Greentide; the Fever Wood when its hold lifts) names a vanilla
    // GameConditionDef of class GameCondition_TemperatureOffset. Every map of that biome carries the condition
    // permanently, so the heat shows on the thermometer and in the conditions list, rooms leak toward it, coolers
    // fight it and insulation answers it, all the vanilla way. Shade never cools it. It is never Direct Sun and never
    // switches off with Direct Sun.
    //
    // The condition's offset is the def's temperatureOffset. The biome mod's own Mod Settings write that field (its
    // on/off and its °C slider; off writes 0), and this component follows it: 0 ends the condition, any other value
    // starts it or retunes the running one.
    //
    // The natives live in that air. The plant check of spec 6 (Utils/direct_sun_air_heat_plant_check.py, 2026-11-26)
    // measured that 12 °C on the Greentide drops its 21 trees from 0.78 to 0.03 growth, and 15 °C on the Scald stops 7 of
    // its 8 plants. So each wild plant of a hot-air biome has its upper growth bounds raised by the current offset, from
    // its band as loaded (widen only: owner, 2026-08-23, "I am ruling for widening only please"). A foreign crop still
    // feels the heat. The fit is recomputed from the loaded band whenever the offset changes, so it never stacks.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AirHeatExtension : DefModExtension
    {
        public GameConditionDef condition;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (condition == null)
            {
                yield return "RM_AirHeatExtension: no condition";
            }
            else if (!typeof(GameCondition_TemperatureOffset).IsAssignableFrom(condition.conditionClass))
            {
                yield return "RM_AirHeatExtension: " + condition.defName + " is not a GameCondition_TemperatureOffset";
            }
        }
    }

    public static class RM_AirHeatNatives
    {
        private struct Band
        {
            public float maxOptimal, max;
        }

        private static readonly Dictionary<ThingDef, Band> loaded = new Dictionary<ThingDef, Band>();
        private static readonly Dictionary<BiomeDef, float> fittedFor = new Dictionary<BiomeDef, float>();

        /// <summary>The upper bounds a native plant needs in air this much hotter: its loaded band raised by the offset,
        /// never below the loaded band (pure; selftest_direct_sun.py reads the same rule).</summary>
        public static void Fit(float loadedMaxOptimal, float loadedMax, float offsetC, out float maxOptimal, out float max)
        {
            float up = offsetC > 0f ? offsetC : 0f;
            maxOptimal = loadedMaxOptimal + up;
            max = loadedMax + up;
        }

        /// <summary>Fit every wild plant of this biome to its air-heat offset. Idempotent per offset. A plant native to
        /// two hot-air biomes takes the larger of their offsets.</summary>
        public static void FitFor(BiomeDef biome, float offsetC)
        {
            if (biome == null || (fittedFor.TryGetValue(biome, out float done) && done == offsetC))
            {
                return;
            }
            fittedFor[biome] = offsetC;
            foreach (ThingDef p in biome.AllWildPlants)
            {
                if (p?.plant == null)
                {
                    continue;
                }
                if (!loaded.TryGetValue(p, out Band b))
                {
                    b = new Band { maxOptimal = p.plant.maxOptimalGrowthTemperature, max = p.plant.maxGrowthTemperature };
                    loaded[p] = b;
                }
                float need = 0f;
                foreach (KeyValuePair<BiomeDef, float> kv in fittedFor)
                {
                    if (kv.Value > need && kv.Key.AllWildPlants.Contains(p))
                    {
                        need = kv.Value;
                    }
                }
                Fit(b.maxOptimal, b.max, need, out float mo, out float mx);
                p.plant.maxOptimalGrowthTemperature = mo;
                p.plant.maxGrowthTemperature = mx;
            }
        }
    }

    /// <summary>Fits the natives of every hot-air biome at startup, before any map is generated; a map's Sync re-fits
    /// when a Mod Setting moved the offset.</summary>
    [StaticConstructorOnStartup]
    public static class RM_AirHeatStartup
    {
        static RM_AirHeatStartup()
        {
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                GameConditionDef c = b.GetModExtension<RM_AirHeatExtension>()?.condition;
                if (c != null)
                {
                    RM_AirHeatNatives.FitFor(b, c.temperatureOffset);
                }
            }
        }
    }

    public class RM_MapComponent_AirHeat : MapComponent
    {
        // Danger guarded: a Mod Settings change of the offset reaches running maps. Evidence: the slider exists. One
        // in-game hour is far below anything a player would notice; the check is O(conditions).
        private const int CheckIntervalTicks = 2500;

        public RM_MapComponent_AirHeat(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Sync();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % CheckIntervalTicks == 41)
            {
                Sync();
            }
        }

        /// <summary>The biome's air-heat condition, or null.</summary>
        public static GameConditionDef ConditionFor(Map map)
        {
            return map?.Biome?.GetModExtension<RM_AirHeatExtension>()?.condition;
        }

        public void Sync()
        {
            GameConditionDef def = ConditionFor(map);
            GameConditionManager gcm = map?.gameConditionManager;
            if (def == null || gcm == null)
            {
                return;
            }
            GameCondition_TemperatureOffset live = gcm.GetActiveCondition(def) as GameCondition_TemperatureOffset;
            float want = def.temperatureOffset;
            RM_AirHeatNatives.FitFor(map.Biome, want);
            if (want == 0f)
            {
                live?.End();
                return;
            }
            if (live == null)
            {
                live = GameConditionMaker.MakeConditionPermanent(def) as GameCondition_TemperatureOffset;
                if (live == null)
                {
                    return;
                }
                gcm.RegisterCondition(live);
            }
            live.tempOffset = want;
        }
    }
}
