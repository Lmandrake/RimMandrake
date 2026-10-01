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

        public static bool TableEnabled(RM_SunTableKind kind)
        {
            switch (kind)
            {
                case RM_SunTableKind.furnace: return sunFurnaceEnabled;
                case RM_SunTableKind.lensBench: return lensBenchEnabled;
                case RM_SunTableKind.oven: return solarOvenEnabled;
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
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
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
            list.Label("Glass sand from shovelled drifts is set in \"Moving Dunes\". Fulgurites on sand "
                       + "follow the Pyrelands' fulgurite toggle.");
            list.End();
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
                    return;
                }
                new Harmony("mandrake.rm.stillsand.glasschain")
                    .Patch(target, postfix: new HarmonyMethod(typeof(Patch_WorkTable_SunGate), "Postfix"));
            }
            catch (Exception e)
            {
                Log.Error(rule + "patch FAILED, sun tables are NOT gated by the sun: " + e.Message);
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
}
