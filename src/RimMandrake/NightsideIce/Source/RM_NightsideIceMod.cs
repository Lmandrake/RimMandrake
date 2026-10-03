using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.NightsideIce
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Nightside Ice.
    //
    // Precedent: src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs.
    //
    // Master switch plus the heat dial (NIGHTSIDEICE_HEAT_DIAL_1, RM_HeatDial.cs). The breach
    // cracks and the shivven that read the dial are filed, unbuilt, and get settings when they land.
    // ════════════════════════════════════════════════════════════════════
    public class RM_NightsideIceSettings : ModSettings
    {
        /// <summary>Master switch. Off: the def still loads; no mechanic of this mod runs.</summary>
        public static bool masterEnabled = true;

        // NIGHTSIDEICE_HEAT_DIAL_1 -- the heat dial (RM_HeatDial.cs)
        public static bool heatDialEnabled = true;            // measure the colony's heat on the Sleeping Ice
        public static float heatDialScale = 150f;             // raw heat at which the dial reads about 63%
        public static bool heatDialAlert = true;              // show the thermal-signature alert
        public static float heatDialAlertThreshold = 0.2f;    // dial at which the alert appears

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref heatDialEnabled, "heatDialEnabled", true);
            Scribe_Values.Look(ref heatDialScale, "heatDialScale", 150f);
            Scribe_Values.Look(ref heatDialAlert, "heatDialAlert", true);
            Scribe_Values.Look(ref heatDialAlertThreshold, "heatDialAlertThreshold", 0.2f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Nightside Ice");
            list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                "Off: RM_NightsideIce still loads and can be assigned to a tile directly, but none of its "
              + "mechanics run.");
            list.GapLine();
            list.Label("The heat dial");
            list.CheckboxLabeled("Measure the colony's heat on the ice", ref heatDialEnabled,
                "One continuous dial of how warm the colony is against the ice: working heaters, fires, power "
              + "drawn and heated rooms. Everything in the ice that hunts by heat reads it. Off: it reads zero.");
            if (heatDialEnabled)
            {
                list.Label("Sensitivity: the dial reads about 63% at " + heatDialScale.ToString("0") + " heat "
                    + "(a heater is about 21, a 1000 W draw about 10)");
                heatDialScale = list.Slider(heatDialScale, 25f, 600f);
                list.CheckboxLabeled("Show the thermal-signature alert", ref heatDialAlert);
                if (heatDialAlert)
                {
                    list.Label("Alert from " + Mathf.RoundToInt(heatDialAlertThreshold * 100f) + "%");
                    heatDialAlertThreshold = list.Slider(heatDialAlertThreshold, 0f, 1f);
                }
            }
            list.GapLine();
            list.Label("Not built yet, so no settings: the breach cracks and the shivven that answer the dial.");

            list.End();
        }
    }

    public class RM_NightsideIceMod : Mod
    {
        public static RM_NightsideIceSettings settings;

        public RM_NightsideIceMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_NightsideIceSettings>();
        }

        public override string SettingsCategory()
        {
            return "Nightside Ice";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
