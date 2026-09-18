using UnityEngine;
using Verse;
using RimMandrake.Property;
using RimMandrake.SalvageClaim;

namespace RimMandrake.HirePlaceless
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, social-fabric pass. Spec item 9's "hiring the
    /// placeless": a flat, tunable hiring-advance fee — no per-skill or
    /// per-labor-value pricing model, same "flat and tunable only" discipline
    /// WalkableCommerce used before haggling and PickpocketUtility used for
    /// its own value floor. No second pricing model invented here.
    ///
    /// Silver counting/removal is NOT duplicated — reuses
    /// SalvageClaimFeeUtility.CountSilverInInventory/RemoveSilverFromInventory
    /// directly, same reuse WalkableCommerce's own BuyMerchandiseUtility
    /// already established for this mod.
    /// </summary>
    public static class HirePlacelessUtility
    {
        public static int ComputeHireFeeSilver() => Mathf.Max(1, Mathf.RoundToInt(PropertySettings.hirePlacelessFeeSilver));

        public static int CountSilverInInventory(Pawn pawn) => SalvageClaimFeeUtility.CountSilverInInventory(pawn);

        public static void RemoveSilverFromInventory(Pawn pawn, int amount) => SalvageClaimFeeUtility.RemoveSilverFromInventory(pawn, amount);
    }
}
