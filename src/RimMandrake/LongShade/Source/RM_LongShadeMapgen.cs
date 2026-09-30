using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_BEDAZZLE_MECHANICS_1 tranche 2 — two map-generation pieces
    // (design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md):
    //
    //   §6.4 the Crawler Road  (RM_GenStep_CrawlerRoad)
    //   §6.5 the Long Carry    (RM_GenStep_SunGraves)
    //
    // Both read SOLAR_HEAT_EXPOSURE_1's shade-patch graph (RM_ShadePatchGraph)
    // and its dash arithmetic (RM_DashMath) — reused, never re-derived. At
    // generation time no pawn exists and the grid's own lazy PatchGraph reads
    // the path grid and rooms, neither of which is settled mid-generation, so
    // RM_LongShadeMapgen builds the graph straight from the grid's layers with
    // its own terrain/edifice walk mask, and derives "a human's dash" from the
    // Human race def instead of a pawn.
    //
    // Both steps sit in RM_LongShade's extraGenSteps only (that is the biome
    // gate), and each checks its Long Shade Mod Settings toggle and that
    // mandrake.rm.creaturebehaviors is active before touching any of its types
    // (a soft reference, same as the dewfringe gate).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_LongShadeMapgen
    {
        public static bool CreatureBehaviorsActive => ModsConfig.IsActive("mandrake.rm.creaturebehaviors");

        public sealed class Survey
        {
            public RM_MapComponent_ShadeGrid grid;
            public RM_SunHeatExtension ext;
            public RM_ShadePatchGraph graph;
        }

        private static bool Walkable(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.passability == Traversability.Impassable)
            {
                return false;
            }
            Building ed = c.GetEdifice(map);
            return ed == null || ed.def.passability != Traversability.Impassable;
        }

        /// <summary>Recomputes the shade grid on the map as it stands now and
        /// builds a patch graph with the given cap (cells). Null when the map
        /// has no sun heat (the biome or the settings) or the heat is ambient.</summary>
        public static Survey Build(Map map, float capCells)
        {
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid == null || !grid.SunHeatActive || grid.HeatExtension.heatKind == RM_HeatKind.ambient)
            {
                return null;
            }
            grid.Recompute();
            RM_SunHeatExtension ext = grid.HeatExtension;
            int n = map.cellIndices.NumGridCells;
            bool[] shade = new bool[n];
            bool[] walk = new bool[n];
            foreach (IntVec3 c in map.AllCells)
            {
                int i = map.cellIndices.CellToIndex(c);
                bool w = Walkable(c, map);
                walk[i] = w;
                if (!w)
                {
                    continue;
                }
                RoofDef roof = map.roofGrid.RoofAt(c);
                float ex = RM_SunHeatMath.Exposure(ext.heatKind, true, grid.RoofShadeAt(c), roof != null && roof.isThickRoof,
                    grid.CastShadeAt(c), grid.GearShadeAt(c));
                shade[i] = ex <= ext.shadeExposureMax;
            }
            int cap = Mathf.CeilToInt(Mathf.Max(1f, capCells)) * RM_ShadePatchGraph.CardinalCost;
            return new Survey
            {
                grid = grid,
                ext = ext,
                graph = RM_ShadePatchGraph.Build(map.Size.x, map.Size.z, shade, walk, cap, ext.minPatchCells),
            };
        }

        /// <summary>A baseline human's go-and-return budget in open sun on
        /// this map, in cost units (10 per cell): the §6 ring arithmetic
        /// (RM_ShadeHop.ColonistRingCost) with the Human race def standing in
        /// for a pawn. `cover` is worn shade (0 bare, a parasol's depth).</summary>
        public static int HumanRingCost(Map map, RM_SunHeatExtension ext, float cover)
        {
            ThingDef human = ThingDefOf.Human;
            float size = RM_SunHeatMath.BodySizeFactor(human.race.baseBodySize, ext.bodySizeExponent,
                ext.minBodySizeFactor, ext.maxBodySizeFactor);
            float exposure = RM_SunHeatMath.WithCover(1f, cover);
            float offset = RM_SunHeatMath.HeatOffset(exposure, ext.heatOffsetC, RM_CreatureBehaviorsSettings.sunHeatStrength,
                size, ext.maxHeatOffsetC);
            float felt = map.mapTemperature.OutdoorTemp + offset;
            float safeMax = GenTemperature.SafeTemperatureRange(human).max;
            float curved = HediffGiver_Heat.TemperatureOverageAdjustmentCurve.Evaluate(Mathf.Max(0f, felt - safeMax));
            int ticks = RM_DashMath.ToleratedTicks(felt, safeMax, curved, ext.ringHeatstrokeBudget);
            float speed = human.GetStatValueAbstract(StatDefOf.MoveSpeed);
            float ticksPerCell = RM_DashMath.TicksPerCell(speed > 0f ? 60f / speed : 13f, 1f);
            return RM_DashMath.DashRangeCost(ticks, ticksPerCell, 1f, 0f, ext.ringMaxCells);
        }

        /// <summary>The kind-resolved shade depth of a worn shade-gear def
        /// (the parasol) made of nothing special.</summary>
        public static float GearCover(string gearDefName, RM_HeatKind kind)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(gearDefName);
            RM_CompProperties_ShadeGear p = def?.GetCompProperties<RM_CompProperties_ShadeGear>();
            return p != null ? RM_ShadeGear.DepthOf(null, p, kind) : 0f;
        }

        /// <summary>A cell near `at` where a def of this size fits on open,
        /// buildable ground with nothing standing there (plants excepted).</summary>
        public static bool TryFindSpot(Map map, IntVec3 at, IntVec2 size, int radius, out IntVec3 spot)
        {
            spot = IntVec3.Invalid;
            float best = float.MaxValue;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, radius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                CellRect r = GenAdj.OccupiedRect(c, Rot4.North, size);
                if (!r.InBounds(map) || !RectClear(map, r))
                {
                    continue;
                }
                float d = (c - at).LengthHorizontalSquared;
                if (d < best)
                {
                    best = d;
                    spot = c;
                }
            }
            return spot.IsValid;
        }

        private static bool RectClear(Map map, CellRect r)
        {
            foreach (IntVec3 c in r)
            {
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.passability == Traversability.Impassable || t.IsWater
                    || !t.affordances.Contains(TerrainAffordanceDefOf.Light))
                {
                    return false;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    ThingCategory cat = things[i].def.category;
                    if (cat != ThingCategory.Plant && cat != ThingCategory.Filth)
                    {
                        return false;
                    }
                }
            }
            return true;
        }
    }

    /// <summary>
    /// §6.4 THE CRAWLER ROAD (owner: "Cool inhabited vision"). A dotted line
    /// of wrecked machines across the widest gap on the map, each about one
    /// human dash from the next, ending (on the Star Wars layer) at a dead
    /// sandcrawler. Every wreck is shade: its staticSunShadowHeight throws a
    /// strip along the pinned sun, which the grid reads, so the chain IS a
    /// crossing in the patch graph. Stripping a wreck (deconstruct, or
    /// uninstall: the wrecks are minifiable) breaks the crossing, because the
    /// hop across the hole is longer than a dash and the shade-hop AI will not
    /// take it; reinstalling one, or pitching a shade tent in the hole, mends it.
    ///
    /// "The widest gap": the patch graph is built with edges no longer than a
    /// human dash, its patches grouped into islands by those edges, and the
    /// road is laid across the shortest open stretch between the two biggest
    /// islands — the one crossing that joins the map's shade network, and
    /// that nothing on foot can make today.
    ///
    /// linkDefs are the wrecks laid along the road (the RM layer ships
    /// RM_WreckedCart; mandrake.rsw.injections patches in the skiff and the
    /// crawler tread). terminusStep, when set, is a GenStepDef run centred on
    /// the road's last stop through a transient RM_CrawlerRoadTerminus marker
    /// (the dead crawler, a GenStep_RimplacePlan with anchorThingDef).
    /// </summary>
    public class RM_GenStep_CrawlerRoad : GenStep
    {
        public List<ThingDef> linkDefs = new List<ThingDef>();
        public GenStepDef terminusStep;
        public ThingDef terminusMarker;

        /// <summary>Link spacing as a fraction of a human's one-way dash.</summary>
        public float spacingFactor = 0.8f;
        public FloatRange spacingCells = new FloatRange(6f, 24f);

        /// <summary>A gap shorter than this many spacings needs no road.</summary>
        public float minGapSpacings = 1.5f;
        public float maxGapCells = 160f;

        public override int SeedPart => 519624113;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.crawlerRoadEnabled
                || !RM_LongShadeMapgen.CreatureBehaviorsActive)
            {
                return;
            }
            RM_CrawlerRoadLogic.Lay(this, map, parms);
        }
    }

    public static class RM_CrawlerRoadLogic
    {
        private const int RimSample = 300;

        public static void Lay(RM_GenStep_CrawlerRoad step, Map map, GenStepParams parms)
        {
            List<ThingDef> links = step.linkDefs.FindAll(d => d != null);
            if (links.Count == 0)
            {
                return;
            }
            RM_MapComponent_ShadeGrid probe = RM_MapComponent_ShadeGrid.For(map);
            if (probe == null || !probe.SunHeatActive)
            {
                return;
            }
            // The dash: a baseline human, bare-headed, crossing one way from shade
            // into shade (the ring's whole heat budget, spent on the way out).
            // Capped at the animals' own dash cap, so the herds can use the road too.
            int ringCost = RM_LongShadeMapgen.HumanRingCost(map, probe.HeatExtension, 0f);
            float dashCells = Mathf.Min(ringCost / (float)RM_ShadePatchGraph.CardinalCost,
                probe.HeatExtension.maxDashCells);
            float spacing = step.spacingCells.ClampToRange(dashCells * step.spacingFactor);
            RM_LongShadeMapgen.Survey s = RM_LongShadeMapgen.Build(map, spacing);
            if (s == null || s.graph.PatchCount < 2)
            {
                return;
            }
            RM_ShadePatchGraph g = s.graph;
            int[] island = Islands(g, out int islandCount, out long[] islandCells);
            if (islandCount < 2)
            {
                return; // the shade network is already whole: no gap to bridge
            }
            int a = -1, b = -1;
            for (int i = 0; i < islandCount; i++)
            {
                if (a < 0 || islandCells[i] > islandCells[a])
                {
                    b = a;
                    a = i;
                }
                else if (b < 0 || islandCells[i] > islandCells[b])
                {
                    b = i;
                }
            }
            List<int> rimA = RimsOf(g, island, a);
            List<int> rimB = RimsOf(g, island, b);
            if (!ClosestPair(g, rimA, rimB, out int ca, out int cb))
            {
                return;
            }
            IntVec3 from = map.cellIndices.IndexToCell(ca);
            IntVec3 to = map.cellIndices.IndexToCell(cb);
            float gap = (to - from).LengthHorizontal;
            if (gap < spacing * step.minGapSpacings || gap > step.maxGapCells)
            {
                return;
            }
            int segments = Mathf.CeilToInt(gap / spacing);
            Vector3 dir = (to - from).ToVector3() / gap;
            float stride = gap / segments;
            bool terminus = step.terminusStep != null && step.terminusMarker != null;
            int placed = 0;
            for (int k = 1; k < segments; k++)
            {
                IntVec3 at = (from.ToVector3Shifted() + dir * (stride * k)).ToIntVec3();
                if (terminus && k == segments - 1)
                {
                    break; // the last stop is the terminus, laid below
                }
                ThingDef def = links[(k - 1 + Rand.Range(0, links.Count)) % links.Count];
                if (!RM_LongShadeMapgen.TryFindSpot(map, at, def.size, 4, out IntVec3 spot))
                {
                    continue;
                }
                Thing wreck = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
                if (GenSpawn.Spawn(wreck, spot, map, Rot4.North, WipeMode.Vanish) != null)
                {
                    placed++;
                }
            }
            if (terminus && segments >= 2)
            {
                IntVec3 end = (from.ToVector3Shifted() + dir * (stride * (segments - 1))).ToIntVec3();
                LayTerminus(step, map, parms, end);
            }
            if (placed == 0)
            {
                Log.Warning("[RM LongShade] Crawler Road: a " + gap.ToString("0") + "-cell gap was found but no wreck could be placed along it.");
            }
        }

        private static void LayTerminus(RM_GenStep_CrawlerRoad step, Map map, GenStepParams parms, IntVec3 at)
        {
            if (!at.InBounds(map))
            {
                return;
            }
            Thing marker = GenSpawn.Spawn(ThingMaker.MakeThing(step.terminusMarker), at, map);
            try
            {
                step.terminusStep.genStep.Generate(map, parms);
            }
            catch (System.Exception e)
            {
                Log.Error("[RM LongShade] Crawler Road terminus " + step.terminusStep.defName + " threw: " + e);
            }
            finally
            {
                if (marker != null && marker.Spawned)
                {
                    marker.Destroy(DestroyMode.Vanish);
                }
            }
        }

        /// <summary>Groups patches joined by edges into islands.</summary>
        private static int[] Islands(RM_ShadePatchGraph g, out int count, out long[] cells)
        {
            int n = g.PatchCount;
            int[] island = new int[n];
            for (int i = 0; i < n; i++)
            {
                island[i] = -1;
            }
            List<long> size = new List<long>();
            Stack<int> stack = new Stack<int>();
            count = 0;
            for (int s = 0; s < n; s++)
            {
                if (island[s] >= 0)
                {
                    continue;
                }
                long total = 0;
                island[s] = count;
                stack.Push(s);
                while (stack.Count > 0)
                {
                    int u = stack.Pop();
                    total += g.patches[u].cellCount;
                    List<RM_ShadePatchGraph.Edge> edges = g.patches[u].edges;
                    for (int k = 0; k < edges.Count; k++)
                    {
                        int v = edges[k].to;
                        if (island[v] < 0)
                        {
                            island[v] = count;
                            stack.Push(v);
                        }
                    }
                }
                size.Add(total);
                count++;
            }
            cells = size.ToArray();
            return island;
        }

        private static List<int> RimsOf(RM_ShadePatchGraph g, int[] island, int which)
        {
            List<int> all = new List<int>();
            for (int p = 0; p < g.PatchCount; p++)
            {
                if (island[p] == which)
                {
                    all.AddRange(g.patches[p].rim);
                }
            }
            if (all.Count <= RimSample)
            {
                return all;
            }
            List<int> sample = new List<int>(RimSample);
            float step = all.Count / (float)RimSample;
            for (int i = 0; i < RimSample; i++)
            {
                sample.Add(all[(int)(i * step)]);
            }
            return sample;
        }

        private static bool ClosestPair(RM_ShadePatchGraph g, List<int> ra, List<int> rb, out int ca, out int cb)
        {
            ca = cb = -1;
            long best = long.MaxValue;
            for (int i = 0; i < ra.Count; i++)
            {
                int ax = ra[i] % g.width, az = ra[i] / g.width;
                for (int j = 0; j < rb.Count; j++)
                {
                    int dx = ax - rb[j] % g.width, dz = az - rb[j] / g.width;
                    long d = (long)dx * dx + (long)dz * dz;
                    if (d < best)
                    {
                        best = d;
                        ca = ra[i];
                        cb = rb[j];
                    }
                }
            }
            return ca >= 0;
        }
    }

    /// <summary>
    /// §6.5 THE LONG CARRY (owner: "5 Long Carry: IN, and widened to shade
    /// GEAR"). Unlooted dead lie out on the open sand where a colonist cannot
    /// walk out and back before the heat takes them, bare-headed, but can
    /// under a parasol: the grave's walk to the nearest shade is more than
    /// half a bare human's ring and no more than half a parasol-bearer's
    /// (the §6 ring arithmetic, with SHADE_GEAR_FAMILY_1's RM_Parasol depth).
    /// If the sun is too mild for gear to matter, the graves go simply far out.
    ///
    /// Each grave is a traveller (dessicated, still in their gear), their dead
    /// pack animal and its spilled load, and sometimes something to read.
    /// 🔴 Salvage and lore ONLY: the reading points at nothing. The gnomon
    /// line it once pointed to was CUT (the item's spec).
    /// </summary>
    public class RM_GenStep_SunGraves : GenStep
    {
        public IntRange count = new IntRange(1, 3);
        public List<PawnKindDef> travellerKinds = new List<PawnKindDef>();
        public List<PawnKindDef> packAnimalKinds = new List<PawnKindDef>();
        public List<ThingDefCountClass> load = new List<ThingDefCountClass>();
        public ThingDef readable;
        public float readableChance = 0.5f;
        public string gearDef = "RM_Parasol";

        /// <summary>When gear makes no difference: graves at least this
        /// fraction of the ring cap from shade.</summary>
        public float fallbackFarFraction = 0.4f;

        public override int SeedPart => 730117245;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.sunGravesEnabled
                || !RM_LongShadeMapgen.CreatureBehaviorsActive)
            {
                return;
            }
            RM_SunGravesLogic.Lay(this, map);
        }
    }

    public static class RM_SunGravesLogic
    {
        public static void Lay(RM_GenStep_SunGraves step, Map map)
        {
            RM_MapComponent_ShadeGrid probe = RM_MapComponent_ShadeGrid.For(map);
            if (probe == null || !probe.SunHeatActive || probe.HeatExtension.heatKind == RM_HeatKind.ambient)
            {
                return;
            }
            RM_SunHeatExtension ext = probe.HeatExtension;
            float cover = RM_LongShadeMapgen.GearCover(step.gearDef, ext.heatKind);
            int bare = RM_LongShadeMapgen.HumanRingCost(map, ext, 0f);
            int geared = RM_LongShadeMapgen.HumanRingCost(map, ext, cover);
            int capCost = Mathf.RoundToInt(ext.ringMaxCells * RM_ShadePatchGraph.CardinalCost);
            int lo, hi;
            if (geared > bare)
            {
                lo = bare / 2 + 1;  // out and back is beyond a bare human
                hi = geared / 2;    // but within a parasol-bearer's
            }
            else
            {
                lo = Mathf.RoundToInt(capCost * step.fallbackFarFraction);
                hi = capCost;
            }
            RM_LongShadeMapgen.Survey s = RM_LongShadeMapgen.Build(map, ext.ringMaxCells);
            if (s == null || s.graph.PatchCount == 0)
            {
                return;
            }
            List<IntVec3> band = new List<IntVec3>();
            int[] dist = s.graph.distToShade;
            foreach (IntVec3 c in map.AllCells)
            {
                int d = dist[map.cellIndices.CellToIndex(c)];
                if (d != RM_ShadePatchGraph.Unreached && d >= lo && d <= hi && c.Standable(map) && !c.Roofed(map))
                {
                    band.Add(c);
                }
            }
            int want = step.count.RandomInRange;
            List<IntVec3> used = new List<IntVec3>();
            for (int i = 0; i < want && band.Count > 0; i++)
            {
                IntVec3 at = IntVec3.Invalid;
                for (int tries = 0; tries < 20; tries++)
                {
                    IntVec3 c = band.RandomElement();
                    if (used.TrueForAll(u => (u - c).LengthHorizontalSquared > 400f))
                    {
                        at = c;
                        break;
                    }
                }
                if (!at.IsValid)
                {
                    break;
                }
                used.Add(at);
                LayGrave(step, map, at);
            }
        }

        private static void LayGrave(RM_GenStep_SunGraves step, Map map, IntVec3 at)
        {
            if (step.travellerKinds.Count > 0)
            {
                DeadAt(step.travellerKinds.RandomElement(), map, at);
            }
            if (step.packAnimalKinds.Count > 0
                && CellFinder.TryFindRandomCellNear(at, map, 2, c => c != at && c.Standable(map), out IntVec3 beast))
            {
                DeadAt(step.packAnimalKinds.RandomElement(), map, beast);
            }
            for (int i = 0; i < step.load.Count; i++)
            {
                ThingDefCountClass l = step.load[i];
                if (l?.thingDef == null || l.count <= 0)
                {
                    continue;
                }
                Thing item = ThingMaker.MakeThing(l.thingDef, l.thingDef.MadeFromStuff ? GenStuff.DefaultStuffFor(l.thingDef) : null);
                item.stackCount = Mathf.Min(l.count, l.thingDef.stackLimit);
                GenPlace.TryPlaceThing(item, at, map, ThingPlaceMode.Near);
            }
            if (step.readable != null && Rand.Chance(step.readableChance))
            {
                Thing book = ThingMaker.MakeThing(step.readable, step.readable.MadeFromStuff ? GenStuff.DefaultStuffFor(step.readable) : null);
                GenPlace.TryPlaceThing(book, at, map, ThingPlaceMode.Near);
            }
        }

        /// <summary>A wild pawn of this kind, killed where it stands and
        /// dried out — StructureInjections' PAWN state="dessicated" shape.</summary>
        private static void DeadAt(PawnKindDef kind, Map map, IntVec3 at)
        {
            Pawn pawn;
            try
            {
                pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer,
                    forceGenerateNewPawn: true));
            }
            catch (System.Exception e)
            {
                Log.Warning("[RM LongShade] Long Carry: could not generate " + kind.defName + ": " + e.Message);
                return;
            }
            if (GenSpawn.Spawn(pawn, at, map, WipeMode.Vanish) == null)
            {
                return;
            }
            pawn.Kill(null);
            pawn.Corpse?.GetComp<CompRottable>()?.RotImmediately(RotStage.Dessicated);
        }
    }
}
