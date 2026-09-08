using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1. Reauthored, not the donor mod's own class -
    /// same shape as OuterRimDroids.Comp_TargetableOnDownedDroid
    /// (droid_ruling.md section 6/history: "Comp_TargetableOnDownedDroid
    /// validating pawn.Downed || pawn.IsPrisoner") but adds the faction-key
    /// gate the donor never had, and deliberately excludes corpses - the
    /// donor's own documented bug (droid_ruling.md section 8: "Do not use a
    /// data spike on a corpse... InvalidCastException") does not exist here
    /// because corpses were never a legal target in the first place.
    ///
    /// Only supplies the targeting UI/validation half of the flow (which
    /// pawns are legal, clickable targets). The actual walk-carry-work-effect
    /// sequence is entirely in JobDriver_DWDataSpike, NOT in this class's
    /// GetTargets/DoEffect - CompTargetable's base DoEffect is never invoked
    /// in this wiring because RSW_DW_DataSpike's CompProperties_Usable.useJob
    /// points straight at our own JobDef/JobDriver rather than vanilla's
    /// generic JobDriver_UseItem, so CompUsable.UsedBy (and therefore
    /// CompUseEffect.DoEffect) is never reached. This is a deliberate
    /// simplification over the donor's two-stage CompUsable ->
    /// CompTargetEffect -> second job chain (droid_ruling.md section 6): one
    /// job instead of two, with target indices that already match how
    /// CompUsable.TryStartUseJob constructs the job (TargetA = the spike
    /// item/parent, TargetB = the picked pawn/extraTarget).
    /// </summary>
    public class CompTargetable_DWDataSpike : CompTargetable
    {
        protected override bool PlayerChoosesTarget => true;

        protected override TargetingParameters GetTargetingParameters()
        {
            CompDWDataSpike spike = parent.GetComp<CompDWDataSpike>();
            return new TargetingParameters
            {
                canTargetPawns = true,
                canTargetBuildings = false,
                canTargetItems = false,
                mapObjectTargetsMustBeAutoAttackable = false,
                // DROIDWORKS_WILD_DROIDS_1 (packet E4): the downed/prisoner and
                // faction-key tests moved into CompDWDataSpike.ValidTarget so
                // this UI gate and the job's own completion re-check share one
                // definition - E4 adds a third condition (requiresPrisoner) and
                // two copies of the rule would have drifted immediately.
                validator = (TargetInfo x) => x.Thing is Pawn p
                    && spike != null
                    && spike.ValidTarget(p)
            };
        }

        public override IEnumerable<Thing> GetTargets(Thing targetChosenByPlayer = null)
        {
            yield return targetChosenByPlayer;
        }
    }
}
