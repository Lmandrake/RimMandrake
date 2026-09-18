using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S2 build pass. RM_CompWorkedLottery/RM_LotteryTableDef
    // have compiled since the 2026-09-13 spike pass with no WorkGiver or
    // JobDriver ever reaching AddWork() — a hook built but never wired to its
    // consumer, the same class of gap MIASMA_MECHANICS_1/FEVER_WOOD_MECHANICS_1
    // each left themselves this session. This WorkGiver closes it.
    //
    // Generic on any Thing carrying RM_CompWorkedLottery, not hardcoded to one
    // ThingDef — RUT_DigShaft is its first content consumer; a future S6b
    // pump/derrick building (spec: "same comp, different yield table, so
    // derricks and dig shafts share one class") reuses this same WorkGiver
    // for free. Shape cribbed from RimWorld/WorkGiver_DeepDrill.cs (read in
    // full via RimSage this pass) minus the CompPowerTrader/Uninstall checks
    // DeepDrill needs and this manual-labor dig does not — the spec's own S2
    // text is "stake a dig, put work into it," a colonist digging by hand.
    public class RM_WorkGiver_WorkLottery : WorkGiver_Scanner
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
            if (comp == null || comp.Props?.table == null)
            {
                return false;
            }

            if (comp.TrapArmed)
            {
                // A ticking trap is not a work site — the fuse resolves on its
                // own CompTick regardless of any pawn's job. Disarming it is
                // TryDisarmPendingTrap, a separate interaction (owner card 2)
                // whose float-menu/work-type UI is still owed to a later pass.
                return false;
            }

            if (!pawn.CanReserve(t, 1, -1, null, forced))
            {
                return false;
            }

            if (t.IsBurning())
            {
                return false;
            }

            return true;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_WorkLottery, t, 1500, checkOverrideOnExpiry: true);
        }
    }
}
