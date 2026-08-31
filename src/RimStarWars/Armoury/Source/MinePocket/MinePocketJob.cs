using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace MinePocket;

public class MinePocketJob : JobDriver
{
    private int useDuration = 60;

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref useDuration, "useDuration", 0);
    }

    public override bool TryMakePreToilReservations(bool errorOnFailed)
    {
        return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
    }

    protected Toil PrepareToUse()
    {
        Toil toil = Toils_General.Wait(useDuration, TargetIndex.A)
            .WithProgressBarToilDelay(TargetIndex.A)
            .FailOnDespawnedNullOrForbidden(TargetIndex.A)
            .FailOnCannotTouch(TargetIndex.A, TargetThingA.def.hasInteractionCell ? PathEndMode.InteractionCell : PathEndMode.Touch);
        toil.handlingFacing = true;
        return toil;
    }

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOnIncapable(PawnCapacityDefOf.Manipulation);
        yield return Toils_Goto.GotoThing(TargetIndex.A, TargetThingA.def.hasInteractionCell ? PathEndMode.InteractionCell : PathEndMode.Touch);
        yield return PrepareToUse();
        AddFailCondition(() => !Rand.Chance(pawn.GetStatValue(StatDefOf.PawnTrapSpringChance)));

        Toil predefuse = ToilMaker.MakeToil("MakeNewToils");
        predefuse.initAction = delegate
        {
            if (pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation) < 0.6f)
            {
                TargetThingA.TryGetComp<CompExplosive>().StartWick();
            }
        };
        predefuse.defaultCompleteMode = ToilCompleteMode.Instant;
        yield return predefuse;

        Toil lastToil = ToilMaker.MakeToil("MakeNewToils");
        lastToil.initAction = delegate
        {
            if (pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation) < 0.6f)
            {
                return;
            }
            Thing target = TargetThingA;
            if (target.def.HasModExtension<MinePocketDefExtension>())
            {
                MinePocketDefExtension ext = target.def.GetModExtension<MinePocketDefExtension>();
                Thing spawned = ThingMaker.MakeThing(ext.defToSpawnAfterDefuse);
                spawned.stackCount = ext.countToSpawn;
                GenSpawn.Spawn(spawned, TargetLocA, Map);
            }
        };
        lastToil.defaultCompleteMode = ToilCompleteMode.Instant;
        lastToil.AddFinishAction(delegate
        {
            if (pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation) >= 0.6f)
            {
                TargetThingA.Destroy();
            }
        });
        yield return lastToil;
    }
}
