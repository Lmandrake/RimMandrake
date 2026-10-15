using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// GPT pre-release 2026-10-15 (C14, B16, D11; lesson 20261015T025544Z: a static table keyed by things or maps outlives
    /// the save). RimWorld builds one of every GameComponent for each game it starts or loads, so this constructor runs at
    /// exactly the moment the previous game's objects stop meaning anything: it empties the session-wide tables that hold
    /// them. No state of its own, and kept out of the save by Patch_Game_ExposeSmallComponents_SkipSessionReset below.
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

    /// <summary>
    /// Keeps GssSessionReset out of the save (SL2, GSS_SESSION_RESET_REPAIR_SNEAKS_INTO_SAVES; L1 2026-10-15 found
    /// &lt;li Class="RimMandrake.GimmeSomeSlack.GssSessionReset"/&gt; in every save). Game.ExposeSmallComponents writes
    /// every GameComponent in Game.components; while SAVING the reset component is dropped from that list for good -- it
    /// holds nothing and has already done its one job in its constructor. On LOADING nothing is touched: FillComponents
    /// (LoadingVars only) creates a fresh one, which is the reset. A save written between e42ac437f0 and this fix still
    /// names the class; it loads without error because the class still exists, and its next save drops it.
    /// </summary>
    [HarmonyLib.HarmonyPatch(typeof(Game), "ExposeSmallComponents")]
    internal static class Patch_Game_ExposeSmallComponents_SkipSessionReset
    {
        public static int dropped;

        private static void Prefix(Game __instance)
        {
            if (Scribe.mode != LoadSaveMode.Saving || __instance?.components == null) return;
            dropped += __instance.components.RemoveAll(c => c is GssSessionReset);
        }
    }
}
