using RimWorld;
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
    /// Where the ember goes (owner, 2026-11-13: "Prefers to carry it farther rather than shorter if available fuel exists."):
    /// the farthest fuelled cell inside spreadDistance of the stolen fire, a nearer one only when no farther one is lawful, and
    /// no sortie at all when there is no fuel in range. Equally far cells are split by distance from the burn's centre, so the
    /// ember still lands ahead of the blaze (north star: "ahead of the existing blaze"). The pick is
    /// RM_FireHawkKernel.FarthestFuelledDrop, fuzzed offline (family hawk). Wind was NOT wired: the engine exposes wind as a
    /// weather-driven speed (Map.windManager.WindSpeed), not a bearing, so there is no cheap "downwind" vector to read.
    /// </summary>
    public class JobGiver_RUT_FireHawkCarryEmber : ThinkNode_JobGiver
    {
        /// <summary>A cap on reach checks per sortie: the pick asks CanReach only of fuelled cells, farthest first, and a hawk
        /// walled off from this many of them waits out its cooldown instead of pathing to every cell in range.</summary>
        private const int MaxReachTries = 48;

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
            if (source == null || !RM_FireHawkKernel.FireInScan(source.Position.x - pawn.Position.x, source.Position.z - pawn.Position.z, comp.Props.scanRadius))
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
            // re-runs FindFireToStealFrom + the drop search every think tick,
            // exactly the "fire timer with no cooldown" the comment warns against.
            comp.Notify_SortieStarted();

            if (!TryFindCellBeyondTheFire(pawn, source, comp.Props.spreadDistance, out IntVec3 target))
            {
                return null;
            }

            Job job = JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_FireHawkCarryEmber, source, target, source.Position);
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
        /// The farthest fuelled cell inside distance of the fire's own position (RM_FireHawkKernel.FarthestFuelledDrop over
        /// GenRadial's cells, nearest first). Fuel is vanilla's own ChanceToStartFireIn (terrain flammability, fire bulwarks and
        /// fires in the cell, none of it re-derived) plus standing grass with no fire beside it. Cost per sortie, once per
        /// FireHawkCooldownTicks: at most GenRadial.NumCellsInRadius(18) (about 1,000) cells, each a plant lookup first, the 9-cell
        /// fire check and ChanceToStartFireIn only on grown grass, and CanReach on at most MaxReachTries fuelled cells; in open
        /// grass the walk stops in the outermost ring.
        /// </summary>
        private static bool TryFindCellBeyondTheFire(Pawn pawn, Fire source, int distance, out IntVec3 result)
        {
            Map map = pawn.Map;
            MapComponent_BurnLine burn = map.GetComponent<MapComponent_BurnLine>();
            IntVec3 centre = burn != null && burn.AnyBurn ? burn.BurnCenter : source.Position;
            IntVec3 origin = source.Position;
            int n = GenRadial.NumCellsInRadius(distance);
            int pick = RM_FireHawkKernel.FarthestFuelledDrop(n,
                i => GenRadial.RadialPattern[i].LengthHorizontalSquared,
                i => IsFuelledDrop(origin + GenRadial.RadialPattern[i], map),
                i => (origin + GenRadial.RadialPattern[i]).DistanceToSquared(centre),
                i => pawn.CanReach(origin + GenRadial.RadialPattern[i], PathEndMode.OnCell, Danger.Deadly),
                MaxReachTries);
            result = pick < 0 ? IntVec3.Invalid : origin + GenRadial.RadialPattern[pick];
            return result.IsValid;
        }

        private static bool IsFuelledDrop(IntVec3 cell, Map map)
        {
            if (!cell.InBounds(map))
            {
                return false;
            }
            Plant plant = cell.GetPlant(map);
            float growth = plant == null ? -1f : plant.Growth;
            if (growth < MinFuelGrowth)
            {
                return false;
            }
            return RM_FireHawkKernel.FuelledDrop(true, FireUtility.ChanceToStartFireIn(cell, map) > 0f, growth, MinFuelGrowth, FireOnOrBeside(cell, map));
        }

        private static bool FireOnOrBeside(IntVec3 cell, Map map)
        {
            for (int i = 0; i < GenAdj.AdjacentCellsAndInside.Length; i++)
            {
                IntVec3 c = cell + GenAdj.AdjacentCellsAndInside[i];
                if (c.InBounds(map) && c.ContainsStaticFire(map))
                {
                    return true;
                }
            }
            return false;
        }
    }
}
