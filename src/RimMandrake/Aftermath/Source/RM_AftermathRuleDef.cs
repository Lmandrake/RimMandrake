using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.Ninefold;

namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §2.1's rule shape:
    // trigger -> delay -> telegraph -> payload. Data only (this class carries
    // no logic beyond ConfigErrors) - AftermathRuleRunner.cs is the engine
    // that reads these. Ships as XML in the RUT_AftermathRites companion mod.
    public class RM_AftermathRuleDef : Def
    {
        public AftermathTriggerKind triggerKind = AftermathTriggerKind.BattleOutcome;

        // --- BattleOutcome trigger fields (rules 1-3, WIRED) ----------------
        public List<BattleOutcome> triggerOutcomes;
        public int minSurvivors = 0;

        // --- Delay + telegraph -----------------------------------------------
        public float delayDaysMin = 0.5f;
        public float delayDaysMax = 2f;
        public string telegraphLabel;
        public string telegraphText; // {0} = faction label

        // --- Payload -----------------------------------------------------------
        public string payloadIncidentDefName;
        public AftermathPayloadFactionMode payloadFactionMode = AftermathPayloadFactionMode.SameAsTrigger;

        // --- God tie -------------------------------------------------------------
        public God? godTie;
        public float godDelta;

        // --- Baseline letter (fires when the PAYLOAD incident itself lands,
        // not the telegraph) - the "ships a templated letter baseline per
        // rule" requirement. {0} = faction label, {1} = this rule's label.
        public string letterLabel;
        public string letterText;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;

            if (triggerKind == AftermathTriggerKind.BattleOutcome &&
                (triggerOutcomes == null || triggerOutcomes.Count == 0))
                yield return "RM_AftermathRuleDef " + defName + ": triggerKind is BattleOutcome but triggerOutcomes is empty.";

            if (string.IsNullOrEmpty(payloadIncidentDefName))
                yield return "RM_AftermathRuleDef " + defName + ": payloadIncidentDefName is required.";

            if (delayDaysMax < delayDaysMin)
                yield return "RM_AftermathRuleDef " + defName + ": delayDaysMax < delayDaysMin.";
        }
    }
}
