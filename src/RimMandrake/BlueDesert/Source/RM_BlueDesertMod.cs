using UnityEngine;
using Verse;

namespace RimMandrake.BlueDesert
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Blue Desert.
    //
    // Precedent: src/RimMandrake/ForsakenCrags/Source/RM_ForsakenCragsMod.cs.
    // Unlike that sibling, this biome ships a real mechanics kit already
    // (BlueDesertLife.cs, built by BLUE_DESERT_LIFE_AUTHORING_1), so the six
    // per-mechanic toggles below are the same six fields that used to live on
    // RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings — moved here
    // verbatim (BLUEDESERT_RM_MOD_BUILD_1 §6) now that this mod exists to own
    // them. Every default matches what shipped there, so this move changes no
    // player-visible behavior for an existing save.
    //
    // No worldgen-rarity slider: workerClass stays the vanilla Core
    // BiomeWorker_IceSheet (no donor type to replace), so there is no custom
    // RM_BiomeWorker_BlueDesert scoring function for a rarity factor to gate,
    // same reasoning as RM_NightsideIceSettings.
    // ════════════════════════════════════════════════════════════════════
    public class RM_BlueDesertSettings : ModSettings
    {
        /// <summary>Master switch. Off: the biome and its defs still load
        /// (nothing on a saved game silently disappears) — this only gates
        /// the mechanics below, not spawning or worldgen.</summary>
        public static bool masterEnabled = true;

        public static bool nativeDetonationsEnabled = true;
        public static bool floraChainReactionsEnabled = true;
        public static bool coldWaxWarmReactiveEnabled = true;
        public static bool butaneGutEnabled = true;
        public static bool burnerHaloEnabled = true;
        public static float warmDetonationThresholdC = 5f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref nativeDetonationsEnabled, "nativeDetonationsEnabled", true);
            Scribe_Values.Look(ref floraChainReactionsEnabled, "floraChainReactionsEnabled", true);
            Scribe_Values.Look(ref coldWaxWarmReactiveEnabled, "coldWaxWarmReactiveEnabled", true);
            Scribe_Values.Look(ref butaneGutEnabled, "butaneGutEnabled", true);
            Scribe_Values.Look(ref burnerHaloEnabled, "burnerHaloEnabled", true);
            Scribe_Values.Look(ref warmDetonationThresholdC, "warmDetonationThresholdC", 5f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Blue Desert");
            list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                "Off: RM_BlueDesert still loads and can be assigned to a tile directly, "
              + "but the six mechanics below stop mattering (their own toggles below still "
              + "apply if this is back on).");
            list.GapLine();

            list.CheckboxLabeled("Native detonations", ref nativeDetonationsEnabled,
                "The dorrak's gut-wound kill and the krissek's death blast. Off: both natives "
              + "die like an ordinary animal.");
            list.CheckboxLabeled("Flora chain reactions", ref floraChainReactionsEnabled,
                "The transparent fractal flora detonates when warmed or killed by damage. Off: "
              + "the flora is inert.");
            list.CheckboxLabeled("Warm-reactive cold wax", ref coldWaxWarmReactiveEnabled,
                "Cold wax ruined by a warm room starts its own wick. Off: ruined cold wax just "
              + "decays, it does not explode.");
            list.CheckboxLabeled("Butane gut for foreign grazers", ref butaneGutEnabled,
                "A water-based animal that eats the flora builds up a lethal, explosive toxin. "
              + "Off: foreign grazers can eat the flora safely.");
            list.CheckboxLabeled("Burner halo VFX", ref burnerHaloEnabled,
                "The krissek's blue-fire halo while it runs, hunts or fights. Off: no halo.");

            list.Label("Warm-detonation threshold: " + warmDetonationThresholdC.ToString("0") + " °C");
            warmDetonationThresholdC = list.Slider(warmDetonationThresholdC, -1f, 15f);

            list.End();
        }
    }

    public class RM_BlueDesertMod : Mod
    {
        public static RM_BlueDesertSettings settings;

        public RM_BlueDesertMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BlueDesertSettings>();
        }

        public override string SettingsCategory()
        {
            return "Blue Desert";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
