using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCARLANDS_MECHANICS_1 §2 (the Scarlands mark — "never fully fades").
    // Owner ruling 4 (scarlands_kit_spec.md): a marked pawn is marked for
    // life. Vanilla severity math (HediffWithComps.Tick ->
    // Hediff.Severity setter, confirmed against the live 1.6 decompile) has
    // no floor concept of its own — SeverityPerDay drives severity straight
    // to 0 and beyond. This comp is the one line of new C# the spec's own
    // §2 calls for: once severity has ever crossed floorTriggerThreshold,
    // clamp it so it can decay toward floorValue but never below.
    //
    //   <HediffDef>
    //     <defName>RUT_ScarlandsMark</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_SeverityFloor">
    //         <floorTriggerThreshold>0.5</floorTriggerThreshold>
    //         <floorValue>0.25</floorValue>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_SeverityFloor : HediffCompProperties
    {
        // Severity must reach at least this once, on this pawn, before the
        // floor arms. Below this the hediff can still fade to zero and be
        // removed entirely — a light brush with the Scarlands doesn't mark
        // a pawn for life, only a real stay does.
        public float floorTriggerThreshold = 0.5f;

        // Once armed, severity never drops below this again for the rest of
        // the pawn's life (persisted on the hediff, survives leaving the
        // map and the save/load round-trip via PostExposeData below).
        public float floorValue = 0.25f;

        public HediffCompProperties_SeverityFloor()
        {
            compClass = typeof(RM_HediffComp_SeverityFloor);
        }

        public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (floorValue > floorTriggerThreshold)
            {
                yield return "HediffCompProperties_SeverityFloor floorValue (" + floorValue
                    + ") is above floorTriggerThreshold (" + floorTriggerThreshold
                    + ") — the floor would arm and then immediately push severity UP, never down.";
            }
        }
    }

    public class RM_HediffComp_SeverityFloor : HediffComp
    {
        private bool armed;

        private HediffCompProperties_SeverityFloor Props => (HediffCompProperties_SeverityFloor)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);

            HediffCompProperties_SeverityFloor props = Props;
            if (props == null)
            {
                return;
            }

            if (!armed)
            {
                if (parent.Severity >= props.floorTriggerThreshold)
                {
                    armed = true;
                }
                return;
            }

            if (parent.Severity < props.floorValue)
            {
                // Adjust rather than assign parent.Severity directly: this
                // runs mid-tick, ahead of Hediff.Tick's own clamp/removal
                // check, so nudging the pending adjustment is the correct
                // seam (same pattern HediffComp_SeverityModifierBase's
                // callers use) rather than fighting the setter twice.
                severityAdjustment += props.floorValue - parent.Severity;
            }
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref armed, "severityFloorArmed", false);
        }
    }
}
