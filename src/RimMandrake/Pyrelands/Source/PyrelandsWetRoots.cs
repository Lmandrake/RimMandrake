using System;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// Wet roots. The Pyrelands' tiles sit at a 53.6 C median, and a vanilla crop grows only between its optimal 42 C and its
    /// 58 C stop, and only from 06:00 to 19:00, the hottest hours: measured on a 50 C landing (map q, 2026-11-07) rice read a
    /// 0-16% temperature multiplier through the growing day and gained 4% growth a day, watered or not, so the biome's own
    /// promise ("wherever water reaches it, it grows almost anything") was false and a canal changed nothing a player could see.
    /// Here a plant standing on ash-field ground that the ash field counts as watered (MapComponent_PyrelandsAshField.IsWatered:
    /// beside dug water, near a pond or mud, or after a Black Rain) reads its temperature growth factor as if its cell were
    /// PyrelandsTuning.WetRootsCoolingC cooler, never lower than vanilla's. Dry ash keeps vanilla's heat. The plant's inspect pane
    /// says so when it changes the number. Same gate as watered fertility (Mod Settings: ash water fertility).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsWetRoots
    {
        static PyrelandsWetRoots()
        {
            var h = new Harmony("mandrake.rm.pyrelands.wetroots");
            try
            {
                h.Patch(AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.GrowthRateFactor_Temperature)),
                    postfix: new HarmonyMethod(typeof(PyrelandsWetRoots), nameof(Postfix_Temperature)));
                h.Patch(AccessTools.Method(typeof(Plant), nameof(Plant.GetInspectString)),
                    postfix: new HarmonyMethod(typeof(PyrelandsWetRoots), nameof(Postfix_Inspect)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] wet roots: patch FAILED, watered ash gives crops no heat relief: " + e.Message);
            }
        }

        /// <summary>The cooled factor if wet roots apply to this plant now, else -1.</summary>
        internal static float CooledFactor(Plant plant, out float cellTemp)
        {
            cellTemp = 0f;
            if (plant == null || !plant.Spawned || !RM_PyrelandsSettings.ashWaterFertilityEnabled || !PyrelandsMechanicsGate.On) return -1f;
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            if (PyrelandsAshFieldPatches.ExtOf(map.terrainGrid.TerrainAt(c)) == null) return -1f;
            if (!GenTemperature.TryGetTemperatureForCell(c, map, out cellTemp)) return -1f;
            if (cellTemp <= plant.def.plant.maxOptimalGrowthTemperature) return -1f;
            MapComponent_PyrelandsAshField field = MapComponent_PyrelandsAshField.For(map);
            if (field == null || !field.IsWatered(c, Find.TickManager.TicksGame)) return -1f;
            return PlantUtility.GrowthRateFactorFor_Temperature(plant.def,
                RM_FireEcoKernel.WetRootTemperature(cellTemp, PyrelandsTuning.WetRootsCoolingC));
        }

        public static void Postfix_Temperature(Plant __instance, ref float __result)
        {
            try
            {
                float cooled = CooledFactor(__instance, out _);
                if (cooled > __result) __result = cooled;
            }
            catch (Exception)
            {
                // a growth read must never throw; vanilla's number stands
            }
        }

        public static void Postfix_Inspect(Plant __instance, ref string __result)
        {
            try
            {
                float vanilla = __instance.Spawned && GenTemperature.TryGetTemperatureForCell(__instance.Position, __instance.Map, out float t)
                    ? PlantUtility.GrowthRateFactorFor_Temperature(__instance.def, t) : 1f;
                float cooled = CooledFactor(__instance, out _);
                if (cooled <= vanilla + 0.005f) return;
                var sb = new StringBuilder(__result ?? "");
                if (sb.Length > 0) sb.AppendLine();
                sb.Append("RM_WetRootsInspect".Translate(PyrelandsTuning.WetRootsCoolingC.ToStringTemperatureOffset("F0"),
                    vanilla.ToStringPercent()));
                __result = sb.ToString();
            }
            catch (Exception)
            {
            }
        }
    }
}
