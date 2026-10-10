using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.DroidRepairJobs
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Droid Repair Jobs.
    //
    // Gates QuestNode_DroidRepairJob.WritePaymentVars, the only place this
    // mod computes a number: the base repair-job payment (customer's XML
    // slate value, 320 silver fallback) scaled by the faction's wealth
    // (tech level) and reputation (goodwill) factors. Both scaling factors
    // are exposed as one on/off (the "guardrail" DROID_UNIFIED_FRAMEWORK_
    // DESIGN.md section 6 names), plus a flat multiplier on top of
    // everything, default 1x = shipped behavior.
    public class DroidRepairJobsSettings : ModSettings
    {
        public static float paymentMultiplier = 1f;
        public static bool wealthAndReputationScaling = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref paymentMultiplier, "paymentMultiplier", 1f);
            Scribe_Values.Look(ref wealthAndReputationScaling, "wealthAndReputationScaling", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(DroidRepairJobsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(DroidRepairJobsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Repair-job payment", RimMandrake.Shared.SettingScope.NextPulse, new[] { "paymentMultiplier", "wealthAndReputationScaling" }))
            {
                list.Label("Droid repair-job payment: " + paymentMultiplier.ToString("0.00") + "x");
                list.Label("Scales what a repair-job customer pays out, at every quality tier "
                         + "(neglected/shoddy/honest/fine).");
                paymentMultiplier = list.Slider(paymentMultiplier, 0.25f, 3f);
                list.CheckboxLabeled("Customer wealth and reputation affect payment", ref wealthAndReputationScaling,
                    "Off: every repair job pays the flat base amount (times the slider above), regardless of "
                  + "the customer faction's tech level or how much goodwill you have with them.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class DroidRepairJobsMod : Mod
    {
        public static DroidRepairJobsSettings settings;

        public DroidRepairJobsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<DroidRepairJobsSettings>();
        }

        public override string SettingsCategory() => "Droid Repair Jobs";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
