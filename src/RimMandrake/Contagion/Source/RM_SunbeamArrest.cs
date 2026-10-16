using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 4 — the Sunbeam's medical use: the ruled ARREST (Q3, 2026-10-15: "Stops current
    // mutations. No protection if you get exposed again later."). A colonist carrying a Sunbeam as their weapon right-clicks
    // a Contagion-touched pawn who is not a threat and holds the lens on them: RM_ContagionTouched is removed (the
    // progression stops), every grown mutation stays, and the light leaves one shallow UV burn (scar-prone, like every
    // Sunbeam hit). Being shot by a Sunbeam arrests too (DamageWorker_RM_UV); this is the way to do it without a fight.
    // FloatMenuOptionProvider subclasses are found by reflection (FloatMenuMakerMap.Init), as with
    // FloatMenuOptionProvider_InjectGenomeSample: no Harmony.
    public class FloatMenuOptionProvider_SunbeamArrest : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        public static bool HoldsSunbeam(Pawn p)
        {
            return p?.equipment?.Primary != null && p.equipment.Primary.def == RM_ContagionTouchDefOf.RM_Sunbeam;
        }

        // A patient the lens may be held on: touched, alive, not the actor, and not an awake enemy.
        public static bool ValidPatient(Pawn actor, Pawn patient)
        {
            return patient != null && patient != actor && patient.Spawned && !patient.Dead
                && RM_ContagionTouchedUtility.IsTouched(patient)
                && (patient.Downed || !patient.HostileTo(actor));
        }

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_ContagionSettings.sunbeamArrestEnabled) return null;
            if (!(clickedThing is Pawn patient)) return null;
            Pawn actor = context.FirstSelectedPawn;
            if (!HoldsSunbeam(actor) || !ValidPatient(actor, patient)) return null;
            if (!actor.CanReach(patient, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption("Cannot arrest the Contagion: " + "NoPath".Translate().CapitalizeFirst(), null);
            }
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Arrest " + patient.LabelShort + "'s Contagion with the sunbeam",
                delegate
                {
                    Job job = JobMaker.MakeJob(RM_ContagionTouchDefOf.RM_SunbeamArrest, patient);
                    actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                }), actor, patient);
        }
    }

    public class JobDriver_RM_SunbeamArrest : JobDriver
    {
        private const int ArrestDurationTicks = 300;
        // The treatment's price: one shallow UV burn (RM_UVBeam's hediff scars readily).
        private const float TreatmentBurn = 3f;

        private Pawn Patient => (Pawn)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Patient, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_ContagionSettings.sunbeamArrestEnabled);
            this.FailOn(() => !FloatMenuOptionProvider_SunbeamArrest.HoldsSunbeam(pawn));
            this.FailOn(() => !FloatMenuOptionProvider_SunbeamArrest.ValidPatient(pawn, Patient));

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil hold = ToilMaker.MakeToil("SunbeamArrest");
            hold.initAction = delegate
            {
                // A patient on its feet is asked to stand still for the lens.
                Pawn pt = Patient;
                if (!pt.Downed && !pt.Drafted && pt.jobs != null && !pt.InMentalState && pt.Faction == pawn.Faction)
                {
                    Job wait = JobMaker.MakeJob(JobDefOf.Wait, pawn);
                    wait.expiryInterval = ArrestDurationTicks + 60;
                    pt.jobs.StartJob(wait, JobCondition.InterruptForced);
                }
            };
            hold.tickAction = delegate
            {
                pawn.rotationTracker.FaceTarget(Patient);
            };
            hold.FailOn(() => !pawn.Position.AdjacentTo8WayOrInside(Patient.Position));
            hold.defaultCompleteMode = ToilCompleteMode.Delay;
            hold.defaultDuration = ArrestDurationTicks;
            hold.WithProgressBarToilDelay(TargetIndex.A);
            yield return hold;

            // Reached only when the hold ran its full length (a failed or interrupted hold ends the job before this).
            yield return Toils_General.Do(delegate
            {
                Pawn pt = Patient;
                if (pt == null || pt.Dead) return;
                if (RM_ContagionTouchedUtility.Arrest(pt, "under " + pawn.LabelShort + "'s sunbeam"))
                {
                    pt.TakeDamage(new DamageInfo(RM_ContagionTouchDefOf.RM_UVBeam, TreatmentBurn, 0f, -1f, pawn));
                }
            });
        }
    }
}
