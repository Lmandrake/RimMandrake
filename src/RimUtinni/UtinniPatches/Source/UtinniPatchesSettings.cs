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

        // LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1 — worldgen-affecting (new Deeps only).
        public static bool mindstoneGalleryEnabled = true;

        // ZERSIUM_FORGE_BIOME_1 — worldgen-affecting (new Forge maps only).
        public static bool zersiumForgeEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ambientShrineDoctrineEnabled, "ambientShrineDoctrineEnabled", true);
            Scribe_Values.Look(ref geothermalDensityFieldEnabled, "geothermalDensityFieldEnabled", true);
            Scribe_Values.Look(ref geothermalMountainFalloffDeg, "geothermalMountainFalloffDeg", 20f);
            Scribe_Values.Look(ref utinniWorldIconEnabled, "utinniWorldIconEnabled", true);
            Scribe_Values.Look(ref holyFlameActEnabled, "holyFlameActEnabled", true);
            Scribe_Values.Look(ref mindstoneGalleryEnabled, "mindstoneGalleryEnabled", true);
            Scribe_Values.Look(ref zersiumForgeEnabled, "zersiumForgeEnabled", true);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

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
            list.CheckboxLabeled("Mindstone galleries in the Lantern Deeps", ref mindstoneGalleryEnabled,
                "On: in a newly generated Lantern Deep, the rock around one Shard-mind carries a few veins of mindstone, "
              + "the only place on the planet it can be mined. Off: no gallery, and no mindstone anywhere. "
              + "Worldgen-affecting: applies to Deeps generated after the change.");

            list.GapLine();
            list.CheckboxLabeled("Zersium ore in the Forge", ref zersiumForgeEnabled,
                "On: newly generated Forge maps carry a few small seams of zersium ore, the mineral that turns "
              + "steel into durasteel, and the only place on the planet it can be mined. Off: no zersium seams "
              + "anywhere. Worldgen-affecting: applies to Forge maps generated after the change.");

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
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
