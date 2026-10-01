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
    // (STILLSAND_BEDAZZLE_CONTENT_1), which has a toggle and a threshold. Defaults
    // are the shipped behaviour; all-off leaves the biome whole (the zuurrik
    // def is then simply never woken).
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillsandSettings : ModSettings
    {
        /// <summary>Master toggle for the zuurrik: blood on sand wakes a stripping swarm.</summary>
        public bool zuurrikEnabled = true;

        /// <summary>Stained sand cells within one cluster that wake a swarm.</summary>
        public int zuurrikBloodThreshold = 8;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref zuurrikEnabled, "zuurrikEnabled", true);
            Scribe_Values.Look(ref zuurrikBloodThreshold, "zuurrikBloodThreshold", 8);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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
            }
            list.GapLine();
            list.Label("The biome itself reuses vanilla Core's BiomeWorker_ExtremeDesert unchanged, "
              + "so there is no natural-placement score of this mod's own to toggle. The event "
              + "creatures (muurrok, krayt attack) have their own panel: \"Stillsand: event creatures\".");

            list.End();
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
