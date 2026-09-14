using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <HediffDef>
    //     <defName>RUT_Miasma_LoamLunged</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_LocalGrowthAura">
    //         <radius>3</radius>
    //         <tickIntervalTicks>2500</tickIntervalTicks>
    //         <growthPerCycle>0.002</growthPerCycle>
    //       </li>
    //     </comps>
    //   </HediffDef>
    //
    // MIASMA_MECHANICS_1 M5 build pass, "Loam-lunged" (miasma_kit_spec.md
    // Owner cards #1, ruled 2026-09-12: "slightly faster plant growth
    // immediately around their sleeping/working spots ... PASSIVE AND TINY —
    // the line against the Greentide/explosive-growth soak territory is that
    // this never triggers, never surges, never scales").
    //
    // Generic, not Miasma-specific — a HediffComp that nudges Plant.Growth up
    // by a tiny amount, periodically, for plants in a small radius around the
    // carrier's current position. Crib of HediffComp_PeriodicAreaAttack's
    // CompPostTickInterval + GenRadial scan shape (this mod's own
    // ALPHA_MECHANICS_KIT_1 item), substituting a direct growth nudge for
    // area damage.
    //
    // Why new C#, not a stat offset or an existing comp: checked before
    // writing — no vanilla StatDef reaches "the ground gets slightly richer
    // wherever THIS pawn rests" (PlantDensityFactor is a map-wide
    // GameCondition virtual, already used by this mod's own M4 build pass,
    // not something a per-pawn Hediff can drive); RM_CompResourceCondenser
    // (SCALD_MECHANICS_1, vent-locked building output) and
    // HediffComp_PeriodicAreaAttack (ALPHA_MECHANICS_KIT_1, damage not
    // growth) are this mod's only "periodic radius effect" precedents and
    // neither does a growth nudge. Kept deliberately smaller than either: no
    // filth, no sound, no damage — a direct Plant.Growth write, clamped by
    // Plant.Growth's own setter (Verse/Plant.cs, Mathf.Clamp01), so this can
    // never push a plant past its normal maximum and never compounds into a
    // surge.
    public class CompProperties_LocalGrowthAura : HediffCompProperties
    {
        /// <summary>Cells around the carrier's current position nudged each
        /// cycle. INVENTED: 3 — "immediately around" (spec's own words), not
        /// room- or map-scale.</summary>
        public float radius = 3f;

        /// <summary>Ticks between nudge cycles. INVENTED: 2500 (~about an
        /// in-game hour) — frequent enough to matter over a full rest/work
        /// shift, rare enough that "never scales" holds by construction.</summary>
        public int tickIntervalTicks = 2500;

        /// <summary>Growth added per plant per cycle. INVENTED: 0.002 — the
        /// spec's own "PASSIVE AND TINY": at this rate a plant sat next to
        /// for a full day gains roughly 2% growth, not a free harvest.</summary>
        public float growthPerCycle = 0.002f;

        /// <summary>Minimum parent severity before this comp does anything —
        /// lets a def gate the aura behind a stage if a future author wants
        /// that; 0 means "on from the moment the hediff exists," this
        /// hediff's own default.</summary>
        public float minSeverity;

        public CompProperties_LocalGrowthAura()
        {
            compClass = typeof(RM_HediffComp_LocalGrowthAura);
        }
    }

    public class RM_HediffComp_LocalGrowthAura : HediffComp
    {
        private int ticksUntilCycle;

        public CompProperties_LocalGrowthAura Props => (CompProperties_LocalGrowthAura)props;

        public override void CompPostMake()
        {
            base.CompPostMake();
            // Stagger so a pack of carriers doesn't all nudge in lockstep.
            ticksUntilCycle = Rand.RangeInclusive(1, Mathf.Max(1, Props.tickIntervalTicks));
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (!RM_EnvironmentalHazardsSettings.localGrowthAuraEnabled)
            {
                return; // mod option: local growth aura disabled
            }

            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                return;
            }

            if (parent.Severity < Props.minSeverity)
            {
                return;
            }

            ticksUntilCycle -= delta;
            if (ticksUntilCycle > 0)
            {
                return;
            }
            ticksUntilCycle = Mathf.Max(1, Props.tickIntervalTicks);

            NudgeGrowth(pawn);
        }

        private void NudgeGrowth(Pawn pawn)
        {
            Map map = pawn.Map;
            IntVec3 origin = pawn.Position;

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(origin, Props.radius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                Plant plant = cell.GetPlant(map);
                if (plant == null || plant.Destroyed)
                {
                    continue;
                }

                plant.Growth += Props.growthPerCycle;
            }
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksUntilCycle, "ticksUntilCycle", 0);
        }
    }
}
