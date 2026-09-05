using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.RaidRedesigner
{
    // Two verified seams, one file (both are "a Blackstar/prisoner guest
    // status change" per design/Jawa/proposals/plot_mechanisms_wave.md §1.4's
    // table, just the two opposite directions):
    //
    //   - Source/RimWorld/GenGuest.cs: `public static void PrisonerRelease(Pawn p)`
    //     is the real public entry point for "we released a prisoner" (it
    //     unconditionally sets `p.guest.Released = true` via the private
    //     GuestRelease helper). The design doc's own literal citation --
    //     `Pawn_GuestTracker.SetGuestStatus(null)` -- only fires on the branch
    //     of GuestRelease taken when the released pawn STAYS on our map
    //     (ShouldStayOnMapOnRelease: player-home pawns and WildMen); a
    //     released FOREIGN prisoner (the raider/captive case this hook cares
    //     about) instead takes the exitMapOnArrival branch and never calls
    //     SetGuestStatus at all. PrisonerRelease is the seam that always
    //     fires for both branches, so it replaces the doc's literal citation
    //     with the real always-fires equivalent of the same event.
    //   - Source/RimWorld/Pawn_GuestTracker.cs: `public void CapturedBy(Faction by, Pawn byPawn = null)`
    //     is the real, single "this pawn just became a prisoner" seam
    //     (`SetGuestStatus(by, GuestStatus.Prisoner)` is only the last of
    //     three things it does) -- cleaner than patching the broader
    //     SetGuestStatus overload directly.
    //
    // Blackstar identity: src/RimUtinni/UtinniPatches/Patches/BlackstarCompany.xml
    // ("BlackstarCompany.xml ... Builds FACTION_SPEC.md section 10, 'Blackstar
    // Company ; PATCH vanilla `Pirate`'. A reskin, not a new def.") --
    // Blackstar pawns carry the real vanilla FactionDef `Pirate`, verified by
    // reading that patch file, not guessed. Per this mod's own RoleTag.cs
    // comment, NamedHunter fires on the doc's own hook condition (any
    // Blackstar guest-status change) -- no extra "is this specifically a
    // named individual" detection is invented.
    [HarmonyPatch(typeof(GenGuest), nameof(GenGuest.PrisonerRelease))]
    public static class Patch_PrisonerReleased
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn p)
        {
            if (p?.Faction == null) return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            bool blackstar = p.Faction.def?.defName == "Pirate";
            RoleTag role = blackstar ? RoleTag.NamedHunter : RoleTag.Released;
            string summary = blackstar ? "a Blackstar hunter, released" : "released from our prison";

            roster.RecordEncounter(p, p.Faction, role, Find.TickManager.TicksGame, summary,
                // Canon (plot_mechanisms_wave.md §1.4): Blackstar honours a
                // fair release as a professional courtesy, everyone else's
                // reaction (owed mercy vs. resented capture) is the LLM's
                // call in Part 1 -- C# alone applies no sign here.
                grudgeDelta: blackstar ? -5 : 0,
                notabilityDelta: 10,
                pin: true);
        }
    }

    [HarmonyPatch(typeof(Pawn_GuestTracker), nameof(Pawn_GuestTracker.CapturedBy))]
    public static class Patch_NamedHunterCaptured
    {
        // Harmony's standard private-field convention: a postfix parameter
        // named `___<fieldName>` binds to that instance field on the patched
        // type's `__instance` (RimWorld/Pawn_GuestTracker.cs: `private Pawn pawn;`,
        // confirmed via RimSage's read_csharp_symbol field listing).
        [HarmonyPostfix]
        public static void Postfix(Faction by, Pawn ___pawn)
        {
            if (by != Faction.OfPlayer) return;

            Pawn pawn = ___pawn;
            if (pawn?.Faction == null || pawn.Faction.def?.defName != "Pirate") return;

            GameComponent_OldFriends roster = GameComponent_OldFriends.Instance;
            if (roster == null) return;

            roster.RecordEncounter(pawn, pawn.Faction, RoleTag.NamedHunter,
                Find.TickManager.TicksGame, "a Blackstar hunter, captured",
                grudgeDelta: 0, notabilityDelta: 15, pin: false);
        }
    }
}
