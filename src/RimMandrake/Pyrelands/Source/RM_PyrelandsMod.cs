using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Pyrelands.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs,
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (cross-biome
    // shape) and src/RimMandrake/BlueDesert/Source/RM_BlueDesertMod.cs
    // (master-toggle shape) — static fields read from everywhere,
    // Scribe_Values in ExposeData, a DoWindowContents helper called from
    // the Mod subclass.
    //
    // Things this gates, each read straight out of FireEcologyHook.cs's
    // own hardcoded numbers (defaults below = shipped behavior, unchanged):
    //   0. Master switch — off degrades every mechanic below gracefully;
    //      the biome and its defs still load (PYRELANDS_RM_MOD_BUILD_1
    //      §6a: "the BiomeDef still loads"). Biome tile PLACEMENT has its
    //      own separate, worldgen-affecting switch (5) and is untouched by
    //      this one.
    //   1. Fulgurite left by a lightning strike on sand-family ground.
    //   2. Loose ash dusting off a burning cell.
    //   3. Scorch-fruit seeded by a burning cell, plus its per-map cap.
    //   4. Ash accumulation (drifts) during Ash Fall / Cinderfall weather.
    //   5. Whether the Pyrelands biome can win tile placement at all —
    //      WORLDGEN-AFFECTING, a new-worlds-only switch.
    //   6. The four absorbed mandrake.rut.pyrelandsmechanics mechanics
    //      (burn line, fire-hawk ember spread, furnace-beast thermal
    //      circuit, fire clock/rite trigger) — PYRELANDS_RM_MOD_BUILD_1 §6.
    //   7. Cross-biome opt-in for the ash-accumulation mechanic (4) on a
    //      non-Pyrelands map, WORLDGEN-AFFECTING (applies once, at map
    //      generation), same shape as RM_GreentideSettings.
    // ════════════════════════════════════════════════════════════════════
    public class RM_PyrelandsSettings : ModSettings
    {
        /// <summary>Master switch. Off: RM_Pyrelands still loads and can
        /// still be assigned to a tile (see biomeGenerationEnabled for the
        /// separate worldgen-placement switch), but every mechanic below
        /// stops mattering — the per-mechanic toggles keep their own state
        /// for when this is back on.</summary>
        public static bool pyrelandsEnabled = true;

        public static bool fulguriteEnabled = true;
        public static float fulguriteChance = 0.35f;

        public static bool ashDustingEnabled = true;
        public static float ashDustingChance = 0.02f;

        public static bool scorchFruitEnabled = true;
        // Per-burned-cell probability (one roll per Fire instance), NOT
        // per-tick. Owner 2026-09-16: "perhaps one in twenty squares".
        public static float scorchFruitChance = 0.05f;
        public static int scorchFruitMapCap = 40;

        public static bool ashfallAccumulationEnabled = true;
        public static float ashfallRateMultiplier = 1f;

        public static bool biomeGenerationEnabled = true;

        // PYRELANDS_FLORA_LEAK_1 — a Harmony postfix on WildPlantSpawner strips
        // any wild-plant candidate off the RM_FE_ grass allowlist on a
        // Pyrelands map, however it reached the candidate list (a foreign
        // mod's plant.wildBiomes entry, a tile mutator's AdditionalWildPlants,
        // or a mixed-biome secondary biome sharing the map). Off: Pyrelands
        // reverts to trusting its own biome-level <wildPlants> list alone,
        // which measurably does not hold on a heavily biome-modded list.
        public static bool wildPlantAllowlistEnabled = true;

        public static bool plantGrowthStagesEnabled = true;

        // PYRELANDS_SCORCHED_RUINS_1: GenStep_ScorchPyrelandsRuins (FireEcologyHook.cs)
        // reads this at mapgen time, per new map — flip it and the NEXT map generated
        // honors it immediately, no restart needed (a map already on disk is untouched).
        public static bool scorchedRuinsEnabled = true;

        // Absorbed from mandrake.rut.pyrelandsmechanics (PYRELANDS_RM_MOD_BUILD_1
        // §6) — every default matches what shipped there, so the absorption
        // changes no player-visible behavior for an existing save.
        public static bool burnLineEnabled = true;
        public static bool fireHawkSpreadEnabled = true;
        public static bool furnaceThermalEnabled = true;
        public static float furnaceWarmthStrength = 1f;
        public static bool fireClockEnabled = true;

        // FURNACEBEAST_WORLD_MIGRATION_1 — the world leg
        // (WorldObject_RM_FurnaceHerd). Nested under furnaceThermalEnabled:
        // this only matters while the thermal circuit itself is on. Off:
        // no herd is ever seeded and any herd already on the world simply
        // stops ticking and delivering/recalling (it is not destroyed —
        // turning this back on lets an existing save's herds resume).
        public static bool furnaceWorldMigrationEnabled = true;
        public static int furnaceHerdCount = PyrelandsTuning.WorldHerdDefaultCount;

        // PYRELANDS_DEDICATED_GRAZER_1 — generic, opt-in via
        // RM_BurrowOnFireExtension; RM_Ashwallow is the first consumer. Off:
        // an extension-carrying race stands its ground like any other animal
        // and takes ordinary fire damage — the mechanic simply stops firing,
        // nothing about the def breaks.
        public static bool burrowOnFireEnabled = true;
        // PYRELANDS_ULLAI_GIANT_BUILD_1. RESTART-REQUIRED (RM_PyrelandsGiants applies them at startup).
        public static bool ullaiEnabled = true;
        public static float ullaiHerdSizeMultiplier = 1f;
        public static bool furnaceBeastGiant = true;
        // PYRELANDS_LIGHTNING_BREAKER_BUILD_1
        public static bool lightningBreakerEnabled = true;
        public static bool breakerPyrelandsOnly = true;
        public static int breakerTripCost = 10;
        public static float breakerRecipeCostFactor = 1f;
        // PYRELANDS_SAND_TERRAIN_YIELD_1: "Shovel sand" orders on terrain carrying RM_TerrainDigYieldExtension.
        public static bool sandShovelEnabled = true;
        public static float sandShovelYieldMultiplier = 1f;

        // Cross-biome opt-in — lets the ash-accumulation mechanic (4) run on
        // a NON-Pyrelands biome's map without importing the whole biome.
        // WORLDGEN-AFFECTING: applies once, right after a map generates; an
        // existing map is never retroactively changed. Same shape as
        // RM_GreentideSettings' cross-biome block.
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        private static string biomeListBuffer;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref pyrelandsEnabled, "pyrelandsEnabled", true);
            Scribe_Values.Look(ref fulguriteEnabled, "fulguriteEnabled", true);
            Scribe_Values.Look(ref fulguriteChance, "fulguriteChance", 0.35f);
            Scribe_Values.Look(ref ashDustingEnabled, "ashDustingEnabled", true);
            Scribe_Values.Look(ref ashDustingChance, "ashDustingChance", 0.02f);
            Scribe_Values.Look(ref scorchFruitEnabled, "scorchFruitEnabled", true);
            // Key renamed with the semantics change (per-tick -> per-cell,
            // 2026-09-16): a settings file saved under the old key holds a
            // per-tick number that would read as ~1-in-400 cells; ignoring
            // the old key gives everyone the new 0.05 default instead.
            Scribe_Values.Look(ref scorchFruitChance, "scorchFruitChancePerCell", 0.05f);
            Scribe_Values.Look(ref scorchFruitMapCap, "scorchFruitMapCap", 40);
            Scribe_Values.Look(ref ashfallAccumulationEnabled, "ashfallAccumulationEnabled", true);
            Scribe_Values.Look(ref ashfallRateMultiplier, "ashfallRateMultiplier", 1f);
            Scribe_Values.Look(ref biomeGenerationEnabled, "biomeGenerationEnabled", true);
            Scribe_Values.Look(ref wildPlantAllowlistEnabled, "wildPlantAllowlistEnabled", true);
            Scribe_Values.Look(ref plantGrowthStagesEnabled, "plantGrowthStagesEnabled", true);
            Scribe_Values.Look(ref scorchedRuinsEnabled, "scorchedRuinsEnabled", true);
            Scribe_Values.Look(ref burnLineEnabled, "burnLineEnabled", true);
            Scribe_Values.Look(ref fireHawkSpreadEnabled, "fireHawkSpreadEnabled", true);
            Scribe_Values.Look(ref furnaceThermalEnabled, "furnaceThermalEnabled", true);
            Scribe_Values.Look(ref furnaceWarmthStrength, "furnaceWarmthStrength", 1f);
            Scribe_Values.Look(ref fireClockEnabled, "fireClockEnabled", true);
            Scribe_Values.Look(ref furnaceWorldMigrationEnabled, "furnaceWorldMigrationEnabled", true);
            Scribe_Values.Look(ref furnaceHerdCount, "furnaceHerdCount", PyrelandsTuning.WorldHerdDefaultCount);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
            Scribe_Values.Look(ref burrowOnFireEnabled, "burrowOnFireEnabled", true);
            Scribe_Values.Look(ref ullaiEnabled, "ullaiEnabled", true);
            Scribe_Values.Look(ref ullaiHerdSizeMultiplier, "ullaiHerdSizeMultiplier", 1f);
            Scribe_Values.Look(ref furnaceBeastGiant, "furnaceBeastGiant", true);
            Scribe_Values.Look(ref lightningBreakerEnabled, "lightningBreakerEnabled", true);
            Scribe_Values.Look(ref breakerPyrelandsOnly, "breakerPyrelandsOnly", true);
            Scribe_Values.Look(ref breakerTripCost, "breakerTripCost", 10);
            Scribe_Values.Look(ref breakerRecipeCostFactor, "breakerRecipeCostFactor", 1f);
            Scribe_Values.Look(ref sandShovelEnabled, "sandShovelEnabled", true);
            Scribe_Values.Look(ref sandShovelYieldMultiplier, "sandShovelYieldMultiplier", 1f);
        }

        /// <summary>True if the cross-biome ash-accumulation opt-in currently
        /// applies to this biome (never to Pyrelands' own — that is native,
        /// not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            return RM_FireEcoKernel.CrossBiomeApplies(crossBiomeEnabled, biome != null, biome != null && biome.defName == "RM_Pyrelands",
                crossBiomeEverywhere, biome != null && crossBiomeEnabled && !crossBiomeEverywhere && ParseBiomeList().Contains(biome.defName));
        }

        private static List<string> ParseBiomeList()
        {
            return RM_FireEcoKernel.ParseList(crossBiomeBiomeList);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_PyrelandsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_PyrelandsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
                if (n == "crossBiomeBiomeList") biomeListBuffer = null;
            }
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): scorched ruins and biome placement are read
        /// while a map or planet is generated, and the furnace-beast herd count only when a new world seeds ([new maps only]);
        /// the giants, ullai and recipe-cost switches are applied at startup ([next game start], a label local to this screen);
        /// every other setting, including the cross-biome ash opt-in (read each weather tick), is read live ([now]).</summary>
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
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Mod enabled", RimMandrake.Shared.SettingScope.Now, new[] { "pyrelandsEnabled" }))
            {
    list.CheckboxLabeled("Mod enabled", ref pyrelandsEnabled,
                    "Off: RM_Pyrelands still loads and can still be assigned to a tile, but every "
                  + "mechanic below stops mattering (their own toggles still apply if this is back "
                  + "on), except fulgurites on ordinary sand outside the Pyrelands' own ground. Biome tile placement has its own separate switch, further down.");
                list.GapLine();
            }

            if (Group(list, "Fulgurite, loose ash and scorch-fruit", RimMandrake.Shared.SettingScope.Now, new[] { "fulguriteEnabled", "fulguriteChance", "ashDustingEnabled", "ashDustingChance", "scorchFruitEnabled", "scorchFruitChance", "scorchFruitMapCap" }))
            {
    list.CheckboxLabeled("Lightning leaves fulgurite", ref fulguriteEnabled,
                    "A strike on sand-family ground (sand, soft sand, deep sand, scorched sand) has a "
                  + "chance to leave a fulgurite behind, in any biome; the Stillsand's dry "
                  + "thunderstorms leave them too. Only strikes on the Pyrelands' own ground also need "
                  + "\"Mod enabled\" above. Off: lightning strikes normally, nothing spawns.");
                if (fulguriteEnabled)
                {
                    list.Label("Chance per strike: " + fulguriteChance.ToString("0%"));
                    fulguriteChance = list.Slider(fulguriteChance, 0f, 1f);
                }
                list.GapLine();

                list.GapLine();
    list.CheckboxLabeled("Fire dusts loose ash", ref ashDustingEnabled,
                    "A burning cell on scorchable ground has a small chance, per tick batch, to "
                  + "drop loose ash filth. Off: fire still burns, no extra ash from this. Rides "
                  + "alongside vanilla's own unconditional scorch mark — that is unaffected either way.");
                if (ashDustingEnabled)
                {
                    list.Label("Rate: " + (ashDustingChance / 0.02f).ToString("0.00") + "x default");
                    ashDustingChance = list.Slider(ashDustingChance, 0.02f * 0.25f, 0.02f * 3f);
                }
                list.Gap();

                list.CheckboxLabeled("Fire seeds scorch-fruit", ref scorchFruitEnabled,
                    "A burning cell on scorchable ground rarely seeds a scorch-fruit pod nearby. "
                  + "Off: no scorch-fruit ever appears this way.");
                if (scorchFruitEnabled)
                {
                    list.Label("Chance per burned cell: 1 in " + (1f / scorchFruitChance).ToString("0") + " (default 1 in 20)");
                    scorchFruitChance = list.Slider(scorchFruitChance, 0.0125f, 0.15f);
                    list.Label("Per-map cap: " + scorchFruitMapCap + " (stops seeding once a map holds this many)");
                    scorchFruitMapCap = (int)list.Slider(scorchFruitMapCap, 10f, 100f);
                }
                list.GapLine();
            }

            if (Group(list, "Ash accumulation (Ash Fall / Cinderfall weather)", RimMandrake.Shared.SettingScope.Now, new[] { "ashfallAccumulationEnabled", "ashfallRateMultiplier" }))
            {
    list.CheckboxLabeled("Weather deposits ash drifts", ref ashfallAccumulationEnabled,
                    "Ash Fall and Cinderfall weather bank loose ash across the map over time. "
                  + "Off: the weather still occurs (darkened sky, lightning on Cinderfall), it just "
                  + "leaves no ash behind.");
                if (ashfallAccumulationEnabled)
                {
                    list.Label("Accumulation rate: " + ashfallRateMultiplier.ToString("0.00") + "x");
                    ashfallRateMultiplier = list.Slider(ashfallRateMultiplier, 0.25f, 3f);
                }
                list.GapLine();
            }

            if (Group(list, "Plant art and wild flora", RimMandrake.Shared.SettingScope.Now, new[] { "plantGrowthStagesEnabled", "wildPlantAllowlistEnabled" }))
            {
    list.CheckboxLabeled("Grass shows its growth stage", ref plantGrowthStagesEnabled,
                    "Quickgrass is drawn as a sprout, then half-grown, then tall lush grass as it "
                  + "regrows after a fire. Off: it is always drawn with its full-grown art (it still "
                  + "grows and still starts small — only the artwork stops changing).");
                list.GapLine();

                list.GapLine();
    list.CheckboxLabeled("Only RM_FE grasses grow wild on Pyrelands", ref wildPlantAllowlistEnabled,
                    "Strips any wild-plant candidate outside the two RM_FE_ grasses on a Pyrelands map, "
                  + "however it got there (a foreign mod's own biome list leaking in via a mixed-biome "
                  + "or tile-mutator mechanism). Off: Pyrelands trusts its own biome definition alone, "
                  + "which other biome-blending mods can bypass.");
                list.GapLine();
            }

            if (Group(list, "Scorched ruins (new maps)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "scorchedRuinsEnabled" }))
            {
    list.CheckboxLabeled("Ruins generate scorched and burned", ref scorchedRuinsEnabled,
                    "Ancient ruins (and mutator-placed ancient structures) on a Pyrelands map get "
                  + "ash terrain and soot filth laid over their footprint as the map is made. "
                  + "Off: ruins generate with plain ground, same as any other biome. Map-generation-"
                  + "affecting — only the NEXT map generated is affected; an existing map is untouched.");
                list.GapLine();
            }

            if (Group(list, "Biome placement (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeGenerationEnabled" }))
            {
    list.CheckboxLabeled("Pyrelands can generate on new worlds", ref biomeGenerationEnabled,
                    "Off: the Pyrelands biome never wins tile placement when generating a NEW world. "
                  + "A world already generated, and any Pyrelands tiles already on it, are unaffected — "
                  + "this never retroactively changes an existing planet.");
                list.GapLine();
            }

            if (Group(list, "Absorbed mechanics (mandrake.rut.pyrelandsmechanics)", RimMandrake.Shared.SettingScope.Now, new[] { "burnLineEnabled", "fireHawkSpreadEnabled", "furnaceThermalEnabled", "furnaceWarmthStrength", "fireClockEnabled", "furnaceWorldMigrationEnabled" }))
            {
    list.CheckboxLabeled("Standing burn line", ref burnLineEnabled,
                    "The grass fire that walks the map with its own burn intelligence, rather than "
                  + "spreading and dying out like an ordinary vanilla fire. Off: fire behaves vanilla.");
                list.CheckboxLabeled("Fire-hawk ember carrying", ref fireHawkSpreadEnabled,
                    "A fire-hawk can carry a live ember and drop it to start a new burn elsewhere. "
                  + "Off: fire-hawks never do this job.");
                list.CheckboxLabeled("Furnace-beast thermal circuit", ref furnaceThermalEnabled,
                    "The furnace-beast's local warmth (a felt-temperature offset around it), bed ignition and thermal charge "
                  + "cycle. Off: it behaves as an ordinary heat-immune grazer.");
                list.Label("Furnace-beast warmth strength: " + furnaceWarmthStrength.ToString("0.00") + "x (+"
                           + (PyrelandsTuning.FurnaceWarmthMaxC * furnaceWarmthStrength).ToString("0") + " C at the beast)");
                furnaceWarmthStrength = list.Slider(furnaceWarmthStrength, 0f, 2f);
                list.CheckboxLabeled("Fire clock (flame harvest / fire raid / fire rite)", ref fireClockEnabled,
                    "The Deep Desert Tribes' incidents that answer the burn. Off: those incidents never "
                  + "fire.");
                list.CheckboxLabeled("Furnace-beast world migration", ref furnaceWorldMigrationEnabled,
                    "Off-map furnace-beast herds cycling the planet (Deep Desert -> Pyrelands -> near "
                  + "terminator -> back), delivering onto a player's map when their route reaches its "
                  + "tile and rejoining the world if that map is later abandoned. Off: no herd is ever "
                  + "seeded and an existing herd simply stops moving until this is back on — it is "
                  + "never destroyed.");
                list.GapLine();
            }

            if (Group(list, "Furnace-beast herds at world start (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "furnaceHerdCount" }))
            {
                list.Label("Seeded once, when a new world begins; a world already running keeps the herds it has. Ignored while world migration is off.");
                list.Label("Herds seeded at world start: " + furnaceHerdCount);
                furnaceHerdCount = (int)list.Slider(furnaceHerdCount, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Giants and recipe costs (restart)", RimMandrake.Shared.SettingScope.Now, new[] { "furnaceBeastGiant", "ullaiEnabled", "ullaiHerdSizeMultiplier", "breakerRecipeCostFactor" }, "[next game start]"))
            {
    list.CheckboxLabeled("Giant furnace-beast (restart)", ref furnaceBeastGiant,
                    "Shipped default: ON. The furnace-beast is a giant (body size 6, a few per map, rarer), drawn huge, "
                  + "with a wider warmth and a bigger smouldering bed. Off after a restart: the classic beast (body size "
                  + "3.2, herds of 3 to 7, its original sprite). Animals already spawned keep their size until regenerated.");
    list.CheckboxLabeled("Ullai herds (restart)", ref ullaiEnabled,
                    "Shipped default: ON. Long-legged ash-grazers in herds of 8 to 20 that drift to where it burned about two "
                  + "days ago. Off: none spawn wild (after a restart) and the herds stop following the burn at once.");
                list.Label("Ullai herd size (restart): " + ullaiHerdSizeMultiplier.ToStringPercent());
                ullaiHerdSizeMultiplier = list.Slider(ullaiHerdSizeMultiplier, 0.25f, 2f);
                list.Label("Breaker core recipe cost (restart): " + breakerRecipeCostFactor.ToStringPercent());
                breakerRecipeCostFactor = list.Slider(breakerRecipeCostFactor, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Burrowers", RimMandrake.Shared.SettingScope.Now, new[] { "burrowOnFireEnabled" }))
            {
    list.CheckboxLabeled("Extension-carrying races burrow ahead of the fire", ref burrowOnFireEnabled,
                    "A race carrying RM_BurrowOnFireExtension (RM_Ashwallow ships with it) goes to "
                  + "ground and shelters near-immune to heat while a fire front is close, then "
                  + "surfaces once it clears. Off: those races stand their ground like any other "
                  + "animal and take ordinary fire damage — nothing about the def breaks.");
                list.GapLine();
            }

            if (Group(list, "Lightning breakers and sand shovelling", RimMandrake.Shared.SettingScope.Now, new[] { "lightningBreakerEnabled", "breakerPyrelandsOnly", "breakerTripCost", "sandShovelEnabled", "sandShovelYieldMultiplier" }))
            {
    list.CheckboxLabeled("Breakers trip on a short circuit", ref lightningBreakerEnabled,
                    "Shipped default: ON. A lightning breaker on a power line trips when a short circuit strikes its side of the "
                  + "grid: the grid splits there and only the faulted side's batteries discharge. Off: breakers are plain "
                  + "conduits and every short circuit drains the whole grid, as in vanilla.");
                list.CheckboxLabeled("Learnable only in the Pyrelands", ref breakerPyrelandsOnly,
                    "Shipped default: ON (owner ruling). The research can only be begun while you hold a home on a Pyrelands "
                  + "map; once known, breakers are buildable anywhere and desert sand works. Off: researchable anywhere.");
                list.Label("Glass sand spent per trip: " + breakerTripCost);
                breakerTripCost = Mathf.RoundToInt(list.Slider(breakerTripCost, 0f, 30f));
                list.CheckboxLabeled("Shovel sand (Orders)", ref sandShovelEnabled,
                    "Shipped default: ON. A 'Shovel sand' order on Pyrelands sand: a miner digs the cell out for glass sand and "
                  + "leaves gravel underneath, so a sand patch is a finite deposit. Off: the order cannot be placed and "
                  + "standing orders are ignored.");
                list.Label("Glass sand per shovelled cell: " + sandShovelYieldMultiplier.ToStringPercent());
                sandShovelYieldMultiplier = list.Slider(sandShovelYieldMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            if (Group(list, "Cross-biome ash accumulation", RimMandrake.Shared.SettingScope.Now, new[] { "crossBiomeEnabled", "crossBiomeEverywhere", "crossBiomeBiomeList", "crossBiomeCoverage" }))
            {
                list.Label("Lets the ash-drift mechanic (Ash Fall / Cinderfall accumulation) apply on a "
                  + "NON-Pyrelands biome's map, without adding the whole Pyrelands biome. Read every "
                  + "weather tick, so a change applies to maps already running.");
                list.CheckboxLabeled("Enable outside the Pyrelands biome", ref crossBiomeEnabled,
                    "Master switch for the section below.");
                if (crossBiomeEnabled)
                {
                    list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                        "Apply to any non-Pyrelands biome. Off: only the biomes named below.");
                    if (!crossBiomeEverywhere)
                    {
                        list.Label("  Biome defNames, comma-separated (e.g. RM_Wasteland, AridShrubland):");
                        biomeListBuffer = list.TextEntry(biomeListBuffer);
                        crossBiomeBiomeList = biomeListBuffer;
                    }
                    list.Label("  Coverage: " + crossBiomeCoverage.ToStringPercent() + " of the native ash-accumulation rate");
                    crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
                }
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_PyrelandsMod : Mod
    {
        public static RM_PyrelandsSettings settings;

        public RM_PyrelandsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_PyrelandsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Pyrelands";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
