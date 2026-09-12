using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Antiquities.
    //
    // Gates the two real runtime mechanics found in this mod's Source:
    //   1. WorkGiver_ExamineAntiquity offering the reading job at all
    //      (master on/off, degrades gracefully — pawns simply never pick
    //      the job up; nothing is destroyed, nothing NREs).
    //   2. JobDriver_ExamineAntiquity's read duration and "key text" bonus
    //      chance (design doc section 4.2's yield curve) — both were flat
    //      hardcoded numbers, now sliders with the shipped values as
    //      defaults.
    public class AntiquitiesSettings : ModSettings
    {
        public static bool readingEnabled = true;
        public static float durationMultiplier = 1f;
        public static bool keyTextBonusEnabled = true;
        public static float keyTextChanceScale = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref readingEnabled, "readingEnabled", true);
            Scribe_Values.Look(ref durationMultiplier, "durationMultiplier", 1f);
            Scribe_Values.Look(ref keyTextBonusEnabled, "keyTextBonusEnabled", true);
            Scribe_Values.Look(ref keyTextChanceScale, "keyTextChanceScale", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Antiquity reading enabled", ref readingEnabled,
                "Off: pawns never take the antiquity-reading job. Already-catalogued antiquities "
              + "and research progress already made are unaffected.");
            list.Gap();

            list.Label("Reading time: " + durationMultiplier.ToString("0.00") + "x");
            list.Label("Scales how long a pawn spends reading an antiquity at the station "
                     + "(the pawn's own Intellectual/Artistic skill still matters on top of this).");
            durationMultiplier = list.Slider(durationMultiplier, 0.5f, 2f);
            list.GapLine();

            list.CheckboxLabeled("\"Key text\" bonus reads", ref keyTextBonusEnabled,
                "Once the LANGUAGE stage is finished, a read has a chance to double its research "
              + "progress and print a special letter.");
            if (keyTextBonusEnabled)
            {
                list.Label("Key text chance: " + keyTextChanceScale.ToString("0.00") + "x the base rate");
                keyTextChanceScale = list.Slider(keyTextChanceScale, 0f, 2f);
            }

            list.End();
        }
    }

    public class AntiquitiesMod : Mod
    {
        public static AntiquitiesSettings settings;

        public AntiquitiesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<AntiquitiesSettings>();
        }

        public override string SettingsCategory() => "Antiquities";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
