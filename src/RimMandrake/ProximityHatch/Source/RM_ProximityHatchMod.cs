using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ProximityHatch
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Proximity Hatch.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, a
    // DoWindowContents helper called from the Mod subclass).
    //
    // This mod has no worldgen surface at all — CompProximityHatch is pure
    // live-play ThingComp logic (a manual tick countdown + a radial scan),
    // so every option here is ordinary runtime tuning, not "new maps only".
    //
    //   1. Master on/off — default ON, matching shipped behavior. Off:
    //      CompProximityHatch.RunScan() no-ops entirely; the egg only ever
    //      hatches on CompHatcher's own vanilla timer, same as a vanilla egg.
    //   2. Detection radius multiplier, scaling each egg's own
    //      CompProperties_ProximityHatch.triggerRadius — default 1x.
    //   3. Scan interval multiplier, scaling each egg's own scanIntervalTicks
    //      — default 1x (higher = checks less often).
    //   4. Ambush toggle — whether the hatchling is forced hostile/attacking
    //      on the triggering pawn, or just hatches early and wakes up neutral
    //      like any normal hatchling — default ON, matching shipped behavior.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ProximityHatchSettings : ModSettings
    {
        public static bool enabled = true;
        public static float radiusMultiplier = 1f;
        public static float scanIntervalMultiplier = 1f;
        public static bool aggroEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref radiusMultiplier, "radiusMultiplier", 1f);
            Scribe_Values.Look(ref scanIntervalMultiplier, "scanIntervalMultiplier", 1f);
            Scribe_Values.Look(ref aggroEnabled, "aggroEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_ProximityHatchSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_ProximityHatchSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            // Scopes audited per read site: enabled/radius/aggro are read on every scan (now); the scan interval is read when the
            // countdown restarts, so a change lands on each egg's next scan.
            if (Group(list, "Proximity hatching", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "radiusMultiplier", "aggroEnabled" }))
            {
                list.CheckboxLabeled("Proximity hatch enabled", ref enabled,
                    "Eggs with a proximity trigger hatch early the moment a living pawn walks into "
                  + "range. Off: those eggs only ever hatch on their own normal timer, same as a "
                  + "vanilla egg - no ambush, no early hatch, no error.");
                list.Label("Detection radius: " + radiusMultiplier.ToString("0.00") + "x");
                list.Label("Scales every proximity egg's own trigger radius (each egg's base radius times this).");
                radiusMultiplier = list.Slider(radiusMultiplier, 0.25f, 3f);
                list.CheckboxLabeled("Hatchling ambushes the triggering pawn", ref aggroEnabled,
                    "On: the freshly hatched creature immediately attacks whoever walked into "
                  + "range (the shipped ambush beat). Off: it still hatches early, but wakes up "
                  + "neutral like any ordinary hatchling.");
                list.GapLine();
            }

            if (Group(list, "Scan cadence", RimMandrake.Shared.SettingScope.NextPulse, new[] { "scanIntervalMultiplier" }))
            {
                list.Label("Scan interval: " + scanIntervalMultiplier.ToString("0.00") + "x");
                list.Label("How often eggs check for a nearby pawn. Higher = checks less often "
                          + "(cheaper, slightly less responsive to a pawn walking in).");
                scanIntervalMultiplier = list.Slider(scanIntervalMultiplier, 0.25f, 4f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_ProximityHatchMod : Mod
    {
        public static RM_ProximityHatchSettings settings;

        public RM_ProximityHatchMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_ProximityHatchSettings>();
        }

        public override string SettingsCategory()
        {
            return "Proximity Hatch";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
