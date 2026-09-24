// Selftest for mandrake.rm.seashores (SEA_FLOOR_AND_CATCH_PASS_1).
//
// TWO THINGS ARE REAL, compiled straight from production source:
//   RM_SeaShoreUtility.DeepTerrainOf / ShallowTerrainOf - the four-step
//     resolution order that decides what a sea's shore is made of, driven by
//     bare BiomeDef/TerrainDef instances carrying a real RM_SeaShoreExtension.
//     🔴 Those defs are made with FormatterServices.GetUninitializedObject, NOT
//     `new`: TerrainDef's constructor reaches Verse.BaseContent, whose static
//     initializer loads shaders through UnityEngine.Resources and throws
//     "ECall methods must be packaged into a system module" outside a Unity
//     player. Aftermath's SelfTest gets away with `new RM_AftermathRuleDef()`
//     because a plain Def does not touch BaseContent; a BuildableDef does.
//   RM_SeaShoreUtility.BandFor - the empty-band fallback that keeps
//     RUT_TheScald fishable, since its catches are authored under
//     freshwater_* while the terrain its shore lays declares Saltwater.
//
// NOT covered, and why: everything else in the mod reads Find.WorldGrid,
// DefDatabase or a live Map. PrimarySeaFor/SeaForCell walk the world grid;
// the mutator worker needs a Map; every Harmony patch needs the game. The
// final fallback rung of the terrain resolution (TerrainDefOf.WaterOceanDeep
// / WaterOceanShallow) is likewise unreachable here - DefOfs are null with no
// DefDatabase - so the cases below stop one rung short of it deliberately
// rather than asserting null and calling it a result.
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\Rimworld\src\RimMandrake\SeaShores\Source\SelfTest\RimMandrakeSeaShores.SelfTest.csproj -c Release

using System;
using System.Collections.Generic;
using System.Runtime.Serialization;
using RimWorld;
using Verse;

