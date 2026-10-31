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

        // COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES (§6): canon dishes need their preserved ingredient (blast-chilled
        // cream for the carbonite pie). Off: a fresh-ingredient variant of each such bill appears too (Cold Storage
        // reads this by name with settingInverted, so it applies at once).
        public static bool preservationRequired = true;

        // §5/§6: Vanilla Cooking Expanded's canning machine and cans read as a ration sealer and sealed ration tins.
        // Labels are patched at load (PatchOperation_CuisineSetting), so a change applies after a restart.
        public static bool vceReskinEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref carbonPressEnabled, "carbonPressEnabled", true);
            Scribe_Values.Look(ref carbonShockChance, "carbonShockChance", DefaultCarbonShockChance);
            Scribe_Values.Look(ref preservationRequired, "preservationRequired", true);
            Scribe_Values.Look(ref vceReskinEnabled, "vceReskinEnabled", true);
            carbonShockChance = Mathf.Clamp(carbonShockChance, 0f, 0.5f);
        }

        public static void ResetToDefaults()
        {
            carbonPressEnabled = true;
            carbonShockChance = DefaultCarbonShockChance;
            preservationRequired = true;
            vceReskinEnabled = true;
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
            Text.Font = GameFont.Medium;
            list.Label("RSW_Cuisine_SettingsPreserved".Translate());
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("RSW_Cuisine_SettingPreservationRequired".Translate(), ref preservationRequired, "RSW_Cuisine_SettingPreservationRequiredDesc".Translate());
            list.CheckboxLabeled("RSW_Cuisine_SettingVceReskin".Translate(), ref vceReskinEnabled, "RSW_Cuisine_SettingVceReskinDesc".Translate());
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
