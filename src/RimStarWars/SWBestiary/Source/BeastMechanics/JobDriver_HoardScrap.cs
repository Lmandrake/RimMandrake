using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // SHRUBLAND_SCRAPNEST_BIRDS_1 — see CompScrapHoarder.cs for the header.
    //
    // Deliberately thin: every step but the last is a stock vanilla haul toil,
    // because a bird carrying an item is exactly what Toils_Haul already does
    // and re-implementing a carry is how carry bugs get written. Unlike
    // JobDriver_EatMetal — which HAD to be bespoke, since steel has no
    // ingestible properties for JobDriver_Ingest to read — nothing here needed
    // inventing.
    //
    //   A = the piece of scrap        B = the nest
    //
    // The one custom toil is the drop. Vanilla's Toils_Haul.PlaceHauledThingInCell
    // drops with ThingPlaceMode.Direct and, on a cell that cannot take the
    // stack, jumps back to the carry toil — which on a one-cell nest that is
    // already holding a different item is an infinite walk. ThingPlaceMode.Near
    // spills onto the next free cell instead, which is also what a real nest
    // looks like once it is full.
    public class JobDriver_HoardScrap : JobDriver
    {
        private const TargetIndex ScrapInd = TargetIndex.A;
        private const TargetIndex NestInd = TargetIndex.B;

        private Thing Scrap => job.GetTarget(ScrapInd).Thing;
        private Thing Nest => job.GetTarget(NestInd).Thing;

        // SCRAPNEST_BIRD_BASE_THEFT_1: whether the scrap was taken from the
        // player's home area or storage, read before it is lifted (once it is
        // carried it has no cell). Saved, so a load mid-carry still alerts.
        private bool fromBase;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref fromBase, "rswFromBase", false);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Wild animals have no faction and so reserve nothing — the same
            // early-out JobDriver_EatMetal takes.
            if (pawn.Faction == null)
            {
                return true;
            }
            return pawn.Reserve(Scrap, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(ScrapInd);
            this.FailOnDestroyedOrNull(NestInd);

            yield return Toils_Goto.GotoThing(ScrapInd, PathEndMode.ClosestTouch)
                .FailOnSomeonePhysicallyInteracting(ScrapInd);

            Toil note = ToilMaker.MakeToil("RSW_HoardScrap_NoteOrigin");
            note.initAction = delegate
            {
                Thing t = Scrap;
                Map map = note.actor.Map;
                fromBase = t != null && t.Spawned && map != null
                    && (map.areaManager.Home[t.Position] || t.IsInAnyStorage() || t.Position.GetEdifice(map) is Building_Storage);
            };
            note.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return note;

            yield return Toils_Haul.StartCarryThing(ScrapInd, putRemainderInQueue: false,
                subtractNumTakenFromJobCount: false, failIfStackCountLessThanJobCount: false,
                reserve: false);

            // The owner's 2026-09-21 requirement: the player is ALERTED when a
            // theft occurs, never left to discover the loss later.
            Toil alert = ToilMaker.MakeToil("RSW_HoardScrap_TheftAlert");
            alert.initAction = delegate
            {
                Thing carried = alert.actor.carryTracker?.CarriedThing;
                if (fromBase && carried != null)
                {
                    RSW_ScrapThiefFlock.NotifyTheft(alert.actor, carried);
                }
            };
            alert.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return alert;

            yield return Toils_Haul.CarryHauledThingToCell(NestInd, PathEndMode.Touch);

            yield return MakeDepositToil();
        }

        private Toil MakeDepositToil()
        {
            Toil toil = ToilMaker.MakeToil("RSW_HoardScrap_Deposit");
            toil.initAction = delegate
            {
                Pawn actor = toil.actor;
                Thing carried = actor.carryTracker?.CarriedThing;
                if (carried == null)
                {
                    return;
                }
                Thing nest = actor.CurJob?.GetTarget(NestInd).Thing;
                IntVec3 cell = (nest != null && nest.Spawned) ? nest.Position : actor.Position;

                if (!actor.carryTracker.TryDropCarriedThing(cell, ThingPlaceMode.Near, out Thing placed))
                {
                    actor.jobs.EndCurrentJob(JobCondition.Incompletable);
                    return;
                }

                // Forbidden on arrival, to match the nest's own
                // CompProperties_Spawner (spawnForbidden). A hoard is
                // something the player goes and TAKES; it is not free loot
                // ferried to the colony by a passing hauler.
                placed?.SetForbidden(true, false);
            };
            toil.defaultCompleteMode = ToilCompleteMode.Instant;
            return toil;
        }
    }
}
