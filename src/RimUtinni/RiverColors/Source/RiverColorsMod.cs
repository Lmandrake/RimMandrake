// MOD_OPTIONS_RETROFIT_1 — Mod Settings for River Colors.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
//
// The one mechanism (Patch_WorldDrawLayer_Paths_GeneratePaths) substitutes a
// per-tile gradient colour for the world map's river mesh. The three hardcoded
// anchor colours (headwater/jungle/terminus) are exposed as RGB sliders with a
// live swatch; a master toggle reverts to vanilla's single flat river colour.
// WORLDGEN-AFFECTING NOTE: none of this touches worldgen — it only repaints the
// planet-view river mesh, which RiverGradient already rebuilds lazily whenever
// Find.World changes, so a slider change is visible immediately, live game or not.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RiverColors
{
    public class RiverColorsSettings : ModSettings
    {
        public static bool enabled = true;

        public static Color headwaterColor = new Color(0xE0 / 255f, 0x31 / 255f, 0x1C / 255f);
        public static Color jungleColor = new Color(0x7A / 255f, 0x7A / 255f, 0x2E / 255f);
        public static Color terminusColor = new Color(0x3D / 255f, 0x4A / 255f, 0x52 / 255f);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref headwaterColor, "headwaterColor",
                new Color(0xE0 / 255f, 0x31 / 255f, 0x1C / 255f));
            Scribe_Values.Look(ref jungleColor, "jungleColor",
                new Color(0x7A / 255f, 0x7A / 255f, 0x2E / 255f));
            Scribe_Values.Look(ref terminusColor, "terminusColor",
                new Color(0x3D / 255f, 0x4A / 255f, 0x52 / 255f));
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Colour rivers by position", ref enabled,
                "Off: rivers draw with the game's own single flat colour, as if this mod "
              + "were not installed. On by default.");
            list.GapLine();

            if (enabled)
            {
                list.Label("Red at the headwaters, fading through this colour in the jungle "
                  + "reaches, ending in this colour at the dead-river termini.");
                ColorSection(list, "Headwater colour (red spore-toxin country)", ref headwaterColor);
                ColorSection(list, "Jungle colour (brackish green/brown)", ref jungleColor);
                ColorSection(list, "Terminus colour (toxic brown/blue salt flats)", ref terminusColor);
            }

            list.End();
        }

        private static void ColorSection(Listing_Standard list, string label, ref Color color)
        {
            list.Label(label);

            Rect row = list.GetRect(24f);
            Rect swatch = row.LeftPart(0.12f);
            Widgets.DrawBoxSolid(swatch, color);
            Widgets.DrawBox(swatch);

            float r = color.r, g = color.g, b = color.b;
            r = list.Slider(r, 0f, 1f);
            g = list.Slider(g, 0f, 1f);
            b = list.Slider(b, 0f, 1f);
            color = new Color(r, g, b);
            list.Gap();
        }
    }

    public class RiverColorsMod : Mod
    {
        public static RiverColorsSettings settings;

        public RiverColorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RiverColorsSettings>();
        }

        public override string SettingsCategory()
        {
            return "River Colors";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
