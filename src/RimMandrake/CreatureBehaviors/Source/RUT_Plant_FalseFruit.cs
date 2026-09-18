using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_GUARDIAN_GROVES_1 (rot_kit_spec.md M6, "the mimic-lure"). RUT_FalseFruit
    // (RotSporeKit) sets this as its thingClass. Lives here rather than in
    // RotSporeKit's own Defs/ (which ships no Source/ of its own): the
    // established precedent for Rot-specific glue classes referencing this
    // assembly's mechanics is RM_CompWoundLink/RM_HediffComp_KinMending
    // themselves (M7, content-blind but still creature-behavior-shaped) —
    // this class needs RM_CompPlantAlarm directly, so splitting it into a
    // third assembly just for one class would only add a project reference
    // for no reason.
    //
    // Seam verified this pass (RimSage, RimWorld/Plant.cs and
    // RimWorld/JobDriver_PlantWork.cs): Plant.PlantCollected(Pawn by,
    // PlantDestructionMode) is called by JobDriver_PlantWork.MakeNewToils
    // for BOTH the Harvest and Cut-Plant job drivers — so this fires whether
    // a colonist harvests the lure or simply cuts it down.
    //
    // Effects fire BEFORE base.PlantCollected(): a HarvestDestroys plant's
    // own PlantCollected calls Destroy() partway through, and by then
    // parent.Spawned is false and GetComp/TriggerAlarm would silently no-op.
    // Triggering first also reads truer to the flavor — the trap springs
    // the instant it's touched, not after it's already gone.
    public class RUT_Plant_FalseFruit : Plant
    {
        private static HediffDef matGripHediffCached;
        private static bool matGripLookupDone;

        private static HediffDef MatGripHediff
        {
            get
            {
                if (!matGripLookupDone)
                {
                    matGripLookupDone = true;
                    matGripHediffCached = DefDatabase<HediffDef>.GetNamedSilentFail("RUT_MatGrip");
                    if (matGripHediffCached == null)
                    {
                        Log.ErrorOnce(
                            "[RotSporeKit] RUT_Plant_FalseFruit could not find HediffDef RUT_MatGrip.",
                            0x52A6710);
                    }
                }
                return matGripHediffCached;
            }
        }

        public override void PlantCollected(Pawn by, PlantDestructionMode plantDestructionMode)
        {
            if (RM_CreatureBehaviorsSettings.guardianAlarmEnabled && by != null && !by.Dead && by.health != null)
            {
                HediffDef hediff = MatGripHediff;
                if (hediff != null)
                {
                    by.health.AddHediff(hediff);
                }

                GetComp<RM_CompPlantAlarm>()?.TriggerAlarm();
            }

            base.PlantCollected(by, plantDestructionMode);
        }
    }
}
