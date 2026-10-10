using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// Mod Settings per the standing rule (owner, 2026-09-12): a toggle per major mechanic, a
    /// slider wherever a number IS the experience, defaults equal to shipped behavior, and
    /// all-off degrading gracefully.
    ///
    /// All-off here leaves a powered cylinder that holds one pawn and does nothing to them —
    /// still buildable, still placeable, still ejects on command. Nothing errors, nothing
    /// disappears from a save.
    ///
    /// None of these settings affect worldgen. Every one is read live by the tank's tick, job or use
    /// code (audited 2026-10-10), so each group is tagged "now".
    /// </summary>
    public class BactaSettings : ModSettings
    {
        // ---- Master switches, one per mechanic -------------------------------------------
        public static bool healingEnabled = true;
        public static bool scarErasureEnabled = true;
        public static bool infectionAssistEnabled = true;
        public static bool suspendNeedsEnabled = true;
        public static bool autoEjectEnabled = true;

        /// <summary>
        /// BACTA_REVIVAL_MECHANIC_1. Shipped OFF: reviving the dead is a bigger claim than
        /// healing the living, and a player should opt into it deliberately.
        /// </summary>
        public static bool revivalEnabled = false;

        /// <summary>BACTA_SIDE_ITEMS_1: the 2-1B-style medical droid facility.</summary>
        public static bool medicalDroidEnabled = true;

        /// <summary>BACTA_SIDE_ITEMS_1: the field consumables (bacta patch, bacta spray).</summary>
        public static bool fieldItemsEnabled = true;

        // ---- Tunables --------------------------------------------------------------------
        public static float woundHealPerDay = BactaTuning.WoundHealPerDay;
        public static float scarHealPerDay = BactaTuning.ScarHealPerDay;
        public static float immunityGainPerDay = BactaTuning.ImmunityGainPerDay;
        public static float fluidCostPerDay = BactaTuning.FluidCostPerDay;
        public static float tendQuality = BactaTuning.TendQuality;

        /// <summary>
        /// Hours since death a corpse stays eligible for the tank. Owner ruling verbatim:
        /// "works on dead bodies IF retrieved within a few hours."
        /// </summary>
        public static float revivalWindowHours = BactaTuning.RevivalWindowHours;

        /// <summary>BACTA_SIDE_ITEMS_1: multiplies the tank's heal/scar/immunity rates while a linked, powered RSW_MedicalDroid is active.</summary>
        public static float medicalDroidHealMultiplier = BactaTuning.MedicalDroidHealMultiplier;

        /// <summary>BACTA_SIDE_ITEMS_1: multiplies every field item's per-use wound/scar/immunity amounts.</summary>
        public static float fieldItemPotency = BactaTuning.FieldItemPotency;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref healingEnabled, "healingEnabled", true);
            Scribe_Values.Look(ref scarErasureEnabled, "scarErasureEnabled", true);
            Scribe_Values.Look(ref infectionAssistEnabled, "infectionAssistEnabled", true);
            Scribe_Values.Look(ref suspendNeedsEnabled, "suspendNeedsEnabled", true);
            Scribe_Values.Look(ref autoEjectEnabled, "autoEjectEnabled", true);
            Scribe_Values.Look(ref revivalEnabled, "revivalEnabled", defaultValue: false);
            Scribe_Values.Look(ref medicalDroidEnabled, "medicalDroidEnabled", true);
            Scribe_Values.Look(ref fieldItemsEnabled, "fieldItemsEnabled", true);

            Scribe_Values.Look(ref woundHealPerDay, "woundHealPerDay", BactaTuning.WoundHealPerDay);
            Scribe_Values.Look(ref scarHealPerDay, "scarHealPerDay", BactaTuning.ScarHealPerDay);
            Scribe_Values.Look(ref immunityGainPerDay, "immunityGainPerDay", BactaTuning.ImmunityGainPerDay);
            Scribe_Values.Look(ref fluidCostPerDay, "fluidCostPerDay", BactaTuning.FluidCostPerDay);
            Scribe_Values.Look(ref tendQuality, "tendQuality", BactaTuning.TendQuality);
            Scribe_Values.Look(ref revivalWindowHours, "revivalWindowHours", BactaTuning.RevivalWindowHours);
            Scribe_Values.Look(ref medicalDroidHealMultiplier, "medicalDroidHealMultiplier", BactaTuning.MedicalDroidHealMultiplier);
            Scribe_Values.Look(ref fieldItemPotency, "fieldItemPotency", BactaTuning.FieldItemPotency);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(BactaSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(BactaSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "The fluid's work", RimMandrake.Shared.SettingScope.Now, new[] { "healingEnabled", "woundHealPerDay", "tendQuality" }))
            {
                list.CheckboxLabeled("Accelerated healing", ref healingEnabled,
                    "Off: a bacta tank becomes a powered cylinder that holds one pawn and heals "
                  + "nothing. It still builds, still takes an occupant, and still ejects on command.");
                list.Label("Wound healing: " + woundHealPerDay.ToString("0") + " severity per day per injury"
                    + "   (shipped: " + BactaTuning.WoundHealPerDay.ToString("0") + ")");
                woundHealPerDay = Mathf.Round(list.Slider(woundHealPerDay, 2f, 120f));

                list.Label("Wound tending quality applied on immersion: " + tendQuality.ToString("0.00"));
                tendQuality = list.Slider(tendQuality, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Scars and permanent injuries", RimMandrake.Shared.SettingScope.Now, new[] { "scarErasureEnabled", "scarHealPerDay" }))
            {
                list.CheckboxLabeled("Erase scars and permanent physical injuries", ref scarErasureEnabled,
                    "Off: bacta closes fresh wounds but never fades an old scar or a permanent "
                  + "injury. Missing limbs and organs are never regrown either way — bacta heals, "
                  + "it does not regenerate.");
                list.Label("Scar erasure: " + scarHealPerDay.ToString("0.0") + " severity per day"
                    + "   (shipped: " + BactaTuning.ScarHealPerDay.ToString("0.0") + ")");
                scarHealPerDay = list.Slider(scarHealPerDay, 0.2f, 20f);
                list.GapLine();
            }

            if (Group(list, "Infections", RimMandrake.Shared.SettingScope.Now, new[] { "infectionAssistEnabled", "immunityGainPerDay" }))
            {
                list.CheckboxLabeled("Help fight treatable infections", ref infectionAssistEnabled,
                    "Off: bacta does nothing at all for disease. On, it only helps where medicine "
                  + "could have helped — an untendable illness runs its course in the tank exactly "
                  + "as it would in a bed.");
                list.Label("Extra immunity gained: " + immunityGainPerDay.ToString("0.00") + " per day"
                    + "   (shipped: " + BactaTuning.ImmunityGainPerDay.ToString("0.00") + ")");
                immunityGainPerDay = list.Slider(immunityGainPerDay, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Fluid cost", RimMandrake.Shared.SettingScope.Now, new[] { "fluidCostPerDay" }))
            {
                list.Label("Bacta consumed: " + fluidCostPerDay.ToString("0.0") + " per day while healing"
                    + "   (shipped: " + BactaTuning.FluidCostPerDay.ToString("0.0") + ")");
                fluidCostPerDay = list.Slider(fluidCostPerDay, 0f, 40f);
                list.GapLine();
            }

            if (Group(list, "The occupant", RimMandrake.Shared.SettingScope.Now, new[] { "suspendNeedsEnabled", "autoEjectEnabled" }))
            {
                list.CheckboxLabeled("Suspend hunger and tiredness while immersed", ref suspendNeedsEnabled,
                    "On (shipped): the tank feeds and rests its occupant, so a multi-day immersion "
                  + "does not starve them. Off: hunger and tiredness run normally inside the tank, "
                  + "and a long immersion needs watching.");
                list.CheckboxLabeled("Eject automatically", ref autoEjectEnabled,
                    "On (shipped): the occupant is let out when there is nothing left to heal, or "
                  + "when the tank runs dry. Off: they stay in until ejected by hand.");
                list.GapLine();
            }

            if (Group(list, "Revival", RimMandrake.Shared.SettingScope.Now, new[] { "revivalEnabled", "revivalWindowHours" }))
            {
                list.CheckboxLabeled("Revive the recently dead", ref revivalEnabled,
                    "Off (shipped): the tank never touches a corpse. On: a fresh corpse of ours — "
                  + "one retrieved within the window below — can be carried into an empty tank and "
                  + "revived. The revived pawn keeps whatever bacta can't fix: no missing part "
                  + "regrows, and nothing about the brain or the mind is touched. It then heals in "
                  + "the tank exactly like a living occupant.");
                list.Label("Revival window: " + revivalWindowHours.ToString("0.0") + " hours since death"
                    + "   (shipped: " + BactaTuning.RevivalWindowHours.ToString("0.0") + ")");
                revivalWindowHours = list.Slider(revivalWindowHours, 0.5f, 48f);
                list.GapLine();
            }

            if (Group(list, "Medical droid (BACTA_SIDE_ITEMS_1)", RimMandrake.Shared.SettingScope.Now, new[] { "medicalDroidEnabled", "medicalDroidHealMultiplier" }))
            {
                list.CheckboxLabeled("2-1B-style medical droid speeds the tank", ref medicalDroidEnabled,
                    "On (shipped): a powered RSW_MedicalDroid linked to a bacta tank multiplies its "
                  + "wound/scar/immunity rates while it is active. Off: the droid still builds and "
                  + "links, but does nothing.");
                list.Label("Droid speed multiplier: " + medicalDroidHealMultiplier.ToString("0.00") + "x"
                    + "   (shipped: " + BactaTuning.MedicalDroidHealMultiplier.ToString("0.00") + "x)");
                medicalDroidHealMultiplier = list.Slider(medicalDroidHealMultiplier, 1f, 3f);
                list.GapLine();
            }

            if (Group(list, "Field kit (BACTA_SIDE_ITEMS_1)", RimMandrake.Shared.SettingScope.Now, new[] { "fieldItemsEnabled", "fieldItemPotency" }))
            {
                list.CheckboxLabeled("Bacta patch and bacta spray are usable", ref fieldItemsEnabled,
                    "Off: the patch and the spray still build/buy but their Use option is disabled "
                  + "— nothing happens if used. On (shipped): each is a one-shot field dose of the "
                  + "same guarded mechanism the tank runs, scaled down. Neither ever regrows a "
                  + "missing part or touches the brain — same law as the tank.");
                list.Label("Field item potency: " + fieldItemPotency.ToString("0.00") + "x"
                    + "   (shipped: " + BactaTuning.FieldItemPotency.ToString("0.00") + "x)");
                fieldItemPotency = list.Slider(fieldItemPotency, 0.25f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class BactaMod : Mod
    {
        public static BactaSettings settings;

        public BactaMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<BactaSettings>();
        }

        public override string SettingsCategory()
        {
            return "RimStarWars — Bacta";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
