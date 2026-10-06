using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_GLASS_LENS_CHAIN_1 §12 — Mod Settings for the glass-and-lens
    // chain. Its own Mod class (RimWorld instantiates every Mod subclass in an
    // assembly, each with its own settings file), same as the event creatures.
    //
    // Drift yield (the shovel half of §1) lives with the dune engine that owns
    // the clear job: MovingDunes' own settings panel. Stillsand fulgurites ride
    // the Pyrelands' fulgurite toggle, which no longer needs the Pyrelands
    // master switch off Pyrelands ground.
    //
    // A table toggled off still stands but works no bills and says why. All
    // off: the items remain plain trade goods.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GlassChainSettings : ModSettings
    {
        public static bool sunFurnaceEnabled = true;
        public static bool lensBenchEnabled = true;
        public static bool solarOvenEnabled = true;
        public static float sunWorkSpeedMultiplier = 1f;
        public static bool sieveEnabled = true;
        public static float sieveYieldMultiplier = 1f;
        public static bool solarStillEnabled = true;
        public static float stillRateMultiplier = 1f;
        public static bool wringingStillEnabled = true;
        public static bool sunLanceEnabled = true;
        public static bool geophoneEnabled = true;
        public static float geophoneRadius = 20f;
        public static bool kraytLensEnabled = true;
        public static bool glassGogglesEnabled = true;

        // Recipes the Mod Settings can hide. Read by the RecipeDef.AvailableNow postfix below.
        public static bool RecipeHidden(string defName)
        {
            if (defName == "RSW_GrindKraytLens") return !kraytLensEnabled;
            if (defName == "RM_SunGogglesGlass") return !glassGogglesEnabled;
            return false;
        }

        public static bool TableEnabled(RM_SunTableKind kind)
        {
            switch (kind)
            {
                case RM_SunTableKind.furnace: return sunFurnaceEnabled;
                case RM_SunTableKind.lensBench: return lensBenchEnabled;
                case RM_SunTableKind.oven: return solarOvenEnabled;
                case RM_SunTableKind.still: return solarStillEnabled;
                default: return true;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sunFurnaceEnabled, "sunFurnaceEnabled", true);
            Scribe_Values.Look(ref lensBenchEnabled, "lensBenchEnabled", true);
            Scribe_Values.Look(ref solarOvenEnabled, "solarOvenEnabled", true);
            Scribe_Values.Look(ref sunWorkSpeedMultiplier, "sunWorkSpeedMultiplier", 1f);
            Scribe_Values.Look(ref sieveEnabled, "sieveEnabled", true);
            Scribe_Values.Look(ref sieveYieldMultiplier, "sieveYieldMultiplier", 1f);
            Scribe_Values.Look(ref solarStillEnabled, "solarStillEnabled", true);
            Scribe_Values.Look(ref stillRateMultiplier, "stillRateMultiplier", 1f);
            Scribe_Values.Look(ref wringingStillEnabled, "wringingStillEnabled", true);
            Scribe_Values.Look(ref sunLanceEnabled, "sunLanceEnabled", true);
            Scribe_Values.Look(ref geophoneEnabled, "geophoneEnabled", true);
            Scribe_Values.Look(ref geophoneRadius, "geophoneRadius", 20f);
            Scribe_Values.Look(ref kraytLensEnabled, "kraytLensEnabled", true);
            Scribe_Values.Look(ref glassGogglesEnabled, "glassGogglesEnabled", true);
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
            list.Label("Sun-fed work tables burn no fuel and draw no power. They work only in open sun: "
                       + "not under a roof, not in shade, not in a sand gale.");
            list.GapLine();
            list.CheckboxLabeled("Sun furnace", ref sunFurnaceEnabled,
                "Melts glass sand into sun glass and fine sand into lens glass. Off: it stands idle.");
            list.CheckboxLabeled("Lens bench", ref lensBenchEnabled,
                "Grinds lens glass into precision lenses and pearl lenses. Off: it stands idle.");
            list.CheckboxLabeled("Solar oven", ref solarOvenEnabled,
                "Cooks meals with no fuel. The crest-plate oven also bakes sun glass. Off: both stand idle.");
            list.Label("Sun work speed: x" + sunWorkSpeedMultiplier.ToString("0.00"));
            sunWorkSpeedMultiplier = list.Slider(sunWorkSpeedMultiplier, 0.25f, 3f);
            list.GapLine();
            list.CheckboxLabeled("Sand sieve chore", ref sieveEnabled,
                "Pawns carrying a sand sieve sift glass sand in the home area into fine sand, unordered. Off: nobody sifts and no pawn fetches a sieve.");
            list.Label("Sieve yield: x" + sieveYieldMultiplier.ToString("0.00") + " fine sand");
            sieveYieldMultiplier = list.Slider(sieveYieldMultiplier, 0.25f, 3f);
            list.GapLine();
            list.CheckboxLabeled("Solar still", ref solarStillEnabled,
                "A glazed lens condenser distils water from brine, eggs and raw meat in open sun. Off: stills stand idle.");
            list.CheckboxLabeled("Wringing still", ref wringingStillEnabled,
                "The wringing still also distils corpses, and onlookers dislike it. Off: it stands idle.");
            list.Label("Still rate: x" + stillRateMultiplier.ToString("0.00"));
            stillRateMultiplier = list.Slider(stillRateMultiplier, 0.25f, 3f);
            list.GapLine();
            list.CheckboxLabeled("Sun lance", ref sunLanceEnabled,
                "The heliostat turret focuses the fixed sun on one target. It heats and never ignites, scales with the sun's elevation, and does nothing in shade, under a roof or in a sand gale. Off: it stands idle.");
            list.GapLine();
            list.CheckboxLabeled("Geophone", ref geophoneEnabled,
                "A staked biosilica resonator turns rumbles under the sand into a rough bearing and size class. It cannot tell a lure's drumming from a real swimmer. Off: it hears nothing.");
            list.Label("Geophone radius: " + Mathf.RoundToInt(geophoneRadius) + " cells");
            geophoneRadius = Mathf.Round(list.Slider(geophoneRadius, 8f, 40f));
            list.GapLine();
            list.CheckboxLabeled("Krayt lens recipe", ref kraytLensEnabled,
                "The lens bench grinds a krayt pearl into a krayt lens (needs the Star Wars bestiary's pearl). Off: the recipe is hidden.");
            list.CheckboxLabeled("Sun-glass goggles recipe", ref glassGogglesEnabled,
                "Sun-glass goggles are a second way to make glare-proof eyewear, from sun glass and cloth. Off: the recipe is hidden.");
            list.GapLine();
            list.Label("Glass sand from shovelled drifts is set in \"Moving Dunes\". Fulgurites on sand "
                       + "follow the Pyrelands' fulgurite toggle.");
            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_GlassChainMod : Mod
    {
        public static RM_GlassChainSettings settings;

        public RM_GlassChainMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GlassChainSettings>();
            ArmPatches();
        }

        private static void ArmPatches()
        {
            const string rule = "[RimMandrake.Stillsand] sun-table gate: ";
            try
            {
                var target = AccessTools.Method(typeof(Building_WorkTable), "UsableForBillsAfterFueling");
                if (target == null)
                {
                    Log.Error(rule + "TARGET METHOD NOT FOUND, sun tables are NOT gated by the sun.");
                }
                else new Harmony("mandrake.rm.stillsand.glasschain")
                    .Patch(target, postfix: new HarmonyMethod(typeof(Patch_WorkTable_SunGate), "Postfix"));
            }
            catch (Exception e)
            {
                Log.Error(rule + "patch FAILED, sun tables are NOT gated by the sun: " + e.Message);
            }
            try
            {
                var avail = AccessTools.PropertyGetter(typeof(RecipeDef), "AvailableNow");
                if (avail == null)
                {
                    Log.Error("[RimMandrake.Stillsand] RecipeDef.AvailableNow getter NOT FOUND, the krayt-lens and glass-goggles toggles do nothing.");
                    return;
                }
                new Harmony("mandrake.rm.stillsand.glasschain.recipes")
                    .Patch(avail, postfix: new HarmonyMethod(typeof(Patch_Recipe_Toggle), "Postfix"));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Stillsand] recipe toggle patch FAILED: " + e.Message);
            }
        }

        public override string SettingsCategory()
        {
            return "Stillsand: glass and lenses";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    // Hides the recipes the Mod Settings switch off. Hidden recipes drop out of the bill menu.
    public static class Patch_Recipe_Toggle
    {
        public static void Postfix(RecipeDef __instance, ref bool __result)
        {
            if (__result && RM_GlassChainSettings.RecipeHidden(__instance.defName)) __result = false;
        }
    }
}
