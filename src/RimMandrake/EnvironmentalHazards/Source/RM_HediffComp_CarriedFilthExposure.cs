using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_NASTINESS_1 (item spec §2, "tarred-pawn hediffs... severity
    // from exposure"). Sibling to HediffCompProperties_EnvironmentalExposure
    // (RUT_MiasmaExposure's own comp) but keyed on CARRIED FILTH rather than
    // weather+roof — this is the extension point the task brief named
    // explicitly: "triggers off RM_Filth_Tar presence in a pawn's filth
    // list," reusing SUMP_WALKWAYS_1's already-shipped filth-tracking
    // foundation instead of inventing a second tar representation.
    //
    // Pawn_FilthTracker.CarriedFilthListForReading (RimWorld/
    // Pawn_FilthTracker.cs, read in full this pass) is the real, public,
    // already-Scribed field this reads: a List<Filth> of whatever the pawn
    // is currently tracking on its boots, gained via
    // Pawn_FilthTracker.TryPickupFilth (standing in/crossing RM_TarShallow,
    // or a tar-coated cell laid by RM_Comp_TarCoatingSource — both feed the
    // exact same list) and lost via TryDropFilth (stepping onto a clean
    // cell that accepts the filth) or ordinary cleaning thinning it off a
    // terrain cell before it is ever picked up. This comp does not touch
    // that list itself — it only reads it — so it stays correct no matter
    // which of the two coating mechanisms (tracking or splash) put the tar
    // there.
    //
    //   <HediffDef>
    //     <defName>RUT_Tarred</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_CarriedFilthExposure">
    //         <filthDef>RM_Filth_Tar</filthDef>
    //         <severityPerDayCarrying>0.9</severityPerDayCarrying>
    //         <severityPerDayClean>-0.6</severityPerDayClean>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_CarriedFilthExposure : HediffCompProperties
    {
        // The filth def that keeps this hediff accruing while carried.
        // Null is a real config error, not "never accrues in any weather"
        // (EnvironmentalExposure's own ConfigErrors wording) — there is no
        // silent-inert reading here worth allowing, so this is flagged the
        // same way.
        public ThingDef filthDef;

        public float severityPerDayCarrying = 0.9f;

        // Heals off once the pawn's boots are clean again — plain avoidance
        // (never stepping in tar) already gets someone clean eventually.
        // This is deliberately NOT the only route off: a weak solvent
        // (RUT_ScrubTarredSolvent, this item's piece 3) removes the hediff
        // outright via a real Recipe_RemoveHediff bill, same shape
        // RSW_RemoveBrainWorm already uses in this repo — solvent is the
        // fast, deliberate cure; walking clean is the slow, free one.
        public float severityPerDayClean = -0.6f;

        public HediffCompProperties_CarriedFilthExposure()
        {
            compClass = typeof(RM_HediffComp_CarriedFilthExposure);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (filthDef == null)
            {
                yield return "HediffCompProperties_CarriedFilthExposure has no filthDef — this hediff can never tell whether its carrier is still tarred, so it will only ever heal (severityPerDayClean).";
            }
        }
    }

    // Base class HediffComp_SeverityModifierBase (Verse/
    // HediffComp_SeverityModifierBase.cs, confirmed against the live 1.6
    // decompile — same class RUT_MiasmaExposure's own comp already cribs
    // in this assembly) already provides the per-200-ticks hashed interval
    // and the /day-to-/tick conversion; this only supplies what changes.
    public class RM_HediffComp_CarriedFilthExposure : HediffComp_SeverityModifierBase
    {
        public HediffCompProperties_CarriedFilthExposure Props => (HediffCompProperties_CarriedFilthExposure)props;

        public override float SeverityChangePerDay()
        {
            HediffCompProperties_CarriedFilthExposure props = Props;
            Pawn pawn = base.Pawn;
            if (props == null || props.filthDef == null || pawn?.filth == null)
            {
                return 0f;
            }

            if (!RM_EnvironmentalHazardsSettings.tarredHediffEnabled)
            {
                return 0f; // mod option: the tarred hediff freezes exactly where it is
            }

            return IsCarryingTar(pawn) ? props.severityPerDayCarrying : props.severityPerDayClean;
        }

        private bool IsCarryingTar(Pawn pawn)
        {
            var carried = pawn.filth.CarriedFilthListForReading;
            for (int i = 0; i < carried.Count; i++)
            {
                if (carried[i]?.def == Props.filthDef)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
