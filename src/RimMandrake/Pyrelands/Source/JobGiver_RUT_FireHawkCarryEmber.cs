using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 3 — the decision half of the fire-hawk's
    /// twig (RUT_ruled_commissions_wave2.md §7c).
    ///
    /// 🔴 SPREAD-ONLY, NEVER EX NIHILO — RATIFIED (owner, 2026-09-10, commit
    /// 4a6f6200). The FIRST thing this method does after the cheap gates is look
    /// for an existing fire, and it returns null if there is not one. There is no
    /// other branch: the hawk cannot start a fire, only move one. Lightning and
    /// the furnace-beast start; the hawk spreads. Anyone editing this file: that
    /// early return is the def's law, not an optimisation.
    ///
    /// Wired into the vanilla Animal think tree at the Animal_PreWander insertion
    /// tag, the same supported modder hook
    /// src/RimMandrake/RimProperty/Defs/AnimalTheft/ThinkTreeDefs_AnimalSteal.xml
    /// uses in this repo. No faction gate: §7d rules the hawk tameable and rules
    /// that "the fire a tamed hawk spreads is still nobody's friend", so a tamed
    /// hawk carries twigs in your base exactly as a wild one does.
    ///
    /// Direction is ahead of the blaze, away from the burn's centre (north star: "ahead of the existing blaze"; the first
    /// version was random). Wind was NOT wired: the
    /// engine exposes wind as a weather-driven speed
    /// (WeatherManager/Map.windManager.WindSpeed), not a bearing, so there is no
    /// cheap "downwind" vector to read. Saying so here rather than inventing one.
    /// </summary>
    public class JobGiver_RUT_FireHawkCarryEmber : ThinkNode_JobGiver
    {
        /// <summary>How many random bearings are tried before the hawk gives up
        /// on this fire and waits out its cooldown.</summary>
        private const int BearingTries = 8;

        /// <summary>Younger grass than this is a scar's sprouts, not fuel worth an ember.</summary>
        private const float MinFuelGrowth = 0.25f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.fireHawkSpreadEnabled)
            {
                return null;
            }
            if (pawn == null || !pawn.Spawned || pawn.Downed || !pawn.Awake())
            {
                return null;
            }

            CompFireHawkSpread comp = pawn.TryGetComp<CompFireHawkSpread>();
            if (comp == null || !comp.CanSortieNow)
            {
                return null;
            }

            // ---- THE SPREAD-ONLY GATE. No fire in range, no behaviour. ----
            Fire source = FindFireToStealFrom(pawn, comp.Props.scanRadius);
            if (source == null)
            {
                return null;
            }

            // The sortie STARTS here, the moment a fire worth chasing is found —
            // not only once a landing cell is also found. CompFireHawkSpread's own
            // header is explicit: "charged when the sortie STARTS, not when it
            // succeeds, so a hawk that fails to find a lawful cell still pays."
            // Charging it only after TryFindCellBeyondTheFire also succeeds left a
            // hawk beside a fire with no reachable/flammable cell nearby (map edge,
            // rock, water) with NO cooldown at all — CanSortieNow stays true and it
            // re-runs FindFireToStealFrom + the 8-bearing search every think tick,
            // exactly the "fire timer with no cooldown" the comment warns against.
            comp.Notify_SortieStarted();

            if (!TryFindCellBeyondTheFire(pawn, source, comp.Props.spreadDistance, out IntVec3 target))
            {
                return null;
            }

            Job job = JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_FireHawkCarryEmber, source, target);
            job.count = 1;
            return job;
        }

        private static Fire FindFireToStealFrom(Pawn pawn, float radius)
        {
            return (Fire)GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForDef(ThingDefOf.Fire),
                PathEndMode.Touch,
                TraverseParms.For(pawn, Danger.Deadly),
                radius,
                // A fire attached to a burning pawn or a burning wall is not a
                // burn-line to steal from; only free-standing ground fire is.
                (Thing t) => t is Fire { parent: null } f && f.Spawned && !f.Position.Fogged(f.Map));
        }

        /// <summary>
        /// One cell, spreadDistance out from the fire's own position, AHEAD of the blaze: of the lawful bearings tried, the
        /// one with standing grass and no fire beside it that lies farthest from the burn's centre, so the ember lands in
        /// fuel the front has not reached rather than back in its own scar. With no such cell, any lawful one, as before.
        /// Validated against vanilla's own ChanceToStartFireIn so terrain flammability, fire bulwarks and existing fires are
        /// all respected without re-deriving any of it.
        /// </summary>
        private static bool TryFindCellBeyondTheFire(Pawn pawn, Fire source, int distance, out IntVec3 result)
        {
            Map map = pawn.Map;
            MapComponent_BurnLine burn = map.GetComponent<MapComponent_BurnLine>();
            IntVec3 centre = burn != null && burn.AnyBurn ? burn.BurnCenter : source.Position;
            result = IntVec3.Invalid;
            bool haveFuel = false;
            float best = -1f;
            for (int i = 0; i < BearingTries; i++)
            {
                float angle = Rand.Range(0f, 360f);
                Vector3 offset = Quaternion.AngleAxis(angle, Vector3.up) * Vector3.forward * distance;
                IntVec3 candidate = source.Position + offset.ToIntVec3();

                if (candidate == source.Position || !candidate.InBounds(map))
                {
                    continue;
                }
                if (FireUtility.ChanceToStartFireIn(candidate, map) <= 0f)
                {
                    continue;
                }
                if (!pawn.CanReach(candidate, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }

                bool fuel = HasStandingFuel(candidate, map);
                if (haveFuel && !fuel)
                {
                    continue;
                }
                float score = candidate.DistanceToSquared(centre);
                if ((fuel && !haveFuel) || score > best)
                {
                    haveFuel = fuel;
                    best = score;
                    result = candidate;
                }
            }
            return result.IsValid;
        }

        private static bool HasStandingFuel(IntVec3 cell, Map map)
        {
            Plant plant = cell.GetPlant(map);
            if (plant == null || plant.Growth < MinFuelGrowth)
            {
                return false;
            }
            for (int i = 0; i < GenAdj.AdjacentCellsAndInside.Length; i++)
            {
                IntVec3 c = cell + GenAdj.AdjacentCellsAndInside[i];
                if (c.InBounds(map) && c.ContainsStaticFire(map))
                {
                    return false;
                }
            }
            return true;
        }
    }
}
