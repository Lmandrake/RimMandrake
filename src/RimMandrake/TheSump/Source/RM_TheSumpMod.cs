using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.TheSump
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Sump.
    //
    // Precedent: src/RimMandrake/Miasma/Source/RM_MiasmaMod.cs (the honest-
    // pointer reasoning below) and src/RimMandrake/PoisonForest/Source/
    // RM_PoisonForestMod.cs (the worldgen-rarity slider shape).
    //
    // This mod ships a real BiomeWorker of its own (RM_BiomeWorker_TheSump),
    // so it gets the standard worldgen-rarity master toggle every sibling
    // biome-worker mod ships. Its actual gameplay mechanics — the poured tar
    // moat + fuse-post ignition, the dig-shaft stratum lottery, the tar-
    // beast dormant set-piece, the sump-mouse filth-trail telegraphy, the
    // wick-garden crop, and the permanent-dusk weather lock — are all
    // implemented by classes in the SHARED mandrake.rm.environmentalhazards
    // assembly. Of those, tarCoatingEnabled/tarredHediffEnabled/
    // glasswalkSlipEnabled/warblingGlowEnabled/biomeGlowMultiplierEnabled
    // already live on THAT mod's own settings screen (RM_EnvironmentalHazardsSettings)
    // and are shared with other biomes (Greentide, Miasma) reading the same
    // switches — duplicating a Sump-only copy here would either do nothing
    // or silently diverge from what that screen already promises a player,
    // same reasoning RM_MiasmaMod.cs already documents.
    //
    // HONEST GAP, not this item's to fix: the moat-ignition (RM_CompFloodIgniter),
    // dig-lottery (RM_CompWorkedLottery), beast-bulge dread field/wake-relay,
    // and mouse filth-trail comps have NO static settings toggle anywhere
    // today (MEASURED against RM_EnvironmentalHazardsMod.cs this pass — no
    // lottery/dread/wake/floodIgniter/filthTrail field exists) — they are
    // simply always-on wherever their content is deployed. A settings screen
    // that invented a checkbox for them without any C# reading it would be a
    // screen that lies (same standard RM_MiasmaMod.cs's own comment sets);
    // wiring real toggles for them is MOD_OPTIONS_RETROFIT_1 follow-up work
    // on the shared kit, not scaffolded here.
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TheSumpSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        // 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // SUMP_TAR_VAULT_1 — RM_Comp_TarVaultSeal reads this static field
        // directly (same "static field, no Mod instance needed" idiom this
        // settings class already documents above for biomeRarityFactor,
        // since a comp's CompTick has no guaranteed settings-instance
        // handy either). All-off degrades gracefully: a disabled vault's
        // stored contents simply rot normally, same as any other shelf —
        // no half-sealed state is possible.
        public static bool tarVaultEnabled = true;

        // SUMP_TAR_HYDROLOGY_1 ruling 7 — RUT_GenStep_DeepBlackMere reads
        // this static field directly at map generation, same "static field,
        // no Mod instance needed" idiom this class already documents above.
        // All-off degrades gracefully: without the mere, a Sump map simply
        // keeps the biome's ordinary scattered tar pockets it already
        // generates today, nothing else changes.
        public static bool deepBlackMereEnabled = true;

        // SUMP_KETHREL_BUILD_1 - the kethrel's scrap shell (RM_CompKethrelShell reads these static fields).
        // Off: it picks nothing up and wears no shell (the stock animal). Density scales its wild commonality at
        // startup (restart to apply). The value ceiling is silver per stack it will still pick up.
        public static bool kethrelShellEnabled = true;
        public static float kethrelDensity = 1f;
        public static float kethrelValueCeiling = 200f;
        public static bool kethrelTakeColonyProperty = false;
        public static float kethrelMoltLoadKg = 30f;
        public static float kethrelHandlingDifficulty = 1f;
        // SUMP_CAPSTAN_TURRET_BUILD_1: the lasso's numbers (Melee Animation bases) set on the building.
        public static bool capstanEnabled = true;
        public static float capstanRange = 10f;
        public static float capstanReelSpeed = 1f;
        public static float capstanCooldownSeconds = 20f;
        public static bool capstanFriendlyPull = true;
        public static float capstanSnapChance = 0.08f;
        public static float capstanMaxMass = 150f;
        public static float capstanMaxBodySize = 2.5f;
        public static float capstanSnapDamage = 20f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref tarVaultEnabled, "tarVaultEnabled", true, true);
            Scribe_Values.Look(ref deepBlackMereEnabled, "deepBlackMereEnabled", true, true);
            Scribe_Values.Look(ref kethrelShellEnabled, "kethrelShellEnabled", true, true);
            Scribe_Values.Look(ref kethrelDensity, "kethrelDensity", 1f, true);
            Scribe_Values.Look(ref kethrelValueCeiling, "kethrelValueCeiling", 200f, true);
            Scribe_Values.Look(ref kethrelTakeColonyProperty, "kethrelTakeColonyProperty", false, true);
            Scribe_Values.Look(ref kethrelMoltLoadKg, "kethrelMoltLoadKg", 30f, true);
            Scribe_Values.Look(ref kethrelHandlingDifficulty, "kethrelHandlingDifficulty", 1f, true);
            Scribe_Values.Look(ref capstanEnabled, "capstanEnabled", true, true);
            Scribe_Values.Look(ref capstanRange, "capstanRange", 10f, true);
            Scribe_Values.Look(ref capstanReelSpeed, "capstanReelSpeed", 1f, true);
            Scribe_Values.Look(ref capstanCooldownSeconds, "capstanCooldownSeconds", 20f, true);
            Scribe_Values.Look(ref capstanFriendlyPull, "capstanFriendlyPull", true, true);
            Scribe_Values.Look(ref capstanSnapChance, "capstanSnapChance", 0.08f, true);
            Scribe_Values.Look(ref capstanMaxMass, "capstanMaxMass", 150f, true);
            Scribe_Values.Look(ref capstanMaxBodySize, "capstanMaxBodySize", 2.5f, true);
            Scribe_Values.Look(ref capstanSnapDamage, "capstanSnapDamage", 20f, true);
        }

                // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_TheSumpSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_TheSumpSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the rarity slider is read by the biome worker and the mere by a map GenStep ([new maps only]); the kethrel density edits the biome animal list once at startup ([next game start], a label local to this screen); everything else is read on a tick, a job or a property evaluated per use ([now]).</summary>
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
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeRarityFactor" }))
            {
                list.Label("Biome rarity: " + RarityLabel());
                list.Label("At 0 the Sump never generates on a new planet. The default places a scattering of low, flat, permanently-dusky tar basins. Affects planets generated afterwards, never one that already exists.");
                biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Tar vault", RimMandrake.Shared.SettingScope.Now, new[] { "tarVaultEnabled" }))
            {
                list.CheckboxLabeled("Tar vault seals contents (no rot; extraction needs solvent)", ref tarVaultEnabled,
                    "The tar vault (RM_TarVault) freezes rot on anything sealed inside it. "
                  + "Off: it behaves like an ordinary shelf, no sealing, no solvent gate.");
                list.GapLine();
            }

            if (Group(list, "Deep Black mere (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "deepBlackMereEnabled" }))
            {
                list.CheckboxLabeled("Generate the Deep Black mere", ref deepBlackMereEnabled,
                    "A landmark-scale unbroken expanse of deep tar generates once per Sump map, well "
                  + "clear of the edge -- the biome's own \"ocean\" at map scale, and (via FlowWorks' "
                  + "natural-liquid-source rule) an effectively infinite canal source once a channel "
                  + "reaches it. Off: the map keeps only the biome's ordinary scattered tar pockets. "
                  + "Read when a Sump map is generated; existing maps keep what they have.");
                list.GapLine();
            }

            if (Group(list, "Kethrel scrap shell", RimMandrake.Shared.SettingScope.Now, new[] { "kethrelShellEnabled", "kethrelValueCeiling", "kethrelTakeColonyProperty", "kethrelMoltLoadKg", "kethrelHandlingDifficulty" }))
            {
                list.CheckboxLabeled("Kethrel wears a scrap shell", ref kethrelShellEnabled,
                    "The kethrel picks up loose weapons and scrap near tar and wears them as armour, "
                  + "getting slower and harder with load. Off: it picks nothing up (the plain animal).");
                list.Label("Most valuable thing a kethrel will pick up: " + kethrelValueCeiling.ToString("0") + " silver per stack");
                kethrelValueCeiling = list.Slider(kethrelValueCeiling, 20f, 2000f);
                list.CheckboxLabeled("Kethrel may take things from the colony's home area", ref kethrelTakeColonyProperty,
                    "Off: it ignores anything lying inside your home area. On: stockpiled weapons and scrap are fair game.");
                list.Label("Kethrel molts by itself at: " + kethrelMoltLoadKg.ToString("0") + " kg carried");
                kethrelMoltLoadKg = list.Slider(kethrelMoltLoadKg, 10f, 80f);
                list.Label("Molt handling difficulty: " + kethrelHandlingDifficulty.ToString("0.0") + "x");
                kethrelHandlingDifficulty = list.Slider(kethrelHandlingDifficulty, 0f, 2f);
                list.GapLine();
            }

            if (Group(list, "Kethrel density (restart)", RimMandrake.Shared.SettingScope.Now, new[] { "kethrelDensity" }, "[next game start]"))
            {
                list.Label("Kethrel density: " + kethrelDensity.ToString("0.0") + "x");
                kethrelDensity = list.Slider(kethrelDensity, 0f, 3f);
                list.Label("Scales the kethrel's wild commonality in the Sump's animal list once at startup. At 0 it is removed from the list.");
                list.GapLine();
            }

            if (Group(list, "Capstan turret", RimMandrake.Shared.SettingScope.Now, new[] { "capstanEnabled", "capstanRange", "capstanReelSpeed", "capstanCooldownSeconds", "capstanFriendlyPull", "capstanSnapChance", "capstanMaxMass", "capstanMaxBodySize", "capstanSnapDamage" }))
            {
                list.CheckboxLabeled("Capstan turret ropes and reels", ref capstanEnabled,
                    "Shipped default: ON. A powered capstan turret throws a line at a visible enemy in range and reels it in "
                  + "toward itself. Off: the turret stands idle.");
                list.Label("Capstan range: " + capstanRange.ToString("0") + " cells");
                capstanRange = Mathf.Round(list.Slider(capstanRange, 4f, 25f));
                list.Label("Reel speed: " + capstanReelSpeed.ToStringPercent() + " (one cell every " + (30f / Mathf.Max(0.1f, capstanReelSpeed) / 60f).ToString("0.0") + " s)");
                capstanReelSpeed = list.Slider(capstanReelSpeed, 0.25f, 4f);
                list.Label("Cooldown between lines: " + capstanCooldownSeconds.ToString("0") + " s");
                capstanCooldownSeconds = Mathf.Round(list.Slider(capstanCooldownSeconds, 2f, 120f));
                list.CheckboxLabeled("Capstan pulls downed colonists to safety", ref capstanFriendlyPull,
                    "Shipped default: ON. With no enemy in range, it ropes a downed colonist in the open and reels them in.");
                list.Label("Chance per cell that a struggling target snaps the line: " + capstanSnapChance.ToStringPercent());
                capstanSnapChance = list.Slider(capstanSnapChance, 0f, 0.5f);
                list.Label("Heaviest it can reel: " + capstanMaxMass.ToString("0") + " kg, body size " + capstanMaxBodySize.ToString("0.0"));
                capstanMaxMass = Mathf.Round(list.Slider(capstanMaxMass, 30f, 1000f));
                capstanMaxBodySize = list.Slider(capstanMaxBodySize, 0.5f, 6f);
                list.Label("Damage to the turret when the line snaps: " + capstanSnapDamage.ToString("0"));
                capstanSnapDamage = Mathf.Round(list.Slider(capstanSnapDamage, 0f, 100f));
                list.GapLine();
            }

            list.Label("This biome's own mechanics (the poured tar moat and fuse-post ignition, the dig-shaft stratum lottery, the dormant "
                      + "tar-beast set-piece, sump-mouse filth-trail telegraphy, the wick-garden crop, and the permanent-dusk weather lock) "
                      + "are not toggled here. The tar-coating, tarred-hediff, glasswalk-slip, warbling-gaslight and glow-multiplier switches "
                      + "live on the shared \"RimMandrake: Environmental Hazards Kit\" mod's own settings screen (Greentide and Miasma read the "
                      + "same switches); the moat-ignition, dig-lottery, beast-bulge dread and mouse filth-trail mechanics have no toggle "
                      + "anywhere yet and are always on wherever their content is deployed.");

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_TheSumpMod : Mod
    {
        public static RM_TheSumpSettings settings;

        public RM_TheSumpMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TheSumpSettings>();
        }

        public override string SettingsCategory()
        {
            return "the Sump";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
