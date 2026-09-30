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
    // processor animals (RM_CompProcessorGatherable), and the gripper's theft
    // (RM_GripperTheft.cs, WASTELAND_GRIPPER_STEAL_BEHAVIOR_1). Each of those
    // reads its toggle below at runtime.
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

        // WASTELAND_GRIPPER_STEAL_BEHAVIOR_1 — wild grippers steal (RM_GripperTheft.cs).
        public static bool gripperTheftEnabled = true;
        public static bool gripperSpawnsCarrying = true;
        public static float gripperTheftMtbHours = 3f;

        // WASTELAND_MIDDENSHELL_FOOTPRINT_1 — the 20-wide giant (RM_Middenshell.cs).
        public static bool middenshellEnabled = true;
        public static bool middenshellGrabEnabled = true;
        public static int middenshellStepTicks = 400;

        // WASTELAND_GPT_ENRICHMENT_1 §1 — named storms (RM_NamedStorms.cs).
        public static bool namedStormPhasesEnabled = true;
        public static float namedStormWarningFactor = 1f;
        public static bool cinderwireEmpEnabled = true;

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
            Scribe_Values.Look(ref gripperTheftEnabled, "gripperTheftEnabled", true);
            Scribe_Values.Look(ref gripperSpawnsCarrying, "gripperSpawnsCarrying", true);
            Scribe_Values.Look(ref gripperTheftMtbHours, "gripperTheftMtbHours", 3f);
            Scribe_Values.Look(ref middenshellEnabled, "middenshellEnabled", true);
            Scribe_Values.Look(ref middenshellGrabEnabled, "middenshellGrabEnabled", true);
            Scribe_Values.Look(ref middenshellStepTicks, "middenshellStepTicks", 400);
            Scribe_Values.Look(ref namedStormPhasesEnabled, "namedStormPhasesEnabled", true);
            Scribe_Values.Look(ref namedStormWarningFactor, "namedStormWarningFactor", 1f);
            Scribe_Values.Look(ref cinderwireEmpEnabled, "cinderwireEmpEnabled", true);
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

            list.Label("Storms (ash storm, deadlight halo, cinderwire storm). The weathers still occur "
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
            list.CheckboxLabeled("Named storm warnings", ref namedStormPhasesEnabled,
                "The deadlight halo and the cinderwire storm arrive with a quiet warning (doubled "
              + "shadows, quickening dosimeter clicks, a sickly rim-light; crawling static, "
              + "levitating scraps and a rising whine) before their dose, fall, EMP and lightning "
              + "begin. Off: they strike at once and the cues are skipped.");
            list.Label("Storm warning length: " + namedStormWarningFactor.ToStringPercent()
                     + " (100% = about one in-game hour)");
            namedStormWarningFactor = list.Slider(namedStormWarningFactor, 0.25f, 3f);
            list.CheckboxLabeled("Cinderwire EMP pulses", ref cinderwireEmpEnabled,
                "Once a cinderwire storm breaks, EMP pulses strike random open ground, stunning "
              + "powered buildings and mechanoids caught in them.");
            list.GapLine();

            list.CheckboxLabeled("Ambient dose creatures", ref ambientDoseEnabled,
                "Smolderbacks and the Middenshell (and its mined-out carcass) dose nearby pawns, or their "
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
            list.GapLine();

            list.CheckboxLabeled("Grippers steal", ref gripperTheftEnabled,
                "Wild grippers pick up small unforbidden items they can reach, swapping "
              + "whatever scrap they hold for anything worth more, and scurry off with it. "
              + "A hurt gripper may drop its haul; a dead one always does. Tamed grippers "
              + "never steal. Off: grippers are ordinary beetles and carry nothing new.");
            list.CheckboxLabeled("Grippers spawn carrying scrap", ref gripperSpawnsCarrying,
                "A newly arrived wild gripper already holds a scrap of junk (steel, silver, "
              + "cloth, a component).");
            list.Label("Gripper theft attempts: about every "
                     + gripperTheftMtbHours.ToString("0.#") + " hours per idle gripper");
            gripperTheftMtbHours = list.Slider(gripperTheftMtbHours, 0.5f, 24f);
            list.GapLine();

            list.CheckboxLabeled("The Middenshell", ref middenshellEnabled,
                "The twenty-cell-wide giant crawls in from a map edge on Wasteland maps (one at "
              + "most per map), flattening what lies in its path. Never hostile; being near it "
              + "doses you. Off: it never arrives, and one already on a map lies still.");
            list.CheckboxLabeled("Middenshell tentacle grabs", ref middenshellGrabEnabled,
                "Now and then it lashes a tentacle at a nearby object (items, doors, walls) and "
              + "eats it. Never anything on gravship substructure or any gravship part.");
            list.Label("Middenshell crawl: one cell every " + middenshellStepTicks + " ticks");
            middenshellStepTicks = (int)list.Slider(middenshellStepTicks, 120f, 2000f);

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
