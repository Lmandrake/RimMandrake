using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.SalvageClaim
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, salvage-law pass only. The claim-fee gizmo
    /// (item point 1), built as a right-click float-menu order — the same
    /// shape BUILDING_THEFT_HAULER_1's FloatMenuOptionProvider_
    /// TheftHaulUninstall uses, chosen for the identical reason: this needs
    /// TWO selections at once (the paying pawn AND the target Thing), which
    /// only a "select the pawn, right-click the target" order naturally
    /// provides — a Command_Action gizmo on the target itself has no acting-
    /// pawn context. RimWorld 1.6's FloatMenuMakerMap.Init() auto-registers
    /// every non-abstract FloatMenuOptionProvider subclass via reflection,
    /// so no Harmony hook or registration call is needed.
    ///
    /// Unlike TheftHauler's uninstall job, paying a fee needs no multi-tick
    /// work (item spec: "this does NOT need a travel job ... since paying a
    /// fee doesn't require uninstalling anything") — the whole transaction
    /// (silver deduction + PropertyEngine.Fire) runs instantly from this
    /// option's own delegate, no JobDriver/JobDef at all. CanReach is still
    /// checked (mirrors vanilla's own FloatMenuOptionProvider_Strip) purely
    /// as a "can this pawn physically get there" UX gate, matching the
    /// established float-menu-order pattern.
    /// </summary>
    public class FloatMenuOptionProvider_PaySalvageClaim : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            Pawn actor = context.FirstSelectedPawn;
            if (clickedThing == null || clickedThing == actor) return null;
            if (!clickedThing.Spawned) return null;

            // Item point 3, "the powered-down droid case": Pawn IS a Thing
            // (Pawn : ThingWithComps : Thing, traced directly off Verse.Pawn's
            // own class declaration — not assumed), and both TakingEvent.Thing
            // and ClaimEngine.ResolveClaim(Thing, int) are typed generically
            // enough to accept one, so the interaction below falls out for a
            // Pawn target with no special-casing needed past this gate.
            //
            // The gate itself: only a DOWNED mechanoid/droid — mirrors
            // vanilla's own "can only interact with a downed pawn" precedent
            // (Verse.StrippableUtility.CanBeStrippedByColony's pawn.Downed
            // check) so this can't be used on a pawn that can still fight or
            // flee. Restricted further to RaceProps.IsMechanoid: a downed
            // HUMANLIKE pawn is vanilla's own Arrest/Rescue/Capture territory
            // and edges into the crime-suite/capture verb family, which this
            // pass explicitly does not build (see design/Jawa/
            // ownership_settlement_spec.md item 9 and this item's "Explicitly
            // OUT of this pass" list) — "the powered-down droid" is this
            // pass's literal scope, not "any downed pawn."
            if (clickedThing is Pawn targetPawn)
            {
                if (!targetPawn.Downed) return null;
                if (targetPawn.RaceProps == null || !targetPawn.RaceProps.IsMechanoid) return null;
            }
            else
            {
                // Nothing gated the TARGET KIND before this point - only "not the
                // actor" and "spawned". ClaimEngine.ResolveVirtualClaim only ever
                // suppresses the offer for Faction-owned things (colony property),
                // so with no gate here every wild plant, rock chunk, unowned ruin
                // item and enemy corpse under the cursor (all Faction == null) got
                // offered a paid salvage claim. Scope this to what a "salvage
                // claim" actually means: a real, valuable, ownable Item or
                // Building, not the map itself.
                if (clickedThing.def.category != ThingCategory.Item && clickedThing.def.category != ThingCategory.Building)
                    return null;
                if (clickedThing.def.building != null && clickedThing.def.building.isNaturalRock)
                    return null;
                if (clickedThing.MarketValue <= 0f)
                    return null;
            }

            ClaimantRef actorRef = ClaimantRef.OfPawn(actor);
            int tick = Find.TickManager.TicksGame;

            // Item point 2's own instruction: resolve via ClaimEngine.
            // ResolveClaim before deciding whether the interaction should
            // even be offered (the pattern BUILDING_THEFT_HAULER_1's own
            // provider follows to decide float-menu offering — see that
            // mod's Source/FloatMenuOptionProvider_TheftHaulUninstall.cs).
            ClaimResolution? priorClaim = ClaimEngine.ResolveClaim(clickedThing, tick);
            if (IsAlreadyFreeToUse(actorRef, priorClaim)) return null;

            int fee = SalvageClaimFeeUtility.ComputeFeeSilver(clickedThing, priorClaim);

            if (!actor.CanReach(clickedThing, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot pay salvage claim on " + clickedThing.LabelShort + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            int carried = SalvageClaimFeeUtility.CountSilverInInventory(actor);
            if (carried < fee)
            {
                return new FloatMenuOption(
                    "Cannot pay salvage claim on " + clickedThing.LabelShort
                    + ": not enough silver (need " + fee + ", have " + carried + ")", null);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Pay salvage claim fee (" + fee + " silver) on " + clickedThing.LabelShort,
                delegate
                {
                    SalvageClaimFeeUtility.RemoveSilverFromInventory(actor, fee);
                    // PropertyEngine.Fire's own Claim case (ClaimBasis.
                    // ClaimFeePaid, WasAuthorized = true unconditionally) IS
                    // the result this whole interaction exists to trigger —
                    // this mod builds only the job/interaction that fires it,
                    // per the item spec's own framing.
                    PropertyEngine.Fire(new TakingEvent(clickedThing, actorRef, TakingAct.Claim, Find.TickManager.TicksGame));
                }), actor, clickedThing);
        }

        // Mirrors RimMandrake.Property.PropertyEngine's private IsAuthorized
        // rule (own claim, or Commons + same faction as the actor) — that
        // method is intentionally private to the fabric (one source of
        // truth for AUTHORIZATION), so this is a separate, narrower copy
        // used ONLY to decide whether to show the gizmo at all. Fire() would
        // still behave correctly (a fresh, unwanted ClaimFeePaid record) even
        // if this check were skipped; this exists purely so the game never
        // offers to sell a pawn a fee for something that is already theirs
        // for free.
        private static bool IsAlreadyFreeToUse(ClaimantRef actor, ClaimResolution? priorClaim)
        {
            if (!priorClaim.HasValue) return false; // unclaimed - still an admin fee worth charging

            ClaimantRef claimant = priorClaim.Value.Claimant;
            if (claimant.Equals(actor)) return true;

            if (claimant.Kind == ClaimantKind.Commons && actor.Kind == ClaimantKind.Pawn
                && actor.Pawn?.Faction == claimant.Faction)
            {
                return true;
            }

            return false;
        }
    }
}
