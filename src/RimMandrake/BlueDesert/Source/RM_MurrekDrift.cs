// BLUEDESERT_MECHANICS_BUILD_1 §6 — murrek drift re-seeding.
//
// "After each drift storm, buried murrek re-seed at fresh drift cells; drifts
// near the colony are a clearable threat (dig the drift, flush the thing)."
// (bluedesert_bedazzle_review_2026-09-28.md §4 G, ruled 2026-09-28.)
//
// Three pieces:
//  - RM_MapComponent_MurrekDrifts watches the map's weather. When
//    RM_IceSandDrift gives way to anything else on an RM_BlueDesert map, it
//    sends every idle wild murrek on the map to the nearest deep drift and,
//    if the wild-animal ecosystem has room, seeds a few new murrek already
//    buried in drifts away from the colony. Tuning is XML, on the drift
//    WeatherDef's RM_MurrekReseedExtension.
//  - RM_JobDriver_MurrekBurrow is the burrow/unburrow job: walk to the drift
//    cell, dig in, then lie buried (RM_MurrekBuried hediff = vanilla
//    HediffComp_Invisibility, so the player cannot see or target it) until
//    prey comes within ambushRadius (it erupts into a vanilla PredatorHunt),
//    the drift under it is dug out or erodes below flushDepth (it surfaces),
//    it is hurt, it gets hungry or tired, or it has waited maxBuriedTicks.
//    Every exit path runs one finish action that makes it visible again.
//  - "Dig the drift" is vanilla: the Clear snow/sand area's
//    JobDriver_ClearSnowAndSand sets the cell's sand depth to 0, which the
//    buried murrek reads as being flushed; the digger standing next to it is
//    inside ambushRadius, so digging out a murrek means fighting it on the
//    colony's terms.
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-29):
//  - Odyssey sand is Map.sandGrid (SandGrid.GetDepth, 0..1). A drift weather
//    adds depth via SteadyEnvironmentEffects.AddFallenSandAt while its
//    sandRate > 0.001; otherwise every unroofed outdoor cell erodes by 1/180
//    per steady pass. So "fresh drift cells" right after the storm are the
//    deep ones, and they wear away on their own over the following days.
//  - HediffComp_Invisibility (visibleToPlayer false) drives
//    Pawn.IsHiddenFromPlayer / IsPsychologicallyInvisible; FoodUtility.
//    IsAcceptablePreyFor refuses hidden prey, so nothing hunts a buried
//    murrek either. Needs Royalty or Anomaly (ModLister.CheckRoyaltyOrAnomaly)
//    — every DLC is assumed present (owner ruling 2026-09-26).
//  - JobDriver.DriverTick runs every tick and calls Toil.tickAction; the lie
//    toil throttles itself with IsHashIntervalTick.
//  - WildAnimalSpawner.AnimalEcosystemFull gates the top-up spawn, so the
//    re-seed never pushes the map past the biome's own animal density.
//
// Gates: RM_BlueDesertSettings.masterEnabled && murrekReseedEnabled, and the
// map's biome must be RM_BlueDesert. Off: storms end with nothing re-seeded,
// and any murrek already buried surfaces at its next check.

