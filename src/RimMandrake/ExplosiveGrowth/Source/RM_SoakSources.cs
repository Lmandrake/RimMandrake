using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // THE §1 SOAK ROUTES THIS ENGINE READS FOR ITSELF.
    //
    //   crack_flood      PUSHED, not read: mandrake.rm.floodedcanyon calls
    //                    ExplosiveGrowthAPI.Soak on every cell its flood
    //                    wets. (That mod's own light soak stub is retired.)
    //   player irrigation  READ here from FlowWorks: a DUG cell holding a
    //                    qualifying fresh fluid soaks itself and its 8
    //                    neighbours. FlowWorks' own header names this:
    //                    "irrigation wants a per-cell soak map". Natural
    //                    liquid (rivers, lakes) reads through as SUPERDEEP
    //                    with depth-grid 0 and is deliberately NOT a soak —
    //                    river_steam stopped being one on 2026-09-21.
    //   miasma_axis      READ here from EnvironmentalHazards' gradient axis:
    //                    while a surge shift is running, the fresh side of
    //                    the salt line soaks ("the surge line decides which
    //                    half blooms"). Miasma plants churn, never burst.
    //   red_water etc.   A roster-named WEATHER soaks open ground while it
    //                    runs. No weather is named by default: the Contagion
    //                    rain, scald_melt and slime_flood have no def/system
    //                    yet (OWED, see the item file).
    //   Greentide extract  NOT BUILT (the item does not exist yet) — OWED.
    //
    // Both READ routes are reflection-soft: neither mod is a dependency, and
    // with either absent that route is simply silent.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SoakSources
    {
        // 🄸 INVENTED: an irrigated cell stays soaked a day after its last
        // re-read; a full grid sweep takes 8 passes (2000 ticks).
        private const int IrrigationSoakTicks = GenDate.TicksPerDay;
        private const int SliceCount = 8;
        // 🄸 INVENTED: the band of the fresh side that blooms in a surge.
        private const float SurgeFreshMin = 0.25f;
        private const float SurgeFreshMax = 0.48f;
        private const int SurgeSoakTicks = GenDate.TicksPerDay;
        private const int WeatherSoakTicks = GenDate.TicksPerDay / 2;

        private static bool resolved;
        private static Type excavationType;
        private static FieldInfo depthGridField, fillGridField;
        private static PropertyInfo activeFluidProp;
        private static Type gradientType;
        private static FieldInfo salinityField;
        private static PropertyInfo shiftInProgressProp;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                excavationType = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_MapComponent_Excavation");
                if (excavationType != null)
                {
                    depthGridField = AccessTools.Field(excavationType, "depthGrid");
                    fillGridField = AccessTools.Field(excavationType, "fillGrid");
                    activeFluidProp = AccessTools.Property(excavationType, "ActiveFluid");
                }
                gradientType = AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_MapComponent_GradientAxis");
                if (gradientType != null)
                {
                    salinityField = AccessTools.Field(gradientType, "salinity");
                    shiftInProgressProp = AccessTools.Property(gradientType, "ShiftInProgress");
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RM ExplosiveGrowth] soak-source reflection failed; irrigation/surge soak disabled: " + e.Message);
                excavationType = null;
                gradientType = null;
            }
        }

        public static void Pulse(RM_MapComponent_ExplosiveGrowth comp, int now)
        {
            Resolve();
            Map map = comp.map;
            if (RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome)) return;
            try
            {
                if (ExplosiveGrowthSettings.irrigationSoakEnabled && excavationType != null) PulseIrrigation(comp, map);
                if (ExplosiveGrowthSettings.gradientSurgeSoakEnabled && gradientType != null) PulseSurge(comp, map);
                if (ExplosiveGrowthSettings.weatherSoakEnabled && RM_ExplosiveGrowthRegistry.SoakWeathers.Count > 0) PulseWeather(comp, map);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM ExplosiveGrowth] soak-source pulse failed: " + e, 0x5E0A);
            }
        }

        private static MapComponent FindComp(Map map, Type t)
        {
            List<MapComponent> list = map.components;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] != null && t.IsInstanceOfType(list[i])) return list[i];
            }
            return null;
        }

        private static void PulseIrrigation(RM_MapComponent_ExplosiveGrowth comp, Map map)
        {
            MapComponent ex = FindComp(map, excavationType);
            if (ex == null) return;
            if (!(depthGridField?.GetValue(ex) is byte[] depth) || !(fillGridField?.GetValue(ex) is byte[] fill)) return;
            if (activeFluidProp?.GetValue(ex) is Def fluid && !RM_ExplosiveGrowthRegistry.IrrigationFluids.Contains(fluid.defName)) return;

            int n = depth.Length;
            if (fill.Length != n) return;
            int slice = (n + SliceCount - 1) / SliceCount;
            int start = (comp.irrigationCursor % SliceCount) * slice;
            int end = Math.Min(n, start + slice);
            comp.irrigationCursor = (comp.irrigationCursor + 1) % SliceCount;

            CellIndices idx = map.cellIndices;
            for (int i = start; i < end; i++)
            {
                if (depth[i] == 0 || fill[i] == 0) continue;
                IntVec3 c = idx.IndexToCell(i);
                comp.TrySoak(c, IrrigationSoakTicks);
                for (int d = 0; d < 8; d++)
                {
                    IntVec3 nb = c + GenAdj.AdjacentCells[d];
                    if (nb.InBounds(map)) comp.TrySoak(nb, IrrigationSoakTicks);
                }
            }
        }

        private static void PulseSurge(RM_MapComponent_ExplosiveGrowth comp, Map map)
        {
            MapComponent axis = FindComp(map, gradientType);
            if (axis == null) return;
            if (!(shiftInProgressProp?.GetValue(axis) is bool running) || !running) return;
            if (!(salinityField?.GetValue(axis) is float[] sal)) return;

            int n = sal.Length;
            int slice = (n + SliceCount - 1) / SliceCount;
            int start = (comp.surgeCursor % SliceCount) * slice;
            int end = Math.Min(n, start + slice);
            comp.surgeCursor = (comp.surgeCursor + 1) % SliceCount;

            CellIndices idx = map.cellIndices;
            for (int i = start; i < end; i++)
            {
                float s = sal[i];
                if (s < SurgeFreshMin || s > SurgeFreshMax) continue;
                comp.TrySoak(idx.IndexToCell(i), SurgeSoakTicks);
            }
        }

        private static void PulseWeather(RM_MapComponent_ExplosiveGrowth comp, Map map)
        {
            WeatherDef w = map.weatherManager?.curWeather;
            if (w == null || !RM_ExplosiveGrowthRegistry.SoakWeathers.Contains(w)) return;
            // 🄸 INVENTED: rain soaks a scatter of open, unroofed ground each
            // pulse rather than the whole map at once — the soak spreads while
            // the rain lasts.
            int tries = Math.Max(20, map.Area / 300);
            for (int i = 0; i < tries; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.Roofed(map)) continue;
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.IsWater) continue;
                comp.TrySoak(c, WeatherSoakTicks);
            }
        }
    }
}
