using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// A spark off a live cut end, where that end is now (owner 2026-11-07: "the spark of the cut powerline should follow the writhing
    /// edge of the cable"). Vanilla's ThrowMicroSparks would not do: MicroSparks takes 0.75 s to fade in (Fleck_Visual.xml) and vanilla throws it
    /// up and to the right whatever the wire is doing, so the visible sparks hung in a cloud off to one side. These use MicroSparksFast
    /// (0.15 s in), small, thrown off the end the way it points, on Unity's own random so a draw never moves the game's.
    /// </summary>
    internal static class TipSparks
    {
        /// <summary>Ticks between sparks from one end at intensity 1.</summary>
        public const int Period = 24;

        private static FleckDef def;
        private static FleckDef Def => def ?? (def = DefDatabase<FleckDef>.GetNamedSilentFail("MicroSparksFast") ?? FleckDefOf.MicroSparks);

        public static void Throw(Map map, float x, float z, float outX, float outZ)
        {
            var loc = new Vector3(x, AltitudeLayer.MoteOverhead.AltitudeFor(), z);
            if (!loc.ShouldSpawnMotesAt(map)) return;
            FleckCreationData d = FleckMaker.GetDataStatic(loc, map, Def, Random.Range(0.32f, 0.55f));
            d.rotationRate = Random.Range(-40f, 40f);
            // velocityAngle: 0 = screen up, 90 = screen right
            d.velocityAngle = Mathf.Atan2(outX, outZ) * Mathf.Rad2Deg + Random.Range(-55f, 55f);
            d.velocitySpeed = Random.Range(0.12f, 0.4f);   // slow enough that the sparks stay round the end they came off, not a cloud beside it
            map.flecks.CreateFleck(d);
        }
    }
}
