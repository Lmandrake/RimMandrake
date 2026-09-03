using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace KoltoTank;

public class JobDriver_EnterKoltoTank : JobDriver
{
    public override bool TryMakePreToilReservations(bool errorOnFailed)
    {
        return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
    }

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOnDespawnedOrNull(TargetIndex.A);
        yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.InteractionCell);

        Toil prepare = Toils_General.Wait(500)
            .FailOnCannotTouch(TargetIndex.A, PathEndMode.InteractionCell)
            .WithProgressBarToilDelay(TargetIndex.A);
        yield return prepare;

        Toil enter = new Toil();
        enter.initAction = delegate
        {
            Pawn actor = enter.actor;
            Building_KoltoTank pod = (Building_KoltoTank)actor.CurJob.targetA.Thing;
            void Action()
            {
                actor.DeSpawn();
                // Building_KoltoTank.TryAcceptThing refuses (power off, out of
                // kolto, or another pawn beat this one in) AFTER the DeSpawn
                // above already removed the actor from the map - a discarded
                // false here leaves the pawn held by no ThingOwner and on no
                // map, permanently.
                if (!pod.TryAcceptThing(actor))
                {
                    GenSpawn.Spawn(actor, pod.Position, pod.Map);
                }
            }
            if (!pod.def.building.isPlayerEjectable)
            {
                int freeColonists = Map.mapPawns.FreeColonistsSpawnedOrInPlayerEjectablePodsCount;
                if (freeColonists <= 1)
                {
                    Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                        "CasketWarning".Translate(actor.Named("PAWN")).AdjustedFor(actor, "PAWN"),
                        Action));
                }
                else
                {
                    Action();
                }
            }
            else
            {
                Action();
            }
        };
        enter.defaultCompleteMode = ToilCompleteMode.Instant;
        yield return enter;
    }
}
