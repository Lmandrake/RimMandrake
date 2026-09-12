using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1. The two questions every other file in this mod asks:
    /// "is this pawn one of the hive's?" and "put worms on the ground here".
    /// </summary>
    public static class BrainWormUtility
    {
        /// <summary>
        /// The hive lens. A puppeted host does not attack the worms that made it,
        /// nor other hosts - that is the whole difference between this and vanilla
        /// berserk, which attacks everything on the map including its own side.
        ///
        /// Deliberately asks only whether the infection hediff is PRESENT, not what
        /// severity it sits at: a latent carrier standing in the room is already
        /// hive property as far as a puppet is concerned, and that reads correctly
        /// in play (the puppet walks past the friend it infected last week).
        /// </summary>
        public static bool IsHiveFlesh(Pawn p)
        {
            if (p == null || p.Dead)
            {
                return false;
            }
            if (p.kindDef == BrainWormsDefOf.RSW_BrainWormKind)
            {
                return true;
            }
            return p.health?.hediffSet?.HasHediff(BrainWormsDefOf.RSW_BrainWormInfection) ?? false;
        }

        /// <summary>
        /// Spawn <paramref name="count"/> loose worms of <paramref name="kind"/> around
        /// a cell - used by the egg shell's projectile on impact and by the cold
        /// cure's expulsion. Factionless: the worms are not a raid, they are a hazard
        /// that crawls. <paramref name="kind"/> is caller-supplied rather than hardcoded
        /// here so a HediffCompProperties_BrainWormProgress.expelledWorm configured to
        /// something other than the default actually takes effect; null spawns nothing.
        /// </summary>
        public static void SpawnWormBurst(Map map, IntVec3 center, int count, PawnKindDef kind)
        {
            if (map == null || !center.InBounds(map) || kind == null)
            {
                return;
            }

            for (int i = 0; i < count; i++)
            {
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(center, map, 3);
                Pawn worm = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(worm, cell, map);
            }
        }
    }
}
