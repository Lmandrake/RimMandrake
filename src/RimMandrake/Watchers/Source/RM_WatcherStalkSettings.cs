using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>The Rust Cathedral Watcher's own Mod Settings (pitch §5.6; the 2026-09-12 every-mod-ships-settings rule). Saved and drawn
    /// inside RM_WatchersSettings (one ModSettings per Mod), as its own section. Defaults = shipped behaviour.
    ///   watcherEnabled  off: the Watcher never raises its stalk; it is a small machine that crawls the deck seams and nothing more.
    ///   stalkAnimation  off: no rise/retract animation; the stalk is simply up or down (the hide still waits for the retract, now 0 ticks).
    ///   smoothTracking  off: the head snaps to the nearest of its eight directions instead of easing round.</summary>
    public static class RM_WatcherStalkSettings
    {
        public static bool watcherEnabled = true;
        public static bool stalkAnimation = true;
        public static bool smoothTracking = true;

        public static void Expose()
        {
            Scribe_Values.Look(ref watcherEnabled, "watcherStalkEnabled", true);
            Scribe_Values.Look(ref stalkAnimation, "watcherStalkAnimation", true);
            Scribe_Values.Look(ref smoothTracking, "watcherStalkSmoothTracking", true);
        }

        public static void Draw(Listing_Standard list)
        {
            list.GapLine();
            list.Label("RM_WatcherStalk_Setting_Header".Translate());
            list.CheckboxLabeled("RM_WatcherStalk_Setting_Enabled".Translate(), ref watcherEnabled, "RM_WatcherStalk_Setting_Enabled_Tip".Translate());
            if (watcherEnabled)
            {
                list.CheckboxLabeled("RM_WatcherStalk_Setting_Animation".Translate(), ref stalkAnimation,
                    "RM_WatcherStalk_Setting_Animation_Tip".Translate());
                list.CheckboxLabeled("RM_WatcherStalk_Setting_Smooth".Translate(), ref smoothTracking,
                    "RM_WatcherStalk_Setting_Smooth_Tip".Translate());
            }
        }
    }
}
