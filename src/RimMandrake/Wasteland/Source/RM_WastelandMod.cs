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

        // WASTELAND_GPT_ENRICHMENT_1 §2 — the Middenshell Procession (RM_MiddenshellProcession.cs).
        public static bool middenshellProcessionEnabled = true;
        public static int middenshellOmenHours = 4;
        public static bool middenshellTrailEnabled = true;
        public static bool middenshellLureEnabled = true;
        public static float middenshellLureRange = 60f;

        // WASTELAND_GPT_ENRICHMENT_1 §3 — the sealed cask bay and waste casks (RM_WasteCaskBay.cs).
        public static bool caskLeaksEnabled = true;
        public static float caskLeakSeverity = 1f;
        public static int caskBayPerCell = 2;
        public static bool caskProcessingEnabled = true;
        public static float caskProcessingPerDay = 0.5f;
        public static bool caskLaunchCheckEnabled = true;
        public static bool caskReburialEnabled = true;

        // WASTELAND_GPT_ENRICHMENT_1 §4 — the Rite of Tipping (RM_RiteOfTipping.cs).
        public static bool tippingEnabled = true;

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
            Scribe_Values.Look(ref middenshellProcessionEnabled, "middenshellProcessionEnabled", true);
            Scribe_Values.Look(ref middenshellOmenHours, "middenshellOmenHours", 4);
            Scribe_Values.Look(ref middenshellTrailEnabled, "middenshellTrailEnabled", true);
            Scribe_Values.Look(ref middenshellLureEnabled, "middenshellLureEnabled", true);
            Scribe_Values.Look(ref middenshellLureRange, "middenshellLureRange", 60f);
            Scribe_Values.Look(ref caskLeaksEnabled, "caskLeaksEnabled", true);
            Scribe_Values.Look(ref caskLeakSeverity, "caskLeakSeverity", 1f);
            Scribe_Values.Look(ref caskBayPerCell, "caskBayPerCell", 2);
            Scribe_Values.Look(ref caskProcessingEnabled, "caskProcessingEnabled", true);
            Scribe_Values.Look(ref caskProcessingPerDay, "caskProcessingPerDay", 0.5f);
            Scribe_Values.Look(ref caskLaunchCheckEnabled, "caskLaunchCheckEnabled", true);
            Scribe_Values.Look(ref caskReburialEnabled, "caskReburialEnabled", true);
            Scribe_Values.Look(ref tippingEnabled, "tippingEnabled", true);
        }

        private static Vector2 scroll;
        private static float viewHeight = 1400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

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
            list.CheckboxLabeled("Middenshell procession", ref middenshellProcessionEnabled,
                "It announces itself hours ahead (the crust trembles, loose metal creeps toward the "
              + "edge it will come from), then crosses the map on a straight, readable line and "
              + "leaves by the far edge. Off: it arrives unannounced and wanders until killed.");
            list.Label("Procession warning: " + middenshellOmenHours + " hours before it arrives");
            middenshellOmenHours = (int)list.Slider(middenshellOmenHours, 1f, 12f);
            list.CheckboxLabeled("Middenshell trail", ref middenshellTrailEnabled,
                "It presses a trail of crushed ground behind it and drops hot footprints, shell "
              + "flakes and the odd small bezoar; where it leaves the map it tears an edge scar. "
              + "The trail and scar are permanent terrain.");
            list.CheckboxLabeled("Waste stockpiles divert it", ref middenshellLureEnabled,
                "A stockpile holding toxic wastepacks or waste casks within range draws it off its "
              + "line until the waste is eaten.");
            list.Label("Waste lure range: " + middenshellLureRange.ToString("0") + " cells");
            middenshellLureRange = list.Slider(middenshellLureRange, 10f, 150f);
            list.GapLine();

            list.Label("Waste casks and the sealed cask bay (not the warcasket bay).");
            list.CheckboxLabeled("Breached casks leak", ref caskLeaksEnabled,
                "A waste cask below half its hit points, or a sealed cask bay whose seals fail, leaks tox gas "
              + "and pollution — always with a message and an alert. Off: casks are inert.");
            list.Label("Leak severity: " + caskLeakSeverity.ToStringPercent());
            caskLeakSeverity = list.Slider(caskLeakSeverity, 0.25f, 3f);
            list.Label("Sealed cask bay capacity: " + caskBayPerCell + " casks per cell ("
                     + (caskBayPerCell * 6) + " per bay)");
            caskBayPerCell = (int)list.Slider(caskBayPerCell, 1f, 6f);
            list.CheckboxLabeled("Processor animals convert casks", ref caskProcessingEnabled,
                "With processing switched on at a bay, a tamed sloghog or sootgrazer standing next to it "
              + "converts stored casks into bezoars or soot bricks.");
            list.Label("Processing rate: " + caskProcessingPerDay.ToString("0.##") + " casks per day");
            caskProcessingPerDay = list.Slider(caskProcessingPerDay, 0.1f, 3f);
            list.CheckboxLabeled("Waste blocks unsafe gravship launches", ref caskLaunchCheckEnabled,
                "A gravship will not launch while a sealed cask bay aboard is unpowered, damaged or hot, "
              + "or while a waste cask sits loose on its deck.");
            list.CheckboxLabeled("Illegal reburial", ref caskReburialEnabled,
                "Casks can be marked to be dug back into the ground: gone from the map, but the ground is "
              + "fouled and the burial may be discovered.");
            list.GapLine();

            list.CheckboxLabeled("Rite of Tipping", ref tippingEnabled,
                "On Wasteland maps a supervised waste convoy may offer silver and goodwill to tip waste "
              + "casks on a licensed tipping pad; another faction may ask for evidence, and a third may "
              + "finance proper containment. Off: the offer never comes.");

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
            RM_WasteCaskBayUtility.ApplyCapacity();
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
