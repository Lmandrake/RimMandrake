using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 6 of 8 (mechanism reference:
    /// infrastructure/state/items/RUT_SCAVENGEREVENTS_BUILD_1.md). A random
    /// free colonist collapses: downed, rest need maxed, current job ended,
    /// gains a two-day "had a stroke" memory, ten blood-filth splashes
    /// scattered nearby, game speed nudged back to normal so the player
    /// doesn't miss it while fast-forwarding. Ported behavior-not-bugs from
    /// MoreIncidents.MOIncidentWorker_Stroke.
    /// </summary>
    public class IncidentWorker_Stroke : IncidentWorker
    {
        private const int BloodSplashCount = 10;
        private const int BloodSplashRadius = 3;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!ScavengerEventsSettings.strokeEnabled)
                return false;
            var map = (Map)parms.target;
            return map.mapPawns.FreeColonists.Count > 0;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;

            if (!map.mapPawns.FreeColonists.TryRandomElement(out Pawn pawn))
                return false;

            HealthUtility.DamageUntilDowned(pawn);
            pawn.needs.rest.CurLevel = 10f; // clamps to max; matches the donor's own literal
            pawn.jobs.EndCurrentJob(JobCondition.None, true, true);
            pawn.needs.mood.thoughts.memories.TryGainMemory(
                ThoughtDef.Named("RUT_HadStroke"));

            Find.LetterStack.ReceiveLetter(
                "RUT_Stroke".Translate(),
                "RUT_StrokeDesc".Translate(pawn.Named("PAWN")),
                LetterDefOf.NegativeEvent,
                pawn);

            for (int i = 0; i < BloodSplashCount; i++)
            {
                IntVec3 splashCell = CellFinder.RandomClosewalkCellNear(pawn.Position, map, BloodSplashRadius);
                FilthMaker.TryMakeFilth(splashCell, map, ThingDefOf.Filth_Blood);
            }

            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }
    }
}
