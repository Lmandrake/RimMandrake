using RimWorld;
using Verse;
using RimMandrake.Property;

namespace RimMandrake.TheftHauler
{
    /// <summary>
    /// BUILDING_THEFT_HAULER_1's own toils are vanilla's — this subclasses
    /// JobDriver_RemoveBuilding (the same base JobDriver_Uninstall itself
    /// extends) purely to reuse MakeNewToils' goto/work/FinishedRemoving
    /// shape (Toils_Goto, the uninstallWork-driven progress bar,
    /// designationManager cleanup) rather than reimplement uninstall
    /// physics. Two differences from vanilla JobDriver_Uninstall:
    ///
    ///  1. Designation => null skips FailOnThingMissingDesignation entirely
    ///     — there is deliberately no Designation_Uninstall placed (that
    ///     designator's own DesignateThing forcibly SetFaction(Player)s the
    ///     target before the job even starts, which would erase the very
    ///     "not yours" fact this whole item exists to check). Nothing here
    ///     requires the target be player-owned or already claimable — the
    ///     float menu provider is the only gate on what can be targeted.
    ///
    ///  2. FinishedRemoving fires PropertyEngine.Fire's TakingEvent(Act=Strip)
    ///     BEFORE calling the real MinifyUtility.Uninstall() extension method
    ///     (via Building.Uninstall(), same call vanilla's own FinishedRemoving
    ///     makes) — "at the moment of uninstall, not haul-pickup" per the item
    ///     spec. Fire() resolves the prior claim and authorization itself; an
    ///     own-claim or unclaimed building is a no-op inside it, so this calls
    ///     Fire unconditionally rather than duplicate that test out here. The
    ///     event fires against the live Building (before it is wrapped into a
    ///     MinifiedThing); MakeMinified reuses the SAME Thing object as
    ///     MinifiedThing.InnerThing, so a claim recorded against that
    ///     reference stays keyed correctly in GameComponent_PropertyLedger's
    ///     Dictionary&lt;Thing, ClaimRecordList&gt; afterward.
    /// </summary>
    public class JobDriver_TheftHaulUninstall : JobDriver_RemoveBuilding
    {
        protected override DesignationDef Designation => null;

        protected override float TotalNeededWork => TargetA.Thing?.def?.building?.uninstallWork ?? 200f;

        protected override EffecterDef WorkEffecter => null;

        protected override void FinishedRemoving()
        {
            Building building = base.Building;
            if (building != null)
            {
                // PropertyEngine.Fire resolves the prior claim and the
                // authorization check ITSELF (that logic is private to
                // PropertyEngine, by design — one source of truth). An own-
                // claim or unclaimed building is a no-op inside Fire (no
                // record, no perception roll): safe to call unconditionally
                // rather than duplicate the own/not-own test out here.
                PropertyEngine.Fire(new TakingEvent(building, ClaimantRef.OfPawn(pawn),
                    TakingAct.Strip, Find.TickManager.TicksGame));
            }
            building.Uninstall();
            pawn.records.Increment(RecordDefOf.ThingsUninstalled);
        }
    }
}