namespace RimMandrake.SeaShores.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new List<string>();
        private static readonly List<string> Fail = new List<string>();

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
            }
            catch (Exception ex)
            {
                Fail.Add(name + ": " + ex.Message);
            }
        }

        private static void Expect(bool condition, string message)
        {
            if (!condition)
            {
                throw new Exception(message);
            }
        }

        // TerrainDef's and ThingDef's constructors touch Verse.BaseContent, whose
        // static initializer loads shaders through UnityEngine.Resources and dies
        // outside a Unity player ("ECall methods must be packaged into a system
        // module"). Nothing here needs a CONSTRUCTED def - only distinct reference
        // identities to compare - so the constructor is skipped outright.
        private static T Bare<T>() where T : Def
        {
            return (T)FormatterServices.GetUninitializedObject(typeof(T));
        }

        private static TerrainDef Terrain(string defName)
        {
            TerrainDef t = Bare<TerrainDef>();
            t.defName = defName;
            return t;
        }

        private static BiomeDef Sea(RM_SeaShoreExtension ext)
        {
            BiomeDef sea = Bare<BiomeDef>();
            sea.defName = "TestSea";
            sea.modExtensions = new List<DefModExtension> { ext };
            return sea;
        }

        private static FishChance Fish(string defName)
        {
            ThingDef thing = Bare<ThingDef>();
            thing.defName = defName;
            return new FishChance { fishDef = thing, chance = 1f };
        }

        private static int Main()
        {
            TerrainDef fromExt = Terrain("Ext_Deep");
            TerrainDef fromOcean = Terrain("Ocean_Deep");
            TerrainDef fromWater = Terrain("Water_Deep");

            Case("deep: extension field wins over both biome fields", () =>
            {
                BiomeDef sea = Sea(new RM_SeaShoreExtension { deepTerrain = fromExt });
                sea.oceanDeepTerrain = fromOcean;
                sea.waterDeepTerrain = fromWater;
                Expect(RM_SeaShoreUtility.DeepTerrainOf(sea) == fromExt,
                    "expected the extension's deepTerrain");
            });

            Case("deep: oceanDeepTerrain used when the extension is silent", () =>
            {
                BiomeDef sea = Sea(new RM_SeaShoreExtension());
                sea.oceanDeepTerrain = fromOcean;
                sea.waterDeepTerrain = fromWater;
                Expect(RM_SeaShoreUtility.DeepTerrainOf(sea) == fromOcean,
                    "expected oceanDeepTerrain, not waterDeepTerrain");
            });

            Case("deep: waterDeepTerrain is the last resort before vanilla", () =>
            {
                // This is exactly RUT_TheScald's shape without its extension
                // override: no oceanDeepTerrain at all, only the fresh pair.
                BiomeDef sea = Sea(new RM_SeaShoreExtension());
                sea.waterDeepTerrain = fromWater;
                Expect(RM_SeaShoreUtility.DeepTerrainOf(sea) == fromWater,
                    "expected waterDeepTerrain");
            });

            Case("shallow: extension field wins", () =>
            {
                TerrainDef extShallow = Terrain("Ext_Shallow");
                BiomeDef sea = Sea(new RM_SeaShoreExtension { shallowTerrain = extShallow });
                sea.oceanShallowTerrain = Terrain("Ocean_Shallow");
                Expect(RM_SeaShoreUtility.ShallowTerrainOf(sea) == extShallow,
                    "expected the extension's shallowTerrain");
            });

            Case("a biome with no extension is not a sea and resolves nothing", () =>
            {
                BiomeDef land = Bare<BiomeDef>();
                land.defName = "TestLand";
                land.oceanDeepTerrain = fromOcean;
                Expect(RM_SeaShoreUtility.DeepTerrainOf(land) == null,
                    "a non-sea biome must resolve to null, not to its own ocean terrain");
                Expect(RM_SeaShoreUtility.ShallowTerrainOf(land) == null,
                    "a non-sea biome must resolve to null");
            });

            Case("band: the populated band is used when it matches", () =>
            {
                BiomeFishTypes fish = new BiomeFishTypes();
                fish.saltwater_Common.Add(Fish("Salt"));
                fish.freshwater_Common.Add(Fish("Fresh"));
                Expect(RM_SeaShoreUtility.BandFor(fish, saltwater: true, uncommon: false)[0].fishDef.defName == "Salt",
                    "saltwater body must take the saltwater band");
                Expect(RM_SeaShoreUtility.BandFor(fish, saltwater: false, uncommon: false)[0].fishDef.defName == "Fresh",
                    "freshwater body must take the freshwater band");
            });

            Case("band: the Scald case - salt body, fresh-only table", () =>
            {
                BiomeFishTypes fish = new BiomeFishTypes();
                fish.freshwater_Common.Add(Fish("Eesh"));
                fish.freshwater_Uncommon.Add(Fish("Karrash"));
                Expect(RM_SeaShoreUtility.BandFor(fish, saltwater: true, uncommon: false)[0].fishDef.defName == "Eesh",
                    "an empty saltwater_Common must fall back to freshwater_Common");
                Expect(RM_SeaShoreUtility.BandFor(fish, saltwater: true, uncommon: true)[0].fishDef.defName == "Karrash",
                    "an empty saltwater_Uncommon must fall back to freshwater_Uncommon");
            });

            Case("band: both bands empty yields an empty list, never null", () =>
            {
                Expect(RM_SeaShoreUtility.BandFor(new BiomeFishTypes(), true, false).Count == 0,
                    "expected an empty band");
                Expect(RM_SeaShoreUtility.BandFor(null, true, true) != null,
                    "a null fishTypes must yield an empty band, not null");
            });

            foreach (string name in Pass)
            {
                Console.WriteLine("PASS  " + name);
            }
            foreach (string message in Fail)
            {
                Console.WriteLine("FAIL  " + message);
            }
            Console.WriteLine(Fail.Count == 0
                ? string.Format("{0}/{0} passed", Pass.Count)
                : string.Format("{0}/{1} passed", Pass.Count, Pass.Count + Fail.Count));
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
