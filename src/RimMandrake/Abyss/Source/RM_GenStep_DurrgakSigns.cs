using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_DURRGAK_BUILD_1 remainder: the durrgak's SIGNS on a fresh map. Report
    // blackcrags_bedazzle_review_2026-09-30.md §4 row 2: "Rings and caches spawn on the map as a
    // sign (a few RM_DurrgakCairn things and a stocked den), and the cairns go up whether or not
    // a durrgak is in sight."
    //
    // Reached only through RM_Abyss's own BiomeDef.extraGenSteps (the frozen RUT_ twin is not
    // touched), order 915: after Plants (900), before Animals (1200). Places one stocked den
    // (scrap steel + a component lying around its mouth, forbidden like ruin loot), a few shard
    // rings in a loose row near it, and on some maps a salvage cache set inside its own ring.
    // Nothing ever says who made them. Glow-berry caches are painted into the den art only:
    // no glow-berry item exists yet (slate #7 "the lamp is a crop" is unbuilt).
    // Not retroactive; setting durrgakMapSignsEnabled off = no signs on maps generated afterwards.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GenStep_DurrgakSigns : GenStep
    {
        public ThingDef denDef;
        public ThingDef cacheDef;
        public ThingDef cairnDef;
        public IntRange cairnCount = new IntRange(3, 6);
        public float cacheChance = 0.4f;
        public IntRange denSteel = new IntRange(15, 40);
        public IntRange denComponents = new IntRange(0, 2);
        public IntRange cacheSteel = new IntRange(10, 25);
        public IntRange cacheComponents = new IntRange(1, 3);
        public int edgeMargin = 12;
        public int maxTries = 300;

        public override int SeedPart => 730115294;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_AbyssSettings.durrgakMapSignsEnabled) return;
            Place(map);
        }

        /// <summary>Returns "den=<0|1> cache=<0|1> rings=<n>" for what this run actually placed.</summary>
        public string Place(Map map)
        {
            MapGenerator.TryGetVar("UsedRects", out List<CellRect> used);
            int den = 0, cache = 0, rings = 0;
            IntVec3 denCell = IntVec3.Invalid;
            if (denDef != null && TryFindSite(map, used, IntVec3.Invalid, 0f, out denCell))
            {
                Spawn(denDef, denCell, map);
                Scatter(map, denCell, ThingDefOf.Steel, denSteel.RandomInRange);
                Scatter(map, denCell, ThingDefOf.ComponentIndustrial, denComponents.RandomInRange);
                den = 1;
            }
            IntVec3 anchor = denCell.IsValid ? denCell : CellFinder.RandomCell(map);
            if (cairnDef != null)
            {
                // a loose ROW: each ring a few cells on from the last along one heading
                IntVec3 heading = GenAdj.AdjacentCells[Rand.Range(0, 8)];
                IntVec3 at = anchor + heading * 4;
                int want = cairnCount.RandomInRange;
                for (int i = 0, tries = 0; i < want && tries < want * 6; tries++)
                {
                    IntVec3 c = at + new IntVec3(Rand.RangeInclusive(-1, 1), 0, Rand.RangeInclusive(-1, 1));
                    at += heading * 3;
                    if (!Clear(c, map, used)) continue;
                    Spawn(cairnDef, c, map);
                    rings++;
                    i++;
                }
            }
            if (cacheDef != null && Rand.Chance(cacheChance)
                && TryFindSite(map, used, denCell, 25f, out IntVec3 cacheCell))
            {
                Spawn(cacheDef, cacheCell, map);
                Scatter(map, cacheCell, ThingDefOf.Steel, cacheSteel.RandomInRange);
                Scatter(map, cacheCell, ThingDefOf.ComponentIndustrial, cacheComponents.RandomInRange);
                if (cairnDef != null)
                {
                    // set squarely in the middle of a small ring of shards
                    foreach (IntVec3 off in GenAdj.DiagonalDirections)
                    {
                        IntVec3 c = cacheCell + off * 2;
                        if (Clear(c, map, used)) { Spawn(cairnDef, c, map); rings++; }
                    }
                }
                cache = 1;
            }
            return "den=" + den + " cache=" + cache + " rings=" + rings;
        }

        /// <summary>
        /// Bridge proof (jawa/static_call): run the real placement on `map` regardless of the map
        /// setting. "den=1 cache=0|1 rings=n" = what this run added.
        /// </summary>
        public static string ProofSigns(Map map)
        {
            GenStepDef def = DefDatabase<GenStepDef>.GetNamedSilentFail("RM_DurrgakSigns");
            if (map == null || !(def?.genStep is RM_GenStep_DurrgakSigns step))
            {
                return "REFUSED: no map or no RM_DurrgakSigns step";
            }
            return step.Place(map);
        }

        private bool TryFindSite(Map map, List<CellRect> used, IntVec3 awayFrom, float minDist, out IntVec3 found)
        {
            for (int t = 0; t < maxTries; t++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.CloseToEdge(map, edgeMargin)) continue;
                if (awayFrom.IsValid && c.InHorDistOf(awayFrom, minDist)) continue;
                bool ok = true;
                foreach (IntVec3 n in GenRadial.RadialCellsAround(c, 1.5f, true))
                {
                    if (!Clear(n, map, used)) { ok = false; break; }
                }
                if (!ok) continue;
                found = c;
                return true;
            }
            found = IntVec3.Invalid;
            return false;
        }

        private static bool Clear(IntVec3 c, Map map, List<CellRect> used)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null) return false;
            if (c.GetTerrain(map).passability != Traversability.Standable) return false;
            if (used != null)
            {
                foreach (CellRect r in used)
                {
                    if (r.Contains(c)) return false;
                }
            }
            foreach (Thing t in c.GetThingList(map))
            {
                if (!(t is Plant)) return false;
            }
            return true;
        }

        private static void Spawn(ThingDef def, IntVec3 c, Map map)
        {
            foreach (Thing t in new List<Thing>(c.GetThingList(map)))
            {
                if (t is Plant) t.Destroy();
            }
            GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
        }

        // the den is "lined with dropped steel and components": stacks lying around its mouth, forbidden
        private static void Scatter(Map map, IntVec3 centre, ThingDef def, int count)
        {
            if (def == null || count <= 0) return;
            int left = count;
            int stacks = 0;
            while (left > 0 && stacks < 4)
            {
                int n = Mathf.Min(left, Mathf.Max(1, Mathf.CeilToInt(count / 3f)));
                Thing thing = ThingMaker.MakeThing(def);
                thing.stackCount = n;
                if (!GenPlace.TryPlaceThing(thing, centre, map, ThingPlaceMode.Near)) return;
                thing.SetForbidden(true, false);
                left -= n;
                stacks++;
            }
        }
    }
}
