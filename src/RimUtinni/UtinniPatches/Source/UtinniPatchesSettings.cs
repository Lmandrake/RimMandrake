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
    // BLUE_DESERT_LIFE_AUTHORING_1's six toggles/one slider MOVED OUT
    // (BLUEDESERT_RM_MOD_BUILD_1, 2026-09-25) to
    // src/RimMandrake/BlueDesert/Source/RM_BlueDesertMod.cs's own
    // RM_BlueDesertSettings, alongside BlueDesertLife.cs itself — that mod now
    // exists to own them. Same field names, same defaults; no behavior change
    // for an existing save.
    public class UtinniPatchesSettings : ModSettings
    {
        public static bool ambientShrineDoctrineEnabled = true;
        public static bool geothermalDensityFieldEnabled = true;
        public static float geothermalMountainFalloffDeg = 20f;
        public static bool utinniWorldIconEnabled = true;

        // SUMP_UTINNI_LAYER_1 §2 — "the holy act": gates the flame statue's
        // "perform the sun-rite" Use interaction (Patches/
        // FlameStatuary_HolyAct.xml, via PatchOperationSettingGate). Off:
        // RM_FlameStatuary stays exactly the plain secular art piece
        // SUMP_GASLIGHT_1 shipped. Takes effect on the next game start (the
        // def is already built by the time a settings change is read).
        public static bool holyFlameActEnabled = true;

        // GREATBOLE_HARVEST_LADDER_1 — "a number is the experience" case for
        // all three of the greatbole's own thresholds (RUT_
        // CompGreatboleHarvestLadder reads these instead of hardcoding
        // 0.40/0.60/0.70), plus the one on/off the spec's own §12 asks for:
        // "toggles for the catastrophe and the breeding." The breeding
        // toggle is NOT duplicated here — RM_CreatureBehaviorsSettings.
        // verminBreedingEnabled (that kit's own existing master switch)
        // already gates the grubs' breeder comp; a second toggle in a
        // different mod's settings for the same comp would just be two
        // switches wired to one wire.
        public static float greatboleShakingThreshold = 0.40f;
        public static float greatboleHealingThreshold = 0.60f;
        public static float greatboleCatastropheThreshold = 0.70f;
        public static bool greatboleCatastropheEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ambientShrineDoctrineEnabled, "ambientShrineDoctrineEnabled", true);
            Scribe_Values.Look(ref geothermalDensityFieldEnabled, "geothermalDensityFieldEnabled", true);
            Scribe_Values.Look(ref geothermalMountainFalloffDeg, "geothermalMountainFalloffDeg", 20f);
            Scribe_Values.Look(ref utinniWorldIconEnabled, "utinniWorldIconEnabled", true);
            Scribe_Values.Look(ref holyFlameActEnabled, "holyFlameActEnabled", true);
            Scribe_Values.Look(ref greatboleShakingThreshold, "greatboleShakingThreshold", 0.40f);
            Scribe_Values.Look(ref greatboleHealingThreshold, "greatboleHealingThreshold", 0.60f);
            Scribe_Values.Look(ref greatboleCatastropheThreshold, "greatboleCatastropheThreshold", 0.70f);
            Scribe_Values.Look(ref greatboleCatastropheEnabled, "greatboleCatastropheEnabled", true);
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

            list.CheckboxLabeled("Flame statue holy act", ref holyFlameActEnabled,
                "A colonist can perform the sun-rite at a flame statue, honoring Sh'kaar the "
              + "All-Searing — an ideoligion with the Ritualist meme can hold this as a "
              + "precept. Off: the flame statue stays a plain secular art piece. Takes effect "
              + "on the next game start.");

            // Blue Desert hydrocarbon life settings (dorrak/krissek/vekkit, the fractal
            // flora, cold wax) moved to the Blue Desert mod's own settings screen —
            // BLUEDESERT_RM_MOD_BUILD_1.

            list.GapLine();
            list.Label("Greatbole harvest ladder — fraction of the bole's own footprint removed.");
            list.Label("The Great Shaking: " + (greatboleShakingThreshold * 100f).ToString("0") + "% removed");
            greatboleShakingThreshold = list.Slider(greatboleShakingThreshold, 0.1f, 0.9f);
            list.Label("The violent healing: " + (greatboleHealingThreshold * 100f).ToString("0") + "% removed");
            greatboleHealingThreshold = list.Slider(greatboleHealingThreshold, 0.1f, 0.95f);
            list.CheckboxLabeled("The catastrophe can happen", ref greatboleCatastropheEnabled,
                "Off: a greatbole never dies from being mined out, no matter how much of its "
              + "footprint is removed. The Great Shaking and the violent healing still fire.");
            list.Label("The catastrophe: " + (greatboleCatastropheThreshold * 100f).ToString("0") + "% removed");
            greatboleCatastropheThreshold = list.Slider(greatboleCatastropheThreshold, 0.1f, 0.99f);

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
