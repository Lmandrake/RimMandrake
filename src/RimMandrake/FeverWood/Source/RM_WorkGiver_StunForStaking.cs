using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TWO_FRONT_LURE_1, step 1 of 2: a pawn flagged
    /// RM_Designation_StakeLure that is not yet Downed gets wounded down
    /// first — "chained down and WOUNDED" (design sheet §5/§6l) needs both
    /// halves regardless of which of the three permitted sources the bait
    /// came from. Drives RM_JobDriver_StunVictim
    /// (mandrake.rm.environmentalhazards) completely unmodified. Shape
    /// cribbed from vanilla WorkGiver_Slaughter (read via RimSage this
    /// pass).</summary>
    public class RM_WorkGiver_StunForStaking : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.OnCell;

        public override System.Collections.Generic.IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_TwoFrontLureDefOf.RM_Designation_StakeLure))
            {
                yield return d.target.Thing;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_TwoFrontLureDefOf.RM_Designation_StakeLure);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!(t is Pawn victim) || victim.Dead || victim.Downed)
            {
                return false; // already down: RM_WorkGiver_HaulToStake takes it from here
            }
            if (pawn.Map.designationManager.DesignationOn(victim, RM_TwoFrontLureDefOf.RM_Designation_StakeLure) == null)
            {
                return false;
            }
            if (!pawn.CanReserve(victim, 1, -1, null, forced))
            {
                return false;
            }
            if (pawn.WorkTagIsDisabled(WorkTags.Violent))
            {
                return false;
            }
            return true;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_TwoFrontLureDefOf.RM_StunForStaking, t);
        }
    }
}
