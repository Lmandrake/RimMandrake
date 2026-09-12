using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Graffiti.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // Four things this exposes:
    //   1. Painting enabled — master switch for the graffiti-painting joy
    //      activity AND the mental-break painting spree (both funnel
    //      through JoyGiver_PaintGraffiti / JobGiver_GraffitiPaintingSpree,
    //      which simply hand back no job when off — the ThinkTree falls
    //      through to whatever else a pawn would otherwise do, same as any
    //      vanilla JobGiver returning null).
    //   2. Paint interval — how often (in ticks) a painting pawn leaves a
    //      fresh mark while working (JobDriver_PaintGraffiti's hardcoded
    //      250-tick PaintIntervalTicks).
    //   3. Viewer reaction — the mood/thought effect from noticing a mark
    //      nearby (ThoughtWorker_ViewedGraffitiMark).
    //   4. Breach-bias — raiders funneling their breach target toward a
    //      "Come And Take It" taunt mark (BreachBiasHookMod's Harmony
    //      postfix on BreachingGrid.FindBuildingToBreach).
    // ════════════════════════════════════════════════════════════════════
    public class RM_GraffitiSettings : ModSettings
    {
        public static bool paintingEnabled = true;
        public static int paintIntervalTicks = 250;
        public static bool viewerReactionEnabled = true;
        public static bool breachBiasEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref paintingEnabled, "paintingEnabled", true);
            Scribe_Values.Look(ref paintIntervalTicks, "paintIntervalTicks", 250);
            Scribe_Values.Look(ref viewerReactionEnabled, "viewerReactionEnabled", true);
            Scribe_Values.Look(ref breachBiasEnabled, "breachBiasEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Graffiti painting", ref paintingEnabled,
                "Pawns can paint graffiti marks on walls as a joy activity, and during "
              + "the painting-spree mental break. Off: no pawn ever paints a mark.");
            list.Label("Paint interval: every " + paintIntervalTicks + " ticks while painting");
            paintIntervalTicks = (int)list.Slider(paintIntervalTicks, 60f, 1000f);
            list.GapLine();

            list.CheckboxLabeled("Viewer reactions to marks", ref viewerReactionEnabled,
                "Pawns get a mood effect from noticing a graffiti mark nearby that reacts to them. "
              + "Off: marks are purely decorative filth.");
            list.Gap();
            list.CheckboxLabeled("Raiders lured to taunt marks", ref breachBiasEnabled,
                "A \"Come And Take It\"-style taunt mark biases raiders to breach toward it. "
              + "Off: raiders pick a breach target the ordinary (nearest) way.");

            list.End();
        }
    }

    public class RM_GraffitiMod : Mod
    {
        public static RM_GraffitiSettings settings;

        public RM_GraffitiMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GraffitiSettings>();
        }

        public override string SettingsCategory()
        {
            return "Graffiti";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
