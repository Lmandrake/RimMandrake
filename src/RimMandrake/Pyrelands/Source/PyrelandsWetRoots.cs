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
    ///
    /// The growth season too (live, map w 2026-11-08, 58.8 C under Black Rain: watered rice read "Growth rate: 0% (out of
    /// temperature growth range)" right above our "Grows as if 27F cooler" line). Vanilla's season gate,
    /// PlantUtility.GrowthSeasonNow(IntVec3, Map, ThingDef) (minGrowthTemperature &lt; T &lt; maxGrowthTemperature on the raw cell
    /// temperature), zeroes Plant.GrowthRate and skips the growth in Plant.TickLong, and sowing and the zone pane read it too. On
    /// the same watered ash it is read at the cooled root temperature, hot side only (RM_FireEcoKernel.WetRootGrowthSeason), so
    /// the season opens where the heat shut it and never shuts or warms a cold cell.
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
            try
            {
                h.Patch(AccessTools.Method(typeof(PlantUtility), nameof(PlantUtility.GrowthSeasonNow),
                        new[] { typeof(IntVec3), typeof(Map), typeof(ThingDef) }),
                    postfix: new HarmonyMethod(typeof(PyrelandsWetRoots), nameof(Postfix_GrowthSeason)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] wet roots: growth-season patch FAILED, a watered crop past its heat stop reads 0%: " + e.Message);
            }
        }

        /// <summary>Ash-field ground with the switches on: the only cells wet roots may touch.</summary>
        static bool AshGround(Map map, IntVec3 c)
        {
            return map != null && RM_PyrelandsSettings.ashWaterFertilityEnabled && PyrelandsMechanicsGate.On && c.InBounds(map)
                && PyrelandsAshFieldPatches.ExtOf(map.terrainGrid.TerrainAt(c)) != null;
        }

        static bool Watered(Map map, IntVec3 c)
        {
            MapComponent_PyrelandsAshField field = MapComponent_PyrelandsAshField.For(map);
            return field != null && field.IsWatered(c, Find.TickManager.TicksGame);
        }

        /// <summary>The cooled factor if wet roots apply to this plant now, else -1.</summary>
        internal static float CooledFactor(Plant plant, out float cellTemp)
        {
            cellTemp = 0f;
            if (plant == null || !plant.Spawned) return -1f;
            Map map = plant.Map;
            IntVec3 c = plant.Position;
            if (!AshGround(map, c)) return -1f;
            if (!GenTemperature.TryGetTemperatureForCell(c, map, out cellTemp)) return -1f;
            if (cellTemp <= plant.def.plant.maxOptimalGrowthTemperature) return -1f;
            if (!Watered(map, c)) return -1f;
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

        /// <summary>Vanilla said no season: on watered ash past the heat stop, ask again at the root temperature. Same cell
        /// read as vanilla's (c.GetTemperature is TryGetTemperatureForCell), same room-or-adjacent requirement.</summary>
        public static void Postfix_GrowthSeason(IntVec3 c, Map map, ThingDef plantDef, ref bool __result)
        {
            if (__result) return;
            try
            {
                if (plantDef?.plant == null || !AshGround(map, c)) return;
                if (!GenTemperature.TryGetTemperatureForCell(c, map, out float cellTemp) || cellTemp < plantDef.plant.maxGrowthTemperature) return;
                if (c.GetRoomOrAdjacent(map, RegionType.Set_All) == null || !Watered(map, c)) return;
                __result = RM_FireEcoKernel.WetRootGrowthSeason(cellTemp, plantDef.plant.minGrowthTemperature,
                    plantDef.plant.maxGrowthTemperature, PyrelandsTuning.WetRootsCoolingC);
            }
            catch (Exception)
            {
                // a season read must never throw; vanilla's answer stands
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
