namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md Part 2, the battle
    // recorder's four classifications.
    public enum BattleOutcome
    {
        Repelled,  // >= 60% of the raiding pawns dead/downed
        Routed,    // survivors exited under their own power - feeds the roster
        Stalemate, // timeout / steal-and-leave / ambiguous end
        Lost,      // colonist deaths/kidnaps >= 1 and raiders left largely intact, by choice
    }
}
