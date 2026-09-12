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
    // TWINKLE_FLORA_SPIKE_1 (TwinkleFloraSpike.cs) is a timeboxed feasibility
    // spike that ships compiled but is not wired into any live biome or
    // shipped plant def — nothing in a real game ever runs it, so it gets no
    // settings entry.
    public class UtinniPatchesSettings : ModSettings
    {
        public static bool ambientShrineDoctrineEnabled = true;
        public static bool geothermalDensityFieldEnabled = true;
        public static float geothermalMountainFalloffDeg = 20f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ambientShrineDoctrineEnabled, "ambientShrineDoctrineEnabled", true);
            Scribe_Values.Look(ref geothermalDensityFieldEnabled, "geothermalDensityFieldEnabled", true);
            Scribe_Values.Look(ref geothermalMountainFalloffDeg, "geothermalMountainFalloffDeg", 20f);
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
