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
        // Master switch. Off: every patch no-ops, nothing charges: vanilla growth everywhere (all-off degrades to vanilla).
        // Every runtime read goes through On, which ANDs it with the Baroque Biomes roster toggle "ExplosiveGrowth".
        public static bool enabled = true;

        /// <summary>The roster key of this engine in src/RimMandrake/Biomes.compose.json.</summary>
        public const string RosterKey = "ExplosiveGrowth";

        public static bool On => enabled && RimMandrake.Biomes.RM_BiomesSettings.Enabled(RosterKey);

        // ── the ruled rates (design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md §2.5; defaults = the rulings) ──
        // ONE factor per plant, multiplying vanilla's composite growth rate (light included: a dark cell stays dark).
        public static float dryWetMultiplier = 10f;       // C6 / W3: a dry native on wet, lit ground
        public static float dryDryMultiplier = 0.1f;      // C6 "Tenth speed": a dry native on dry ground
        public static float wetNativeMultiplier = 4f;     // C1 "x4, always": a wet native, wet or dry
        public static float treeRatio = 0.625f;           // EC1: anything yielding wood runs this share of its rate (2.5/4)
        public static float stuntedMultiplier = 0.4f;     // stalled (terminator) biomes, unchanged by the rulings
        public static bool vanillaCropsNeedWater = true;  // setting A (C4): default "need water nearby"
        public static float vanillaDryMultiplier = 0.1f;  // OQ-16: a vanilla plant with no water nearby grows AND ages x0.1
        public static int nearbyRadius = 2;               // OQ-17: "water nearby" = within 2 cells of a source
        public static bool nativesSameRuleInOtherBiomes = false; // setting B (OQ-10): default vanilla, labelled UNSUPPORTED

        // ── the cycle (§4) ───────────────────────────────────────────────
        public static float defaultRuptureChance = 0.3333f; // C3 "1 in 3": the Burst odds of a dry native's cycle
        public static float wetFruitFactor = 2f;          // C2 "fruit prolifically" (PROPOSED 2.0)
        public static bool cropSelfFruitEnabled = true;   // EC3 / OQ-15: our natives sown as crops drop a full harvest
        public static bool waterUseEnabled = true;        // EC3 / OQ-8: every fruiting plant uses the water on its cell
        public static int cropDrawLevels = 1;             // D5: channel levels a fruiting plant draws (needs FlowWorks' exit)
        public static bool dormancyEnabled = true;        // WP2: a plant below x1 ages at its slowed rate
        public static bool tidalLockNoRest = true;        // OQ-7: on a tidally locked world a lit plant never rests
        public static bool sealedGrowersVanilla = true;   // H1: basins, pots, hydroponics grow at vanilla speed, no cycle
        public static bool waveStaggerEnabled = false;    // §7 fallback (3): stagger arming over a day (PF1: only if perf fails)
        // R-G5's under-a-day clause and the fungal carve-out: these plants are Exempt (vanilla speed, no cycle).
        public static float minGrowDaysToSoak = 1f;
        public static bool cavePlantsNeverSoak = true;

        // ── the water sources (§3; one switch each) ──────────────────────
        public static bool naturalWaterEnabled = true;    // W2: river / fresh water / marsh / mud cells
        public static bool spillWaterEnabled = true;      // W4: hose spills and poured water (standing-water filth)
        public static bool irrigationSoakEnabled = true;  // a dug FlowWorks channel and its 8 neighbours
        public static bool rainWaterEnabled = true;       // unroofed ground while it rains, and a few hours after (OQ-9)
        public static float rainLingerHours = 3f;         // OQ-9 "a few hours" (PROPOSED 3)
        public static bool rainPuddlesEnabled = true;     // OQ-9 "shown by puddles"
        public static bool snowmeltEnabled = true;        // OQ-3: snow in the snowmelt biomes waters like rain
        public static bool gradientSurgeSoakEnabled = true; // OQ-13: the salt line stays a water source
        public static bool ashFreshEnabled = true;        // C5: a burnt cell counts as fresh for fire-adapted plants
        public static float ashFlushDays = 3f;            // OQ-11: 3 days, restarted when a seedling appears

        // ── the charge ──────────────────────────────────────────────────
        public static float chargeHours = 6f;             // INVENTED: full growth to the top
        public static float maxOvergrowthScale = 2f;      // INVENTED (design doc §2 "~2x")
        public static int reprintIntervalTicks = 250;     // the tremble wobble cadence; swell steps re-mesh only on change
        public static bool hueShiftEnabled = true;
        public static bool tellSoundsEnabled = true;
        public static bool groundTellEnabled = true;

        // ── the tops ────────────────────────────────────────────────────
        public static bool churnEnabled = true;
        public static bool burstEnabled = true;
        public static bool burstHurtsPawns = true;
        public static bool tinderEnabled = true;
        public static bool slimeEnabled = true;
        public static bool ruptureEnabled = true;
        public static float ruptureMutationChance = 0.08f; // INVENTED
        public static bool flushEnabled = true;

        // ── the player verbs ────────────────────────────────────────────
        public static bool harvestJackpotEnabled = true;  // OQ-14: wild plants only
        public static bool lastSwingGambleEnabled = true; // OQ-14: wild plants only
        public static bool suppressionEnabled = true;

        /// <summary>The rate sliders as the kernel takes them.</summary>
        public static RM_RateSettings Rates => new RM_RateSettings
        {
            dryWet = dryWetMultiplier, dryDry = dryDryMultiplier, wetNative = wetNativeMultiplier, treeRatio = treeRatio,
            stunted = stuntedMultiplier, vanillaDry = vanillaDryMultiplier, vanillaNeedsWater = vanillaCropsNeedWater,
        };

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            // D18 save migration: the retired keys (bandsEnabled, defaultMultiplier, treeMultiplier, terminatorMultiplier,
            // wetAmbient*, minGrowDaysToBoost, soakMultiplier, defaultSoakHours, applyInOtherBiomes, weatherSoakEnabled) are
            // simply no longer read; a settings file holding them loads without error and every new key takes its default.
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref dryWetMultiplier, "dryWetMultiplier", 10f);
            Scribe_Values.Look(ref dryDryMultiplier, "dryDryMultiplier", 0.1f);
            Scribe_Values.Look(ref wetNativeMultiplier, "wetNativeMultiplier", 4f);
            Scribe_Values.Look(ref treeRatio, "treeRatio", 0.625f);
            Scribe_Values.Look(ref stuntedMultiplier, "stuntedMultiplier", 0.4f);
            Scribe_Values.Look(ref vanillaCropsNeedWater, "vanillaCropsNeedWater", true);
            Scribe_Values.Look(ref vanillaDryMultiplier, "vanillaDryMultiplier", 0.1f);
            Scribe_Values.Look(ref nearbyRadius, "nearbyRadius", 2);
            Scribe_Values.Look(ref nativesSameRuleInOtherBiomes, "nativesSameRuleInOtherBiomes", false);
            Scribe_Values.Look(ref defaultRuptureChance, "defaultRuptureChance", 0.3333f);
            Scribe_Values.Look(ref wetFruitFactor, "wetFruitFactor", 2f);
            Scribe_Values.Look(ref cropSelfFruitEnabled, "cropSelfFruitEnabled", true);
            Scribe_Values.Look(ref waterUseEnabled, "waterUseEnabled", true);
            Scribe_Values.Look(ref cropDrawLevels, "cropDrawLevels", 1);
            Scribe_Values.Look(ref dormancyEnabled, "dormancyEnabled", true);
            Scribe_Values.Look(ref tidalLockNoRest, "tidalLockNoRest", true);
            Scribe_Values.Look(ref sealedGrowersVanilla, "sealedGrowersVanilla", true);
            Scribe_Values.Look(ref waveStaggerEnabled, "waveStaggerEnabled", false);
            Scribe_Values.Look(ref minGrowDaysToSoak, "minGrowDaysToSoak", 1f);
            Scribe_Values.Look(ref cavePlantsNeverSoak, "cavePlantsNeverSoak", true);
            Scribe_Values.Look(ref naturalWaterEnabled, "naturalWaterEnabled", true);
            Scribe_Values.Look(ref spillWaterEnabled, "spillWaterEnabled", true);
            Scribe_Values.Look(ref irrigationSoakEnabled, "irrigationSoakEnabled", true);
            Scribe_Values.Look(ref rainWaterEnabled, "rainWaterEnabled", true);
            Scribe_Values.Look(ref rainLingerHours, "rainLingerHours", 3f);
            Scribe_Values.Look(ref rainPuddlesEnabled, "rainPuddlesEnabled", true);
            Scribe_Values.Look(ref snowmeltEnabled, "snowmeltEnabled", true);
            Scribe_Values.Look(ref gradientSurgeSoakEnabled, "gradientSurgeSoakEnabled", true);
            Scribe_Values.Look(ref ashFreshEnabled, "ashFreshEnabled", true);
            Scribe_Values.Look(ref ashFlushDays, "ashFlushDays", 3f);
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
        private static float settingsViewHeight = 2000f;

        private static void Pct(Listing_Standard list, string label, ref float v, float min, float max, string fmt = "0.00")
        {
            list.Label(label + ": x" + v.ToString(fmt));
            v = list.Slider(v, min, max);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);
            bool shellOff = !RimMandrake.Biomes.RM_BiomesSettings.Enabled(RosterKey);

            if (Group(list, "Mod switch", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Plant growth rules enabled", ref enabled,
                    "Off: every plant grows at vanilla speed, nothing swells or reaches a top.\n\n"
                    + "The Baroque Biomes settings page has its own toggle for this engine (under Engines); both must be on.");
                if (shellOff) list.Label("  The Baroque Biomes page has this engine switched OFF, so nothing here runs until it is back on.");
                list.GapLine();
            }

            if (Group(list, "Growth rates", RimMandrake.Shared.SettingScope.Now, new[] { "dryWetMultiplier", "dryDryMultiplier", "wetNativeMultiplier", "treeRatio", "stuntedMultiplier" }))
            {
                list.Label("One rate per plant, by its kind and whether its ground is wet. It multiplies the plant's normal growth, "
                           + "and only while it has light: a dark plant does not grow at all.");
                Pct(list, "Dry-land natives on wet ground", ref dryWetMultiplier, 1f, 20f, "0.0");
                Pct(list, "Dry-land natives on dry ground", ref dryDryMultiplier, 0.01f, 1f);
                Pct(list, "Jungle natives (Greentide, Miasma, Fever Wood, Webwork, Contagion), wet or dry", ref wetNativeMultiplier, 1f, 10f, "0.0");
                Pct(list, "Anything that yields wood grows at this share of its kind's rate", ref treeRatio, 0.1f, 1f, "0.000");
                Pct(list, "Stalled biomes (terminator / poison forest)", ref stuntedMultiplier, 0.1f, 2f);
                list.GapLine();
            }

            if (Group(list, "Vanilla crops and plants in our biomes", RimMandrake.Shared.SettingScope.Now, new[] { "vanillaCropsNeedWater", "vanillaDryMultiplier", "nearbyRadius" }))
            {
                list.CheckboxLabeled("Vanilla crops need water nearby (default)", ref vanillaCropsNeedWater,
                    "On: in our biomes a vanilla crop or plant grows at vanilla speed only with water within reach; without it, "
                    + "it grows and ages at the rate below. Off: vanilla crops grow normally. Our own plants outgrow them either way.");
                Pct(list, "  Without water nearby, they grow and age at", ref vanillaDryMultiplier, 0.01f, 1f);
                list.Label("  \"Nearby\" is within " + nearbyRadius + " cells of a water source");
                nearbyRadius = Mathf.RoundToInt(list.Slider(nearbyRadius, 0f, 6f));
                list.GapLine();
            }

            if (Group(list, "Our plants outside our biomes", RimMandrake.Shared.SettingScope.Now, new[] { "nativesSameRuleInOtherBiomes" }))
            {
                list.CheckboxLabeled("UNSUPPORTED: our plants follow the same rule in other biomes", ref nativesSameRuleInOtherBiomes,
                    "Off (default): outside Baroque Biomes' own biomes our plants grow at vanilla speed and never cycle.\n\n"
                    + "On: they grow x10 watered / x0.1 dry (and cycle) everywhere. Untested and unsupported: it should work, "
                    + "but nobody validates it. Vanilla plants are never affected outside our biomes.");
                if (RM_ExplosiveGrowthRegistry.ScopeForcedBy != null)
                    list.Label("  A campaign layer on your mod list (" + RM_ExplosiveGrowthRegistry.ScopeForcedBy
                               + ") puts every biome in scope, so this option changes nothing while it is loaded.");
                list.GapLine();
            }

            if (Group(list, "The cycle at maturity", RimMandrake.Shared.SettingScope.Now, new[] { "defaultRuptureChance", "wetFruitFactor", "cropSelfFruitEnabled", "waterUseEnabled", "cropDrawLevels", "waveStaggerEnabled" }))
            {
                list.Label("A grown dry-land native on wet, lit ground fruits and throws many sprouts (or bursts) and dies; its "
                           + "seedlings carry on. A jungle native fruits heavily, then withers, leaving a few sprouts.");
                list.Label("Dry natives burst instead of fruiting: " + defaultRuptureChance.ToStringPercent() + " (plants can override)");
                defaultRuptureChance = list.Slider(defaultRuptureChance, 0f, 1f);
                Pct(list, "Jungle natives' fruit, times a normal harvest", ref wetFruitFactor, 1f, 5f, "0.0");
                list.CheckboxLabeled("Our plants sown as crops fruit on their own: a full harvest, and their water is used up", ref cropSelfFruitEnabled);
                list.CheckboxLabeled("Every fruiting plant uses the water on its cell", ref waterUseEnabled,
                    "Spilled water and puddles vanish, the after-rain wet ends there. Rivers, mud and a running flood are never used up.");
                list.Label("  Channel levels a fruiting plant drinks: " + cropDrawLevels + " (waits on FlowWorks; no effect yet)");
                cropDrawLevels = Mathf.RoundToInt(list.Slider(cropDrawLevels, 0f, 4f));
                list.CheckboxLabeled("Stagger a flood's wave over a day (performance fallback)", ref waveStaggerEnabled,
                    "Off (default): every grown plant on newly wet ground arms at once. On: each cell arms in its own hour of the day.");
                list.GapLine();
            }

            if (Group(list, "Ageing, light and growers", RimMandrake.Shared.SettingScope.Now, new[] { "dormancyEnabled", "tidalLockNoRest", "sealedGrowersVanilla", "minGrowDaysToSoak", "cavePlantsNeverSoak" }))
            {
                list.CheckboxLabeled("A plant growing slower than normal also ages slower", ref dormancyEnabled,
                    "A dry native at x0.1 lives ten times as long. Only the water rule slows ageing; darkness and cold never do.");
                list.CheckboxLabeled("On a tidally locked world, lit plants never rest", ref tidalLockNoRest,
                    "Always lit means always growing. Only on a world a loaded campaign marks as tidally locked.");
                list.CheckboxLabeled("Basins, pots and hydroponics grow at vanilla speed", ref sealedGrowersVanilla,
                    "They are their own water source: no bonus, no cycle.");
                list.Label("Plants faster than " + minGrowDaysToSoak.ToString("0.0") + " grow-days keep vanilla speed (applied when you close this window)");
                minGrowDaysToSoak = list.Slider(minGrowDaysToSoak, 0.1f, 5f);
                list.CheckboxLabeled("Cave plants and fungi keep vanilla speed", ref cavePlantsNeverSoak,
                    "Plants a roster lists explicitly are unaffected. Applied when you close this window.");
                list.GapLine();
            }

            if (Group(list, "Water sources", RimMandrake.Shared.SettingScope.Now, new[] { "naturalWaterEnabled", "spillWaterEnabled", "irrigationSoakEnabled", "rainWaterEnabled", "snowmeltEnabled", "gradientSurgeSoakEnabled", "ashFreshEnabled", "ashFlushDays" }))
            {
                list.Label("Ground is wet while water is on it, and only then. Clean water waters every plant; other liquids only plants adapted to them.");
                list.CheckboxLabeled("Rivers, fresh water, marsh and mud (the cell itself)", ref naturalWaterEnabled);
                list.CheckboxLabeled("Spilled and poured water", ref spillWaterEnabled, "A hose spill of water lies as standing water until a plant drinks it or it soaks away.");
                list.CheckboxLabeled("Dug channels holding water (FlowWorks): the channel and the ground beside it", ref irrigationSoakEnabled);
                list.CheckboxLabeled("Rain on open ground", ref rainWaterEnabled);
                list.CheckboxLabeled("Falling snow melts like rain where the biome says so", ref snowmeltEnabled);
                list.CheckboxLabeled("Salt-line surges water the fresh side", ref gradientSurgeSoakEnabled,
                    "Needs the gradient-axis surge (RimMandrake: Environmental Hazards).");
                list.CheckboxLabeled("Fresh ash counts as fresh water for fire-adapted plants", ref ashFreshEnabled, "Needs the Pyrelands' ash field.");
                list.Label("  Fresh for " + ashFlushDays.ToString("0.0") + " days after a burn, restarted when a seedling appears");
                ashFlushDays = list.Slider(ashFlushDays, 0.5f, 10f);
                list.GapLine();
            }

            // Read when a rain STOPS (RM_MapComponent_ExplosiveGrowth.UpdateRain): a change applies from the next rain's end.
            if (Group(list, "After the rain", RimMandrake.Shared.SettingScope.NextPulse, new[] { "rainLingerHours", "rainPuddlesEnabled" }))
            {
                list.Label("The ground stays wet " + rainLingerHours.ToString("0.0") + " h after the rain stops");
                rainLingerHours = list.Slider(rainLingerHours, 0f, 12f);
                list.CheckboxLabeled("Rain leaves puddles (the visible reason the ground is still wet)", ref rainPuddlesEnabled);
                list.GapLine();
            }

            if (Group(list, "The charge", RimMandrake.Shared.SettingScope.Now, new[] { "chargeHours", "maxOvergrowthScale", "reprintIntervalTicks", "hueShiftEnabled", "tellSoundsEnabled", "groundTellEnabled" }))
            {
                list.Label("Full growth to the top: " + chargeHours.ToString("0.0") + " in-game hours");
                chargeHours = list.Slider(chargeHours, 1f, 24f);
                list.Label("Overgrown up to " + maxOvergrowthScale.ToString("0.00") + "x natural size");
                maxOvergrowthScale = list.Slider(maxOvergrowthScale, 1f, 3f);
                list.Label("Trembling plants wobble every " + reprintIntervalTicks + " ticks (lower = smoother, costlier)");
                reprintIntervalTicks = Mathf.RoundToInt(list.Slider(reprintIntervalTicks, 60f, 2000f));
                list.CheckboxLabeled("Swelling plants shift to a wrong hue", ref hueShiftEnabled);
                list.CheckboxLabeled("Strain sounds (the creak before the top)", ref tellSoundsEnabled);
                list.CheckboxLabeled("The ground darkens when a plant starts to charge", ref groundTellEnabled);
                list.GapLine();
            }

            if (Group(list, "The tops (a disabled top falls back to fruiting)", RimMandrake.Shared.SettingScope.Now, new[] { "churnEnabled", "burstEnabled", "burstHurtsPawns", "tinderEnabled", "slimeEnabled", "ruptureEnabled", "ruptureMutationChance", "flushEnabled" }))
            {
                list.CheckboxLabeled("The cycle (fruit and sprouts) itself", ref churnEnabled, "Off: a grown plant never charges and just keeps growing at its rate.");
                list.CheckboxLabeled("Burst: a dry native can pop and sow into your zones", ref burstEnabled, "Off: it fruits instead.");
                list.CheckboxLabeled("  Bursts can bruise and knock down nearby pawns", ref burstHurtsPawns, "Injury and knockdown only; a burst never downs or kills on its own.");
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
                list.CheckboxLabeled("Harvesting a swollen wild plant pays extra", ref harvestJackpotEnabled, "Never on crops: a crop's harvest is exactly its full yield.");
                list.CheckboxLabeled("The last swing at a swollen wild plant is a gamble", ref lastSwingGambleEnabled, "Never on crops.");
                list.CheckboxLabeled("Grazing and dry air suppress encroachment", ref suppressionEnabled,
                    "Where animals graze (and where a dry-air blower runs), water does not count and charging plants relax for a few days.");
                list.GapLine();
            }

            if (RM_ExplosiveGrowthRegistry.Ready)
            {
                int[] a = RM_ExplosiveGrowthRegistry.CountByArchetype;
                list.Label("Plant kinds now: dry natives " + a[0] + ", jungle natives " + a[1] + ", fire-adapted " + a[2]
                           + ", vanilla speed (exempt) " + a[3] + ", vanilla " + a[4] + ". Biomes: " + RM_ExplosiveGrowthRegistry.HomeBiomes.Count + " of ours.");
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

        /// <summary>The mod this engine shipped in — Baroque Biomes (mandrake.rm.biomes), of which it is a composed
        /// member. Its plants, and the wild flora of its biomes, are the soak's native scope.</summary>
        public static ModContentPack Home;

        public ExplosiveGrowthMod(ModContentPack content) : base(content)
        {
            Home = content;
            settings = GetSettings<ExplosiveGrowthSettings>();
            // The shell's tooltip then says this engine's toggle stops it on running maps too (spec §5, arm 2).
            RimMandrake.Biomes.RM_BiomesSettings.mechanicsGated.Add(ExplosiveGrowthSettings.RosterKey);
        }

        public override string SettingsCategory() => "Plant Growth (water, rates and the cycle)";

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);

        public override void WriteSettings()
        {
            base.WriteSettings();
            if (RM_ExplosiveGrowthRegistry.Ready) RM_ExplosiveGrowthRegistry.TryRebuild("settings closed");
        }
    }
}
