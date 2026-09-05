using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md:
    // "art completed" is the first of Ozzik's ambition-acts (§3⑨ pleases) - the
    // pride-meter that draws fire. A finished sculpture is the clearest single
    // "we reached for greatness" event in play.
    //
    // Verified against decompiled source (RimSage): CompArt.JustCreatedBy(Pawn)
    // is called once when a piece of art is finished and attributed to its
    // maker. Gated to art made by a player colonist.
    [HarmonyPatch(typeof(CompArt), nameof(CompArt.JustCreatedBy))]
    public static class Patch_ArtCreated
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn pawn)
        {
            if (pawn?.Faction != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Ozzik, EventMagnitude.Small,
                "art completed by " + pawn.LabelShortCap);
        }
    }
}
