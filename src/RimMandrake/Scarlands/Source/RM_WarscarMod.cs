using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // SCARLANDS_STANDALONE_MOD_1 — Mod Settings for Warscar: the worldgen-rarity
    // slider (applied by RM_WarscarPatches_Rarity), one switch per mechanic, and the
    // cross-biome opt-in (DEAD_OR_INERT_SETTINGS wiring 2026-10-08, same shape as
    // RM_TheRotSettings): wreck-lichen seeding and the settling-dust calm run on an
    // opted-in non-Warscar map, the lichen scaled by the intensity slider.
    //
    // STATIC FIELD, read from worldgen with no Mod instance handy.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WarscarSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        public static float biomeRarityFactor = 1f;

        // MOD_OPTIONS_RETROFIT_1: let the map-level mechanics (wreck-lichen, the settling calm) run on other biomes.
        // Persisted and exposed here honestly as NOT YET WIRED to any
        // mechanic — there is no mechanic in this mod for it to gate yet.
        // WARSCAR_TURRETS_TRACK_1 toggles.
        public static bool turretTrackingEnabled = true;   // broken turrets' barrels follow movers
        public static bool turretRefitEnabled = true;      // wreck -> RM_OldLineTurret gizmo
        public static float oldLineDamageFactor = 1f;      // applied at game start
        public static float oldLineCooldownFactor = 1f;    // applied at game start

        // WARSCAR_TOTCHAK_WAKES_1 toggles.
        public static bool totchakEnabled = true;           // totchak spawns dormant in walls and wakes
        public static bool totchakEatsPlayerWalls = true;   // ruled default on
        public static float totchakWakeRadius = 12f;        // demolition wake radius (cells)
        public static float totchakBiteScale = 1f;          // wall-eating damage scale
        public static float totchakGrazeDays = 8f;          // awake days before it lies down again

        // WARSCAR_OLD_TONGUE_1 toggles.
        public static bool oldTongueEnabled = true;          // inscribed panels generate on new maps
        public static float oldTonguePanelsPerMap = 3f;      // panels placed per map (a quota, filled from wall-side cells)
        // PROVISIONAL (auto-decided 2026-10-09, WARSCAR_TUNING_SEMANTICS_1): relabelled, behaviour unchanged. This is
        // rolled per shuffled wall-side CELL until the quota fills, so it only thins panels on maps with few such
        // cells; it is not a per-attempt chance (making it one would cut the panels research sets rely on).
        public static float oldTongueRevealChance = 0.8f;
        public static int oldTongueSkillGate = 8;            // Intellectual needed to transcribe (0 = none)

        // WARSCAR_HOSPICE_DESERTERS_1 toggles.
        public static bool hospiceEnabled = true;            // rings, cradle jobs and walk-ins
        public static int hospiceIntactPerMap = 2;           // max intact chassis rolled per map (0-3)
        public static float hospiceStageDays = 1.5f;         // days per cradle stage (five stages)
        public static float hospiceFailureChance = 0.08f;    // per risky stage
        public static bool hospiceLashOut = true;            // limbs stage may hit an adjacent pawn once
        public static bool hospiceWalkInEnabled = true;      // deserter walk-in incident
        public static float hospiceWalkInFrequency = 1f;     // chance the incident proceeds when it rolls

        // WARSCAR_RAINBOW_POOLS_1 toggles.
        public static bool poolsEnabled = true;              // pools generate on new maps; taps work
        public static float poolsPerMap = 3f;                // up to this many pools (1-3), new maps
        public static float poolCycleHours = 24f;            // one full four-phase cycle
        public static float bloomDanger = 1f;                // scales the burn and toxic buildup of drawing the bloom
        public static bool catalystEnabled = true;           // glower crust holds a phase

        // WARSCAR_CHOTRIX_BUILD_1 toggles.
        public static bool chotrixEnabled = true;            // chotrix spawns on new maps and hunts
        public static bool chotrixHuntRevalidate = true;     // CHOTRIX_HUNT_TARGET_REVALIDATE_1: abandon prey that stops being lone
        public static float chotrixPerMap = 2f;              // up to this many per map (0-2), new maps
        public static float chotrixRevealSeconds = 4f;       // seconds visible after it strikes
        public static bool chotrixDragEnabled = true;        // WARSCAR_CHOTRIX_SIGNS_1: drags its kill to cover, furrowing the film
        public static bool lacquerCloakEnabled = true;       // lacquered cloaks grant still-and-unseen invisibility
        public static float lacquerSeenRadius = 15f;         // a hostile with sight within this many cells "sees" the wearer
        public static bool lacquerDeniedWhileGlowing = true; // DEEPFIRE_WORLD_LIGHT_1 (d): a pawn carrying a light (deepfire glow) cannot vanish

        // WARSCAR_FREE_TIER_BODY_1 toggles. Species rows apply at startup (restart needed).
        public static bool enableChatrak = true;
        public static bool enableTetchik = true;
        public static bool enablePallbearer = true;
        public static bool enableScarRoach = true;
        public static bool enableWreckLichenSeeder = true;
        // WARSCAR_SHEET_DONOR_PORT_1: the five owned ports that replaced the donor rows (was one "interim donors" switch).
        public static bool enableRimclaw = true;
        public static bool enableBileworm = true;
        public static bool enableElectricTick = true;
        public static bool enableElectricGryllotalpa = true;
        public static bool enableJuggernautBeetle = true;
        // BILEWORM_CORPSE_ROT_1: corpses near a bileworm rot fast into corpse bile it drinks; colonists nearby smell it.
        public static bool bilewormGasEnabled = true;

        // WARSCAR_SETTLING_WEATHER_1 toggles.
        public static bool settlingEnabled = true;           // calm starts the Settling at all
        public static float settlingCalmThreshold = 0.35f;   // wind speed below this is calm
        public static float settlingCalmHours = 4f;          // hours of calm before it starts
        public static float settlingEndWind = 0.8f;          // wind speed above this ends it
        public static float settlingEndHours = 1f;           // hours of strong wind before it ends
        public static float settlingToxicStrength = 1f;      // scales the airborne toxic buildup (0 = harmless)
        public static bool liftFrontEnabled = true;          // the visible front with brief toxic exposure
        public static bool warDustEnabled = true;            // film can be swept up for war dust
        public static bool warDustBlightCureEnabled = true;  // growers dust blighted plants with war dust (insecticide)
        public static float ordnancePerMap = 3f;             // buried shells per new map (0-8)
        // ORDNANCE_TRIGGER_REAL_SHOT_1 PROVISIONAL (auto-decided 2026-10-09): "set off from range" fires the
        // shooter's real weapon at the shell from 9+ cells (ammo, accuracy, range and min-range all apply).
        public static bool ordnanceRealShot = true;

        // WARSCAR_GEIGER_CHOIR_1 toggles.
        public static bool choirEnabled = true;              // the whole choir (ticks, wind, hum, boil, jar sound)
        public static float choirVolume = 1f;                // one global volume
        public static float choirTickVolumeCeiling = 1f;     // cap on how loud the tick gets
        public static float choirTickDensity = 1f;           // tick tempo scale
        public static bool choirWindEnabled = true;          // wind-on-metal layer
        public static bool choirReducedRepetition = false;   // fewer, jittered clicks
        public static bool choirJarWarnings = true;          // caravan message before a polluted tile

        // WARSCAR_MARK_TRADE_BUILD_1 -- the mark made a trade
        public static bool markEnabled = true;               // hourly accrual on a Warscar map
        public static float markAccrualPerDay = 0.3f;        // gross per day on the map (fade is -0.1/day)
        public static bool markFloorEnabled = true;          // past 0.5 it never fades below 0.25
        public static bool markTradeBonusesEnabled = true;   // hacking / mech butchery / smelting offsets (restart)

        // WARSCAR_CHATRAK_SNAP_BUILD_1 -- the chatrak's snap
        public static bool snapEnabled = true;               // scaria chatrak are armed and eventually snap
        public static float snapArmingHours = 24f;           // hours between arming sweeps on a Warscar map
        public static float snapStageSpeed = 1f;             // scales the incubation climb (restart)

        // WARSCAR_LOOSENED_PANEL_BUILD_1 -- the mark opens loosened panels
        public static bool loosenedPanelsEnabled = true;     // panels generate on new maps and can be worked loose
        public static float loosenedPanelsPerMap = 3f;       // up to this many per new map (0-8)

        // WARSCAR_AEROSOL_SCREEN_1 -- the aerosol screen core
        public static bool aerosolScreenEnabled = true;      // screens block airborne toxins, fallout and the film
        public static float aerosolScreenRadiusFactor = 1f;  // scales every screen's radius
        public static bool calibrationEnabled = true;        // calibrated screens scrub tox gas and slowly un-pollute ground
        public static int hummingRingsPerMap = 2;            // projector rings per new map (0-3); the first is always live
        public static bool ringSalvageEnabled = true;        // evaluated rings can be uninstalled, repaired or stripped
        public static bool glowerShieldingEnabled = true;    // glower shield panels and plates shield against toxins
        public static float projectorCoreChance = 0.3f;      // chance a stripped dead ring yields a projector core
        public static bool shipWakesLine = true;             // a landed gravship's engine within 40 cells wakes dead rings

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;
        private static Vector2 biomeScroll = Vector2.zero;
        private static List<BiomeDef> biomesSorted;

        // Checklist replaces the free-text box, where a typo silently matched nothing (belt SC-2).
        // Names already in the stored list that are not real biomes are kept untouched.
        private static void DrawBiomeChecklist(Rect outRect)
        {
            if (biomesSorted == null)
            {
                biomesSorted = new List<BiomeDef>(DefDatabase<BiomeDef>.AllDefsListForReading);
                biomesSorted.Sort((x, y) => string.Compare(x.LabelCap.ToString(), y.LabelCap.ToString(), System.StringComparison.OrdinalIgnoreCase));
            }
            List<string> sel = new List<string>();
            if (!crossBiomeBiomeList.NullOrEmpty())
                foreach (string part in crossBiomeBiomeList.Split(',', ';')) { string t = part.Trim(); if (t.Length > 0) sel.Add(t); }
            const float rowH = 24f;
            Rect view = new Rect(0f, 0f, outRect.width - 16f, biomesSorted.Count * rowH);
            Widgets.BeginScrollView(outRect, ref biomeScroll, view);
            float y = 0f;
            bool changed = false;
            foreach (BiomeDef b in biomesSorted)
            {
                bool was = sel.Contains(b.defName), now = was;
                Widgets.CheckboxLabeled(new Rect(0f, y, view.width, rowH), b.LabelCap + " (" + b.defName + ")", ref now);
                if (now != was)
                {
                    if (now) sel.Add(b.defName); else sel.RemoveAll(n => n == b.defName);
                    changed = true;
                }
                y += rowH;
            }
            Widgets.EndScrollView();
            if (changed) crossBiomeBiomeList = string.Join(", ", sel.ToArray());
        }

        public static bool IsWarscar(BiomeDef biome) { return biome != null && biome.defName == "RM_Warscar"; }

        /// <summary>True if the cross-biome opt-in applies to this biome (never to the Warscar itself: that is native).</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            if (!RM_WarscarSettings.crossBiomeEnabled || biome == null || IsWarscar(biome)) return false;
            if (RM_WarscarSettings.crossBiomeEverywhere) return true;
            if (RM_WarscarSettings.crossBiomeBiomeList.NullOrEmpty()) return false;
            foreach (string part in RM_WarscarSettings.crossBiomeBiomeList.Split(',', ';'))
                if (part.Trim() == biome.defName) return true;
            return false;
        }

        /// <summary>The Warscar's map mechanics run here: the biome itself, or an opted-in cross-biome map.</summary>
        public static bool Governs(BiomeDef biome) { return IsWarscar(biome) || AppliesToBiome(biome); }

        /// <summary>1 on the Warscar; the intensity slider on a cross-biome map; 0 elsewhere.</summary>
        public static float Coverage(BiomeDef biome) { return IsWarscar(biome) ? 1f : (AppliesToBiome(biome) ? RM_WarscarSettings.crossBiomeCoverage : 0f); }

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref turretTrackingEnabled, "turretTrackingEnabled", true);
            Scribe_Values.Look(ref turretRefitEnabled, "turretRefitEnabled", true);
            Scribe_Values.Look(ref oldLineDamageFactor, "oldLineDamageFactor", 1f);
            Scribe_Values.Look(ref oldLineCooldownFactor, "oldLineCooldownFactor", 1f);
            Scribe_Values.Look(ref totchakEnabled, "totchakEnabled", true);
            Scribe_Values.Look(ref totchakEatsPlayerWalls, "totchakEatsPlayerWalls", true);
            Scribe_Values.Look(ref totchakWakeRadius, "totchakWakeRadius", 12f);
            Scribe_Values.Look(ref totchakBiteScale, "totchakBiteScale", 1f);
            Scribe_Values.Look(ref totchakGrazeDays, "totchakGrazeDays", 8f);
            Scribe_Values.Look(ref oldTongueEnabled, "oldTongueEnabled", true);
            Scribe_Values.Look(ref oldTonguePanelsPerMap, "oldTonguePanelsPerMap", 3f);
            Scribe_Values.Look(ref oldTongueRevealChance, "oldTongueRevealChance", 0.8f);
            Scribe_Values.Look(ref oldTongueSkillGate, "oldTongueSkillGate", 8);
            Scribe_Values.Look(ref hospiceEnabled, "hospiceEnabled", true);
            Scribe_Values.Look(ref hospiceIntactPerMap, "hospiceIntactPerMap", 2);
            Scribe_Values.Look(ref hospiceStageDays, "hospiceStageDays", 1.5f);
            Scribe_Values.Look(ref hospiceFailureChance, "hospiceFailureChance", 0.08f);
            Scribe_Values.Look(ref hospiceLashOut, "hospiceLashOut", true);
            Scribe_Values.Look(ref hospiceWalkInEnabled, "hospiceWalkInEnabled", true);
            Scribe_Values.Look(ref hospiceWalkInFrequency, "hospiceWalkInFrequency", 1f);
            Scribe_Values.Look(ref poolsEnabled, "poolsEnabled", true);
            Scribe_Values.Look(ref poolsPerMap, "poolsPerMap", 3f);
            Scribe_Values.Look(ref poolCycleHours, "poolCycleHours", 24f);
            Scribe_Values.Look(ref bloomDanger, "bloomDanger", 1f);
            Scribe_Values.Look(ref catalystEnabled, "catalystEnabled", true);
            Scribe_Values.Look(ref chotrixEnabled, "chotrixEnabled", true);
            Scribe_Values.Look(ref chotrixHuntRevalidate, "chotrixHuntRevalidate", true);
            Scribe_Values.Look(ref chotrixPerMap, "chotrixPerMap", 2f);
            Scribe_Values.Look(ref chotrixRevealSeconds, "chotrixRevealSeconds", 4f);
            Scribe_Values.Look(ref chotrixDragEnabled, "chotrixDragEnabled", true);
            Scribe_Values.Look(ref lacquerCloakEnabled, "lacquerCloakEnabled", true);
            Scribe_Values.Look(ref lacquerSeenRadius, "lacquerSeenRadius", 15f);
            Scribe_Values.Look(ref lacquerDeniedWhileGlowing, "lacquerDeniedWhileGlowing", true);
            Scribe_Values.Look(ref enableChatrak, "enableChatrak", true);
            Scribe_Values.Look(ref enableTetchik, "enableTetchik", true);
            Scribe_Values.Look(ref enablePallbearer, "enablePallbearer", true);
            Scribe_Values.Look(ref enableScarRoach, "enableScarRoach", true);
            Scribe_Values.Look(ref enableWreckLichenSeeder, "enableWreckLichenSeeder", true);
            Scribe_Values.Look(ref enableRimclaw, "enableRimclaw", true);
            Scribe_Values.Look(ref enableBileworm, "enableBileworm", true);
            Scribe_Values.Look(ref bilewormGasEnabled, "bilewormGasEnabled", true);
            Scribe_Values.Look(ref enableElectricTick, "enableElectricTick", true);
            Scribe_Values.Look(ref enableElectricGryllotalpa, "enableElectricGryllotalpa", true);
            Scribe_Values.Look(ref enableJuggernautBeetle, "enableJuggernautBeetle", true);
            Scribe_Values.Look(ref settlingEnabled, "settlingEnabled", true);
            Scribe_Values.Look(ref settlingCalmThreshold, "settlingCalmThreshold", 0.35f);
            Scribe_Values.Look(ref settlingCalmHours, "settlingCalmHours", 4f);
            Scribe_Values.Look(ref settlingEndWind, "settlingEndWind", 0.8f);
            Scribe_Values.Look(ref settlingEndHours, "settlingEndHours", 1f);
            Scribe_Values.Look(ref settlingToxicStrength, "settlingToxicStrength", 1f);
            Scribe_Values.Look(ref liftFrontEnabled, "liftFrontEnabled", true);
            Scribe_Values.Look(ref warDustEnabled, "warDustEnabled", true);
            Scribe_Values.Look(ref warDustBlightCureEnabled, "warDustBlightCureEnabled", true);
            Scribe_Values.Look(ref ordnancePerMap, "ordnancePerMap", 3f);
            Scribe_Values.Look(ref ordnanceRealShot, "ordnanceRealShot", true);
            Scribe_Values.Look(ref choirEnabled, "choirEnabled", true);
            Scribe_Values.Look(ref choirVolume, "choirVolume", 1f);
            Scribe_Values.Look(ref choirTickVolumeCeiling, "choirTickVolumeCeiling", 1f);
            Scribe_Values.Look(ref choirTickDensity, "choirTickDensity", 1f);
            Scribe_Values.Look(ref choirWindEnabled, "choirWindEnabled", true);
            Scribe_Values.Look(ref choirReducedRepetition, "choirReducedRepetition", false);
            Scribe_Values.Look(ref choirJarWarnings, "choirJarWarnings", true);
            Scribe_Values.Look(ref markEnabled, "markEnabled", true);
            Scribe_Values.Look(ref markAccrualPerDay, "markAccrualPerDay", 0.3f);
            Scribe_Values.Look(ref markFloorEnabled, "markFloorEnabled", true);
            Scribe_Values.Look(ref markTradeBonusesEnabled, "markTradeBonusesEnabled", true);
            Scribe_Values.Look(ref snapEnabled, "snapEnabled", true);
            Scribe_Values.Look(ref snapArmingHours, "snapArmingHours", 24f);
            Scribe_Values.Look(ref snapStageSpeed, "snapStageSpeed", 1f);
            Scribe_Values.Look(ref loosenedPanelsEnabled, "loosenedPanelsEnabled", true);
            Scribe_Values.Look(ref loosenedPanelsPerMap, "loosenedPanelsPerMap", 3f);
            Scribe_Values.Look(ref aerosolScreenEnabled, "aerosolScreenEnabled", true);
            Scribe_Values.Look(ref aerosolScreenRadiusFactor, "aerosolScreenRadiusFactor", 1f);
            Scribe_Values.Look(ref calibrationEnabled, "calibrationEnabled", true);
            Scribe_Values.Look(ref glowerShieldingEnabled, "glowerShieldingEnabled", true);
            Scribe_Values.Look(ref hummingRingsPerMap, "hummingRingsPerMap", 2);
            Scribe_Values.Look(ref shipWakesLine, "shipWakesLine", true);
            Scribe_Values.Look(ref ringSalvageEnabled, "ringSalvageEnabled", true);
            Scribe_Values.Look(ref projectorCoreChance, "projectorCoreChance", 0.3f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
            if (settlingEndWind < settlingCalmThreshold + SettlingWindGap) settlingEndWind = settlingCalmThreshold + SettlingWindGap;
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // The Settling's hysteresis: a constant wind between the two thresholds would otherwise start and end it repeatedly.
        public const float SettlingWindGap = 0.05f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WarscarSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WarscarSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scroll;
        private static float viewHeight = 2400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): a GenStep.Generate or the BiomeWorker score is
        /// [new maps only]; a [StaticConstructorOnStartup] edit of defs is [next game start]; a tick, job, comp or inspect read is [now].
        /// Nothing in this mod is read by nothing, so there is no change-nothing group.</summary>
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
        public void DoWindowContents(Rect inRect)
        {
            // maxOneColumn is load-bearing: once content outgrows viewHeight, Listing wraps into an off-screen second
            // column and CurHeight then reports that column's height, so the view shrinks and the tail is unreachable.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Read in RM_WarscarPatches_Rarity, a postfix on BiomeWorker_Scarlands.GetScore: planet generation only.
            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeRarityFactor" }))
            {
                list.Label("Biome rarity: " + RarityLabel());
                list.Label("At 0 Warscar never generates on a new planet. Affects planets "
                           + "generated afterwards, never one that already exists.");
                biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Broken turrets", RimMandrake.Shared.SettingScope.Now, new[] { "turretTrackingEnabled", "turretRefitEnabled" }))
            {
                list.CheckboxLabeled("Broken turrets track movement", ref turretTrackingEnabled,
                    "The barrel of a broken ancient turret turns to follow the nearest moving pawn. It never fires.");
                list.CheckboxLabeled("Allow refitting broken turrets", ref turretRefitEnabled,
                    "Adds a Refit button to broken turrets that converts them into an old-line turret.");
                list.GapLine();
            }

            // Read once in OldLineTurretTuning, a [StaticConstructorOnStartup] that edits the shared defs.
            if (Group(list, "Old-line turret tuning", RimMandrake.Shared.SettingScope.Now, new[] { "oldLineDamageFactor", "oldLineCooldownFactor" }, "[next game start]"))
            {
                list.Label("Old-line turret damage: x" + oldLineDamageFactor.ToString("0.00") + " (applies after restart)");
                oldLineDamageFactor = list.Slider(oldLineDamageFactor, 0.25f, 3f);
                list.Label("Old-line turret cooldown: x" + oldLineCooldownFactor.ToString("0.00") + " (applies after restart)");
                oldLineCooldownFactor = list.Slider(oldLineCooldownFactor, 0.25f, 3f);
                list.GapLine();
            }

            // totchakEnabled is read on the tick, in jobs and in GenStep (so it also gates new maps); the rest are tick/job reads.
            if (Group(list, "Totchak (wall colossus)", RimMandrake.Shared.SettingScope.Now, new[] { "totchakEnabled", "totchakEatsPlayerWalls", "totchakWakeRadius", "totchakBiteScale", "totchakGrazeDays" }))
            {
                list.CheckboxLabeled("Totchak (wall colossus)", ref totchakEnabled,
                    "A totchak sleeps in a run of ruin wall, wakes to demolition, eats walls, and lies down again. Off: awake totchak go back to sleep now, and none are placed on new maps.");
                list.CheckboxLabeled("Totchak eats player walls", ref totchakEatsPlayerWalls,
                    "When no ruin wall is in reach, a woken totchak eats your walls.");
                list.Label("Totchak wake radius: " + totchakWakeRadius.ToString("0") + " cells");
                totchakWakeRadius = list.Slider(totchakWakeRadius, 4f, 30f);
                list.Label("Totchak wall-eating damage: x" + totchakBiteScale.ToString("0.00"));
                totchakBiteScale = list.Slider(totchakBiteScale, 0.25f, 4f);
                list.Label("Totchak grazing days before it lies down: " + totchakGrazeDays.ToString("0.0"));
                totchakGrazeDays = list.Slider(totchakGrazeDays, 1f, 30f);
                list.GapLine();
            }

            // All three are read in GenStep_OldTongue.Generate.
            if (Group(list, "Inscribed panels: placement (old tongue)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "oldTongueEnabled", "oldTonguePanelsPerMap", "oldTongueRevealChance" }))
            {
                list.CheckboxLabeled("Inscribed panels (old tongue)", ref oldTongueEnabled,
                    "Panels of an old script stand against ruin walls; reading a full set unlocks research. Affects new maps.");
                list.Label("Panels per map: " + oldTonguePanelsPerMap.ToString("0"));
                oldTonguePanelsPerMap = list.Slider(oldTonguePanelsPerMap, 1f, 8f);
                list.Label("Panel chance per wall-side spot: " + oldTongueRevealChance.ToString("0%")
                    + " (the per-map count above still fills wherever a ruin has enough wall; this only matters on small ruins)");
                oldTongueRevealChance = list.Slider(oldTongueRevealChance, 0.1f, 1f);
                list.GapLine();
            }

            // Read in the panel's CanInteract each time someone tries to read it.
            if (Group(list, "Inscribed panels: reading", RimMandrake.Shared.SettingScope.Now, new[] { "oldTongueSkillGate" }))
            {
                list.Label("Intellectual needed to read a panel: " + oldTongueSkillGate + (oldTongueSkillGate == 0 ? " (no gate)" : ""));
                oldTongueSkillGate = Mathf.RoundToInt(list.Slider(oldTongueSkillGate, 0f, 20f));
                list.GapLine();
            }

            if (Group(list, "Hospice (kneeling chassis and cradle)", RimMandrake.Shared.SettingScope.Now, new[] { "hospiceEnabled", "hospiceStageDays", "hospiceFailureChance", "hospiceLashOut", "hospiceWalkInEnabled", "hospiceWalkInFrequency" }))
            {
                list.CheckboxLabeled("Hospice (kneeling chassis and cradle)", ref hospiceEnabled,
                    "Rings of kneeling chassis in ruins; an intact one can be hauled to a hospice cradle and woken over days. Off: the cradle, its jobs and the walk-in stop now, and no rings are placed on new maps.");
                list.Label("Cradle stage length: " + hospiceStageDays.ToString("0.0") + " days (five stages)");
                hospiceStageDays = list.Slider(hospiceStageDays, 0.1f, 5f);
                list.Label("Cradle failure chance per risky stage: " + hospiceFailureChance.ToString("0%"));
                hospiceFailureChance = list.Slider(hospiceFailureChance, 0f, 0.6f);
                list.CheckboxLabeled("Limbs stage may lash out", ref hospiceLashOut,
                    "At the twitching-limbs stage the machine may hit one adjacent pawn, once.");
                list.CheckboxLabeled("Deserter walks in", ref hospiceWalkInEnabled,
                    "Rarely, a damaged machine walks onto the map toward your cradle. Only while a cradle stands.");
                list.Label("Walk-in frequency: " + hospiceWalkInFrequency.ToString("0%") + " of rolls proceed");
                hospiceWalkInFrequency = list.Slider(hospiceWalkInFrequency, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Hospice: chassis placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "hospiceIntactPerMap" }))
            {
                list.Label("Intact chassis per map: up to " + hospiceIntactPerMap + " (new maps)");
                hospiceIntactPerMap = Mathf.RoundToInt(list.Slider(hospiceIntactPerMap, 0f, 3f));
                list.GapLine();
            }

            if (Group(list, "Rainbow pools", RimMandrake.Shared.SettingScope.Now, new[] { "poolsEnabled", "poolCycleHours", "bloomDanger", "catalystEnabled" }))
            {
                bool flowWorksLoaded = ModLister.GetActiveModWithIdentifier("mandrake.rm.flowworks", true) != null;
                list.Label("Partner mod FlowWorks (pool terrain): " + (flowWorksLoaded ? "loaded" : "NOT loaded -- no pools will be placed"));
                bool trackGridLoaded = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_MapComponent_TrackGrid") != null;
                list.Label("Partner mod CreatureBehaviors (footprint track grid): " + (trackGridLoaded ? "loaded" : "NOT loaded -- the Settling leaves no footprints"));
                list.CheckboxLabeled("Rainbow pools", ref poolsEnabled,
                    "Reaction-liquor pools cycle through four phases a day; a tap at the rim draws each phase's reagent. Off: pools stop cycling and taps stop now, and none are placed on new maps. Needs FlowWorks.");
                list.Label("Cycle length: " + poolCycleHours.ToString("0") + " hours (four phases)");
                poolCycleHours = list.Slider(poolCycleHours, 4f, 96f);
                list.Label("Bloom danger: x" + bloomDanger.ToString("0.00") + (bloomDanger <= 0f ? " (drawing the bloom is harmless)" : ""));
                bloomDanger = list.Slider(bloomDanger, 0f, 3f);
                list.CheckboxLabeled("Glower crust catalyst", ref catalystEnabled,
                    "Glower crust loaded into a tap holds the pool's phase (6 hours per crust) and doubles each draw.");
                list.GapLine();
            }

            if (Group(list, "Rainbow pools: placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "poolsPerMap" }))
            {
                list.Label("Pools per map: up to " + Mathf.RoundToInt(poolsPerMap) + " (new maps)");
                poolsPerMap = Mathf.Round(list.Slider(poolsPerMap, 1f, 3f));
                list.GapLine();
            }

            if (Group(list, "Chotrix (invisible hunter)", RimMandrake.Shared.SettingScope.Now, new[] { "chotrixEnabled", "chotrixHuntRevalidate", "chotrixRevealSeconds", "chotrixDragEnabled" }))
            {
                list.CheckboxLabeled("Chotrix (invisible hunter)", ref chotrixEnabled,
                    "A lean cloaked scavenger hunts lone small animals, and lone pawns at night. It shows when it strikes. Off: existing chotrix stop hunting and show themselves now, and none spawn on new maps.");
                list.CheckboxLabeled("Chotrix breaks off when prey gains company", ref chotrixHuntRevalidate,
                    "On: a stalking chotrix gives up its prey the moment someone joins it, so it never bites into a group of two. "
                  + "Off: once it picks a lone target it follows through even if others arrive.");
                list.Label("Chotrix visible after a strike: " + chotrixRevealSeconds.ToString("0.0") + " seconds");
                chotrixRevealSeconds = list.Slider(chotrixRevealSeconds, 1f, 15f);
                list.CheckboxLabeled("Chotrix drags its kill to cover", ref chotrixDragEnabled,
                    "After a kill it drags the body 8-16 cells off before eating. On settled film the drag leaves a furrow in place of its prints.");
                list.GapLine();
            }

            if (Group(list, "Chotrix: placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "chotrixPerMap" }))
            {
                list.Label("Chotrix per map: up to " + Mathf.RoundToInt(chotrixPerMap) + " (new maps)");
                chotrixPerMap = Mathf.Round(list.Slider(chotrixPerMap, 0f, 2f));
                list.GapLine();
            }

            if (Group(list, "Lacquered cloaks", RimMandrake.Shared.SettingScope.Now, new[] { "lacquerCloakEnabled", "lacquerSeenRadius", "lacquerDeniedWhileGlowing" }))
            {
                list.CheckboxLabeled("Lacquered cloaks hide the wearer", ref lacquerCloakEnabled,
                    "A cloak made with cloak lacquer makes the wearer invisible while standing still and unseen. Permanent; never expires.");
                list.Label("Lacquer: seen within " + lacquerSeenRadius.ToString("0") + " cells by a hostile with line of sight");
                lacquerSeenRadius = list.Slider(lacquerSeenRadius, 3f, 40f);
                list.CheckboxLabeled("A glowing wearer cannot hide", ref lacquerDeniedWhileGlowing,
                    "A pawn giving off light (deepfire on the skin or on the clothes) cannot vanish under a lacquered cloak until the glow is gone. Needs Luminous Pigment. Safe mid-game.");
                list.GapLine();
            }

            if (Group(list, "The Settling (calm-triggered war fallout)", RimMandrake.Shared.SettingScope.Now, new[] { "settlingEnabled", "settlingCalmThreshold", "settlingCalmHours", "settlingEndWind", "settlingEndHours", "settlingToxicStrength", "liftFrontEnabled" }))
            {
                list.CheckboxLabeled("The Settling (calm-triggered war fallout)", ref settlingEnabled,
                    "When the wind stays calm the old war's dust settles: toxic to anything unroofed, and a film that keeps every footprint until the wind returns. Off: it never starts and ends at once if running.");
                list.Label("Calm means wind below: " + settlingCalmThreshold.ToString("0.00"));
                settlingCalmThreshold = list.Slider(settlingCalmThreshold, 0.05f, 0.8f);
                list.Label("Calm hours before it starts: " + settlingCalmHours.ToString("0.0"));
                settlingCalmHours = list.Slider(settlingCalmHours, 0.5f, 24f);
                list.Label("Strong wind that ends it: above " + settlingEndWind.ToString("0.00"));
                settlingEndWind = list.Slider(settlingEndWind, 0.4f, 1.5f);
                if (settlingEndWind < settlingCalmThreshold + SettlingWindGap)
                {
                    settlingEndWind = settlingCalmThreshold + SettlingWindGap;   // one wind can never both start and end it
                    list.Label("(kept above the calm threshold: the ending wind must be stronger than calm)");
                }
                list.Label("Hours of strong wind before it ends: " + settlingEndHours.ToString("0.0"));
                settlingEndHours = list.Slider(settlingEndHours, 0.25f, 12f);
                list.Label("Toxic strength: x" + settlingToxicStrength.ToString("0.00") + (settlingToxicStrength <= 0f ? " (harmless)" : ""));
                settlingToxicStrength = list.Slider(settlingToxicStrength, 0f, 3f);
                list.CheckboxLabeled("Lift front", ref liftFrontEnabled,
                    "When the wind returns the film lifts as a grey front crossing the map downwind, with brief airborne toxic exposure as it passes.");
                list.GapLine();
            }

            if (Group(list, "War dust and buried shells", RimMandrake.Shared.SettingScope.Now, new[] { "warDustEnabled", "warDustBlightCureEnabled", "ordnanceRealShot" }))
            {
                list.CheckboxLabeled("War dust", ref warDustEnabled,
                    "Colonists may sweep the film into war dust (thickest in crater bowls), a toxic powder for tox shells, an insecticide and a dye filler.");
                list.CheckboxLabeled("War dust cures blight", ref warDustBlightCureEnabled,
                    "Growers carry one war dust to each blighted plant and dust it: the blight dies and the plant lives. Off: blight is cut as in vanilla.");
                list.CheckboxLabeled("Shells are set off by a real shot", ref ordnanceRealShot,
                    "On: \"Set off from range\" sends a colonist whose weapon can reach a safe 9+ cells to really shoot the shell "
                  + "(it can miss, spends a shot, and a shotgun cannot reach). Off: any ranged weapon works and the shell simply "
                  + "goes off after a short aim.");
                list.GapLine();
            }

            if (Group(list, "Buried shells: placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "ordnancePerMap" }))
            {
                list.Label("Buried shells per map: up to " + Mathf.RoundToInt(ordnancePerMap) + " (new maps)");
                ordnancePerMap = Mathf.Round(list.Slider(ordnancePerMap, 0f, 8f));
                list.GapLine();
            }

            if (Group(list, "Geiger choir (Warscar soundscape)", RimMandrake.Shared.SettingScope.Now, new[] { "choirEnabled", "choirVolume", "choirTickVolumeCeiling", "choirTickDensity", "choirWindEnabled", "choirReducedRepetition", "choirJarWarnings" }))
            {
                list.CheckboxLabeled("Geiger choir (Warscar soundscape)", ref choirEnabled,
                    "Tetchik tick over glower and beetles, wind on ancient metal (silent during the Settling), the projector hum, the pool boil, and the tetchik jar's sound.");
                list.Label("Choir volume: " + choirVolume.ToString("0.00"));
                choirVolume = list.Slider(choirVolume, 0f, 1f);
                list.Label("Tick volume ceiling: " + choirTickVolumeCeiling.ToString("0.00"));
                choirTickVolumeCeiling = list.Slider(choirTickVolumeCeiling, 0.1f, 1f);
                list.Label("Tick density: x" + choirTickDensity.ToString("0.00"));
                choirTickDensity = list.Slider(choirTickDensity, 0.25f, 3f);
                list.CheckboxLabeled("Wind-on-metal layer", ref choirWindEnabled);
                list.CheckboxLabeled("Reduced-repetition mode", ref choirReducedRepetition,
                    "Far fewer clicks, each with a slightly different pitch.");
                list.CheckboxLabeled("Tetchik jar warnings", ref choirJarWarnings,
                    "A caravan carrying a tetchik jar gets a message before it enters a polluted tile.");
                list.GapLine();
            }

            if (Group(list, "The Warscar mark", RimMandrake.Shared.SettingScope.Now, new[] { "markEnabled", "markAccrualPerDay", "markFloorEnabled" }))
            {
                list.CheckboxLabeled("Walking the Warscar marks people", ref markEnabled,
                    "Every hour on a Warscar map, roofed or not, deepens a mark on each person there: a mood hit, "
                  + "sad wandering at the deeper stages, and a trade in return. Off: no new mark accrues.");
                if (markEnabled)
                {
                    list.Label("Mark accrual: " + markAccrualPerDay.ToString("0.00") + " per day on the map (it fades 0.10 per day)");
                    markAccrualPerDay = list.Slider(markAccrualPerDay, 0f, 1f);
                }
                list.CheckboxLabeled("A deep mark never fully fades", ref markFloorEnabled,
                    "Once a mark has passed halfway it never fades below a mild mark, on or off the Warscar.");
                list.GapLine();
            }

            // Read once in RM_WarscarMarkStartup, a [StaticConstructorOnStartup] that edits the mark hediff's stages.
            if (Group(list, "The Warscar mark: trade", RimMandrake.Shared.SettingScope.Now, new[] { "markTradeBonusesEnabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("The mark pays a trade (restart to apply)", ref markTradeBonusesEnabled,
                    "Marked people hack faster, butcher mechanoids faster and, from a deepening mark, smelt faster. "
                  + "Off: the mark only costs.");
                list.GapLine();
            }

            if (Group(list, "The chatrak's snap", RimMandrake.Shared.SettingScope.Now, new[] { "snapEnabled", "snapArmingHours" }))
            {
                list.CheckboxLabeled("Scaria chatrak snap in the end", ref snapEnabled,
                    "A wild chatrak carrying scaria on a Warscar map starts to turn: its plates lift, it stops eating, "
                  + "it circles, and then it goes for anyone. Off: no chatrak is armed, and one already turning never snaps.");
                if (snapEnabled)
                {
                    list.Label("Arming sweep every " + snapArmingHours.ToString("0") + " hours");
                    snapArmingHours = list.Slider(snapArmingHours, 1f, 120f);
                }
                list.GapLine();
            }

            // Read once in RM_ChatrakSnapStartup, a [StaticConstructorOnStartup] that rescales the incubation hediff.
            if (Group(list, "The chatrak's snap: turning speed", RimMandrake.Shared.SettingScope.Now, new[] { "snapStageSpeed" }, "[next game start]"))
            {
                list.Label("Turning speed (restart to apply): x" + snapStageSpeed.ToString("0.00")
                    + " (default: about one to two weeks from armed to snap)");
                snapStageSpeed = list.Slider(snapStageSpeed, 0.25f, 4f);
                list.GapLine();
            }

            if (Group(list, "Loosened wall panels", RimMandrake.Shared.SettingScope.Now, new[] { "loosenedPanelsEnabled" }))
            {
                list.CheckboxLabeled("Loosened wall panels", ref loosenedPanelsEnabled,
                    "A few panels in each new Warscar map's ancient walls sit loose with a sealed crate behind them. Only "
                  + "someone carrying a deepening Warscar mark can work one loose; anyone else is refused. Off: no panels on "
                  + "new maps, and existing ones cannot be worked now.");
                list.GapLine();
            }

            if (Group(list, "Loosened wall panels: placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "loosenedPanelsPerMap" }))
            {
                list.Label("Up to " + loosenedPanelsPerMap.ToString("0") + " per new map");
                loosenedPanelsPerMap = list.Slider(loosenedPanelsPerMap, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Aerosol screens", RimMandrake.Shared.SettingScope.Now, new[] { "aerosolScreenEnabled", "aerosolScreenRadiusFactor", "calibrationEnabled", "glowerShieldingEnabled" }))
            {
                list.CheckboxLabeled("Aerosol screens", ref aerosolScreenEnabled,
                    "Inside a working aerosol screen's dome there is no airborne toxic buildup (toxic fallout, toxic rain, the Settling "
                  + "and its lift front), no fallout damage to plants and items, and no settled film. Never stops bullets, heat or cold. "
                  + "Off: screens do nothing.");
                if (aerosolScreenEnabled)
                {
                    list.Label("Screen radius: x" + aerosolScreenRadiusFactor.ToString("0.00"));
                    aerosolScreenRadiusFactor = list.Slider(aerosolScreenRadiusFactor, 0.5f, 2f);
                    list.CheckboxLabeled("Calibrated screens scrub the air and ground", ref calibrationEnabled,
                        "A calibrated aerosol screen slowly clears toxic gas and, more slowly, ground pollution inside its dome. "
                      + "Off: calibrated screens only block, like the plain ones.");
                }
                list.CheckboxLabeled("Glower shielding", ref glowerShieldingEnabled,
                    "Glower shield panels give pawns in their room toxic environment resistance and halve room toxic damage; "
                  + "glower plates add resistance to the wearer. Off: panels do nothing; plates are ordinary apparel and keep their resistance.");
                list.GapLine();
            }

            if (Group(list, "Projector rings", RimMandrake.Shared.SettingScope.Now, new[] { "shipWakesLine", "ringSalvageEnabled", "projectorCoreChance" }))
            {
                list.CheckboxLabeled("The ship wakes the line", ref shipWakesLine,
                    "A landed gravship whose engine is within 40 cells wakes dead projector rings until it lifts.");
                list.CheckboxLabeled("Ring salvage", ref ringSalvageEnabled,
                    "Once evaluated, a working ring can be uninstalled and reinstalled at home as a working screen with no research, "
                  + "a failing ring can be repaired, and a dead ring can be stripped. Off: rings can still be evaluated but not taken apart.");
                if (ringSalvageEnabled)
                {
                    list.Label("Projector core from a stripped dead ring: " + Mathf.RoundToInt(projectorCoreChance * 100f) + "%");
                    projectorCoreChance = list.Slider(projectorCoreChance, 0f, 1f);
                }
                list.GapLine();
            }

            if (Group(list, "Projector rings: placement", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "hummingRingsPerMap" }))
            {
                list.Label("Projector rings per map: up to " + hummingRingsPerMap + " (new maps; the first is always humming)");
                hummingRingsPerMap = Mathf.RoundToInt(list.Slider(hummingRingsPerMap, 0f, 3f));
                list.GapLine();
            }

            // Read once in RM_WarscarStartup, a [StaticConstructorOnStartup] that removes the switched-off wildAnimals rows.
            if (Group(list, "Species (restart required)", RimMandrake.Shared.SettingScope.Now, new[] { "enableChatrak", "enableTetchik", "enablePallbearer", "enableScarRoach", "enableRimclaw", "enableBileworm", "enableElectricTick", "enableElectricGryllotalpa", "enableJuggernautBeetle" }, "[next game start]"))
            {
                list.CheckboxLabeled("Chatrak (plated grazer)", ref enableChatrak);
                list.CheckboxLabeled("Tetchik (glower beetle)", ref enableTetchik);
                list.CheckboxLabeled("Pallbearer (carrion eater)", ref enablePallbearer);
                list.CheckboxLabeled("Scar roach (cleaner)", ref enableScarRoach);
                list.CheckboxLabeled("Rimclaw (rust-plated scavenger)", ref enableRimclaw);
                list.CheckboxLabeled("Bileworm (corpse slug)", ref enableBileworm);
                list.CheckboxLabeled("Electric tick (short-lived, bursts on death)", ref enableElectricTick);
                list.CheckboxLabeled("Electric gryllotalpa (throws arcs)", ref enableElectricGryllotalpa);
                list.CheckboxLabeled("Juggernaut beetle (armoured giant)", ref enableJuggernautBeetle);
                list.GapLine();
            }

            if (Group(list, "Bileworm gas", RimMandrake.Shared.SettingScope.Now, new[] { "bilewormGasEnabled" }))
            {
                list.CheckboxLabeled("Bileworm gas rots nearby corpses into bile it drinks", ref bilewormGasEnabled,
                    "On: corpses near a bileworm rot within hours, frozen or not; one it reaches dissolves into corpse bile it drinks, and colonists nearby smell it. Off: an ordinary slug. Safe mid-game.");
                list.GapLine();
            }

            // Read in MapComponent_WreckLichen.MapComponentTick: a per-tick map component, not a worldgen step.
            if (Group(list, "Wreck-lichen", RimMandrake.Shared.SettingScope.Now, new[] { "enableWreckLichenSeeder" }))
            {
                list.CheckboxLabeled("Wreck-lichen grows beside ruins and wreck", ref enableWreckLichenSeeder,
                    "Places wreck-lichen on open cells next to ruins and wreck as the map runs. Safe mid-game; not part of world generation.");
                list.GapLine();
            }

            // Governs/Coverage are read by MapComponent_WreckLichen and MapComponent_Settling on their ticks.
            if (Group(list, "Cross-biome opt-in", RimMandrake.Shared.SettingScope.Now, new[] { "crossBiomeEnabled", "crossBiomeEverywhere", "crossBiomeBiomeList", "crossBiomeCoverage" }))
            {
                list.Label("Runs the Warscar's map mechanics on a NON-Warscar map: wreck-lichen beside ruins and wreck, "
                           + "and the settling dust after a calm. Rings, panels and the cast stay Warscar-only.");
                list.CheckboxLabeled("Enable outside the Warscar", ref crossBiomeEnabled, "Master switch for the section below.");
                if (crossBiomeEnabled)
                {
                    list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere, "Apply to any non-Warscar biome. Off: only the biomes named below.");
                    if (!crossBiomeEverywhere)
                    {
                        list.Label("  Tick the biomes (stored as a defName list):");
                        DrawBiomeChecklist(list.GetRect(180f));
                    }
                    list.Label("  Wreck-lichen intensity on those maps: " + (crossBiomeCoverage * 100f).ToString("0") + "%");
                    crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
                }
                list.GapLine();
            }

            viewHeight = list.CurHeight + 24f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    // Static Thing registries (CompChotrix.All, CompTotchak.All, CompInscribedPanel.All) are pruned only on PostDeSpawn,
    // and a discarded game's Things never despawn. Thing.Map is Find.Maps[index], so a stale entry would alias onto the
    // new game's map at the same index. The engine constructs every GameComponent for each new or loaded Game, before
    // any map's Things spawn, so clearing here gives each game a clean registry.
    public class RM_GameComponent_WarscarRegistryReset : GameComponent
    {
        public RM_GameComponent_WarscarRegistryReset(Game game)
        {
            CompChotrix.All.Clear();
            CompTotchak.All.Clear();
            CompInscribedPanel.All.Clear();
        }
    }

    public class RM_WarscarMod : Mod
    {
        public static RM_WarscarSettings settings;

        public RM_WarscarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarscarSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warscar";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}

namespace RimMandrake.Scarlands
{
    // Removes the wildAnimals rows of species the player switched off.
    // BiomeDef.wildAnimals is private and its commonality cache is lazy, so
    // this runs once at startup, before any map asks for a commonality.
    [StaticConstructorOnStartup]
    public static class RM_WarscarStartup
    {
        static RM_WarscarStartup()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Warscar");
            if (biome == null) return;

            HashSet<string> off = new HashSet<string>();
            if (!RM_WarscarSettings.enableChatrak) off.Add("RM_Chatrak");
            if (!RM_WarscarSettings.enableTetchik) off.Add("RM_Tetchik");
            if (!RM_WarscarSettings.enablePallbearer) off.Add("RM_Pallbearer");
            if (!RM_WarscarSettings.enableScarRoach) off.Add("RM_ScarRoach");
            if (!RM_WarscarSettings.enableRimclaw) off.Add("RM_Rimclaw");
            if (!RM_WarscarSettings.enableBileworm) off.Add("RM_Bileworm");
            if (!RM_WarscarSettings.enableElectricTick) off.Add("RM_ElectricTick");
            if (!RM_WarscarSettings.enableElectricGryllotalpa) off.Add("RM_ElectricGryllotalpa");
            if (!RM_WarscarSettings.enableJuggernautBeetle) off.Add("RM_JuggernautBeetle");
            if (off.Count == 0) return;

            FieldInfo wild = AccessTools.Field(typeof(BiomeDef), "wildAnimals");
            FieldInfo cache = AccessTools.Field(typeof(BiomeDef), "cachedAnimalCommonalities");
            if (wild == null || cache == null)
            {
                Log.Warning("[RM_Warscar] BiomeDef.wildAnimals/cachedAnimalCommonalities not found; species toggles not applied.");
                return;
            }
            List<BiomeAnimalRecord> rows = (List<BiomeAnimalRecord>)wild.GetValue(biome);
            rows.RemoveAll(r => r.animal != null && off.Contains(r.animal.defName));
            cache.SetValue(biome, null);
        }
    }
}
