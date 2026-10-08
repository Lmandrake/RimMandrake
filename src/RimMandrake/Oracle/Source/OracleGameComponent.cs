using System;
using System.Threading.Tasks;
using RimWorld;
using Verse;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// Owns the off-tick async call and the main-thread delivery queue.
    /// design/RimMandrake/llm_ingame_wiring_spec.md §0 law #2: the game is
    /// whole with the LLM absent -- every path below ends in a delivered
    /// letter, live or fallback, never an exception reaching the player and
    /// never a silent no-op.
    /// </summary>
    public class OracleGameComponent : GameComponent
    {
        private readonly OracleDeliveryQueue pendingDeliveries = new OracleDeliveryQueue();
        private int godsCallsToday = 0;
        private int lastBudgetResetDay = -1;

        public OracleGameComponent(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref godsCallsToday, "godsCallsToday", 0);
            Scribe_Values.Look(ref lastBudgetResetDay, "lastBudgetResetDay", -1);
        }

        public override void GameComponentTick()
        {
            pendingDeliveries.Drain(e => Log.Error("RimMandrake.Oracle: delivery action threw -- " + e));
        }

        /// <summary>
        /// The one consumer this spike ships: a letter attributed to Ohm.
        /// contextSummary is the user-turn content; fallbackText ships if
        /// anything at all goes wrong.
        /// </summary>
        public void RequestOhmLetter(string letterLabel, string contextSummary, string fallbackText)
        {
            OracleSettings settings = OracleMod.Settings;

            int today = (int)(GenTicks.TicksGame / GenDate.TicksPerDay);
            // No credential gate any more: the Claude Code CLI authenticates through the machine's own login, so there is
            // nothing here to check that would not amount to guessing. A CLI that is missing, logged out or broken fails
            // inside the call below and lands in the same fallback as every other failure.
            if (OracleKernel.Admit(settings.enabled, today, settings.godsBudgetPerDay, ref lastBudgetResetDay, ref godsCallsToday, out string refusal)
                != OracleKernel.Admission.Call)
            {
                Deliver(letterLabel, OracleKernel.Refused(refusal, fallbackText));
                return;
            }

            string system = OracleKernel.SystemPrompt(OracleRegisterBlocks.Law, OracleRegisterBlocks.Ohm);

            Task.Run(async () =>
            {
                string content = null;
                Exception failure = null;
                try
                {
                    content = await OracleClient.RequestCompletion(
                        system, contextSummary,
                        settings.timeoutSeconds, settings.claudeCliPath).ConfigureAwait(false);
                }
                catch (Exception e)
                {
                    failure = e;
                }
                OracleKernel.Outcome outcome = OracleKernel.Resolve(content, failure, fallbackText);
                pendingDeliveries.Enqueue(() => Deliver(letterLabel, outcome));
            });
        }

        /// <summary>
        /// Ships one letter, live or fallback, per spec law #2. ORACLE_FALLBACK_UNVALIDATED_1 (2026-09-17): the fallback
        /// is a CALLER argument and used to reach ReceiveLetter verbatim -- the one path guaranteed to run whenever
        /// validation rejects a live reply was the one path never validated. OracleKernel holds the fallback to the SAME
        /// bar as a live response and ships the hardcoded safe text if even that fails.
        /// </summary>
        private static void Deliver(string label, OracleKernel.Outcome outcome)
        {
            if (outcome.Kind == OracleKernel.DeliveryKind.SafeDefault)
            {
                Log.Message("RimMandrake.Oracle: fallback text itself rejected for \"" + label +
                    "\" -- shipping the safe default instead (" + outcome.Reason + ")");
            }
            else if (outcome.Kind == OracleKernel.DeliveryKind.Fallback)
            {
                Log.Message("RimMandrake.Oracle: falling back for \"" + label + "\" -- " + outcome.Reason);
            }
            Find.LetterStack.ReceiveLetter(label, outcome.Text, LetterDefOf.NeutralEvent);
        }
    }
}
