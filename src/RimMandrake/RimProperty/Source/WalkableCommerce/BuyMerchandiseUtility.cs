using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Property;
using RimMandrake.SalvageClaim;

namespace RimMandrake.WalkableCommerce
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, walkable-commerce pass. Spec item 9's
    /// "purchase as the legal provenance record": prices a merchandise item
    /// for the Buy interaction (<see cref="FloatMenuOptionProvider_BuyMerchandise"/>)
    /// purely from the Thing's own already-published <c>MarketValue</c> stat
    /// (per-unit, per Verse.Thing.MarketValue's own definition — multiplied
    /// by stackCount for a stack, the same shape vanilla trade pricing
    /// uses) — no second, invented pricing model, same discipline as
    /// SalvageClaimFeeUtility.ComputeFeeSilver. Haggling (spec item 9's own
    /// word) is deliberately NOT built this pass: a flat markup only,
    /// tunable in Mod Settings — a negotiation mechanic is a follow-up, not
    /// required for this pass's criteria.
    ///
    /// Silver handling (counting/removing from the acting pawn's own carried
    /// inventory) is NOT duplicated here — it reuses
    /// SalvageClaimFeeUtility.CountSilverInInventory/RemoveSilverFromInventory
    /// directly, both already public and already correct (same v1
    /// simplification: the paying pawn's own carried silver only, no
    /// colony-stockpile draw).
    /// </summary>
    public static class BuyMerchandiseUtility
    {
        // A nominal floor so a worthless trinket never sells for 0 silver
        // (a purchase that costs nothing isn't a purchase, and a
        // ClaimBasis.Purchased record ought to mean something happened).
        private const int MinPriceSilver = 1;

        public static int ComputePriceSilver(Thing thing)
        {
            float unitValue = Mathf.Max(0f, thing.MarketValue);
            float total = unitValue * Mathf.Max(1, thing.stackCount) * PropertySettings.walkableCommerceMarkup;
            return Mathf.Max(MinPriceSilver, Mathf.RoundToInt(total));
        }

        public static int CountSilverInInventory(Pawn pawn) => SalvageClaimFeeUtility.CountSilverInInventory(pawn);

        public static void RemoveSilverFromInventory(Pawn pawn, int amount) => SalvageClaimFeeUtility.RemoveSilverFromInventory(pawn, amount);
    }
}
