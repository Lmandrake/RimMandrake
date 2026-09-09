using HarmonyLib;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #4's trigger point: the instant a T3 titan's Corpse actually
    /// spawns onto a map (Verse/Corpse.cs SpawnSetup), swap it for the
    /// landmark. Firing on SpawnSetup rather than on Pawn.Kill / MakeCorpse
    /// means this works regardless of which vanilla code path caused the
    /// corpse to appear (death, quest cleanup, debug spawn, ...) - anywhere a
    /// T3 Corpse ends up on a map, it becomes a site instead.
    ///
    /// OPEN QUESTION (flagged, not resolved here): respawningAfterLoad is
    /// skipped so a save/reload never re-triggers conversion on an
    /// already-loaded Corpse. If a T3 corpse is ever saved and reloaded
    /// UNCONVERTED (e.g. this mod is added to an existing save with a titan
    /// already dead), it will sit there as an ordinary Corpse rather than
    /// becoming a site - untested, since no live game access was available
    /// for this build.
    /// </summary>
    [HarmonyPatch(typeof(Corpse), nameof(Corpse.SpawnSetup))]
    internal static class Patch_Corpse_SpawnSetup_TitanicSite
    {
        private static void Postfix(Corpse __instance, Map map, bool respawningAfterLoad)
        {
            if (respawningAfterLoad)
            {
                return;
            }
            Pawn inner = __instance.InnerPawn;
            if (inner == null || TitanicTierUtility.GetTier(inner) != TitanicTier.T3)
            {
                return;
            }
            TitanicCorpseSiteUtility.ConvertToSite(__instance, map);
        }
    }
}
