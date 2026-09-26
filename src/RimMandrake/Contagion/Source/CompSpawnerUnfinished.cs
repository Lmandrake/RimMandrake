using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_UNFINISHED_SPAWNER_1. Patched onto the donor AA_RedGoo
    // (Patches/RedGooSpawnsUnfinished.xml) — "What the goo buds" per
    // the_contagion.md §4: the amoeba periodically buds a short-lived
    // RM_TheUnfinished nearby.
    //
    // Deliberately NOT vanilla CompProperties_SpawnerPawn/CompSpawnerPawn
    // (used by Hives to spawn insects): that comp joins every spawned pawn to
    // a Lord and the spawner's own Faction for a defended-nest behaviour,
    // which does not fit a neutral, faction-less wildlife host. This is the
    // same "small utility ThingComp calling vanilla static spawn APIs
    // directly" idiom this mod already uses (AmoebaHostUtility), and the
    // actual spawn call (PawnGenerationRequest + PawnGenerator.GeneratePawn +
    // GenSpawn.Spawn) mirrors CompSpawnerPawn.TrySpawnPawn's own vanilla code.
    public class CompProperties_SpawnerUnfinished : CompProperties
    {
        public PawnKindDef spawnKind;
        public FloatRange intervalDaysRange = new FloatRange(0.6f, 1.4f);
        public int maxNearby = 3;
        public float nearbyCheckRadius = 20f;
        public int spawnCellRadius = 3;

        public CompProperties_SpawnerUnfinished()
        {
            compClass = typeof(CompSpawnerUnfinished);
        }
    }

    public class CompSpawnerUnfinished : ThingComp
    {
        private int nextSpawnTick = -1;

        private CompProperties_SpawnerUnfinished Props => (CompProperties_SpawnerUnfinished)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref nextSpawnTick, "rmUnfinishedNextSpawnTick", -1);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (nextSpawnTick < 0)
            {
                ScheduleNext();
            }
        }

        public override void CompTick()
        {
            if (!RM_ContagionSettings.unfinishedSpawnerEnabled)
            {
                return;
            }
            if (!parent.Spawned || Props.spawnKind == null)
            {
                return;
            }
            if (Find.TickManager.TicksGame < nextSpawnTick)
            {
                return;
            }
            if (NearbyCount() < Props.maxNearby)
            {
                TrySpawn();
            }
            ScheduleNext();
        }

        private int NearbyCount()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return 0;
            }
            int count = 0;
            IReadOnlyList<Pawn> allPawnsSpawned = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < allPawnsSpawned.Count; i++)
            {
                Pawn p = allPawnsSpawned[i];
                if (p.kindDef == Props.spawnKind && p.Position.InHorDistOf(parent.Position, Props.nearbyCheckRadius))
                {
                    count++;
                }
            }
            return count;
        }

        private void TrySpawn()
        {
            Map map = parent.Map;
            if (map == null || !parent.Spawned)
            {
                return;
            }
            if (!CellFinder.TryFindRandomCellNear(
                parent.Position,
                map,
                Props.spawnCellRadius,
                c => c.Standable(map) && !c.Fogged(map),
                out IntVec3 cell))
            {
                return;
            }

            PawnGenerationRequest request = new PawnGenerationRequest(Props.spawnKind, null);
            Pawn pawn = PawnGenerator.GeneratePawn(request);
            GenSpawn.Spawn(pawn, cell, map);
        }

        private void ScheduleNext()
        {
            nextSpawnTick = Find.TickManager.TicksGame + (int)(Props.intervalDaysRange.RandomInRange * 60000f);
        }
    }
}
