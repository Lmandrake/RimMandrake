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
    // Wave 1 ships bestiary + cuisine data only — the husbandry loop this
    // toggle is meant to gate (pen zones, PoolStock bookkeeping, ring-read
    // overlay, handler injuries) has not landed yet, so the shipped default
    // is OFF: enabling this mod today must change nothing about a running
    // game. Flip the default to true in the wave that wires the loop in.
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
              + "economy around eating them. Off by default: this wave ships only the "
              + "bestiary and cuisine defs, no live husbandry mechanism yet, so this toggle "
              + "currently gates nothing. Wild fishing (the ruled gentle six) is never "
              + "affected by this setting.");

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
