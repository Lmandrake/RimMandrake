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
            Scribe_Values.Look(ref labRatEnabled, "labRatEnabled", true);
            Scribe_Values.Look(ref labRatFrequency, "labRatFrequency", 1f);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

            list.CheckboxLabeled("Only on Fall Line maps", ref onlyOnFallLine,
                "On: these events fire only on a map whose tile is part of the Fall Line. Off: they fire on "
              + "any colony map. This changes which maps get events; it is not worldgen.");

            list.GapLine();
            list.CheckboxLabeled("Wrecks fall (ship-vermin nests)", ref wreckFallsEnabled,
                "A wreck comes down near the colony. It is salvage, and ship-vermin crawl out of it until it is "
              + "stripped (Ship Vermin's settings choose which species, and cap them at 12 per map).");
            if (wreckFallsEnabled)
            {
                list.Label("Wreck frequency: x" + wreckFrequency.ToString("0.00"));
                wreckFrequency = list.Slider(wreckFrequency, 0.25f, 4f);
                list.CheckboxLabeled("  Hull ribs (mostly mynocks)", ref wreckHull);
                list.CheckboxLabeled("  Cargo sections (mostly scavrats and womp rats)", ref wreckCargo);
                list.CheckboxLabeled("  Fuel tanks (mostly zhakkas)", ref wreckTank);
            }

            list.GapLine();
            list.CheckboxLabeled("Fall survivors (feral droids)", ref survivorsEnabled,
                "Droids that survived a fall and have lived out on the flats ever since. They belong to no one, "
              + "run from people, hide in wreckage and fight only when cornered. One drifts in now and then, and "
              + "some fallen wrecks hide one that bolts when a colonist comes near. Down one, take it prisoner, and "
              + "a wild-keyed data spike wipes it clean. Needs Droidworks for the droids themselves.");
            if (survivorsEnabled)
            {
                list.Label("Drift-in frequency: x" + survivorFrequency.ToString("0.00"));
                survivorFrequency = list.Slider(survivorFrequency, 0.25f, 4f);
                list.Label("Chance a fallen wreck hides one: " + wreckLurkerChance.ToStringPercent());
                wreckLurkerChance = Mathf.Round(list.Slider(wreckLurkerChance, 0f, 1f) * 20f) / 20f;
                list.Label("Most feral droids on one map: " + maxFeralPerMap);
                maxFeralPerMap = Mathf.RoundToInt(list.Slider(maxFeralPerMap, 1f, 10f));
                list.CheckboxLabeled("  Allow the destroyer droid (the one dangerous survivor)", ref allowDestroyer);
                list.CheckboxLabeled("  They attack instead of running (like a wild droid)", ref feralAttackInstead,
                    "Off (the ruled behaviour): they flee and hide. On: they attack on sight, the way the desert's "
                  + "wild droids do.");
            }

            list.GapLine();
            list.CheckboxLabeled("The specimen (a lab rat in an escape pod)", ref labRatEnabled,
                "Very rarely, one escape pod lands holding a single white lab rat, and nothing else.");
            if (labRatEnabled)
            {
                list.Label("Specimen frequency: x" + labRatFrequency.ToString("0.00"));
                labRatFrequency = list.Slider(labRatFrequency, 0.25f, 4f);
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
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
}
