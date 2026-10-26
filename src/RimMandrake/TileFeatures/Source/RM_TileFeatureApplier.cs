using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TileFeatures
{
    // Applies the Mod Settings to the tile-feature defs: at startup and every time the settings window is closed.
    // Each def's original state is snapshotted once, restored, then a switched-off group is made inert (no worker, no extra
    // gen steps, conditions or weathers, neutral densities, no VEF extension) and a switched-on group gets its numbers.
    // VEF's TileMutatorExtension is reached by reflection so this assembly has no compile-time VEF reference.
    [StaticConstructorOnStartup]
    public static class RM_TileFeatureApplier
    {
        public static readonly string[] Flora =
        {
            "RM_Cactus_Barrel", "RM_Cactus_Beavertail", "RM_Cactus_Hedgehog", "RM_Cactus_OrganPipe", "RM_RedDesertPlants",
            "RM_Mycelium", "RM_PlantLife_Overgrown", "RM_PlantLife_Decimated", "RM_NoTrees", "RM_PoisonousFlora",
            "RM_Fertility_Reduced", "RM_MarineSanctuary", "RM_MechanoidShipChunks",
        };
        public static readonly string[] Weather = { "RM_Sandstorms", "RM_DustStorms", "RM_RottenStench" };
        public static readonly string[] Vents = { "RM_ToxicVents", "RM_RotstinkVents", "RM_SmokeVents" };
        public static readonly string[] Diseases = { "RM_IncreasedDiseases" };
        public static readonly string[] Infestations = { "RM_IncreasedInfestations" };

        private const string VefExtension = "VEF.Maps.TileMutatorExtension";

        private static readonly FieldInfo WorkerClassField = AccessTools.Field(typeof(TileMutatorDef), "workerClass");
        private static readonly FieldInfo WorkerCacheField = AccessTools.Field(typeof(TileMutatorDef), "mutatorWorker");

        private class Snapshot
        {
            public Type workerClass;
            public List<GenStepDef> extraGenSteps;
            public List<GameConditionDef> additionalGameConditions;
            public List<WeatherDef> weathersToAffect;
            public float plantDensityFactor, animalDensityFactor;
            public List<DefModExtension> modExtensions;
            public IntRange? prefabsToSpawnAmount;
        }

        private static readonly Dictionary<TileMutatorDef, Snapshot> snapshots = new Dictionary<TileMutatorDef, Snapshot>();
        private static bool warned;

        static RM_TileFeatureApplier()
        {
            Apply();
        }

        public static void Apply()
        {
            if (WorkerClassField == null || WorkerCacheField == null)
            {
                if (!warned) Log.Warning("[RM TileFeatures] TileMutatorDef worker fields not found (game update?): Mod Settings switches cannot take effect.");
                warned = true;
                return;
            }
            ApplyGroup(Flora, RM_TileFeaturesSettings.floraEnabled);
            ApplyGroup(Weather, RM_TileFeaturesSettings.weatherEnabled);
            ApplyGroup(Vents, RM_TileFeaturesSettings.ventsEnabled && RM_TileFeaturesSettings.ventCountScale > 0f);
            ApplyGroup(Diseases, RM_TileFeaturesSettings.diseasesEnabled);
            ApplyGroup(Infestations, RM_TileFeaturesSettings.infestationsEnabled);
        }

        private static void ApplyGroup(string[] names, bool on)
        {
            foreach (string name in names)
            {
                TileMutatorDef def = DefDatabase<TileMutatorDef>.GetNamedSilentFail(name);
                if (def == null)
                {
                    Log.Warning("[RM TileFeatures] tile feature " + name + " not loaded; its Mod Settings switch does nothing.");
                    continue;
                }
                Restore(def);
                if (on) Tune(def);
                else MakeInert(def);
                WorkerCacheField.SetValue(def, null); // Worker is rebuilt lazily from workerClass
            }
        }

        private static void Restore(TileMutatorDef def)
        {
            if (!snapshots.TryGetValue(def, out Snapshot s))
            {
                s = new Snapshot
                {
                    workerClass = (Type)WorkerClassField.GetValue(def),
                    extraGenSteps = new List<GenStepDef>(def.extraGenSteps ?? new List<GenStepDef>()),
                    additionalGameConditions = new List<GameConditionDef>(def.additionalGameConditions ?? new List<GameConditionDef>()),
                    weathersToAffect = new List<WeatherDef>(def.weathersToAffect ?? new List<WeatherDef>()),
                    plantDensityFactor = def.plantDensityFactor,
                    animalDensityFactor = def.animalDensityFactor,
                    modExtensions = def.modExtensions == null ? null : new List<DefModExtension>(def.modExtensions),
                };
                object ext = VefExt(def);
                FieldInfo f = ext == null ? null : AccessTools.Field(ext.GetType(), "prefabsToSpawnAmount");
                if (f != null && f.FieldType == typeof(IntRange)) s.prefabsToSpawnAmount = (IntRange)f.GetValue(ext);
                snapshots[def] = s;
            }
            WorkerClassField.SetValue(def, s.workerClass);
            def.extraGenSteps = new List<GenStepDef>(s.extraGenSteps);
            def.additionalGameConditions = new List<GameConditionDef>(s.additionalGameConditions);
            def.weathersToAffect = new List<WeatherDef>(s.weathersToAffect);
            def.plantDensityFactor = s.plantDensityFactor;
            def.animalDensityFactor = s.animalDensityFactor;
            def.modExtensions = s.modExtensions == null ? null : new List<DefModExtension>(s.modExtensions);
        }

        private static void MakeInert(TileMutatorDef def)
        {
            WorkerClassField.SetValue(def, null);
            def.extraGenSteps = new List<GenStepDef>();
            def.additionalGameConditions = new List<GameConditionDef>();
            def.weathersToAffect = new List<WeatherDef>();
            def.plantDensityFactor = 1f;
            def.animalDensityFactor = 1f;
            def.modExtensions?.RemoveAll(e => e != null && e.GetType().FullName == VefExtension);
        }

        private static void Tune(TileMutatorDef def)
        {
            object ext = VefExt(def);
            if (ext == null) return;
            Type t = ext.GetType();
            if (def.defName == "RM_IncreasedDiseases")
            {
                FieldInfo f = AccessTools.Field(t, "diseaseMTBMultiplier");
                if (f != null && f.FieldType == typeof(float)) f.SetValue(ext, RM_TileFeaturesSettings.diseaseMtbMultiplier);
            }
            // Only the vents' prefab count is a Mod Setting; every VEF extension carries a default 1~1 that must stay put.
            if (Array.IndexOf(Vents, def.defName) >= 0 && snapshots.TryGetValue(def, out Snapshot s) && s.prefabsToSpawnAmount.HasValue)
            {
                FieldInfo f = AccessTools.Field(t, "prefabsToSpawnAmount");
                IntRange r = s.prefabsToSpawnAmount.Value;
                float k = RM_TileFeaturesSettings.ventCountScale;
                f?.SetValue(ext, new IntRange(UnityEngine.Mathf.RoundToInt(r.min * k), UnityEngine.Mathf.RoundToInt(r.max * k)));
            }
        }

        private static object VefExt(TileMutatorDef def)
        {
            if (def.modExtensions == null) return null;
            foreach (DefModExtension e in def.modExtensions)
                if (e != null && e.GetType().FullName == VefExtension) return e;
            return null;
        }

        public static bool On(Map map, TileMutatorDef def)
        {
            return def != null && map?.TileInfo?.Mutators != null && map.TileInfo.Mutators.Contains(def);
        }
    }

    [DefOf]
    public static class RM_TileFeatureDefOf
    {
        public static TileMutatorDef RM_PoisonousFlora;
        public static TileMutatorDef RM_IncreasedInfestations;
        public static HediffDef RM_RottenStench;

        static RM_TileFeatureDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TileFeatureDefOf));
        }
    }
}
