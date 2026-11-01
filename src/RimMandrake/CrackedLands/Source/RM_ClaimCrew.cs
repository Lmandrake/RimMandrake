using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.CrackedLands
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_SALVAGE_CLAIM_CREW_1: THE RIVAL CREW.
    //
    // A temporary visitor lord on the floodline claim. It races the player for what the recede exposed (a piece the player
    // has allowed, hauled or moved is claimed and left alone), keeps a short-lived shop (the card of 2026-10-08: it TRADES:
    // it sells what it dug out and buys salvage back), and leaves after about a day. It turns on the player only when its
    // faction's relations collapse: then it strips what is left of the claim, fights anyone in its way, and runs.
    //
    // Who comes and what they say is data (RM_ClaimCrewProfileDef), so the Utinni patch substitutes Jawas, a crawler prop
    // and Star Wars dialogue without code. The map component owns when (RM_MapComponent_RecedeAftermath).
    // ════════════════════════════════════════════════════════════════════
    public class RM_ClaimCrewProfileDef : Def
    {
        // By name, in order: a faction only some mod lists carry must not be a cross-reference error on the rest.
        public List<string> factionDefs = new List<string>();
        public TraderKindDef traderKind;
        // Optional: a thing parked on the claim while the crew works it (by name, same reason).
        public string campProp;
        public string arrivalLabel = "";
        public string arrivalText = "";     // {0} = faction name
        public string collapseLabel = "";
        public string collapseText = "";    // {0} = faction name
        public string leaveText = "";       // {0} = faction name

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (factionDefs.NullOrEmpty())
            {
                yield return "no factionDefs: the crew could never come";
            }
            if (traderKind == null)
            {
                yield return "no traderKind: the crew could never trade";
            }
        }
    }

    public class RM_LordJob_SalvageClaim : LordJob
    {
        public const string MemoClaimEmpty = "RM_ClaimEmpty";

        private Faction faction;
        private IntVec3 claim;
        private int stayTicks;

        public RM_LordJob_SalvageClaim()
        {
        }

        public RM_LordJob_SalvageClaim(Faction faction, IntVec3 claim, int stayTicks)
        {
            this.faction = faction;
            this.claim = claim;
            this.stayTicks = stayTicks;
        }

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            RM_ClaimCrewProfileDef profile = RM_CrackedLandsDefOf.RM_ClaimCrew_Scavengers;

            RM_LordToil_SalvageClaim work = new RM_LordToil_SalvageClaim(claim, RM_CrackedLandsDefOf.RM_WorkSalvageClaim, false);
            graph.StartingToil = work;
            RM_LordToil_SalvageClaim steal = new RM_LordToil_SalvageClaim(claim, RM_CrackedLandsDefOf.RM_StealSalvageClaim, true);
            graph.AddToil(steal);
            LordToil_ExitMap leave = new LordToil_ExitMap(LocomotionUrgency.Walk, canDig: true);
            graph.AddToil(leave);

            Transition done = new Transition(work, leave);
            done.AddTrigger(new Trigger_TicksPassed(stayTicks));
            done.AddPreAction(new TransitionAction_Custom((System.Action)(() => Messages.Message(
                string.Format(profile.leaveText, faction.Name), MessageTypeDefOf.NeutralEvent))));
            done.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(done);

            Transition collapse = new Transition(work, steal);
            collapse.AddTrigger(new Trigger_BecamePlayerEnemy());
            collapse.AddPreAction(new TransitionAction_Custom((System.Action)(() => Find.LetterStack.ReceiveLetter(
                profile.collapseLabel, string.Format(profile.collapseText, faction.Name), LetterDefOf.ThreatSmall,
                new LookTargets(claim, lord.Map), faction))));
            collapse.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(collapse);

            Transition stripped = new Transition(steal, leave);
            stripped.AddTrigger(new Trigger_Memo(MemoClaimEmpty));
            stripped.AddTrigger(new Trigger_TicksPassed(RM_ClaimKernel.StealCapTicks));
            stripped.AddPostAction(new TransitionAction_EndAllJobs());
            graph.AddTransition(stripped);
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_References.Look(ref faction, "faction");
            Scribe_Values.Look(ref claim, "claim");
            Scribe_Values.Look(ref stayTicks, "stayTicks");
        }
    }

    public class RM_LordToil_SalvageClaim : LordToil
    {
        private readonly IntVec3 claim;
        private readonly DutyDef duty;
        private readonly bool stealing;

        public RM_LordToil_SalvageClaim(IntVec3 claim, DutyDef duty, bool stealing)
        {
            this.claim = claim;
            this.duty = duty;
            this.stealing = stealing;
        }

        public override void UpdateAllDuties()
        {
            for (int i = 0; i < lord.ownedPawns.Count; i++)
            {
                lord.ownedPawns[i].mindState.duty = new PawnDuty(duty, claim);
            }
        }

        public override void LordToilTick()
        {
            if (stealing && lord.ticksInToil % 250 == 0
                && lord.Map.GetComponent<RM_MapComponent_RecedeAftermath>().StealableCount() == 0)
            {
                lord.ReceiveMemo(RM_LordJob_SalvageClaim.MemoClaimEmpty);
            }
        }
    }

    /// <summary>The nearest piece this crew may still take: open while they are visitors, anything left once hostile.</summary>
    public class RM_JobGiver_TakeClaimSalvage : ThinkNode_JobGiver
    {
        public bool stealing;

        public override ThinkNode DeepCopy(bool resolve = true)
        {
            RM_JobGiver_TakeClaimSalvage copy = (RM_JobGiver_TakeClaimSalvage)base.DeepCopy(resolve);
            copy.stealing = stealing;
            return copy;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            Thing piece = pawn.Map.GetComponent<RM_MapComponent_RecedeAftermath>()?.NearestPieceFor(pawn, stealing);
            if (piece == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(JobDefOf.TakeInventory, piece);
            job.count = piece.stackCount;
            job.takeInventoryDelay = RM_ClaimKernel.DigTicks;
            return job;
        }
    }
}
