using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Drinker: "sacks that it
    // uses to store drained body fluids. Strangely, if it drains any
    // day-side races with normal warm iron blood, it becomes poisoned and
    // rapidly dies."). See RM_CompFluidSacs for the full mechanism.
    public class RM_CompProperties_FluidSacs : CompProperties
    {
        /// <summary>Hunger restored (Need_Food.CurLevel, same units as
        /// vanilla nutrition) per point of drained-hediff severity fed back
        /// through — i.e. per point of RM_Drained.Severity, which itself is
        /// severityPerDamageDealt * the bite's actual damage dealt (see
        /// RM_Drained_Hediffs.xml). INVENTED: 0.02 — a solid bite (severity
        /// ~1) restores a small fraction of a small flier's own nutrition
        /// bar, several bites to fully feed rather than one.</summary>
        public float hungerRestoredPerSeverity = 0.02f;

        /// <summary>A drained victim whose RaceProps.FleshType is in this
        /// list poisons the drinker instead of feeding it — "day-side races
        /// with normal warm iron blood". Defaults to vanilla's own
        /// FleshTypeDefOf.Normal (humans and virtually every vanilla
        /// mammal/bird) set in XML so a content author can extend the list
        /// without new C#; left empty, nothing ever poisons this comp's
        /// owner (feeding always succeeds).</summary>
        public List<FleshTypeDef> poisonousFleshTypes;

        /// <summary>Hediff applied to the DRINKER itself (never the victim)
        /// when it drains a poisonous flesh type. Expected to carry its own
        /// fast ramp/lethalSeverity — this comp only adds it once per bad
        /// bite, no severity math here.</summary>
        public HediffDef poisonHediff;

        /// <summary>The visible gauge hediff on the DRINKER (RM_FluidSacks
        /// in this mod's Defs): every feed raises its severity by
        /// sackFillPerSeverity * drained severity, its own XML maxSeverity
        /// caps it, and on death its severity sets the drainedFluidsThing
        /// drop. Null = no gauge, no drop (hunger/poison still work).</summary>
        public HediffDef sacksHediff;

        /// <summary>Gauge severity gained per point of drained severity.
        /// INVENTED: 0.1 — about ten solid bites to fill the sacks.</summary>
        public float sackFillPerSeverity = 0.1f;

        /// <summary>Item dropped beside the corpse on death, count =
        /// round(gauge severity * drainedFluidsAtFull). RM_DrainedFluids in
        /// this mod's Defs; null = nothing drops.</summary>
        public ThingDef drainedFluidsThing;

        /// <summary>Items dropped by a drinker killed with FULL sacks
        /// (gauge severity 1). INVENTED: 10.</summary>
        public int drainedFluidsAtFull = 10;

        public RM_CompProperties_FluidSacs()
        {
            compClass = typeof(RM_CompFluidSacs);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (hungerRestoredPerSeverity < 0f)
            {
                yield return "RM_CompProperties_FluidSacs hungerRestoredPerSeverity must be >= 0.";
            }

            if (sackFillPerSeverity < 0f)
            {
                yield return "RM_CompProperties_FluidSacs sackFillPerSeverity must be >= 0.";
            }

            if (drainedFluidsAtFull < 0)
            {
                yield return "RM_CompProperties_FluidSacs drainedFluidsAtFull must be >= 0.";
            }

            if (drainedFluidsThing != null && sacksHediff == null)
            {
                yield return "RM_CompProperties_FluidSacs sets drainedFluidsThing but no sacksHediff — nothing would ever drop.";
            }

            if (!poisonousFleshTypes.NullOrEmpty() && poisonHediff == null)
            {
                yield return "RM_CompProperties_FluidSacs sets poisonousFleshTypes but no poisonHediff — nothing would happen on a bad bite.";
            }
        }
    }
}
