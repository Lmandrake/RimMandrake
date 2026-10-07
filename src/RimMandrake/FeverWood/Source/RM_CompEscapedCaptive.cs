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

        private int nextSearchTick; // transient: throttles the whole-map water scan

        public bool Released => released;

        public void Notify_JustEscaped()
        {
            armed = true;
        }

        /// <summary>FEVERWOOD_BROOD_RANSOM_1: a deliberate release (tank
        /// gizmo or an opened young-cask). Non-hostile; walks for the
        /// nearest water. Distinct from an escape: only a released young
        /// buys a gift.</summary>
        public void Notify_ReleasedToDeep()
        {
            released = true;
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
            }
        }

        /// <summary>A registered pool cell is preferred over any other water
        /// (Fever Wood pools first, the gift's own rule).</summary>
        private static IntVec3 WaterAtOrBeside(IntVec3 pos, Map map)
        {
            IntVec3 other = IntVec3.Invalid;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(pos, map)))
            {
                if (c.InBounds(map) && RM_DeepGift.IsFeverWoodPool(c, map))
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
                if (c.InBounds(map) && c.GetTerrain(map).IsWater)
                {
                    other = c;
                    break;
                }
            }
            return other;
        }

        /// <summary>Nearest reachable standable cell on or beside water,
        /// Fever Wood pools first.</summary>
        private static IntVec3 WalkTarget(Pawn pawn)
        {
            Map map = pawn.Map;
            IntVec3 bestPool = IntVec3.Invalid, bestOther = IntVec3.Invalid;
            float poolD = float.MaxValue, otherD = float.MaxValue;
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = c.GetTerrain(map);
                if (t == null || !t.IsWater)
                {
                    continue;
                }
                float d = (c - pawn.Position).LengthHorizontalSquared;
                if (RM_DeepGift.IsFeverWoodPool(c, map))
                {
                    if (d < poolD) { poolD = d; bestPool = c; }
                }
                else if (d < otherD)
                {
                    otherD = d; bestOther = c;
                }
            }
            IntVec3 target = bestPool.IsValid ? bestPool : bestOther;
            if (!target.IsValid)
            {
                return IntVec3.Invalid;
            }
            if (target.Standable(map) && pawn.CanReach(target, PathEndMode.OnCell, Danger.Deadly))
            {
                return target;
            }
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(target, map)))
            {
                if (c.InBounds(map) && c.Standable(map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    return c;
                }
            }
            return IntVec3.Invalid;
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
                watch.ScheduleDeepGift(water);
                Messages.Message("The young slips into the pool and is gone. Something below has noticed.",
                    new TargetInfo(water, map), MessageTypeDefOf.PositiveEvent);
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
        }
    }
}
