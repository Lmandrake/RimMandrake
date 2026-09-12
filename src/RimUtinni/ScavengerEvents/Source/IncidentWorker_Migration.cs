using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 1 of 8 (mechanism reference:
    /// infrastructure/state/items/RUT_SCAVENGEREVENTS_BUILD_1.md). Ambient
    /// wildlife passage: a small herd of biome-correct animals enters at a
    /// map edge, walks toward a far point, and leaves on arrival or after a
    /// timeout. Ported behavior-not-bugs from
    /// MoreIncidents.MOIncidentWorker_Migration -- the donor's animal-count
    /// formula was an opaque integer-division artifact (poolCount canceled
    /// out of its own ratio, then a redundant Math.Round on an already-
    /// integer value), not intentional tuning, so it is replaced here with a
    /// plain Rand.RangeInclusive(2, 8).
    /// </summary>
    public class IncidentWorker_Migration : IncidentWorker
    {
        private const int MinHerdSize = 2;
        private const int MaxHerdSize = 8;
        private const int MinExitTicks = 10000;
        private const int MaxExitTicks = 12000;
        private const int WalkTargetSearchRadius = 10;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!ScavengerEventsSettings.migrationEnabled)
                return false;
            var map = (Map)parms.target;
            return map.Biome.AllWildAnimals.Any();
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;

            var pool = map.Biome.AllWildAnimals.ToList();
            if (pool.Count == 0)
                return false;

            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entryCell, map, 0f, false))
                return false;

            IntVec3 walkTarget = CellFinder.RandomClosewalkCellNear(map.Center, map, WalkTargetSearchRadius);

            int herdSize = Rand.RangeInclusive(MinHerdSize, MaxHerdSize);
            bool spawnedAny = false;
            for (int i = 0; i < herdSize; i++)
            {
                PawnKindDef kind = pool.RandomElement();
                Pawn animal = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(animal, entryCell, map);

                Job goJob = new Job(JobDefOf.Goto, walkTarget) { exitMapOnArrival = true };
                animal.jobs.StartJob(goJob, JobCondition.InterruptForced);
                animal.mindState.exitMapAfterTick = Find.TickManager.TicksGame + Rand.Range(MinExitTicks, MaxExitTicks);
                spawnedAny = true;
            }

            if (!spawnedAny)
                return false;

            Find.LetterStack.ReceiveLetter(
                "RUT_Migration".Translate(),
                "RUT_MigrationDesc".Translate(),
                LetterDefOf.NeutralEvent,
                new TargetInfo(entryCell, map));

            return true;
        }
    }
}
