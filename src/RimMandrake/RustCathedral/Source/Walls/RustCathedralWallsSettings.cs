using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RustCathedralWalls
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RustCathedralWalls.
    //
    // Three mechanisms this mod runs, each gated here:
    //   1. GenStep_ScatterCathedralWallTiers (Tiers 1-2) — worldgen-affecting.
    //   2. GenStep_ScatterSacredWalls (Tier 3, faction-owned wall) — worldgen-
    //      affecting, plus the per-map chance it already carries as a field.
    //   3. HarmonyPatch_GateLivePatternMetal (Tier 4, deep-scan biome gate) —
    //      runs live, whenever a deep scanner picks a resource.
    //
    // 🔑 STATIC FIELDS, READ FROM EVERYWHERE. Class name avoids
    // "RustCathedralWallsMod", already taken by the static Harmony-init class
    // in HarmonyPatch_GateLivePatternMetal.cs.
    public class RustCathedralWallsSettings : ModSettings
    {
        public static bool wallTiersEnabled = true;
        public static bool sacredWallsEnabled = true;
        public static float sacredWallChanceMultiplier = 1f;
        public static bool livePatternMetalGateEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wallTiersEnabled, "wallTiersEnabled", true);
            Scribe_Values.Look(ref sacredWallsEnabled, "sacredWallsEnabled", true);
            Scribe_Values.Look(ref sacredWallChanceMultiplier, "sacredWallChanceMultiplier", 1f);
            Scribe_Values.Look(ref livePatternMetalGateEnabled, "livePatternMetalGateEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Worldgen-affecting — applies to new maps only.");
            list.CheckboxLabeled("Cathedral wall tiers (Tiers 1-2)", ref wallTiersEnabled,
                "Scatters the low-tier rust cathedral wall fragments on Rust Cathedral maps.");
            list.CheckboxLabeled("Sacred wall (Tier 3)", ref sacredWallsEnabled,
                "A rare, faction-owned sacred wall segment placed on Rust Cathedral maps.");
            list.Label("Sacred wall chance: " + (sacredWallChanceMultiplier * 100f).ToString("0") + "% of the base rate");
            sacredWallChanceMultiplier = list.Slider(sacredWallChanceMultiplier, 0f, 2f);
            list.GapLine();

            list.Label("Live play");
            list.CheckboxLabeled("Restrict Live Pattern Metal to the Rust Cathedral", ref livePatternMetalGateEnabled,
                "Off: deep scanners anywhere may find Live Pattern Metal, same as an unpatched game.");

            list.End();
        }
    }

    // RUSTCATHEDRAL_RM_MOD_BUILD_1: the standalone RustCathedralWallsSettingsMod
    // wrapper (one Mod-derived class per satellite kit) is RETIRED now that
    // Hum/Walls/Roaches/the biome all ship in one mod, mandrake.rm.rustcathedral.
    // This settings DATA class is unchanged and still read from everywhere it
    // always was; it is now surfaced through the single
    // RimMandrake.RustCathedral.RM_RustCathedralMod settings screen instead of
    // its own category, so GetSettings<RustCathedralWallsSettings>() is called
    // from that Mod's constructor.
}
