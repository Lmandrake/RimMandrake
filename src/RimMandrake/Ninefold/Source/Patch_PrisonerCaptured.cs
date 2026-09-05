using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md:
    // "taking prisoners (captured body = captured value)" pleases Mob'Unloo
    // (§3④), and Oomo reads a captured body as the household growing and the
    // clan "dominant enough over other races to hold" them (§3③ dominance).
    //
    // Verified against decompiled source (RimSage): Pawn_GuestTracker.CapturedBy
    // is the single choke every capture funnels through (it sets GuestStatus to
    // Prisoner). Filtered to captures BY the player faction.
    [HarmonyPatch(typeof(Pawn_GuestTracker), nameof(Pawn_GuestTracker.CapturedBy))]
    public static class Patch_PrisonerCaptured
    {
        [HarmonyPostfix]
        public static void Postfix(Faction by, Pawn ___pawn)
        {
            if (by != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.MobUnloo, EventMagnitude.Medium,
                "prisoner taken: " + (___pawn?.LabelShortCap ?? "someone"));
            comp.ApplyDelta(God.Oomo, EventMagnitude.Small, "a body for the household");
        }
    }
}
