using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// DEEP_TRIBES_FIRE_RITE_1 — the rite itself, as a state graph.
    ///
    /// THREE TOILS, and only the middle one is ours:
    ///
    ///   1. TRAVEL — vanilla's LordJob_Travel subgraph, attached whole. It already
    ///      holds a humanlike group together on a long walk, drops them into
    ///      LordToil_DefendPoint if anything shoots at them, and picks the walk up
    ///      again 1200 ticks after the shooting stops. None of that is worth
    ///      rewriting and the sheet does not ask for pathing heroics.
    ///   2. RITE AND HARVEST — LordToil_RUT_RiteHarvest, below. Lights the fire
    ///      clock's line where the party is standing, attributed to the lead
    ///      harvester, and then puts everyone on the RUT_RiteHarvest duty.
    ///   3. EXIT — vanilla's LordToil_ExitMap. They leave with what is in their
    ///      inventories, which is the harvest.
    ///
    /// ⚠️ THE TRAVEL LEG HAS A TIMEOUT AS WELL AS AN ARRIVAL. A party that cannot
    /// reach the origin — a wall, a chasm, a colony in the way — must not leave
    /// the fire clock silently skipped, because the clock has already re-armed.
    /// So the rite fires on "arrived" OR on FireRiteTravelTimeoutTicks, whichever
    /// comes first, and lights where they actually got to.
    ///
    /// 🔑 BECOMING AN ENEMY ENDS THE RITE, IT DOES NOT START A BATTLE. If the
    /// player turns on them mid-rite they walk off the map. Arson-justice
    /// (IncidentWorker_FireRaid) is the mechanism that brings the Tribes back
    /// angry; this one is not a raid wearing a hat.
    /// </summary>
    public class LordJob_RUT_FireRite : LordJob
    {
        private IntVec3 riteOrigin;
        private int harvestTicks;

        /// <summary>Saved so a reloaded game cannot light a second front for the
        /// same rite. LordToil.Init runs on toil entry, and a load re-enters the
        /// current toil.</summary>
        private bool ignited;

        public LordJob_RUT_FireRite()
        {
        }

        public LordJob_RUT_FireRite(IntVec3 riteOrigin, int harvestTicks)
        {
            this.riteOrigin = riteOrigin;
            this.harvestTicks = harvestTicks;
        }

        internal bool AlreadyIgnited => ignited;

        internal void MarkIgnited() => ignited = true;

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();

            LordToil travel = graph.StartingToil =
                graph.AttachSubgraph(new LordJob_Travel(riteOrigin).CreateGraph()).StartingToil;

            LordToil_RUT_RiteHarvest rite = new LordToil_RUT_RiteHarvest(this, riteOrigin);
            graph.AddToil(rite);

            LordToil_ExitMap exit = new LordToil_ExitMap(LocomotionUrgency.Walk, canDig: true);
            graph.AddToil(exit);

            Transition arrived = new Transition(travel, rite);
            arrived.AddTrigger(new Trigger_Memo("TravelArrived"));
            arrived.AddTrigger(new Trigger_TicksPassed(PyrelandsTuning.FireRiteTravelTimeoutTicks));
            arrived.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(arrived);

            Transition finished = new Transition(rite, exit);
            finished.AddTrigger(new Trigger_TicksPassed(harvestTicks));
            finished.AddPreAction(new TransitionAction_EnsureHaveExitDestination());
            finished.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(finished);

            Transition turnedOn = new Transition(travel, exit);
            turnedOn.AddSources(rite);
            turnedOn.AddTrigger(new Trigger_BecamePlayerEnemy());
            turnedOn.AddPreAction(new TransitionAction_EnsureHaveExitDestination());
            turnedOn.AddPostAction(new TransitionAction_WakeAll());
            turnedOn.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(turnedOn);

            return graph;
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref riteOrigin, "riteOrigin");
            Scribe_Values.Look(ref harvestTicks, "harvestTicks", 0);
            Scribe_Values.Look(ref ignited, "ignited", defaultValue: false);
        }
    }

    /// <summary>
    /// The rite proper: light it, then work it.
    ///
    /// 🔴 THE FIRE IS ATTRIBUTED TO THE LEAD HARVESTER AND THAT IS SAFE — checked,
    /// not assumed:
    ///   - MapComponent_BurnLine.IsPlayerAttributed accrues arson debt only for a
    ///     fire whose instigator belongs to the PLAYER faction, so a Tribes-lit
    ///     front provokes no arson-justice raid against the colony.
    ///   - Fire damage carries Fire.instigator into its DamageInfo (Verse/Fire.cs),
    ///     and Faction.Notify_MemberTookDamage — the one place damage turns into
    ///     goodwill — returns immediately when the victim's faction IS the player,
    ///     and otherwise only charges goodwill when dinfo.Instigator.Faction is the
    ///     player. Neither branch can fire here, so a colonist caught by the rite's
    ///     burn costs the player nothing in relations and cannot flip the Tribes
    ///     hostile behind the player's back.
    ///
    /// SAFE STANDOFF IS REUSED, NOT BUILT. The RUT_RiteHarvest duty carries
    /// vanilla's JobGiver_SeekSafeTemperature ahead of the harvest job-giver, the
    /// constant humanlike think tree already handles a pawn who catches fire, and
    /// JobGiver_RUT_HarvestScorchFruit refuses any pod whose cell is currently
    /// burning. The result is a file of harvesters working just behind the front —
    /// which is what the sheet describes — with no pathing code of ours at all.
    /// </summary>
    public class LordToil_RUT_RiteHarvest : LordToil
    {
        private readonly LordJob_RUT_FireRite job;
        private readonly IntVec3 riteOrigin;

        public LordToil_RUT_RiteHarvest(LordJob_RUT_FireRite job, IntVec3 riteOrigin)
        {
            this.job = job;
            this.riteOrigin = riteOrigin;
        }

        public override IntVec3 FlagLoc => riteOrigin;

        public override bool AllowSatisfyLongNeeds => false;

        public override void Init()
        {
            base.Init();

            if (job == null || job.AlreadyIgnited)
            {
                return;
            }
            job.MarkIgnited();

            MapComponent_BurnLine watch = MapComponent_BurnLine.For(Map);
            if (watch == null)
            {
                return;
            }

            Pawn lead = LeadHarvester();
            IntVec3 at = lead != null ? lead.Position : riteOrigin;

            int lit = watch.IgniteRiteFront(at, lead);
            if (lit == 0 && at != riteOrigin)
            {
                // They stopped somewhere that will not take a fire — a paved
                // patch, the home area, too close to what the colony built. The
                // rite still happens, at the place it was walking to.
                watch.IgniteRiteFront(riteOrigin, lead);
            }
        }

        public override void UpdateAllDuties()
        {
            List<Pawn> pawns = lord.ownedPawns;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn?.mindState == null)
                {
                    continue;
                }
                PawnDuty duty = new PawnDuty(PyrelandsMechanicsDefOf.RUT_RiteHarvest, riteOrigin)
                {
                    focusSecond = riteOrigin,
                    radius = PyrelandsTuning.FireRiteHarvestRadius,
                    wanderRadius = PyrelandsTuning.FireRiteWanderRadius,
                };
                pawn.mindState.duty = duty;
            }
        }

        private Pawn LeadHarvester()
        {
            List<Pawn> pawns = lord.ownedPawns;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn != null && pawn.Spawned && !pawn.Dead && !pawn.Downed)
                {
                    return pawn;
                }
            }
            return null;
        }
    }
}
