// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the restraining-bolt goodwill cap.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
//
// The one mechanism here (GoodwillSituationWorker_RestrainingBolts) computes
// maxGoodwill = 100 - penaltyPerBoltedDroid * N, floored at goodwillFloor. Both
// numbers were hardcoded (2.5 and -70); both are exposed below, plus a master
// off switch that returns the vanilla 100 ceiling unconditionally.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RestrainingBolts
{
    public class RestrainingBoltsSettings : ModSettings
    {
        public static bool enabled = true;
        public static float penaltyPerBoltedDroid = 2.5f;
        public static float goodwillFloor = -70f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref penaltyPerBoltedDroid, "penaltyPerBoltedDroid", 2.5f);
            Scribe_Values.Look(ref goodwillFloor, "goodwillFloor", -70f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Cap Free Droid Enclaves goodwill by bolted droids", ref enabled,
                "Off: your goodwill ceiling with the Free Droid Enclaves is always 100, "
              + "same as any other faction. Requires Droid Depot to do anything either way.");
            list.Gap();

            list.Label("Goodwill penalty per bolted droid: " + penaltyPerBoltedDroid.ToString("0.0"));
            list.Label("Every droid you own carrying a restraining bolt right now lowers your "
              + "possible goodwill ceiling with the Enclaves by this much.");
            penaltyPerBoltedDroid = list.Slider(penaltyPerBoltedDroid, 0f, 10f);
            list.Gap();

            list.Label("Goodwill floor: " + goodwillFloor.ToString("0"));
            list.Label("The ceiling never drops below this, however many droids you bolt "
              + "(kept above the -75 hostility line by default, leaving margin).");
            goodwillFloor = list.Slider(goodwillFloor, -100f, 0f);

            list.End();
        }
    }

    public class RestrainingBoltsMod : Mod
    {
        public static RestrainingBoltsSettings settings;

        public RestrainingBoltsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RestrainingBoltsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Restraining Bolts";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
