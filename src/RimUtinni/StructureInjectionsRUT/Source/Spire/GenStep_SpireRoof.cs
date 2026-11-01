using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // Thick rock over the whole hull: the seal stays the only way in, against pods and shells alike.
    // Linked to RUT_SpireSite after the structure step, so the hull walls are already on the map.
    public class GenStep_SpireRoof : GenStep
    {
        public override int SeedPart => 794122601;

        public override void Generate(Map map, GenStepParams parms)
        {
            ThingDef hull = DefDatabase<ThingDef>.GetNamed("RUT_SpireHullWall");
            List<Thing> walls = map.listerThings.ThingsOfDef(hull);
            if (walls.Count == 0)
            {
                Log.Error("[SPIRE] no hull on the map: the structure step did not place RUT_Spire_HighCommand");
                return;
            }
            int minX = map.Size.x, minZ = map.Size.z, maxX = 0, maxZ = 0;
            foreach (Thing wall in walls)
            {
                IntVec3 c = wall.Position;
                minX = System.Math.Min(minX, c.x);
                minZ = System.Math.Min(minZ, c.z);
                maxX = System.Math.Max(maxX, c.x);
                maxZ = System.Math.Max(maxZ, c.z);
            }
            foreach (IntVec3 c in CellRect.FromLimits(minX, minZ, maxX, maxZ))
            {
                map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThick);
            }
        }
    }
}
