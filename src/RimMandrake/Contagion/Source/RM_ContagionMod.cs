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
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the screen outgrew one page with the mechanics build.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Contagion never generates on a new planet. "
                       + "The default places a handful of rare, hot, storm-roofed peaks. "
                       + "Affects planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.Gap();
            list.CheckboxLabeled(
                "Amoeba genome/organ growing enabled",
                ref genomeOrganGrowingEnabled,
                "Lets a colonist extract a genome sample and inject it into a Contagion "
                + "amoeba (the bloody mess), which gestates a one-time batch of organs matched "
                + "to that colonist and dies producing it. Off removes the surgery recipe "
                + "and the injection option entirely.");

            list.Gap();
            list.CheckboxLabeled(
                "The Unfinished spawner enabled",
                ref unfinishedSpawnerEnabled,
                "Lets the Contagion's bloody mess periodically bud a short-lived "
                + "Unfinished chimera nearby — random-limb, days-long-lived, dissolving to "
                + "goo on death. Off stops new ones from budding; any already alive keep "
                + "living out their (short) lives normally.");

            list.GapLine();
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
            list.Label("Burn frequency: " + burnFrequency.ToString("0.00") + "x (1 = one every ~3 days)");
            burnFrequency = list.Slider(burnFrequency, 0.1f, 4f);
            list.Label("Burn damage: " + burnDamageFactor.ToString("0.00") + "x (0 = weather only, no harm)");
            burnDamageFactor = list.Slider(burnDamageFactor, 0f, 3f);
            list.CheckboxLabeled(
                "The Coalescence enabled",
                ref coalescenceEnabled,
                "During a long Bloom the Contagion can gather itself into one giant organism "
                + "that absorbs the Unfinished, grows through three forms and sends out mad ones. "
                + "Any Burn kills it, spilling genome samples. With the Burn switched off only "
                + "damage or a Cloud Repulsor can kill it. Off: none forms.");

            list.CheckboxLabeled(
                "Grown limbs enabled",
                ref grownLimbsEnabled,
                "Monstrous genome samples (the Coalescence's death-spill) gestate one grown "
                + "limb, rolled at random: a Pillar Arm, a Lash, an Eyeburst, a Caudal Spring or a Bellows. Each is a real trade, never "
                + "an upgrade. Off: a Monstrous sample grows the normal organ batch. Limbs "
                + "already installed keep working.");

            list.GapLine();
            list.CheckboxLabeled(
                "Cloud Repulsor enabled",
                ref cloudRepulsorEnabled,
                "The Helix device: once warmed up and powered it forces the Burn on a "
                + "Contagion map (its harm still follows the Burn settings above), and holds "
                + "the sky clear of rain and fog anywhere else. Off: the device does nothing.");
            list.Label("Sunbeam vs Contagion natives: " + sunbeamNativeFactor.ToString("0.0") + "x (1 = no bonus)");
            sunbeamNativeFactor = list.Slider(sunbeamNativeFactor, 1f, 12f);

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        // Starts tall so the first frame never column-wraps; then tracks the
        // listing's real height.
        private static float viewHeight = 2000f;

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
