using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.LoreStages
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for LoreStages.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This engine's only live mechanism is GameComponent_LoreStage.Apply(),
    // which rewrites a handful of def description/label fields to whatever
    // rung each RM_LoreStageTableDef ladder currently sits at, then clears
    // the two private description caches so the change shows immediately.
    // There is no rate/chance/interval anywhere in this mechanism — a ladder
    // advances only when a debug action or a consumer mod calls SetStage/
    // AdvanceStage — so the one honest control is a master on/off.
    //
    // GATING CHOICE: off makes every ladder read as stage 0 (defs show their
    // shipped, unstaged text) via GameComponent_LoreStage.EffectiveStage.
    // The real per-ladder progress in GameComponent_LoreStage.stages is left
    // completely alone — SetStage/AdvanceStage calls from elsewhere keep
    // recording it — so turning this back on picks up exactly where the
    // colony's progress already was, never resets it.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LoreStagesSettings : ModSettings
    {
        public static bool stagedTextEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stagedTextEnabled, "stagedTextEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Staged lore text", RimMandrake.Shared.SettingScope.Now, new[] { "stagedTextEnabled" }))
            {
                bool before = stagedTextEnabled;
                list.CheckboxLabeled("Staged lore descriptions", ref stagedTextEnabled,
                    "Biome, item and hediff descriptions can change wording as your colony learns "
                  + "more about a place. Off: everything shows its original, unstaged text — your "
                  + "colony's actual progress keeps being tracked in the background and picks back "
                  + "up right away if you turn this on again.");
                if (stagedTextEnabled != before)
                {
                    GameComponent_LoreStage.Current?.Reapply();
                }
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 600f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_LoreStagesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_LoreStagesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_LoreStagesMod : Mod
    {
        public static RM_LoreStagesSettings settings;

        public RM_LoreStagesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_LoreStagesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Lore Stages";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
