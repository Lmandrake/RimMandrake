using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.Pickpocket
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, crime-suite pass. Spec item 9: "crime suite
    /// (pickpocket, night burglary, fencing, smuggling past gate searches)."
    /// This pass scopes to pickpocket only — see this mod's own item-file
    /// entry for why the other three stay out.
    ///
    /// Same right-click float-menu-order shape as SalvageClaim/
    /// WalkableCommerce's own providers (needs a selected acting pawn AND a
    /// clicked target; no JobDriver — the whole transaction, including the
    /// physical hand-off, runs instantly from this option's own delegate).
    /// FloatMenuMakerMap.Init() auto-registers every non-abstract
    /// FloatMenuOptionProvider subclass via reflection, so no Harmony hook or
    /// registration call is needed here either.
    ///
    /// Where this GENUINELY differs from the prior two verbs, and from
    /// TheftHauler/AnimalTheft: those two fire TakingAct.Buy/Claim, whose
    /// PropertyEngine.Fire case sets WasAuthorized = true unconditionally —
    /// a legitimate transaction, by definition never witnessed. This verb
    /// fires plain TakingAct.Take against a Thing a target Pawn currently
    /// possesses (ClaimEngine's own virtual Situational claim, resolved to
    /// that Pawn at strength 0.9 — see ClaimEngine.FindPossessor's
    /// Pawn_InventoryTracker case) with actor != that Pawn, which
    /// PropertyEngine.IsAuthorized correctly refuses. That is NOT new fabric
    /// work either: it's the exact same "fabric already implements the
    /// RESULT" situation Claim/Buy were in — PropertyEngine.Fire's own
    /// Take case (RecordTransfer(..., ClaimBasis.Stolen, ...) against the
    /// ORIGIN claimant, then RollPerceptionAndPropagate) already fully
    /// covers what happens once this fires; AnimalTheft/TheftHauler already
    /// exercise that exact case, just for unattended items and buildings
    /// rather than a living pawn's own carried inventory. This is the first
    /// verb to point Take at a person, which is what makes it "pickpocket"
    /// and not a duplicate of either.
    /// </summary>
    public class FloatMenuOptionProvider_Pickpocket : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!PropertySettings.pickpocketEnabled) return null;

            Pawn actor = context.FirstSelectedPawn;

            // Scoped to a living Pawn target only — an ordinary Thing's
            // unauthorized Take is already AnimalTheft's (unattended ground
            // items) and TheftHauler's (buildings, via Strip) territory; this
            // verb's whole reason to exist is reaching into someone's own
            // carried inventory, which only a Pawn target has.
            if (!(clickedThing is Pawn targetPawn)) return null;
            if (targetPawn == actor) return null;
            if (!targetPawn.Spawned) return null;

            // Actively hostile is vanilla's own attack/capture territory,
            // not a quiet lift — pickpocketing mid-firefight isn't the verb
            // this pass is building. A downed, sleeping, or simply
            // unaware-of-you pawn (same faction or not) is exactly the
            // intended target; RollWitnesses already excludes anyone
            // !Awake() or Downed from being able to personally notice, so a
            // sleeping/downed target's own perception risk drops out
            // naturally with no special-casing needed here.
            if (targetPawn.HostileTo(actor)) return null;

            Thing stolenItem = PickpocketUtility.FindStealableItem(targetPawn);
            if (stolenItem == null) return null;

            if (!actor.CanReach(targetPawn, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot pickpocket " + targetPawn.LabelShort + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            ClaimantRef actorRef = ClaimantRef.OfPawn(actor);

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Pickpocket " + stolenItem.LabelShort + " from " + targetPawn.LabelShort,
                delegate
                {
                    // Fire BEFORE the hand-off, same ordering AnimalTheft/
                    // TheftHauler already use ("at the moment of taking, not
                    // haul-pickup") — ClaimEngine.ResolveClaim needs to see
                    // the item still IN the target's inventory to resolve
                    // their Situational claim correctly.
                    PropertyEngine.Fire(new TakingEvent(stolenItem, actorRef, TakingAct.Take, Find.TickManager.TicksGame));
                    PickpocketUtility.TransferToActor(stolenItem, targetPawn, actor);
                }), actor, targetPawn);
        }
    }
}
