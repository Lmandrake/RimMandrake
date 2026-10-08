using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_THURROCK_HERD_BUILD_1 §9 Mod Settings. RM_ThurrockShatter carries two
    // HediffComp_PeriodicAreaAttack comps: the resting tree-felling aura (minSeverity 0) and
    // the provoked wall-shouldering aura (minSeverity > 0, keyed by RM_HediffComp_AggroSeverity).
    // The aura reads its Props every tick, so the settings are written onto the live props,
    // same mechanism as RM_GreentideDensityApplier writing the live BiomeDef. Shipped XML values
    // are captured once, so turning a toggle back on restores them exactly.
    [StaticConstructorOnStartup]
    public static class RM_ThurrockAuraStartup
    {
        static RM_ThurrockAuraStartup()
        {
            LongEventHandler.ExecuteWhenFinished(RM_ThurrockAuraApplier.Apply);
        }
    }

    public static class RM_ThurrockAuraApplier
    {
        private class Shipped
        {
            public int tickIntervalTicks;
            public float plantMultiplier;
            public float buildingMultiplier;
            public float fellsTreesBelowHealthFraction;
        }

        private static readonly Dictionary<HediffCompProperties_PeriodicAreaAttack, Shipped> shipped =
            new Dictionary<HediffCompProperties_PeriodicAreaAttack, Shipped>();

        public static void Apply()
        {
            HediffDef def = DefDatabase<HediffDef>.GetNamedSilentFail("RM_ThurrockShatter");
            if (def?.comps == null)
            {
                return;
            }
            for (int i = 0; i < def.comps.Count; i++)
            {
                if (!(def.comps[i] is HediffCompProperties_PeriodicAreaAttack p))
                {
                    continue;
                }
                if (!shipped.TryGetValue(p, out Shipped s))
                {
                    s = new Shipped
                    {
                        tickIntervalTicks = p.tickIntervalTicks,
                        plantMultiplier = p.plantMultiplier,
                        buildingMultiplier = p.buildingMultiplier,
                        fellsTreesBelowHealthFraction = p.fellsTreesBelowHealthFraction,
                    };
                    shipped[p] = s;
                }

                bool provoked = p.minSeverity > 0f;
                if (provoked)
                {
                    p.buildingMultiplier = RM_RulesKernel.Gated(RM_GreentideSettings.thurrockProvokedWallDamage, s.buildingMultiplier);
                }
                else
                {
                    bool fell = RM_GreentideSettings.thurrockFellingEnabled;
                    p.plantMultiplier = RM_RulesKernel.Gated(fell, s.plantMultiplier);
                    p.fellsTreesBelowHealthFraction = RM_RulesKernel.Gated(fell, s.fellsTreesBelowHealthFraction);
                    p.tickIntervalTicks = RM_RulesKernel.ThurrockInterval(s.tickIntervalTicks, RM_GreentideSettings.thurrockFellingPace);
                }
            }
        }
    }
}
