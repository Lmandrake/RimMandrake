using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// GREENTIDE_MECHANICS_2 M7 build. The lunge's "opener" only — closes
    /// distance on the target (RM_CompAquaticAmbusher already applied the
    /// short move-speed hediff, if the kind's XML sets one, before starting
    /// this job) and delivers ONE manual first-strike hit at
    /// baseLungeDamageRange * firstStrikeDamageMultiplier, then ends. The
    /// job never loops into ongoing combat — per the spec's own "hunting AI
    /// stays vanilla predator ThinkTree", the pawn's own ThinkTree picks up
    /// normal Hunt/AttackMelee behavior on its next think cycle once the
    /// target is visible and hostile.
    /// </summary>
    public class RM_JobDriver_LungeAttack : JobDriver
    {
        private CompProperties_AquaticAmbusher Props =>
            pawn.TryGetComp<RM_CompAquaticAmbusher>()?.Props;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true; // a wild ambush strike reserves nothing — same posture RM_JobDriver_Gnaw's building-target branch takes when there's nothing to haul
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !(job.targetA.Thing is Pawn target) || target.Dead || target.Destroyed);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil strike = ToilMaker.MakeToil("MakeNewToils");
            strike.initAction = delegate
            {
                if (!RM_CreatureBehaviorsSettings.aquaticAmbushEnabled)
                {
                    return; // mod option: disabled mid-lunge — the opener simply doesn't land, ThinkTree takes over next tick
                }

                if (!(job.targetA.Thing is Pawn target) || target.Dead || target.Destroyed)
                {
                    return;
                }

                CompProperties_AquaticAmbusher props = Props;
                if (props == null)
                {
                    return;
                }

                float amount = props.baseLungeDamageRange.RandomInRange * props.firstStrikeDamageMultiplier;
                Vector3Direction(pawn, target, out float angle);
                target.TakeDamage(new DamageInfo(DamageDefOf.Bite, amount, 0f, angle, pawn));
            };
            strike.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return strike;
        }

        private static void Vector3Direction(Pawn from, Pawn to, out float angle)
        {
            angle = (to.Position - from.Position).ToVector3().AngleFlat();
        }
    }
}
