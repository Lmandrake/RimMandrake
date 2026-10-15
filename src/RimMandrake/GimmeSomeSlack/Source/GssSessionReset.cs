using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// GPT pre-release 2026-10-15 (C14, B16, D11; lesson 20261015T025544Z: a static table keyed by things or maps outlives
    /// the save). RimWorld builds one of every GameComponent for each game it starts or loads, so this constructor runs at
    /// exactly the moment the previous game's objects stop meaning anything: it empties the session-wide tables that hold
    /// them. No state of its own and nothing saved.
    /// </summary>
    public class GssSessionReset : GameComponent
    {
        public static int resets;

        public GssSessionReset(Game game)
        {
            resets++;
            Aerial.TapRegistry.Clear();                         // C14: the tap ledger held the old game's transmitters
            SectionLayer_RM_MessyCords.PrintedStatic.Clear();   // B16: the old maps' section keys and strand names
            Aerial.StylePicker.ClearPicks();                    // D11: a new game starts on the default look, not the
            Aerial.ConduitStylePicker.ClearPicks();             //      last colony's picks
            GimmeSomeSlackProbe.request = "";                  // B22: a probe request queued in the last game never fires
            Aerial.AerialProbe.request = "";                   //      in this one (thing ids repeat across loads)
            Aerial.CompAerialAnchor.debugSkipReseed = false;   // C15: an interrupted negative control never leaks into a game
        }
    }
}
