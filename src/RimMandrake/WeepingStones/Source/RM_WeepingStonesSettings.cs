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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stockedPoolsEnabled, "stockedPoolsEnabled", true);
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
