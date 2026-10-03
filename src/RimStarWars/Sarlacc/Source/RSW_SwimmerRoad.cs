using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Sarlacc
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_BEDAZZLE_MECHANICS_1 part 3, tranche 2 — the swimmer's road.
    // Design: design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md
    // §6.3 (and §2D S1/S2). Owner: "3 Swimmer's road: IN, with a condition."
    //
    // One young sarlacc swimmer per map, EVER. It comes up at the map edge and
    // travels rim to rim along SOLAR_HEAT_EXPOSURE_1's shade-patch graph
    // (RM_MapComponent_ShadeGrid.PatchGraph — reused, not rebuilt here) toward
    // the largest dew ring on soft ground: the patch with the most rim cells
    // on diggable, unfloored terrain, which on a colonised map is usually the
    // player's walls. It pauses at each rim (the shared RM_ShadeDash job) and
    // leaps at whatever flesh stands on the dew line in reach. If it reaches
    // the ring it roots into a permanent anchored sarlacc in the middle of the
    // shade, and every wild tenant of that patch flees at once.
    //
    // Signs (the owner's condition, nothing "disappears spontaneously"): a
    // take lays RM_Filth_DisturbedSand and names the prey (CompSarlaccSwimmer,
    // tranche 1 + 2); the rooting is a letter naming the patch it took.
    //
    // Tier: RSW (a canon creature). Gated on the biome by the IncidentDef's
    // RSW_SwimmerRoadExtension.biomes (defNames, so the Long Shade mod need
    // not be loaded), on mandrake.rm.creaturebehaviors being active (soft
    // reference: every method that names one of its types is reached only
    // after that check), and on the Mod Settings toggle.
    // ════════════════════════════════════════════════════════════════════

    public class RSW_SwimmerRoadExtension : DefModExtension
    {
        /// <summary>BiomeDef defNames the road can happen on.</summary>
        public List<string> biomes = new List<string>();

        /// <summary>The swimmer's PawnKindDef (Anomaly-gated, so by name).</summary>
        public string pawnKind = "RSW_SarlaccSwimmer";

        /// <summary>A dew ring smaller than this (rim cells on soft ground)
        /// is not worth the swim.</summary>
        public int minRingRimCells = 8;

        /// <summary>Within this many cells of the ring's centre it roots.</summary>
        public float rootWithinCells = 2.9f;

        public IntRange rimPauseTicks = new IntRange(90, 240);

        /// <summary>STILLSAND_EVENT_CREATURES_REMAINDER_1: the seep incident's marker thing
        /// (RSW_DeepDesertSeep). Empty on the Long Shade road.</summary>
        public string seepMarker;

        /// <summary>Seep incident: terrain defName counted around each marker to find the
        /// largest seep (a brine pool); its cells within seepScoreRadius are the score.</summary>
        public string seepTerrain;

        public float seepScoreRadius = 6.9f;
    }

    public class RSW_MapComponent_SwimmerRoad : MapComponent
    {
        private const int CheckIntervalTicks = 250;

        /// <summary>Set the moment the incident fires; never cleared. One per map, ever.</summary>
        public bool fired;
        public Pawn swimmer;
        public Thing anchored;
        public IntVec3 targetCell = IntVec3.Invalid;
        public string incidentDefName;

        /// <summary>STILLSAND_EVENT_CREATURES_REMAINDER_1: this swimmer is walking to a buried seep, not a dew ring.</summary>
        public bool seepMode;

        public RSW_MapComponent_SwimmerRoad(Map map)
            : base(map)
        {
        }

        public static RSW_MapComponent_SwimmerRoad For(Map map)
        {
            return map?.GetComponent<RSW_MapComponent_SwimmerRoad>();
        }

        public static bool CreatureBehaviorsActive => ModsConfig.IsActive("mandrake.rm.creaturebehaviors");

        public bool IsRoadSwimmer(Pawn p)
        {
            return p != null && swimmer == p && !p.Dead;
        }

        public RSW_SwimmerRoadExtension Extension
        {
            get
            {
                IncidentDef def = incidentDefName != null ? DefDatabase<IncidentDef>.GetNamedSilentFail(incidentDefName) : null;
                return def?.GetModExtension<RSW_SwimmerRoadExtension>() ?? new RSW_SwimmerRoadExtension();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref fired, "rswRoadFired", false);
            Scribe_References.Look(ref swimmer, "rswRoadSwimmer");
            Scribe_References.Look(ref anchored, "rswRoadAnchored");
            Scribe_Values.Look(ref targetCell, "rswRoadTarget", IntVec3.Invalid);
            Scribe_Values.Look(ref incidentDefName, "rswRoadIncident");
            Scribe_Values.Look(ref seepMode, "rswRoadSeepMode", false);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (swimmer == null || Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (swimmer.Dead || swimmer.Destroyed || !swimmer.Spawned || swimmer.Map != map)
            {
                if (swimmer.Dead || swimmer.Destroyed)
                {
                    swimmer = null; // killed, or rooted by its own reserve: the road is over
                }
                return;
            }
            if (seepMode)
            {
                if (RSW_SarlaccSettings.swimmerSeepEnabled)
                {
                    RSW_SwimmerSeepLogic.CheckArrival(this);
                }
                return;
            }
            if (!RSW_SarlaccSettings.swimmerRoadEnabled || !CreatureBehaviorsActive)
            {
                return;
            }
            RSW_SwimmerRoadLogic.CheckArrival(this);
        }
    }

    public class RSW_IncidentWorker_SwimmerRoad : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RSW_SarlaccSettings.swimmerRoadEnabled || !RSW_MapComponent_SwimmerRoad.CreatureBehaviorsActive)
            {
                return false;
            }
            Map map = parms.target as Map;
            RSW_SwimmerRoadExtension ext = def.GetModExtension<RSW_SwimmerRoadExtension>();
            if (map == null || ext == null || map.Biome == null || !ext.biomes.Contains(map.Biome.defName))
            {
                return false;
            }
            RSW_MapComponent_SwimmerRoad road = RSW_MapComponent_SwimmerRoad.For(map);
            if (road == null || road.fired)
            {
                return false;
            }
            if (DefDatabase<PawnKindDef>.GetNamedSilentFail(ext.pawnKind) == null)
            {
                return false;
            }
            return RSW_SwimmerRoadLogic.TryPickTarget(map, ext, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RSW_SwimmerRoadExtension ext = def.GetModExtension<RSW_SwimmerRoadExtension>();
            RSW_MapComponent_SwimmerRoad road = RSW_MapComponent_SwimmerRoad.For(map);
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(ext.pawnKind);
            if (road == null || road.fired || kind == null || !RSW_SwimmerRoadLogic.TryPickTarget(map, ext, out IntVec3 target))
            {
                return false;
            }
            if (!RSW_SwimmerRoadLogic.TryFindEntry(map, target, out IntVec3 entry))
            {
                return false;
            }
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null));
            if (GenSpawn.Spawn(pawn, entry, map) == null)
            {
                return false;
            }
            road.fired = true;
            road.swimmer = pawn;
            road.targetCell = target;
            road.incidentDefName = def.defName;
            SendStandardLetter(def.letterLabel, def.letterText, def.letterDef, parms,
                new LookTargets(pawn));
            return true;
        }
    }

    /// <summary>Devourer_PreWander (the swimmer runs Anomaly's Devourer think
    /// tree): for the road swimmer only, leap at flesh on the dew line in
    /// reach, else take the next hop toward its ring. Every other pawn
    /// running that tree gets null at the first check.</summary>
    public class RSW_JobGiver_SwimmerRoad : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn?.Map == null)
            {
                return null;
            }
            RSW_MapComponent_SwimmerRoad seepRoad = RSW_MapComponent_SwimmerRoad.For(pawn.Map);
            if (seepRoad != null && seepRoad.seepMode && seepRoad.IsRoadSwimmer(pawn))
            {
                // Seep incident: needs no shade graph and no Creature Behaviors.
                return RSW_SarlaccSettings.swimmerSeepEnabled ? RSW_SwimmerSeepLogic.NextJob(pawn, seepRoad) : null;
            }
            if (!RSW_SarlaccSettings.swimmerRoadEnabled)
            {
                return null;
            }
            RSW_MapComponent_SwimmerRoad road = RSW_MapComponent_SwimmerRoad.For(pawn.Map);
            if (road == null || !road.IsRoadSwimmer(pawn) || !RSW_MapComponent_SwimmerRoad.CreatureBehaviorsActive)
            {
                return null;
            }
            return RSW_SwimmerRoadLogic.NextJob(pawn, road);
        }
    }

    /// <summary>Every use of mandrake.rm.creaturebehaviors' types lives here,
    /// reached only after RSW_MapComponent_SwimmerRoad.CreatureBehaviorsActive.</summary>
    public static class RSW_SwimmerRoadLogic
    {
        private const string LeapAbility = "ConsumeLeap_Devourer";
        private const int DewLineCost = 14; // one diagonal step off the rim, in patch-graph cost units

        private static RM_ShadePatchGraph Graph(Map map)
        {
            return RM_MapComponent_ShadeGrid.For(map)?.PatchGraph;
        }

        private static bool SoftGround(IntVec3 c, Map map, TerrainAffordanceDef diggable)
        {
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsFloor || t.IsWater)
            {
                return false;
            }
            return diggable == null || t.affordances == null || t.affordances.Contains(diggable);
        }

        /// <summary>The largest dew ring on soft ground: the patch with the
        /// most rim cells on diggable, unfloored terrain, and the patch cell
        /// nearest its centre.</summary>
        public static bool TryPickTarget(Map map, RSW_SwimmerRoadExtension ext, out IntVec3 target)
        {
            target = IntVec3.Invalid;
            RM_ShadePatchGraph g = Graph(map);
            if (g == null || g.PatchCount == 0)
            {
                return false;
            }
            TerrainAffordanceDef diggable = DefDatabase<TerrainAffordanceDef>.GetNamedSilentFail("Diggable");
            int best = -1, bestRim = 0;
            for (int p = 0; p < g.patches.Count; p++)
            {
                List<int> rim = g.patches[p].rim;
                int soft = 0;
                for (int k = 0; k < rim.Count; k++)
                {
                    if (SoftGround(map.cellIndices.IndexToCell(rim[k]), map, diggable))
                    {
                        soft++;
                    }
                }
                if (soft > bestRim)
                {
                    bestRim = soft;
                    best = p;
                }
            }
            if (best < 0 || bestRim < ext.minRingRimCells)
            {
                return false;
            }
            return TryCentreOf(map, g, best, out target);
        }

        private static bool TryCentreOf(Map map, RM_ShadePatchGraph g, int patch, out IntVec3 centre)
        {
            centre = IntVec3.Invalid;
            long sx = 0, sz = 0;
            int n = 0;
            for (int i = 0; i < g.patchOf.Length; i++)
            {
                if (g.patchOf[i] == patch)
                {
                    sx += i % g.width;
                    sz += i / g.width;
                    n++;
                }
            }
            if (n == 0)
            {
                return false;
            }
            float cx = sx / (float)n, cz = sz / (float)n;
            float bestD = float.MaxValue;
            for (int i = 0; i < g.patchOf.Length; i++)
            {
                if (g.patchOf[i] != patch)
                {
                    continue;
                }
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (!c.Standable(map))
                {
                    continue;
                }
                float d = (c.x - cx) * (c.x - cx) + (c.z - cz) * (c.z - cz);
                if (d < bestD)
                {
                    bestD = d;
                    centre = c;
                }
            }
            return centre.IsValid;
        }

        /// <summary>A soft-ground edge cell that can reach the target, as far
        /// from it as a few tries find: the swim should take days, not minutes.</summary>
        public static bool TryFindEntry(Map map, IntVec3 target, out IntVec3 entry)
        {
            entry = IntVec3.Invalid;
            TerrainAffordanceDef diggable = DefDatabase<TerrainAffordanceDef>.GetNamedSilentFail("Diggable");
            float bestD = -1f;
            for (int i = 0; i < 12; i++)
            {
                if (!CellFinder.TryFindRandomEdgeCellWith(
                        c => c.Standable(map) && SoftGround(c, map, diggable)
                             && map.reachability.CanReach(c, target, PathEndMode.OnCell, TraverseMode.PassDoors, Danger.Deadly),
                        map, 0f, out IntVec3 c2))
                {
                    continue;
                }
                float d = (c2 - target).LengthHorizontalSquared;
                if (d > bestD)
                {
                    bestD = d;
                    entry = c2;
                }
            }
            return entry.IsValid;
        }

        /// <summary>The road target's patch in the CURRENT graph; re-picked if
        /// the ring it swam for has gone (walls torn down, shade moved).</summary>
        private static int TargetPatch(RSW_MapComponent_SwimmerRoad road, RM_ShadePatchGraph g, Map map)
        {
            int patch = road.targetCell.IsValid && road.targetCell.InBounds(map)
                ? g.PatchAt(map.cellIndices.CellToIndex(road.targetCell))
                : RM_ShadePatchGraph.NoPatch;
            if (patch == RM_ShadePatchGraph.NoPatch && TryPickTarget(map, road.Extension, out IntVec3 t))
            {
                road.targetCell = t;
                patch = g.PatchAt(map.cellIndices.CellToIndex(t));
            }
            return patch;
        }

        private static bool OnDewLine(RM_ShadePatchGraph g, IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            int d = g.distToShade[map.cellIndices.CellToIndex(c)];
            if (d == RM_ShadePatchGraph.Unreached || d > DewLineCost)
            {
                return false;
            }
            if (d > 0)
            {
                return true; // the open cells hugging the rim
            }
            // a shade cell: on the line only if it is a rim (touches open sun)
            foreach (IntVec3 n in GenAdj.AdjacentCells)
            {
                IntVec3 v = c + n;
                if (v.InBounds(map))
                {
                    int dv = g.distToShade[map.cellIndices.CellToIndex(v)];
                    if (dv > 0 && dv != RM_ShadePatchGraph.Unreached)
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        public static Job NextJob(Pawn pawn, RSW_MapComponent_SwimmerRoad road)
        {
            Map map = pawn.Map;
            RM_ShadePatchGraph g = Graph(map);
            if (g == null)
            {
                return null; // shade hopping off on this map: vanilla Devourer wander
            }
            CompDevourer devourer = pawn.TryGetComp<CompDevourer>();
            if (devourer != null && devourer.Digesting)
            {
                return null;
            }
            Job leap = TryLeap(pawn, g);
            if (leap != null)
            {
                return leap;
            }
            int target = TargetPatch(road, g, map);
            if (target == RM_ShadePatchGraph.NoPatch)
            {
                return null;
            }
            RSW_SwimmerRoadExtension ext = road.Extension;
            int here = g.PatchAt(map.cellIndices.CellToIndex(pawn.Position));
            if (here == target)
            {
                return Goto(road.targetCell);
            }
            if (here == RM_ShadePatchGraph.NoPatch)
            {
                // In the open: dash to the nearest shade, like everything here.
                int idx = map.cellIndices.CellToIndex(pawn.Position);
                int near = g.nearestShade[idx];
                if (g.distToShade[idx] != RM_ShadePatchGraph.Unreached && near >= 0)
                {
                    IntVec3 c = map.cellIndices.IndexToCell(near);
                    if (c != pawn.Position && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                    {
                        return RM_ShadeHop.MakeDash(pawn.Position, c, 0);
                    }
                }
                return Goto(road.targetCell);
            }
            if (TryFirstHop(g, here, target, out RM_ShadePatchGraph.Edge hop))
            {
                IntVec3 from = map.cellIndices.IndexToCell(hop.fromCell);
                IntVec3 to = map.cellIndices.IndexToCell(hop.toCell);
                if (pawn.CanReach(to, PathEndMode.OnCell, Danger.Deadly))
                {
                    return RM_ShadeHop.MakeDash(from, to, ext.rimPauseTicks.RandomInRange);
                }
            }
            // No chain of patches reaches the ring: it swims the gap anyway,
            // spending water every metre.
            return Goto(road.targetCell);
        }

        private static Job Goto(IntVec3 cell)
        {
            Job job = JobMaker.MakeJob(JobDefOf.Goto, cell);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            job.expiryInterval = 600; // re-plan: a leap chance, a ring re-pick
            job.checkOverrideOnExpire = true;
            return job;
        }

        /// <summary>Dijkstra over the patch graph; the first edge of the
        /// cheapest route from `from` to `to`.</summary>
        private static bool TryFirstHop(RM_ShadePatchGraph g, int from, int to, out RM_ShadePatchGraph.Edge first)
        {
            first = default;
            int n = g.PatchCount;
            int[] dist = new int[n];
            int[] firstEdgeOwner = new int[n];
            RM_ShadePatchGraph.Edge[] firstEdge = new RM_ShadePatchGraph.Edge[n];
            bool[] done = new bool[n];
            for (int i = 0; i < n; i++)
            {
                dist[i] = int.MaxValue;
                firstEdgeOwner[i] = -1;
            }
            dist[from] = 0;
            for (int iter = 0; iter < n; iter++)
            {
                int u = -1, bu = int.MaxValue;
                for (int i = 0; i < n; i++)
                {
                    if (!done[i] && dist[i] < bu)
                    {
                        bu = dist[i];
                        u = i;
                    }
                }
                if (u < 0)
                {
                    break;
                }
                if (u == to)
                {
                    break;
                }
                done[u] = true;
                List<RM_ShadePatchGraph.Edge> edges = g.patches[u].edges;
                for (int k = 0; k < edges.Count; k++)
                {
                    RM_ShadePatchGraph.Edge e = edges[k];
                    int nd = bu + e.cost;
                    if (nd < dist[e.to])
                    {
                        dist[e.to] = nd;
                        firstEdge[e.to] = u == from ? e : firstEdge[u];
                        firstEdgeOwner[e.to] = 1;
                    }
                }
            }
            if (dist[to] == int.MaxValue || firstEdgeOwner[to] < 0)
            {
                return false;
            }
            first = firstEdge[to];
            return true;
        }

        /// <summary>Flesh standing on the dew line within the leap's reach.
        /// Droids carry no water and are never taken (the shipped rule).</summary>
        private static Job TryLeap(Pawn pawn, RM_ShadePatchGraph g)
        {
            if (pawn.abilities == null)
            {
                return null;
            }
            AbilityDef def = DefDatabase<AbilityDef>.GetNamedSilentFail(LeapAbility);
            Ability ability = def != null ? pawn.abilities.GetAbility(def) : null;
            if (ability == null || ability.OnCooldown)
            {
                return null;
            }
            float range = ability.verb?.EffectiveRange ?? 9.9f;
            Map map = pawn.Map;
            Pawn best = null;
            float bestD = float.MaxValue;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == pawn || p.Dead || !p.RaceProps.IsFlesh)
                {
                    continue;
                }
                float d = (p.Position - pawn.Position).LengthHorizontal;
                if (d > range || d >= bestD || !OnDewLine(g, p.Position, map))
                {
                    continue;
                }
                LocalTargetInfo t = p;
                if (!ability.CanApplyOn(t) || !ability.AICanTargetNow(t)
                    || !GenSight.LineOfSight(pawn.Position, p.Position, map))
                {
                    continue;
                }
                best = p;
                bestD = d;
            }
            return best != null ? ability.GetJob(best, best) : null;
        }

        /// <summary>From the map component's slow tick: roots the swimmer once
        /// it stands at the centre of its ring, then empties the patch.</summary>
        public static void CheckArrival(RSW_MapComponent_SwimmerRoad road)
        {
            Pawn s = road.swimmer;
            Map map = s.Map;
            RM_ShadePatchGraph g = Graph(map);
            if (g == null)
            {
                return;
            }
            int target = TargetPatch(road, g, map);
            if (target == RM_ShadePatchGraph.NoPatch
                || g.PatchAt(map.cellIndices.CellToIndex(s.Position)) != target
                || (s.Position - road.targetCell).LengthHorizontal > road.Extension.rootWithinCells)
            {
                return;
            }
            CompDevourer devourer = s.TryGetComp<CompDevourer>();
            CompSarlaccSwimmer comp = s.TryGetComp<CompSarlaccSwimmer>();
            if (comp == null || (devourer != null && devourer.Digesting))
            {
                return; // it roots once the press is empty
            }
            // Tenants first, while the graph still knows the patch (the new
            // anchored mouth is an edifice and will cut it at the next recompute).
            List<Pawn> tenants = new List<Pawn>();
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p != s && p.Faction == null && p.RaceProps.Animal && !p.Downed && !p.Dead
                    && g.PatchAt(map.cellIndices.CellToIndex(p.Position)) == target)
                {
                    tenants.Add(p);
                }
            }
            string swimmerLabel = s.LabelShort;
            Thing mouth = comp.RootAtDewRing();
            if (mouth == null)
            {
                return;
            }
            road.anchored = mouth;
            road.swimmer = null;
            int fled = RSW_SarlaccSettings.rootingEvacuatesPatch ? Evacuate(tenants, g, target, mouth) : 0;
            string text = "The sarlacc swimmer has reached the biggest dew ring on the map and rooted in the middle of its shade. "
                + "It is an anchored sarlacc now, a permanent well with a mouth, and it will not move again."
                + (fled > 0 ? "\n\nEvery creature sheltering in that shade (" + fled + ") broke from it at once." : "");
            Find.LetterStack.ReceiveLetter("Sarlacc rooted: " + swimmerLabel, text, LetterDefOf.NeutralEvent, mouth);
        }

        private static int Evacuate(List<Pawn> tenants, RM_ShadePatchGraph g, int patch, Thing mouth)
        {
            int fled = 0;
            List<Thing> threats = new List<Thing> { mouth };
            for (int i = 0; i < tenants.Count; i++)
            {
                Pawn p = tenants[i];
                if (!p.Spawned || p.jobs == null)
                {
                    continue;
                }
                Job job = null;
                if (RM_ShadeHop.TryFindHop(p, g, patch, int.MaxValue / 4, out IntVec3 rim, out IntVec3 landing))
                {
                    job = RM_ShadeHop.MakeDash(p.Position, landing, 0);
                    job.locomotionUrgency = LocomotionUrgency.Sprint;
                }
                else
                {
                    IntVec3 dest = CellFinderLoose.GetFleeDestAnimal(p, threats, 23f);
                    if (dest.IsValid && dest != p.Position)
                    {
                        job = JobMaker.MakeJob(JobDefOf.Flee, dest, mouth);
                    }
                }
                if (job != null)
                {
                    p.jobs.StartJob(job, JobCondition.InterruptForced);
                    fled++;
                }
            }
            return fled;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_EVENT_CREATURES_REMAINDER_1 §1 — the swimmer comes to root.
    // A Stillsand incident: one sarlacc swimmer, once per map, comes up at the map edge
    // and swims for the LARGEST buried seep (the sarlacc seep precious cave's brine pool,
    // marked by RSW_DeepDesertSeep) and roots there. It reuses the road's map component,
    // job giver and the swimmer comp's rooting; what it adds is the target finder (seeps,
    // not dew rings) and the worker. Needs no shade graph and no Creature Behaviors.
    // Sign (owner: nothing vanishes unseen): the arrival letter names the seep, the take
    // signs are the comp's, and the rooting is a letter naming where.
    // Gate: biomes by defName on the IncidentDef extension (the Long Shade pattern).
    // ════════════════════════════════════════════════════════════════════

    public class RSW_IncidentWorker_SwimmerSeep : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RSW_SarlaccSettings.swimmerSeepEnabled)
            {
                return false;
            }
            Map map = parms.target as Map;
            RSW_SwimmerRoadExtension ext = def.GetModExtension<RSW_SwimmerRoadExtension>();
            if (map == null || ext == null || map.Biome == null || !ext.biomes.Contains(map.Biome.defName))
            {
                return false;
            }
            RSW_MapComponent_SwimmerRoad road = RSW_MapComponent_SwimmerRoad.For(map);
            if (road == null || road.fired || DefDatabase<PawnKindDef>.GetNamedSilentFail(ext.pawnKind) == null)
            {
                return false;
            }
            return RSW_SwimmerSeepLogic.TryPickSeep(map, ext, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RSW_SwimmerRoadExtension ext = def.GetModExtension<RSW_SwimmerRoadExtension>();
            RSW_MapComponent_SwimmerRoad road = RSW_MapComponent_SwimmerRoad.For(map);
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(ext.pawnKind);
            if (road == null || road.fired || kind == null || !RSW_SwimmerSeepLogic.TryPickSeep(map, ext, out IntVec3 seep)
                || !RSW_SwimmerSeepLogic.TryFindEntry(map, seep, out IntVec3 entry))
            {
                return false;
            }
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null));
            if (GenSpawn.Spawn(pawn, entry, map) == null)
            {
                return false;
            }
            road.fired = true;
            road.seepMode = true;
            road.swimmer = pawn;
            road.targetCell = seep;
            road.incidentDefName = def.defName;
            SendStandardLetter(def.letterLabel, def.letterText, def.letterDef, parms,
                new LookTargets(new TargetInfo(seep, map)));
            return true;
        }
    }

    public static class RSW_SwimmerSeepLogic
    {
        /// <summary>The largest seep: the RSW_DeepDesertSeep marker with the most
        /// seepTerrain cells around it (ties: first found). A marker with no terrain
        /// scores 0 and still qualifies, so a map seeded by hand is not refused.</summary>
        public static bool TryPickSeep(Map map, RSW_SwimmerRoadExtension ext, out IntVec3 seep)
        {
            seep = IntVec3.Invalid;
            ThingDef marker = ext.seepMarker.NullOrEmpty() ? null : DefDatabase<ThingDef>.GetNamedSilentFail(ext.seepMarker);
            if (marker == null)
            {
                return false;
            }
            TerrainDef pool = ext.seepTerrain.NullOrEmpty() ? null : DefDatabase<TerrainDef>.GetNamedSilentFail(ext.seepTerrain);
            int best = -1;
            List<Thing> markers = map.listerThings.ThingsOfDef(marker);
            for (int i = 0; i < markers.Count; i++)
            {
                Thing m = markers[i];
                if (!m.Spawned)
                {
                    continue;
                }
                int score = 0;
                if (pool != null)
                {
                    foreach (IntVec3 c in GenRadial.RadialCellsAround(m.Position, ext.seepScoreRadius, true))
                    {
                        if (c.InBounds(map) && c.GetTerrain(map) == pool)
                        {
                            score++;
                        }
                    }
                }
                if (score > best)
                {
                    best = score;
                    seep = m.Position;
                }
            }
            return seep.IsValid;
        }

        /// <summary>A walkable edge cell that can reach the seep, as far from it as a few tries find.</summary>
        public static bool TryFindEntry(Map map, IntVec3 seep, out IntVec3 entry)
        {
            entry = IntVec3.Invalid;
            float bestD = -1f;
            for (int i = 0; i < 12; i++)
            {
                if (!CellFinder.TryFindRandomEdgeCellWith(
                        c => c.Standable(map) && !c.Fogged(map)
                             && map.reachability.CanReach(c, seep, PathEndMode.OnCell, TraverseMode.PassDoors, Danger.Deadly),
                        map, 0f, out IntVec3 c2))
                {
                    continue;
                }
                float d = (c2 - seep).LengthHorizontalSquared;
                if (d > bestD)
                {
                    bestD = d;
                    entry = c2;
                }
            }
            return entry.IsValid;
        }

        public static Job NextJob(Pawn pawn, RSW_MapComponent_SwimmerRoad road)
        {
            CompDevourer devourer = pawn.TryGetComp<CompDevourer>();
            if (devourer != null && devourer.Digesting)
            {
                return null;
            }
            if (!road.targetCell.IsValid || (pawn.Position - road.targetCell).LengthHorizontal <= road.Extension.rootWithinCells)
            {
                return null; // arrived: CheckArrival roots it on the next slow tick
            }
            Job job = JobMaker.MakeJob(JobDefOf.Goto, road.targetCell);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            job.expiryInterval = 600;
            job.checkOverrideOnExpire = true;
            return job;
        }

        /// <summary>From the map component's slow tick: roots the swimmer once it is at the seep.</summary>
        public static void CheckArrival(RSW_MapComponent_SwimmerRoad road)
        {
            Pawn s = road.swimmer;
            if (s == null || !s.Spawned || !road.targetCell.IsValid
                || (s.Position - road.targetCell).LengthHorizontal > road.Extension.rootWithinCells)
            {
                return;
            }
            CompDevourer devourer = s.TryGetComp<CompDevourer>();
            CompSarlaccSwimmer comp = s.TryGetComp<CompSarlaccSwimmer>();
            if (comp == null || (devourer != null && devourer.Digesting))
            {
                return;
            }
            string label = s.LabelShort;
            Thing mouth = comp.RootAtSeep();
            if (mouth == null)
            {
                return;
            }
            road.anchored = mouth;
            road.swimmer = null;
            Find.LetterStack.ReceiveLetter("Sarlacc rooted: " + label,
                "The sarlacc swimmer has reached the seep it swam for and rooted over the water. It is an anchored sarlacc now, "
                + "a permanent well with a mouth, and it will not move again.",
                LetterDefOf.NeutralEvent, mouth);
        }
    }
}
