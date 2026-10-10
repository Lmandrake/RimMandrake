using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;
using RimMandrake.TitanicCreatures;

namespace RimMandrake.HugeThings
{
    // MOD_OPTIONS_RETROFIT_1 contract: one toggle per mechanic, tuning where a number is the experience, defaults = shipped behaviour,
    // all-off = vanilla. Owner 2026-10-07 (merge of Titanic Creatures into Huge Things): "Many configurations. Do you want giant
    // plants? Giant animals? Detailed behaviors. Etc." -> two master toggles, each with its detailed behaviours beneath. Every
    // field keeps the key it had in its old mod (Titanic Creatures' twelve came over unchanged). A behaviour is live through its
    // *Active property (HugeGates in the kernel): master AND its own toggle. "(restart)" marks what is read once at startup.
    public class RM_HugeThingsSettings : ModSettings
    {
        public const float MaxTrunkScale = 1.5f;

        // --- Giant plants -------------------------------------------------------------------------------------------------------
        public static bool giantPlantsEnabled = true;
        public static bool plantTrunkEnabled = true;
        public static bool plantSelectionEnabled = true;
        public static float plantTrunkScale = 1f;
        public static bool plantTrunkDamageEnabled = true;
        public static bool plantItemPushEnabled = true;

        // --- Giant animals ------------------------------------------------------------------------------------------------------
        public static bool giantAnimalsEnabled = true;
        public static bool pawnHitboxEnabled = true;
        public static float pawnHitboxScale = 1f;
        public static bool largePawnsFootprintEnabled = true;
        // LARGEPAWNS_BRIDGE_HARDENING_1 (B3.15, owed by TITANIC_CREATURES_MOD_1 card #3): Large Pawns' own wall-break off.
        public static bool largePawnsClearingOff = true;
        public static bool tierThresholdsCustom = false;
        public static float tierT1MinBodySize = 4f;
        public static float tierT2MinBodySize = 8f;
        public static float tierT3MinBodySize = 20f;
        public static bool wakeEnabled = true;
        public static float wakeCrushDamageMultiplier = 1f;
        public static float wakeFilthTrailChance = 0.35f;
        public static bool wakeRoofHolingEnabled = true;
        public static bool giantPlantSmashEnabled = true;
        public static int giantPlantSmashMinTier = 3;
        public static bool roofAvoidanceEnabled = true;
        public static bool yieldCurveEnabled = true;
        public static float yieldCurveMinFactor = 0.15f;
        public static bool corpseSiteEnabled = true;
        public static int corpseSiteHarvestMeatPerSession = 25;
        public static int corpseSiteHarvestLeatherPerSession = 10;
        public static float corpseSiteMeatSpoilagePerDay = 0.15f;
        public static float corpseSiteLeatherSpoilagePerDay = 0.08f;
        // 2500 ticks == 1 in-game hour (GenDate.TicksPerHour).
        public static float corpseSiteWorkHoursPerSession = 1f;

