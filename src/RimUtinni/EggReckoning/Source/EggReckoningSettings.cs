using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for The Reckoning (Egg Reckoning).
    //
    // This mod ships three quest-selection routes for "The Reckoning"
    // (WEBWORK_EGG_RECKONING_QUEST_1): RUT_Reckoning_Rumor (natural-pool,
    // storyteller-picked via rootSelectionWeight), RUT_Reckoning_CartelOffer
    // (trader-offered, givenBy Traders, randomlySelectable false), and the
    // base RUT_Reckoning abstract the other two inherit from. There is no
    // paired IncidentDef/IncidentWorker to gate here (unlike
    // KyberTradePlot's RUT_GiveQuest_* pattern) — these fire through
    // RimWorld's own native quest-selection machinery, so this mod's
    // toggle is wired the same way WreckedMachinesPatcher/
    // FungalSoilTradeOptions already mutate loaded def fields directly:
    // a [StaticConstructorOnStartup] patcher flips rootSelectionWeight to 0
    // and clears givenBy when off, restoring the captured originals when on.
    //
    // Off degrades gracefully: neither quest can ever be offered again, but
    // nothing already granted (an in-progress Reckoning) is touched — the
    // toggle only affects future selection, matching every other mod's
    // "affects new occurrences, not existing state" convention.
    //
    // Shipped default: ON — matches current behavior exactly.
    public class EggReckoningSettings : ModSettings
    {
        public static bool reckoningEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref reckoningEnabled, "reckoningEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("The Reckoning quest enabled", ref reckoningEnabled,
                "Off: neither the natural rumor route nor the Cartel trader offer for "
              + "\"The Reckoning\" (the egg-assassination quest family) can be selected "
              + "again. A Reckoning already granted to a colony is unaffected.");

            list.End();
        }
    }

    public class EggReckoningMod : Mod
    {
        public static EggReckoningSettings settings;

        public EggReckoningMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<EggReckoningSettings>();
        }

        public override string SettingsCategory() => "The Reckoning";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            EggReckoningPatcher.Apply();
        }
    }

    // Defs are fully loaded and cross-reference-resolved before any
    // [StaticConstructorOnStartup] class runs, so reading/writing
    // DefDatabase entries here is safe — same timing precedent as
    // RimMandrake.WreckedMachines.WreckedMachinesPatcher.
    [StaticConstructorOnStartup]
    public static class EggReckoningPatcher
    {
        private static readonly QuestScriptDef RumorQuest =
            DefDatabase<QuestScriptDef>.GetNamedSilentFail("RUT_Reckoning_Rumor");

        private static readonly QuestScriptDef CartelOfferQuest =
            DefDatabase<QuestScriptDef>.GetNamedSilentFail("RUT_Reckoning_CartelOffer");

        // Shipped baselines, captured once before any settings-driven edit.
        private static readonly float BaseRumorWeight =
            RumorQuest != null ? RumorQuest.rootSelectionWeight : 0f;

        private static readonly List<QuestGiverTag> BaseCartelGivenBy =
            CartelOfferQuest != null && CartelOfferQuest.givenBy != null
                ? new List<QuestGiverTag>(CartelOfferQuest.givenBy)
                : new List<QuestGiverTag>();

        static EggReckoningPatcher()
        {
            Apply();
        }

        public static void Apply()
        {
            if (RumorQuest != null)
            {
                RumorQuest.rootSelectionWeight = EggReckoningSettings.reckoningEnabled ? BaseRumorWeight : 0f;
            }

            if (CartelOfferQuest != null)
            {
                CartelOfferQuest.givenBy = EggReckoningSettings.reckoningEnabled
                    ? new List<QuestGiverTag>(BaseCartelGivenBy)
                    : new List<QuestGiverTag>();
            }
        }
    }
}
