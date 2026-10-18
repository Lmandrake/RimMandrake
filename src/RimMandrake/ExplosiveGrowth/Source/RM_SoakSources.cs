using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // THE PUSHED (TIMED) SOURCES THIS ENGINE READS FOR ITSELF. Every other water source (natural water, spills, channels,
    // rain, ash) is read ON DEMAND by RM_WetSources (the presence model, ruled spec §2-3); only the salt-line surge still
    // writes timed soaks here, as the miasma surge always did (OQ-13: it stays a water source, unchanged).
    //   crack_flood   PUSHED by mandrake.rm.crackedlands through ExplosiveGrowthAPI.SoakCells while the flood runs.
    //   miasma_axis   READ here from EnvironmentalHazards' gradient axis: while a surge shift runs, the fresh side soaks.
    // Reflection-soft: with Environmental Hazards absent the route is silent.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SoakSources
    {
        // 🄸 INVENTED: an irrigated cell stays soaked a day after its last
        // re-read; a full grid sweep takes 8 passes (2000 ticks).
        // 🄸 INVENTED: the band of the fresh side that blooms in a surge.
        private const int SurgeSoakTicks = GenDate.TicksPerDay;

        private static bool resolved;
        private static Type gradientType;
        private static FieldInfo salinityField;
        private static PropertyInfo shiftInProgressProp;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            try
            {
                gradientType = AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_MapComponent_GradientAxis");
                if (gradientType != null)
                {
                    salinityField = AccessTools.Field(gradientType, "salinity");
                    shiftInProgressProp = AccessTools.Property(gradientType, "ShiftInProgress");
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RM ExplosiveGrowth] soak-source reflection failed; surge soak disabled: " + e.Message);
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
                if (ExplosiveGrowthSettings.gradientSurgeSoakEnabled && gradientType != null) PulseSurge(comp, map);
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

        private static void PulseSurge(RM_MapComponent_ExplosiveGrowth comp, Map map)
        {
            MapComponent axis = FindComp(map, gradientType);
            if (axis == null) return;
            if (!(shiftInProgressProp?.GetValue(axis) is bool running) || !running) return;
            if (!(salinityField?.GetValue(axis) is float[] sal)) return;

            int n = sal.Length;
            RM_ExplosiveGrowthKernel.SliceRange(n, comp.surgeCursor, out int start, out int end);
            comp.surgeCursor = RM_ExplosiveGrowthKernel.NextCursor(comp.surgeCursor);

            CellIndices idx = map.cellIndices;
            for (int i = start; i < end; i++)
            {
                float s = sal[i];
                if (!RM_ExplosiveGrowthKernel.InSurgeBand(s)) continue;
                comp.TrySoak(idx.IndexToCell(i), SurgeSoakTicks);
            }
        }
    }
}
