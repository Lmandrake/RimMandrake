using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_MIDDENS_SPENT_BUILD_1 — map generation for the lee-side middens.
    //
    //   RM_GenStep_Middens      seeds old heaps at the DOWN-SUN end of small rock outcrops
    //                           (the lee a rock throws along the pinned sun, read from the
    //                           shade grid's SunShadowDirection and confirmed with ShadeAt).
    //   RM_GenStep_CleanPatches puts a visible "unnaturally clean" patch on the ground, with an
    //                           inspect line, at every shade patch that a mirrak or a gulloth
    //                           (rooted-sarlacc family) lairs in. It runs after Animals so the
    //                           lairing animals exist; the patch graph is the same one the Crawler
    //                           Road uses (RM_LongShadeMapgen.Build). Owner card 2026-10-08.
    //
    // Both are named in RM_LongShade's extraGenSteps only, and each has its Mod Settings toggle.
    // All numbers are PROVISIONAL.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GenStep_Middens : GenStep
    {
        public IntRange count = new IntRange(2, 5);
        /// <summary>An outcrop is "small" and "old" when at most this many rock cells lie within radius 2 of the rock cell.</summary>
        public int maxRockNeighbours = 12;
        public int leeReach = 2;
        public float minShade = 0.5f;
        public float minSpacing = 16f;

        public override int SeedPart => 847261903;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.middenMapgenEnabled
                || !RM_LongShadeMapgen.CreatureBehaviorsActive)
            {
                return;
            }
            ThingDef heapDef = RM_LongShadeMiddenDefOf.RM_LongShadeMidden;
            CompProperties_RM_MiddenHeap props = heapDef?.GetCompProperties<CompProperties_RM_MiddenHeap>();
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (props == null || grid == null || !grid.SunHeatActive || !grid.IsDirectional)
            {
                return;
            }
            grid.Recompute();
            Vector2 dir = grid.SunShadowDirection;
            if (dir.sqrMagnitude < 0.0001f)
            {
                return;
            }
            dir.Normalize();

            List<IntVec3> candidates = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (!IsRock(c, map) || RM_LongShadeKernel.RockNeighbourCount(c.x, c.z, 2, (x, z) => IsRock(new IntVec3(x, 0, z), map)) > maxRockNeighbours)
                {
                    continue;
                }
                for (int reach = 1; reach <= leeReach; reach++)
                {
                    IntVec3 l = new IntVec3(c.x + Mathf.RoundToInt(dir.x * reach), 0, c.z + Mathf.RoundToInt(dir.y * reach));
                    if (l.InBounds(map) && LeeOk(l, map, grid))
                    {
                        candidates.Add(l);
                        break;
                    }
                }
            }
            int want = count.RandomInRange;
            List<IntVec3> placed = new List<IntVec3>();
            for (int tries = 0; tries < 200 && placed.Count < want && candidates.Count > 0; tries++)
            {
                IntVec3 at = candidates.RandomElement();
                if (!placed.TrueForAll(p => RM_LongShadeKernel.SpacingOk(p.DistanceTo(at), minSpacing)) || !LeeOk(at, map, grid))
                {
                    continue;
                }
                Thing heap = GenSpawn.Spawn(heapDef, at, map, WipeMode.Vanish);
                RM_CompMiddenHeap comp = heap.TryGetComp<RM_CompMiddenHeap>();
                if (comp != null)
                {
                    // an old heap: the wind and the vrekka have been at it for a long time
                    comp.layers = Rand.RangeInclusive(RM_LongShadeKernel.ClampStartLayers(props.startLayers, props.maxLayers), props.maxLayers);
                    comp.lastTendTick = Find.TickManager.TicksGame;
                }
                placed.Add(at);
            }
        }

        private static bool IsRock(IntVec3 c, Map map)
        {
            if (!c.InBounds(map)) return false;
            Building b = c.GetEdifice(map);
            return b != null && b.def.building != null && b.def.building.isNaturalRock;
        }

        private bool LeeOk(IntVec3 c, Map map, RM_MapComponent_ShadeGrid grid)
        {
            if (!c.Standable(map) || c.Roofed(map) || c.GetEdifice(map) != null || c.GetFirstItem(map) != null) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater || !t.affordances.Contains(TerrainAffordanceDefOf.Light)) return false;
            return grid.ShadeAt(c) >= minShade;
        }
    }

    public class RM_GenStep_CleanPatches : GenStep
    {
        public ThingDef markerDef;
        public List<string> lairRaces = new List<string>();
        public int patchCapCells = 40;

        public override int SeedPart => 392718451;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.cleanPatchTellEnabled
                || markerDef == null || !RM_LongShadeMapgen.CreatureBehaviorsActive)
            {
                return;
            }
            RM_LongShadeMapgen.Survey s = RM_LongShadeMapgen.Build(map, patchCapCells);
            if (s == null || s.graph.PatchCount == 0)
            {
                return;
            }
            HashSet<int> done = new HashSet<int>();
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Faction != null || !lairRaces.Contains(p.def.defName)) continue;
                int idx = map.cellIndices.CellToIndex(p.Position);
                int patch = s.graph.PatchAt(idx);
                if (patch < 0 || !done.Add(patch)) continue;
                IntVec3 at = FindCell(map, p.Position, s.graph, patch);
                if (at.IsValid) GenSpawn.Spawn(markerDef, at, map, WipeMode.Vanish);
            }
        }

        /// <summary>The standable, unbuilt cell of the creature's own patch nearest the creature.</summary>
        private static IntVec3 FindCell(Map map, IntVec3 near, RM_ShadePatchGraph g, int patch)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, 6f, true))
            {
                if (c.InBounds(map) && g.PatchAt(map.cellIndices.CellToIndex(c)) == patch && c.Standable(map)
                    && c.GetEdifice(map) == null && !c.GetThingList(map).Exists(t => t.def.category == ThingCategory.Pawn))
                {
                    return c;
                }
            }
            return IntVec3.Invalid;
        }
    }

    /// <summary>The inspect line on a clean patch: ground a lairing animal keeps scoured.</summary>
    public class CompProperties_RM_CleanPatchTell : CompProperties
    {
        public string line = "Unnaturally clean.";
        public CompProperties_RM_CleanPatchTell() { compClass = typeof(RM_CompCleanPatchTell); }
    }

    public class RM_CompCleanPatchTell : ThingComp
    {
        public override string CompInspectStringExtra()
        {
            return ((CompProperties_RM_CleanPatchTell)props).line;
        }
    }
}
