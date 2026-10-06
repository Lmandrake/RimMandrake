using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §3.2: an unpowered mirror is aimed by a colonist. The aim gizmo
    // sets a pending target; a Construction worker walks over and turns it (Props.reAimTicks x the
    // settings dial), and the job commits the new normal.
    public class RM_WorkGiver_ReAimMirror : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            if (comp == null)
            {
                yield break;
            }
            foreach (Building b in pawn.Map.listerBuildings.allBuildingsColonist)
            {
                RM_CompMirror m = b.TryGetComp<RM_CompMirror>();
                if (m != null && m.HasPending)
                {
                    yield return b;
                }
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            return comp == null || comp.MirrorCount == 0;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompMirror m = t.TryGetComp<RM_CompMirror>();
            if (m == null || !m.HasPending || t.IsForbidden(pawn) || t.IsBurning())
            {
                return false;
            }
            return pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return HasJobOnThing(pawn, t, forced) ? JobMaker.MakeJob(RM_SolarMirrorsDefOf.RM_ReAimMirror, t) : null;
        }
    }

    public class RM_JobDriver_ReAimMirror : JobDriver
    {
        private Thing Mirror => job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Mirror.TryGetComp<RM_CompMirror>()?.HasPending != true);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            RM_CompMirror m = Mirror.TryGetComp<RM_CompMirror>();
            int ticks = m == null ? 600 : UnityEngine.Mathf.Max(1,
                UnityEngine.Mathf.RoundToInt(m.Props.reAimTicks * RM_SolarMirrorsSettings.reAimWorkMultiplier));
            yield return Toils_General.Wait(ticks, TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil commit = ToilMaker.MakeToil("RM_CommitAim");
            commit.initAction = () =>
            {
                RM_CompMirror mm = Mirror.TryGetComp<RM_CompMirror>();
                if (mm != null && mm.HasPending)
                {
                    mm.CommitAim(mm.PendingTarget);
                }
            };
            commit.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return commit;
        }
    }
}
