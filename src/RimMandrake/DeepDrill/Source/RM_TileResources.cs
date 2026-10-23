using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DeepDrill
{
    // VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR (design/RimMandrake/vee_port_plan_2026-10-22.md §2 group O). The four VEE resource tile
    // mutators, ported as RM_DeepOreRich / RM_DeepOreDevoid / RM_MineralDevoid / RM_MineableComponentSpacer
    // (Defs/TileMutatorDefs/RM_TileResources.xml). Decisions live in Kernel/RM_TileResourceKernel.cs.
    //
    // Deep ores in 1.6 come from one place (RimSage): CompDeepScanner.DoFind writes a lump into map.deepResourceGrid with
    // thingDef.deepCountPerCell per cell. Rich scales that count; Devoid stops the scanner (CanUseNow says why, like vanilla's
    // "no bedrock"). Drilling base rock is untouched.

    /// <summary>Carried by a ported resource mutator. Numbers are Mod Settings, not fields, except the scatter blotch factor.</summary>
    public class RM_TileResourceExtension : DefModExtension
    {
        public RM_DeepOreKind deepOre = RM_DeepOreKind.None;
        /// <summary>RM_TileMutatorWorker_ScatterMineable: the mineable to scatter.</summary>
        public ThingDef scatterMineable;
        /// <summary>Lumps per 10k cells as a fraction of the map's resource blotches (vanilla obsidian deposits use 0.1).</summary>
        public float scatterBlotchFactor = 0.05f;
    }

    public static class RM_TileResources
    {
        public static float DeepOreFactor(Map map)
        {
            IList<TileMutatorDef> on = map?.TileInfo?.Mutators;
            if (on == null || on.Count == 0) return 1f;
            return RM_TileResourceKernel.DeepOreFactor(
                on.Select(m => m.GetModExtension<RM_TileResourceExtension>()?.deepOre ?? RM_DeepOreKind.None),
                RM_DeepDrillSettings.richDeepOreFactor, RM_DeepDrillSettings.deepOreFactorsEnabled);
        }

        /// <summary>Set by the DoFind prefix while a scanner writes its lump; DeepResourceGrid.SetAt scales by it.</summary>
        public static float activeScanFactor = 1f;
    }

    [HarmonyPatch(typeof(CompDeepScanner), nameof(CompDeepScanner.CanUseNow), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Deep-ore-devoid tiles", typeof(RM_DeepDrillSettings), "deepOreFactorsEnabled")]
    public static class Patch_DeepScanner_CanUseNow
    {
        public static void Postfix(CompDeepScanner __instance, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || !RM_DeepDrillSettings.deepOreFactorsEnabled || __instance?.parent?.Map == null) return;
            if (RM_TileResources.DeepOreFactor(__instance.parent.Map) <= 0f)
                __result = "No deep ores lie under this place: the scanner has nothing to find.";
        }
    }

    [HarmonyPatch(typeof(CompDeepScanner), "DoFind")]
    [RimMandrake.Shared.PatchFeature("Deep-ore-rich tiles", typeof(RM_DeepDrillSettings), "deepOreFactorsEnabled")]
    public static class Patch_DeepScanner_DoFind
    {
        public static bool Prefix(CompDeepScanner __instance)
        {
            RM_TileResources.activeScanFactor = 1f;
            if (!RM_DeepDrillSettings.deepOreFactorsEnabled) return true;
            float f = RM_TileResources.DeepOreFactor(__instance?.parent?.Map);
            if (f <= 0f) return false; // devoid: CanUseNow already refuses; a dev "find now" finds nothing
            RM_TileResources.activeScanFactor = f;
            return true;
        }

        public static void Finalizer()
        {
            RM_TileResources.activeScanFactor = 1f;
        }
    }

    [HarmonyPatch(typeof(DeepResourceGrid), nameof(DeepResourceGrid.SetAt))]
    [RimMandrake.Shared.PatchFeature("Deep-ore-rich tiles (grid)", typeof(RM_DeepDrillSettings), "deepOreFactorsEnabled")]
    public static class Patch_DeepResourceGrid_SetAt
    {
        public static void Prefix(ref int count)
        {
            float f = RM_TileResources.activeScanFactor;
            if (f != 1f && count > 0) count = RM_TileResourceKernel.ScaledCount(count, f);
        }
    }

    /// <summary>RM_MineralDevoid: after the rock is laid, every ore vein becomes the plain rock of its place.</summary>
    public class RM_TileMutatorWorker_MineralDevoid : TileMutatorWorker
    {
        private static readonly HashSet<string> Keep = new HashSet<string> { "ComponentIndustrial", "ComponentSpacer" };

        public RM_TileMutatorWorker_MineralDevoid(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostTerrain(Map map)
        {
            if (!RM_DeepDrillSettings.mineralDevoidEnabled) return;
            ThingDef fallback = Find.World?.NaturalRockTypesIn(map.Tile)?.FirstOrDefault();
            int stripped = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                Building ed = c.GetEdifice(map);
                BuildingProperties b = ed?.def?.building;
                if (b == null || !RM_TileResourceKernel.StripsToPlainRock(b.isResourceRock, b.mineableScatterCommonality, b.mineableThing?.defName, Keep))
                    continue;
                ThingDef rock = DeepDrillUtility.RockForTerrain(map.terrainGrid.BaseTerrainAt(c)) ?? fallback;
                if (rock == null) continue;
                GenSpawn.Spawn(rock, c, map, WipeMode.Vanish);
                stripped++;
            }
            if (Prefs.DevMode && stripped > 0)
                Log.Message("[RM DeepDrill] mineral devoid: " + stripped + " ore cells became plain rock on " + map);
        }
    }

    /// <summary>RM_MineableComponentSpacer: scatters the extension's mineable as lumps in natural rock (vanilla
    /// GenStep_ScatterLumpsMineable, as vanilla's obsidian deposits do).</summary>
    public class RM_TileMutatorWorker_ScatterMineable : TileMutatorWorker
    {
        public RM_TileMutatorWorker_ScatterMineable(TileMutatorDef def) : base(def)
        {
        }

        public override void GeneratePostTerrain(Map map)
        {
            RM_TileResourceExtension ext = def.GetModExtension<RM_TileResourceExtension>();
            if (!RM_DeepDrillSettings.spacerDepositsEnabled || ext?.scatterMineable == null) return;
            float per10k = RM_TileResourceKernel.ScatterPer10k(GenStep_RocksFromGrid.GetResourceBlotchesPer10KCellsForMap(map),
                ext.scatterBlotchFactor, RM_DeepDrillSettings.spacerDepositScale);
            if (per10k <= 0f) return;
            new GenStep_ScatterLumpsMineable
            {
                maxValue = float.MaxValue,
                countPer10kCellsRange = new FloatRange(per10k, per10k),
                forcedDefToScatter = ext.scatterMineable,
            }.Generate(map, default(GenStepParams));
        }
    }
}
