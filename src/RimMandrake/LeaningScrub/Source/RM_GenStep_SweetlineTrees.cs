using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SWEETLINE_TREE_MAP_STEP_1 — owner ruling R13 (card 2026-10-03): "a rare map step plants
    // one or two sweetline trees on Leaning Scrub maps". Spec:
    // design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md §8.
    //
    // Reached through RM_LeaningScrub's own BiomeDef.extraGenSteps (engine: MapGenerator
    // concatenates them onto every map of that biome), order 910: after Plants (900) so the
    // trunk cell can be cleared of scrub, before Animals (1200). The frozen RUT_ twin is not
    // touched. Not retroactive: it runs only when a map is generated; the dev spawn remains
    // the way to place one by hand. A map with no tree is the normal case.
    //
    // Spawning runs the station comp (name, History "named", registry) and the roost comp
    // (2-3 sleeping bark-wardens); pawns spawning during map generation is normal.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GenStep_SweetlineTrees : GenStep
    {
        public ThingDef treeDef;
        public float secondTreeChance = 0.3f;
        public int edgeMargin = 15;
        public float minTreeSpacing = 40f;
        public int maxTries = 200;
        public int ancientAgeYears = 300;

        public override int SeedPart => 518733021;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (treeDef == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineStationsEnabled))
            {
                return;
            }
            float chance = Mathf.Clamp01(RM_LeaningScrubSettings.sweetlineTreeMapChance);
            if (chance <= 0f || !Rand.Chance(chance))
            {
                return;
            }
            int want = Rand.Chance(secondTreeChance) ? 2 : 1;
            List<IntVec3> placed = new List<IntVec3>();
            MapGenerator.TryGetVar("UsedRects", out List<CellRect> used);
            for (int tries = 0; tries < maxTries && placed.Count < want; tries++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (!Fits(c, map, used, placed))
                {
                    continue;
                }
                if (Plant(c, map))
                {
                    placed.Add(c);
                }
            }
        }

        /// <summary>
        /// Bridge proof (jawa/static_call): run the real step on `map` with the map chance forced to
        /// `chance` (setting restored after). "PLANTED n" = trees added by this run.
        /// </summary>
        public static string ProofMapStep(Map map, float chance)
        {
            GenStepDef def = DefDatabase<GenStepDef>.GetNamedSilentFail("RM_SweetlineTrees");
            if (map == null || !(def?.genStep is RM_GenStep_SweetlineTrees step) || step.treeDef == null)
            {
                return "REFUSED: no map or no RM_SweetlineTrees step";
            }
            float keep = RM_LeaningScrubSettings.sweetlineTreeMapChance;
            int before = map.listerThings.ThingsOfDef(step.treeDef).Count;
            try
            {
                RM_LeaningScrubSettings.sweetlineTreeMapChance = chance;
                step.Generate(map, default(GenStepParams));
            }
            finally
            {
                RM_LeaningScrubSettings.sweetlineTreeMapChance = keep;
            }
            return "PLANTED " + (map.listerThings.ThingsOfDef(step.treeDef).Count - before);
        }

        private bool Fits(IntVec3 c, Map map, List<CellRect> used, List<IntVec3> placed)
        {
            if (c.CloseToEdge(map, edgeMargin) || !c.Standable(map) || c.Roofed(map))
            {
                return false;
            }
            TerrainDef terrain = c.GetTerrain(map);
            if (terrain == null || terrain.IsWater || map.fertilityGrid.FertilityAt(c) <= 0f)
            {
                return false;
            }
            if (c.GetEdifice(map) != null)
            {
                return false;
            }
            if (used != null)
            {
                for (int i = 0; i < used.Count; i++)
                {
                    if (used[i].Contains(c))
                    {
                        return false;
                    }
                }
            }
            for (int i = 0; i < placed.Count; i++)
            {
                if (placed[i].InHorDistOf(c, minTreeSpacing))
                {
                    return false;
                }
            }
            // An existing tree of ours already on the map (a second step run, a dev spawn) also spaces.
            List<Thing> standing = RM_SweetlineScratching.TreesOn(map);
            if (standing != null)
            {
                for (int i = 0; i < standing.Count; i++)
                {
                    if (standing[i].Spawned && standing[i].Position.InHorDistOf(c, minTreeSpacing))
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        private bool Plant(IntVec3 c, Map map)
        {
            List<Thing> here = c.GetThingList(map);
            for (int i = here.Count - 1; i >= 0; i--)
            {
                Thing t = here[i];
                if (t is Plant || t.def.category == ThingCategory.Item || t.def.category == ThingCategory.Filth)
                {
                    t.Destroy();
                }
            }
            if (c.GetThingList(map).Count > 0)
            {
                return false;
            }
            Plant tree = (Plant)ThingMaker.MakeThing(treeDef);
            tree.Growth = 1f;
            tree.Age = ancientAgeYears * GenDate.TicksPerYear;
            GenSpawn.Spawn(tree, c, map);
            return true;
        }
    }
}
