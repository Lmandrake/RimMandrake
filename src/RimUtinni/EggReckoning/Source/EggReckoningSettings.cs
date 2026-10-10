using System.Reflection;
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

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(EggReckoningSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(EggReckoningSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "The Reckoning quest", RimMandrake.Shared.SettingScope.NextPulse, new[] { "reckoningEnabled" }))
            {
                list.CheckboxLabeled("The Reckoning quest enabled", ref reckoningEnabled,
                    "Off: neither the natural rumor route nor the Cartel trader offer for "
                  + "\"The Reckoning\" (the egg-assassination quest family) can be selected "
                  + "again. A Reckoning already granted to a colony is unaffected.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
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
