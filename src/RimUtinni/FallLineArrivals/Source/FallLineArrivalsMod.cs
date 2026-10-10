using System.Reflection;
using System.Collections.Generic;
using System;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.FallLineArrivals
{
    // FALL_LINE_ARRIVAL_MECHANISM_1 — Mod Settings (spec §10). Defaults are the shipped behaviour;
    // all-off degrades to "the Fall Line is just empty desert", a legal state. No setting touches a
    // wildAnimals table: the ambient route is the mechanism the owner rejected (fall_line.md §8a).
    public class FallLineArrivalsSettings : ModSettings
    {
        public static bool onlyOnFallLine = true;

        public static bool wreckFallsEnabled = true;
        public static float wreckFrequency = 1f;
        public static bool wreckHull = true;
        public static bool wreckCargo = true;
        public static bool wreckTank = true;

        // FALL_LINE_FERAL_SURVIVORS_BUILD_1 (Band B, spec §10)
        public static bool survivorsEnabled = true;
        public static float survivorFrequency = 1f;
        public static float wreckLurkerChance = 0.3f;
        public static bool allowDestroyer = true;
        public static int maxFeralPerMap = 3;
        public static bool feralAttackInstead = false;
        // FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 (§8b feral races)
        public static bool feralRacesEnabled = true;

        public static bool labRatEnabled = true;
        public static float labRatFrequency = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref onlyOnFallLine, "onlyOnFallLine", true);
            Scribe_Values.Look(ref wreckFallsEnabled, "wreckFallsEnabled", true);
            Scribe_Values.Look(ref wreckFrequency, "wreckFrequency", 1f);
            Scribe_Values.Look(ref wreckHull, "wreckHull", true);
            Scribe_Values.Look(ref wreckCargo, "wreckCargo", true);
            Scribe_Values.Look(ref wreckTank, "wreckTank", true);
            Scribe_Values.Look(ref survivorsEnabled, "survivorsEnabled", true);
            Scribe_Values.Look(ref survivorFrequency, "survivorFrequency", 1f);
            Scribe_Values.Look(ref wreckLurkerChance, "wreckLurkerChance", 0.3f);
            Scribe_Values.Look(ref allowDestroyer, "allowDestroyer", true);
            Scribe_Values.Look(ref maxFeralPerMap, "maxFeralPerMap", 3);
            Scribe_Values.Look(ref feralAttackInstead, "feralAttackInstead", false);
            Scribe_Values.Look(ref feralRacesEnabled, "feralRacesEnabled", true);
            Scribe_Values.Look(ref labRatEnabled, "labRatEnabled", true);
            Scribe_Values.Look(ref labRatFrequency, "labRatFrequency", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(FallLineArrivalsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(FallLineArrivalsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Where events fire", RimMandrake.Shared.SettingScope.NextPulse, new[] { "onlyOnFallLine" }))
            {
                list.CheckboxLabeled("Only on Fall Line maps", ref onlyOnFallLine,
                    "On: these events fire only on a map whose tile is part of the Fall Line. Off: they fire on any colony map. This changes which maps get events when the storyteller rolls; it is not worldgen.");
                list.GapLine();
            }

            if (Group(list, "Wrecks fall (ship-vermin nests)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "wreckFallsEnabled", "wreckFrequency", "wreckHull", "wreckCargo", "wreckTank" }))
            {
                list.CheckboxLabeled("Wrecks fall (ship-vermin nests)", ref wreckFallsEnabled,
                    "A wreck comes down near the colony. It is salvage, and ship-vermin crawl out of it until it is stripped (Ship Vermin's settings choose which species, and cap them at 12 per map).");
                list.Label((TaggedString)("Wreck frequency: " + "x" + wreckFrequency.ToString("0.00")), -1f, "Multiplies the incident's base chance at each roll.");
                wreckFrequency = list.Slider(wreckFrequency, 0.25f, 4f);
                list.CheckboxLabeled("Hull ribs (mostly mynocks)", ref wreckHull,
                    "Whether this wreck kind can be picked.");
                list.CheckboxLabeled("Cargo sections (mostly scavrats and womp rats)", ref wreckCargo,
                    "Whether this wreck kind can be picked.");
                list.CheckboxLabeled("Fuel tanks (mostly zhakkas)", ref wreckTank,
                    "Whether this wreck kind can be picked.");
                list.GapLine();
            }

            if (Group(list, "Fall survivors (feral droids)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "survivorsEnabled", "survivorFrequency", "wreckLurkerChance", "maxFeralPerMap", "allowDestroyer", "feralAttackInstead", "feralRacesEnabled" }))
            {
                list.CheckboxLabeled("Fall survivors (feral droids)", ref survivorsEnabled,
                    "Droids that survived a fall and have lived out on the flats ever since. They belong to no one, run from people, hide in wreckage and fight only when cornered. Down one, take it prisoner, and a wild-keyed data spike wipes it clean. Needs Droidworks for the droids themselves.");
                list.Label((TaggedString)("Drift-in frequency: " + "x" + survivorFrequency.ToString("0.00")), -1f, "Multiplies the incident's base chance at each roll.");
                survivorFrequency = list.Slider(survivorFrequency, 0.25f, 4f);
                list.Label((TaggedString)("Chance a fallen wreck hides one: " + wreckLurkerChance.ToStringPercent()), -1f, "Rolled when a wreck falls.");
                wreckLurkerChance = Mathf.Round(list.Slider(wreckLurkerChance, 0f, 1f) * 20f) / 20f;
                list.Label((TaggedString)("Most feral droids on one map: " + maxFeralPerMap.ToString()), -1f, "Checked when one would arrive.");
                maxFeralPerMap = Mathf.RoundToInt(list.Slider(maxFeralPerMap, 1f, 10f));
                list.CheckboxLabeled("Allow the destroyer droid (the one dangerous survivor)", ref allowDestroyer,
                    "Off: it is never picked.");
                list.CheckboxLabeled("They attack instead of running (like a wild droid)", ref feralAttackInstead,
                    "Off (the ruled behaviour): they flee and hide. On: they attack on sight, the way the desert's wild droids do. Read when a survivor arrives.");
                list.CheckboxLabeled("Feral people too (crash survivors)", ref feralRacesEnabled,
                    "People who survived a fall and went feral out on the flats arrive the same ways the droids do, and behave the same. Capture and enslave one (or recruit them) and they keep a permanent Fall Line scar: unlike a droid, there is nothing to wipe.");
                list.GapLine();
            }

            if (Group(list, "The specimen (a lab rat in an escape pod)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "labRatEnabled", "labRatFrequency" }))
            {
                list.CheckboxLabeled("The specimen (a lab rat in an escape pod)", ref labRatEnabled,
                    "Very rarely, one escape pod lands holding a single white lab rat, and nothing else.");
                list.Label((TaggedString)("Specimen frequency: " + "x" + labRatFrequency.ToString("0.00")), -1f, "Multiplies the incident's base chance at each roll.");
                labRatFrequency = list.Slider(labRatFrequency, 0.25f, 4f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class FallLineArrivalsMod : Mod
    {
        public static FallLineArrivalsSettings settings;

        public FallLineArrivalsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<FallLineArrivalsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Fall Line Arrivals";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>
    /// Spec §3.3: "is this map ON the Fall Line?" — primary gate is the hand-placed RUT_FallLine tile
    /// mutator; until that world-authoring pass lands (filed), the tile's world feature name is
    /// accepted too (the canonical worldmap names the two halves "Fall Line" and "The Breaks"; whether
    /// the in-game WorldFeature carries exactly those names is UNMEASURED — the first live poke).
    /// </summary>
    public static class FallLineGate
    {
        private static readonly string[] FeatureNames = { "Fall Line", "The Fall Line", "The Breaks" };

        private static TileMutatorDef mutator;

        private static TileMutatorDef Mutator =>
            mutator ?? (mutator = DefDatabase<TileMutatorDef>.GetNamedSilentFail("RUT_FallLine"));

        public static bool OnFallLine(Map map)
        {
            Tile tile = map?.TileInfo;
            if (tile == null)
            {
                return false;
            }
            if (Mutator != null && tile.Mutators.Contains(Mutator))
            {
                return true;
            }
            string name = tile.feature?.name;
            if (name.NullOrEmpty())
            {
                return false;
            }
            foreach (string n in FeatureNames)
            {
                if (string.Equals(name, n, StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }
            return false;
        }

        public static bool Allowed(Map map)
        {
            return map != null && (!FallLineArrivalsSettings.onlyOnFallLine || OnFallLine(map));
        }
    }

    /// <summary>Bridge proof (jawa/static_call): asks the real FallLineGate on the current map, independent of the
    /// incident's earliestDay / cooldown gates. Returns "ALLOWED ..." or "REFUSED ..." plus the reason and inputs.</summary>
    public static class FallLineGateProof
    {
        public static string ProofGate(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "REFUSED: no current map";
            }
            bool setting = FallLineArrivalsSettings.onlyOnFallLine;
            bool on = FallLineGate.OnFallLine(map);
            bool allowed = FallLineGate.Allowed(map);
            string reason = allowed
                ? (setting ? "setting ON and map is on the Fall Line" : "setting OFF so any map is allowed")
                : "setting ON and map is not on the Fall Line";
            return (allowed ? "ALLOWED" : "REFUSED") + ": " + reason
                + " onlyOnFallLine=" + setting + " onFallLine=" + on;
        }
    }
}
