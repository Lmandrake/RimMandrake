using System.Collections.Generic;
using RimWorld;
using Verse.AI;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. Per-pawn comp on RM_Sekkulaath_Juvenile
    // (and, once the Star Wars swap patch retargets the occupant, on
    // RSW_Dianoga too — this comp is added generically via <comps> on
    // whichever race is actually spawned, not hardcoded to one defName).
    //
    // §6m's escape ladder, read from the pawn's side:
    //   stage 1 — TOUGH, water-seeking, hostile: delivered on the RACE
    //             (Wildness/manhunterOnDamageChance/waterSeeker in the
    //             ThingDef), nothing to do here.
    //   stage 2 — "if it reaches a pool it establishes": THIS class's job.
    //             Only armed after an actual tank escape (Notify_JustEscaped)
    //             — a wild-born or successfully tamed Sekkulaath must not
    //             "install" just for standing in water it always lived near.
    //   stage 3 — "left alone in water it can mature into the real thing":
    //             explicitly UNSET duration/interruptibility (item's own
    //             `open` list) — NOT built. What ships instead: reaching a
    //             pool immediately calls Notify_SekkulaathInstalled(),
    //             which un-sets any prior "permanently killed on this map"
    //             flag on RM_MapComponent_TentacleWatch, i.e. the ambient
    //             elder-being system is guaranteed live on this map again.
    //             That is a real, honest reading of "you will have created
    //             the biome's worst threat yourself" without inventing a
    //             maturation timer the owner never gave. A true staged
    //             maturation (small horror -> full elder being, on a clock)
    //             is deferred to FEVERWOOD_DIANOGA_TANK_TUNING_1.
    public class RM_CompEscapedCaptive : ThingComp
    {
        private const int CheckIntervalTicks = 60; // frequent enough to catch a fast dash to water

        private bool armed;
        private bool released; // FEVERWOOD_BROOD_RANSOM_1: let go on purpose, walking home
        private int giftRolls = 1; // a display tank's young (Sporefall's) buys the doubled "greatest gift"

        private int nextSearchTick; // transient: throttles the whole-map water scan

        public bool Released => released;
        public int GiftRolls => giftRolls;

        public void Notify_JustEscaped()
        {
            armed = true;
        }

        /// <summary>FEVERWOOD_BROOD_RANSOM_1: a deliberate release (tank
        /// gizmo or an opened young-cask). Non-hostile; walks for the
        /// nearest water. Distinct from an escape: only a released young
        /// buys a gift.</summary>
        public void Notify_ReleasedToDeep(int rolls = 1)
        {
            released = true;
            giftRolls = UnityEngine.Mathf.Max(1, rolls);
            armed = false;
        }

        public override void CompTick()
        {
            base.CompTick();
            if (released)
            {
                TickReleased();
                return;
            }
            if (!armed)
            {
                return;
            }

            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Dead)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (pawn.Faction != null)
            {
                armed = false; // tamed or claimed before it reached water: a tamed one must not install (header, stage 2)
                return;
            }

            RUT_MapComponent_TheTenant tenant = pawn.Map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null || !tenant.IsRegisteredWater(pawn.Position))
            {
                return;
            }

            Install(pawn);
        }

        private void Install(Pawn pawn)
        {
            armed = false;
            Map map = pawn.Map;
            IntVec3 pos = pawn.Position;

            map.GetComponent<RM_MapComponent_TentacleWatch>()?.Notify_SekkulaathInstalled();

            Messages.Message(
                "The escaped creature has reached the water and settled in — the pools have gained a new tenant.",
                new TargetInfo(pos, map), MessageTypeDefOf.ThreatBig);

            if (pawn.Spawned)
            {
                pawn.DeSpawn(DestroyMode.Vanish);
            }
        }

        private void TickReleased()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Dead)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (pawn.Faction != null)
            {
                released = false; // tamed or claimed on the way: it is someone's animal now, not going home
                return;
            }
            Map map = pawn.Map;
            IntVec3 water = WaterAtOrBeside(pawn.Position, map);
            if (water.IsValid)
            {
                ArriveReleased(pawn, water);
                return;
            }
            if (pawn.CurJobDef == JobDefOf.Goto)
            {
                return;
            }
            if (Find.TickManager.TicksGame < nextSearchTick)
            {
                return;
            }
            IntVec3 dest = WalkTarget(pawn);
            if (!dest.IsValid)
            {
                nextSearchTick = Find.TickManager.TicksGame + 2500; // no reachable water: look again in an hour
            }
            else
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(job, JobCondition.InterruptForced);
                nextSearchTick = Find.TickManager.TicksGame + 600; // FEVERWOOD_WATER_TOPOLOGY_SERVICE_1: no re-scan every check
            }
        }

        /// <summary>A registered pool cell is preferred over any other water
        /// (Fever Wood pools first, the gift's own rule).</summary>
        private static IntVec3 WaterAtOrBeside(IntVec3 pos, Map map)
        {
            IntVec3 other = IntVec3.Invalid;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(pos, map)))
            {
                if (c.InBounds(map) && Touches(pos, c, map) && RM_DeepGift.IsFeverWoodPool(c, map))
                {
                    return c;
                }
            }
            if (RM_DeepGift.IsFeverWoodPool(pos, map))
            {
                return pos;
            }
            if (pos.GetTerrain(map).IsWater)
            {
                return pos;
            }
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(pos, map)))
            {
                if (c.InBounds(map) && Touches(pos, c, map) && c.GetTerrain(map).IsWater)
                {
                    other = c;
                    break;
                }
            }
            return other;
        }

        /// <summary>FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 (#10): a diagonal neighbour only counts when the corner is
        /// open, the same rule a pawn's own diagonal step obeys, so it never "arrives" at water through a wall.</summary>
        private static bool Touches(IntVec3 from, IntVec3 to, Map map)
        {
            if (from.x == to.x || from.z == to.z)
            {
                return true;
            }
            return new IntVec3(to.x, 0, from.z).Walkable(map) && new IntVec3(from.x, 0, to.z).Walkable(map);
        }

        private const int MaxWalkCandidates = 24;
        private const int MaxFloodCells = 4000;

        /// <summary>Nearest reachable standable cell on or beside water, Fever Wood pools first.
        /// FEVERWOOD_WATER_TOPOLOGY_SERVICE_1: when the nearest body of water is enclosed, its whole connected
        /// water is ruled out and the next-nearest BODY is tried, instead of stranding the creature on one pick.</summary>
        private static IntVec3 WalkTarget(Pawn pawn)
        {
            Map map = pawn.Map;
            var pools = new List<IntVec3>();
            var others = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = c.GetTerrain(map);
                if (t == null || !t.IsWater)
                {
                    continue;
                }
                (RM_DeepGift.IsFeverWoodPool(c, map) ? pools : others).Add(c);
            }
            IntVec3 from = pawn.Position;
            foreach (List<IntVec3> list in new[] { pools, others })
            {
                list.Sort((a, b) => (a - from).LengthHorizontalSquared.CompareTo((b - from).LengthHorizontalSquared));
                var ruledOut = new HashSet<IntVec3>();
                int tried = 0;
                for (int i = 0; i < list.Count && tried < MaxWalkCandidates; i++)
                {
                    IntVec3 target = list[i];
                    if (ruledOut.Contains(target))
                    {
                        continue;
                    }
                    tried++;
                    if (target.Standable(map) && pawn.CanReach(target, PathEndMode.OnCell, Danger.Deadly))
                    {
                        return target;
                    }
                    foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(target, map)))
                    {
                        if (c.InBounds(map) && c.Standable(map) && Touches(c, target, map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                        {
                            return c;
                        }
                    }
                    FloodWater(target, map, ruledOut); // this body is enclosed from here: skip the rest of it
                }
            }
            return IntVec3.Invalid;
        }

        private static void FloodWater(IntVec3 start, Map map, HashSet<IntVec3> into)
        {
            var queue = new Queue<IntVec3>();
            if (into.Add(start))
            {
                queue.Enqueue(start);
            }
            while (queue.Count > 0 && into.Count < MaxFloodCells)
            {
                IntVec3 c = queue.Dequeue();
                for (int d = 0; d < 4; d++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[d];
                    if (n.InBounds(map) && n.GetTerrain(map)?.IsWater == true && into.Add(n))
                    {
                        queue.Enqueue(n);
                    }
                }
            }
        }

        private void ArriveReleased(Pawn pawn, IntVec3 water)
        {
            released = false;
            Map map = pawn.Map;
            bool home = RM_DeepGift.IsFeverWoodPool(water, map);
            RM_MapComponent_TentacleWatch watch = map.GetComponent<RM_MapComponent_TentacleWatch>();
            if (home && RM_FeverWoodSettings.broodRansomEnabled && watch != null)
            {
                watch.Notify_SekkulaathInstalled();
                watch.ScheduleDeepGift(water, giftRolls);
                Messages.Message("The young slips into the pool and is gone. Something below has noticed.",
                    new TargetInfo(water, map), MessageTypeDefOf.PositiveEvent);
                string returned = RM_CompProperties_DeepYoungLines.ForCask()?.returnedLine;
                if (!returned.NullOrEmpty())
                {
                    Messages.Message(returned, new TargetInfo(water, map), MessageTypeDefOf.NeutralEvent);
                }
            }
            else
            {
                Messages.Message("The young slips into the water and settles in. This is not the deep's water; nothing answers.",
                    new TargetInfo(water, map), MessageTypeDefOf.NeutralEvent);
            }
            if (pawn.Spawned)
            {
                pawn.DeSpawn(DestroyMode.Vanish);
            }
            RM_WorldComponent_DeepYoung.Get?.Recompute();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref armed, "armed", false);
            Scribe_Values.Look(ref released, "released", false);
            Scribe_Values.Look(ref giftRolls, "giftRolls", 1);
        }
    }
}
