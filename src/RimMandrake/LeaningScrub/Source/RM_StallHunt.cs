using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 1 — the stallhawk rises.
    //
    // "Stall: wind dies, small fauna freeze, stallhawk (RM_Zellik) rises" (item spec); "useless in wind, lethal in the
    // Stall" (bedazzle slate). Waited on the part 6 cover system, which now exists (RM_Ripple.cs):
    //   wind  — small prey on fuzz is hidden (ripple), so vanilla hunting cannot target it: the hawk starves of targets
    //           with no code here.
    //   Stall — every PassInterval ticks each idle wild stall hunter (ThingDef carries RM_StallHunterExtension; RM_Zellik
    //           in this mod) is given a vanilla PredatorHunt job (the JobGiver_GetFood shape: killIncappedTarget) on the
    //           nearest visible wild creature of another kind within SearchRadius and maxPreyBodySize that vanilla's
    //           FoodUtility.IsAcceptablePreyFor also accepts, hungry or not. Only an idle hawk is sent (never a fleeing one).
    //           A creature that holds still in the Stall keeps its ripple cover and cannot be picked.
    // Flight itself is the def's MaxFlightTime stat (vanilla). Never live-tested without the owner (flyer law); the
    // proof reads job state only.
    // Gate: modEnabled && stallHuntEnabled. Numbers PROVISIONAL (RM_StallHuntKernel).
    // ════════════════════════════════════════════════════════════════════
    public class RM_StallHunterExtension : DefModExtension
    {
        public float maxPreyBodySize = 0.65f;
    }

    public class RM_MapComponent_StallHunt : MapComponent
    {
        private readonly List<Pawn> tmpPawns = new List<Pawn>();

        public RM_MapComponent_StallHunt(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % RM_StallHuntKernel.PassInterval != 0 || !RM_WindCalendar.IsStall(map))
            {
                return;
            }
            Pass();
        }

        /// <summary>Send every idle stall hunter after prey. Returns how many hunts were started.</summary>
        public int Pass()
        {
            return Pass(null);
        }

        /// <summary>As Pass(), but only <paramref name="only"/> may hunt when it is given (the proof hook drives
        /// its own spawned hawk without starting hunts for the map's real ones).</summary>
        public int Pass(Pawn only)
        {
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.stallHuntEnabled);
            if (!on || !RM_WindCalendar.IsStall(map))
            {
                return 0;
            }
            int started = 0;
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn hawk = tmpPawns[i];
                if (only != null && hawk != only)
                {
                    continue;
                }
                RM_StallHunterExtension ext = hawk.def.GetModExtension<RM_StallHunterExtension>();
                if (ext == null)
                {
                    continue;
                }
                if (!RM_StallHuntKernel.Hunts(on, true, hawk.Faction == null, hawk.Awake(), hawk.Downed, hawk.InMentalState,
                        hawk.CurJobDef == JobDefOf.PredatorHunt) || !Idle(hawk))
                {
                    continue;
                }
                Pawn prey = FindPrey(hawk, ext);
                if (prey == null)
                {
                    continue;
                }
                Job job = JobMaker.MakeJob(JobDefOf.PredatorHunt, prey);
                job.killIncappedTarget = true;
                hawk.jobs.StartJob(job, JobCondition.InterruptForced);
                started++;
            }
            tmpPawns.Clear();
            return started;
        }

        // Only an idle hawk is sent: never one fleeing, eating, mating or otherwise busy (InterruptForced would cut it).
        private static bool Idle(Pawn hawk)
        {
            JobDef cur = hawk.CurJobDef;
            return cur == null || cur == JobDefOf.Wait_Wander || cur == JobDefOf.GotoWander || cur == JobDefOf.Wait;
        }

        private Pawn FindPrey(Pawn hawk, RM_StallHunterExtension ext)
        {
            Pawn best = null;
            float bestDist = RM_StallHuntKernel.SearchRadius * RM_StallHuntKernel.SearchRadius;
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (p == hawk || !p.Spawned || !p.RaceProps.Animal)
                {
                    continue;
                }
                float d = (p.Position - hawk.Position).LengthHorizontalSquared;
                if (d >= bestDist)
                {
                    continue;
                }
                if (!RM_StallHuntKernel.Prey(p.Faction == null, p.def.GetModExtension<RM_StallHunterExtension>() != null, p.Dead,
                        p.IsPsychologicallyInvisible(), p.BodySize, ext.maxPreyBodySize))
                {
                    continue;
                }
                // Vanilla's own prey test (flesh, canBePredatorPrey, fog, the combat-power check, the race's own
                // maxPreyBodySize): the Stall makes the hawk bold, not suicidal.
                if (!FoodUtility.IsAcceptablePreyFor(hawk, p) || !hawk.CanReach(p, PathEndMode.Touch, Danger.Deadly))
                {
                    continue;
                }
                best = p;
                bestDist = d;
            }
            return best;
        }
    }

    // Proof hook for jawa/static_call (validation.py chain "stall", row stallhawk_hunts_in_the_stall): spawns a stall
    // hunter and a moving-sized prey near it, forces the Stall, drives the SHIPPED pass, reads the hunter's job. No
    // flight is observed (flyer law): job state only. Everything made is removed and the weather restored.
    public static class RM_StallHuntProof
    {
        public static string ProofStallHunt(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            var comp = map.GetComponent<RM_MapComponent_StallHunt>();
            if (comp == null) return "FAIL: RM_MapComponent_StallHunt not on the map";
            PawnKindDef hawkKind = null, preyKind = null;
            foreach (PawnKindDef k in DefDatabase<PawnKindDef>.AllDefsListForReading)
            {
                if (k.race == null || k.RaceProps == null || !k.RaceProps.Animal) continue;
                if (hawkKind == null && k.race.GetModExtension<RM_StallHunterExtension>() != null) hawkKind = k;
                else if (preyKind == null && k.race.race.baseBodySize <= 0.3f && !k.RaceProps.Dryad && !k.RaceProps.predator && k.RaceProps.IsFlesh
                    && k.RaceProps.canBePredatorPrey && k.race.GetModExtension<RM_StallHunterExtension>() == null) preyKind = k;
            }
            if (hawkKind == null || preyKind == null) return "UNMEASURED: no stall hunter or no small prey kind loaded";
            IntVec3 at = CellFinder.RandomClosewalkCellNear(map.Center, map, 20, c => !c.Roofed(map) && c.GetFirstPawn(map) == null);
            if (!at.IsValid) return "UNMEASURED: no open cell near the map centre";
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedHunt = RM_LeaningScrubSettings.stallHuntEnabled, savedRipple = RM_LeaningScrubSettings.rippleEnabled;
            WeatherDef savedWeather = map.weatherManager.curWeather;
            var made = new List<Pawn>();
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.stallHuntEnabled = mode != "off";
                RM_LeaningScrubSettings.rippleEnabled = false; // the prey must be visible; the ripple has its own row
                map.weatherManager.curWeather = RM_LeaningScrubDefOf.RM_Stall;
                Pawn hawk = PawnGenerator.GeneratePawn(hawkKind);
                GenSpawn.Spawn(hawk, at, map);
                made.Add(hawk);
                Pawn prey = PawnGenerator.GeneratePawn(preyKind);
                GenSpawn.Spawn(prey, CellFinder.RandomClosewalkCellNear(at, map, 4), map);
                made.Add(prey);
                if (!hawk.Awake()) return "UNMEASURED: the spawned " + hawkKind.defName + " is asleep";
                int started = comp.Pass(hawk);
                bool hunting = hawk.CurJobDef == JobDefOf.PredatorHunt && hawk.CurJob.targetA.Thing == prey;
                string st = string.Format("hawk={0} prey={1} started={2} hunting={3}", hawkKind.defName, preyKind.defName, started, hunting);
                if (mode == "off") return hunting ? "FAIL: stallHuntEnabled off but the hawk hunted " + st : "PASS off " + st;
                return hunting ? "PASS " + st : "FAIL: a stall hunter beside visible prey did not hunt in the Stall " + st;
            }
            finally
            {
                foreach (Pawn p in made) { if (!p.Destroyed) p.Destroy(); }
                map.weatherManager.curWeather = savedWeather;
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.stallHuntEnabled = savedHunt;
                RM_LeaningScrubSettings.rippleEnabled = savedRipple;
            }
        }
    }
}
