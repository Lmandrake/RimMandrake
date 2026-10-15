using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_DEDICATED_GRAZER_1 — the burrow itself. Two toils: go to
    /// ground (apply the hediff), then hold until it is safe to come back up.
    ///
    /// RM_Burrowed's statOffsets are what let "the fire pass over" the pawn
    /// instead of killing it, applied only WHILE burrowed, on top of
    /// RM_Ashwallow's own (PROVISIONAL) heat stats. The dome pose is drawn by
    /// RM_BurrowHeatReaction's GraphicFor postfix while the hediff holds,
    /// from RM_BurrowOnFireExtension.domeTexPath when that art is installed.
    ///
    /// Two ways in: RM_JobGiver_BurrowOnFire (a free ground fire within the
    /// race's radius) and RM_BurrowHeatReaction (a heat-category hit,
    /// ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE), which also sets the heat hold.
    ///
    /// Ends on whichever comes first: it is safe to surface (RM_FireEcoKernel.
    /// BurrowMayEmerge: RM_JobGiver_BurrowOnFire.FireIsNear false — the
    /// identical query that started the job, answered the other way — and
    /// the last heat hit's hold run out) or the safety-cap tick count
    /// (RM_BurrowOnFireExtension.maxBurrowTicks). A timeout is recorded with
    /// RM_JobGiver_BurrowOnFire.NoteTimeout, which keeps the animal above
    /// ground for PyrelandsTuning.BurrowTimeoutCooldownTicks; without that the
    /// giver would re-issue the burrow at once. AddFinishAction removes the
    /// hediff on every exit path — safe emergence, timeout, the job being
    /// interrupted by damage or capture, or the pawn dying — so the hediff
    /// can never outlive the job that granted it.
    /// </summary>
    public class RM_JobDriver_Burrow : JobDriver
    {
        // The safety cap reads JobDriver's own startTick: set by Notify_Starting and Scribed by base.ExposeData
        // (decompiled 1.6, Verse/AI/JobDriver.cs), so it survives save/load. A field of the same name here once hid it
        // (CS0108); FireEcologyHook.csproj now makes member hiding a build error.

        // Tick until which a heat hit keeps the dome shut with no fire near; -1 = never hit. Saved: a reload mid-attack
        // must not surface the animal into the flamethrower.
        private int heatHoldUntil = -1;

        internal int HeatHoldUntil => heatHoldUntil;

        /// <summary>RM_BurrowHeatReaction: a heat hit (re)starts the hold; a shorter hold never cuts a longer one.</summary>
        internal void NoteHeatHit(int now, int holdTicks)
        {
            heatHoldUntil = RM_FireEcoKernel.BurrowHeatHoldUntil(now, heatHoldUntil, holdTicks);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref heatHoldUntil, "rmHeatHoldUntil", -1);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Nothing reserved: burrowing is self-directed animal behaviour,
            // not a claim on a resource or a cell anyone else wants.
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => pawn.Dead);

            yield return Toils_General.Do(() => ApplyBurrowedHediff(pawn));

            RM_BurrowOnFireExtension ext = pawn.def.GetModExtension<RM_BurrowOnFireExtension>();
            int maxTicks = ext?.maxBurrowTicks ?? PyrelandsTuning.BurrowMaxTicks;
            float radius = ext?.detectionRadius ?? PyrelandsTuning.BurrowDetectionRadius;

            Toil hide = ToilMaker.MakeToil("RM_BurrowWait");
            hide.defaultCompleteMode = ToilCompleteMode.Never;
            hide.tickAction = () =>
            {
                Map map = pawn.Map;
                bool timedOut = startTick >= 0
                    && Find.TickManager.TicksGame - startTick >= maxTicks;
                bool safeToEmerge = map == null
                    || RM_FireEcoKernel.BurrowMayEmerge(Find.TickManager.TicksGame, heatHoldUntil,
                        RM_JobGiver_BurrowOnFire.FireIsNear(pawn, map, radius));
                if (timedOut || safeToEmerge)
                {
                    if (!safeToEmerge)
                    {
                        RM_JobGiver_BurrowOnFire.NoteTimeout(pawn);
                    }
                    ReadyForNextToil();
                }
            };
            hide.AddFinishAction(() => RemoveBurrowedHediff(pawn));
            yield return hide;
        }

        private static void ApplyBurrowedHediff(Pawn pawn)
        {
            if (pawn?.health?.hediffSet == null
                || pawn.health.hediffSet.HasHediff(PyrelandsMechanicsDefOf.RM_Burrowed))
            {
                return;
            }
            Hediff hediff = HediffMaker.MakeHediff(PyrelandsMechanicsDefOf.RM_Burrowed, pawn);
            pawn.health.AddHediff(hediff);
        }

        private static void RemoveBurrowedHediff(Pawn pawn)
        {
            if (pawn?.health?.hediffSet == null)
            {
                return;
            }
            Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(PyrelandsMechanicsDefOf.RM_Burrowed);
            if (hediff != null)
            {
                pawn.health.RemoveHediff(hediff);
            }
        }
    }
}
