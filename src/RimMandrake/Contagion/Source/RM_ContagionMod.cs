using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: every mod ships a real
    // settings screen. CONTAGION_GENOME_ORGAN_GROWING_1 (2026-09-26) added the
    // mod's first real mechanic — the amoeba genome/organ-growing loop — so
    // this now also carries that feature's own on/off toggle, default =
    // shipped behaviour (on).
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ContagionSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // CONTAGION_GENOME_ORGAN_GROWING_1: master toggle for the genome
        // sample extraction recipe and the amoeba-injection interaction.
        // Off degrades gracefully — the recipe refuses and the float-menu
        // option simply never appears.
        public static bool genomeOrganGrowingEnabled = true;

        // CONTAGION_UNFINISHED_SPAWNER_1: master toggle for RM_BloodyMess's
        // CompSpawnerUnfinished. Off degrades gracefully — the comp's CompTick
        // simply never spawns; any Unfinished already on the map keep living
        // out their (short) lives normally.
        public static bool unfinishedSpawnerEnabled = true;

        // CONTAGION_MECHANICS_BUILD_1 Part 1 — the Burn and the Bloom. Only
        // ever acts on a map whose biome carries RM_ContagionSkyExtension.
        // Off: no Burn is ever scheduled; the Bloom weather still rolls from
        // the biome's commonalities (it is plain weather).
        public static bool burnEnabled = true;
        public static bool burnTellsEnabled = true;
        // Multiplier on how often Burns come (1 = shipped: one every ~3 days).
        public static float burnFrequency = 1f;
        // Multiplier on the Burn's damage to natives and dose to visitors.
        public static float burnDamageFactor = 1f;

        // CONTAGION_MECHANICS_BUILD_1 Parts 3/4 — the Helix devices.
        // Repulsor off: the device is inert furniture (no warmup, no effect).
        public static bool cloudRepulsorEnabled = true;
        // Sunbeam damage multiplier against Contagion natives (1 = no bonus).
        public static float sunbeamNativeFactor = 6f;

        // CONTAGION_MECHANICS_BUILD_1 Part 2 — the Coalescence. Off: none
        // forms, and an existing one stops growing, absorbing and emitting
        // (it still dies to the next Burn).
        public static bool coalescenceEnabled = true;

        // CONTAGION_GROWN_LIMBS_BUILD_1: off removes grown limbs from the
        // Monstrous gestation roll (a Monstrous sample then grows the normal
        // organ batch). Limbs already installed keep working.
        public static bool grownLimbsEnabled = true;

        // CONTAGION_GPT_ENRICHMENT_1 part 1 — Draftprints. Off: no sampling
        // option, no Helix contract is offered, and existing prints cannot be
        // transmitted (they keep their trade value).
        public static bool draftprintsEnabled = true;
        // Chance a conscious Unfinished turns manhunter on its sampler.
        public static float draftprintProvokeChance = 0.35f;
        // Multiplier on the silver a Helix contract pays.
        public static float helixContractRewardFactor = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref genomeOrganGrowingEnabled, "genomeOrganGrowingEnabled", true, true);
            Scribe_Values.Look(ref unfinishedSpawnerEnabled, "unfinishedSpawnerEnabled", true, true);
            Scribe_Values.Look(ref burnEnabled, "burnEnabled", true, true);
            Scribe_Values.Look(ref burnTellsEnabled, "burnTellsEnabled", true, true);
            Scribe_Values.Look(ref burnFrequency, "burnFrequency", 1f, true);
            Scribe_Values.Look(ref burnDamageFactor, "burnDamageFactor", 1f, true);
            Scribe_Values.Look(ref cloudRepulsorEnabled, "cloudRepulsorEnabled", true, true);
            Scribe_Values.Look(ref sunbeamNativeFactor, "sunbeamNativeFactor", 6f, true);
            Scribe_Values.Look(ref coalescenceEnabled, "coalescenceEnabled", true, true);
            Scribe_Values.Look(ref grownLimbsEnabled, "grownLimbsEnabled", true, true);
            Scribe_Values.Look(ref draftprintsEnabled, "draftprintsEnabled", true, true);
            Scribe_Values.Look(ref draftprintProvokeChance, "draftprintProvokeChance", 0.35f, true);
            Scribe_Values.Look(ref helixContractRewardFactor, "helixContractRewardFactor", 1f, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the screen outgrew one page with the mechanics build.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeRarityFactor" }))
            {
                list.Label("Biome rarity: " + RarityLabel());
                list.Label("At 0 the Contagion never generates on a new planet. "
                           + "The default places a handful of rare, hot, storm-roofed peaks. "
                           + "Affects planets generated afterwards, never one that already exists.");
                biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Genome growing and the Unfinished", RimMandrake.Shared.SettingScope.Now, new[] { "genomeOrganGrowingEnabled", "unfinishedSpawnerEnabled", "grownLimbsEnabled" }))
            {
                list.CheckboxLabeled(
                    "Amoeba genome/organ growing enabled",
                    ref genomeOrganGrowingEnabled,
                    "Lets a colonist extract a genome sample and inject it into a Contagion "
                    + "amoeba (the bloody mess), which gestates a one-time batch of organs matched "
                    + "to that colonist and dies producing it. Off removes the surgery recipe "
                    + "and the injection option entirely.");
                list.CheckboxLabeled(
                    "The Unfinished spawner enabled",
                    ref unfinishedSpawnerEnabled,
                    "Lets the Contagion's bloody mess periodically bud a short-lived "
                    + "Unfinished chimera nearby — random-limb, days-long-lived, dissolving to "
                    + "goo on death. Off stops new ones from budding; any already alive keep "
                    + "living out their (short) lives normally.");
                list.CheckboxLabeled(
                    "Grown limbs enabled",
                    ref grownLimbsEnabled,
                    "Monstrous genome samples (the Coalescence's death-spill) gestate one grown "
                    + "limb, rolled at random: a Pillar Arm, a Lash, an Eyeburst, a Caudal Spring or a Bellows. Each is a real trade, never "
                    + "an upgrade. Off: a Monstrous sample grows the normal organ batch. Limbs "
                    + "already installed keep working.");
                list.GapLine();
            }

            if (Group(list, "The Burn", RimMandrake.Shared.SettingScope.Now, new[] { "burnEnabled", "burnTellsEnabled", "burnDamageFactor" }))
            {
                list.CheckboxLabeled(
                    "The Burn enabled",
                    ref burnEnabled,
                    "Rare tears in the Contagion's storm: the red fog lifts, ranged fire works, "
                    + "and raw UV scorches everything under open sky — natives burn and dive for "
                    + "roof, canopy or water; visitors take a sunscald dose. Only ever happens on a "
                    + "Contagion map. Off: the storm never tears.");
                list.CheckboxLabeled(
                    "Burn tells enabled",
                    ref burnTellsEnabled,
                    "Shortly before a Burn the gawpsacks stop and settle, puffing, as one — "
                    + "the only forecast the valley gives. Off: Burns arrive unannounced.");
                list.Label("Burn damage: " + burnDamageFactor.ToString("0.00") + "x (0 = weather only, no harm)");
                burnDamageFactor = list.Slider(burnDamageFactor, 0f, 3f);
                list.GapLine();
            }

            if (Group(list, "Burn frequency", RimMandrake.Shared.SettingScope.NextPulse, new[] { "burnFrequency" }))
            {
                list.Label("Burn frequency: " + burnFrequency.ToString("0.00") + "x (1 = one every ~3 days)");
                burnFrequency = list.Slider(burnFrequency, 0.1f, 4f);
                list.GapLine();
            }

            if (Group(list, "The Coalescence", RimMandrake.Shared.SettingScope.Now, new[] { "coalescenceEnabled" }))
            {
                list.CheckboxLabeled(
                    "The Coalescence enabled",
                    ref coalescenceEnabled,
                    "During a long Bloom the Contagion can gather itself into one giant organism "
                    + "that absorbs the Unfinished, grows through three forms and sends out mad ones. "
                    + "Any Burn kills it, spilling genome samples. With the Burn switched off only "
                    + "damage or a Cloud Repulsor can kill it. Off: none forms.");
                list.GapLine();
            }

            if (Group(list, "Draftprints", RimMandrake.Shared.SettingScope.Now, new[] { "draftprintsEnabled", "draftprintProvokeChance" }))
            {
                list.CheckboxLabeled(
                    "Draftprints enabled",
                    ref draftprintsEnabled,
                    "A colonist can walk up to a living Unfinished and scan it into a draftprint "
                    + "recording its limbs, its most extreme stat and what failed on it. The Helix "
                    + "post contracts for particular combinations and buy matching prints. Off: no "
                    + "sampling, no contracts; prints already made keep their trade value.");
                list.Label("Sampling provokes a conscious Unfinished: " + draftprintProvokeChance.ToStringPercent()
                           + " (downed ones never fight back)");
                draftprintProvokeChance = list.Slider(draftprintProvokeChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Helix contract pay", RimMandrake.Shared.SettingScope.NextPulse, new[] { "helixContractRewardFactor" }))
            {
                list.Label("Helix contract pay: " + helixContractRewardFactor.ToString("0.00") + "x");
                helixContractRewardFactor = list.Slider(helixContractRewardFactor, 0.25f, 4f);
                list.GapLine();
            }

            if (Group(list, "Helix devices", RimMandrake.Shared.SettingScope.Now, new[] { "cloudRepulsorEnabled", "sunbeamNativeFactor" }))
            {
                list.CheckboxLabeled(
                    "Cloud Repulsor enabled",
                    ref cloudRepulsorEnabled,
                    "The Helix device: once warmed up and powered it forces the Burn on a "
                    + "Contagion map (its harm still follows the Burn settings above), and holds "
                    + "the sky clear of rain and fog anywhere else. Off: the device does nothing.");
                list.Label("Sunbeam vs Contagion natives: " + sunbeamNativeFactor.ToString("0.0") + "x (1 = no bonus)");
                sunbeamNativeFactor = list.Slider(sunbeamNativeFactor, 1f, 12f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        // Starts tall so the first frame never column-wraps; then tracks the
        // listing's real height.
        private static float viewHeight = 2000f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_ContagionSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_ContagionSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. A search matches the section title or any of its setting names. Scope AUDITED per setting against its
        /// read site (2026-10-10): the biome rarity is read by the worldgen biome worker ([new maps only]); the Burn gap length is rolled when the next Burn is scheduled and the Helix contract pay when a contract is generated ([next pulse]); every other setting is read by a tick, recipe, float-menu option, comp or damage worker ([now]).</summary>
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
            // tagOverride "[next game start]": the kit has no such scope; these are read while defs load or when a game loads.
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
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

    public class RM_ContagionMod : Mod
    {
        public static RM_ContagionSettings settings;

        public RM_ContagionMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_ContagionSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Contagion";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
