using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_GPT_ENRICHMENT_1 part 2 — the runway bloom.
    //
    // "Canopy disturbance propagates across three floors: crustweevils
    // scatter, fuzzrunners bolt through stem tunnels, ribbonwhips sway,
    // dustflutters erupt, fly ~40 cells and land visibly (real 1.6 flight);
    // visslers shed twitching harvestable arms (RM_VisslerArm). No despawns."
    //
    // Driver: a MapComponent. Every SweepInterval ticks it looks for a
    // DISTURBER — a pawn moving on foot through a cell holding a non-tree
    // plant (the canopy) that is humanlike or at least minDisturberBodySize,
    // and is not itself a bloom species. A bloom then fires at that cell
    // unless another bloom went off nearby within the cooldown.
    //
    // Who answers, and how, is DATA: an RM_RunwayBloomExtension on the
    // animal's race ThingDef. Each response is staged by its own delayTicks,
    // so the floors go off in succession rather than all at once. Nothing is
    // ever despawned: scatterers and bolters run (vanilla Flee job),
    // eruptors run AND take off (RM_Flight.TryLaunch, real flight that lands
    // by itself when MaxFlightTime runs out), shedders drop their shed thing
    // beside them and run.
    //
    // LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1: ribbonwhips SWAY (no flee; held in
    // place and rocked side to side through the vanilla JitterHandler (the
    // same draw offset a hit uses), so no animation def or art is needed;
    // the surrik, the cast's one crust-swimmer, SURFACES: it leaves an exit
    // hole (RM_Filth_SurrikExitHole) where it broke out, then runs.
    // NOT here, a filed follow-up: arms drawing scavengers (which species
    // scavenge, and is an arm food?).
    // ════════════════════════════════════════════════════════════════════

    public enum RM_RunwayBloomResponse
    {
        Scatter,
        Bolt,
        Erupt,
        Shed,
        Sway,
        Surface,
    }

    public class RM_RunwayBloomExtension : DefModExtension
    {
        public RM_RunwayBloomResponse response = RM_RunwayBloomResponse.Scatter;
        // Ticks after the disturbance before this animal answers.
        public int delayTicks;
        // How far it runs (cells). For an eruptor this is the flee target;
        // the flight itself lasts MaxFlightTime.
        public int fleeDistance = 12;
        // Shed response only.
        public ThingDef shedThing;
        public int shedCount = 1;
        public float shedChance = 1f;
        // Sway response only: how long it rocks (ticks).
        public int swayTicks = 180;
        // Surface response only: the mark left where it broke out.
        public ThingDef exitFilth;
    }

    public class RM_MapComponent_RunwayBloom : MapComponent
    {
        // TUNED: once a second is fine-grained enough that a walker cannot
        // cross a bloom radius between sweeps.
        private const int SweepInterval = 60;
        // TUNED: a person, or an animal at least the size of a large dog.
        private const float MinDisturberBodySize = 1.0f;
        // TUNED: a bloom answers within a dozen cells of the disturbance.
        private const float BloomRadius = 12f;
        // TUNED: no second bloom within 15 cells for half an in-game hour, so
        // one walker sets off a wave rather than a strobe.
        private const float CooldownRadius = 15f;
        private const int CooldownTicks = 1250;

        private struct Pending
        {
            public int tick;
            public Pawn pawn;
            public IntVec3 from;
        }

        private struct Recent
        {
            public int tick;
            public IntVec3 cell;
        }

        // Transient: a pending answer lost to a save/load simply never fires,
        // which is indistinguishable from the animal not noticing.
        private readonly List<Pending> pending = new List<Pending>();
        private readonly List<Recent> recent = new List<Recent>();
        private readonly List<Pawn> tmpPawns = new List<Pawn>();
        // Swayers: pawn -> tick the sway ends. Transient, like pending.
        private readonly Dictionary<Pawn, int> swaying = new Dictionary<Pawn, int>();
        private readonly List<Pawn> tmpSway = new List<Pawn>();
        // TUNED: half a swing every 12 ticks; 0.2 cells decays to rest (0.018/tick) just before the next push.
        private const int SwayHalfPeriod = 12;
        private const float SwayDistance = 0.2f;

        public RM_MapComponent_RunwayBloom(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.runwayBloomEnabled))
            {
                pending.Clear();
                swaying.Clear();
                return;
            }
            int now = Find.TickManager.TicksGame;
            RunPending(now);
            TickSway(now);
            if (now % SweepInterval != 0)
            {
                return;
            }
            recent.RemoveAll(r => now - r.tick > CooldownTicks);
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (IsDisturber(p) && !OnCooldown(p.Position))
                {
                    Bloom(p.Position, now);
                }
            }
            tmpPawns.Clear();
        }

        private bool IsDisturber(Pawn p)
        {
            if (!p.Spawned || p.Dead || p.Downed || p.Flying || p.pather == null || !p.pather.Moving)
            {
                return false;
            }
            if (p.def.HasModExtension<RM_RunwayBloomExtension>())
            {
                return false;
            }
            if (!p.RaceProps.Humanlike && p.BodySize < MinDisturberBodySize)
            {
                return false;
            }
            Plant plant = p.Position.GetPlant(map);
            return plant != null && !plant.def.plant.IsTree;
        }

        private bool OnCooldown(IntVec3 c)
        {
            float sq = CooldownRadius * CooldownRadius;
            for (int i = 0; i < recent.Count; i++)
            {
                if ((recent[i].cell - c).LengthHorizontalSquared <= sq)
                {
                    return true;
                }
            }
            return false;
        }

        private void Bloom(IntVec3 center, int now)
        {
            recent.Add(new Recent { tick = now, cell = center });
            float sq = BloomRadius * BloomRadius;
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn a = all[i];
                RM_RunwayBloomExtension ext = a.def.GetModExtension<RM_RunwayBloomExtension>();
                if (ext == null || a.Faction != null || a.Downed || a.Dead
                    || (a.Position - center).LengthHorizontalSquared > sq)
                {
                    continue;
                }
                pending.Add(new Pending { tick = now + Mathf.Max(0, ext.delayTicks), pawn = a, from = center });
            }
        }

        private void RunPending(int now)
        {
            for (int i = pending.Count - 1; i >= 0; i--)
            {
                Pending p = pending[i];
                if (p.tick > now)
                {
                    continue;
                }
                pending.RemoveAt(i);
                Answer(p.pawn, p.from);
            }
        }

        private void Answer(Pawn a, IntVec3 from)
        {
            if (a == null || !a.Spawned || a.Map != map || a.Dead || a.Downed || a.Faction != null)
            {
                return;
            }
            RM_RunwayBloomExtension ext = a.def.GetModExtension<RM_RunwayBloomExtension>();
            if (ext == null)
            {
                return;
            }
            if (ext.response == RM_RunwayBloomResponse.Sway)
            {
                StartSway(a, ext);
                return;
            }
            if (ext.response == RM_RunwayBloomResponse.Surface && ext.exitFilth != null)
            {
                FilthMaker.TryMakeFilth(a.Position, map, ext.exitFilth, 1);
            }
            if (ext.response == RM_RunwayBloomResponse.Shed && ext.shedThing != null && Rand.Chance(ext.shedChance))
            {
                Thing shed = ThingMaker.MakeThing(ext.shedThing);
                shed.stackCount = Mathf.Max(1, ext.shedCount);
                GenPlace.TryPlaceThing(shed, a.Position, map, ThingPlaceMode.Near);
            }
            Job flee = FleeFrom(a, from, ext.fleeDistance);
            if (flee == null)
            {
                return;
            }
            a.jobs.StartJob(flee, JobCondition.InterruptForced);
            if (ext.response == RM_RunwayBloomResponse.Erupt)
            {
                RM_Flight.TryLaunch(a);
            }
        }

        // Pawn_DrawTracker.jitterer is private (RimSage 2026-10-03); read once by reflection, no Harmony needed.
        private static readonly System.Reflection.FieldInfo JitterField = typeof(Pawn_DrawTracker).GetField("jitterer",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);

        private static JitterHandler Jitterer(Pawn p)
        {
            return p?.Drawer == null || JitterField == null ? null : JitterField.GetValue(p.Drawer) as JitterHandler;
        }

        private void StartSway(Pawn a, RM_RunwayBloomExtension ext)
        {
            int ticks = Mathf.Max(SwayHalfPeriod * 2, ext.swayTicks);
            swaying[a] = Find.TickManager.TicksGame + ticks;
            Job hold = JobMaker.MakeJob(JobDefOf.Wait_MaintainPosture);
            hold.expiryInterval = ticks;
            a.jobs.StartJob(hold, JobCondition.InterruptForced);
        }

        private void TickSway(int now)
        {
            if (swaying.Count == 0 || now % SwayHalfPeriod != 0)
            {
                return;
            }
            tmpSway.Clear();
            tmpSway.AddRange(swaying.Keys);
            for (int i = 0; i < tmpSway.Count; i++)
            {
                Pawn p = tmpSway[i];
                if (p == null || !p.Spawned || p.Map != map || p.Dead || now >= swaying[p])
                {
                    swaying.Remove(p);
                    continue;
                }
                // Alternate east and west: the ribbon leans one way, then the other.
                Jitterer(p)?.AddOffset(SwayDistance, (now / SwayHalfPeriod) % 2 == 0 ? 90f : 270f);
            }
            tmpSway.Clear();
        }

        /// <summary>Bridge proof (jawa/static_call "current"): fires a bloom at the first answering animal's cell and
        /// reports what answered after delays run: "SWAYING 1 HOLES +1 ANSWERED 4". Needs bloom animals on the map.</summary>
        public static string ProofVisuals(Map map)
        {
            var comp = map?.GetComponent<RM_MapComponent_RunwayBloom>();
            if (comp == null)
            {
                return "REFUSED: no runway bloom component";
            }
            ThingDef hole = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_SurrikExitHole");
            int holesBefore = hole == null ? 0 : map.listerThings.ThingsOfDef(hole).Count;
            Pawn first = null;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def.HasModExtension<RM_RunwayBloomExtension>() && p.Faction == null)
                {
                    first = p;
                    break;
                }
            }
            if (first == null)
            {
                return "REFUSED: no wild bloom animal on the map (spawn a ribbonwhip and a surrik)";
            }
            int now = Find.TickManager.TicksGame;
            comp.Bloom(first.Position, now);
            int answered = comp.pending.Count;
            comp.RunPending(now + 1000);
            int holesAfter = hole == null ? 0 : map.listerThings.ThingsOfDef(hole).Count;
            return "SWAYING " + comp.swaying.Count + " HOLES +" + (holesAfter - holesBefore) + " ANSWERED " + answered;
        }

        private Job FleeFrom(Pawn a, IntVec3 from, int distance)
        {
            if (a.CurJob != null && a.CurJob.def == JobDefOf.Flee)
            {
                return null; // already running; leave it be
            }
            // CellFinderLoose.GetFleeDest wants threat Things; the disturbance
            // is a cell, so pick directly: RCellFinder.TryFindDirectFleeDestination
            // takes the root to flee FROM.
            if (!RCellFinder.TryFindDirectFleeDestination(from, distance, a, out IntVec3 dest) || dest == a.Position)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(JobDefOf.Flee, dest);
            job.locomotionUrgency = LocomotionUrgency.Sprint;
            return job;
        }
    }
}
