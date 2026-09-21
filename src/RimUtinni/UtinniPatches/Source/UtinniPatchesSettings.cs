using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for UtinniPatches.
    //
    // Two shipped, worldgen-affecting mechanisms:
    //   1. SHRINE_GUARDIAN_BIOME_GATE_1 (AmbientShrineGuardians.cs) — swaps
    //      the ancient-temple guardian on eight ambient-mechanoid-deny biomes
    //      from a mechanoid/fleshbeast/hive group to a sealed cryptosleep
    //      watch. Fires only during map generation.
    //   2. GEOTHERMAL_DENSITY_FIELD_1 (GeothermalDensityField.cs) — scales
    //      steam geyser count by a world-position density field. Also fires
    //      only during map generation.
    //   3. UTINNI_WORLDMAP_FLIGHT_ICON_1 (Patches/UtinniWorldIcon.xml) — swaps
    //      the gravship's world-map sprite from vanilla's grav-engine glyph to
    //      the Utinni's own ring silhouette. Applied at XML patch time through
    //      PatchOperationSettingGate, so it takes effect on the next game start.
    // TWINKLE_FLORA_SPIKE_1 (TwinkleFloraSpike.cs) is a timeboxed feasibility
    // spike that ships compiled but is not wired into any live biome or
    // shipped plant def — nothing in a real game ever runs it, so it gets no
    // settings entry.
    // BLUE_DESERT_LIFE_AUTHORING_1 (2026-09-21, BlueDesertLife.cs, namespace
    // RimMandrake.BlueDesert) adds six toggles/one slider per the standing Mod
    // Settings rule (MOD_OPTIONS_RETROFIT_1) and the design brief's own §9 table.
    // None of these are worldgen-affecting -- they gate runtime behaviour only.
    public class UtinniPatchesSettings : ModSettings
    {
        public static bool ambientShrineDoctrineEnabled = true;
        public static bool geothermalDensityFieldEnabled = true;
        public static float geothermalMountainFalloffDeg = 20f;
        public static bool utinniWorldIconEnabled = true;

        // BLUE_DESERT_LIFE_AUTHORING_1 (brief §9)
        public static bool nativeDetonationsEnabled = true;
        public static bool floraChainReactionsEnabled = true;
        public static bool coldWaxWarmReactiveEnabled = true;
        public static bool butaneGutEnabled = true;
        public static bool burnerHaloEnabled = true;
        public static float warmDetonationThresholdC = 5f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ambientShrineDoctrineEnabled, "ambientShrineDoctrineEnabled", true);
            Scribe_Values.Look(ref geothermalDensityFieldEnabled, "geothermalDensityFieldEnabled", true);
            Scribe_Values.Look(ref geothermalMountainFalloffDeg, "geothermalMountainFalloffDeg", 20f);
            Scribe_Values.Look(ref utinniWorldIconEnabled, "utinniWorldIconEnabled", true);
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

            list.Label("Both options below are worldgen-affecting — they apply to new maps only.");
            list.GapLine();

            list.CheckboxLabeled("Ambient shrine guardian doctrine", ref ambientShrineDoctrineEnabled,
                "On sparse/dead biomes, ancient temple shrines get a sealed cryptosleep watch "
              + "and scavenged loot instead of a living mechanoid/fleshbeast/hive guard. "
              + "Off: those biomes use the stock vanilla shrine guardian logic.");
            list.GapLine();

            list.CheckboxLabeled("World-position geothermal density", ref geothermalDensityFieldEnabled,
                "Scales steam geyser counts by how close a map is to the sunlit side and to "
              + "dayside mountain ranges. Off: geyser counts use vanilla's own formula only.");
            list.Label("Mountain-range falloff: " + geothermalMountainFalloffDeg.ToString("0") + " degrees");
            geothermalMountainFalloffDeg = list.Slider(geothermalMountainFalloffDeg, 5f, 60f);
            list.GapLine();

            list.CheckboxLabeled("Utinni world-map icon", ref utinniWorldIconEnabled,
                "Draws the Utinni's own ring hull on the planet map while the gravship is in "
              + "flight, at both zoom levels, instead of vanilla's generic grav-engine glyph. "
              + "Off: the vanilla gravship sprite is used. Takes effect on the next game start.");
            list.GapLine();

            list.Label("Blue Desert hydrocarbon life (dorrak, krissek, vekkit, the fractal flora):");

            list.CheckboxLabeled("Native detonations", ref nativeDetonationsEnabled,
                "Dorrak (destroyed gut) and krissek (killed) explode on death. "
              + "Off: these natives die like ordinary animals.");

            list.CheckboxLabeled("Flora chain reactions", ref floraChainReactionsEnabled,
                "Palefloss/glassfern/chimeglobe detonate when killed or when a warm room "
              + "sustains around them. Off: they die like ordinary plants and warm rooms do "
              + "nothing to them.");

            list.CheckboxLabeled("Warm-reactive cold wax", ref coldWaxWarmReactiveEnabled,
                "RM_ColdWax ruined by warm storage detonates. Off: it behaves as an inert "
              + "chemfuel precursor regardless of temperature.");

            list.CheckboxLabeled("Butane gut for foreign grazers", ref butaneGutEnabled,
                "A water-based grazer (e.g. a colonist's muffalo) that eats the flora takes a "
              + "building hydrocarbon toxin. Off: eating the flora is harmless to foreign animals.");

            list.CheckboxLabeled("Burner halo VFX", ref burnerHaloEnabled,
                "The krissek's blue-fire halo shows while it runs fast, hunts, or fights. "
              + "Purely cosmetic -- off if you want it for GPU cost, not balance.");

            list.Label("Warm-detonation threshold: " + warmDetonationThresholdC.ToString("0") + " °C");
            warmDetonationThresholdC = list.Slider(warmDetonationThresholdC, -1f, 15f);

            list.End();
        }
    }

    public class UtinniPatchesMod : Mod
    {
        public static UtinniPatchesSettings settings;

        public UtinniPatchesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<UtinniPatchesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Utinni Patches";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
