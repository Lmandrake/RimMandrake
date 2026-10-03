using UnityEngine;
using Verse;

namespace RimMandrake.WeepingStones
{
    // ════════════════════════════════════════════════════════════════════
    // STOCKED_POOL_BUILD_1 — Mod Settings.
    // Precedent: src/RimMandrake/DivingInteraction/Source/RM_DivingSettings.cs.
    //
    // MOD_OPTIONS_RETROFIT_1 doctrine (CLAUDE.md "Every mod ships superb Mod
    // Settings"): defaults = shipped behavior, all-off degrades gracefully.
    // Wave 4 (STOCKED_POOL_BUILD_1) lands HARVEST, CULL, the vhorrin
    // emergence trigger and the vizhik escape event — the husbandry loop
    // (STOCK/FEED/HARVEST/OVERDRAW/CULL/RECAPTURE) is now playable end to
    // end, so the default flips to true per this file's own prior note.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WeepingStonesSettings : ModSettings
    {
        public static bool stockedPoolsEnabled = true;

        // Multiplier on both vhorrin emergence chances (crowded 0.02, crashed 0.01 per pulse). 0-3.
        public static float vhorrinOddsMultiplier = 1f;

        // Per-pulse chance that a stocked vizhik escapes its pen. Shipped 0.05. 0-0.25.
        public static float vizhikEscapeChance = 0.05f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stockedPoolsEnabled, "stockedPoolsEnabled", true);
            Scribe_Values.Look(ref vhorrinOddsMultiplier, "vhorrinOddsMultiplier", 1f);
            Scribe_Values.Look(ref vizhikEscapeChance, "vizhikEscapeChance", 0.05f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Stocked pools enabled", ref stockedPoolsEnabled,
                "Master switch for the Weeping Stones' stocked-pool husbandry kit — the "
              + "nasty, over-active fish and alien-beast catches, pen zones, and the mood "
              + "economy around eating them. Gates the pool-pen zone designator, its "
              + "per-pool bookkeeping, and the STOCK/FEED/HARVEST/CULL jobs. On by default: "
              + "the full loop is built. Wild fishing (the ruled gentle six) and the "
              + "bestiary/cuisine content itself are never affected by this setting.");

            list.Gap();
            list.Label("Vhorrin odds: " + vhorrinOddsMultiplier.ToString("0.00") + "x (shipped 1.00x)",
                -1f, (TipSignal?)("How likely a crowded or crashed pool is to breed a vhorrin. At 0 an "
                   + "overcrowded or starved pen never produces one; at 3 it is three times as "
                   + "likely each pulse. A pen is checked about every 2500 ticks."));
            vhorrinOddsMultiplier = Mathf.Round(list.Slider(vhorrinOddsMultiplier, 0f, 3f) * 20f) / 20f;

            list.Label("Vizhik escape chance: " + vizhikEscapeChance.ToString("0.000")
                       + " per pulse (shipped 0.050)",
                -1f, (TipSignal?)("Chance each pulse that one stocked vizhik slips its pen and goes wild. "
                   + "At 0 nothing ever escapes; at 0.25 a pen leaks constantly."));
            vizhikEscapeChance = Mathf.Round(list.Slider(vizhikEscapeChance, 0f, 0.25f) * 200f) / 200f;

            if (list.ButtonText("Reset to defaults"))
            {
                stockedPoolsEnabled = true;
                vhorrinOddsMultiplier = 1f;
                vizhikEscapeChance = 0.05f;
            }

            list.End();
        }
    }

    public class RM_WeepingStonesMod : Mod
    {
        public static RM_WeepingStonesSettings settings;

        public RM_WeepingStonesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WeepingStonesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Weeping Stones: Stocked Pool";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
