using System.Collections.Generic;
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
    /// Where the ember goes (owner, 2026-11-13: "Carry distance should actually be anywhere on the map, unlimited. To the largest
    /// fuel source easily found."; earlier the same day: "Prefers to carry it farther rather than shorter if available fuel
    /// exists."): anywhere on the map, to the best bucket of MapComponent_RM_FireHawkFuel's coarse fuel map, its densest fuel
    /// cell. "Largest" is the fuel in a bucket's 3 x 3 block; "easily found" is unfogged, unroofed, unburnt, out of the blaze's
    /// block and reachable; ties go to the farther patch. No fuel anywhere, no sortie. The pick is RM_FireHawkKernel.PickDrop,
    /// fuzzed offline (family hawk). Owner, 2026-11-13: "That gives a great reason for players to hunt the Firehawk."
    /// </summary>
    public class JobGiver_RUT_FireHawkCarryEmber : ThinkNode_JobGiver
    {
        /// <summary>A cap on reach checks per sortie: one per candidate patch, best first, and a hawk walled off from this many
        /// of them waits out its cooldown instead of asking every bucket on the map.</summary>
        private const int MaxReachTries = 48;

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
            // Charging it only after the drop search (TryFindFuelOnTheMap) also succeeds left a
            // hawk beside a fire with no reachable/flammable cell nearby (map edge,
            // rock, water) with NO cooldown at all — CanSortieNow stays true and it
            // re-runs FindFireToStealFrom + the drop search every think tick,
            // exactly the "fire timer with no cooldown" the comment warns against.
            comp.Notify_SortieStarted();

            if (!TryFindFuelOnTheMap(pawn, source.Position, out IntVec3 target))
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
        /// The ember's target anywhere on the map (RM_FireHawkKernel.PickDrop). Cost per sortie, once per FireHawkCooldownTicks: the
        /// cached fuel counts (a whole-map scan only when they are FireHawkFuelRefreshTicks old), one pass over the map's fires to
        /// mark burning buckets, a sort of the candidate buckets (1,024 on a 250 map), and per candidate tried a 64-cell densest-cell
        /// walk, the full drop check and one CanReach, at most MaxReachTries of them.
        /// </summary>
        /// <summary>Script probe (jawa/static_call, args "hawkThingID|x,z"; firehawk_mapwide_carry): recount the hawk's map now and
        /// say where an ember stolen at `from` would go. A STATE read of the same pick a sortie makes, never a flight.</summary>
        public static string ProbeFuelPick(Pawn hawk, IntVec3 from)
        {
            if (hawk?.Map == null) return "pick=none reason=no-map";
            MapComponent_RM_FireHawkFuel fuel = MapComponent_RM_FireHawkFuel.For(hawk.Map);
            if (fuel == null) return "pick=none reason=no-fuel-component";
            fuel.Recount();
            bool ok = TryFindFuelOnTheMap(hawk, from, out IntVec3 c);
            return (ok ? "pick=" + c.x + "," + c.z : "pick=none") + " fuelCells=" + fuel.CountedCells + " bucket=" + PyrelandsTuning.FireHawkFuelBucket;
        }

        private static bool TryFindFuelOnTheMap(Pawn pawn, IntVec3 origin, out IntVec3 result)
        {
            Map map = pawn.Map;
            MapComponent_RM_FireHawkFuel fuel = MapComponent_RM_FireHawkFuel.For(map);
            result = IntVec3.Invalid;
            if (fuel == null)
            {
                return false;
            }
            int sx = map.Size.x, sz = map.Size.z, bucket = PyrelandsTuning.FireHawkFuelBucket;
            var fires = new List<int>();
            List<Thing> all = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < all.Count; i++)
            {
                fires.Add(map.cellIndices.CellToIndex(all[i].Position));
            }
            int pick = RM_FireHawkKernel.PickDrop(sx, sz, bucket, fuel.Counts, RM_FireHawkKernel.FireBuckets(sx, sz, bucket, fires),
                origin.x, origin.z, fuel.FuelCell,
                (x, z) =>
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    return IsFuelledDrop(c, map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly);
                },
                MaxReachTries);
            if (pick < 0)
            {
                return false;
            }
            result = map.cellIndices.IndexToCell(pick);
            return true;
        }

        private static bool IsFuelledDrop(IntVec3 cell, Map map)
        {
            if (!cell.InBounds(map))
            {
                return false;
            }
            Plant plant = cell.GetPlant(map);
            float growth = plant == null ? -1f : plant.Growth;
            float min = MapComponent_RM_FireHawkFuel.MinFuelGrowth;
            if (growth < min || cell.Fogged(map) || cell.Roofed(map))
            {
                return false;
            }
            return RM_FireHawkKernel.FuelledDrop(true, FireUtility.ChanceToStartFireIn(cell, map) > 0f, growth, min, FireOnOrBeside(cell, map));
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
