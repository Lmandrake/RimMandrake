using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md:
    // a marriage is a bond that pleases Oomo (§3③ "marriages") and Mob'Unloo
    // ("a contract struck, a soul into the ledger", §3④), and it is one of
    // Ozzik's ambition-acts ("marriage", §3⑨ pleases).
    //
    // Verified against decompiled source (RimSage): Pawn_RelationsTracker.
    // AddDirectRelation is where every marriage lands its Spouse relation (the
    // ceremony's outcome). Spouse is reflexive but AddDirectRelation is called
    // once per marriage, so no double-count. Gated to a marriage that touches a
    // player colonist; ___pawn is the tracker's own pawn (Harmony field inject).
    [HarmonyPatch(typeof(Pawn_RelationsTracker), nameof(Pawn_RelationsTracker.AddDirectRelation))]
    public static class Patch_Marriage
    {
        [HarmonyPostfix]
        public static void Postfix(PawnRelationDef def, Pawn otherPawn, Pawn ___pawn)
        {
            if (def != PawnRelationDefOf.Spouse) return;

            bool touchesColony =
                (___pawn?.Faction == Faction.OfPlayer) ||
                (otherPawn?.Faction == Faction.OfPlayer);
            if (!touchesColony) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Oomo, EventMagnitude.Medium, "a marriage, the family grows");
            comp.ApplyDelta(God.MobUnloo, EventMagnitude.Small, "a marriage, a contract struck");
            comp.ApplyDelta(God.Ozzik, EventMagnitude.Small, "a marriage, an act of statecraft");
        }
    }
}
