using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.DroidRepairJobs
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Droid Repair Jobs.
    //
    // Gates QuestNode_DroidRepairJob.WritePaymentVars, the only place this
    // mod computes a number: the base repair-job payment (customer's XML
    // slate value, 320 silver fallback) scaled by the faction's wealth
    // (tech level) and reputation (goodwill) factors. Both scaling factors
    // are exposed as one on/off (the "guardrail" DROID_UNIFIED_FRAMEWORK_
    // DESIGN.md section 6 names), plus a flat multiplier on top of
    // everything, default 1x = shipped behavior.
    public class DroidRepairJobsSettings : ModSettings
    {
        public static float paymentMultiplier = 1f;
        public static bool wealthAndReputationScaling = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref paymentMultiplier, "paymentMultiplier", 1f);
            Scribe_Values.Look(ref wealthAndReputationScaling, "wealthAndReputationScaling", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Droid repair-job payment: " + paymentMultiplier.ToString("0.00") + "x");
            list.Label("Scales what a repair-job customer pays out, at every quality tier "
                     + "(neglected/shoddy/honest/fine).");
            paymentMultiplier = list.Slider(paymentMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Customer wealth and reputation affect payment", ref wealthAndReputationScaling,
                "Off: every repair job pays the flat base amount (times the slider above), regardless of "
              + "the customer faction's tech level or how much goodwill you have with them.");

            list.End();
        }
    }

    public class DroidRepairJobsMod : Mod
    {
        public static DroidRepairJobsSettings settings;

        public DroidRepairJobsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<DroidRepairJobsSettings>();
        }

        public override string SettingsCategory() => "Droid Repair Jobs";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
