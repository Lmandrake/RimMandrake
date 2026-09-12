using System.Collections.Generic;
using RimWorld;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.DroidRepairJobs
{
    /// <summary>
    /// DROID_REPAIR_FOR_PROFIT_EVENTS_1 (packet C5). The one custom verb this
    /// quest needs, and nothing else - everything a stock node can already do
    /// (arrival, timer, letters, drop pods, goodwill, end) stays in XML, per
    /// skills/rimworld-quests/SKILL.md section 9's hybrid shape.
    ///
    /// It does two jobs, both at GENERATION time in RunInt(), plus one QuestPart
    /// that ticks:
    ///   1. Breaks the customer's droid (adds <faultHediff>) so it visibly
    ///      arrives needing work.
    ///   2. Computes the three outcome-scaled payments and writes them to the
    ///      slate as payFine / payHonest / payShoddy, so the quest description
    ///      can quote them and QuestPart_DroidRepairJobOutcome can pay them.
    ///   3. Emits QuestPart_DroidRepairJobOutcome, which at <inSignal> reads
    ///      which quality of part the player actually fitted and fires one of
    ///      four out-signals.
    ///
    /// ANTI-EXPONENTIAL GUARDRAIL (DROID_UNIFIED_FRAMEWORK_DESIGN.md section 6,
    /// "repair-for-profit events | silver printer"): payment scales with the
    /// customer faction's tech level and its goodwill toward the player, the
    /// parts consumed are the player's own (the install recipes eat real
    /// RSW_DW_Part_* items off the player's stockpile), and the incident is
    /// frequency-capped on the QuestScriptDef itself.
    ///
    /// The three tier lists are passed from XML rather than resolved through a
    /// DefOf on purpose: the def loader then cross-checks every hediff name at
    /// load, and this assembly carries no compile-time dependency on Droidworks.
    /// </summary>
    public class QuestNode_DroidRepairJob : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> inSignal;

        public SlateRef<IEnumerable<Pawn>> droids;

        public SlateRef<Faction> customer;

        /// <summary>Silver an honest, standard-quality job is worth before scaling.</summary>
        public SlateRef<int> basePayment;

        public SlateRef<HediffDef> faultHediff;

        public SlateRef<List<HediffDef>> inferiorHediffs;

        public SlateRef<List<HediffDef>> standardHediffs;

        public SlateRef<List<HediffDef>> superiorHediffs;

        [NoTranslate]
        public SlateRef<string> outSignalFine;

        [NoTranslate]
        public SlateRef<string> outSignalHonest;

        [NoTranslate]
        public SlateRef<string> outSignalShoddy;

        [NoTranslate]
        public SlateRef<string> outSignalNeglected;

        private const float FineMultiplier = 1.6f;
        private const float ShoddyMultiplier = 0.4f;

        /// <summary>
        /// Reputation half of the guardrail. A faction that barely tolerates you
        /// pays 0.75x; one at maximum goodwill pays 1.25x. Hostility cannot
        /// arise here (QuestNode_GetNearbySettlement only yields visitable
        /// settlements) but the clamp makes the floor explicit anyway.
        /// </summary>
        private static float ReputationFactor(Faction f)
        {
            if (f == null) return 1f;
            return 0.75f + Mathf.Clamp(f.PlayerGoodwill, 0, 100) / 100f * 0.5f;
        }

        /// <summary>
        /// Wealth half of the guardrail. RimWorld factions carry no wealth stat,
        /// so tech level stands in for it: a neolithic clan cannot pay what a
        /// spacer buyer can.
        /// </summary>
        private static float WealthFactor(Faction f)
        {
            if (f?.def == null) return 1f;
            switch (f.def.techLevel)
            {
                case TechLevel.Undefined:
                case TechLevel.Animal:
                case TechLevel.Neolithic:
                    return 0.7f;
                case TechLevel.Medieval:
                    return 0.8f;
                case TechLevel.Industrial:
                    return 1f;
                case TechLevel.Spacer:
                    return 1.3f;
                default:
                    return 1.5f;
            }
        }

        private void WritePaymentVars(Slate slate, out int fine, out int honest, out int shoddy)
        {
            int fromXml = basePayment.GetValue(slate);
            if (fromXml <= 0) fromXml = 320;

            Faction customerFaction = customer.GetValue(slate);
            float wealthFactor = DroidRepairJobsSettings.wealthAndReputationScaling ? WealthFactor(customerFaction) : 1f;
            float reputationFactor = DroidRepairJobsSettings.wealthAndReputationScaling ? ReputationFactor(customerFaction) : 1f;
            float scaled = fromXml * wealthFactor * reputationFactor * DroidRepairJobsSettings.paymentMultiplier;
            honest = Mathf.Max(1, Mathf.RoundToInt(scaled));
            fine = Mathf.Max(1, Mathf.RoundToInt(scaled * FineMultiplier));
            shoddy = Mathf.Max(1, Mathf.RoundToInt(scaled * ShoddyMultiplier));

            slate.Set("payFine", fine);
            slate.Set("payHonest", honest);
            slate.Set("payShoddy", shoddy);
        }

        protected override bool TestRunInt(Slate slate)
        {
            // The description quotes these, so they must exist during the test
            // run too or the grammar resolver blanks the whole rule.
            WritePaymentVars(slate, out int _, out int _, out int _);
            return true;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            WritePaymentVars(slate, out int fine, out int honest, out int shoddy);

            HediffDef fault = faultHediff.GetValue(slate);
            List<Pawn> jobDroids = new List<Pawn>();
            IEnumerable<Pawn> fromSlate = droids.GetValue(slate);
            if (fromSlate != null)
            {
                foreach (Pawn p in fromSlate)
                {
                    if (p == null) continue;
                    jobDroids.Add(p);
                    // Break it. This is why the customer is here.
                    if (fault != null && p.health != null && !p.health.hediffSet.HasHediff(fault))
                    {
                        p.health.AddHediff(fault);
                    }
                }
            }

            QuestPart_DroidRepairJobOutcome part = new QuestPart_DroidRepairJobOutcome
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate))
                           ?? slate.Get<string>("inSignal"),
                customer = customer.GetValue(slate),
                mapParent = slate.Get<Map>("map")?.Parent,
                faultHediff = fault,
                payFine = fine,
                payHonest = honest,
                payShoddy = shoddy,
                outSignalFine = QuestGenUtility.HardcodedSignalWithQuestID(outSignalFine.GetValue(slate)),
                outSignalHonest = QuestGenUtility.HardcodedSignalWithQuestID(outSignalHonest.GetValue(slate)),
                outSignalShoddy = QuestGenUtility.HardcodedSignalWithQuestID(outSignalShoddy.GetValue(slate)),
                outSignalNeglected = QuestGenUtility.HardcodedSignalWithQuestID(outSignalNeglected.GetValue(slate))
            };
            part.droids.AddRange(jobDroids);
            AddAll(part.inferiorHediffs, inferiorHediffs.GetValue(slate));
            AddAll(part.standardHediffs, standardHediffs.GetValue(slate));
            AddAll(part.superiorHediffs, superiorHediffs.GetValue(slate));

            QuestGen.quest.AddPart(part);
        }

        private static void AddAll(List<HediffDef> target, List<HediffDef> source)
        {
            if (source == null) return;
            for (int i = 0; i < source.Count; i++)
            {
                if (source[i] != null) target.Add(source[i]);
            }
        }
    }
}
