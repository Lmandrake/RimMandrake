using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 3 of 8 (item's "spacer rescue";
    /// mechanism reference: infrastructure/state/items/
    /// RUT_SCAVENGEREVENTS_BUILD_1.md). Unconditional: one Villager-kind pawn
    /// from a random non-hostile faction, downed (not dead), dropped in a pod.
    /// Uses a quest-hook LetterDef ("NewQuest") rather than a plain Positive/
    /// NegativeEvent, matching the donor's own choice -- this is meant to read
    /// as an opportunity, not just flavor. Ported behavior-not-bugs from
    /// MoreIncidents.MOIncidentWorker_PodCrashTribal.
    /// </summary>
    public class IncidentWorker_PodCrashTribal : IncidentWorker
    {
        private const int OpenDelayTicks = 180;

        private static LetterDef newQuestLetter;
        private static bool newQuestLetterResolved;

        private static LetterDef NewQuestLetter
        {
            get
            {
                if (!newQuestLetterResolved)
                {
                    newQuestLetter = DefDatabase<LetterDef>.GetNamedSilentFail("NewQuest");
                    newQuestLetterResolved = true;
                }
                return newQuestLetter;
            }
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;
            IntVec3 dropSpot = DropCellFinder.RandomDropSpot(map);

            Faction faction = Find.FactionManager.RandomNonHostileFaction(true, true, true, TechLevel.Neolithic);
            if (faction == null)
                return false;

            var request = new PawnGenerationRequest(
                PawnKindDefOf.Villager,
                faction,
                PawnGenerationContext.NonPlayer);
            Pawn pawn = PawnGenerator.GeneratePawn(request);

            HealthUtility.DamageUntilDowned(pawn);

            Find.LetterStack.ReceiveLetter(
                "RUT_TribalAid".Translate(),
                "RUT_TribalAidDesc".Translate(),
                NewQuestLetter ?? LetterDefOf.PositiveEvent,
                new TargetInfo(dropSpot, map));

            var podInfo = new ActiveTransporterInfo
            {
                openDelay = OpenDelayTicks,
                leaveSlag = true,
            };
            podInfo.SingleContainedThing = pawn;
            DropPodUtility.MakeDropPodAt(dropSpot, map, podInfo);

            return true;
        }
    }
}
