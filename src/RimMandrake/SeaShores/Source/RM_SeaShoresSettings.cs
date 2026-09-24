using UnityEngine;
using Verse;

namespace RimMandrake.SeaShores
{
    // MOD_OPTIONS_RETROFIT_1. Four switches, one per mechanic, defaults = shipped
    // behaviour. Fields are INSTANCE fields reached through Cur, not public
    // statics: the bridge's rimworld/update_mod_settings reflects over instance
    // fields on the ModSettings object and refuses a static one outright
    // (found live 2026-09-12 on the Pits pilot).
    public class RM_SeaShoresSettings : ModSettings
    {
        public bool seasCountAsCoast = true;
        public bool generateSeaShores = true;
        public bool seaCatchTables = true;
        public bool healFrozenWorldOnLoad = true;

        private static readonly RM_SeaShoresSettings Defaults = new RM_SeaShoresSettings();

        // Every read goes through here so the patches are safe before (or
        // without) the Mod class being constructed — a null settings object
        // degrades to shipped defaults rather than an NRE inside a Harmony
        // patch, which would be unrecoverable at worldgen time.
        public static RM_SeaShoresSettings Cur => RM_SeaShoresMod.settings ?? Defaults;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seasCountAsCoast, "seasCountAsCoast", true);
            Scribe_Values.Look(ref generateSeaShores, "generateSeaShores", true);
            Scribe_Values.Look(ref seaCatchTables, "seaCatchTables", true);
            Scribe_Values.Look(ref healFrozenWorldOnLoad, "healFrozenWorldOnLoad", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Modded seas count as coastline", ref seasCountAsCoast,
                "A land tile bordering a modded sea reads as coastal: coastal animals spawn there, "
              + "attackers can emerge from the water, and river deltas can form. "
              + "Off: only the vanilla ocean makes a tile coastal.");

            list.CheckboxLabeled("Generate shores on maps beside a modded sea", ref generateSeaShores,
                "Maps on those tiles get a real shore — the sea's own deep and shallow water, "
              + "then the land's beach. Off: the tile may still read as coastal, but the map "
              + "generates with no water at its edge.\n\nAffects world and map generation.");

            list.CheckboxLabeled("Fish the sea's catch table, not the land's", ref seaCatchTables,
                "Fishing a shore made of a modded sea's water pulls that sea's own fish, including "
              + "its rare catches. Off: the land biome's fish are used, as in vanilla.");

            list.GapLine();
            list.CheckboxLabeled("Repair existing worlds on load", ref healFrozenWorldOnLoad,
                "Tile mutators are saved with the world, so a planet created before this mod was "
              + "installed has no shores beside its modded seas and will never regenerate. This "
              + "adds them on load, once, to tiles that have no coastline of any kind yet. Harmless "
              + "to run repeatedly.\n\nAffects an existing saved world.");

            list.End();
        }
    }
}
