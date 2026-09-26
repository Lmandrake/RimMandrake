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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref tarVaultEnabled, "tarVaultEnabled", true, true);
            Scribe_Values.Look(ref deepBlackMereEnabled, "deepBlackMereEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Sump never generates on a new planet. The default "
                       + "places a scattering of low, flat, permanently-dusky tar "
                       + "basins. Affects planets generated afterwards, never one "
                       + "that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.CheckboxLabeled("Tar vault seals contents (no rot; extraction needs solvent)", ref tarVaultEnabled,
                "The tar vault (RUT_TarVault) freezes rot on anything sealed inside it. "
              + "Off: it behaves like an ordinary shelf, no sealing, no solvent gate.");
            list.GapLine();

            list.CheckboxLabeled("Generate the Deep Black mere", ref deepBlackMereEnabled,
                "A landmark-scale unbroken expanse of deep tar generates once per Sump map, well "
              + "clear of the edge -- the biome's own \"ocean\" at map scale, and (via FlowWorks' "
              + "natural-liquid-source rule) an effectively infinite canal source once a channel "
              + "reaches it. Off: the map keeps only the biome's ordinary scattered tar pockets.");
            list.GapLine();

            list.Label("This biome's own mechanics — the poured tar moat and fuse-"
                      + "post ignition, the dig-shaft stratum lottery, the dormant "
                      + "tar-beast set-piece, sump-mouse filth-trail telegraphy, the "
                      + "wick-garden crop, and the permanent-dusk weather lock — are "
                      + "not toggled here. The tar-coating, tarred-hediff, glasswalk-"
                      + "slip, warbling-gaslight and glow-multiplier switches live on "
                      + "the shared \"RimMandrake: Environmental Hazards Kit\" mod's "
                      + "own settings screen (Greentide and Miasma read those exact "
                      + "same switches, so a second copy here would either do nothing "
                      + "or silently disagree with that one); the moat-ignition, dig-"
                      + "lottery, beast-bulge dread and mouse filth-trail mechanics "
                      + "have no toggle anywhere yet — they are simply always-on "
                      + "wherever their content is deployed.");

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
