using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
    // GRAVSHIP_ACOUSTIC_SCANNER_1 — Mod Settings (MOD_OPTIONS_RETROFIT_1 doctrine:
    // defaults = shipped behaviour, every toggle wired to something real).
    public class RM_AcousticScannerSettings : ModSettings
    {
        public const int MinBandSize = RM_AcousticKernel.MinBandSize;   // hard floor: a reading is ALWAYS banded, never exact
        public const int MaxBandSize = RM_AcousticKernel.MaxBandSize;

        public bool enabled = true;
        public bool requireLandedShip = true;
        public float cooldownHours = 24f;
        public float overlayHours = 6f;
        public int bandSize = 11;
        public float rangeCells = 60f;
        public bool pulseEffects = true;

        public int BandSizeClamped => RM_AcousticKernel.ClampBandSetting(bandSize);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref requireLandedShip, "requireLandedShip", true);
            Scribe_Values.Look(ref cooldownHours, "cooldownHours", 24f);
            Scribe_Values.Look(ref overlayHours, "overlayHours", 6f);
            Scribe_Values.Look(ref bandSize, "bandSize", 11);
            Scribe_Values.Look(ref rangeCells, "rangeCells", 60f);
            Scribe_Values.Look(ref pulseEffects, "pulseEffects", true);
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

            if (Group(list, "Sounder availability", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "requireLandedShip", "cooldownHours" }))
            {
                list.CheckboxLabeled("RM_Acoustic_SettingEnabled".Translate(), ref enabled,
                    "RM_Acoustic_SettingEnabledTip".Translate());
                list.CheckboxLabeled("RM_Acoustic_SettingRequireShip".Translate(), ref requireLandedShip,
                    "RM_Acoustic_SettingRequireShipTip".Translate());
                list.Label("RM_Acoustic_SettingCooldown".Translate(cooldownHours.ToString("0")));
                cooldownHours = Mathf.Round(list.Slider(cooldownHours, 1f, 120f));
                list.GapLine();
            }

            if (Group(list, "Pulse reading", RimMandrake.Shared.SettingScope.NextPulse, new[] { "pulseEffects", "overlayHours", "rangeCells", "bandSize" }))
            {
                list.CheckboxLabeled("RM_Acoustic_SettingEffects".Translate(), ref pulseEffects,
                    "RM_Acoustic_SettingEffectsTip".Translate());
                list.Label("RM_Acoustic_SettingOverlay".Translate(overlayHours.ToString("0")));
                overlayHours = Mathf.Round(list.Slider(overlayHours, 1f, 48f));
                list.Label("RM_Acoustic_SettingRange".Translate(rangeCells.ToString("0")));
                rangeCells = Mathf.Round(list.Slider(rangeCells, 20f, 250f));
                list.Label("RM_Acoustic_SettingBand".Translate(BandSizeClamped, MinBandSize));
                bandSize = Mathf.RoundToInt(list.Slider(BandSizeClamped, MinBandSize, MaxBandSize));
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from a fresh instance's
        // field initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new RM_AcousticScannerSettings();
            foreach (FieldInfo f in typeof(RM_AcousticScannerSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_AcousticScannerSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the sounder reads enabled, requireLandedShip
        /// and cooldownHours every gizmo/inspect/pulse check (now); pulseEffects, rangeCells, bandSize and overlayHours only when a pulse fires.</summary>
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_AcousticScannerMod : Mod
    {
        public static RM_AcousticScannerSettings settings;

        public RM_AcousticScannerMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AcousticScannerSettings>();
        }

        public override string SettingsCategory() => "RM_Acoustic_SettingsCategory".Translate();

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }
}
