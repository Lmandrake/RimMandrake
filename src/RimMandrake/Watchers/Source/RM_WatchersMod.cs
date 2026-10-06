using UnityEngine;
using Verse;

namespace RimMandrake.Watchers
{
    // WATCHER_CREATURES_MOD_1, design §6. Defaults = shipped behaviour. All off = the members are
    // ordinary small animals that never hide. The readable sign has no toggle: it is the "no animal
    // vanishes" rule, not a feature. Scroll view per the Webwork fix (cfdba9344): maxOneColumn is
    // load-bearing, or the overflow wraps into a hidden second column and the view never grows.
    public class RM_WatchersSettings : ModSettings
    {
        public static bool watchersEnabled = true;
        public static bool hideAndFlinch = true;
        public static bool turnToFace = true;
        public static bool stayOnMedium = true;
        public static bool geophone = true;
        public static bool flushMarksHunt = true;
        public static float flinchRadiusScale = 1f;   // PROVISIONAL range 0.5-2 (design §6 gives 3-12 cells around 6)
        public static float emergeDelayScale = 1f;    // PROVISIONAL range 0.25-3 (design §6: "1-3 h, slider")
        public static int maxActivePerMap = 40;       // design §6 default; PROVISIONAL range 5-200

        public static bool HideActive => watchersEnabled && hideAndFlinch;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref watchersEnabled, "watchersEnabled", true);
            Scribe_Values.Look(ref hideAndFlinch, "hideAndFlinch", true);
            Scribe_Values.Look(ref turnToFace, "turnToFace", true);
            Scribe_Values.Look(ref stayOnMedium, "stayOnMedium", true);
            Scribe_Values.Look(ref geophone, "geophone", true);
            Scribe_Values.Look(ref flushMarksHunt, "flushMarksHunt", true);
            Scribe_Values.Look(ref flinchRadiusScale, "flinchRadiusScale", 1f);
            Scribe_Values.Look(ref emergeDelayScale, "emergeDelayScale", 1f);
            Scribe_Values.Look(ref maxActivePerMap, "maxActivePerMap", 40);
        }

        private Vector2 scrollPosition;
        private float lastContentHeight;

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(lastContentHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            var list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);

            list.CheckboxLabeled("RM_Watchers_Setting_Enabled".Translate(), ref watchersEnabled,
                "RM_Watchers_Setting_Enabled_Tip".Translate());
            if (watchersEnabled)
            {
                list.GapLine();
                list.CheckboxLabeled("RM_Watchers_Setting_Hide".Translate(), ref hideAndFlinch,
                    "RM_Watchers_Setting_Hide_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Face".Translate(), ref turnToFace,
                    "RM_Watchers_Setting_Face_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Medium".Translate(), ref stayOnMedium,
                    "RM_Watchers_Setting_Medium_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Geophone".Translate(), ref geophone,
                    "RM_Watchers_Setting_Geophone_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_FlushHunt".Translate(), ref flushMarksHunt,
                    "RM_Watchers_Setting_FlushHunt_Tip".Translate());
                list.GapLine();
                list.Label("RM_Watchers_Setting_FlinchRadius".Translate(flinchRadiusScale.ToStringPercent()));
                flinchRadiusScale = Mathf.Round(list.Slider(flinchRadiusScale, 0.5f, 2f) * 20f) / 20f;
                list.Label("RM_Watchers_Setting_EmergeDelay".Translate(emergeDelayScale.ToStringPercent()));
                emergeDelayScale = Mathf.Round(list.Slider(emergeDelayScale, 0.25f, 3f) * 20f) / 20f;
                list.Label("RM_Watchers_Setting_MaxActive".Translate(maxActivePerMap));
                maxActivePerMap = Mathf.RoundToInt(list.Slider(maxActivePerMap, 5f, 200f));
            }

            lastContentHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_WatchersMod : Mod
    {
        public static RM_WatchersSettings settings;

        public RM_WatchersMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WatchersSettings>();
        }

        public override string SettingsCategory()
        {
            return "RM_Watchers_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
