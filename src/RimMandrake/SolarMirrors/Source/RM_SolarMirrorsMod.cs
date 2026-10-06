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
            list.CheckboxLabeled("RM_SolarMirrors_Setting_Furnace".Translate(), ref solarFurnace,
                "RM_SolarMirrors_Setting_Furnace_Tip".Translate());

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
        }
    }

    public class RM_SolarMirrorsMod : Mod
    {
        public static RM_SolarMirrorsSettings settings;

        public RM_SolarMirrorsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SolarMirrorsSettings>();
            new Harmony("mandrake.rm.solarmirrors").PatchAll(typeof(RM_SolarMirrorsMod).Assembly);
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
            // A changed switch must show on the open map without waiting for a mirror event.
            if (Current.Game != null)
            {
                foreach (Map m in Find.Maps)
                {
                    RM_MapComponent_MirrorLight.For(m)?.RequestPass();
                }
            }
        }
    }

    [DefOf]
    public static class RM_SolarMirrorsDefOf
    {
        public static JobDef RM_ReAimMirror;

        static RM_SolarMirrorsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_SolarMirrorsDefOf));
        }
    }
}
