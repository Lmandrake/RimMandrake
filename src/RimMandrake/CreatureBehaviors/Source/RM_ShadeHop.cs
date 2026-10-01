using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 §5: rest, dash, rest. §6: the dash ring.
    //
    // The owner's condition: "a tad boring unless we get really strict about
    // the dashing animal behavior." So on a sun-heat map a wild animal never
    // ambles across open sun:
    //   • In the sun, it sprints to the nearest shade within its dash range
    //     (RM_JobGiver_SunEscape, at Animal_PreMain). This runs after
    //     mental states, lord duties and roping, and before needs, so a
    //     grazer steps out to eat and then dashes back.
    //   • In shade, it rests while hot. Otherwise it sometimes picks a
    //     neighbouring patch in the shade-patch graph within dash range,
    //     walks to its own rim, pauses there, and sprints across
    //     (RM_JobGiver_ShadeHop at Animal_PreWander, ahead of every wander
    //     node). With no hop in range it rests or mills about inside its
    //     patch, and never wanders out.
    // Dash range comes from tranche 1's exposure model: full-sun felt heat
    // (body-size scaled), vanilla's Heatstroke rate at that heat, a severity
    // budget, and the animal's own sprint speed (RM_DashMath).
    //
    // Only wild animals are affected: no faction, which rules out tamed and
    // drafted animals, and not in a mental state, which rules out manhunters.
    // Fleeing and melee reactions are started directly or sit earlier in the
    // tree, so they keep precedence. Where the biome has no
    // RM_SunHeatExtension, or the heat is ambient, every entry point returns
    // at its first check, and the patch graph is never built.
    //
    // The mirrak counts (LONGSHADE_BEDAZZLE_MECHANICS_1): a lying
    // false-shade pawn is a destination and a resting place, exactly as the
    // shade it pretends to be.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ShadeHop
    {
        private const float SprintFactor = 0.75f; // Pawn_PathFollower.CostToMoveIntoCell
        private const float JogFactor = 1f;

        private static readonly List<Candidate> candidates = new List<Candidate>();

        private struct Candidate
        {
            public IntVec3 from;
            public IntVec3 to;
            public float weight;
        }

        /// <summary>The grid and extension when this pawn should hop, else false.</summary>
        public static bool Eligible(Pawn pawn, out RM_MapComponent_ShadeGrid grid, out RM_ShadePatchGraph graph)
        {
            grid = null;
            graph = null;
            if (!RM_CreatureBehaviorsSettings.shadeHopEnabled || pawn == null || !pawn.Spawned)
            {
                return false;
            }
            if (pawn.Faction != null || !pawn.RaceProps.Animal || pawn.Downed || pawn.InMentalState
                || pawn.Drafted || pawn.roping?.IsRoped == true)
            {
                return false;
            }
            RM_SunDashExtension race = pawn.def.GetModExtension<RM_SunDashExtension>();
            if (race != null && race.exempt)
            {
                return false;
            }
            grid = RM_SunHeatPatches.ActiveGridFor(pawn);
            if (grid == null || !grid.ShadeHopsApply)
            {
                return false;
            }
            graph = grid.PatchGraph;
            return graph != null;
        }

        /// <summary>How far (cost units, 10 per cell) this pawn can cross
        /// open sun and still meet its heat budget. The budget is net of any
        /// Heatstroke it already carries.</summary>
        public static int RangeCost(Pawn pawn, RM_SunHeatExtension ext, float exposure, float budget, float urgencyFactor,
            float multiplier, float minCells, float maxCells)
        {
            float size = RM_SunHeatMath.BodySizeFactor(pawn.BodySize, ext.bodySizeExponent,
                ext.minBodySizeFactor, ext.maxBodySizeFactor);
            // STILLSAND_SUN_FROM_LATITUDE_1: the map's offset (by sun angle where the biome scales it).
            float baseOffset = RM_MapComponent_ShadeGrid.For(pawn.Map)?.EffectiveHeatOffsetC ?? ext.heatOffsetC;
            float offset = RM_SunHeatMath.HeatOffset(exposure, baseOffset, RM_CreatureBehaviorsSettings.sunHeatStrength,
                size, ext.maxHeatOffsetC);
            float felt = pawn.Map.mapTemperature.OutdoorTemp + offset;
            float safeMax = pawn.SafeTemperatureRange().max;
            float curved = HediffGiver_Heat.TemperatureOverageAdjustmentCurve.Evaluate(Mathf.Max(0f, felt - safeMax));
            Hediff stroke = pawn.health?.hediffSet?.GetFirstHediffOfDef(HediffDefOf.Heatstroke);
            float left = budget - (stroke?.Severity ?? 0f);
            int ticks = RM_DashMath.ToleratedTicks(felt, safeMax, curved, left);
            float tpc = RM_DashMath.TicksPerCell(pawn.TicksPerMoveCardinal, urgencyFactor);
            return RM_DashMath.DashRangeCost(ticks, tpc, multiplier, minCells, maxCells);
        }

        public static int AnimalDashCost(Pawn pawn, RM_SunHeatExtension ext)
        {
            float race = pawn.def.GetModExtension<RM_SunDashExtension>()?.rangeFactor ?? 1f;
            return RangeCost(pawn, ext, 1f, ext.dashHeatstrokeBudget, SprintFactor,
                RM_CreatureBehaviorsSettings.shadeHopRangeMultiplier * race, ext.minDashCells, ext.maxDashCells);
        }

        /// <summary>§6: a colonist's go-and-return budget in open sun, net
        /// of the shade it carries (a parasol).</summary>
        public static int ColonistRingCost(Pawn pawn, RM_MapComponent_ShadeGrid grid)
        {
            RM_SunHeatExtension ext = grid.HeatExtension;
            float exposure = RM_SunHeatMath.WithCover(1f, RM_ShadeGear.WornCover(pawn, grid.GearKind, out _));
            return RangeCost(pawn, ext, exposure, ext.ringHeatstrokeBudget, JogFactor, 1f, 0f, ext.ringMaxCells);
        }

        private static RM_MapComponent_FalseShade Lures(Map map)
        {
            return RM_CreatureBehaviorsSettings.falseShadeAmbushEnabled ? map.GetComponent<RM_MapComponent_FalseShade>() : null;
        }

        /// <summary>Shelter as the pawn perceives it: a real shade patch, or a
        /// lying mirrak's false shade.</summary>
        public static bool InPerceivedShade(Pawn pawn, RM_MapComponent_ShadeGrid grid, RM_ShadePatchGraph graph, out int patch)
        {
            Map map = pawn.Map;
            patch = graph.PatchAt(map.cellIndices.CellToIndex(pawn.Position));
            if (patch != RM_ShadePatchGraph.NoPatch)
            {
                return true;
            }
            // LONGSHADE_GPT_ENRICHMENT_1 §2: a giant's moving shadow is real
            // shade, though the patch graph (rebuilt every 2000 ticks) never
            // holds it: an animal standing in it is sheltered, not "caught in
            // the open", so it rests there instead of sprinting away.
            if (grid.MovingShadeAt(pawn.Position) >= 1f - grid.HeatExtension.shadeExposureMax)
            {
                return true;
            }
            RM_MapComponent_FalseShade fs = Lures(map);
            return fs != null && fs.FalseShadeAt(pawn.Position) >= 1f - grid.HeatExtension.shadeExposureMax;
        }

        /// <summary>A cell beside a lying false-shade pawn, reachable within
        /// maxCost of `from`.</summary>
        private static void AddLureCandidates(Pawn pawn, IntVec3 from, int maxCost, float weight)
        {
            RM_MapComponent_FalseShade fs = Lures(pawn.Map);
            if (fs == null)
            {
                return;
            }
            IReadOnlyList<Pawn> lures = fs.Lures;
            for (int i = 0; i < lures.Count; i++)
            {
                Pawn lure = lures[i];
                if (lure == pawn || !lure.Spawned || lure.Map != pawn.Map)
                {
                    continue;
                }
                IntVec3 at = lure.Position;
                if (RM_ShadePatchGraph.Octile(from.x, from.z, at.x, at.z) > maxCost || (at - pawn.Position).LengthHorizontalSquared <= 2.25f)
                {
                    continue;
                }
                if (CellFinder.TryFindRandomCellNear(at, pawn.Map, 1, c => c != at && c.Standable(pawn.Map), out IntVec3 beside))
                {
                    candidates.Add(new Candidate { from = from, to = beside, weight = weight });
                }
            }
        }

        /// <summary>In the sun: the nearest shade within dash range (graph
        /// field or a lure), or false.</summary>
        public static bool TryFindEscape(Pawn pawn, RM_ShadePatchGraph graph, int range, out IntVec3 target)
        {
            target = IntVec3.Invalid;
            Map map = pawn.Map;
            int idx = map.cellIndices.CellToIndex(pawn.Position);
            int best = int.MaxValue;
            int d = graph.distToShade[idx];
            if (d != RM_ShadePatchGraph.Unreached && d <= range && graph.nearestShade[idx] >= 0)
            {
                IntVec3 c = map.cellIndices.IndexToCell(graph.nearestShade[idx]);
                if (pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    target = c;
                    best = d;
                }
            }
            candidates.Clear();
            AddLureCandidates(pawn, pawn.Position, range, 1f);
            for (int i = 0; i < candidates.Count; i++)
            {
                IntVec3 c = candidates[i].to;
                int cost = RM_ShadePatchGraph.Octile(pawn.Position.x, pawn.Position.z, c.x, c.z);
                if (cost < best && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    best = cost;
                    target = c;
                }
            }
            candidates.Clear();
            return target.IsValid;
        }

        /// <summary>In a patch: a neighbouring patch (or a lure) within dash
        /// range, weighted toward bigger patches.</summary>
        public static bool TryFindHop(Pawn pawn, RM_ShadePatchGraph graph, int patch, int range,
            out IntVec3 rim, out IntVec3 landing)
        {
            rim = IntVec3.Invalid;
            landing = IntVec3.Invalid;
            Map map = pawn.Map;
            candidates.Clear();
            if (patch != RM_ShadePatchGraph.NoPatch)
            {
                List<RM_ShadePatchGraph.Edge> edges = graph.patches[patch].edges;
                for (int i = 0; i < edges.Count; i++)
                {
                    RM_ShadePatchGraph.Edge e = edges[i];
                    if (e.cost > range)
                    {
                        continue;
                    }
                    candidates.Add(new Candidate
                    {
                        from = map.cellIndices.IndexToCell(e.fromCell),
                        to = map.cellIndices.IndexToCell(e.toCell),
                        weight = Mathf.Sqrt(graph.patches[e.to].cellCount),
                    });
                }
            }
            AddLureCandidates(pawn, pawn.Position, range, 1.5f);
            bool found = false;
            for (int tries = 0; tries < 3 && candidates.Count > 0; tries++)
            {
                if (!candidates.TryRandomElementByWeight(c => c.weight, out Candidate pick))
                {
                    break;
                }
                if (pawn.CanReach(pick.to, PathEndMode.OnCell, Danger.Deadly))
                {
                    rim = pick.from;
                    landing = pick.to;
                    found = true;
                    break;
                }
                candidates.Remove(pick);
            }
            candidates.Clear();
            return found;
        }

        public static Job MakeDash(IntVec3 rim, IntVec3 landing, int pauseTicks)
        {
            Job job = JobMaker.MakeJob(RM_JobDefOf.RM_ShadeDash, rim, landing);
            job.count = Mathf.Max(0, pauseTicks); // the pause at the rim, in ticks
            job.locomotionUrgency = LocomotionUrgency.Walk;
            return job;
        }

        public static Job MakeRest(Pawn pawn, RM_SunHeatExtension ext)
        {
            Job job = JobMaker.MakeJob(JobDefOf.Wait, pawn.Position);
            job.expiryInterval = ext.restTicks.RandomInRange;
            // Lie down when tired, as a resting animal does; stand otherwise.
            job.forceSleep = pawn.needs?.rest != null && pawn.needs.rest.CurLevelPercentage < 0.75f;
            return job;
        }
    }

    /// <summary>Animal_PreMain: a wild animal standing in open sun sprints
    /// to the nearest shade it can reach within its dash range.</summary>
    public class RM_JobGiver_SunEscape : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_ShadeHop.Eligible(pawn, out RM_MapComponent_ShadeGrid grid, out RM_ShadePatchGraph graph))
            {
                return null;
            }
            if (RM_ShadeHop.InPerceivedShade(pawn, grid, graph, out _))
            {
                return null;
            }
            // Caught in the open, an animal runs for the nearest shade up to
            // the full dash cap, whatever budget it has left: staying out
            // there is worse.
            int reach = Mathf.RoundToInt(grid.HeatExtension.maxDashCells * RM_ShadePatchGraph.CardinalCost);
            if (!RM_ShadeHop.TryFindEscape(pawn, graph, reach, out IntVec3 target))
            {
                return null; // no shade in reach: vanilla behaviour, with sun-cost pathing
            }
            return RM_ShadeHop.MakeDash(pawn.Position, target, 0);
        }
    }

    /// <summary>Animal_PreWander: in shade, rest while hot, else hop to a
    /// neighbouring patch (walk to the rim, pause, sprint), else stay in the
    /// patch. Never a wander into the sun.</summary>
    public class RM_JobGiver_ShadeHop : ThinkNode_JobGiver
    {
        private const int MillRadius = 6;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_ShadeHop.Eligible(pawn, out RM_MapComponent_ShadeGrid grid, out RM_ShadePatchGraph graph))
            {
                return null;
            }
            RM_SunHeatExtension ext = grid.HeatExtension;
            if (!RM_ShadeHop.InPerceivedShade(pawn, grid, graph, out int patch))
            {
                // Caught in the sun at wander time (the PreMain escape found
                // nothing in reach). Let vanilla wander, with sun-cost pathing.
                return null;
            }
            // Hot = carrying half its dash budget or more in Heatstroke. That
            // only drains below the comfortable max, so on a hot map a
            // cooked animal stays in the shade.
            bool hot = (pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.Heatstroke)?.Severity ?? 0f)
                       >= ext.dashHeatstrokeBudget * 0.5f;
            if (hot || !Rand.Chance(ext.hopChance))
            {
                return RM_ShadeHop.MakeRest(pawn, ext);
            }
            int range = RM_ShadeHop.AnimalDashCost(pawn, ext);
            if (range > 0 && RM_ShadeHop.TryFindHop(pawn, graph, patch, range, out IntVec3 rim, out IntVec3 landing))
            {
                return RM_ShadeHop.MakeDash(rim, landing, ext.rimPauseTicks.RandomInRange);
            }
            // Nowhere in reach: mill about inside this patch, or rest.
            if (patch != RM_ShadePatchGraph.NoPatch && Rand.Bool)
            {
                Map map = pawn.Map;
                if (CellFinder.TryFindRandomCellNear(pawn.Position, map, MillRadius,
                        c => c != pawn.Position && c.Standable(map)
                             && graph.PatchAt(map.cellIndices.CellToIndex(c)) == patch
                             && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly),
                        out IntVec3 spot))
                {
                    Job walk = JobMaker.MakeJob(JobDefOf.GotoWander, spot);
                    walk.locomotionUrgency = LocomotionUrgency.Walk;
                    return walk;
                }
            }
            return RM_ShadeHop.MakeRest(pawn, ext);
        }
    }

    /// <summary>RM_ShadeDash: TargetA is the rim cell to leave from, TargetB
    /// the shade to land in, and job.count is the pause at the rim in ticks.
    /// The pawn walks to A, stands facing B for the pause, then sprints to B.
    /// The escape from open sun gives A = its own cell and a zero pause, so
    /// it simply sprints.</summary>
    public class RM_JobDriver_ShadeDash : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => pawn.Downed || pawn.InMentalState);
            Toil walk = Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            walk.AddPreInitAction(() => job.locomotionUrgency = LocomotionUrgency.Walk);
            yield return walk;

            Toil pause = ToilMaker.MakeToil("RM_ShadeDash_Pause");
            pause.initAction = () =>
            {
                pawn.pather?.StopDead();
                // LONGSHADE_GPT_ENRICHMENT_1 §3: a herd calls before it dashes.
                RM_HeatSoundscape.TryHerdCall(pawn);
            };
            pause.tickAction = () => pawn.rotationTracker.FaceCell(job.targetB.Cell);
            pause.handlingFacing = true;
            pause.defaultCompleteMode = ToilCompleteMode.Delay;
            pause.defaultDuration = Mathf.Max(1, job.count);
            if (job.count > 0)
            {
                yield return pause;
            }

            Toil sprint = Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            sprint.AddPreInitAction(() => job.locomotionUrgency = LocomotionUrgency.Sprint);
            yield return sprint;
        }
    }

    /// <summary>§6: the back-to-shade ring around a selected, drafted
    /// colonist on a sun-heat map. Drawn as field edges (GenDraw.DrawFieldEdges)
    /// round every cell it can reach and still walk back into shade within
    /// its heat budget. The cell set is cached per pawn, and rebuilt only when
    /// the pawn moves, the grid changes, or a quarter-second of game time passes.</summary>
    public static class RM_DashRing
    {
        private const int RefreshTicks = 15;
        private static readonly Color RingColor = new Color(1f, 0.62f, 0.2f, 0.9f);

        private static readonly List<int> scratch = new List<int>();

        private sealed class Cache
        {
            public IntVec3 pos;
            public int version;
            public int tick;
            public Map map;
            public readonly List<IntVec3> cells = new List<IntVec3>();
        }

        private static readonly Dictionary<int, Cache> caches = new Dictionary<int, Cache>();

        public static void Draw(Pawn pawn)
        {
            if (!RM_CreatureBehaviorsSettings.dashRingEnabled || pawn == null || !pawn.Drafted || !pawn.Spawned
                || pawn.Map != Find.CurrentMap)
            {
                return;
            }
            RM_MapComponent_ShadeGrid grid = RM_SunHeatPatches.ActiveGridFor(pawn);
            if (grid == null || !grid.ShadeHopsApply)
            {
                return;
            }
            RM_ShadePatchGraph graph = grid.PatchGraph;
            if (graph == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (caches.Count > 16)
            {
                caches.Clear();
            }
            if (!caches.TryGetValue(pawn.thingIDNumber, out Cache c))
            {
                c = new Cache { version = -1 };
                caches[pawn.thingIDNumber] = c;
            }
            if (c.version != grid.GridVersion || c.pos != pawn.Position || c.map != pawn.Map || now - c.tick >= RefreshTicks)
            {
                c.version = grid.GridVersion;
                c.pos = pawn.Position;
                c.map = pawn.Map;
                c.tick = now;
                c.cells.Clear();
                int range = RM_ShadeHop.ColonistRingCost(pawn, grid);
                graph.ReachableWithReturn(pawn.Map.cellIndices.CellToIndex(pawn.Position), range, scratch);
                for (int i = 0; i < scratch.Count; i++)
                {
                    c.cells.Add(pawn.Map.cellIndices.IndexToCell(scratch[i]));
                }
            }
            if (c.cells.Count > 0)
            {
                GenDraw.DrawFieldEdges(c.cells, RingColor);
            }
        }
    }
}
