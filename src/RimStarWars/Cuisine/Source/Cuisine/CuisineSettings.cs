using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Cuisine
{
    // Star Wars Cuisine Mod Settings (design/RimStarWars/cold_storage_line_2026-10-26.md §6, Cuisine).
    // COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS: the carbon-freezing press switch and its carbon-shock chance. Cold
    // Storage reads both by name ("RimMandrake.StarWars.Cuisine.RSW_CuisineSettings:field", Defs/RSW_CarbonFreezing.xml),
    // so neither mod depends on the other: the switch hides the press and its bills, the chance is read at each thaw.
    public class RSW_CuisineSettings : ModSettings
    {
        public const float DefaultCarbonShockChance = 0.05f;

        public static bool carbonPressEnabled = true;
        public static float carbonShockChance = DefaultCarbonShockChance; // 0 - 0.5, per meal thawed

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref carbonPressEnabled, "carbonPressEnabled", true);
            Scribe_Values.Look(ref carbonShockChance, "carbonShockChance", DefaultCarbonShockChance);
            carbonShockChance = Mathf.Clamp(carbonShockChance, 0f, 0.5f);
        }

        public static void ResetToDefaults()
        {
            carbonPressEnabled = true;
            carbonShockChance = DefaultCarbonShockChance;
        }

        public static void Draw(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { maxOneColumn = true };
            list.Begin(inRect);
            Text.Font = GameFont.Medium;
            list.Label("RSW_Cuisine_SettingsCarbon".Translate());
            Text.Font = GameFont.Small;
            list.Label("RSW_Cuisine_SettingsNeedsColdStorage".Translate());
            list.CheckboxLabeled("RSW_Cuisine_SettingCarbonPress".Translate(), ref carbonPressEnabled, "RSW_Cuisine_SettingCarbonPressDesc".Translate());
            list.Label("RSW_Cuisine_SettingCarbonShock".Translate(carbonShockChance.ToStringPercent()), -1f, "RSW_Cuisine_SettingCarbonShockDesc".Translate());
            carbonShockChance = Mathf.Round(list.Slider(carbonShockChance, 0f, 0.5f) * 100f) / 100f;
            list.Gap();
            if (list.ButtonText("RSW_Cuisine_SettingsReset".Translate()))
            {
                ResetToDefaults();
            }
            list.End();
        }
    }

    public class RSW_CuisineMod : Mod
    {
        public RSW_CuisineMod(ModContentPack content) : base(content)
        {
            GetSettings<RSW_CuisineSettings>();
        }

        public override string SettingsCategory()
        {
            return "RSW_Cuisine_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            RSW_CuisineSettings.Draw(inRect);
        }
    }
}
