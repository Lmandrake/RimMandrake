using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // STILLSAND_PRECIOUS_CAVES_1 spec 6: toggle the genstep, the rockless tor and
    // each table row; a weight slider per row. Kept in its own file and scribed
    // under its own keys so RM_StillsandSettings only has to call Expose() and
    // Draw() — the Stillsand settings class is shared by several items' work.
    //
    // Defaults are shipped behaviour: everything on, each row at its def's own
    // weight. All toggles act on NEW maps only; a map already generated keeps
    // its rock and its cave.
    public static class RM_PreciousCaveSettings
    {
        public static bool genStepEnabled = true;
        public static bool yardangShapingEnabled = true;
        public static bool torEnabled = true;
        public static float torChance = 0.25f;

        // STILLSAND_CAVE_AS_PLACE_1. Preservation acts live on every cave; the others on NEW maps.
        public static bool preservationEnabled = true;
        public static bool dripEnabled = true;
        public static bool wallRingEnabled = true;
        public static bool tribalMarkEnabled = true;

        // Per-row overrides keyed by RM_PreciousCaveDef.defName. A row absent
        // from either dictionary uses its def's own default (enabled, def.weight).
        public static Dictionary<string, bool> rowEnabled = new Dictionary<string, bool>();
        public static Dictionary<string, float> rowWeight = new Dictionary<string, float>();

        public static bool RowEnabled(RM_PreciousCaveDef def)
        {
            return def != null && (!rowEnabled.TryGetValue(def.defName, out bool on) || on);
        }

        public static float RowWeight(RM_PreciousCaveDef def)
        {
            if (def == null)
            {
                return 0f;
            }
            return rowWeight.TryGetValue(def.defName, out float w) ? w : def.weight;
        }

        public static void Expose()
        {
            Scribe_Values.Look(ref genStepEnabled, "preciousCaves_genStepEnabled", true);
            Scribe_Values.Look(ref yardangShapingEnabled, "preciousCaves_yardangShapingEnabled", true);
            Scribe_Values.Look(ref torEnabled, "preciousCaves_torEnabled", true);
            Scribe_Values.Look(ref torChance, "preciousCaves_torChance", 0.25f);
            Scribe_Values.Look(ref preservationEnabled, "preciousCaves_preservationEnabled", true);
            Scribe_Values.Look(ref dripEnabled, "preciousCaves_dripEnabled", true);
            Scribe_Values.Look(ref wallRingEnabled, "preciousCaves_wallRingEnabled", true);
            Scribe_Values.Look(ref tribalMarkEnabled, "preciousCaves_tribalMarkEnabled", true);
            Scribe_Collections.Look(ref rowEnabled, "preciousCaves_rowEnabled", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref rowWeight, "preciousCaves_rowWeight", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                rowEnabled = rowEnabled ?? new Dictionary<string, bool>();
                rowWeight = rowWeight ?? new Dictionary<string, float>();
            }
        }

        public static void Draw(Listing_Standard list)
        {
            list.GapLine();
            list.Label("The rare rock and its precious cave (new maps only)");
            list.CheckboxLabeled("Carve a cave into the map's largest outcrop", ref genStepEnabled,
                "Off: the Stillsand generates its rock as before, with no cave, no table roll and no landing letter.");
            list.CheckboxLabeled("Shape the outcrop as a wind-aligned yardang", ref yardangShapingEnabled,
                "Trims and fills the largest outcrop into a long, tapering ridge laid along the one wind. Off: the outcrop keeps its generated shape; the cave is still carved.");
            list.CheckboxLabeled("Seat a small tor on rockless maps", ref torEnabled,
                "When a map has no rock at all, sometimes raise one small yardang tor so the map still has its landmark.");
            if (torEnabled)
            {
                list.Label("Rockless-map tor chance: " + torChance.ToStringPercent());
                torChance = list.Slider(torChance, 0f, 1f);
            }

            list.CheckboxLabeled("Nothing rots in the cave", ref preservationEnabled,
                "Corpses and food lying on a roofed cave cell do not rot, and desiccated remains stay. Acts live, on existing caves too. Off: vanilla rot resumes.");
            list.CheckboxLabeled("The cave drips", ref dripEnabled,
                "Each new cave carries one ambient water-drip sound, the only water sound in the biome. New maps only.");
            list.CheckboxLabeled("Lens grotto: grown-biosilica walls", ref wallRingEnabled,
                "The lens grotto rings its chamber with mineable biosilica wall. Off: the grotto is bare rock. New maps only.");
            list.CheckboxLabeled("Taken cave: tribal mark on the wall", ref tribalMarkEnabled,
                "The emptied cave carries its own tribal glyph. New maps only.");

            list.Label("What the cave holds (one weighted roll per cave):");
            foreach (RM_PreciousCaveDef def in DefDatabase<RM_PreciousCaveDef>.AllDefsListForReading)
            {
                Rect row = list.GetRect(Text.LineHeight);
                Rect left = row.LeftPart(0.45f);
                Rect right = row.RightPart(0.53f);
                bool on = RowEnabled(def);
                Widgets.CheckboxLabeled(left, def.LabelCap, ref on);
                rowEnabled[def.defName] = on;
                float w = RowWeight(def);
                float nw = Widgets.HorizontalSlider(right, w, 0f, 10f, true,
                    "weight " + w.ToString("0.0"), null, null, 0.1f);
                if (!Mathf.Approximately(nw, w))
                {
                    rowWeight[def.defName] = nw;
                }
                list.Gap(2f);
            }
        }
    }
}
