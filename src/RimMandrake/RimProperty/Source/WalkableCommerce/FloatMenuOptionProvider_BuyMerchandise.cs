using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.WalkableCommerce
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, walkable-commerce pass. Spec item 9:
    /// "walkable commerce (merchandise, haggling, purchase as the legal
    /// provenance record)" — distinct from a caravan trade menu, this is a
    /// right-click order a pawn can use while physically standing at a
    /// settlement (or anywhere else another claimant's merchandise sits),
    /// same float-menu-order shape as SalvageClaim's own
    /// FloatMenuOptionProvider_PaySalvageClaim (needs both a selected paying
    /// pawn and a clicked target Thing; no travel job — the whole
    /// transaction runs instantly from the option's own delegate, same
    /// precedent as the claim-fee gizmo). FloatMenuMakerMap.Init() auto-
    /// registers every non-abstract FloatMenuOptionProvider via reflection,
    /// so no Harmony hook is needed here either.
    ///
    /// Where this DIFFERS from the claim-fee gizmo, deliberately: a claim
    /// fee is an admin fee payable on an UNCLAIMED thing (nobody's selling
    /// it, you're just settling the gray zone). A purchase needs an actual
    /// seller — a resolved prior claim held by someone who isn't the actor.
    /// An unclaimed item has nothing to buy FROM; that's the claim-fee
    /// verb's territory, not this one's, so this provider explicitly
    /// requires <c>priorClaim.HasValue</c> where PaySalvageClaim explicitly
    /// allows it to be absent.
    ///
    /// Firing TakingAct.Buy is not new fabric work: PropertyEngine.Fire's
    /// existing Buy case (RecordTransfer(..., ClaimBasis.Purchased, 1f, ...),
    /// WasAuthorized = true unconditionally — "a completed sale is
    /// legitimate by definition") already fully implements the RESULT, same
    /// as Claim did for SalvageClaim; this mod builds only the job/
    /// interaction that fires it. No physical hand-off of the Thing happens
    /// here (same v1 simplification as the claim-fee gizmo, which doesn't
    /// haul the wreck either) — the point of the interaction is the
    /// PROVENANCE RECORD (spec item 9's own framing), not an inventory
    /// move; a colonist can haul/carry the now-legitimately-claimed item
    /// through the normal vanilla routes afterward.
    /// </summary>
    public class FloatMenuOptionProvider_BuyMerchandise : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!PropertySettings.walkableCommerceEnabled) return null;

            Pawn actor = context.FirstSelectedPawn;
            if (clickedThing == null || clickedThing == actor) return null;
            if (!clickedThing.Spawned) return null;

            // Merchandise means portable goods — a live pawn (hiring/
            // indenture) is social-fabric/crime-suite territory (spec item
            // 9), and a Building is fixed infrastructure, not stock for
            // sale. Scoped to ThingCategory.Item only, same discipline
            // PaySalvageClaim used to scope ITS target kind.
            if (clickedThing.def.category != ThingCategory.Item) return null;
            if (clickedThing.MarketValue <= 0f) return null;

            ClaimantRef actorRef = ClaimantRef.OfPawn(actor);
            int tick = Find.TickManager.TicksGame;

            ClaimResolution? priorClaim = ClaimEngine.ResolveClaim(clickedThing, tick);

            // No resolved claimant at all means nobody is selling this —
            // the claim-fee gizmo (PaySalvageClaim) is the verb for an
            // unclaimed thing, not this one.
            if (!priorClaim.HasValue) return null;
            if (IsAlreadyFreeToUse(actorRef, priorClaim.Value)) return null;

            int price = BuyMerchandiseUtility.ComputePriceSilver(clickedThing);

            if (!actor.CanReach(clickedThing, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot buy " + clickedThing.LabelShort + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            int carried = BuyMerchandiseUtility.CountSilverInInventory(actor);
            if (carried < price)
            {
                return new FloatMenuOption(
                    "Cannot buy " + clickedThing.LabelShort
                    + ": not enough silver (need " + price + ", have " + carried + ")", null);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Buy " + clickedThing.LabelShort + " (" + price + " silver)",
                delegate
                {
                    BuyMerchandiseUtility.RemoveSilverFromInventory(actor, price);
                    // PropertyEngine.Fire's own Buy case already fully
                    // implements the result — see this method's doc comment.
                    PropertyEngine.Fire(new TakingEvent(clickedThing, actorRef, TakingAct.Buy, Find.TickManager.TicksGame));
                }), actor, clickedThing);
        }

        // Narrower local copy of PropertyEngine's own private IsAuthorized
        // rule, same pattern and same reasoning as PaySalvageClaim's own
        // IsAlreadyFreeToUse: used only to decide whether to OFFER the
        // gizmo (never buy from yourself, or from your own faction's
        // Commons stock) — PropertyEngine.Fire's Buy case would still
        // behave correctly (an odd but harmless self-purchase record) even
        // if this check were skipped.
        private static bool IsAlreadyFreeToUse(ClaimantRef actor, ClaimResolution priorClaim)
        {
            ClaimantRef claimant = priorClaim.Claimant;
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
