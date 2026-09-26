using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 owner card 2 (RULED 2026-09-12, sump_kit_spec.md "Open
    // owner cards"): "era traps are disarmable — high skill gate, failure
    // detonates." RM_CompWorkedLottery.TryDisarmPendingTrap has shipped a
    // real, callable API since the 2026-09-13 spike pass; every build pass
    // since (S2/S3/S4) has flagged its float-menu/work-type UI as owed,
    // "content/UI work for the full build, not an engine-fact question" —
    // this WorkGiver/JobDriver pair (see RM_JobDriver_DisarmLotteryTrap.cs)
    // closes it, cribbing RM_WorkGiver_WorkLottery.cs's own shape (its
    // opposite-sense sibling: that one refuses an armed trap as a work site,
    // this one exists ONLY for an armed trap).
    //
    // 🔑 Deliberate design choice, not an oversight: this WorkGiver does NOT
    // pre-check the pawn's Mining skill against
    // RM_CompWorkedLottery.Props.disarmSkillThreshold before assigning the
    // job. "High skill gate, failure detonates" reads truest as a real
    // stake, not a filtered non-event that can never actually happen — a
    // colony sends whoever currently has Mining work enabled and free (the
    // player's own work-priority assignment IS "the click is a decision,"
    // per the spec's own framing of the ruling), and
    // TryDisarmPendingTrap's own deterministic skill check decides the
    // outcome for real, exactly as carded. A player who wants this safe
    // keeps a high-Mining pawn on Mining duty near an armed find; a player
    // who does not gambles, per the spec's own intent — the gate lives in
    // the comp's own API, not in a filter that would make the "failure"
    // branch unreachable in ordinary play.
    public class RM_WorkGiver_DisarmLotteryTrap : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial);

        public override PathEndMode PathEndMode => PathEndMode.InteractionCell;

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (t.Faction != pawn.Faction)
            {
                return false;
            }

            RM_CompWorkedLottery comp = t.TryGetComp<RM_CompWorkedLottery>();
            if (comp == null || !comp.TrapArmed)
            {
                // No trap armed — this is RM_WorkGiver_WorkLottery's own job
                // to offer instead (see that class's own HasJobOnThing,
                // which refuses the opposite case for the same reason).
                return false;
            }

            return pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_DisarmLotteryTrap, t);
        }
    }
}
