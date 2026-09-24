using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.SeaShores
{
    [StaticConstructorOnStartup]
    public static class RM_SeaShoresHarmony
    {
        public const string HarmonyId = "mandrake.rm.seashores";

        static RM_SeaShoresHarmony()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            // WorldGenStep_Mutators.TryAddMutator is private static, so it
            // cannot be reached by attribute.
            MethodInfo tryAdd = AccessTools.Method(typeof(WorldGenStep_Mutators), "TryAddMutator");
            if (tryAdd == null)
            {
                Log.Warning("[RM_SeaShores] WorldGenStep_Mutators.TryAddMutator not found; "
                          + "fresh worldgen will lay vanilla coasts beside modded seas. "
                          + "Existing worlds are still healed on load.");
            }
            else
            {
                harmony.Patch(tryAdd, prefix: new HarmonyMethod(
                    typeof(RM_Patch_TryAddMutator), nameof(RM_Patch_TryAddMutator.Prefix)));
            }
        }
    }

    // Vanilla CoastDirectionAt only ever sees BiomeDefOf.Ocean. Where it found
    // nothing, look again for a sea of ours and answer the same shape of answer:
    // same dedupe, same tile-hash-seeded pick, so the direction is stable across
    // loads and identical for every consumer (IsCoastal, Basin, RiverConfluence).
    [HarmonyPatch(typeof(World), nameof(World.CoastDirectionAt))]
    public static class RM_Patch_CoastDirectionAt
    {
        private static readonly List<PlanetTile> tmpNeighbours = new List<PlanetTile>();
        private static readonly List<Rot4> tmpDirs = new List<Rot4>();

        public static void Postfix(PlanetTile tile, ref Rot4 __result)
        {
            if (__result.IsValid || !RM_SeaShoresSettings.Cur.seasCountAsCoast || !tile.Valid)
            {
                return;
            }
            Tile t = tile.Tile;
            if (t?.PrimaryBiome == null || !t.PrimaryBiome.canBuildBase)
            {
                return;
            }
            WorldGrid grid = Find.WorldGrid;
            if (grid == null)
            {
                return;
            }

            tmpDirs.Clear();
            tmpNeighbours.Clear();
            grid.GetTileNeighbors(tile, tmpNeighbours);
            for (int i = 0; i < tmpNeighbours.Count; i++)
            {
                RM_SeaShoreExtension ext = RM_SeaShoreUtility.ExtensionOf(grid[tmpNeighbours[i]]?.PrimaryBiome);
                if (ext == null || !ext.countsAsCoast)
                {
                    continue;
                }
                Rot4 dir = grid.GetRotFromTo(tile, tmpNeighbours[i]);
                if (!tmpDirs.Contains(dir))
                {
                    tmpDirs.Add(dir);
                }
            }
            if (tmpDirs.Count == 0)
            {
                return;
            }

            Rand.PushState();
            Rand.Seed = tile.GetHashCode();
            int index = Rand.Range(0, tmpDirs.Count);
            Rand.PopState();
            __result = tmpDirs[index];
        }
    }

    // Worldgen asks for vanilla Coast the moment CoastDirectionAt is valid —
    // which, thanks to the postfix above, now includes tiles beside our seas.
    // Substitute our mutator there so the shore is laid with the sea's water.
    // A tile that genuinely borders the vanilla ocean is left alone.
    public static class RM_Patch_TryAddMutator
    {
        public static void Prefix(Tile tile, PlanetLayer layer, ref TileMutatorDef mutator)
        {
            if (mutator != TileMutatorDefOf.Coast || RM_SeaShoresDefOf.RM_SeaCoast == null || tile == null)
            {
                return;
            }
            if (HasVanillaOceanNeighbour(tile.tile, layer))
            {
                return;
            }
            if (RM_SeaShoreUtility.PrimarySeaFor(tile.tile) == null)
            {
                return;
            }
            mutator = RM_SeaShoresDefOf.RM_SeaCoast;
        }

        private static readonly List<PlanetTile> tmpNeighbours = new List<PlanetTile>();

        public static bool HasVanillaOceanNeighbour(PlanetTile tile, PlanetLayer layer)
        {
            if (layer == null || !tile.Valid)
            {
                return false;
            }
            tmpNeighbours.Clear();
            layer.GetTileNeighbors(tile, tmpNeighbours);
            for (int i = 0; i < tmpNeighbours.Count; i++)
            {
                if (layer[tmpNeighbours[i]]?.PrimaryBiome == BiomeDefOf.Ocean)
                {
                    return true;
                }
            }
            return false;
        }
    }

    // A water body made of a sea's water serves that SEA's fish, not the land
    // map's. Mirrors vanilla SetFishTypes exactly, including its two size
    // curves, with one addition: a band pair that is empty falls back to the
    // other pair, because RUT_TheScald keeps its catches in freshwater_* while
    // its terrain declares waterBodyType Saltwater.
    [HarmonyPatch(typeof(WaterBody), nameof(WaterBody.SetFishTypes))]
    public static class RM_Patch_SetFishTypes
    {
        public static void Postfix(WaterBody __instance, ref bool ___shouldHaveFish,
            List<ThingDef> ___commonFish, List<ThingDef> ___uncommonFish)
        {
            if (!RM_SeaShoresSettings.Cur.seaCatchTables || __instance?.map == null)
            {
                return;
            }
            BiomeDef sea = RM_SeaShoreUtility.SeaForWaterBody(__instance);
            RM_SeaShoreExtension ext = RM_SeaShoreUtility.ExtensionOf(sea);
            if (ext == null || !ext.providesCatch || sea.fishTypes == null)
            {
                return;
            }

            ___commonFish.Clear();
            ___uncommonFish.Clear();

            // Vanilla returns before rolling shouldHaveFish when the LAND biome
            // has no fishTypes at all, which is the common case beside a sea.
            if (__instance.map.Biome.fishTypes == null)
            {
                ___shouldHaveFish = Rand.Chance(
                    FishingUtility.ChanceForCommonFishFromWaterBodySizeCurve.Evaluate(__instance.Size));
            }
            if (!___shouldHaveFish)
            {
                return;
            }

            bool uncommon = Rand.Chance(
                FishingUtility.ChanceForUncommonFishFromWaterBodySizeCurve.Evaluate(__instance.Size));
            bool salt = __instance.waterBodyType == WaterBodyType.Saltwater;

            if (RM_SeaShoreUtility.BandFor(sea.fishTypes, salt, uncommon: false)
                    .TryRandomElement(out FishChance common) && common?.fishDef != null)
            {
                ___commonFish.Add(common.fishDef);
            }
            if (uncommon && RM_SeaShoreUtility.BandFor(sea.fishTypes, salt, uncommon: true)
                    .TryRandomElement(out FishChance rare) && rare?.fishDef != null)
            {
                ___uncommonFish.Add(rare.fishDef);
            }
        }
    }

    // FishingUtility.GetCatchesFor reads `pawn.Map.Biome` twice, both times to
    // reach fishTypes.rareCatchesSetMaker — the one catch path SetFishTypes
    // does not cover, because it is rolled at fishing time rather than cached
    // on the water body. Redirect those two loads to the biome that owns the
    // CELL being fished; FishBiomeFor returns map.Biome unchanged everywhere
    // else, so a non-sea map is bit-for-bit vanilla.
    [HarmonyPatch(typeof(FishingUtility), nameof(FishingUtility.GetCatchesFor))]
    public static class RM_Patch_RareCatches
    {
        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
        {
            MethodInfo getBiome = AccessTools.PropertyGetter(typeof(Map), nameof(Map.Biome));
            MethodInfo replacement = AccessTools.Method(typeof(RM_SeaShoreUtility),
                nameof(RM_SeaShoreUtility.FishBiomeFor));
            int hits = 0;

            foreach (CodeInstruction ci in instructions)
            {
                if (getBiome != null && replacement != null && ci.Calls(getBiome))
                {
                    hits++;
                    // Rewrite in place so labels and exception blocks on the
                    // original instruction survive; the Map is already on the
                    // stack, so push the cell (arg 1) and call our resolver.
                    ci.opcode = OpCodes.Ldarg_1;
                    ci.operand = null;
                    yield return ci;
                    yield return new CodeInstruction(OpCodes.Call, replacement);
                }
                else
                {
                    yield return ci;
                }
            }

            if (hits == 0)
            {
                Log.Warning("[RM_SeaShores] rare-catch transpiler matched no Map.Biome load in "
                          + "FishingUtility.GetCatchesFor; rare catches stay vanilla. "
                          + "Common and uncommon catches are unaffected.");
            }
        }
    }
}
