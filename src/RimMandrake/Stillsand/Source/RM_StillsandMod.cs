using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Stillsand.
    //
    // Precedent: src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs.
    //
    // The biome itself reuses vanilla Core's BiomeWorker_ExtremeDesert unchanged,
    // so there is no placement score to gate. The one mechanic this assembly
    // owns besides the sand-buster eruption is the zuurrik blood-waker
    // (STILLSAND_BEDAZZLE_CONTENT_1), which has a toggle and a threshold, and the
    // rock-and-cave gen steps (STILLSAND_PRECIOUS_CAVES_1, RM_PreciousCaveSettings). Defaults
    // are the shipped behaviour; all-off leaves the biome whole (the zuurrik
    // def is then simply never woken).
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillsandSettings : ModSettings
    {
        /// <summary>Master toggle for the zuurrik: blood on sand wakes a stripping swarm.</summary>
        public bool zuurrikEnabled = true;

        /// <summary>Stained sand cells within one cluster that wake a swarm.</summary>
        public int zuurrikBloodThreshold = 8;

        /// <summary>ZUURRIK_GROWTH_BY_FEEDING_1: the next swarm grows by what this one really ate.
        /// PROVISIONAL (auto-decided 2026-10-09, ZUURRIK_GROWTH_BY_FEEDING_1). Off: by the stain it woke to.</summary>
        public bool zuurrikGrowByFeeding = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref zuurrikEnabled, "zuurrikEnabled", true);
            Scribe_Values.Look(ref zuurrikBloodThreshold, "zuurrikBloodThreshold", 8);
            Scribe_Values.Look(ref zuurrikGrowByFeeding, "zuurrikGrowByFeeding", true);
            RM_PreciousCaveSettings.Expose(); // STILLSAND_PRECIOUS_CAVES_1
            RM_StillsandWaterSettings.Expose(); // STILLSAND_RETURN_RITUAL_1
            RM_SandSwimRemSettings.Expose(); // STILLSAND_SAND_SWIM_REMAINDER_1
            RM_DuneTrackEraserSettings.Expose(); // FOOTPRINT_TRACK_GRID_1
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1400f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

            list.Label("Stillsand");
            list.CheckboxLabeled("Blood on the sand wakes the zuurrik",
                ref zuurrikEnabled,
                "On a Stillsand map, enough fresh blood on sand wakes a swarm that strips the stain "
                + "and the bodies beside it, then re-buries. Never attacks the unwounded. Off: the "
                + "zuurrik never wakes.");
            if (zuurrikEnabled)
            {
                list.Label("Stained cells needed to wake a swarm: " + zuurrikBloodThreshold);
                zuurrikBloodThreshold = (int)list.Slider(zuurrikBloodThreshold, 2, 40);
                list.CheckboxLabeled("Swarms grow by what they eat", ref zuurrikGrowByFeeding,
                    "On: the next swarm is bigger by the stains and bodies this one actually stripped; a stain your "
                    + "colonists cleaned first feeds nothing. Off: it grows by the size of the stain it woke to.");
            }
            list.GapLine();
            list.Label("The biome itself reuses vanilla Core's BiomeWorker_ExtremeDesert unchanged, "
              + "so there is no natural-placement score of this mod's own to toggle. The event "
              + "creatures (muurrok, krayt attack) have their own panel: \"Stillsand: event creatures\".");
            RM_PreciousCaveSettings.Draw(list); // STILLSAND_PRECIOUS_CAVES_1
            RM_StillsandWaterSettings.Draw(list); // STILLSAND_RETURN_RITUAL_1
            RM_SandSwimRemSettings.Draw(list); // STILLSAND_SAND_SWIM_REMAINDER_1
            RM_DuneTrackEraserSettings.Draw(list); // FOOTPRINT_TRACK_GRID_1

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_StillsandMod : Mod
    {
        public static RM_StillsandSettings settings;

        public RM_StillsandMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StillsandSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
