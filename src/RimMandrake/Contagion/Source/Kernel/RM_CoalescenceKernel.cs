// Verse-free kernel of the Coalescence (Building_RM_Coalescence): stage from absorbed mass, per-stage tables, the passive
// growth and emission clocks, the manhunter cap, and the death spill. The building calls these with the same expressions;
// SelfTest/ContagionFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Contagion
{
    public static class RM_CoalescenceKernel
    {
        // The highest stage whose threshold the mass has reached (thresholds ascend; [0] is 0).
        public static int Stage(int mass, IList<int> stageMass)
        {
            int s = 0;
            for (int i = 0; i < stageMass.Count; i++)
            {
                if (mass >= stageMass[i]) s = i;
            }
            return s;
        }

        // A per-stage table value, clamped to the table's ends; the fallback for an empty table.
        public static int At(IList<int> list, int i, int fallback)
        {
            if (list == null || list.Count == 0) return fallback;
            int idx = i < 0 ? 0 : (i > list.Count - 1 ? list.Count - 1 : i);
            return list[idx];
        }

        public static bool PassiveGrowthDue(int passiveGrowthTicks, int now, int lastGrowthTick) { return passiveGrowthTicks > 0 && now - lastGrowthTick >= passiveGrowthTicks; }

        public static bool EmitDue(int now, int lastEmitTick, int intervalForStage) { return now - lastEmitTick >= intervalForStage; }

        // Emission is held back at the stage's cap of live manhunters.
        public static bool MayEmit(int liveManhunters, int maxForStage) { return liveManhunters < maxForStage; }

        // Genome samples spilled on death: base + perStage * stage + mass / massPerSample, capped.
        public static int Samples(int samplesBase, int samplesPerStage, int stage, int massPerSample, int mass, int samplesMax)
        {
            return Math.Min(samplesMax, samplesBase + samplesPerStage * stage + (massPerSample > 0 ? mass / massPerSample : 0));
        }

        // Burn catches it: collapses even with the setting off. Otherwise it only acts with the setting on.
        public static bool Collapses(bool burnActive) { return burnActive; }
        public static bool Acts(bool burnActive, bool coalescenceEnabled) { return !burnActive && coalescenceEnabled; }
    }
}
