/* Ported from Ruthless Faction Pursuit (workshop 3621784437) by Matathias, GPLv3.
 * See ../../LICENSE.txt and About.xml for the fork's credit and scope.
 * MODIFIED 2026-10-06 (EMPIRE_ESCALATION_LADDER_1): the escalation ladder's settings,
 * design doc §6. All on = the ladder as designed; ladder off = upstream's flat pursuit. */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Verse;

namespace RuthlessPursuingMechanoids
{
    public class RFPSettings : ModSettings
    {
        public static bool printDebug = false;

        /* EMPIRE_ESCALATION_LADDER_1 — defaults are the shipped behaviour (PROVISIONAL numbers). */
        public static bool ladderEnabled = true;
        public static bool probesOpen = true;
        public static float ladderPace = 1f;
        public static bool visibilityDrivesPace = true;
        public static bool rememberRungs = true;
        public static int rungDecayPerSeason = 1;
        public static bool cordonEnabled = true;
        public static float ionLockoutHours = 6f;
        public static float ionVolleyIntervalHours = 8f;
        public static bool bombardmentEnabled = true;
        public static bool endlessAfterTop = true;
        public static bool showSearchAlert = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref printDebug, "printDebug", false, true);
            Scribe_Values.Look(ref ladderEnabled, "ladderEnabled", true, true);
            Scribe_Values.Look(ref probesOpen, "probesOpen", true, true);
            Scribe_Values.Look(ref ladderPace, "ladderPace", 1f, true);
            Scribe_Values.Look(ref visibilityDrivesPace, "visibilityDrivesPace", true, true);
            Scribe_Values.Look(ref rememberRungs, "rememberRungs", true, true);
            Scribe_Values.Look(ref rungDecayPerSeason, "rungDecayPerSeason", 1, true);
            Scribe_Values.Look(ref cordonEnabled, "cordonEnabled", true, true);
            Scribe_Values.Look(ref ionLockoutHours, "ionLockoutHours", 6f, true);
            Scribe_Values.Look(ref ionVolleyIntervalHours, "ionVolleyIntervalHours", 8f, true);
            Scribe_Values.Look(ref bombardmentEnabled, "bombardmentEnabled", true, true);
            Scribe_Values.Look(ref endlessAfterTop, "endlessAfterTop", true, true);
            Scribe_Values.Look(ref showSearchAlert, "showSearchAlert", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            var list = new Listing_Standard()
            {
                ColumnWidth = inRect.width
            };
            list.Begin(inRect);

            list.CheckboxLabeled("printDebug".Translate(), ref printDebug);
            list.GapLine();
            list.Label("RUT_Ladder_Header".Translate());
            list.CheckboxLabeled("RUT_Ladder_Enabled".Translate(), ref ladderEnabled, "RUT_Ladder_EnabledDesc".Translate());
            if (ladderEnabled)
            {
                list.CheckboxLabeled("RUT_Ladder_ProbesOpen".Translate(), ref probesOpen, "RUT_Ladder_ProbesOpenDesc".Translate());
                list.Label("RUT_Ladder_Pace".Translate(ladderPace.ToString("0.00")));
                ladderPace = list.Slider(ladderPace, 0.25f, 4f);
                list.CheckboxLabeled("RUT_Ladder_VisibilityPace".Translate(), ref visibilityDrivesPace, "RUT_Ladder_VisibilityPaceDesc".Translate());
                list.CheckboxLabeled("RUT_Ladder_Remember".Translate(), ref rememberRungs, "RUT_Ladder_RememberDesc".Translate());
                if (rememberRungs)
                {
                    list.Label("RUT_Ladder_Decay".Translate(rungDecayPerSeason));
                    rungDecayPerSeason = Mathf.RoundToInt(list.Slider(rungDecayPerSeason, 0f, 3f));
                }
                list.CheckboxLabeled("RUT_Ladder_Cordon".Translate(), ref cordonEnabled, "RUT_Ladder_CordonDesc".Translate());
                if (cordonEnabled)
                {
                    list.Label("RUT_Ladder_IonLockout".Translate(ionLockoutHours.ToString("0")));
                    ionLockoutHours = Mathf.Round(list.Slider(ionLockoutHours, 1f, 23f));
                }
                list.CheckboxLabeled("RUT_Ladder_Bombardment".Translate(), ref bombardmentEnabled, "RUT_Ladder_BombardmentDesc".Translate());
                list.CheckboxLabeled("RUT_Ladder_Endless".Translate(), ref endlessAfterTop);
                list.CheckboxLabeled("RUT_Ladder_Alert".Translate(), ref showSearchAlert);
            }

            list.End();
        }

    }
    public class RFPMod : Mod
    {
        public static RFPSettings settings = new RFPSettings();

        public RFPMod(ModContentPack content) : base(content)
        {
            Pack = content;
            settings = GetSettings<RFPSettings>();
        }

        public ModContentPack Pack { get; }

        public override string SettingsCategory() => Pack.Name;

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }
}
