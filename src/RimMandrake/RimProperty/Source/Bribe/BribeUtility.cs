using UnityEngine;
using Verse;
using RimMandrake.Property;
using RimMandrake.SalvageClaim;

namespace RimMandrake.Bribe
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, social-fabric pass (bribes/bought-rounds as
    /// propagation dampers — spec item 9's second social-fabric sub-mechanic
    /// after Hiring the Placeless). A flat, tunable silver cost buys a flat,
    /// tunable REDUCTION in whatever a faction's own record already carries
    /// against the payer (FactionRecord.DampenSuspicion) — no new pricing
    /// model, same "flat and tunable only" discipline every other verb in
    /// this item already applies (WalkableCommerce's markup, Pickpocket's
    /// value floor, HirePlaceless's advance).
    ///
    /// Silver counting/removal is NOT duplicated — reuses
    /// SalvageClaimFeeUtility.CountSilverInInventory/RemoveSilverFromInventory
    /// directly, same reuse chain every other verb in this mod already
    /// established.
    /// </summary>
    public static class BribeUtility
    {
        public static int ComputeBribeFeeSilver() => Mathf.Max(1, Mathf.RoundToInt(PropertySettings.bribeFeeSilver));

        public static int CountSilverInInventory(Pawn pawn) => SalvageClaimFeeUtility.CountSilverInInventory(pawn);

        public static void RemoveSilverFromInventory(Pawn pawn, int amount) => SalvageClaimFeeUtility.RemoveSilverFromInventory(pawn, amount);
    }
}
