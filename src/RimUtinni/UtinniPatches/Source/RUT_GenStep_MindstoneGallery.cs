using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1 (slate row 6 of
    // design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md; canon
    // design/Jawa/worldbuilding/creatures/RUT_mechanoid_origin_canon.md §2b, name ruling N1).
    //
    // A mindstone gallery the Shard-minds keep: on a new Lantern Deep, the natural rock face
    // around one Shard-mind is threaded with RUT_MindstoneVein, which mines out to RUT_Mindstone.
    // This genstep is the ONLY source (the vein has mineableScatterCommonality 0 and is no deep
    // resource), so the mindstone is findable here and only here. Campaign tier: wired into
    // RM_LanternDeepGenerator from Utinni by Patches/RUT_LanternDeepMindstoneGallery.xml.
    // Knowledge gate (owner, hard): no text here says who else wants the crystal.
    public class RUT_GenStep_MindstoneGallery : GenStep
    {
        public ThingDef veinDef;
        public IntRange veins = new IntRange(3, 5);
        public float radius = 10f;

        public override int SeedPart => 551803227;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (UtinniPatchesSettings.mindstoneGalleryEnabled)
            {
                Place(map, veinDef, veins.RandomInRange, radius);
            }
        }

        public static string Place(Map map, ThingDef vein, int want, float radius)
        {
            ThingDef mind = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ShardMind");
            if (vein == null || mind == null)
            {
                return "no defs";
            }
            Thing keeper = map.listerThings.ThingsOfDef(mind).RandomElementWithFallback();
            if (keeper == null)
            {
                return "no shard-mind";
            }
            // The gallery's walls: natural rock facing open floor, within reach of the mind.
            List<Building> face = GenRadial.RadialCellsAround(keeper.Position, radius, false)
                .Where(c => c.InBounds(map))
                .Select(c => c.GetEdifice(map))
                .Where(b => b != null && b.def.building != null && b.def.building.isNaturalRock && b.def != vein
                            && GenAdj.CellsAdjacentCardinal(b).Any(a => a.InBounds(map) && a.Standable(map)))
                .Distinct()
                .InRandomOrder()
                .Take(want)
                .ToList();
            int placed = 0;
            foreach (Building rock in face)
            {
                IntVec3 c = rock.Position;
                rock.Destroy(DestroyMode.Vanish);
                GenSpawn.Spawn(ThingMaker.MakeThing(vein), c, map);
                placed++;
            }
            return "veins=" + placed + " keeper=" + keeper.Position;
        }
    }

    // jawa/static_call proof (validation.py, mindstone_gallery): run the real placement on the
    // current map (a Lantern Deep with a Shard-mind).
    public static class RUT_MindstoneGalleryProof
    {
        public static string ProofGallery(string unused)
        {
            Map map = Find.CurrentMap;
            ThingDef vein = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_MindstoneVein");
            return map == null ? "no map" : RUT_GenStep_MindstoneGallery.Place(map, vein, 4, 10f);
        }
    }
}
