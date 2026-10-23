using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Webwork
{
    // ════════════════════════════════════════════════════════════════════
    // WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE — the Webwork siege (design/RimMandrake/webwork_spider_siege_2026-10-22.md).
    // Owner, 2026-10-22: "Make a webwork event into neighboring biomes where spiders come in and start spinning webs as a
    // map attack. Their version of a raid. Siege". His card answers the same day: shaded neighbour maps only (no desert),
    // cutting siege silk yields thrixweave (capped per siege here), a cocooned colonist dies after a day, silk stays until cut.
    //
    // Every web here is SPUN by a living ollathrix doing a job (RM_JobDriver_SpinSiegeWeb): walk, face, work with a progress
    // bar, then the silk appears. Nothing lays silk on its own. The decisions are in Kernel/RM_WebworkSiegeKernel.cs (fuzzed).
    // ════════════════════════════════════════════════════════════════════

    [DefOf]
    public static class RM_WebworkSiegeDefOf
    {
        public static IncidentDef RM_WebworkSiege;
        public static JobDef RM_WebSiegeSpin;
        public static JobDef RM_WebSiegeCocoon;
        public static JobDef RM_WebSiegeWrapDoor;
        public static DutyDef RM_WebSiegeSpinDuty;
        public static DutyDef RM_WebSiegePressDuty;
        public static ThingDef RM_Webwork_SiegeWeb;
        public static ThingDef RM_Webwork_SiegeDoorWrap;
        public static ThingDef RM_Webwork_SiegeCocoon;
        public static HediffDef RM_Webwork_SilkSuffocation;
        public static PawnKindDef RM_Ollathrix;

        static RM_WebworkSiegeDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WebworkSiegeDefOf));
        }
    }

    public static class RM_WebworkSiegeUtility
    {
        // The Webwork's own biome and its campaign twin (retired by the end paint; a missing def is simply skipped).
        public static readonly string[] WebworkBiomeDefNames = { "RM_Webwork", "RUT_Webwork" };

        // Silk already on a cell: a spider never spins over it.
        private static readonly string[] WebDefNames = { "RM_Webwork_SiegeWeb", "RM_Webwork_Strand", "RM_Webwork_Cable", "RM_Webwork_Web", "RM_Webwork_Anchor" };

        public const float SpinSearchRadius = 8f;
        public const float CocoonSearchRadius = 25f;
        public const float DoorSearchRadius = 30f;

        private static readonly List<PlanetTile> tmpNeighbours = new List<PlanetTile>();

        public static bool IsWebworkBiome(BiomeDef b)
        {
            return b != null && Array.IndexOf(WebworkBiomeDefNames, b.defName) >= 0;
        }

        public static bool IsWebworkMap(Map map) => map != null && IsWebworkBiome(map.Biome);

        /// <summary>The map's world tile borders a Webwork tile. Out-param: one such tile (for the entry edge).</summary>
        public static bool BordersWebwork(Map map, out PlanetTile webworkTile)
        {
            webworkTile = PlanetTile.Invalid;
            if (map == null || !map.Tile.Valid || Find.WorldGrid == null)
            {
                return false;
            }
            tmpNeighbours.Clear();
            Find.WorldGrid.GetTileNeighbors(map.Tile, tmpNeighbours);
            foreach (PlanetTile nb in tmpNeighbours)
            {
                if (IsWebworkBiome(Find.WorldGrid[nb]?.PrimaryBiome))
                {
                    webworkTile = nb;
                    return true;
                }
            }
            return false;
        }

        /// <summary>Answer 1 (shaded only), measured from the shade grid the scald reads. Measurable only when the grid can answer
        /// for the scald here (present, sun heat active on this biome, the scald reading tree shade); otherwise fails closed.
        /// Samples every third open-sky standable cell; roofed cells are left out so a roofed base never makes a map "shaded".</summary>
        public static void MeasureShade(Map map, out bool measurable, out int sampled, out int shaded)
        {
            sampled = 0;
            shaded = 0;
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            measurable = grid != null && grid.SunHeatActive && RM_CreatureBehaviorsSettings.sunScaldReadsShade;
            if (!measurable)
            {
                return;
            }
            float thr = RM_CreatureBehaviorsSettings.sunScaldShadeThreshold;
            for (int x = 1; x < map.Size.x; x += 3)
            {
                for (int z = 1; z < map.Size.z; z += 3)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (c.Roofed(map) || !c.Standable(map))
                    {
                        continue;
                    }
                    sampled++;
                    if (grid.ShadeAt(c) >= thr)
                    {
                        shaded++;
                    }
                }
            }
        }

        public static SiegeEligibility EligibilityFor(Map map, out int sampled, out int shaded, out bool measurable)
        {
            sampled = shaded = 0;
            measurable = false;
            if (map == null)
            {
                return SiegeEligibility.Disabled;
            }
            bool hook = RM_WebworkSettings.siegeTestIgnoreMapChecks;
            bool borders = !hook && BordersWebwork(map, out _);
            if (!hook && borders)
            {
                MeasureShade(map, out measurable, out sampled, out shaded);
            }
            return RM_WebworkSiegeKernel.Eligibility(RM_WebworkSettings.siegeEnabled, hook, IsWebworkMap(map), borders,
                measurable, sampled, shaded, RM_WebworkSettings.siegeMinShadedFraction);
        }

        public static RM_LordJob_WebworkSiege SiegeOf(Pawn p)
        {
            return p?.GetLord()?.LordJob as RM_LordJob_WebworkSiege;
        }

        /// <summary>Where the colony is: the mean of the colony's buildings, else its colonists, else the map centre.</summary>
        public static IntVec3 ColonyPoint(Map map)
        {
            List<Building> bs = map.listerBuildings.allBuildingsColonist;
            if (bs.Count > 0)
            {
                return Mean(bs.Select(b => b.Position), map);
            }
            List<Pawn> cs = map.mapPawns.FreeColonistsSpawned;
            return cs.Count > 0 ? Mean(cs.Select(p => p.Position), map) : map.Center;
        }

        private static IntVec3 Mean(IEnumerable<IntVec3> cells, Map map)
        {
            long sx = 0, sz = 0;
            int n = 0;
            foreach (IntVec3 c in cells)
            {
                sx += c.x;
                sz += c.z;
                n++;
            }
            return n == 0 ? map.Center : new IntVec3((int)(sx / n), 0, (int)(sz / n)).ClampInsideMap(map);
        }

        /// <summary>The edge facing the Webwork, at a cell the scald reads unexposed and that can reach the colony; then any
        /// reachable cell on that edge; then any reachable edge cell. "Reach" is touching the colony point through doors, or
        /// failing that through anything breakable (a sealed base is still besieged: the colony point may sit on a wall).</summary>
        public static bool TryFindEntry(Map map, IntVec3 colony, out IntVec3 entry)
        {
            Rot4 dir = Rot4.Invalid;
            if (BordersWebwork(map, out PlanetTile ww))
            {
                dir = Find.WorldGrid.GetRotFromTo(map.Tile, ww);
            }
            foreach (TraverseMode mode in new[] { TraverseMode.PassDoors, TraverseMode.PassAllDestroyableThings })
            {
                Predicate<IntVec3> reach = c => c.Standable(map) && !c.Fogged(map)
                    && map.reachability.CanReach(c, colony, PathEndMode.Touch, TraverseParms.For(mode, Danger.Deadly));
                if (dir.IsValid)
                {
                    if (CellFinder.TryFindRandomEdgeCellWith(c => reach(c) && !RM_Hediff_SunScald.ExposedAt(map, c), map, dir, 0f, out entry))
                    {
                        return true;
                    }
                    if (CellFinder.TryFindRandomEdgeCellWith(reach, map, dir, 0f, out entry))
                    {
                        return true;
                    }
                }
                if (CellFinder.TryFindRandomEdgeCellWith(reach, map, 0f, out entry))
                {
                    return true;
                }
            }
            entry = IntVec3.Invalid;
            return false;
        }

        public static bool HasWebAt(Map map, IntVec3 c)
        {
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                if (Array.IndexOf(WebDefNames, things[i].def.defName) >= 0)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>A cell a spider may spin on now: standable, no edifice, no web yet, and the sun-scald predicate reads it
        /// unexposed (they never choose to work in sun).</summary>
        public static bool SpinCellValid(Map map, IntVec3 c)
        {
            return map != null && c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null && !HasWebAt(map, c)
                && !RM_Hediff_SunScald.ExposedAt(map, c);
        }

        private static bool IsAnchor(Map map, IntVec3 c)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            if (c.GetEdifice(map) != null)
            {
                return true;
            }
            Plant p = c.GetPlant(map);
            return p != null && p.def.plant != null && p.def.plant.IsTree;
        }

        public static int CountAdjacentSiegeWebs(Map map, IntVec3 c)
        {
            int n = 0;
            foreach (IntVec3 a in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
            {
                if (a.InBounds(map) && a.GetFirstThing(map, RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb) != null)
                {
                    n++;
                }
            }
            return n;
        }

        public static int CountAdjacentAnchors(Map map, IntVec3 c)
        {
            int n = 0;
            foreach (IntVec3 a in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
            {
                if (IsAnchor(map, a))
                {
                    n++;
                }
            }
            return n;
        }

        /// <summary>The best spin cell within SpinSearchRadius by RM_WebworkSiegeKernel.SpinScore that the spider can reserve
        /// and reach.</summary>
        public static bool TryFindSpinCell(Pawn pawn, RM_LordJob_WebworkSiege siege, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            Map map = pawn.Map;
            if (map == null || siege == null || !RM_WebworkSiegeKernel.MaySpinMore(siege.spun))
            {
                return false;
            }
            var scored = new List<KeyValuePair<float, IntVec3>>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SpinSearchRadius, true))
            {
                if (!SpinCellValid(map, c) || !pawn.CanReserve(c))
                {
                    continue;
                }
                float s = RM_WebworkSiegeKernel.SpinScore(c.DistanceTo(siege.colonyPoint), c.DistanceTo(pawn.Position),
                    CountAdjacentSiegeWebs(map, c), CountAdjacentAnchors(map, c));
                scored.Add(new KeyValuePair<float, IntVec3>(s, c));
            }
            foreach (KeyValuePair<float, IntVec3> kv in scored.OrderByDescending(k => k.Key).Take(6))
            {
                if (pawn.CanReach(kv.Value, PathEndMode.Touch, Danger.Deadly))
                {
                    cell = kv.Value;
                    return true;
                }
            }
            return false;
        }

        /// <summary>The spider's work is done: the silk appears (answer 4: it stays until cut or burned).</summary>
        public static Thing CompleteSpin(Pawn spinner, IntVec3 cell)
        {
            Map map = spinner?.Map;
            RM_LordJob_WebworkSiege siege = SiegeOf(spinner);
            if (map == null || siege == null || !SpinCellValid(map, cell) || !RM_WebworkSiegeKernel.MaySpinMore(siege.spun))
            {
                return null;
            }
            Thing web = ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb);
            web.TryGetComp<RM_CompSiegeSilk>()?.SetSiege(siege.siegeId);
            GenSpawn.Spawn(web, cell, map, WipeMode.Vanish);
            siege.Notify_Spun(cell);
            return web;
        }

        public static bool IsCocoonTarget(Pawn v, Pawn spider)
        {
            return v != null && v.Spawned && !v.Dead && v.Downed && v.RaceProps.Humanlike && v.Faction == Faction.OfPlayer
                && !v.InBed() && v.Map == spider.Map && !RM_Hediff_SunScald.ExposedAt(v.Map, v.Position);
        }

        public static Pawn FindCocoonTarget(Pawn spider)
        {
            if (!RM_WebworkSettings.siegeCocoonDowned || spider.Map == null)
            {
                return null;
            }
            return spider.Map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer)
                .Where(v => IsCocoonTarget(v, spider) && v.Position.InHorDistOf(spider.Position, CocoonSearchRadius)
                            && spider.CanReserveAndReach(v, PathEndMode.Touch, Danger.Deadly))
                .OrderBy(v => v.Position.DistanceToSquared(spider.Position))
                .FirstOrDefault();
        }

        public static Building_Door FindDoorToWrap(Pawn spider)
        {
            Map map = spider.Map;
            if (!RM_WebworkSettings.siegeWrapDoors || map == null)
            {
                return null;
            }
            return map.listerBuildings.allBuildingsColonist.OfType<Building_Door>()
                .Where(d => d.Spawned && !RM_Building_SiegeDoorWrap.IsWrapped(d) && d.Position.InHorDistOf(spider.Position, DoorSearchRadius)
                            && !RM_Hediff_SunScald.ExposedAt(map, d.Position)
                            && spider.CanReserveAndReach(d, PathEndMode.Touch, Danger.Deadly))
                .OrderBy(d => d.Position.DistanceToSquared(spider.Position))
                .FirstOrDefault();
        }

        public static RM_Building_SiegeDoorWrap WrapDoor(Building_Door door)
        {
            if (door == null || !door.Spawned || RM_Building_SiegeDoorWrap.IsWrapped(door))
            {
                return null;
            }
            var wrap = (RM_Building_SiegeDoorWrap)ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeDoorWrap);
            GenSpawn.Spawn(wrap, door.Position, door.Map, WipeMode.Vanish);
            return wrap;
        }

        /// <summary>Wraps a downed pawn where it fell (or the nearest free cell within 2). Null if no cell could take it.</summary>
        public static RM_Building_SiegeCocoon Cocoon(Pawn victim)
        {
            Map map = victim?.Map;
            if (map == null || victim.Dead)
            {
                return null;
            }
            IntVec3 at = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(victim.Position, 2f, true))
            {
                if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null
                    && c.GetFirstThing(map, RM_WebworkSiegeDefOf.RM_Webwork_SiegeCocoon) == null)
                {
                    at = c;
                    break;
                }
            }
            if (!at.IsValid)
            {
                return null;
            }
            var cocoon = (RM_Building_SiegeCocoon)ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeCocoon);
            GenSpawn.Spawn(cocoon, at, map, WipeMode.Vanish);
            IntVec3 back = victim.Position;
            victim.DeSpawnOrDeselect();
            if (!cocoon.TryAcceptThing(victim))
            {
                GenSpawn.Spawn(victim, back, map);
                cocoon.Destroy();
                return null;
            }
            cocoon.Notify_Cocooned();
            return cocoon;
        }

        /// <summary>Spawns the siege on `map` (the worker's body; the proof calls it too). Null = nothing arrived, nothing
        /// spawned (generated pawns are discarded).</summary>
        public static Lord StartSiege(Map map, float points, out List<Pawn> spiders, out string why)
        {
            spiders = new List<Pawn>();
            why = null;
            Faction insects = Faction.OfInsects;
            if (insects == null)
            {
                why = "no insect faction in this save";
                return null;
            }
            IntVec3 colony = ColonyPoint(map);
            if (!TryFindEntry(map, colony, out IntVec3 entry))
            {
                why = "no reachable edge cell";
                return null;
            }
            int n = RM_WebworkSiegeKernel.SpiderCount(points, RM_WebworkSettings.siegeStrength);
            for (int i = 0; i < n; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(RM_WebworkSiegeDefOf.RM_Ollathrix, insects);
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(entry, map, 5), map);
                p.TryGetComp<CompCanBeDormant>()?.WakeUp(); // the race starts dormant; a siege does not sleep at the edge
                spiders.Add(p);
            }
            if (spiders.Count == 0)
            {
                why = "no spider spawned";
                return null;
            }
            var mc = map.GetComponent<RM_MapComponent_WebworkSiege>();
            int id = mc != null ? mc.NewSiegeId() : Find.TickManager.TicksGame;
            var job = new RM_LordJob_WebworkSiege(id, colony, entry, spiders.Count);
            return LordMaker.MakeNewLord(insects, job, map, spiders);
        }
    }

    public class RM_IncidentWorker_WebworkSiege : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms) || !RM_WebworkSettings.siegeEnabled || Faction.OfInsects == null)
            {
                return false;
            }
            return parms.target is Map map && RM_WebworkSiegeUtility.EligibilityFor(map, out _, out _, out _) == SiegeEligibility.Eligible;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map) || RM_WebworkSiegeUtility.EligibilityFor(map, out _, out _, out _) != SiegeEligibility.Eligible)
            {
                return false;
            }
            Lord lord = RM_WebworkSiegeUtility.StartSiege(map, parms.points, out List<Pawn> spiders, out string why);
            if (lord == null)
            {
                Log.Message("[RM Webwork] siege did not start: " + why);
                return false;
            }
            SendStandardLetter("The Webwork comes out", "The web has come out of the Webwork. " + spiders.Count
                + " ollathrix have come onto the map under the trees and are spinning toward the colony.\n\n"
                + "They will not cross open sunlight by choice. Their silk is sticky and burns well. Cut wrapped doors free, and cut "
                + "anyone they cocoon out within " + RM_WebworkSettings.siegeCocoonDeathHours.ToString("0") + " hours.",
                LetterDefOf.ThreatBig, parms, spiders);
            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }
    }

    public class RM_LordJob_WebworkSiege : LordJob
    {
        public int siegeId = -1;
        public int startTick = -1;
        public IntVec3 colonyPoint = IntVec3.Invalid;
        public IntVec3 entry = IntVec3.Invalid;
        public IntVec3 front = IntVec3.Invalid;
        public int spun;
        public int initialCount;
        public bool webNearColony;
        public bool breakLetterSent;

        public RM_LordJob_WebworkSiege() { }

        public RM_LordJob_WebworkSiege(int siegeId, IntVec3 colonyPoint, IntVec3 entry, int initialCount)
        {
            this.siegeId = siegeId;
            this.colonyPoint = colonyPoint;
            this.entry = entry;
            front = entry;
            this.initialCount = initialCount;
            startTick = Find.TickManager.TicksGame;
        }

        public override bool GuiltyOnDowned => true;

        public int TicksSinceArrival => Find.TickManager.TicksGame - startTick;

        public IntVec3 DutyFocus => front.IsValid ? front : entry;

        public bool ShouldPress => RM_WebworkSiegeKernel.ShouldPress(webNearColony, spun, TicksSinceArrival);

        public bool TimedOut => RM_WebworkSiegeKernel.TimedOut(TicksSinceArrival, RM_WebworkSettings.siegeMaxDays);

        public void Notify_Spun(IntVec3 cell)
        {
            spun++;
            front = cell;
            if (!webNearColony && lord?.Map != null)
            {
                foreach (Building b in lord.Map.listerBuildings.allBuildingsColonist)
                {
                    if (b.Position.InHorDistOf(cell, RM_WebworkSiegeKernel.PressRadius))
                    {
                        webNearColony = true;
                        break;
                    }
                }
            }
        }

        public override StateGraph CreateGraph()
        {
            var graph = new StateGraph();
            LordToil spin = new RM_LordToil_WebworkSiege(press: false);
            LordToil press = new RM_LordToil_WebworkSiege(press: true);
            LordToil exit = new LordToil_ExitMap(LocomotionUrgency.Walk, canDig: false, interruptCurrentJob: true);
            graph.AddToil(spin);
            graph.AddToil(press);
            graph.AddToil(exit);
            var toPress = new Transition(spin, press);
            toPress.AddTrigger(new Trigger_TickCondition(() => ShouldPress, 250));
            graph.AddTransition(toPress);
            var toBreak = new Transition(spin, exit);
            toBreak.AddSource(press);
            toBreak.AddTrigger(new Trigger_FractionPawnsLost(0.5f));
            toBreak.AddTrigger(new Trigger_TickCondition(() => TimedOut, 250));
            toBreak.AddPreAction(new TransitionAction_Custom(SendBreakLetter));
            graph.AddTransition(toBreak);
            return graph;
        }

        public void SendBreakLetter()
        {
            if (breakLetterSent || lord?.Map == null)
            {
                return;
            }
            breakLetterSent = true;
            int leaving = lord.ownedPawns.Count(p => p.Spawned && !p.Dead && !p.Downed);
            int dead = lord.numPawnsLostViolently;
            Find.LetterStack.ReceiveLetter("The siege breaks", "The siege has broken. " + leaving + " ollathrix are going back toward the "
                + "Webwork; " + dead + " are dead. What they spun stays until you cut or burn it.",
                LetterDefOf.PositiveEvent, new LookTargets(lord.ownedPawns.Where(p => p.Spawned)));
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref siegeId, "siegeId", -1);
            Scribe_Values.Look(ref startTick, "startTick", -1);
            Scribe_Values.Look(ref colonyPoint, "colonyPoint", IntVec3.Invalid);
            Scribe_Values.Look(ref entry, "entry", IntVec3.Invalid);
            Scribe_Values.Look(ref front, "front", IntVec3.Invalid);
            Scribe_Values.Look(ref spun, "spun", 0);
            Scribe_Values.Look(ref initialCount, "initialCount", 0);
            Scribe_Values.Look(ref webNearColony, "webNearColony", false);
            Scribe_Values.Look(ref breakLetterSent, "breakLetterSent", false);
        }
    }

    /// <summary>Spin (press=false) or Press (press=true): one duty for every spider, focused on the siege's newest web.</summary>
    public class RM_LordToil_WebworkSiege : LordToil
    {
        public bool press;

        public RM_LordToil_WebworkSiege() { }

        public RM_LordToil_WebworkSiege(bool press)
        {
            this.press = press;
        }

        public override bool ForceHighStoryDanger => press;

        private RM_LordJob_WebworkSiege Siege => lord.LordJob as RM_LordJob_WebworkSiege;

        public override void UpdateAllDuties()
        {
            RM_LordJob_WebworkSiege s = Siege;
            IntVec3 focus = s != null ? s.DutyFocus : lord.ownedPawns.FirstOrDefault()?.Position ?? IntVec3.Invalid;
            DutyDef d = press ? RM_WebworkSiegeDefOf.RM_WebSiegePressDuty : RM_WebworkSiegeDefOf.RM_WebSiegeSpinDuty;
            foreach (Pawn p in lord.ownedPawns)
            {
                p.mindState.duty = new PawnDuty(d, focus, 10f);
            }
        }

        public override void LordToilTick()
        {
            base.LordToilTick();
            if (Find.TickManager.TicksGame % 250 == 0)
            {
                UpdateAllDuties(); // the focus follows the newest web
            }
        }
    }

    /// <summary>The siege's work, by priority: cocoon a downed colonist, wrap a door (each only if this giver says so and the
    /// setting is on), then spin.</summary>
    public class RM_JobGiver_WebworkSiegeWork : ThinkNode_JobGiver
    {
        public bool cocoon;
        public bool wrapDoors;
        public bool spin = true;

        public override ThinkNode DeepCopy(bool resolve = true)
        {
            var c = (RM_JobGiver_WebworkSiegeWork)base.DeepCopy(resolve);
            c.cocoon = cocoon;
            c.wrapDoors = wrapDoors;
            c.spin = spin;
            return c;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_LordJob_WebworkSiege siege = RM_WebworkSiegeUtility.SiegeOf(pawn);
            if (siege == null || pawn.Downed || pawn.Map == null)
            {
                return null;
            }
            if (cocoon)
            {
                Pawn v = RM_WebworkSiegeUtility.FindCocoonTarget(pawn);
                if (v != null)
                {
                    return JobMaker.MakeJob(RM_WebworkSiegeDefOf.RM_WebSiegeCocoon, v);
                }
            }
            if (wrapDoors)
            {
                Building_Door d = RM_WebworkSiegeUtility.FindDoorToWrap(pawn);
                if (d != null)
                {
                    return JobMaker.MakeJob(RM_WebworkSiegeDefOf.RM_WebSiegeWrapDoor, d);
                }
            }
            if (spin && RM_WebworkSiegeUtility.TryFindSpinCell(pawn, siege, out IntVec3 cell))
            {
                return JobMaker.MakeJob(RM_WebworkSiegeDefOf.RM_WebSiegeSpin, cell);
            }
            return null;
        }
    }

    public class RM_JobDriver_SpinSiegeWeb : JobDriver
    {
        private IntVec3 Cell => job.targetA.Cell;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !RM_WebworkSiegeUtility.SpinCellValid(Map, Cell));
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(RM_WebworkSiegeKernel.SpinTicks(RM_WebworkSettings.siegeSpinSpeed), TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);   // GPT deep review 2026-10-22 #9
            SoundDef sound = DefDatabase<SoundDef>.GetNamedSilentFail("Recipe_Tailor");
            if (sound != null)
            {
                work.PlaySustainerOrSound(sound);
            }
            yield return work;
            yield return new Toil
            {
                initAction = () => RM_WebworkSiegeUtility.CompleteSpin(pawn, Cell),
                defaultCompleteMode = ToilCompleteMode.Instant
            };
        }
    }

    public class RM_JobDriver_SiegeCocoon : JobDriver
    {
        public const int WrapTicks = 300; // PROVISIONAL

        private Pawn Victim => (Pawn)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_WebworkSettings.siegeCocoonDowned || !RM_WebworkSiegeUtility.IsCocoonTarget(Victim, pawn));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(WrapTicks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);   // GPT deep review 2026-10-22 #9: a dragged-off victim ends the wrap
            yield return new Toil
            {
                initAction = () => RM_WebworkSiegeUtility.Cocoon(Victim),
                defaultCompleteMode = ToilCompleteMode.Instant
            };
        }
    }

    public class RM_JobDriver_SiegeWrapDoor : JobDriver
    {
        public const int WrapTicks = 240; // PROVISIONAL

        private Building_Door Door => (Building_Door)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_WebworkSettings.siegeWrapDoors || RM_Building_SiegeDoorWrap.IsWrapped(Door));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(WrapTicks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);   // GPT deep review 2026-10-22 #9: a dragged-off victim ends the wrap
            yield return new Toil
            {
                initAction = () => RM_WebworkSiegeUtility.WrapDoor(Door),
                defaultCompleteMode = ToilCompleteMode.Instant
            };
        }
    }

    /// <summary>Per map: siege ids and the thrixweave each siege has yielded to cutting (answer 2's farm guard).</summary>
    public class RM_MapComponent_WebworkSiege : MapComponent
    {
        private int nextSiegeId = 1;
        private Dictionary<int, int> yielded = new Dictionary<int, int>();

        public RM_MapComponent_WebworkSiege(Map map) : base(map) { }

        public int NewSiegeId() => nextSiegeId++;

        public int YieldedBy(int siegeId) => yielded.TryGetValue(siegeId, out int n) ? n : 0;

        /// <summary>How much one cut of this siege's silk drops now; records it.</summary>
        public int TakeYield(int siegeId, int perCut)
        {
            int got = RM_WebworkSiegeKernel.YieldGranted(YieldedBy(siegeId), RM_WebworkSettings.siegeSilkYieldCap, perCut);
            if (got > 0)
            {
                yielded[siegeId] = YieldedBy(siegeId) + got;
            }
            return got;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref nextSiegeId, "nextSiegeId", 1);
            Scribe_Collections.Look(ref yielded, "yielded", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && yielded == null)
            {
                yielded = new Dictionary<int, int>();
            }
        }
    }

    public class RM_CompProperties_SiegeSilk : CompProperties
    {
        public int perCut = RM_WebworkSiegeKernel.YieldPerCut;
        public HediffDef slickHediff;
        public float severityPerScan = 0.034f;

        public RM_CompProperties_SiegeSilk()
        {
            compClass = typeof(RM_CompSiegeSilk);
        }
    }

    /// <summary>Siege silk: which siege spun it, the sticky coat (RM_Webwork_Slick on anyone standing in it but an ollathrix,
    /// under CreatureBehaviors' own adhesive settings), and the capped thrixweave a colonist's cut (vanilla Deconstruct) drops.
    /// A force-broken web drops nothing (the def has no killedLeavings), so cutting is the only route.</summary>
    public class RM_CompSiegeSilk : ThingComp
    {
        public int siegeId = -1;

        // Proof read (static: the parent is gone by the time anyone asks); describes the last call only.
        public static int lastYieldSpawned;

        public RM_CompProperties_SiegeSilk Props => (RM_CompProperties_SiegeSilk)props;

        public void SetSiege(int id) { siegeId = id; }

        public override void CompTick()
        {
            base.CompTick();
            if (Props.slickHediff == null || !RM_CreatureBehaviorsSettings.adhesiveSlickEnabled || !parent.Spawned
                || !parent.IsHashIntervalTick(60))
            {
                return;
            }
            float amount = Props.severityPerScan * Mathf.Max(0f, RM_CreatureBehaviorsSettings.adhesiveSlickSeverityMultiplier);
            if (amount <= 0f)
            {
                return;
            }
            List<Thing> here = parent.Map.thingGrid.ThingsListAtFast(parent.Position);
            for (int i = here.Count - 1; i >= 0; i--)
            {
                if (here[i] is Pawn p && !p.Dead && p.health != null && p.def.defName != "RM_Ollathrix")
                {
                    Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.slickHediff);
                    if (h != null)
                    {
                        h.Severity += amount;
                    }
                    else
                    {
                        h = HediffMaker.MakeHediff(Props.slickHediff, p);
                        h.Severity = amount;
                        p.health.AddHediff(h);
                    }
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref siegeId, "siegeId", -1);
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            lastYieldSpawned = 0;
            if (mode != DestroyMode.Deconstruct || previousMap == null)
            {
                return;
            }
            var mc = previousMap.GetComponent<RM_MapComponent_WebworkSiege>();
            ThingDef silk = DefDatabase<ThingDef>.GetNamedSilentFail("Hyperweave");
            IntVec3 pos = parent.PositionHeld;
            if (mc == null || silk == null || !pos.IsValid || !pos.InBounds(previousMap))
            {
                return;
            }
            // The cap is spent BEFORE placement; a failed Near-placement (practically never) loses that share (GPT deep
            // review 2026-10-22 #14: the old comment claimed otherwise)
            int n = mc.TakeYield(siegeId, Props.perCut);
            if (n <= 0)
            {
                return;
            }
            Thing t = ThingMaker.MakeThing(silk);
            t.stackCount = n;
            if (GenPlace.TryPlaceThing(t, pos, previousMap, ThingPlaceMode.Near))
            {
                lastYieldSpawned = n;
            }
        }

        public override string CompInspectStringExtra()
        {
            Map map = parent.MapHeld;
            var mc = map?.GetComponent<RM_MapComponent_WebworkSiege>();
            if (mc == null || siegeId < 0)
            {
                return null;
            }
            int left = Mathf.Max(0, RM_WebworkSettings.siegeSilkYieldCap - mc.YieldedBy(siegeId));
            return "Spun by a siege. Thrixweave still to be cut from that siege: " + left;
        }
    }

    /// <summary>Silk wrapped round a door's cell: the door opens for no one while it stands (RM_WebworkSiegeDoorPatch). Cut it
    /// with vanilla Deconstruct; fire burns it.</summary>
    public class RM_Building_SiegeDoorWrap : Building
    {
        /// <summary>Wraps spawned anywhere; the door postfix is one compare while this is zero. Only a fast path: leaving a
        /// game does not DeSpawn its things, so this can stay high after a reload, and IsWrapped still reads the cell itself.</summary>
        public static int LiveWraps;

        public static bool IsWrapped(Building_Door door)
        {
            if (LiveWraps <= 0 || door == null || !door.Spawned)
            {
                return false;
            }
            return door.Position.GetFirstThing(door.Map, RM_WebworkSiegeDefOf.RM_Webwork_SiegeDoorWrap) != null;
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            LiveWraps++;
            Building_Door door = Position.GetDoor(map);
            if (door != null && !respawningAfterLoad)
            {
                // A held-open door would stay passable (FreePassage); the wrap pulls it shut as soon as the doorway is clear.
                AccessTools.Field(typeof(Building_Door), "holdOpenInt")?.SetValue(door, false);
                door.StartManualCloseBy(null);
            }
            Refresh(map);
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            base.DeSpawn(mode);
            LiveWraps = Mathf.Max(0, LiveWraps - 1);
            Refresh(map);
        }

        private void Refresh(Map map)
        {
            if (map == null)
            {
                return;
            }
            map.reachability.ClearCache();
            map.pathing.RecalculatePerceivedPathCostAt(Position);
        }
    }

    /// <summary>A downed colonist wrapped where they fell (answer 3: dies after siegeCocoonDeathHours unless cut out). Cut out
    /// with vanilla Open (right-click, or the Open designator); burning or breaking it drops them, downed (Building_Casket).
    /// The cocoon does not tick its pawn (vanilla casket), so its own clock is the only killer.</summary>
    public class RM_Building_SiegeCocoon : Building_Casket
    {
        private int cocoonedTick = -1;
        private bool died;

        public override int OpenTicks => 240; // PROVISIONAL: 4 s to cut someone out

        public int TicksInside => cocoonedTick < 0 ? 0 : Find.TickManager.TicksGame - cocoonedTick;

        public Pawn Inside => ContainedThing as Pawn;

        public void Notify_Cocooned()
        {
            cocoonedTick = Find.TickManager.TicksGame;
            Pawn p = Inside;
            if (p != null)
            {
                Find.LetterStack.ReceiveLetter("Cocooned: " + p.LabelShort, "An ollathrix has wrapped " + p.LabelShort
                    + " in silk where they fell. Cut them out (right-click the cocoon: Open) within "
                    + RM_WebworkSettings.siegeCocoonDeathHours.ToString("0") + " hours, or they will die inside.",
                    LetterDefOf.ThreatSmall, this);
            }
        }

        /// <summary>Proof hook: put the clock back so the deadline can be reached without waiting.</summary>
        public void Debug_AgeBy(int ticks) { cocoonedTick -= ticks; }

        protected override void Tick()
        {
            base.Tick();
            if (this.IsHashIntervalTick(250))
            {
                CheckClock();
            }
        }

        public void CheckClock()
        {
            Pawn p = Inside;
            if (died || p == null || p.Dead || !RM_WebworkSiegeKernel.CocoonKills(TicksInside, RM_WebworkSettings.siegeCocoonDeathHours))
            {
                return;
            }
            died = true;
            string name = p.LabelShort;
            Hediff h = HediffMaker.MakeHediff(RM_WebworkSiegeDefOf.RM_Webwork_SilkSuffocation, p);
            h.Severity = 1f;
            p.health.AddHediff(h);
            if (!p.Dead)
            {
                p.Kill(null, h);
            }
            // Vanilla Pawn.Kill already sends the death letter (cause: silk suffocation); this only says where the body is.
            Messages.Message(name + " was not cut out of the ollathrix cocoon in time. The body is still in the cocoon (Open it).",
                this, MessageTypeDefOf.NegativeEvent);
        }

        public override void Open()
        {
            base.Open();
            if (!Destroyed)
            {
                Destroy(DestroyMode.Vanish); // the cut silk falls away
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            Pawn p = Inside;
            if (p != null && !p.Dead)
            {
                s += "\nDies in " + RM_WebworkSiegeKernel.CocoonHoursLeft(TicksInside, RM_WebworkSettings.siegeCocoonDeathHours).ToString("0.0")
                     + " hours unless cut out (Open).";
            }
            return s;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cocoonedTick, "cocoonedTick", -1);
            Scribe_Values.Look(ref died, "died", false);
        }
    }

    /// <summary>The one Harmony change: a door with a siege wrap on its cell opens for no one and gives no free passage. Inert
    /// (one integer compare) while no wrap exists anywhere.</summary>
    [StaticConstructorOnStartup]
    public static class RM_WebworkSiegeDoorPatch
    {
        static RM_WebworkSiegeDoorPatch()
        {
            try
            {
                var harmony = new Harmony("mandrake.rm.webwork.siegedoor");
                var canOpen = AccessTools.Method(typeof(Building_Door), nameof(Building_Door.PawnCanOpen));
                var free = AccessTools.PropertyGetter(typeof(Building_Door), nameof(Building_Door.FreePassage));
                if (canOpen == null || free == null)
                {
                    Log.Warning("[RM Webwork] siege: Building_Door.PawnCanOpen/FreePassage not found; wrapped doors will still open.");
                    return;
                }
                var post = new HarmonyMethod(typeof(RM_WebworkSiegeDoorPatch), nameof(Postfix_Blocked));
                harmony.Patch(canOpen, postfix: post);
                harmony.Patch(free, postfix: post);
            }
            catch (Exception e)
            {
                Log.Error("[RM Webwork] siege: door patch failed; wrapped doors will still open: " + e);
            }
        }

        public static void Postfix_Blocked(Building_Door __instance, ref bool __result)
        {
            if (__result && RM_Building_SiegeDoorWrap.LiveWraps > 0 && RM_Building_SiegeDoorWrap.IsWrapped(__instance))
            {
                __result = false;
            }
        }
    }
}
