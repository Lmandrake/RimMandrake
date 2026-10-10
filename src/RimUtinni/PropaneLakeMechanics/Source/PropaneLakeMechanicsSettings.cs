using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// MOD_OPTIONS_RETROFIT_1's standing law: every mod ships a real settings
	/// screen — on/off per mechanic, tuning where a number is the experience,
	/// defaults = shipped behaviour, all-off degrades gracefully. Four
	/// mechanics, four kill switches; the deflagration hook is the one the
	/// design doc itself flags as needing real playtesting, so it gets its own
	/// intensity slider rather than a flat on/off.
	/// </summary>
	public class PropaneLakeMechanicsSettings : ModSettings
	{
		public bool gasVentsEnabled = true;
		public bool pipeNetworksEnabled = true;
		public bool saturationDeflagrationEnabled = true;
		public bool vWakeAgitationEnabled = true;
		public bool saturationHeistRaidEnabled = true;

		/// <summary>Multiplies every deflagration/flashover chance rolled by
		/// Patch_GasSaturationDeflagration. 1.0 = the ruled curve as designed;
		/// 0 has the same effect as disabling the toggle, kept as a slider so a
		/// worried player can dial it down instead of losing the mechanic.</summary>
		public float deflagrationIntensity = 1f;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref gasVentsEnabled, "gasVentsEnabled", true);
			Scribe_Values.Look(ref pipeNetworksEnabled, "pipeNetworksEnabled", true);
			Scribe_Values.Look(ref saturationDeflagrationEnabled, "saturationDeflagrationEnabled", true);
			Scribe_Values.Look(ref vWakeAgitationEnabled, "vWakeAgitationEnabled", true);
			Scribe_Values.Look(ref saturationHeistRaidEnabled, "saturationHeistRaidEnabled", true);
			Scribe_Values.Look(ref deflagrationIntensity, "deflagrationIntensity", 1f);
		}

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var inst = new PropaneLakeMechanicsSettings();
            foreach (FieldInfo f in typeof(PropaneLakeMechanicsSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(inst);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(PropaneLakeMechanicsSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
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

            if (Group(list, "Gas vents and pipe networks", RimMandrake.Shared.SettingScope.Now, new[] { "gasVentsEnabled", "pipeNetworksEnabled" }))
            {
                list.CheckboxLabeled("RUT_Settings_GasVentsEnabled".Translate(), ref gasVentsEnabled,
                    "RUT_Settings_GasVentsEnabled_Desc".Translate());
                list.CheckboxLabeled("RUT_Settings_PipeNetworksEnabled".Translate(), ref pipeNetworksEnabled,
                    "RUT_Settings_PipeNetworksEnabled_Desc".Translate());
                list.GapLine();
            }

            if (Group(list, "V-wake agitation", RimMandrake.Shared.SettingScope.Now, new[] { "vWakeAgitationEnabled" }))
            {
                list.CheckboxLabeled("RUT_Settings_VWakeAgitationEnabled".Translate(), ref vWakeAgitationEnabled,
                    "RUT_Settings_VWakeAgitationEnabled_Desc".Translate());
                list.GapLine();
            }

            if (Group(list, "Saturation heist raid", RimMandrake.Shared.SettingScope.NextPulse, new[] { "saturationHeistRaidEnabled" }))
            {
                list.CheckboxLabeled("RUT_Settings_SaturationHeistRaidEnabled".Translate(), ref saturationHeistRaidEnabled,
                    "RUT_Settings_SaturationHeistRaidEnabled_Desc".Translate());
                list.GapLine();
            }

            if (Group(list, "Saturation deflagration", RimMandrake.Shared.SettingScope.Now, new[] { "saturationDeflagrationEnabled", "deflagrationIntensity" }))
            {
                list.CheckboxLabeled("RUT_Settings_DeflagrationEnabled".Translate(), ref saturationDeflagrationEnabled,
                    "RUT_Settings_DeflagrationEnabled_Desc".Translate());
                list.Label("RUT_Settings_DeflagrationIntensity".Translate(deflagrationIntensity.ToStringPercent()));
                deflagrationIntensity = list.Slider(deflagrationIntensity, 0f, 2f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
	}
}
