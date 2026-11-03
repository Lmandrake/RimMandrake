using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Patches
{
    /// <summary>
    /// STARWARS_JUNK_RESKIN_1 — Mod Settings for RimStarWars Patches (owner 2026-09-12: every mod ships superb settings;
    /// MOD_OPTIONS_RETROFIT_1: one toggle, "Star Wars junk on/off"). The default is the shipped behaviour; off leaves
    /// vanilla's ancient junk exactly as Core and the DLC wrote it. Nothing here affects worldgen: the toggle changes
    /// only how the junk looks and is named, never where or how much of it is placed.
    /// </summary>
    public class RSW_StarWarsPatchesSettings : ModSettings
    {
        public const bool DefaultJunkReskin = true;

        // --- applied while the defs load (next game start) ---
        public static bool junkReskin = DefaultJunkReskin;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref junkReskin, "junkReskin", DefaultJunkReskin);
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 300f;
        private static string searchQuery = "";

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            const string title = "Star Wars junk";
            const string label = "Reskin vanilla ancient junk as Star Wars wrecks";
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (!searching || RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches(label, searchQuery))
            {
                Text.Font = GameFont.Medium;
                list.Label(title);
                Text.Font = GameFont.Small;
                list.Label("[restart] changes take effect the next time the game starts");
                RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => junkReskin = DefaultJunkReskin);
                list.CheckboxLabeled(label, ref junkReskin,
                    "On: the ancient cars, trucks, tanks, warwalker parts, wheels, engines, dropships and mega-cannon pieces "
                    + "scattered on maps are drawn as many different Star Wars wrecks (landspeeders, walkers, starfighters, "
                    + "droids) and carry matching names and descriptions. Off: they look and read exactly as vanilla. "
                    + "Size, hit points, passability and salvage are identical either way. Takes effect the next time the game starts.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_StarWarsPatchesMod : Mod
    {
        public static RSW_StarWarsPatchesSettings settings;

        public RSW_StarWarsPatchesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_StarWarsPatchesSettings>();
        }

        public override string SettingsCategory()
        {
            return "RimStarWars Patches";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
