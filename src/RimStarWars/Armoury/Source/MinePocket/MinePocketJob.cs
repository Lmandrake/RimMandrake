using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace MinePocket;

public class MinePocketJob : JobDriver
{
    private int useDuration = 60;
    private bool trapSprang;

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref useDuration, "useDuration", 0);
        Scribe_Values.Look(ref trapSprang, "trapSprang", false);
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

        // Rolled ONCE, here, not re-checked every tick: AddFailCondition
        // registers a GLOBAL fail condition that JobDriver evaluates once per
        // tick for the whole job (confirmed against JobDriver.
        // CheckCurrentToilEndOrFail), so a delegate re-calling Rand.Chance
        // turned the intended single "did the defuser slip?" roll into
        // 1 - p^n over however many ticks the wait/prepare toils take.
        Toil rollSpring = ToilMaker.MakeToil("MakeNewToils");
        rollSpring.initAction = delegate
        {
            trapSprang = !Rand.Chance(pawn.GetStatValue(StatDefOf.PawnTrapSpringChance));
        };
        rollSpring.defaultCompleteMode = ToilCompleteMode.Instant;
        yield return rollSpring;

        yield return Toils_Goto.GotoThing(TargetIndex.A, TargetThingA.def.hasInteractionCell ? PathEndMode.InteractionCell : PathEndMode.Touch);
        yield return PrepareToUse();
        AddFailCondition(() => trapSprang);

        Toil predefuse = ToilMaker.MakeToil("MakeNewToils");
        predefuse.initAction = delegate
        {
            if (pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation) < 0.6f)
            {
                TargetThingA.TryGetComp<CompExplosive>()?.StartWick();
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
