using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Wasteland. Pattern copied
    // from RM_GreentideSettings / RM_TheRotSettings (static fields read from
    // everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass). Defaults = shipped behavior throughout.
    //
    // Owned mechanics: the brine mining archetype (three GenStepDefs scattering
    // RM_BrineDeposit_Tekk/Drazz/BrinePlate — its toggle is still scaffolding:
    // the scatter is plain XML with no runtime gate), and the
    // WASTELAND_MECHANICS_BUILD_1 layer — storm dose / ash-fall pollution /
    // cinderfelt germination (RM_MapComponent_WastelandStorms), ambient dose and
    // radiothermal heat (RM_CompAmbientDose, RM_CompRadiothermalHeat), and the
    // processor animals (RM_CompProcessorGatherable). Each of those reads its
    // toggle below at runtime.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WastelandSettings : ModSettings
    {
        public static bool wastelandEnabled = true;
        public static bool brineDepositsEnabled = true;

        // WASTELAND_MECHANICS_BUILD_1 (tranche 1). Every one defaults ON = shipped
        // behaviour; off degrades to "the weather/creature still exists, the
        // mechanic does nothing".
        public static bool stormDoseEnabled = true;
        public static float stormDoseMultiplier = 1f;
        public static bool ashFallPollutionEnabled = true;
        public static bool cinderfeltGerminationEnabled = true;
        public static bool ambientDoseEnabled = true;
        public static float ambientDoseMultiplier = 1f;
        public static bool radiothermalHeatEnabled = true;
        public static bool processorGatherEnabled = true;
        public static bool processorUnpolluteEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wastelandEnabled, "wastelandEnabled", true);
            Scribe_Values.Look(ref brineDepositsEnabled, "brineDepositsEnabled", true);
            Scribe_Values.Look(ref stormDoseEnabled, "stormDoseEnabled", true);
            Scribe_Values.Look(ref stormDoseMultiplier, "stormDoseMultiplier", 1f);
            Scribe_Values.Look(ref ashFallPollutionEnabled, "ashFallPollutionEnabled", true);
            Scribe_Values.Look(ref cinderfeltGerminationEnabled, "cinderfeltGerminationEnabled", true);
            Scribe_Values.Look(ref ambientDoseEnabled, "ambientDoseEnabled", true);
            Scribe_Values.Look(ref ambientDoseMultiplier, "ambientDoseMultiplier", 1f);
            Scribe_Values.Look(ref radiothermalHeatEnabled, "radiothermalHeatEnabled", true);
            Scribe_Values.Look(ref processorGatherEnabled, "processorGatherEnabled", true);
            Scribe_Values.Look(ref processorUnpolluteEnabled, "processorUnpolluteEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Wasteland enabled", ref wastelandEnabled,
                "Master switch. Off: the biome and its defs still load (nothing here is "
              + "worldgen-affecting — RM_Wasteland ships generatesNaturally=false, placed only "
              + "by hand or by another mod/scenario), but every per-feature toggle below is "
              + "ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Brine deposit mining", ref brineDepositsEnabled,
                "Tekk/drazz/spent-electrode-plate deposits scatter into any generated map's "
              + "hypersaline brine water (RM_WastelandBrineShallow terrain). NOT YET WIRED — "
              + "the scatter is plain XML with no runtime gate, so this toggle is scaffolding "
              + "until a GenStep_ScatterThings subclass reads it.");
            list.GapLine();

            list.Label("Storms (ash storm, radiation halo, plasma storm). The weathers still occur "
                     + "when these are off; only their effects stop. Not worldgen-affecting.");
            list.CheckboxLabeled("Storm dose", ref stormDoseEnabled,
                "While a Wasteland storm runs, unroofed pawns build toxic buildup (the vanilla "
              + "toxic-fallout dose, scaled per storm). Only on maps whose biome opts in.");
            list.Label("Storm dose strength: " + stormDoseMultiplier.ToStringPercent());
            stormDoseMultiplier = list.Slider(stormDoseMultiplier, 0f, 3f);
            list.CheckboxLabeled("Ash fall pollutes the ground", ref ashFallPollutionEnabled,
                "Ash storms lay Biotech pollution on unroofed cells as they blow.");
            list.CheckboxLabeled("Cinderfelt germination", ref cinderfeltGerminationEnabled,
                "When an ash storm ends, cinderfelt grows on part of its fresh fall and dies "
              + "in about eight days. Off: cinderfelt appears only at its token wild weight.");
            list.GapLine();

            list.CheckboxLabeled("Ambient dose creatures", ref ambientDoseEnabled,
                "Smolderbacks (and the Middenshell, when built) dose nearby pawns, or their "
              + "whole room when indoors, with toxic buildup. Never an attack.");
            list.Label("Ambient dose strength: " + ambientDoseMultiplier.ToStringPercent());
            ambientDoseMultiplier = list.Slider(ambientDoseMultiplier, 0f, 3f);
            list.CheckboxLabeled("Radiothermal heat", ref radiothermalHeatEnabled,
                "Smolderbacks push heat like a small heater.");
            list.GapLine();

            list.CheckboxLabeled("Processor animals produce", ref processorGatherEnabled,
                "Tamed sloghogs grow bezoars and sootgrazers soot bricks, fastest on polluted "
              + "or ash-covered ground; collected by the milking job.");
            list.CheckboxLabeled("Processor animals clean pollution", ref processorUnpolluteEnabled,
                "Processor animals occasionally un-pollute the cell they stand on.");

            list.End();
        }
    }

    public class RM_WastelandMod : Mod
    {
        public static RM_WastelandSettings settings;

        public RM_WastelandMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WastelandSettings>();
        }

        public override string SettingsCategory()
        {
            return "Wasteland";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
