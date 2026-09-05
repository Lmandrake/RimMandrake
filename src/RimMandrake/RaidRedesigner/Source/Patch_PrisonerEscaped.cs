using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.RaidRedesigner
{
    // Verified against 1.6 source (RimSage): Source/RimWorld/GuestUtility.cs:72
    // `public static void Notify_PrisonerEscaped(Pawn prisoner)`, called from
    // exactly one place, Verse/Pawn.cs:3839, inside Pawn.ExitMap's own guest
    // block ("if (isPrisonerOfColony) { ...; if (!guest.Released && flag3)
    // GuestUtility.Notify_PrisonerEscaped(this); }") -- i.e. strictly BEFORE
    // that same ExitMap call reaches its own PassToWorld tail. Patch_
    // FledRaiderAndCaptain's ExitMap postfix fires afterward for this same
    // pawn (their Faction is typically still hostile) and does the actual
    // pinning once PassToWorld has run; this postfix only records the more
    // specific EscapedPrisoner tag first so it is not overwritten by the
    // generic FledRaider one (see GameComponent_OldFriends.RecordEncounter's
    // upgrade-only role rule).
    [HarmonyPatch(typeof(GuestUtility), nameof(GuestUtility.Notify_PrisonerEscaped))]
    public static class Patch_PrisonerEscaped
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn prisoner)
        {
            if (prisoner?.Faction == null) return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            roster.RecordEncounter(prisoner, prisoner.Faction, RoleTag.EscapedPrisoner,
                Find.TickManager.TicksGame, "escaped from our prison",
                grudgeDelta: 20, notabilityDelta: 10, pin: true);
        }
    }
}
