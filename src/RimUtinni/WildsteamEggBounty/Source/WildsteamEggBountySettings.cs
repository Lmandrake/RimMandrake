using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.WildsteamEggBounty
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Wildsteam Egg Bounty.
    //
    // One quest, RUT_WildsteamEggBounty, selected via native
    // rootSelectionWeight (no paired IncidentDef to gate, same shape as
    // EggReckoning). Gated the same way WreckedMachinesPatcher/
    // EggReckoningPatcher already mutate loaded def fields via a
    // [StaticConstructorOnStartup] patcher keyed off this settings toggle.
    //
    // Off degrades gracefully: the bounty quest can never be offered again;
    // one already granted is untouched. Shipped default: ON.
    public class WildsteamEggBountySettings : ModSettings
    {
        public static bool bountyEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref bountyEnabled, "bountyEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(WildsteamEggBountySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(WildsteamEggBountySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): closing the window re-applies the quest's rootSelectionWeight (WriteSettings), which only matters the next time the storyteller rolls a quest, so it is [next pulse]. Nothing is read at map or world generation.</summary>
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
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

            if (Group(list, "Wildsteam egg bounty quest", RimMandrake.Shared.SettingScope.NextPulse, new[] { "bountyEnabled" }))
            {
                list.CheckboxLabeled("Wildsteam egg bounty quest enabled", ref bountyEnabled,
                    "Off: the Wildsteam Clan's ollathrix-egg bounty trade request can never be "
                  + "offered again. A bounty already granted to a colony is unaffected.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class WildsteamEggBountyMod : Mod
    {
        public static WildsteamEggBountySettings settings;

        public WildsteamEggBountyMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WildsteamEggBountySettings>();
        }

        public override string SettingsCategory() => "Wildsteam Egg Bounty";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            WildsteamEggBountyPatcher.Apply();
        }
    }

    [StaticConstructorOnStartup]
    public static class WildsteamEggBountyPatcher
    {
        private static readonly QuestScriptDef BountyQuest =
            DefDatabase<QuestScriptDef>.GetNamedSilentFail("RUT_WildsteamEggBounty");

        private static readonly float BaseWeight =
            BountyQuest != null ? BountyQuest.rootSelectionWeight : 0f;

        static WildsteamEggBountyPatcher()
        {
            Apply();
        }

        public static void Apply()
        {
            if (BountyQuest != null)
            {
                BountyQuest.rootSelectionWeight = WildsteamEggBountySettings.bountyEnabled ? BaseWeight : 0f;
            }
        }
    }
}
