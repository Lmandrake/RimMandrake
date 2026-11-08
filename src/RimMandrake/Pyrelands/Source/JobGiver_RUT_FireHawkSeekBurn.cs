using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// pyre_firehawk_carries_ember in ordinary play: a fire-hawk is drawn to a burn it can see. Real fire-hawk raptors gather at a
    /// fire front from far off; this one met a fire only by chance, because its ember job looks no further than scanRadius (18).
    /// On map r both hawks idled 100 to 130 cells from a 190-cell burn for a whole night.
    ///
    /// Out of reach of every open-ground fire and ready for a sortie, it flies (RM_FireHawkSeekBurn requests flight) to a cell on
    /// its own side of the nearest fire, inside scanRadius; the ember node (insertPriority 55, above this one's 54) takes over on
    /// its next think. It never charges the sortie cooldown: only the ember job does.
    /// </summary>
    public class JobGiver_RUT_FireHawkSeekBurn : ThinkNode_JobGiver
    {
        /// <summary>How far a hawk sees smoke: the whole of a standard 250 map from its middle.</summary>
        private const float SightRange = 180f;
        /// <summary>A hawk notices the smoke on some thinks, not the first one, so a new burn draws them over an hour or so.</summary>
        private const float NoticeChance = 0.35f;
        /// <summary>Stand-off from the fire as a share of scanRadius: inside reach, outside the flames.</summary>
        private const float StandOffShare = 0.6f;
        private const int StandOffSearchRadius = 5;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.fireHawkSpreadEnabled)
            {
                return null;
            }
            if (pawn == null || !pawn.Spawned || pawn.Downed || !pawn.Awake() || pawn.InMentalState)
            {
                return null;
            }
            CompFireHawkSpread comp = pawn.TryGetComp<CompFireHawkSpread>();
            if (comp == null || !comp.CanSortieNow)
            {
                return null;
            }
            Map map = pawn.Map;
            Fire nearest = NearestOpenFire(pawn, map, out float distSq);
            if (nearest == null)
            {
                return null;
            }
            float reach = comp.Props.scanRadius;
            if (distSq <= reach * reach * 0.81f || distSq > SightRange * SightRange)
            {
                return null;   // within reach: the ember node decides; or too far to see
            }
            if (!Rand.Chance(NoticeChance))
            {
                return null;
            }
            Vector3 away = (pawn.Position - nearest.Position).ToVector3();
            away.y = 0f;
            IntVec3 goal = nearest.Position + (away.normalized * reach * StandOffShare).ToIntVec3();
            goal = goal.ClampInsideMap(map);
            if (!CellFinder.TryFindRandomCellNear(goal, map, StandOffSearchRadius,
                    c => c.Standable(map) && !c.Fogged(map) && c.GetFirstThing<Fire>(map) == null
                         && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly),
                    out IntVec3 cell))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_FireHawkSeekBurn, cell);
            job.locomotionUrgency = LocomotionUrgency.Jog;
            job.expiryInterval = GenDate.TicksPerHour * 2;
            job.checkOverrideOnExpire = true;
            return job;
        }

        private static Fire NearestOpenFire(Pawn pawn, Map map, out float bestSq)
        {
            bestSq = float.MaxValue;
            Fire best = null;
            var fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (!(fires[i] is Fire f) || f.parent != null || !f.Spawned || f.Position.Fogged(map))
                {
                    continue;
                }
                float d = (f.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestSq)
                {
                    bestSq = d;
                    best = f;
                }
            }
            return best;
        }
    }
}
