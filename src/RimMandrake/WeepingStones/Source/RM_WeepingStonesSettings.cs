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

        // WEEPINGSTONES_WALKING_CONDENSER_1: master switch and season length (days) for the walking condenser.
        public static bool condenserEnabled = true;
        public static float condenserSeasonDays = 15f;

        // WEEPINGSTONES_DEWSILK_COCOON_1: tamed mirrik leave dewsilk cocoons. Read once at startup.
        public static bool dewsilkEnabled = true;

        // WEEPINGSTONES_OASIS_MUTATOR_FLORA_1: our oases grow the biome's own blade flora instead of Earth palms/grasses. Read live.
        public static bool oasisNativeFloraEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stockedPoolsEnabled, "stockedPoolsEnabled", true);
            Scribe_Values.Look(ref vhorrinOddsMultiplier, "vhorrinOddsMultiplier", 1f);
            Scribe_Values.Look(ref vizhikEscapeChance, "vizhikEscapeChance", 0.05f);
            Scribe_Values.Look(ref condenserEnabled, "condenserEnabled", true);
            Scribe_Values.Look(ref condenserSeasonDays, "condenserSeasonDays", 15f);
            Scribe_Values.Look(ref dewsilkEnabled, "dewsilkEnabled", true);
            Scribe_Values.Look(ref oasisNativeFloraEnabled, "oasisNativeFloraEnabled", true);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

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

            list.Gap();
            list.CheckboxLabeled("Walking condenser enabled", ref condenserEnabled,
                "The oldest gorrask, a unique stone-crab carrying a running condenser. While it is settled a "
              + "pool and the water truce form round it; it moves on each season. Off: it spawns nowhere, and any "
              + "pool it already made dries back.");
            list.Label("Condenser season: " + condenserSeasonDays.ToString("0") + " days (shipped 15)",
                -1f, (TipSignal?)("How long the gorrask stays settled before it moves on. 15 is one vanilla quadrum."));
            condenserSeasonDays = Mathf.Round(list.Slider(condenserSeasonDays, 3f, 30f));

            list.Gap();
            list.CheckboxLabeled("Dewsilk cocoons enabled (applies next launch)", ref dewsilkEnabled,
                "Tamed mirrik leave dewsilk cocoons that colonists gather like wool and spin into dewsilk cloth at a tailor bench. "
              + "Off: mirrik yield nothing. Read once when the game starts, so a change needs a restart.");

            list.Gap();
            list.CheckboxLabeled("Native oasis flora", ref oasisNativeFloraEnabled,
                "On a Weeping Stones oasis, the oasis mutator grows the biome's own blade flora (dewblade, bladderquill, steamfrond, dripfringe) "
              + "instead of Earth palms and grasses. Vanilla desert oases are never affected. Off: our oases grow vanilla palms and grass. "
              + "Takes effect for maps generated afterwards.");

            if (list.ButtonText("Reset to defaults"))
            {
                stockedPoolsEnabled = true;
                vhorrinOddsMultiplier = 1f;
                vizhikEscapeChance = 0.05f;
                condenserEnabled = true;
                condenserSeasonDays = 15f;
                dewsilkEnabled = true;
                oasisNativeFloraEnabled = true;
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
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
