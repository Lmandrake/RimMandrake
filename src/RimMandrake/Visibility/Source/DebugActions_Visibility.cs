using LudeonTK;
using Verse;

namespace RimMandrake.Visibility
{
    /// <summary>
    /// COLONY_VISIBILITY_BUILD_1's own test harness. Nothing else sets
    /// shipVisibility directly on a live game -- every real mutator
    /// (Adjust/ResetOnLaunch/ApplyTileMemoryOnArrival) is event-driven, and
    /// most of those events (the design doc's raise/lower hooks) are not
    /// wired to anything yet (see that item's own "not done" list). Without
    /// a way to set the dial, the threat-point Prefix could only ever be
    /// observed at its default (10, Hidden band) -- this lets the live check
    /// actually sweep the ruled Annex A curve's anchor points.
    /// </summary>
    public static class DebugActions_Visibility
    {
        private const string Cat = "RimMandrake.Visibility";

        [DebugAction(Cat, "Set Colony Visibility (dev)", allowedGameStates = AllowedGameStates.Playing)]
        private static void SetVisibility()
        {
            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            if (component == null)
            {
                Log.Error("[RimMandrake.Visibility] no GameComponent_ColonyVisibility on the current game.");
                return;
            }
            float[] presets = { 0f, 25f, 50f, 75f, 100f };
            Dialog_DebugOptionListLister.ShowSimpleDebugMenu(presets, v => v + " (" + GameComponent_ColonyVisibility.BandFor(v) + ")",
                delegate (float v)
                {
                    float before = component.shipVisibility;
                    component.shipVisibility = v;
                    Log.Message("[RimMandrake.Visibility] shipVisibility set " + before + " -> " + v
                        + " (" + component.Band + "), ThreatFactor=" + GameComponent_ColonyVisibility.ThreatFactor(v));
                });
        }
    }
}
