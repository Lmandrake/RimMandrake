using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §3.5. Defaults = shipped behaviour; every effect off
    // leaves inert decorative buildings. Numbers marked PROVISIONAL are first guesses,
    // to be tuned in a live sitting.
    public class RM_SolarMirrorsSettings : ModSettings
    {
        public static bool shadeEffect = true;          // mirror light takes shade off (heat, sun pathing, herds)
        public static bool glowEffect = true;           // mirror light raises ground glow (plants, work in the dim)
        public static int beamRender = 2;               // 0 off, 1 spot only, 2 spot + beam
        public static bool staticSweep = true;          // static mirrors drift with a moving sun
        public static bool blindingDefence = true;      // hostiles in a beam go glare-blind
        public static float blindSeverityPerDay = 6f;   // PROVISIONAL; RM_GlareBlind's own recovery is -2/day
        public static bool solarFurnace = true;         // furnace works only under concentrated light
        public static float reflectivityMultiplier = 1f; // PROVISIONAL range 0.25-1.5
        public static float reAimWorkMultiplier = 1f;   // PROVISIONAL range 0.25-3
        public static int passIntervalTicks = 250;      // design §2.7; range 125-1000
        public static int maxChain = 4;                 // design §2.2 depth cap; range 1-6
        // SOLAR_MIRRORS_BUILD_1 (design §3.4, §3.2, §2.6, §5 E2/E3/E4). Every number is PROVISIONAL.
        public static bool ancientFields = true;        // affects map generation: the Long Shade's ancient mirror field
        public static int puzzleMinReAims = 3;          // design §3.4 difficulty: 2 / 3 / 4
        public static int puzzleMirrors = 5;            // design §3.4: 4 / 5 / 6 ancient mirrors (§3.5's "4/5/6", read as the field's size)
        public static bool dustEnabled = true;          // dust storms dirty mirrors until cleaned
        public static float dustPerDay = 1f;            // dust gained per day of storm; range 0.1-5
        public static float heliostatPower = 150f;      // W while tracking; range 50-500
        public static bool concentrationHeat = true;    // light above 1 adds vanilla felt heat (capped by the biome)
        public static float concentrationCap = 3f;      // light above this adds nothing more; range 1-5
        public static bool roomHeat = true;             // mirror light inside an enclosed room warms it
        public static float roomHeatPerLight = 2f;      // heat per unit of light per lit cell per second; range 0-10
        public static bool heliograph = true;           // signal mirrors flash friendly settlements by day
        public static float heliographRange = 12f;      // world tiles at full daylight; range 2-40
        public static bool dazzle = true;               // hostiles in a beam shoot worse
        public static float dazzleMaxPenalty = 0.4f;    // accuracy lost in full light; range 0-0.9

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shadeEffect, "shadeEffect", true);
            Scribe_Values.Look(ref glowEffect, "glowEffect", true);
            Scribe_Values.Look(ref beamRender, "beamRender", 2);
            Scribe_Values.Look(ref staticSweep, "staticSweep", true);
            Scribe_Values.Look(ref blindingDefence, "blindingDefence", true);
            Scribe_Values.Look(ref blindSeverityPerDay, "blindSeverityPerDay", 6f);
            Scribe_Values.Look(ref solarFurnace, "solarFurnace", true);
            Scribe_Values.Look(ref reflectivityMultiplier, "reflectivityMultiplier", 1f);
            Scribe_Values.Look(ref reAimWorkMultiplier, "reAimWorkMultiplier", 1f);
            Scribe_Values.Look(ref passIntervalTicks, "passIntervalTicks", 250);
            Scribe_Values.Look(ref maxChain, "maxChain", 4);
            Scribe_Values.Look(ref ancientFields, "ancientFields", true);
            Scribe_Values.Look(ref puzzleMinReAims, "puzzleMinReAims", 3);
            Scribe_Values.Look(ref puzzleMirrors, "puzzleMirrors", 5);
            Scribe_Values.Look(ref dustEnabled, "dustEnabled", true);
            Scribe_Values.Look(ref dustPerDay, "dustPerDay", 1f);
            Scribe_Values.Look(ref heliostatPower, "heliostatPower", 150f);
            Scribe_Values.Look(ref concentrationHeat, "concentrationHeat", true);
            Scribe_Values.Look(ref concentrationCap, "concentrationCap", 3f);
            Scribe_Values.Look(ref roomHeat, "roomHeat", true);
            Scribe_Values.Look(ref roomHeatPerLight, "roomHeatPerLight", 2f);
            Scribe_Values.Look(ref heliograph, "heliograph", true);
            Scribe_Values.Look(ref heliographRange, "heliographRange", 12f);
            Scribe_Values.Look(ref dazzle, "dazzle", true);
            Scribe_Values.Look(ref dazzleMaxPenalty, "dazzleMaxPenalty", 0.4f);
        }

        private static Vector2 scrollPosition;
        private static float lastContentHeight;

        public void DoWindowContents(Rect inRect)
        {
            // Scroll view + maxOneColumn, per the Webwork fix (cfdba9344): without maxOneColumn the
            // first frame's overflow wraps into a hidden second column and the view never grows.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(lastContentHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);

            list.Label("RM_SolarMirrors_Section_Light".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Shade".Translate(), ref shadeEffect,
                "RM_SolarMirrors_Setting_Shade_Tip".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Glow".Translate(), ref glowEffect,
                "RM_SolarMirrors_Setting_Glow_Tip".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Sweep".Translate(), ref staticSweep,
                "RM_SolarMirrors_Setting_Sweep_Tip".Translate());
            list.Label("RM_SolarMirrors_Setting_Reflectivity".Translate(reflectivityMultiplier.ToStringPercent()),
                tooltip: "RM_SolarMirrors_Setting_Reflectivity_Tip".Translate());
            reflectivityMultiplier = Mathf.Round(list.Slider(reflectivityMultiplier, 0.25f, 1.5f) * 20f) / 20f;
            list.Label("RM_SolarMirrors_Setting_Chain".Translate(maxChain),
                tooltip: "RM_SolarMirrors_Setting_Chain_Tip".Translate());
            maxChain = Mathf.RoundToInt(list.Slider(maxChain, 1f, 6f));

            list.GapLine();
            list.Label("RM_SolarMirrors_Section_Look".Translate());
            string[] modes = { "RM_SolarMirrors_Render_Off", "RM_SolarMirrors_Render_Spot", "RM_SolarMirrors_Render_Beam" };
            list.Label("RM_SolarMirrors_Setting_Render".Translate(modes[Mathf.Clamp(beamRender, 0, 2)].Translate()),
                tooltip: "RM_SolarMirrors_Setting_Render_Tip".Translate());
            beamRender = Mathf.RoundToInt(list.Slider(beamRender, 0f, 2f));

            list.GapLine();
            list.Label("RM_SolarMirrors_Section_Uses".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Blind".Translate(), ref blindingDefence,
                "RM_SolarMirrors_Setting_Blind_Tip".Translate());
            if (blindingDefence)
            {
                list.Label("RM_SolarMirrors_Setting_BlindRate".Translate(blindSeverityPerDay.ToString("0.0")));
                blindSeverityPerDay = Mathf.Round(list.Slider(blindSeverityPerDay, 1f, 20f) * 2f) / 2f;
            }
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Dazzle".Translate(), ref dazzle,
                "RM_SolarMirrors_Setting_Dazzle_Tip".Translate());
            if (dazzle)
            {
                list.Label("RM_SolarMirrors_Setting_DazzleMax".Translate(dazzleMaxPenalty.ToStringPercent()));
                dazzleMaxPenalty = Mathf.Round(list.Slider(dazzleMaxPenalty, 0f, 0.9f) * 20f) / 20f;
            }
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Furnace".Translate(), ref solarFurnace,
                "RM_SolarMirrors_Setting_Furnace_Tip".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Concentration".Translate(), ref concentrationHeat,
                "RM_SolarMirrors_Setting_Concentration_Tip".Translate());
            if (concentrationHeat)
            {
                list.Label("RM_SolarMirrors_Setting_ConcentrationCap".Translate(concentrationCap.ToString("0.0")));
                concentrationCap = Mathf.Round(list.Slider(concentrationCap, 1f, 5f) * 4f) / 4f;
            }
            list.CheckboxLabeled("RM_SolarMirrors_Setting_RoomHeat".Translate(), ref roomHeat,
                "RM_SolarMirrors_Setting_RoomHeat_Tip".Translate());
            if (roomHeat)
            {
                list.Label("RM_SolarMirrors_Setting_RoomHeatRate".Translate(roomHeatPerLight.ToString("0.0")));
                roomHeatPerLight = Mathf.Round(list.Slider(roomHeatPerLight, 0f, 10f) * 4f) / 4f;
            }
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Helio".Translate(), ref heliograph,
                "RM_SolarMirrors_Setting_Helio_Tip".Translate());
            if (heliograph)
            {
                list.Label("RM_SolarMirrors_Setting_HelioRange".Translate(heliographRange.ToString("0")));
                heliographRange = Mathf.Round(list.Slider(heliographRange, 2f, 40f));
            }

            list.GapLine();
            list.Label("RM_SolarMirrors_Section_Field".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Fields".Translate(), ref ancientFields,
                "RM_SolarMirrors_Setting_Fields_Tip".Translate());
            if (ancientFields)
            {
                list.Label("RM_SolarMirrors_Setting_PuzzleReAims".Translate(puzzleMinReAims),
                    tooltip: "RM_SolarMirrors_Setting_PuzzleReAims_Tip".Translate());
                puzzleMinReAims = Mathf.RoundToInt(list.Slider(puzzleMinReAims, 2f, 4f));
                list.Label("RM_SolarMirrors_Setting_PuzzleMirrors".Translate(puzzleMirrors),
                    tooltip: "RM_SolarMirrors_Setting_PuzzleMirrors_Tip".Translate());
                puzzleMirrors = Mathf.RoundToInt(list.Slider(puzzleMirrors, 4f, 6f));
            }

            list.GapLine();
            list.Label("RM_SolarMirrors_Section_Care".Translate());
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Dust".Translate(), ref dustEnabled,
                "RM_SolarMirrors_Setting_Dust_Tip".Translate());
            if (dustEnabled)
            {
                list.Label("RM_SolarMirrors_Setting_DustRate".Translate(dustPerDay.ToString("0.0")));
                dustPerDay = Mathf.Round(list.Slider(dustPerDay, 0.1f, 5f) * 10f) / 10f;
            }
            list.Label("RM_SolarMirrors_Setting_Power".Translate(heliostatPower.ToString("0")),
                tooltip: "RM_SolarMirrors_Setting_Power_Tip".Translate());
            heliostatPower = Mathf.Round(list.Slider(heliostatPower, 50f, 500f) / 10f) * 10f;

            list.GapLine();
            list.Label("RM_SolarMirrors_Section_Work".Translate());
            list.Label("RM_SolarMirrors_Setting_ReAim".Translate(reAimWorkMultiplier.ToStringPercent()));
            reAimWorkMultiplier = Mathf.Round(list.Slider(reAimWorkMultiplier, 0.25f, 3f) * 20f) / 20f;
            list.Label("RM_SolarMirrors_Setting_Interval".Translate(passIntervalTicks),
                tooltip: "RM_SolarMirrors_Setting_Interval_Tip".Translate());
            passIntervalTicks = Mathf.RoundToInt(list.Slider(passIntervalTicks, 125f, 1000f) / 25f) * 25;

            list.Gap();
            if (list.ButtonText("RM_SolarMirrors_Setting_Reset".Translate()))
            {
                ResetToDefaults();
            }
            if (list.ButtonText("RM_SolarMirrors_Setting_AllOff".Translate()))
            {
                AllOff();
            }

            lastContentHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        public static void ResetToDefaults()
        {
            shadeEffect = true;
            glowEffect = true;
            beamRender = 2;
            staticSweep = true;
            blindingDefence = true;
            blindSeverityPerDay = 6f;
            solarFurnace = true;
            reflectivityMultiplier = 1f;
            reAimWorkMultiplier = 1f;
            passIntervalTicks = 250;
            maxChain = 4;
            ancientFields = true;
            puzzleMinReAims = 3;
            puzzleMirrors = 5;
            dustEnabled = true;
            dustPerDay = 1f;
            heliostatPower = 150f;
            concentrationHeat = true;
            concentrationCap = 3f;
            roomHeat = true;
            roomHeatPerLight = 2f;
            heliograph = true;
            heliographRange = 12f;
            dazzle = true;
            dazzleMaxPenalty = 0.4f;
        }

        /// <summary>Every effect off: mirrors are inert decorative buildings (design §3.5). Used by the settings
        /// screen's "all off" button and pinned by validation.py.</summary>
        public static void AllOff()
        {
            shadeEffect = false;
            glowEffect = false;
            beamRender = 0;
            blindingDefence = false;
            solarFurnace = false;
            ancientFields = false;
            dustEnabled = false;
            concentrationHeat = false;
            roomHeat = false;
            heliograph = false;
            dazzle = false;
        }
    }

    public class RM_SolarMirrorsMod : Mod
    {
        public static RM_SolarMirrorsSettings settings;

        public RM_SolarMirrorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SolarMirrorsSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.solarmirrors"), typeof(RM_SolarMirrorsMod).Assembly, "RimMandrake.SolarMirrors");
        }

        public override string SettingsCategory()
        {
            return "RM_SolarMirrors_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_SolarMirrorsStartup.ApplyHeliostatPower();
            // A changed switch must show on the open map without waiting for a mirror event.
            if (Current.Game != null)
            {
                foreach (Map m in Find.Maps)
                {
                    RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(m);
                    // shadeEffect is read by the grid through AddLight, not by the change hash.
                    comp?.RequestPass();
                    comp?.RequestGridRebuild();
                }
            }
        }
    }

    [DefOf]
    public static class RM_SolarMirrorsDefOf
    {
        public static JobDef RM_ReAimMirror;
        public static JobDef RM_CleanMirror;
        public static JobDef RM_RepairAncientMirror;
        public static JobDef RM_FlashHeliograph;

        static RM_SolarMirrorsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_SolarMirrorsDefOf));
        }
    }
}
