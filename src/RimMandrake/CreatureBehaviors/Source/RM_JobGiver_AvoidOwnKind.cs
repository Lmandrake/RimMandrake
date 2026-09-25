using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. Inserted globally via
    /// RM_ThinkTree_VerminBehaviors (insertTag = Animal_PreMain) — same
    /// no-op-without-the-extension shape as every other JobGiver in that
    /// tree. Steers a pawn away from the nearest other member of its own
    /// PawnKindDef once it is inside RM_SpeciesSpacingExtension's
    /// avoidRadiusCells; RM_CompHeatCook is the "or cook each other"
    /// consequence for whenever this fails to happen in time (a pen, a
    /// cage, a cornered map).
    /// </summary>
    public class RM_JobGiver_AvoidOwnKind : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_CreatureBehaviorsSettings.speciesSpacingEnabled)
            {
                return null; // mod option: species-spacing behavior disabled
            }
            RM_SpeciesSpacingExtension ext = pawn.def?.GetModExtension<RM_SpeciesSpacingExtension>();
            if (ext == null || pawn.Map == null || pawn.Downed)
            {
                return null;
            }
            if (!Rand.Chance(ext.checkChancePerCheck))
            {
                return null;
            }

            float avoidRadiusSq = ext.avoidRadiusCells * ext.avoidRadiusCells;
            Pawn nearest = null;
            float nearestDistSq = avoidRadiusSq;
            IReadOnlyList<Pawn> pawns = pawn.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn other = pawns[i];
                if (other == pawn || other.Dead || other.kindDef != pawn.kindDef)
                {
                    continue;
                }
                float distSq = (other.Position - pawn.Position).LengthHorizontalSquared;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = other;
                }
            }
            if (nearest == null)
            {
                return null; // nothing of its own kind close enough to matter
            }

            Map map = pawn.Map;
            int searchRadius = UnityEngine.Mathf.CeilToInt(ext.avoidRadiusCells * 2f);
            bool found = CellFinder.TryFindRandomCellNear(pawn.Position, map, searchRadius,
                (IntVec3 c) => c.Standable(map)
                    && (c - nearest.Position).LengthHorizontalSquared >= avoidRadiusSq
                    && map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)),
                out IntVec3 dest);
            if (!found)
            {
                return null;
            }
            return JobMaker.MakeJob(JobDefOf.Goto, dest);
        }
    }
}