        // --- What is live (master AND detail) -----------------------------------------------------------------------------------
        public static bool PlantTrunkActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkEnabled);
        public static bool PlantSelectionActive => HugeGates.Plant(giantPlantsEnabled, plantSelectionEnabled);
        public static bool PlantTrunkDamageActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkDamageEnabled);
        public static bool PlantItemPushActive => HugeGates.Plant(giantPlantsEnabled, plantItemPushEnabled);
        public static bool PawnHitboxActive => HugeGates.Animal(giantAnimalsEnabled, pawnHitboxEnabled);
        public static bool LargePawnsFootprintActive => HugeGates.Animal(giantAnimalsEnabled, largePawnsFootprintEnabled);
        public static bool TierThresholdsCustomActive => HugeGates.Animal(giantAnimalsEnabled, tierThresholdsCustom);
        public static bool WakeActive => HugeGates.Animal(giantAnimalsEnabled, wakeEnabled);
        public static bool RoofHolingActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, wakeRoofHolingEnabled);
        public static bool GiantPlantSmashActive => HugeGates.Smash(giantPlantsEnabled, giantAnimalsEnabled, wakeEnabled, giantPlantSmashEnabled);
        public static bool RoofAvoidanceActive => HugeGates.Animal(giantAnimalsEnabled, roofAvoidanceEnabled);
        public static bool YieldCurveActive => HugeGates.Animal(giantAnimalsEnabled, yieldCurveEnabled);
        public static bool CorpseSiteActive => HugeGates.Animal(giantAnimalsEnabled, corpseSiteEnabled);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref giantPlantsEnabled, "giantPlantsEnabled", true);
            Scribe_Values.Look(ref plantTrunkEnabled, "plantTrunkEnabled", true);
            Scribe_Values.Look(ref plantSelectionEnabled, "plantSelectionEnabled", true);
            Scribe_Values.Look(ref plantTrunkScale, "plantTrunkScale", 1f);
            Scribe_Values.Look(ref plantTrunkDamageEnabled, "plantTrunkDamageEnabled", true);
            Scribe_Values.Look(ref plantItemPushEnabled, "plantItemPushEnabled", true);
            Scribe_Values.Look(ref giantAnimalsEnabled, "giantAnimalsEnabled", true);
            Scribe_Values.Look(ref pawnHitboxEnabled, "pawnHitboxEnabled", true);
            Scribe_Values.Look(ref pawnHitboxScale, "pawnHitboxScale", 1f);
            Scribe_Values.Look(ref largePawnsFootprintEnabled, "largePawnsFootprintEnabled", true);
            Scribe_Values.Look(ref largePawnsClearingOff, "largePawnsClearingOff", true);
            Scribe_Values.Look(ref tierThresholdsCustom, "tierThresholdsCustom", false);
            Scribe_Values.Look(ref tierT1MinBodySize, "tierT1MinBodySize", 4f);
            Scribe_Values.Look(ref tierT2MinBodySize, "tierT2MinBodySize", 8f);
            Scribe_Values.Look(ref tierT3MinBodySize, "tierT3MinBodySize", 20f);
            Scribe_Values.Look(ref wakeEnabled, "wakeEnabled", true);
            Scribe_Values.Look(ref wakeCrushDamageMultiplier, "wakeCrushDamageMultiplier", 1f);
            Scribe_Values.Look(ref wakeFilthTrailChance, "wakeFilthTrailChance", 0.35f);
            Scribe_Values.Look(ref wakeRoofHolingEnabled, "wakeRoofHolingEnabled", true);
            Scribe_Values.Look(ref giantPlantSmashEnabled, "giantPlantSmashEnabled", true);
            Scribe_Values.Look(ref giantPlantSmashMinTier, "giantPlantSmashMinTier", 3);
            Scribe_Values.Look(ref roofAvoidanceEnabled, "roofAvoidanceEnabled", true);
            Scribe_Values.Look(ref yieldCurveEnabled, "yieldCurveEnabled", true);
            Scribe_Values.Look(ref yieldCurveMinFactor, "yieldCurveMinFactor", 0.15f);
            Scribe_Values.Look(ref corpseSiteEnabled, "corpseSiteEnabled", true);
            Scribe_Values.Look(ref corpseSiteHarvestMeatPerSession, "corpseSiteHarvestMeatPerSession", 25);
            Scribe_Values.Look(ref corpseSiteHarvestLeatherPerSession, "corpseSiteHarvestLeatherPerSession", 10);
            Scribe_Values.Look(ref corpseSiteMeatSpoilagePerDay, "corpseSiteMeatSpoilagePerDay", 0.15f);
            Scribe_Values.Look(ref corpseSiteLeatherSpoilagePerDay, "corpseSiteLeatherSpoilagePerDay", 0.08f);
            Scribe_Values.Look(ref corpseSiteWorkHoursPerSession, "corpseSiteWorkHoursPerSession", 1f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit || Scribe.mode == LoadSaveMode.LoadingVars) Sanitize();
        }

        /// <summary>
        /// HUGETHINGS_SETTINGS_HARDENING_1 (B3.19 / C3.6 / D3.3): every numeric forced finite and into the range its slider states, on
        /// load and after every edit. A hand-edited or stale config must not outgrow the planning window (MaxKeys uses MaxTrunkScale),
        /// go NaN, or carry a zero/negative work time or batch size. An invalid custom tier ladder still falls back to the shipped one
        /// (TitanicTierUtility.Thresholds), each rung is only kept finite and in range here.
        /// </summary>
        public static void Sanitize()
        {
            plantTrunkScale = RM_TitanicKernel.SaneSetting(plantTrunkScale, 0.5f, MaxTrunkScale, 1f);
            pawnHitboxScale = RM_TitanicKernel.SaneSetting(pawnHitboxScale, 0.5f, MaxTrunkScale, 1f);
            tierT1MinBodySize = RM_TitanicKernel.SaneSetting(tierT1MinBodySize, 1f, 30f, 4f);
            tierT2MinBodySize = RM_TitanicKernel.SaneSetting(tierT2MinBodySize, 2f, 60f, 8f);
            tierT3MinBodySize = RM_TitanicKernel.SaneSetting(tierT3MinBodySize, 3f, 100f, 20f);
            wakeCrushDamageMultiplier = RM_TitanicKernel.SaneSetting(wakeCrushDamageMultiplier, 0.25f, 3f, 1f);
            wakeFilthTrailChance = RM_TitanicKernel.SaneSetting(wakeFilthTrailChance, 0f, 1f, 0.35f);
            giantPlantSmashMinTier = RM_TitanicKernel.SaneSetting(giantPlantSmashMinTier, 1, 3);
            yieldCurveMinFactor = RM_TitanicKernel.SaneSetting(yieldCurveMinFactor, 0.05f, 1f, 0.15f);
            corpseSiteHarvestMeatPerSession = RM_TitanicKernel.SaneSetting(corpseSiteHarvestMeatPerSession, 5, 100);
            corpseSiteHarvestLeatherPerSession = RM_TitanicKernel.SaneSetting(corpseSiteHarvestLeatherPerSession, 2, 50);
            corpseSiteWorkHoursPerSession = RM_TitanicKernel.SaneSetting(corpseSiteWorkHoursPerSession, 0.25f, 6f, 1f);
            corpseSiteMeatSpoilagePerDay = RM_TitanicKernel.SaneSetting(corpseSiteMeatSpoilagePerDay, 0.02f, 0.5f, 0.15f);
            corpseSiteLeatherSpoilagePerDay = RM_TitanicKernel.SaneSetting(corpseSiteLeatherSpoilagePerDay, 0.02f, 0.5f, 0.08f);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1600f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // HUGETHINGS_SETTINGS_HARDENING_1 (A2.7 / D1.5): every string is keyed in Languages/English/Keyed/RM_HugeThings.xml.
            if (Group(list, "Giant plants", RimMandrake.Shared.SettingScope.Now, new[] { "giantPlantsEnabled", "plantTrunkEnabled", "plantSelectionEnabled", "plantTrunkScale", "plantTrunkDamageEnabled", "plantItemPushEnabled" }))
            {
                list.CheckboxLabeled("RM_HugeThings_GiantPlantsEnabled".Translate(), ref giantPlantsEnabled, "RM_HugeThings_GiantPlantsEnabled_Desc".Translate());
                if (giantPlantsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_PlantTrunk".Translate(), ref plantTrunkEnabled, "RM_HugeThings_PlantTrunk_Desc".Translate());
                    if (plantTrunkEnabled)
                    {
                        list.Label("RM_HugeThings_PlantTrunkScale".Translate(plantTrunkScale.ToString("0.00")));
                        plantTrunkScale = list.Slider(plantTrunkScale, 0.5f, MaxTrunkScale);
                        list.CheckboxLabeled("RM_HugeThings_PlantTrunkDamage".Translate(), ref plantTrunkDamageEnabled, "RM_HugeThings_PlantTrunkDamage_Desc".Translate());
                        list.CheckboxLabeled("RM_HugeThings_PlantItemPush".Translate(), ref plantItemPushEnabled, "RM_HugeThings_PlantItemPush_Desc".Translate());
                    }
                    list.CheckboxLabeled("RM_HugeThings_PlantSelection".Translate(), ref plantSelectionEnabled, "RM_HugeThings_PlantSelection_Desc".Translate());
                }
                list.GapLine();
            }

            if (Group(list, "Giant animals: hitbox and roofs", RimMandrake.Shared.SettingScope.Now, new[] { "giantAnimalsEnabled", "pawnHitboxEnabled", "pawnHitboxScale", "roofAvoidanceEnabled" }))
            {
                list.CheckboxLabeled("RM_HugeThings_GiantAnimalsEnabled".Translate(), ref giantAnimalsEnabled, "RM_HugeThings_GiantAnimalsEnabled_Desc".Translate());
                if (giantAnimalsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_PawnHitbox".Translate(), ref pawnHitboxEnabled, "RM_HugeThings_PawnHitbox_Desc".Translate());
                    if (pawnHitboxEnabled)
                    {
                        list.Label("RM_HugeThings_PawnHitboxScale".Translate(pawnHitboxScale.ToString("0.00")));
                        pawnHitboxScale = list.Slider(pawnHitboxScale, 0.5f, MaxTrunkScale);
                    }
                    list.CheckboxLabeled("RM_HugeThings_RoofAvoid".Translate(), ref roofAvoidanceEnabled, "RM_HugeThings_RoofAvoid_Desc".Translate());
                }
                list.GapLine();
            }

            if (Group(list, "Large Pawns footprint and custom size tiers", RimMandrake.Shared.SettingScope.Now, new[] { "largePawnsFootprintEnabled", "largePawnsClearingOff", "tierThresholdsCustom", "tierT1MinBodySize", "tierT2MinBodySize", "tierT3MinBodySize" }, "[next game start]"))
            {
                if (giantAnimalsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_LargePawnsFootprint".Translate(), ref largePawnsFootprintEnabled, "RM_HugeThings_LargePawnsFootprint_Desc".Translate());
                    if (largePawnsFootprintEnabled)
                        list.CheckboxLabeled("RM_HugeThings_LargePawnsClearingOff".Translate(), ref largePawnsClearingOff, "RM_HugeThings_LargePawnsClearingOff_Desc".Translate());
                    list.CheckboxLabeled("RM_HugeThings_TierCustom".Translate(), ref tierThresholdsCustom, "RM_HugeThings_TierCustom_Desc".Translate());
                    if (tierThresholdsCustom)
                    {
                        list.Label("RM_HugeThings_TierT1".Translate(tierT1MinBodySize.ToString("0.0")));
                        tierT1MinBodySize = list.Slider(tierT1MinBodySize, 1f, 30f);
                        list.Label("RM_HugeThings_TierT2".Translate(tierT2MinBodySize.ToString("0.0")));
                        tierT2MinBodySize = list.Slider(tierT2MinBodySize, 2f, 60f);
                        list.Label("RM_HugeThings_TierT3".Translate(tierT3MinBodySize.ToString("0.0")));
                        tierT3MinBodySize = list.Slider(tierT3MinBodySize, 3f, 100f);
                        if (!RM_TitanicKernel.ThresholdsValid(tierT1MinBodySize, tierT2MinBodySize, tierT3MinBodySize))
                            list.Label("RM_HugeThings_TierInvalid".Translate());
                    }
                }
                else list.Label("Turn on giant animals to change these.");
                list.GapLine();
            }

            if (Group(list, "Wake and plant smashing", RimMandrake.Shared.SettingScope.Now, new[] { "wakeEnabled", "wakeCrushDamageMultiplier", "wakeFilthTrailChance", "wakeRoofHolingEnabled", "giantPlantSmashEnabled", "giantPlantSmashMinTier" }))
            {
                if (giantAnimalsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_Wake".Translate(), ref wakeEnabled, "RM_HugeThings_Wake_Desc".Translate());
                    if (wakeEnabled)
                    {
                        list.Label("RM_HugeThings_WakeDamage".Translate(wakeCrushDamageMultiplier.ToString("0.00")));
                        wakeCrushDamageMultiplier = list.Slider(wakeCrushDamageMultiplier, 0.25f, 3f);
                        // B4.6: the roll is made once per footprint cell entered, not once per step.
                        list.Label("RM_HugeThings_WakeRubble".Translate((wakeFilthTrailChance * 100f).ToString("0")));
                        wakeFilthTrailChance = list.Slider(wakeFilthTrailChance, 0f, 1f);
                        list.CheckboxLabeled("RM_HugeThings_WakeRoof".Translate(), ref wakeRoofHolingEnabled, "RM_HugeThings_WakeRoof_Desc".Translate());
                        list.CheckboxLabeled("RM_HugeThings_Smash".Translate(), ref giantPlantSmashEnabled, "RM_HugeThings_Smash_Desc".Translate());
                        if (giantPlantSmashEnabled)
                        {
                            list.Label("RM_HugeThings_SmashTier".Translate(giantPlantSmashMinTier.ToString()));
                            giantPlantSmashMinTier = Mathf.Clamp(Mathf.RoundToInt(list.Slider(giantPlantSmashMinTier, 1f, 3f)), 1, 3);
                        }
                    }
                }
                else list.Label("Turn on giant animals to change these.");
                list.GapLine();
            }

            if (Group(list, "Yield curve", RimMandrake.Shared.SettingScope.Now, new[] { "yieldCurveEnabled", "yieldCurveMinFactor" }))
            {
                if (giantAnimalsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_Yield".Translate(), ref yieldCurveEnabled, "RM_HugeThings_Yield_Desc".Translate());
                    if (yieldCurveEnabled)
                    {
                        list.Label("RM_HugeThings_YieldFloor".Translate((yieldCurveMinFactor * 100f).ToString("0")));
                        yieldCurveMinFactor = list.Slider(yieldCurveMinFactor, 0.05f, 1f);
                    }
                }
                else list.Label("Turn on giant animals to change these.");
                list.GapLine();
            }

            if (Group(list, "Titanic corpse sites", RimMandrake.Shared.SettingScope.Now, new[] { "corpseSiteEnabled", "corpseSiteHarvestMeatPerSession", "corpseSiteHarvestLeatherPerSession", "corpseSiteMeatSpoilagePerDay", "corpseSiteLeatherSpoilagePerDay", "corpseSiteWorkHoursPerSession" }))
            {
                if (giantAnimalsEnabled)
                {
                    list.CheckboxLabeled("RM_HugeThings_CorpseSite".Translate(), ref corpseSiteEnabled, "RM_HugeThings_CorpseSite_Desc".Translate());
                    if (corpseSiteEnabled)
                    {
                        list.Label("RM_HugeThings_CorpseMeat".Translate(corpseSiteHarvestMeatPerSession.ToString()));
                        corpseSiteHarvestMeatPerSession = (int)list.Slider(corpseSiteHarvestMeatPerSession, 5f, 100f);
                        list.Label("RM_HugeThings_CorpseLeather".Translate(corpseSiteHarvestLeatherPerSession.ToString()));
                        corpseSiteHarvestLeatherPerSession = (int)list.Slider(corpseSiteHarvestLeatherPerSession, 2f, 50f);
                        list.Label("RM_HugeThings_CorpseHours".Translate(corpseSiteWorkHoursPerSession.ToString("0.0")));
                        corpseSiteWorkHoursPerSession = list.Slider(corpseSiteWorkHoursPerSession, 0.25f, 6f);
                        list.Label("RM_HugeThings_CorpseMeatSpoil".Translate((corpseSiteMeatSpoilagePerDay * 100f).ToString("0")));
                        corpseSiteMeatSpoilagePerDay = list.Slider(corpseSiteMeatSpoilagePerDay, 0.02f, 0.5f);
                        list.Label("RM_HugeThings_CorpseLeatherSpoil".Translate((corpseSiteLeatherSpoilagePerDay * 100f).ToString("0")));
                        corpseSiteLeatherSpoilagePerDay = list.Slider(corpseSiteLeatherSpoilagePerDay, 0.02f, 0.5f);
                    }
                }
                else list.Label("Turn on giant animals to change these.");
                list.GapLine();
            }
            Sanitize();

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        
        

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_HugeThingsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_HugeThingsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the custom size tiers and the Large Pawns footprint and wall-break switches are latched once when the game starts (their own labels say restart), so they carry [next game start]; every other setting is read live by a tick, a job driver, a spawned building or the wake processor, none at map generation, so [now]. The giant-animals master is listed under the hitbox group but gates the other animal groups.</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_HugeThingsMod : Mod
    {
        public static RM_HugeThingsSettings settings;

        public RM_HugeThingsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_HugeThingsSettings>();
        }

        public override string SettingsCategory() => "RM_HugeThings_SettingsCategory".Translate();

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);

        public override void WriteSettings()
        {
            RM_HugeThingsSettings.Sanitize();
            base.WriteSettings();
            MapComponent_HugeFootprints.RefreshAllMaps();
        }
    }
}
