using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: on/off per major
    // mechanic, tuning where a number is the experience, defaults = shipped
    // behaviour, all-off degrades gracefully. House style: static fields read
    // from everywhere (the Harmony postfixes run far from any Mod instance),
    // written only through this window and ExposeData — same as
    // FloodedCanyon's and PlantGrowth's settings.
    //
    // Every number below that is not a ruling is 🄸 INVENTED and says so.
    // ════════════════════════════════════════════════════════════════════
    public class ExplosiveGrowthSettings : ModSettings
    {
        // Master switch. Off: no soak forms, nothing charges, every patch no-ops.
        public static bool enabled = true;

        // ── the soak ─────────────────────────────────────────────────────
        // Design doc §0 🄸: the soak multiplier stacks multiplicatively on the
        // ambient band (x4 → ~x40 vanilla-relative, "a 3-day plant finishes in
        // under two in-game hours").
        public static float soakMultiplier = 10f;
        // Default soak length for a source that does not say (§1: "hours to a
        // day"). 🄸 INVENTED: a day.
        public static float defaultSoakHours = 24f;
        // R-G5's under-a-day clause.
        public static float minGrowDaysToSoak = 1f;
        // 🄸 INVENTED generalisation of the fungal carve-out to the RM tier.
        public static bool cavePlantsNeverSoak = true;

        public static bool irrigationSoakEnabled = true;
        public static bool gradientSurgeSoakEnabled = true;
        public static bool weatherSoakEnabled = true;

        // ── the charge ──────────────────────────────────────────────────
        // 🄸 INVENTED: six in-game hours from full growth to the top; the tell
        // ladder's tremble lands ~1.8 h before it, the creak ~0.9 h.
        public static float chargeHours = 6f;
        // 🄸 INVENTED: overgrown up to 2x natural scale (design doc §2 "~2×").
        public static float maxOvergrowthScale = 2f;
        // Staged re-print cadence (design doc §5 option 1). The perf gate
        // tunes this; 250 = vanilla's rare-tick cadence.
        public static int reprintIntervalTicks = 250;
        public static bool hueShiftEnabled = true;
        public static bool tellSoundsEnabled = true;
        public static bool groundTellEnabled = true;

        // ── the tops ────────────────────────────────────────────────────
        // A disabled variant falls back to the Churn (the default top); a
        // disabled Churn makes the plant simply relax back to normal size.
        public static bool churnEnabled = true;
        public static bool burstEnabled = true;
        public static bool burstHurtsPawns = true;
        public static bool tinderEnabled = true;
        public static bool slimeEnabled = true;
        public static bool ruptureEnabled = true;
        // 🄸 INVENTED: per rare-tick chance a pawn in a rupture cloud without
        // full vacuum protection gains one mutation.
        public static float ruptureMutationChance = 0.08f;
        public static bool flushEnabled = true;

        // ── the player verbs ────────────────────────────────────────────
        // HARVEST: a charged plant harvested before the top yields swollen
        // produce (§4). SURVIVE: cutting defuses it, and "the last swing is a
        // gamble" — ruling 7 says trigger/weaponize stay unreliable, so this
        // gamble is never tuned toward safety by default.
        public static bool harvestJackpotEnabled = true;
        public static bool lastSwingGambleEnabled = true;
        // M10 / M2 (Greentide kit): grazing and the dry-air blower suppress
        // encroachment.
        public static bool suppressionEnabled = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref soakMultiplier, "soakMultiplier", 10f);
            Scribe_Values.Look(ref defaultSoakHours, "defaultSoakHours", 24f);
            Scribe_Values.Look(ref minGrowDaysToSoak, "minGrowDaysToSoak", 1f);
            Scribe_Values.Look(ref cavePlantsNeverSoak, "cavePlantsNeverSoak", true);
            Scribe_Values.Look(ref irrigationSoakEnabled, "irrigationSoakEnabled", true);
            Scribe_Values.Look(ref gradientSurgeSoakEnabled, "gradientSurgeSoakEnabled", true);
            Scribe_Values.Look(ref weatherSoakEnabled, "weatherSoakEnabled", true);
            Scribe_Values.Look(ref chargeHours, "chargeHours", 6f);
            Scribe_Values.Look(ref maxOvergrowthScale, "maxOvergrowthScale", 2f);
            Scribe_Values.Look(ref reprintIntervalTicks, "reprintIntervalTicks", 250);
            Scribe_Values.Look(ref hueShiftEnabled, "hueShiftEnabled", true);
            Scribe_Values.Look(ref tellSoundsEnabled, "tellSoundsEnabled", true);
            Scribe_Values.Look(ref groundTellEnabled, "groundTellEnabled", true);
            Scribe_Values.Look(ref churnEnabled, "churnEnabled", true);
            Scribe_Values.Look(ref burstEnabled, "burstEnabled", true);
            Scribe_Values.Look(ref burstHurtsPawns, "burstHurtsPawns", true);
            Scribe_Values.Look(ref tinderEnabled, "tinderEnabled", true);
            Scribe_Values.Look(ref slimeEnabled, "slimeEnabled", true);
            Scribe_Values.Look(ref ruptureEnabled, "ruptureEnabled", true);
            Scribe_Values.Look(ref ruptureMutationChance, "ruptureMutationChance", 0.08f);
            Scribe_Values.Look(ref flushEnabled, "flushEnabled", true);
            Scribe_Values.Look(ref harvestJackpotEnabled, "harvestJackpotEnabled", true);
            Scribe_Values.Look(ref lastSwingGambleEnabled, "lastSwingGambleEnabled", true);
            Scribe_Values.Look(ref suppressionEnabled, "suppressionEnabled", true);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 scroll;
        private static float settingsViewHeight = 1600f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Mod switch", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Explosive plant growth enabled", ref enabled,
                    "Off: water never soaks a plant, nothing swells, nothing reaches a top. Plants grow at whatever ambient rate the rest of your mod list gives them.");
                list.GapLine();
            }

            if (Group(list, "The soak", RimMandrake.Shared.SettingScope.Now, new[] { "soakMultiplier", "irrigationSoakEnabled", "gradientSurgeSoakEnabled", "weatherSoakEnabled" }))
            {
                list.Label("Soaked growth: x" + soakMultiplier.ToString("0.0") + " on top of the plant's normal rate");
                soakMultiplier = list.Slider(soakMultiplier, 1f, 30f);
                list.CheckboxLabeled("Irrigation soaks: water-filled dug channels soak the ground beside them", ref irrigationSoakEnabled,
                    "Needs RimMandrake: FlowWorks. Only DUG channels count — rivers and lakes never soak.");
                list.CheckboxLabeled("Salt-line surges soak the fresh side", ref gradientSurgeSoakEnabled,
                    "Needs the gradient-axis surge (RimMandrake: Environmental Hazards). The surge line decides which half blooms.");
                list.CheckboxLabeled("Soaking rains soak open ground", ref weatherSoakEnabled,
                    "Only weathers a roster names as soaking. None are named by default.");
                list.GapLine();
            }

            if (Group(list, "Soak length", RimMandrake.Shared.SettingScope.NextPulse, new[] { "defaultSoakHours" }))
            {
                list.Label("Default soak length: " + defaultSoakHours.ToString("0") + " h (sources that set their own length ignore this)");
                defaultSoakHours = list.Slider(defaultSoakHours, 2f, 96f);
                list.GapLine();
            }

            if (Group(list, "Which plants soak", RimMandrake.Shared.SettingScope.Now, new[] { "minGrowDaysToSoak", "cavePlantsNeverSoak" }))
            {
                list.Label("Plants faster than " + minGrowDaysToSoak.ToString("0.0") + " grow-days never soak (applied when you close this window)");
                minGrowDaysToSoak = list.Slider(minGrowDaysToSoak, 0.1f, 5f);
                list.CheckboxLabeled("Cave plants and fungi never soak", ref cavePlantsNeverSoak,
                    "Fungus does not drink water the way this mechanic means. Plants a roster lists explicitly are unaffected. Applied when you close this window.");
                list.GapLine();
            }

            if (Group(list, "The charge", RimMandrake.Shared.SettingScope.Now, new[] { "chargeHours", "maxOvergrowthScale", "reprintIntervalTicks", "hueShiftEnabled", "tellSoundsEnabled", "groundTellEnabled" }))
            {
                list.Label("Full growth to the top: " + chargeHours.ToString("0.0") + " in-game hours");
                chargeHours = list.Slider(chargeHours, 1f, 24f);
                list.Label("Overgrown up to " + maxOvergrowthScale.ToString("0.00") + "x natural size");
                maxOvergrowthScale = list.Slider(maxOvergrowthScale, 1f, 3f);
                list.Label("Re-draw a swelling plant every " + reprintIntervalTicks + " ticks (lower = smoother, costlier)");
                reprintIntervalTicks = Mathf.RoundToInt(list.Slider(reprintIntervalTicks, 60f, 2000f));
                list.CheckboxLabeled("Swelling plants shift to a wrong hue", ref hueShiftEnabled);
                list.CheckboxLabeled("Strain sounds (the creak before the top)", ref tellSoundsEnabled);
                list.CheckboxLabeled("The ground darkens and sprouts when a plant starts to charge", ref groundTellEnabled);
                list.GapLine();
            }

            if (Group(list, "The tops (a disabled top falls back to the Churn)", RimMandrake.Shared.SettingScope.Now, new[] { "churnEnabled", "burstEnabled", "burstHurtsPawns", "tinderEnabled", "slimeEnabled", "ruptureEnabled", "ruptureMutationChance", "flushEnabled" }))
            {
                list.CheckboxLabeled("Churn: split, fruit, sow sprouts (the default)", ref churnEnabled,
                    "Off: a fully charged plant just relaxes back to normal size.");
                list.CheckboxLabeled("Burst: dry-adapted plants pop and sow into your zones", ref burstEnabled);
                list.CheckboxLabeled("  Bursts can bruise and knock down nearby pawns", ref burstHurtsPawns,
                    "Injury and knockdown only — a burst never downs or kills on its own.");
                list.CheckboxLabeled("Tinder: fire-adapted bursts leave fuel", ref tinderEnabled);
                list.CheckboxLabeled("Slime: slime-fed plants turn the ground to slime", ref slimeEnabled);
                list.CheckboxLabeled("Rupture: contaminated plants vent gas and spawn things", ref ruptureEnabled);
                list.Label("  Mutation chance per pulse in a rupture cloud without a vacuum seal: " + ruptureMutationChance.ToStringPercent());
                ruptureMutationChance = list.Slider(ruptureMutationChance, 0f, 0.5f);
                list.CheckboxLabeled("Flush: giant trees swell inside and survive", ref flushEnabled);
                list.GapLine();
            }

            if (Group(list, "Player verbs", RimMandrake.Shared.SettingScope.Now, new[] { "harvestJackpotEnabled", "lastSwingGambleEnabled", "suppressionEnabled" }))
            {
                list.CheckboxLabeled("Harvesting a swollen plant pays extra", ref harvestJackpotEnabled);
                list.CheckboxLabeled("The last swing is a gamble (a late cut or harvest can set it off)", ref lastSwingGambleEnabled);
                list.CheckboxLabeled("Grazing and dry air suppress encroachment", ref suppressionEnabled,
                    "Where animals graze (and where a dry-air blower runs), soak is refused and charging plants relax for a few days.");
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ExplosiveGrowthSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ExplosiveGrowthSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
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

    public class ExplosiveGrowthMod : Mod
    {
        public static ExplosiveGrowthSettings settings;

        public ExplosiveGrowthMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ExplosiveGrowthSettings>();
        }

        public override string SettingsCategory() => "Explosive Plant Growth";

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);

        public override void WriteSettings()
        {
            base.WriteSettings();
            if (RM_ExplosiveGrowthRegistry.Ready) RM_ExplosiveGrowthRegistry.Rebuild();
        }
    }
}
