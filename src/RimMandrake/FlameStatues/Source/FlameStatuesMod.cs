using System.Reflection;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlameStatues
{
    // FLAME_STATUES_MOD_BUILD_1 — Mod Settings, statue_mods_spec.md §2.4. Defaults = shipped behaviour.
    // All off = plain sculptures with our art. The Helixien row arrives with step 7.
    public class FlameStatuesSettings : ModSettings
    {
        public static bool flamePoints = true;
        public static bool flecks = true;
        public static bool consumeFuel = true;
        public static bool qualityScaling = true;
        public static bool glow = true;
        public static float consumptionMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref flamePoints, "flamePoints", true);
            Scribe_Values.Look(ref flecks, "flecks", true);
            Scribe_Values.Look(ref consumeFuel, "consumeFuel", true);
            Scribe_Values.Look(ref qualityScaling, "qualityScaling", true);
            Scribe_Values.Look(ref glow, "glow", true);
            Scribe_Values.Look(ref consumptionMultiplier, "consumptionMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Flames and light", RimMandrake.Shared.SettingScope.Now, new[] { "flamePoints", "flecks", "qualityScaling", "glow" }))
            {
                list.CheckboxLabeled("Flames drawn", ref flamePoints,
                    "On: a fuelled flame statue burns at every vent its carving has (palms, crown, shoulders). "
                  + "Off: no flames are drawn and the statue does not light the room. Takes effect at once.");
                list.CheckboxLabeled("Fire-glow sparks", ref flecks,
                    "On: burning vents throw small glowing puffs now and then. Off: flames only. Takes effect at once.");
                list.CheckboxLabeled("Better carving, bigger fire", ref qualityScaling,
                    "On: an awful statue burns at half size, a legendary one at double, with sparks to match. "
                  + "Off: every statue burns the same. Takes effect at once.");
                list.CheckboxLabeled("Statues light the room", ref glow,
                    "On: a burning statue casts warm light. Off: flames are drawn but cast no light. "
                  + "Takes effect within a few seconds.");
                list.GapLine();
            }

            if (Group(list, "Fuel on or off", RimMandrake.Shared.SettingScope.Now, new[] { "consumeFuel" }))
            {
                list.CheckboxLabeled("Statues use fuel", ref consumeFuel,
                    "On: flame statues burn chemfuel and go dark when empty. Off: statues never run out. "
                  + "Takes effect at once.");
                list.GapLine();
            }

            if (Group(list, "Fuel use rate (restart)", RimMandrake.Shared.SettingScope.Now, new[] { "consumptionMultiplier" }, "[next game start]"))
            {
                list.Label("Fuel use: " + consumptionMultiplier.ToStringPercent(), -1f,
                    new TipSignal("How fast flame statues burn fuel, against the shipped rate. Takes effect after a restart."));
                consumptionMultiplier = list.Slider(consumptionMultiplier, 0.25f, 4f);
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
            foreach (FieldInfo f in typeof(FlameStatuesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(FlameStatuesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

    public class FlameStatuesMod : Mod
    {
        public static FlameStatuesSettings settings;

        public FlameStatuesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<FlameStatuesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Flame Statues";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>Applies the fuel-use multiplier to every def carrying flame points (CompRefuelable reads its
    /// props' rate directly, so it is scaled once at startup).</summary>
    [StaticConstructorOnStartup]
    public static class FlameStatuesStartup
    {
        public static readonly List<string> Scaled = new List<string>();

        static FlameStatuesStartup()
        {
            float m = RM_FlameKernel.ClampFuelMultiplier(FlameStatuesSettings.consumptionMultiplier);
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.GetCompProperties<RM_CompProperties_FlamePoints>() == null)
                {
                    continue;
                }
                CompProperties_Refuelable fuel = d.GetCompProperties<CompProperties_Refuelable>();
                if (fuel == null)
                {
                    continue;
                }
                if (!Mathf.Approximately(m, 1f))
                {
                    fuel.fuelConsumptionRate = RM_FlameKernel.ScaledFuelRate(fuel.fuelConsumptionRate, m);
                }
                Scaled.Add(d.defName);
            }
            if (!Mathf.Approximately(m, 1f))
            {
                Log.Message("[FlameStatues] fuel use x" + m.ToString("0.##") + " on " + Scaled.Count + " statue def(s).");
            }
        }
    }
}
