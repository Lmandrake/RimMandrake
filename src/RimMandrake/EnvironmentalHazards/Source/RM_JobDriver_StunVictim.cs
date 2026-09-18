using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F9. The spec's "unclamp stun": "the ant job
    // downs the thornbug non-lethally first (an unclamp stun, INVENTED)
    // then rides a kidnap-shaped RUT_HaulPawnAndExit job" (the_fever_wood
    // kit spec, F9) - RUT_HaulPawnAndExit.cs's own header names this as a
    // "separate ant attack-job... not built here". This is that job,
    // written generic (RM_-tier: no thornbug/ant-specific data) so any
    // pawn can non-lethally down any other pawn found via
    // RM_HaulVictimAIUtility.TryFindGoodHaulVictim (WIRED the prior pass)
    // before a haul job like RUT_HaulPawnAndExit can legally target it
    // (that driver's FailOn requires Takee.Downed).
    //
    // Toil shape cribbed from RM_JobDriver_GnawTreeBase (same assembly,
    // GREENTIDE_MECHANICS_2 M6): goto touch, wind-up timer with a progress
    // bar, then the payoff. HealthUtility.DamageUntilDowned (Verse/
    // HealthUtility.cs:246, non-lethal, confirmed real - the same call
    // RUT_MapComponent_TheTenant.Strike already uses for card 2's rescue
    // window) is the payoff instead of a tree fall.
    //
    // NOT done here: nothing calls this yet - the ants' LordJob/LordToil
    // (crib RimWorld/LordToil_KidnapCover.cs's shape) is what would hand a
    // raider this job against a victim RM_HaulVictimAIUtility finds, and
    // that wiring is blocked on the roster pass (no Ant/Feralisk
    // PawnKindDef exists to build a FactionDef's pawnGroupMakers against).
    public class RM_JobDriver_StunVictim : JobDriver
    {
        // INVENTED: no number is given in the spec for the unclamp-stun's
        // own wind-up; ~2 seconds (120 ticks) reads as a quick grab-and-
        // strike rather than a sustained melee exchange, distinct from
        // ordinary combat.
        private const int StunWindupTicks = 120;

        private int ticksRemaining = -1;

        private Pawn Victim => (Pawn)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Victim == null || Victim.Dead);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil stun = ToilMaker.MakeToil("MakeNewToils");
            stun.initAction = delegate
            {
                ticksRemaining = StunWindupTicks;
                // Already down (a second attacker reached it first, or it
                // was already resolved) - nothing left for this toil to do.
                if (Victim.Downed)
                {
                    ReadyForNextToil();
                }
            };
            stun.tickIntervalAction = delegate (int delta)
            {
                if (Victim == null || Victim.Dead || Victim.Downed)
                {
                    ReadyForNextToil();
                    return;
                }
                ticksRemaining -= delta;
                if (ticksRemaining > 0)
                {
                    return;
                }
                HealthUtility.DamageUntilDowned(Victim, allowBleedingWounds: false);
                ReadyForNextToil();
            };
            stun.defaultCompleteMode = ToilCompleteMode.Never;
            stun.WithProgressBar(TargetIndex.A, () => 1f - (float)ticksRemaining / StunWindupTicks);
            stun.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return stun;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksRemaining, "ticksRemaining", -1);
        }
    }
}
