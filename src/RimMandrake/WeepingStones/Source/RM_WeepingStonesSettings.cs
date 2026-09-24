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
    // Wave 2 (STOCKED_POOL_BUILD_1) lands the pen-zone designator and
    // RM_MapComponent_PoolStock's per-pool READ bookkeeping — a real, gated
    // mechanism now, not inert data. Default STAYS OFF this wave anyway: the
    // STOCK/FEED/HARVEST/CULL/RECAPTURE jobs that actually populate a pen are
    // still owed, so turning this on today gives a player a zone designator
    // that tracks a population nothing can yet place there — correct, but not
    // yet worth surfacing by default. Flip the default to true once the job
    // set lands and a pen is actually playable end to end.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WeepingStonesSettings : ModSettings
    {
        public static bool stockedPoolsEnabled = false;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stockedPoolsEnabled, "stockedPoolsEnabled", false);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Stocked pools enabled", ref stockedPoolsEnabled,
                "Master switch for the Weeping Stones' stocked-pool husbandry kit — the "
              + "nasty, over-active fish and alien-beast catches, pen zones, and the mood "
              + "economy around eating them. Gates the pool-pen zone designator and its "
              + "per-pool bookkeeping. Off by default: the jobs that actually stock, feed "
              + "and harvest a pen are still owed, so this is a mechanism with no way yet "
              + "to put anything in it. Wild fishing (the ruled gentle six) and the bestiary/ "
              + "cuisine content itself are never affected by this setting.");

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