using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.BlueDesert
{
    /// <summary>Tuning for murrek re-seeding, carried on the drift WeatherDef
    /// (RM_IceSandDrift). All figures are this build's INVENTED tuning.</summary>
    public class RM_MurrekReseedExtension : DefModExtension
    {
        public PawnKindDef murrekKind;
        public JobDef burrowJob;
        public HediffDef buriedHediff;

        /// <summary>Minimum sand depth (0..1) for a cell to count as a drift a
        /// murrek can bury in.</summary>
        public float minDriftDepth = 0.5f;
        /// <summary>A buried murrek whose cell falls below this depth (dug out
        /// or eroded) surfaces.</summary>
        public float flushDepth = 0.25f;
        /// <summary>How far an existing murrek will travel to re-bury.</summary>
        public float burrowSearchRadius = 40f;
        /// <summary>Cells of separation kept between two buried murrek.</summary>
        public float minSpacing = 6f;
        /// <summary>New murrek seeded buried per storm end, if the ecosystem has
        /// room.</summary>
        public IntRange newPerStorm = new IntRange(0, 2);
        /// <summary>No top-up once this many murrek live on the map.</summary>
        public int maxMurrekOnMap = 6;
        /// <summary>A new murrek is never seeded within this many cells of a
        /// player pawn, nor inside the home area.</summary>
        public float spawnClearanceFromColony = 18f;
        /// <summary>Radius within which acceptable prey triggers the ambush.</summary>
        public float ambushRadius = 2.9f;
        public int burrowTicks = 180;
        public int maxBuriedTicks = 120000;
        /// <summary>One-shot played where a buried murrek breaks the surface
        /// (ambush, flush or damage). Vanilla clip by the 2026-10-03 audio
        /// ruling; null = silent.</summary>
        public SoundDef eruptSound;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (murrekKind == null)
            {
                yield return "RM_MurrekReseedExtension.murrekKind is null.";
            }
            if (burrowJob == null)
            {
                yield return "RM_MurrekReseedExtension.burrowJob is null.";
            }
            if (buriedHediff == null)
            {
                yield return "RM_MurrekReseedExtension.buriedHediff is null.";
            }
            if (flushDepth >= minDriftDepth)
            {
                yield return "RM_MurrekReseedExtension.flushDepth must be below minDriftDepth, or a murrek surfaces the moment it buries.";
            }
        }
    }

    public static class RM_MurrekDrift
    {
        public const string DriftWeatherDefName = "RM_IceSandDrift";
        public const string BiomeDefName = "RM_BlueDesert";

        private static WeatherDef driftWeather;
        private static BiomeDef biome;
        private static bool resolved;

        private static void Resolve()
        {
            if (resolved)
            {
                return;
            }
            resolved = true;
            driftWeather = DefDatabase<WeatherDef>.GetNamedSilentFail(DriftWeatherDefName);
            biome = DefDatabase<BiomeDef>.GetNamedSilentFail(BiomeDefName);
        }

        public static WeatherDef DriftWeather
        {
            get { Resolve(); return driftWeather; }
        }

        public static RM_MurrekReseedExtension Props => DriftWeather?.GetModExtension<RM_MurrekReseedExtension>();

        public static bool Enabled => RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.murrekReseedEnabled;

        public static bool IsBlueDesert(Map map)
        {
            Resolve();
            return map != null && biome != null && map.Biome == biome;
        }

        public static bool IsBuried(Pawn pawn, RM_MurrekReseedExtension props)
        {
            return props?.buriedHediff != null && pawn.health?.hediffSet?.HasHediff(props.buriedHediff) == true;
        }

        public static void Bury(Pawn pawn, RM_MurrekReseedExtension props)
        {
            if (props?.buriedHediff == null || IsBuried(pawn, props))
            {
                return;
            }
            pawn.health.AddHediff(props.buriedHediff);
        }

        public static void Unbury(Pawn pawn, RM_MurrekReseedExtension props)
        {
            if (props?.buriedHediff == null || pawn?.health?.hediffSet == null)
            {
                return;
            }
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(props.buriedHediff);
            if (h == null)
            {
                return;
            }
            h.TryGetComp<HediffComp_Invisibility>()?.BecomeVisible(instant: true);
            pawn.health.RemoveHediff(h);
            if (pawn.Spawned)
            {
                FleckMaker.ThrowDustPuffThick(pawn.DrawPos, pawn.Map, 2.2f, new Color(0.82f, 0.88f, 0.96f));
                props.eruptSound?.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            }
        }
    }

    public class RM_JobDriver_MurrekBurrow : JobDriver
    {
        private int buriedSinceTick = -1;

        private RM_MurrekReseedExtension Props => RM_MurrekDrift.Props;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref buriedSinceTick, "rmBuriedSinceTick", -1);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        public override void Notify_DamageTaken(DamageInfo dinfo)
        {
            base.Notify_DamageTaken(dinfo);
            EndJobWith(JobCondition.InterruptForced);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            AddFinishAction(delegate
            {
                RM_MurrekDrift.Unbury(pawn, Props);
            });

            Toil goTo = Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            goTo.FailOn(() => !RM_MurrekDrift.Enabled);
            goTo.FailOn(() => Map.sandGrid == null || Map.sandGrid.GetDepth(TargetLocA) < (Props?.flushDepth ?? 0f));
            yield return goTo;

            Toil dig = ToilMaker.MakeToil("RM_MurrekDigIn");
            dig.defaultCompleteMode = ToilCompleteMode.Delay;
            dig.defaultDuration = Props?.burrowTicks ?? 180;
            dig.WithEffect(EffecterDefOf.ClearSand, TargetIndex.A);
            dig.initAction = delegate
            {
                // A murrek seeded already buried skips the dig.
                if (RM_MurrekDrift.IsBuried(pawn, Props))
                {
                    ReadyForNextToil();
                }
            };
            yield return dig;

            Toil lie = ToilMaker.MakeToil("RM_MurrekLieBuried");
            lie.defaultCompleteMode = ToilCompleteMode.Never;
            lie.initAction = delegate
            {
                RM_MurrekDrift.Bury(pawn, Props);
                if (buriedSinceTick < 0)
                {
                    buriedSinceTick = Find.TickManager.TicksGame;
                }
                pawn.pather?.StopDead();
            };
            lie.tickAction = delegate
            {
                if (!pawn.IsHashIntervalTick(30))
                {
                    return;
                }
                LieBuriedCheck();
            };
            yield return lie;
        }

        private void LieBuriedCheck()
        {
            RM_MurrekReseedExtension props = Props;
            if (props == null || !RM_MurrekDrift.Enabled)
            {
                EndJobWith(JobCondition.Incompletable);
                return;
            }
            Map map = pawn.Map;
            if (map?.sandGrid == null || map.sandGrid.GetDepth(pawn.Position) < props.flushDepth)
            {
                // Dug out, or the drift wore away: it surfaces.
                EndJobWith(JobCondition.Incompletable);
                return;
            }
            if (Find.TickManager.TicksGame - buriedSinceTick > props.maxBuriedTicks)
            {
                EndJobWith(JobCondition.Succeeded);
                return;
            }
            if (pawn.needs?.food != null && pawn.needs.food.CurCategory >= HungerCategory.UrgentlyHungry)
            {
                EndJobWith(JobCondition.Succeeded);
                return;
            }
            if (pawn.needs?.rest != null && pawn.needs.rest.CurCategory >= RestCategory.VeryTired)
            {
                EndJobWith(JobCondition.Succeeded);
                return;
            }
            Pawn prey = FindAmbushPrey(map, props.ambushRadius);
            if (prey != null)
            {
                RM_MurrekDrift.Unbury(pawn, props);
                Job hunt = JobMaker.MakeJob(JobDefOf.PredatorHunt, prey);
                hunt.killIncappedTarget = true;
                pawn.jobs.StartJob(hunt, JobCondition.InterruptForced);
            }
        }

        private Pawn FindAmbushPrey(Map map, float radius)
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestDist = float.MaxValue;
            float radiusSq = radius * radius;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == pawn || p.Dead)
                {
                    continue;
                }
                float d = (p.Position - pawn.Position).LengthHorizontalSquared;
                if (d > radiusSq || d >= bestDist)
                {
                    continue;
                }
                if (!FoodUtility.IsAcceptablePreyFor(pawn, p))
                {
                    continue;
                }
                best = p;
                bestDist = d;
            }
            return best;
        }
    }

    public class RM_MapComponent_MurrekDrifts : MapComponent
    {
        private bool driftWasActive;

        public RM_MapComponent_MurrekDrifts(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref driftWasActive, "driftWasActive", false);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            if (!RM_MurrekDrift.IsBlueDesert(map))
            {
                return;
            }
            WeatherDef drift = RM_MurrekDrift.DriftWeather;
            bool driftActive = drift != null && map.weatherManager.curWeather == drift;
            bool ended = driftWasActive && !driftActive;
            driftWasActive = driftActive;
            if (ended && RM_MurrekDrift.Enabled)
            {
                Reseed();
            }
        }

        /// <summary>Public so a debug action or bridge tool can drive it
        /// without waiting for a storm.</summary>
        public void Reseed()
        {
            RM_MurrekReseedExtension props = RM_MurrekDrift.Props;
            if (props?.murrekKind == null || props.burrowJob == null || map.sandGrid == null)
            {
                return;
            }

            List<IntVec3> drifts = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (map.sandGrid.GetDepth(c) >= props.minDriftDepth && c.Standable(map) && !c.Roofed(map))
                {
                    drifts.Add(c);
                }
            }
            if (drifts.Count == 0)
            {
                return;
            }

            List<IntVec3> taken = new List<IntVec3>();
            List<Pawn> murrek = map.mapPawns.AllPawnsSpawned
                .Where(p => p.kindDef == props.murrekKind || p.def == props.murrekKind.race)
                .ToList();

            // Buried murrek already hold their cells.
            foreach (Pawn m in murrek)
            {
                if (m.CurJobDef == props.burrowJob)
                {
                    taken.Add(m.CurJob.targetA.Cell);
                }
            }

            // 1. Existing idle wild murrek re-bury in the nearest fresh drift.
            foreach (Pawn m in murrek)
            {
                if (m.Faction != null || m.Downed || m.InMentalState || m.CurJobDef == props.burrowJob
                    || m.CurJobDef == JobDefOf.PredatorHunt || m.CurJobDef == JobDefOf.Ingest
                    || m.CurJobDef == JobDefOf.LayDown)
                {
                    continue;
                }
                if (m.needs?.food != null && m.needs.food.CurCategory >= HungerCategory.UrgentlyHungry)
                {
                    continue;
                }
                float maxSq = props.burrowSearchRadius * props.burrowSearchRadius;
                IntVec3 from = m.Position;
                IEnumerable<IntVec3> near = drifts
                    .Where(c => (c - from).LengthHorizontalSquared <= maxSq && Clear(c, taken, props.minSpacing))
                    .OrderBy(c => (c - from).LengthHorizontalSquared)
                    .Take(12);
                foreach (IntVec3 c in near)
                {
                    if (!m.CanReach(c, PathEndMode.OnCell, Danger.Some))
                    {
                        continue;
                    }
                    taken.Add(c);
                    m.jobs.StartJob(JobMaker.MakeJob(props.burrowJob, c), JobCondition.InterruptForced);
                    break;
                }
            }

            // 2. Top-up: seed new murrek already buried, away from the colony,
            //    only while the biome's own animal density has room.
            int toSpawn = props.newPerStorm.RandomInRange;
            int room = props.maxMurrekOnMap - murrek.Count;
            toSpawn = Mathf.Min(toSpawn, room);
            if (toSpawn <= 0 || map.wildAnimalSpawner.AnimalEcosystemFull)
            {
                return;
            }
            float clearSq = props.spawnClearanceFromColony * props.spawnClearanceFromColony;
            List<Pawn> colonists = map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer);
            Area_Home home = map.areaManager.Home;
            List<IntVec3> spawnable = drifts
                .Where(c => !c.Fogged(map)
                    && (home == null || !home[c])
                    && !colonists.Any(p => (p.Position - c).LengthHorizontalSquared < clearSq))
                .InRandomOrder()
                .ToList();
            foreach (IntVec3 c in spawnable)
            {
                if (toSpawn <= 0)
                {
                    break;
                }
                if (!Clear(c, taken, props.minSpacing))
                {
                    continue;
                }
                Pawn m = PawnGenerator.GeneratePawn(props.murrekKind, null);
                GenSpawn.Spawn(m, c, map);
                RM_MurrekDrift.Bury(m, props);
                m.jobs.StartJob(JobMaker.MakeJob(props.burrowJob, c), JobCondition.InterruptForced);
                taken.Add(c);
                toSpawn--;
            }
        }

        private static bool Clear(IntVec3 c, List<IntVec3> taken, float spacing)
        {
            float sq = spacing * spacing;
            for (int i = 0; i < taken.Count; i++)
            {
                if ((taken[i] - c).LengthHorizontalSquared < sq)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
