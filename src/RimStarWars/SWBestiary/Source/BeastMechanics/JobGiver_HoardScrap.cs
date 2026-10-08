using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // SHRUBLAND_SCRAPNEST_BIRDS_1 — see CompScrapHoarder.cs for the header and
    // for what was surveyed in the engine before any of this was written.
    //
    // Inserted at the vanilla Animal_PreMain think-tree tag (see
    // Defs/ScrapNest/RSW_ScrapNest.xml), which is consulted BEFORE the
    // satisfy-basic-needs subtree. That tree position cannot be relied on to
    // let food win, so this giver gates itself: a hungry, tired, frightened,
    // downed or egg-bound bird never hoards. Every other animal in the game
    // falls straight through the comp check on the first line.
    public class JobGiver_HoardScrap : ThinkNode_JobGiver
    {
        public override float GetPriority(Pawn pawn)
        {
            if (!Eligible(pawn))
            {
                return 0f;
            }
            // Below RSW_MetalEaterInsert's 9.5 and below vanilla's own
            // hungry-animal food priority: hoarding is what a comfortable bird
            // does instead of wandering, never instead of eating.
            return 5f;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!Eligible(pawn))
            {
                return null;
            }

            CompScrapHoarder comp = pawn.TryGetComp<CompScrapHoarder>();
            ThingDef nestDef = DefDatabase<ThingDef>.GetNamedSilentFail(comp.Props.nestDef);
            if (nestDef == null)
            {
                return null;
            }

            Thing nest = NearestNest(pawn, nestDef, comp.Props.nestSearchRadius);
            if (nest == null)
            {
                // No nest of its own in range. Build one and hoard next think —
                // the same direct-spawn shape JobGiver_EatMetal uses for its
                // dig-when-the-map-is-empty fallback, rather than a whole job
                // for an act that has no animation to show.
                TryBuildNest(pawn, nestDef, comp.Props);
                return null;
            }

            Thing scrap = FindScrap(pawn, comp.Props, nest);
            if (scrap == null)
            {
                return null;
            }

            Job job = JobMaker.MakeJob(RSW_BeastMechanicsDefOf.RSW_HoardScrap, scrap, nest);
            job.count = 1;
            return job;
        }

        // ── gating ───────────────────────────────────────────────────────
        private static bool Eligible(Pawn pawn)
        {
            // This node sits on every animal's think tree: the cheap gates run before the kernel's arguments are gathered.
            if (!RSW_BeastMechanicsSettings.scrapHoardingEnabled || pawn == null || pawn.Map == null || pawn.Dead || pawn.Downed
                || pawn.TryGetComp<CompScrapHoarder>() == null)
            {
                return false;
            }
            Need_Food food = pawn.needs?.food;
            Need_Rest rest = pawn.needs?.rest;
            CompEggLayer eggs = pawn.TryGetComp<CompEggLayer>();
            return RSW_HoardKernel.Eligible(true, true, true,
                pawn.Awake(), pawn.mindState != null && !pawn.mindState.anyCloseHostilesRecently,
                pawn.health?.capacities == null || pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation),
                food != null, food != null ? food.CurLevelPercentage : 0f, food != null ? pawn.RaceProps.FoodLevelPercentageWantEat : 0f,
                rest != null, rest != null ? rest.CurLevelPercentage : 0f, eggs != null && eggs.CanLayNow);
        }

        private static Thing NearestNest(Pawn pawn, ThingDef nestDef, float radius)
        {
            List<Thing> nests = pawn.Map.listerThings.ThingsOfDef(nestDef);
            List<float> dist = new List<float>(nests.Count);
            List<bool> spawned = new List<bool>(nests.Count);
            for (int i = 0; i < nests.Count; i++)
            {
                spawned.Add(nests[i].Spawned);
                dist.Add(nests[i].Spawned ? nests[i].Position.DistanceTo(pawn.Position) : 0f);
            }
            int best = RSW_HoardKernel.NearestNest(dist, spawned, i => pawn.CanReach(nests[i], PathEndMode.Touch, Danger.Deadly), radius);
            return best < 0 ? null : nests[best];
        }

        private static void TryBuildNest(Pawn pawn, ThingDef nestDef, CompProperties_ScrapHoarder props)
        {
            Map map = pawn.Map;
            List<Thing> existing = map.listerThings.ThingsOfDef(nestDef);
            if (!RSW_HoardKernel.CanAddNest(existing.Count, props.maxNestsPerMap))
            {
                return;
            }

            // Prefer a cell beside standing vegetation — the sheet's nests are
            // woven INTO the vine, not dropped on bare crust. Fall back to any
            // legal cell so a bird on open ground is not stuck forever.
            if (!TryFindNestCell(pawn, nestDef, props, requirePlantCover: true, out IntVec3 cell)
                && !TryFindNestCell(pawn, nestDef, props, requirePlantCover: false, out cell))
            {
                return;
            }

            GenSpawn.Spawn(nestDef, cell, map, WipeMode.Vanish);
        }

        private static bool TryFindNestCell(Pawn pawn, ThingDef nestDef, CompProperties_ScrapHoarder props,
            bool requirePlantCover, out IntVec3 result)
        {
            Map map = pawn.Map;
            List<Thing> existing = map.listerThings.ThingsOfDef(nestDef);
            return CellFinder.TryFindRandomCellNear(pawn.Position, map, 8, Validator, out result);

            bool Validator(IntVec3 c)
            {
                // 🔴 Never inside the player's base. Base-stealing is an
                // UNRULED candidate (SCRAPNEST_BIRD_BASE_THEFT_1); a nest
                // appearing in the colony would be that mechanic by accident.
                return RSW_HoardKernel.NestCellOk(c.InBounds(map),
                    () => c.Standable(map) && !c.Fogged(map),
                    () => map.areaManager.Home[c],
                    () => c.GetEdifice(map) != null || c.GetFirstItem(map) != null,
                    () => c.Roofed(map),
                    () => pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly),
                    () =>
                    {
                        float nearest = float.MaxValue;
                        for (int i = 0; i < existing.Count; i++)
                        {
                            nearest = System.Math.Min(nearest, existing[i].Position.DistanceTo(c));
                        }
                        return nearest;
                    },
                    props.minNestSpacing, requirePlantCover,
                    () =>
                    {
                        for (int i = 0; i < GenAdj.AdjacentCells.Length; i++)
                        {
                            IntVec3 adj = c + GenAdj.AdjacentCells[i];
                            if (adj.InBounds(map) && adj.GetPlant(map) != null)
                            {
                                return true;
                            }
                        }
                        return false;
                    });
            }
        }

        // ── finding the scrap ────────────────────────────────────────────
        private static Thing FindScrap(Pawn pawn, CompProperties_ScrapHoarder props, Thing nest)
        {
            if (props.hoardableDefs.NullOrEmpty())
            {
                return null;
            }
            Map map = pawn.Map;
            TraverseParms traverse = TraverseParms.For(pawn, Danger.Some, TraverseMode.ByPawn, false);

            for (int i = 0; i < props.hoardableDefs.Count; i++)
            {
                // A list may legitimately name a def from a mod that is not
                // loaded. That is not an error — same convention as
                // CompMetalEater.customThingToEat.
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(props.hoardableDefs[i]);
                if (def == null)
                {
                    continue;
                }
                Thing found = GenClosest.ClosestThingReachable(
                    pawn.Position, map, ThingRequest.ForDef(def), PathEndMode.ClosestTouch,
                    traverse, props.scrapSearchRadius, t => IsTakeable(t, nest));
                if (found != null)
                {
                    return found;
                }
            }
            return null;
        }

        private static bool IsTakeable(Thing t, Thing nest)
        {
            if (t == null)
            {
                return false;
            }
            Map map = t.Map;
            // 🔴 THE BASE-STEALING GUARD. arid_shrubland.md §4's own text calls
            // birds robbing player bases a CANDIDATE, not a ruled mechanic, so
            // it is not built: anything inside the home area or in any storage
            // is off limits, and there is no setting that relaxes that. Ruling
            // is owed on SCRAPNEST_BIRD_BASE_THEFT_1. (The kernel asks these in
            // order and lazily; "already at the nest" keeps the hoard from being
            // shuffled back and forth.)
            return RSW_HoardKernel.Takeable(t.Spawned, t.stackCount, map != null,
                () => map.areaManager.Home[t.Position],
                () => t.IsInAnyStorage(),
                () => t.Position.GetEdifice(map) is Building_Storage,
                () => t.Position.DistanceTo(nest.Position));
        }
    }
}
