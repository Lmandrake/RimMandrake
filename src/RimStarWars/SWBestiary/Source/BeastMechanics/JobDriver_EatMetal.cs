using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // PORTED_BEAST_MECHANICS_REBUILD_1 — see CompMetalEater.cs for the header.
    //
    // Ordinary ingestion toils will not run on a steel slab: vanilla's
    // JobDriver_Ingest goes through the thing's CompIngredient/ingestible
    // properties, and steel has none. So, like the donor, this is a bespoke
    // chew: walk to it, chew for 500 ticks, then apply the comp's own nutrition
    // and eat into the stack.
    public class JobDriver_EatMetal : JobDriver, IEatingDriver
    {
        private const TargetIndex FoodInd = TargetIndex.A;
        private const int ChewTicks = 500;

        private Toil chewing;

        private Thing FoodSource => job.GetTarget(FoodInd).Thing;

        public bool GainingNutritionNow => !FoodSource.DestroyedOrNull() && CurToil == chewing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (pawn.Faction == null)
            {
                return true;
            }
            return pawn.Reserve(FoodSource, job, 10, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            CompMetalEater comp = pawn.TryGetComp<CompMetalEater>();
            if (comp == null)
            {
                yield break;
            }

            this.FailOn(() => FoodSource.DestroyedOrNull());

            yield return Toils_Goto.GotoThing(FoodInd, PathEndMode.Touch);

            chewing = MakeChewToil();
            yield return chewing;

            yield return MakeFinalizeToil(comp);
        }

        private Toil MakeChewToil()
        {
            Toil toil = ToilMaker.MakeToil("RSW_EatMetal_Chew");
            toil.initAction = delegate
            {
                Pawn actor = toil.actor;
                actor.jobs.curDriver.ticksLeftThisToil = ChewTicks;
                Thing thing = actor.CurJob.GetTarget(FoodInd).Thing;
                if (thing != null && thing.Spawned)
                {
                    thing.Map.physicalInteractionReservationManager.Reserve(actor, actor.CurJob, thing);
                }
            };
            toil.tickIntervalAction = delegate
            {
                Thing thing = toil.actor.CurJob.GetTarget(FoodInd).Thing;
                if (thing != null && thing.Spawned)
                {
                    toil.actor.rotationTracker.FaceCell(thing.Position);
                }
            };
            toil.WithProgressBar(FoodInd, () => 1f - toil.actor.jobs.curDriver.ticksLeftThisToil / (float)ChewTicks);
            toil.defaultCompleteMode = ToilCompleteMode.Delay;
            toil.handlingFacing = true;
            toil.FailOnDestroyedOrNull(FoodInd);
            toil.AddFinishAction(delegate
            {
                Pawn actor = toil.actor;
                Thing thing = actor.CurJob?.GetTarget(FoodInd).Thing;
                if (thing != null && actor.Map != null
                    && actor.Map.physicalInteractionReservationManager.IsReservedBy(actor, thing))
                {
                    actor.Map.physicalInteractionReservationManager.Release(actor, actor.CurJob, thing);
                }
            });
            return toil;
        }

        private Toil MakeFinalizeToil(CompMetalEater comp)
        {
            Toil toil = ToilMaker.MakeToil("RSW_EatMetal_Finalize");
            toil.initAction = delegate
            {
                Pawn actor = toil.actor;
                Thing thing = actor.CurJob.GetTarget(FoodInd).Thing;
                if (thing == null || thing.Destroyed)
                {
                    return;
                }

                if (comp.Props.fullyDestroyThing)
                {
                    thing.Destroy();
                }
                else if (thing.def.useHitPoints && !comp.Props.ignoreUseHitPoints)
                {
                    thing.HitPoints -= Mathf.RoundToInt(thing.MaxHitPoints * comp.Props.percentageOfDestruction);
                    if (thing.HitPoints <= 0)
                    {
                        thing.Destroy();
                    }
                }
                else
                {
                    // Eat a fixed fraction of a FULL stack, not of what is
                    // there — a lone steel bar still feeds the animal once and
                    // then vanishes rather than being nibbled forever. Donor
                    // behaviour, kept: the remainder below 10 is destroyed.
                    int bite = Mathf.Max(1, Mathf.RoundToInt(comp.Props.percentageOfDestruction * thing.def.stackLimit));
                    thing.stackCount -= bite;
                    if (thing.stackCount < 10)
                    {
                        thing.Destroy();
                    }
                }

                if (!actor.Dead && actor.needs?.food != null)
                {
                    actor.needs.food.CurLevel += comp.Props.nutrition;
                }
                actor.records.AddTo(RecordDefOf.NutritionEaten, comp.Props.nutrition);
            };
            toil.defaultCompleteMode = ToilCompleteMode.Instant;
            return toil;
        }
    }
}
