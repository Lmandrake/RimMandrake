using UnityEngine;
using Verse;

namespace RimMandrake.Miasma
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Miasma.
    //
    // Precedent: src/RimMandrake/PoisonForest/Source/RM_PoisonForestMod.cs
    // (the worldgen-rarity slider, since this biome ships a real
    // RM_BiomeWorker_Miasma of its own) and
    // src/RimMandrake/NightsideIce/Source/RM_NightsideIceMod.cs (the
    // honest-about-scope reasoning below).
    //
    // This mod ships six real mechanics (gradient axis, breath-tide surge,
    // stranding pools, weather lock + exposure, fever-forged boons, warden/
    // crèche placement), but every one of them is implemented by classes in
    // the SHARED mandrake.rm.environmentalhazards assembly, gated by THAT
    // mod's own static toggles (RM_EnvironmentalHazardsSettings) —
    // strandingPoolsEnabled, wardenCrecheScattererEnabled,
    // crecheDespoilMemoryEnabled and biomeGlowMultiplierEnabled are already
    // shared with Greentide and Sump (both also carry
    // RM_StrandingPoolsExtension). Duplicating a Miasma-only copy of any of
    // those switches here would either do nothing (the shared class only
    // ever reads the shared statics) or silently diverge from what that
    // mod's own settings screen already promises a player. So this screen
    // ships only the standard worldgen-rarity slider every biome-worker mod
    // ships, plus an honest pointer to where the mechanic toggles actually
    // live — a per-mechanic toggle for content this screen does not itself
    // gate would be a settings screen that lies (NightsideIce's own
    // reasoning, same shape here).
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MiasmaSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        // 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // WARDEN_MOTHER_SUCCESSION_1: unlike the six mechanics above, self-
        // taming/water-scoped training/succession is implemented entirely in
        // THIS mod's own assembly (RM_WardenMotherSuccession.cs) — no shared
        // EnvironmentalHazards switch to point at instead, so it belongs on
        // this screen. Default = shipped behavior; off degrades gracefully
        // (the young simply stay wild and the crèche is never inherited).
        public static bool wardenSuccessionEnabled = true;
        public static float selfTameChancePerCheck = 0.12f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref wardenSuccessionEnabled, "wardenSuccessionEnabled", true, true);
            Scribe_Values.Look(ref selfTameChancePerCheck, "selfTameChancePerCheck", 0.12f, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Miasma never generates on a new planet. The default "
                       + "places a scattering of hot, salt-crusted delta forest along "
                       + "rivers. Affects planets generated afterwards, never one that "
                       + "already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.Label("This biome's own mechanics — the salinity gradient, the "
                      + "breath-tide surge, stranding pools, the weather lock and "
                      + "exposure hediff, fever-forged boons, and warden/crèche "
                      + "placement — are togglable per-mechanic in the shared "
                      + "\"RimMandrake: Environmental Hazards Kit\" mod's own settings "
                      + "screen, not here: Greentide and Sump read those exact same "
                      + "switches, so a second, Miasma-only copy of them on this "
                      + "screen would either do nothing or quietly disagree with that "
                      + "one.");
            list.GapLine();

            list.CheckboxLabeled("Warden mother young: self-taming and succession",
                ref wardenSuccessionEnabled,
                "A stranded young may quietly self-tame if the player never harms one "
                + "of its crèche-mates, becomes trainable for water-bound work only, "
                + "and can inherit the crèche if the mother dies of old age. Off: the "
                + "young stay wild and the crèche is never inherited.");
            if (wardenSuccessionEnabled)
            {
                list.Label("  Self-tame chance per check: " + (selfTameChancePerCheck * 100f).ToString("0") + "%");
                selfTameChancePerCheck = list.Slider(selfTameChancePerCheck, 0.01f, 0.5f);
            }

            list.End();
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

    public class RM_MiasmaMod : Mod
    {
        public static RM_MiasmaSettings settings;

        public RM_MiasmaMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_MiasmaSettings>();
        }

        public override string SettingsCategory()
        {
            return "the Miasma";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
