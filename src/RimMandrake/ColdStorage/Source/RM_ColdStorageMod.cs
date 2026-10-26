using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.ColdStorage
{
    // Mod Settings for Cold Storage (design/RimStarWars/cold_storage_line_2026-10-26.md §6).
    // Defaults are the shipped behaviour. With every switch off, cooling units are plain shelves, stasis units are plain
    // shelves, sealed goods keep without aging, and every station stays buildable: the game degrades to vanilla storage.
    // The wall-unit switches (blocks light, airtight) arrive with the wall unit itself (COLD_STORAGE_COOLERS_BUILD_RSW_LADDER).
    public class RM_ColdStorageSettings : ModSettings
    {
        // Engine
        public static bool chillEnabled = true;
        public static bool stasisEnabled = true;
        public static bool sealAgingEnabled = true;

        // Rates
        public static float powerDrawMultiplier = 1f;     // 0.25 - 3
        public static float insulationMultiplier = 1f;    // 0.25 - 4; higher = an unpowered unit warms slower
        public static float agingTimeMultiplier = 1f;     // 0.25 - 4
        public static float sealFailureMultiplier = 1f;   // 0 - 3; 0 = sealed goods never ruin

        // Methods: off hides the station and its recipes
        public static bool methodResin = true;
        public static bool methodSandDry = true;
        public static bool methodBrine = true;
        public static bool methodEvaporativeCrock = true;

        // Behaviour
        public static bool unitsActAsHoppers = true;
        public static bool showClimateReadout = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref chillEnabled, "chillEnabled", true);
            Scribe_Values.Look(ref stasisEnabled, "stasisEnabled", true);
            Scribe_Values.Look(ref sealAgingEnabled, "sealAgingEnabled", true);
            Scribe_Values.Look(ref powerDrawMultiplier, "powerDrawMultiplier", 1f);
            Scribe_Values.Look(ref insulationMultiplier, "insulationMultiplier", 1f);
            Scribe_Values.Look(ref agingTimeMultiplier, "agingTimeMultiplier", 1f);
            Scribe_Values.Look(ref sealFailureMultiplier, "sealFailureMultiplier", 1f);
            Scribe_Values.Look(ref methodResin, "methodResin", true);
            Scribe_Values.Look(ref methodSandDry, "methodSandDry", true);
            Scribe_Values.Look(ref methodBrine, "methodBrine", true);
            Scribe_Values.Look(ref methodEvaporativeCrock, "methodEvaporativeCrock", true);
            Scribe_Values.Look(ref unitsActAsHoppers, "unitsActAsHoppers", true);
            Scribe_Values.Look(ref showClimateReadout, "showClimateReadout", true);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        public static void ResetToDefaults()
        {
            chillEnabled = true;
            stasisEnabled = true;
            sealAgingEnabled = true;
            powerDrawMultiplier = 1f;
            insulationMultiplier = 1f;
            agingTimeMultiplier = 1f;
            sealFailureMultiplier = 1f;
            methodResin = true;
            methodSandDry = true;
            methodBrine = true;
            methodEvaporativeCrock = true;
            unitsActAsHoppers = true;
            showClimateReadout = true;
        }

        /// <summary>Whether a gated station or recipe is available under the current settings.</summary>
        public static bool GateOpen(ColdStorageGate gate)
        {
            switch (gate)
            {
                case ColdStorageGate.Resin: return methodResin;
                case ColdStorageGate.SandDry: return methodSandDry;
                case ColdStorageGate.Brine: return methodBrine;
                case ColdStorageGate.EvaporativeCrock: return methodEvaporativeCrock;
                default: return true;
            }
        }

        private static Vector2 scroll;
        private static float viewHeight = 900f;

        private static void Slider(Listing_Standard list, string key, ref float value, float min, float max)
        {
            list.Label(key.Translate(value.ToString("0.00")));
            value = Mathf.Round(list.Slider(value, min, max) * 20f) / 20f;
        }

        public static void Draw(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            // maxOneColumn is load-bearing: without it the overflow wraps into a hidden second column.
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);

            Text.Font = GameFont.Medium;
            list.Label("RM_ColdStorage_SettingsEngine".Translate());
            Text.Font = GameFont.Small;
            list.Label("RM_ColdStorage_SettingsAppliesNow".Translate());
            list.CheckboxLabeled("RM_ColdStorage_SettingChill".Translate(), ref chillEnabled, "RM_ColdStorage_SettingChillDesc".Translate());
            list.CheckboxLabeled("RM_ColdStorage_SettingStasis".Translate(), ref stasisEnabled, "RM_ColdStorage_SettingStasisDesc".Translate());
            list.CheckboxLabeled("RM_ColdStorage_SettingAging".Translate(), ref sealAgingEnabled, "RM_ColdStorage_SettingAgingDesc".Translate());
            list.GapLine();

            Text.Font = GameFont.Medium;
            list.Label("RM_ColdStorage_SettingsRates".Translate());
            Text.Font = GameFont.Small;
            Slider(list, "RM_ColdStorage_SettingPower", ref powerDrawMultiplier, 0.25f, 3f);
            Slider(list, "RM_ColdStorage_SettingInsulation", ref insulationMultiplier, 0.25f, 4f);
            Slider(list, "RM_ColdStorage_SettingAgingTime", ref agingTimeMultiplier, 0.25f, 4f);
            Slider(list, "RM_ColdStorage_SettingFailure", ref sealFailureMultiplier, 0f, 3f);
            list.GapLine();

            Text.Font = GameFont.Medium;
            list.Label("RM_ColdStorage_SettingsMethods".Translate());
            Text.Font = GameFont.Small;
            list.Label("RM_ColdStorage_SettingsMethodsNote".Translate());
            list.CheckboxLabeled("RM_ColdStorage_SettingResin".Translate(), ref methodResin);
            list.CheckboxLabeled("RM_ColdStorage_SettingSandDry".Translate(), ref methodSandDry);
            list.CheckboxLabeled("RM_ColdStorage_SettingBrine".Translate(), ref methodBrine);
            list.CheckboxLabeled("RM_ColdStorage_SettingCrock".Translate(), ref methodEvaporativeCrock);
            list.GapLine();

            Text.Font = GameFont.Medium;
            list.Label("RM_ColdStorage_SettingsBehaviour".Translate());
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("RM_ColdStorage_SettingHopper".Translate(), ref unitsActAsHoppers, "RM_ColdStorage_SettingHopperDesc".Translate());
            list.CheckboxLabeled("RM_ColdStorage_SettingReadout".Translate(), ref showClimateReadout);
            list.GapLine();

            if (list.ButtonText("RM_ColdStorage_SettingsReset".Translate()))
            {
                ResetToDefaults();
            }
            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_ColdStorageMod : Mod
    {
        public static RM_ColdStorageSettings settings;

        public RM_ColdStorageMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_ColdStorageSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.coldstorage"), typeof(RM_ColdStorageMod).Assembly, "RimMandrake.ColdStorage");
        }

        public override string SettingsCategory()
        {
            return "RM_ColdStorage_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            RM_ColdStorageSettings.Draw(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            ColdStorageStartup.ApplyHopperFlags();
        }
    }
}
