using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.BlueDesert
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Blue Desert.
    //
    // Precedent: src/RimMandrake/Abyss/Source/RM_AbyssMod.cs.
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

        // BLUEDESERT_MECHANICS_BUILD_1 §1 (RM_VhaulkDetonation.cs). Both
        // also sit under nativeDetonationsEnabled.
        public static bool vhaulkHeatGateEnabled = true;
        public static bool vhaulkEmpTrapEnabled = true;

        // BLUEDESERT_MECHANICS_BUILD_1 §4. ruledWeathersEnabled drives
        // RM_BlueDesertWeatherTable (biome-local commonality, live);
        // hazeExposureEnabled is the RM_MechanicGates predicate behind
        // RM_BlueDesertHazeCarrier's gate key.
        public static bool ruledWeathersEnabled = true;
        public static bool hazeExposureEnabled = true;

        // BLUEDESERT_MECHANICS_BUILD_1 §3 (RM_BlueIceThaw.cs).
        public static bool thawRollEnabled = true;

        // BLUEDESERT_MECHANICS_BUILD_1 §5 (CompPlantCharge.PlayCrackCue).
        public static bool crackCueEnabled = true;

        // BLUEDESERT_MECHANICS_BUILD_1 §6 (RM_MurrekDrift.cs).
        public static bool murrekReseedEnabled = true;

        // BLUEDESERT_GPT_ENRICHMENT_1 §1 (RM_ColdSink.cs).
        public static bool coldSinkEnabled = true;
        public static float coldSinkCapacityFactor = 1f;

        // BLUEDESERT_GPT_ENRICHMENT_1 §2 (RM_AblationSalvage.cs).
        public static bool ablationSalvageEnabled = true;
        public static float ablationPaceFactor = 1f;

        // BLUEDESERT_GPT_ENRICHMENT_1 §4 (RM_VhaulkRoad.cs).
        public static bool vhaulkRoadEnabled = true;
        public static float vhaulkRoadDaysFactor = 1f;
        public static bool vhaulkDepartsEnabled = true;
        public static float vhaulkStayDaysFactor = 1f;

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
            Scribe_Values.Look(ref vhaulkHeatGateEnabled, "vhaulkHeatGateEnabled", true);
            Scribe_Values.Look(ref vhaulkEmpTrapEnabled, "vhaulkEmpTrapEnabled", true);
            Scribe_Values.Look(ref ruledWeathersEnabled, "ruledWeathersEnabled", true);
            Scribe_Values.Look(ref hazeExposureEnabled, "hazeExposureEnabled", true);
            Scribe_Values.Look(ref thawRollEnabled, "thawRollEnabled", true);
            Scribe_Values.Look(ref crackCueEnabled, "crackCueEnabled", true);
            Scribe_Values.Look(ref murrekReseedEnabled, "murrekReseedEnabled", true);
            Scribe_Values.Look(ref coldSinkEnabled, "coldSinkEnabled", true);
            Scribe_Values.Look(ref coldSinkCapacityFactor, "coldSinkCapacityFactor", 1f);
            Scribe_Values.Look(ref ablationSalvageEnabled, "ablationSalvageEnabled", true);
            Scribe_Values.Look(ref ablationPaceFactor, "ablationPaceFactor", 1f);
            Scribe_Values.Look(ref vhaulkRoadEnabled, "vhaulkRoadEnabled", true);
            Scribe_Values.Look(ref vhaulkRoadDaysFactor, "vhaulkRoadDaysFactor", 1f);
            Scribe_Values.Look(ref vhaulkDepartsEnabled, "vhaulkDepartsEnabled", true);
            Scribe_Values.Look(ref vhaulkStayDaysFactor, "vhaulkStayDaysFactor", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the enrichment toggles pushed the list past one screen.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(inRect.height, lastListHeight));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

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
            list.CheckboxLabeled("Vhaulk: only fire detonates the cistern", ref vhaulkHeatGateEnabled,
                "On: the vhaulk explodes only when fire, a burn, heatstroke or lightning kills it; a "
              + "kinetic or cold kill leaves the carcass intact. Off: any death detonates it.");
            list.CheckboxLabeled("Vhaulk: EMP detonates it alive", ref vhaulkEmpTrapEnabled,
                "On: any EMP hit on a living vhaulk sets it off at once. Off: EMP does nothing to it.");
            list.CheckboxLabeled("Blue Desert weathers", ref ruledWeathersEnabled,
                "The Haze, ice-sand drift and ice fog in the Blue Desert's weather rotation. Off: "
              + "the Blue Desert is always clear. Takes effect at the next weather change.");
            list.CheckboxLabeled("Haze film exposure", ref hazeExposureEnabled,
                "Colonists outdoors during the Haze pick up a mild chilling film. Off: nobody new "
              + "picks it up.");
            list.CheckboxLabeled("Blue-ice thaw finds", ref thawRollEnabled,
                "Every few blue-ice blocks mined, the warmed face may give up old fallen debris "
              + "(metal, wreckage). Off: blue ice mines cleanly with no roll.");
            list.CheckboxLabeled("Crack warning before flora detonates", ref crackCueEnabled,
                "A warming charge-plant cracks audibly one step before it goes off. Off: no warning "
              + "sound; the detonation timing is unchanged.");
            list.CheckboxLabeled("Murrek bury in fresh drifts", ref murrekReseedEnabled,
                "When an ice-sand drift ends, murrek dig into the new drifts and lie hidden until prey "
              + "comes close, and a few new ones may settle in away from the colony. Clearing the "
              + "sand flushes a buried one. Off: murrek never bury; any already buried surface.");

            list.Label("Warm-detonation threshold: " + warmDetonationThresholdC.ToString("0") + " °C");
            warmDetonationThresholdC = list.Slider(warmDetonationThresholdC, -1f, 15f);
            list.GapLine();

            list.CheckboxLabeled("Blue-ice cold rack", ref coldSinkEnabled,
                "A rack loaded with blue ice keeps an enclosed room at its setting by melting the ice, "
              + "with no power, and drips the melt into cans of clean water. Off: the rack holds its "
              + "ice and does nothing.");
            list.Label("Cold held per block of blue ice: x" + coldSinkCapacityFactor.ToString("0.00"));
            coldSinkCapacityFactor = list.Slider(coldSinkCapacityFactor, 0.25f, 4f);

            list.CheckboxLabeled("The ablation line gives things up", ref ablationSalvageEnabled,
                "Now and then a crack sounds near the plateau's edge; hours later something shows under "
              + "the ice while scavengers circle it, and then wreckage, sky-metal or a long-dead body "
              + "comes to the surface. Off: this event never happens.");
            list.Label("How slowly a find surfaces: x" + ablationPaceFactor.ToString("0.00"));
            ablationPaceFactor = list.Slider(ablationPaceFactor, 0.25f, 3f);

            list.CheckboxLabeled("Vhaulk road", ref vhaulkRoadEnabled,
                "A walking vhaulk presses a pale road into the ice that lasts a few days, crops the plants "
              + "it passes, trails frost and booms now and then. Off: it walks like any animal.");
            list.Label("How long a vhaulk road lasts: x" + vhaulkRoadDaysFactor.ToString("0.00"));
            vhaulkRoadDaysFactor = list.Slider(vhaulkRoadDaysFactor, 0.25f, 4f);
            list.CheckboxLabeled("Vhaulk moves on", ref vhaulkDepartsEnabled,
                "A wild vhaulk walks off the map after a few days, with a letter. Off: it stays, like "
              + "any wild animal.");
            list.Label("How long a vhaulk stays: x" + vhaulkStayDaysFactor.ToString("0.00"));
            vhaulkStayDaysFactor = list.Slider(vhaulkStayDaysFactor, 0.25f, 4f);

            lastListHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPosition;
        private static float lastListHeight = 1400f;
    }

    public class RM_BlueDesertMod : Mod
    {
        public static RM_BlueDesertSettings settings;

        public RM_BlueDesertMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BlueDesertSettings>();

            RM_MechanicGates.Register(
                HazeExposureGateKey,
                () => RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.hazeExposureEnabled);
        }

        // Must match RM_BlueDesertHazeCarrier's RM_MechanicGateExtension.gateKey.
        public const string HazeExposureGateKey = "bluedesert.hazeExposure";

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_BlueDesertWeatherTable.Apply();
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
