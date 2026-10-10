using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Visibility
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Visibility.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // Two things exposed:
    //   1. Master on/off for the raid threat-point scaling
    //      (ColonyVisibilityRaidPatch.Prefix_ScaleHostilePoints) — the dial
    //      itself (GameComponent_ColonyVisibility) keeps tracking harmlessly
    //      either way; only the gameplay EFFECT on raid points is gated.
    //   2. A strength slider that lerps between "no effect" (1.0x) and the
    //      design doc's ruled curve output, so a player can soften/amplify
    //      the whole mechanic without hand-editing
    //      GameComponent_ColonyVisibility.VisibilityToThreatCurve (which
    //      stays the ruled base curve, untouched).
    //   3. The Ta'Baa launch-reset multiplier (how far a gravship launch
    //      resets the dial toward 0) as a tunable, default matching the
    //      shipped 0.15x.
    // ════════════════════════════════════════════════════════════════════
    public class RM_VisibilitySettings : ModSettings
    {
        public static bool enableRaidScaling = true;
        public static float raidScalingStrength = 1f;
        public static float launchResetMultiplier = 0.15f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enableRaidScaling, "enableRaidScaling", true);
            Scribe_Values.Look(ref raidScalingStrength, "raidScalingStrength", 1f);
            Scribe_Values.Look(ref launchResetMultiplier, "launchResetMultiplier", 0.15f);
        }

        /// <summary>
        /// Applies the strength dial to the curve's raw output: at 0 strength,
        /// visibility never changes raid points (factor 1.0); at 1 (default),
        /// the full ruled curve applies; up to 2, the curve's deviation from
        /// 1.0 is doubled.
        /// </summary>
        public static float ScaledThreatFactor(float visibility)
        {
            float curveFactor = GameComponent_ColonyVisibility.ThreatFactor(visibility);
            return RM_VisibilityKernel.ScaledThreatFactor(curveFactor, raidScalingStrength);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_VisibilitySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_VisibilitySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            // Scopes audited per read site: the raid-points patch reads the switch and strength each time a raid is sized; the launch
            // reset is read at the moment a gravship launches. (The old "worldgen-affecting" label on the launch row was wrong.)
            if (Group(list, "Colony Visibility raid scaling", RimMandrake.Shared.SettingScope.NextPulse, new[] { "enableRaidScaling", "raidScalingStrength" }))
            {
                list.CheckboxLabeled("Raids scale with Colony Visibility", ref enableRaidScaling,
                    "How exposed the colony's ship is on the desert changes how hard hostile raids, "
                  + "infestations, manhunter packs and mech clusters hit. Off: the Visibility dial "
                  + "keeps tracking in the background, but raids are never scaled by it.");
                list.Label("Scaling strength: " + raidScalingStrength.ToString("0.00") + "x");
                list.Label("0x = no effect at all. 1x = the ruled curve (unchanged). 2x = double the swing.");
                raidScalingStrength = list.Slider(raidScalingStrength, 0f, 2f);
                list.GapLine();
            }

            if (Group(list, "Launch reset (next gravship launch)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "launchResetMultiplier" }))
            {
                list.Label("Launching a gravship resets Visibility toward "
                    + (launchResetMultiplier * 100f).ToString("0") + "% of its old value (floor 5, ceiling 15).");
                launchResetMultiplier = list.Slider(launchResetMultiplier, 0.05f, 0.5f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_VisibilityMod : Mod
    {
        public static RM_VisibilitySettings settings;

        public RM_VisibilityMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_VisibilitySettings>();
        }

        public override string SettingsCategory()
        {
            return "Colony Visibility";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
