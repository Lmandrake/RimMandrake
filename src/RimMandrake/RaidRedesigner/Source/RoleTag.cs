namespace RimMandrake.RaidRedesigner
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §1.4's capture-hook table.
    // Append-only — an OldFriendEntry's RoleTag is scribed by name (LookMode.Value
    // on an enum serializes the NAME, not the ordinal, so reordering this list is
    // safe, unlike Ninefold's God enum). Still: never remove or rename a tag once
    // a save can hold it.
    public enum RoleTag
    {
        FledRaider,        // Pawn.ExitMap postfix: a hostile-faction pawn survived and left the map
        Captain,           // same seam, plus Faction.leader == pawn (or our own captain flag)
        EscapedPrisoner,   // GuestUtility.Notify_PrisonerEscaped postfix
        Released,          // Pawn_GuestTracker.SetGuestStatus(..., GuestStatus.Released) postfix
        BetrayedTrader,    // mandrake.rm.property's PropertyEngine.Fire postfix: an unauthorized
                           // Take/Strip against a non-player-faction pawn's claim
        Kidnapper,         // the pawn who performed a successful kidnap of one of ours
        WokenAncient,      // STUB — see Patch_WokenAncient_STUB.cs. No real signal wired yet.
        NamedHunter,       // a Blackstar (vanilla `Pirate` FactionDef, reskinned) pawn whose guest
                           // status changed (captured or released) — doc's own hook condition,
                           // no extra "is this pawn named" detection invented.
    }
}
