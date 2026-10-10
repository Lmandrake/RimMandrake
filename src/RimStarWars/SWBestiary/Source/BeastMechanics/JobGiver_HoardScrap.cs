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

            // SCRAPNEST_BIRD_BASE_THEFT_1: a raiding-flock bird flies its loot to ANY nest on the map, however far — it arrived at
            // the colony's edge and has no nest of its own nearby, and the loot must end up somewhere findable.
            bool raiding = RSW_ScrapThiefFlock.IsRaiding(pawn);
            Thing nest = NearestNest(pawn, nestDef, raiding ? float.MaxValue : comp.Props.nestSearchRadius);
            if (nest == null)
            {
                // No nest of its own in range. Build one and hoard next think —
                // the same direct-spawn shape JobGiver_EatMetal uses for its
                // dig-when-the-map-is-empty fallback, rather than a whole job
                // for an act that has no animation to show.
                TryBuildNest(pawn, nestDef, comp.Props);
                return null;
            }

            Thing scrap = FindScrap(pawn, comp.Props, nest, StealsFromBase(pawn, raiding));
            if (scrap == null)
            {
                return null;
            }

            Job job = JobMaker.MakeJob(RSW_BeastMechanicsDefOf.RSW_HoardScrap, scrap, nest);
            job.count = 1;
            return job;
        }

        // ── gating ───────────────────────────────────────────────────────
        // SCRAPNEST_BIRD_BASE_THEFT_1 (owner, 2026-10-10: "Yes they steal everything, and there are also stealing raids."):
        // ambient birds rob stockpiles and the home area when scrapBirdBaseTheftEnabled is on; a bird in a live raiding flock
        // (IncidentWorker_ScrapThiefFlock) always does, whatever that toggle says, because the raid IS the event.
        private static bool StealsFromBase(Pawn pawn, bool raiding)
        {
            return raiding || RSW_BeastMechanicsSettings.scrapBirdBaseTheftEnabled;
        }

        private static bool Eligible(Pawn pawn)
        {
            // This node sits on every animal's think tree: the cheap gates run before the kernel's arguments are gathered.
            if (!RSW_BeastMechanicsSettings.scrapHoardingEnabled || pawn == null || pawn.Map == null || pawn.Dead || pawn.Downed
                || pawn.TryGetComp<CompScrapHoarder>() == null)
            {
                return false;
            }
            // A raiding-flock bird whose time is up stops hoarding so vanilla's ExitTimedOut node walks it off the map.
            if (pawn.mindState != null && RSW_HoardKernel.RaidOver(pawn.mindState.exitMapAfterTick, Find.TickManager.TicksGame))
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
            // The wide last try is for a bird standing inside or beside a colony (a base thief): every cell within 8 may be home area,
            // and the nest must still land OUTSIDE it.
            if (!TryFindNestCell(pawn, nestDef, props, requirePlantCover: true, 8, out IntVec3 cell)
                && !TryFindNestCell(pawn, nestDef, props, requirePlantCover: false, 8, out cell)
                && !TryFindNestCell(pawn, nestDef, props, requirePlantCover: false, 30, out cell))
            {
                return;
            }

            GenSpawn.Spawn(nestDef, cell, map, WipeMode.Vanish);
        }

        private static bool TryFindNestCell(Pawn pawn, ThingDef nestDef, CompProperties_ScrapHoarder props,
            bool requirePlantCover, int radius, out IntVec3 result)
        {
            Map map = pawn.Map;
            List<Thing> existing = map.listerThings.ThingsOfDef(nestDef);
            return CellFinder.TryFindRandomCellNear(pawn.Position, map, radius, Validator, out result);

            bool Validator(IntVec3 c)
            {
                // 🔴 Never inside the player's base, even now that the birds
                // steal from it (SCRAPNEST_BIRD_BASE_THEFT_1): they rob the
                // colony and nest OUTSIDE it, so the loot stays recoverable.
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
        private static Thing FindScrap(Pawn pawn, CompProperties_ScrapHoarder props, Thing nest, bool stealFromBase)
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
                    traverse, props.scrapSearchRadius, t => IsTakeable(t, nest, stealFromBase));
                if (found != null)
                {
                    return found;
                }
            }
            return null;
        }

        private static bool IsTakeable(Thing t, Thing nest, bool stealFromBase)
        {
            if (t == null)
            {
                return false;
            }
            Map map = t.Map;
            // THE BASE-STEALING GUARD, now switchable: SCRAPNEST_BIRD_BASE_THEFT_1
            // was ruled by the owner (2026-09-21 and 2026-10-10) — the birds
            // steal from stockpiles and the home area too. Without
            // stealFromBase, anything inside the home area or in any storage
            // is off limits as before. (The kernel asks these in order and
            // lazily; "already at the nest" keeps the hoard from being
            // shuffled back and forth.)
            return RSW_HoardKernel.Takeable(t.Spawned, t.stackCount, map != null, stealFromBase,
                () => map.areaManager.Home[t.Position],
                () => t.IsInAnyStorage(),
                () => t.Position.GetEdifice(map) is Building_Storage,
                () => t.Position.DistanceTo(nest.Position));
        }
    }
}
