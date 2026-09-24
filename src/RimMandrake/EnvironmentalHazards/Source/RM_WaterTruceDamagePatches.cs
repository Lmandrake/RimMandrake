using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // WATER_TRUCE_RETRIBUTION_1. Postfix on Thing.PostApplyDamage(DamageInfo,
    // float) — the single seam every damage-dealing path in the game
    // converges on after a hit actually lands (Thing.TakeDamage calls it
    // once, at the end; Pawn/Building/ThingWithComps's own overrides all
    // call base.PostApplyDamage before doing their own thing, so patching
    // the BASE method's body fires for every Thing subclass, not just plain
    // Thing). Reading dinfo.Instigator / dinfo.InstigatorGuilty here is the
    // item's own MEASURED engine citation (Verse/DamageInfo.cs:90,114) —
    // no "did the victim fight back" tracking needed at all.
    //
    // Armed from EnvironmentalHazardsMod's static constructor, same posture
    // as every other patch in this file: logs and declines rather than
    // throwing if the signature has moved.
    public static class RM_WaterTruceDamagePatches
    {
        public static void PostApplyDamage_Postfix(Thing __instance, DamageInfo dinfo, float totalDamageDealt)
        {
            __instance?.Map?.GetComponent<RM_MapComponent_WaterTruce>()?.Notify_GuiltyHitInTruce(dinfo, __instance, totalDamageDealt);
        }
    }
}
