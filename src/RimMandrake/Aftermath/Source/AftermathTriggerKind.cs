namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §2.1's eight rules do not
    // share one trigger shape. BattleOutcome is the only kind
    // AftermathRuleRunner currently evaluates (rules 1-3, all off the same
    // MapComponent_BattleRecorder.Close event); the other four names exist so
    // rule DATA for 4/5/6/7/8 can be shipped now and wired to a real engine
    // later without a defName/field rename. See this mod's own item-file note
    // for exactly which engine piece each still needs.
    public enum AftermathTriggerKind
    {
        BattleOutcome,          // rules 1, 2, 3 - WIRED
        PrisonerHeldDuration,   // rule 4 - NOT WIRED (needs Pawn_GuestTracker capture-duration polling)
        GodBandCrossed,         // rule 5 - NOT WIRED (needs a Ninefold band-change signal; Ninefold has no such event yet)
        MentalBreakNearBattle,  // rule 6 - NOT WIRED (needs break-tick vs battle-close-tick correlation)
        RootedClockQuadrum,     // rule 7 - NOT WIRED (needs read access to Ninefold's private Ta'Baa lastLaunchTick)
        TakingEventWitnessed,   // rule 8 - NOT WIRED (needs a Property-fabric postfix keyed to the Hutt faction specifically)
    }
}
