namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §2.1's eight rules do not
    // share one trigger shape. BattleOutcome and (2026-09-09)
    // MentalBreakNearBattle are the kinds AftermathRuleRunner evaluates
    // (rules 1-3 off MapComponent_BattleRecorder.Close, rule 6 off
    // Patch_MentalBreakNearBattle's postfix); the other three names exist so
    // rule DATA for 4/5/7/8 can be shipped now and wired to a real engine
    // later without a defName/field rename. See this mod's own item-file note
    // for exactly which engine piece each still needs.
    public enum AftermathTriggerKind
    {
        BattleOutcome,          // rules 1, 2, 3 - WIRED
        PrisonerHeldDuration,   // rule 4 - NOT WIRED (needs Pawn_GuestTracker capture-duration polling)
        GodBandCrossed,         // rule 5 - NOT WIRED (needs a Ninefold band-change signal; Ninefold has no such event yet)
        MentalBreakNearBattle,  // rule 6 - WIRED (Patch_MentalBreakNearBattle.cs + NinefoldBandBridge.cs, 2026-09-09)
        RootedClockQuadrum,     // rule 7 - NOT WIRED (needs read access to Ninefold's private Ta'Baa lastLaunchTick)
        TakingEventWitnessed,   // rule 8 - NOT WIRED (needs a Property-fabric postfix keyed to the Hutt faction specifically)
    }
}
