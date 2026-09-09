using System;
using System.Collections.Concurrent;
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
        private readonly ConcurrentQueue<Action> pendingDeliveries = new ConcurrentQueue<Action>();
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
            while (pendingDeliveries.TryDequeue(out Action action))
            {
                try
                {
                    action();
                }
                catch (Exception e)
                {
                    Log.Error("RimMandrake.Oracle: delivery action threw -- " + e);
                }
            }
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
            if (today != lastBudgetResetDay)
            {
                lastBudgetResetDay = today;
                godsCallsToday = 0;
            }

            if (!settings.enabled)
            {
                DeliverFallback(letterLabel, fallbackText, "kill switch off");
                return;
            }
            // No credential gate any more: the Claude Code CLI authenticates
            // through the machine's own login, so there is nothing here to check
            // that would not amount to guessing. A CLI that is missing, logged
            // out or broken fails inside the call below and lands in the same
            // fallback as every other failure.
            if (godsCallsToday >= settings.godsBudgetPerDay)
            {
                DeliverFallback(letterLabel, fallbackText, "budget exhausted for today (" + godsCallsToday + "/" + settings.godsBudgetPerDay + ")");
                return;
            }
            godsCallsToday++;

            string system = OracleRegisterBlocks.Law + "\n\n" + OracleRegisterBlocks.Ohm;

            Task.Run(async () =>
            {
                try
                {
                    string content = await OracleClient.RequestCompletion(
                        system, contextSummary,
                        settings.timeoutSeconds, settings.claudeCliPath).ConfigureAwait(false);

                    if (OracleValidator.TryValidateOhm(content, out string rejectReason))
                    {
                        pendingDeliveries.Enqueue(() => Deliver(letterLabel, content));
                    }
                    else
                    {
                        pendingDeliveries.Enqueue(() => DeliverFallback(letterLabel, fallbackText, "validator rejected: " + rejectReason));
                    }
                }
                catch (Exception e)
                {
                    pendingDeliveries.Enqueue(() => DeliverFallback(letterLabel, fallbackText, "call failed: " + e.Message));
                }
            });
        }

        private static void Deliver(string label, string text)
        {
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.NeutralEvent);
        }

        private static void DeliverFallback(string label, string fallbackText, string reason)
        {
            Log.Message("RimMandrake.Oracle: falling back for \"" + label + "\" -- " + reason);
            Find.LetterStack.ReceiveLetter(label, fallbackText, LetterDefOf.NeutralEvent);
        }
    }
}
