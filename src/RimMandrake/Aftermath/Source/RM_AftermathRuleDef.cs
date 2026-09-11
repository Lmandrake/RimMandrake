using System.Collections.Generic;
using RimWorld;
using Verse;

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

        // --- PrisonerHeldDuration trigger field (rule 4, WIRED 2026-09-10) --
        // doc §2.1 row 4: "prisoners of faction F held >= 3 days, F hostile."
        // AftermathRuleRunner.PollPrisoners tracks per-prisoner elapsed days
        // in-memory (same documented not-scribed limitation as BattleRecord
        // and lastClosedByMap: a reload resets the clock, not the mechanism)
        // and AftermathRuleEligibility.IsEligiblePrisonerHeldDuration compares
        // it against this field.
        public float minHeldDays = 3f;

        // --- Delay + telegraph -----------------------------------------------
        public float delayDaysMin = 0.5f;
        public float delayDaysMax = 2f;
        public string telegraphLabel;
        public string telegraphText; // {0} = faction label

        // --- Payload -----------------------------------------------------------
        public string payloadIncidentDefName;
        public AftermathPayloadFactionMode payloadFactionMode = AftermathPayloadFactionMode.SameAsTrigger;

        // --- God tie -------------------------------------------------------------
        // CHRONICLE_NINEFOLD_DECOUPLE_1: a plain string, NOT Ninefold's God
        // enum. This engine has no compile-time knowledge of Ninefold (or of
        // any other consumer), so the god name travels as data on the
        // "chronicle.rule.queued" spine event and Ninefold's own subscriber
        // resolves it to God + calls ApplyDelta. An unresolvable name is
        // therefore Ninefold's warning to log, not a ConfigError here -- this
        // def cannot know which names are valid.
        //
        // The XML representation is UNCHANGED: <godTie>Shkaar</godTie> parsed
        // as an enum before and parses as a string now, so the eight rule
        // defs in mandrake.rut.aftermath needed no edit.
        public string godTie;
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

            if (triggerKind == AftermathTriggerKind.PrisonerHeldDuration && minHeldDays <= 0f)
                yield return "RM_AftermathRuleDef " + defName + ": triggerKind is PrisonerHeldDuration but minHeldDays <= 0.";
        }
    }
}
