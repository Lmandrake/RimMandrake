using UnityEngine;
using Verse;

namespace RimMandrake.RustChrome
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RustChrome.
    //
    // This mod has exactly one mechanic: a one-time (well, live-togglable)
    // reflection recolour of a handful of Widgets/InspectPaneUtility UI
    // fields. There is no rate/chance/threshold to tune — the only honest
    // control is on/off, restoring the game's own stock colours when off.
    public class RustChromeSettings : ModSettings
    {
        public bool themeEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            bool before = themeEnabled;
            list.CheckboxLabeled("Rust & Chrome UI theme", ref themeEnabled,
                "Recolours a handful of menu/window backgrounds to a rusted brown-and-chrome "
              + "palette. Off restores the game's own stock colours immediately.");
            if (themeEnabled != before)
            {
                RustChromeColors.Apply(themeEnabled);
            }

            list.End();
        }
    }

    public class RustChromeMod : Mod
    {
        public static RustChromeSettings settings;

        public RustChromeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RustChromeSettings>();
        }

        public override string SettingsCategory()
        {
            return "Rust & Chrome";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
