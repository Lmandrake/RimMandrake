using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>CREATURE_BEHAVIOR_LAST_OUTCOME_1 (CB-7). What a behaviour comp last decided and why, kept as a short code
    /// the way RM_CompTetherPull keeps tetherLastOutcome, so a test script reads the answer instead of watching for it.
    /// A repeat of the same code only bumps a count (a lure that declines every scan does not rewrite the tick).
    /// Shown in the inspect string and readable as Code/Count/Tick.</summary>
    public class RM_LastOutcomeLog : IExposable
    {
        private string code = "";
        private int count;
        private int sinceTick;

        public string Code => code;
        public int Count => count;
        public int SinceTick => sinceTick;

        public void Record(string newCode)
        {
            if (newCode == code)
            {
                count++;
                return;
            }
            code = newCode;
            count = 1;
            sinceTick = Find.TickManager != null ? Find.TickManager.TicksGame : 0;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref code, "code", "");
            Scribe_Values.Look(ref count, "count");
            Scribe_Values.Look(ref sinceTick, "sinceTick");
        }

        public static void Record(ref RM_LastOutcomeLog log, string newCode)
        {
            if (!RM_CreatureBehaviorsSettings.lastOutcomeInspectEnabled)
            {
                return;
            }
            if (log == null)
            {
                log = new RM_LastOutcomeLog();
            }
            log.Record(newCode);
        }

        public static string InspectLine(RM_LastOutcomeLog log)
        {
            if (!RM_CreatureBehaviorsSettings.lastOutcomeInspectEnabled || log == null || log.code.NullOrEmpty())
            {
                return null;
            }
            int ago = (Find.TickManager != null ? Find.TickManager.TicksGame : 0) - log.sinceTick;
            return "Last decision: " + log.code + (log.count > 1 ? " (x" + log.count + ")" : "") + ", since " + ago.ToStringTicksToPeriod() + " ago";
        }
    }
}
