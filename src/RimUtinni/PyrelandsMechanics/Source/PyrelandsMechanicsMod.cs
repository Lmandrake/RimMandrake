using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the campaign-specific remainder
    /// of the Pyrelands igniter kit, after PYRELANDS_RM_MOD_BUILD_1 §6 absorbed
    /// the franchise-free two-thirds (the burn-line, the fire clock, the
    /// fire-hawk and the furnace-beast's thermal circuit) into
    /// mandrake.rm.pyrelands's own RM_PyrelandsSettings.
    ///
    /// What is left here names the Deep Desert Tribes — a campaign faction —
    /// and cannot move to the franchise-free tier: arson-justice, the flame
    /// harvest, and the fire rite.
    /// </summary>
    public class PyrelandsMechanicsSettings : ModSettings
    {
        // ---- Master switches, one per mechanism -----------------------------
        public static bool arsonJusticeEnabled = true;
        public static bool flameHarvestEnabled = true;

        // DEEP_TRIBES_FIRE_RITE_1. Off means the fire clock lights every front
        // itself, exactly as it did before this mechanism existed — which is what
        // "all-off degrades gracefully" means here.
        public static bool fireRiteEnabled = true;

        // ---- Tunables ---------------------------------------------------------
        public static float arsonDebtRaidThreshold = RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtRaidThreshold;
        public static int flameHarvestMinFires = RimMandrake.Pyrelands.PyrelandsTuning.FlameHarvestMinFires;
        public static float fireRiteFraction = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteFraction;
        public static int fireRiteGroupMin = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMin;
        public static int fireRiteGroupMax = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMax;
        public static float fireRiteHarvestHours = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteHarvestHours;
        public static int fireRiteCarryPerPawn = RimMandrake.Pyrelands.PyrelandsTuning.FireRiteCarryPerPawn;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arsonJusticeEnabled, "arsonJusticeEnabled", true);
            Scribe_Values.Look(ref flameHarvestEnabled, "flameHarvestEnabled", true);
            Scribe_Values.Look(ref fireRiteEnabled, "fireRiteEnabled", true);

            Scribe_Values.Look(ref fireRiteFraction, "fireRiteFraction", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteFraction);
            Scribe_Values.Look(ref fireRiteGroupMin, "fireRiteGroupMin", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMin);
            Scribe_Values.Look(ref fireRiteGroupMax, "fireRiteGroupMax", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteGroupMax);
            Scribe_Values.Look(ref fireRiteHarvestHours, "fireRiteHarvestHours", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteHarvestHours);
            Scribe_Values.Look(ref fireRiteCarryPerPawn, "fireRiteCarryPerPawn", RimMandrake.Pyrelands.PyrelandsTuning.FireRiteCarryPerPawn);

            Scribe_Values.Look(ref arsonDebtRaidThreshold, "arsonDebtRaidThreshold", RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtRaidThreshold);
            Scribe_Values.Look(ref flameHarvestMinFires, "flameHarvestMinFires", RimMandrake.Pyrelands.PyrelandsTuning.FlameHarvestMinFires);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(PyrelandsMechanicsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(PyrelandsMechanicsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "The Tribes answer the burn", RimMandrake.Shared.SettingScope.NextPulse, new[] { "arsonJusticeEnabled", "arsonDebtRaidThreshold", "flameHarvestEnabled", "flameHarvestMinFires" }))
            {
                list.CheckboxLabeled("Arson-justice raids", ref arsonJusticeEnabled,
                    "Off: the Tribes never raid over an unplanned burn, however much arson debt the colony racks up. Read when the storyteller rolls the raid.");
                list.Label((TaggedString)("Arson debt before a raid: " + arsonDebtRaidThreshold.ToString("0")), -1f, "Read when the raid is rolled.");
                arsonDebtRaidThreshold = list.Slider(arsonDebtRaidThreshold, 100f, RimMandrake.Pyrelands.PyrelandsTuning.ArsonDebtCap);
                list.CheckboxLabeled("Flame-harvest visits", ref flameHarvestEnabled,
                    "Off: the Tribes never send a peaceful party to walk a live burn-line. Read when the storyteller rolls the visit.");
                list.Label((TaggedString)("Minimum standing fires to draw a visit: " + flameHarvestMinFires.ToString()), -1f, "Read when the visit is rolled.");
                flameHarvestMinFires = Mathf.RoundToInt(list.Slider(flameHarvestMinFires, 1f, 50f));
                list.GapLine();
            }

            if (Group(list, "The Deep Tribes' fire rite", RimMandrake.Shared.SettingScope.NextPulse, new[] { "fireRiteEnabled", "fireRiteFraction", "fireRiteGroupMin", "fireRiteGroupMax", "fireRiteHarvestHours" }))
            {
                list.CheckboxLabeled("The Tribes sometimes light the burn themselves", ref fireRiteEnabled,
                    "On (shipped): some of the fire clock's burns arrive as a rite: a small Deep Tribes party walks onto the map, torches the grass where they stand, works the burn for scorch-fruit and leaves with it. Off: the clock lights every front itself and the Tribes never come for it. Either way the burn happens on schedule; this only changes whose hand is on it. Read when a front is scheduled.");
                list.Label((TaggedString)("Rites instead of plain fronts: " + fireRiteFraction.ToStringPercent("0")), -1f, "Read when a front is scheduled.");
                fireRiteFraction = list.Slider(fireRiteFraction, 0f, 1f);
                list.Label((TaggedString)("Party size, smallest: " + fireRiteGroupMin.ToString()), -1f, "Read when the party is formed; never above the largest.");
                fireRiteGroupMin = Mathf.RoundToInt(list.Slider(fireRiteGroupMin, 1f, 12f));
                list.Label((TaggedString)("Party size, largest: " + fireRiteGroupMax.ToString()), -1f, "Read when the party is formed.");
                fireRiteGroupMax = Mathf.RoundToInt(list.Slider(fireRiteGroupMax, 1f, 12f));
                list.Label((TaggedString)("In-game hours they work the burn: " + fireRiteHarvestHours.ToString("0.0")), -1f, "Read when the party arrives.");
                fireRiteHarvestHours = list.Slider(fireRiteHarvestHours, 1f, 24f);
                list.GapLine();
            }

            if (Group(list, "What the rite carries off", RimMandrake.Shared.SettingScope.Now, new[] { "fireRiteCarryPerPawn" }))
            {
                list.Label((TaggedString)("Scorch fruit each harvester carries off: " + fireRiteCarryPerPawn.ToString() + " (" + (fireRiteCarryPerPawn * fireRiteGroupMin) + "-" + (fireRiteCarryPerPawn * fireRiteGroupMax) + " a rite)"), -1f, "The number that is the experience: the party competes with you for scorch-fruit. 0 is lawful: they still come, still light it, and take nothing. Read by the harvest job every time it runs.");
                fireRiteCarryPerPawn = Mathf.RoundToInt(list.Slider(fireRiteCarryPerPawn, 0f, 100f));
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class PyrelandsMechanicsMod : Mod
    {
        public static PyrelandsMechanicsSettings settings;

        public PyrelandsMechanicsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PyrelandsMechanicsSettings>();

            // PYRELANDS_RM_MOD_BUILD_1 §6 — fill in RM_Pyrelands' fire-rite hook
            // so its franchise-free fire clock can offer this mod's Deep Tribes
            // rite a chance to intercept a scheduled front. Left null (never
            // set) on a franchise-free world where this mod is not loaded at
            // all — that is the "all-off degrades to the plain front" case.
            RimMandrake.Pyrelands.PyrelandsFireRiteHook.TrySend = PyrelandsFireRite.TrySend;
        }

        public override string SettingsCategory()
        {
            return "Pyrelands Mechanics";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
