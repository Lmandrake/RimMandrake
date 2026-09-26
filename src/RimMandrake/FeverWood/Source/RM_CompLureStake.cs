using RimWorld;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TWO_FRONT_LURE_1. The lure stake's own comp: tracks whether
    // a live staked pawn is currently tied here and tells
    // RM_MapComponent_TwoFrontLure when that becomes true or false again,
    // so the map component's own raid-chance roll knows whether any bait
    // is actually out there. Owns applying/removing RM_LureStaked (the
    // "chained down" hediff) — the "wounded" half of the owner's ruling is
    // already enforced upstream, by RM_WorkGiver_HaulToStake/
    // RM_JobDriver_HaulToStake requiring the target be Downed before it can
    // be carried here at all (RM_WorkGiver_StunForStaking, reusing
    // RM_JobDriver_StunVictim verbatim, is what gets an undowned tamed
    // animal or prisoner to that state in the first place).
    public class RM_CompLureStake : ThingComp
    {
        private const int CheckIntervalTicks = 250;
        private const string StakedHediffDefName = "RM_LureStaked";

        private Pawn stakedPawn;
        private bool wasLiveLastTick;

        /// <summary>FEVERWOOD_TWO_FRONT_LURE_TUNING_1 point 5: true once
        /// this stake's bait has actually drawn a raid wave. Only matters
        /// when RM_FeverWoodSettings.twoFrontLureLockOnceTriggered is on
        /// (default off — see that field); resets whenever new bait is
        /// staked here.</summary>
        private bool raidTriggered;

        public RM_CompProperties_LureStake Props => (RM_CompProperties_LureStake)props;

        public bool HasLiveBait => stakedPawn != null && stakedPawn.Spawned && !stakedPawn.Dead;

        public Pawn StakedPawn => stakedPawn;

        /// <summary>Called by RM_JobDriver_HaulToStake once the bait has been
        /// carried and placed at the stake. Applies the "chained down"
        /// hediff and registers with the map's raid orchestrator.</summary>
        public void TryStake(Pawn bait)
        {
            if (bait == null || parent.Map == null)
            {
                return;
            }
            stakedPawn = bait;
            raidTriggered = false;
            HediffDef stakedDef = DefDatabase<HediffDef>.GetNamedSilentFail(StakedHediffDefName);
            if (stakedDef != null && !bait.health.hediffSet.HasHediff(stakedDef))
            {
                bait.health.AddHediff(stakedDef);
            }
            wasLiveLastTick = true;
            // The "stake as lure" designation's job is done now that the bait
            // is actually staked — clear it. Left in place, it would fire
            // RM_WorkGiver_StunForStaking/RM_WorkGiver_HaulToStake again on
            // this same pawn the next time it goes Downed for any unrelated
            // reason (a fight, an illness), including after ReleaseBait has
            // already freed it — ReleaseBait removes the hediff, not this
            // designation, so nothing else ever clears it.
            Designation stakeDesignation = parent.Map.designationManager.DesignationOn(bait, RM_TwoFrontLureDefOf.RM_Designation_StakeLure);
            if (stakeDesignation != null)
            {
                parent.Map.designationManager.RemoveDesignation(stakeDesignation);
            }
            parent.Map.GetComponent<RM_MapComponent_TwoFrontLure>()?.Notify_LureStaked(this);
        }

        /// <summary>Frees the current bait (colonist choice, or building
        /// destruction) — removes the hediff so a rescued/orphaned pawn
        /// isn't left permanently immobile.</summary>
        public void ReleaseBait()
        {
            if (stakedPawn != null && !stakedPawn.Dead)
            {
                HediffDef stakedDef = DefDatabase<HediffDef>.GetNamedSilentFail(StakedHediffDefName);
                Hediff existing = stakedDef != null ? stakedPawn.health.hediffSet.GetFirstHediffOfDef(stakedDef) : null;
                if (existing != null)
                {
                    stakedPawn.health.RemoveHediff(existing);
                }
            }
            stakedPawn = null;
            wasLiveLastTick = false;
            raidTriggered = false;
            parent.Map?.GetComponent<RM_MapComponent_TwoFrontLure>()?.Notify_LureCleared(this);
        }

        /// <summary>Called by RM_MapComponent_TwoFrontLure once a raid wave
        /// has actually been spawned using this stake as its origin.</summary>
        public void Notify_RaidTriggered()
        {
            raidTriggered = true;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            wasLiveLastTick = HasLiveBait;
            if (respawningAfterLoad && HasLiveBait)
            {
                // The map component's own registry is runtime-only (never
                // Scribed) — every stake re-announces itself on load so the
                // registry is rebuilt from real map state, not a second,
                // driftable copy of it.
                parent.Map.GetComponent<RM_MapComponent_TwoFrontLure>()?.Notify_LureStaked(this);
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || parent.Map == null)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            bool nowLive = HasLiveBait;
            if (wasLiveLastTick && !nowLive)
            {
                // The bait died (or despawned) without going through
                // ReleaseBait — tell the map component so it stops treating
                // this stake as active bait.
                parent.Map.GetComponent<RM_MapComponent_TwoFrontLure>()?.Notify_LureCleared(this);
            }
            wasLiveLastTick = nowLive;
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (stakedPawn != null && !stakedPawn.Dead)
            {
                HediffDef stakedDef = DefDatabase<HediffDef>.GetNamedSilentFail(StakedHediffDefName);
                Hediff existing = stakedDef != null ? stakedPawn.health.hediffSet.GetFirstHediffOfDef(stakedDef) : null;
                if (existing != null)
                {
                    stakedPawn.health.RemoveHediff(existing);
                }
            }
            previousMap?.GetComponent<RM_MapComponent_TwoFrontLure>()?.Notify_LureCleared(this);
        }

        public override string CompInspectStringExtra()
        {
            return HasLiveBait
                ? $"Baited with {stakedPawn.LabelShort} — raiders may be drawn to it."
                : "No bait staked.";
        }

        public override System.Collections.Generic.IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (HasLiveBait)
            {
                Command_Action releaseCommand = new Command_Action
                {
                    defaultLabel = "Release lure",
                    defaultDesc = $"Frees {stakedPawn.LabelShort} from the stake. It keeps whatever wounds it already has.",
                    icon = TexCommand.ClearPrioritizedWork,
                    action = ReleaseBait,
                };
                if (RM_FeverWoodSettings.twoFrontLureLockOnceTriggered && raidTriggered)
                {
                    releaseCommand.Disable("This stake has already drawn a raid — the wager is locked in until the bait is freed by other means.");
                }
                yield return releaseCommand;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref stakedPawn, "stakedPawn");
            Scribe_Values.Look(ref raidTriggered, "raidTriggered", false);
        }
    }
}
