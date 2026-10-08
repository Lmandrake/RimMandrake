using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_GPT_ENRICHMENT_1 §1 — the ship becomes a refuge (Shipfall
    // Commons). Picked by the owner's card, 2026-09-30. The item's spec:
    //   "After landing, the shade grid sees the gravship's large roofed
    //    footprint and runs an escalation ladder: small animals take the ramp
    //    shadow, herds press the hull, pirrik circle, eventually the gloomcast
    //    walks over. Launch is never blocked; occupants get a readable
    //    dispersal job."
    //
    // No new shade is invented: the ship's hull already throws shade into
    // RM_MapComponent_ShadeGrid like any wall. What this adds is WHO goes
    // there, and when. The ladder's rungs are data on the biome
    // (RM_ShipfallCommonsExtension, RM_LongShade.xml): each rung opens after
    // a delay since the ship arrived and admits a class of wild animal (by
    // body size, by herd, or by named race). An admitted animal is pulled to
    // a shaded cell round the hull — by a dash, keeping the Long Shade's
    // rest-dash-rest law, or (for a rung marked walk: the giant, the fliers)
    // at a walk — and, once there, mostly stays.
    //
    // The commons is OFF the ship: shaded, standable cells within `radius` of
    // the substructure, never on it, so nothing wild ever stands on the deck
    // and rides away. When a colonist takes the pilot's console, every wild
    // animal in the commons gets a flee job away from the engine and the
    // player gets one message — the launch itself is never touched.
    //
    // Settings: Long Shade Mod Settings, "Shipfall Commons".
    // Every number on the extension is TUNED (no ruling gives one).
    // ════════════════════════════════════════════════════════════════════
    public class RM_ShipfallStage
    {
        /// <summary>Game hours after the ship arrived before this rung opens.</summary>
        public float afterHours;

        /// <summary>Admits wild animals no bigger than this (0 = no size rule).</summary>
        public float maxBodySize;

        /// <summary>Admits only herd animals.</summary>
        public bool herdOnly;

        /// <summary>Admits only these races (empty = no race rule).</summary>
        public List<ThingDef> races = new List<ThingDef>();

        /// <summary>Walks to the commons whatever the distance, instead of
        /// dashing within its sun range (the giant; fliers).</summary>
        public bool walk;

        /// <summary>The message when this rung opens.</summary>
        [MustTranslate]
        public string message;

        public bool Admits(Pawn pawn)
        {
            return RM_LongShadeKernel.Admits(races != null && races.Count > 0, races != null && races.Contains(pawn.def),
                maxBodySize, pawn.BodySize, herdOnly, pawn.RaceProps.herdAnimal);
        }
    }

    public class RM_ShipfallCommonsExtension : DefModExtension
    {
        /// <summary>Cells round the substructure that count as the commons.</summary>
        public int radius = 8;

        /// <summary>Shade (0..1) a commons cell needs.</summary>
        public float minShade = 0.5f;

        /// <summary>Chance per wander-time check that an admitted animal
        /// outside the commons heads for it.</summary>
        public float pullChance = 0.3f;

        /// <summary>Chance per check that an animal already in the commons
        /// stays (rests) rather than going about its business.</summary>
        public float stayChance = 0.8f;

        /// <summary>How far the scattered animals run from the engine.</summary>
        public float dispersalDistance = 30f;

        [MustTranslate]
        public string dispersalMessage;

        public List<RM_ShipfallStage> stages = new List<RM_ShipfallStage>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (stages == null || stages.Count == 0)
            {
                yield return "RM_ShipfallCommonsExtension has no stages.";
            }
            if (radius < 1)
            {
                yield return "RM_ShipfallCommonsExtension radius must be >= 1.";
            }
        }
    }

    public class RM_MapComponent_ShipfallCommons : MapComponent
    {
        private const int CheckIntervalTicks = 250;

        private int arrivedTick = -1;
        private int stagesOpen;
        private bool dispersedThisLaunch;

        private readonly List<IntVec3> commons = new List<IntVec3>();
        private readonly HashSet<IntVec3> commonsSet = new HashSet<IntVec3>();
        private readonly RM_LongShadeKernel.CommonsKey commonsKey = new RM_LongShadeKernel.CommonsKey();

        public RM_MapComponent_ShipfallCommons(Map map) : base(map)
        {
        }

        public static RM_MapComponent_ShipfallCommons For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_ShipfallCommons>();
        }

        public RM_ShipfallCommonsExtension Ext => map.Biome?.GetModExtension<RM_ShipfallCommonsExtension>();

        public bool Active => RM_LongShadeSettings.shipfallCommonsEnabled && arrivedTick >= 0 && Ext != null;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arrivedTick, "arrivedTick", -1);
            Scribe_Values.Look(ref stagesOpen, "stagesOpen", 0);
            Scribe_Values.Look(ref dispersedThisLaunch, "dispersedThisLaunch", false);
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            RM_ShipfallCommonsExtension ext = Ext;
            if (ext == null || !RM_LongShadeSettings.shipfallCommonsEnabled)
            {
                return;
            }
            Building_GravEngine engine = GravshipUtility.GetPlayerGravEngine_NewTemp(map);
            if (engine == null)
            {
                // The ship left (or never came): the next landing starts the
                // ladder from the bottom again.
                arrivedTick = -1;
                stagesOpen = 0;
                dispersedThisLaunch = false;
                commons.Clear();
                commonsSet.Clear();
                commonsKey.Invalidate();      // an emptied list must never be served as "fresh" when the ship lands again
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (arrivedTick < 0)
            {
                arrivedTick = now;
                stagesOpen = 0;
            }
            AdvanceLadder(ext, now, engine);
            if (PilotAtConsole())
            {
                if (!dispersedThisLaunch)
                {
                    Disperse(ext, engine);
                    dispersedThisLaunch = true;
                }
            }
            else
            {
                dispersedThisLaunch = false;
            }
        }

        private void AdvanceLadder(RM_ShipfallCommonsExtension ext, int now, Building_GravEngine engine)
        {
            var delays = new List<float>(ext.stages.Count);
            for (int i = 0; i < ext.stages.Count; i++)
            {
                delays.Add(ext.stages[i].afterHours);
            }
            int open = RM_LongShadeKernel.OpenStages(delays, now - arrivedTick, GenDate.TicksPerHour);
            while (stagesOpen < open)
            {
                RM_ShipfallStage s = ext.stages[stagesOpen];
                stagesOpen++;
                if (!s.message.NullOrEmpty())
                {
                    Messages.Message(s.message, new LookTargets(engine), MessageTypeDefOf.NeutralEvent, historical: false);
                }
            }
        }

        private bool PilotAtConsole()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (pawns[i].CurJobDef == JobDefOf.PilotConsole)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>The first open rung admitting this pawn, or null.</summary>
        public RM_ShipfallStage StageFor(Pawn pawn)
        {
            RM_ShipfallCommonsExtension ext = Ext;
            if (!Active || ext == null)
            {
                return null;
            }
            int hit = RM_LongShadeKernel.FirstAdmitting(stagesOpen, ext.stages.Count, i => ext.stages[i].Admits(pawn));
            return hit >= 0 ? ext.stages[hit] : null;
        }

        /// <summary>The shaded, standable cells round the hull (never on the
        /// substructure), rebuilt when the shade grid or the ship changes.</summary>
        public List<IntVec3> Commons()
        {
            RM_ShipfallCommonsExtension ext = Ext;
            Building_GravEngine engine = GravshipUtility.GetPlayerGravEngine_NewTemp(map);
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (ext == null || engine == null || grid == null)
            {
                commons.Clear();
                commonsSet.Clear();
                commonsKey.Invalidate();
                return commons;
            }
            HashSet<IntVec3> sub = engine.ValidSubstructure;
            if (sub == null || sub.Count == 0)
            {
                commons.Clear();
                commonsSet.Clear();
                commonsKey.Invalidate();
                return commons;
            }
            if (commonsKey.Fresh(grid.GridVersion, sub.Count, engine.Position.x, engine.Position.z))
            {
                return commons;
            }
            commonsKey.Set(grid.GridVersion, sub.Count, engine.Position.x, engine.Position.z);
            commons.Clear();
            commonsSet.Clear();
            CellRect bounds = CellRect.FromCellList(sub);
            foreach (KeyValuePair<int, int> xz in RM_LongShadeKernel.CommonsCells(bounds.minX, bounds.minZ, bounds.maxX, bounds.maxZ, ext.radius,
                map.Size.x, map.Size.z,
                (x, z) => sub.Contains(new IntVec3(x, 0, z)),
                (x, z) => new IntVec3(x, 0, z).Standable(map),
                (x, z) => grid.ShadeAt(new IntVec3(x, 0, z)),
                ext.minShade))
            {
                IntVec3 c = new IntVec3(xz.Key, 0, xz.Value);
                commons.Add(c);
                commonsSet.Add(c);
            }
            return commons;
        }

        public bool InCommons(IntVec3 c)
        {
            Commons();
            return commonsSet.Contains(c);
        }

        /// <summary>A colonist took the pilot's console: everything wild in
        /// the commons runs from the engine. One message; the launch itself
        /// is never touched.</summary>
        private void Disperse(RM_ShipfallCommonsExtension ext, Building_GravEngine engine)
        {
            Commons();
            List<Thing> threats = new List<Thing> { engine };
            List<Pawn> scattered = new List<Pawn>();
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i];
                if (p.Faction != null || !p.RaceProps.Animal || p.Downed || p.Dead || p.InMentalState
                    || !commonsSet.Contains(p.Position))
                {
                    continue;
                }
                IntVec3 dest = CellFinderLoose.GetFleeDestAnimal(p, threats, ext.dispersalDistance);
                if (!dest.IsValid || dest == p.Position)
                {
                    continue;
                }
                Job flee = JobMaker.MakeJob(JobDefOf.Flee, dest, engine);
                flee.locomotionUrgency = LocomotionUrgency.Sprint;
                p.jobs.StartJob(flee, JobCondition.InterruptForced);
                scattered.Add(p);
            }
            if (scattered.Count > 0 && !ext.dispersalMessage.NullOrEmpty())
            {
                Messages.Message(ext.dispersalMessage, new LookTargets(scattered), MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }
    }

    /// <summary>Animal_PreWander, ahead of the shade hop (insertPriority 15
    /// against its 10) and behind shadow-following (20): an admitted wild
    /// animal heads for the ship's shade, and stays once it is there.</summary>
    public class RM_JobGiver_ShipfallCommons : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_LongShadeSettings.shipfallCommonsEnabled || pawn?.Map == null || pawn.Faction != null
                || !pawn.RaceProps.Animal || pawn.Downed || pawn.InMentalState || pawn.roping?.IsRoped == true)
            {
                return null;
            }
            RM_MapComponent_ShipfallCommons comp = RM_MapComponent_ShipfallCommons.For(pawn.Map);
            RM_ShipfallStage stage = comp?.StageFor(pawn);
            if (stage == null)
            {
                return null;
            }
            RM_ShipfallCommonsExtension ext = comp.Ext;
            RM_SunHeatExtension sun = RM_MapComponent_ShadeGrid.For(pawn.Map)?.HeatExtension;
            if (comp.InCommons(pawn.Position))
            {
                if (!Rand.Chance(ext.stayChance))
                {
                    return null;
                }
                if (sun != null)
                {
                    return RM_ShadeHop.MakeRest(pawn, sun);
                }
                Job wait = JobMaker.MakeJob(JobDefOf.Wait, pawn.Position);
                wait.expiryInterval = 600;
                return wait;
            }
            if (!Rand.Chance(ext.pullChance))
            {
                return null;
            }
            List<IntVec3> cells = comp.Commons();
            if (cells.Count == 0)
            {
                return null;
            }
            for (int tries = 0; tries < 4; tries++)
            {
                IntVec3 target = cells.RandomElement();
                if (!pawn.CanReach(target, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }
                if (stage.walk || sun == null)
                {
                    Job go = JobMaker.MakeJob(JobDefOf.GotoWander, target);
                    go.locomotionUrgency = LocomotionUrgency.Walk;
                    return go;
                }
                // Rest-dash-rest still rules: only a dash it can survive.
                int range = RM_ShadeHop.AnimalDashCost(pawn, sun);
                int cost = RM_ShadePatchGraph.Octile(pawn.Position.x, pawn.Position.z, target.x, target.z);
                if (range > 0 && cost <= range)
                {
                    return RM_ShadeHop.MakeDash(pawn.Position, target, sun.rimPauseTicks.RandomInRange);
                }
            }
            return null;
        }
    }
}
