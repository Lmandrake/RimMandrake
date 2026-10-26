using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Minerals
{
    /// <summary>The surface adapter (MINERAL_SURFACE_BUILD_PER_BIOME; registry design §4, §6.3). Vanilla scatters every map's ore inside
    /// GenStep_RocksFromGrid.Generate (an internal GenStep_ScatterLumpsMineable), so hooking that one method reaches every map
    /// generator that makes rock, surface, underground and modded alike. Two things happen there:
    /// 1. Kept share: vanilla's own scatter picks each lump by RELATIVE weight, so once the policy zeroes governed veins the same number
    ///    of lumps would all go to what is left (an unregistered steel would gain every lump components and plasteel lost). Its lump
    ///    count is scaled by the live share of the original weight, so every def it still scatters keeps its vanilla expectation.
    /// 2. Placement: for map.Biome, each governed row in deposits gets EPM x vein multiplier x hilliness x area x nomadic factor worth of
    ///    lumps, rounded stochastically, placed with the vanilla scatter machinery (forced defs, natural rock only, tutorial-safe).
    /// Only defs vanilla would have scattered (original scatter > 0) are placed here; a 0-scatter vein (zersium, phrikite) has its own
    /// GenStep and is never placed twice. The placer registers with the policy only when both patches are installed.</summary>
    [StaticConstructorOnStartup]
    public static class RM_MineralSurface
    {
        public const string Owner = "RM_MineralSurface";
        public const string HarmonyId = "mandrake.rm.minerals";

        private static readonly AccessTools.FieldRef<GenStep_RocksFromGrid, float> MaxMineableValue =
            AccessTools.FieldRefAccess<GenStep_RocksFromGrid, float>("maxMineableValue");
        private static readonly AccessTools.FieldRef<GenStep_RocksFromGrid, bool> IgnoreMaxIfGravship =
            AccessTools.FieldRefAccess<GenStep_RocksFromGrid, bool>("ignoreMaxIfGravship");
        private static readonly AccessTools.FieldRef<GenStep_RocksFromGrid, float?> OverrideBlotches =
            AccessTools.FieldRefAccess<GenStep_RocksFromGrid, float?>("overrideBlotchesPer10kCells");

        // map generation runs on one thread. The depth counter only scopes the kept-share hook to "inside RocksFromGrid"; the ctx
        // fields are single-slot, so a nested RocksFromGrid (none known) would leave the outer call the inner one's context
        private static int depth;
        private static float ctxMaxValue = float.MaxValue;
        private static float ctxBlotches;
        private static float ctxShare = 1f;
        private static int ctxVanillaBefore = -1, ctxVanillaAfter = -1;

        private static int cachedRevision = -1;
        private static List<SurfaceTarget> cachedTargets = new List<SurfaceTarget>();

        /// <summary>Last map this adapter saw (proof hook and diagnostic).</summary>
        public static string LastMapReport { get; private set; } = "map=none";

        public static bool Registered { get; private set; }

        static RM_MineralSurface()
        {
            bool rocks = RM_MineralQuarry.Owns(AccessTools.Method(typeof(GenStep_RocksFromGrid), nameof(GenStep_RocksFromGrid.Generate)), p => p.Postfixes)
                      && RM_MineralQuarry.Owns(AccessTools.Method(typeof(GenStep_RocksFromGrid), nameof(GenStep_RocksFromGrid.Generate)), p => p.Prefixes);
            bool count = RM_MineralQuarry.Owns(AccessTools.Method(typeof(GenStep_ScatterLumpsMineable), "CalculateFinalCount"), p => p.Postfixes);
            if (!rocks || !count)
            {
                Log.Warning("[RM Minerals] surface placer NOT registered (RocksFromGrid patch " + (rocks ? "ok" : "missing") + ", scatter count patch "
                          + (count ? "ok" : "missing") + "): governed veins keep their vanilla scatter");
                return;
            }
            Registered = true;
            RM_MineralPolicy.RegisterSurfacePlacer(Owner);
        }

        private static List<SurfaceTarget> Targets()
        {
            if (cachedRevision != RM_MineralPolicy.Revision)
            {
                cachedTargets = RM_MineralSurfaceKernel.SurfaceTargets(RM_MineralPolicy.Rows, RM_MineralPolicy.LastDecisions, RM_MineralPolicy.OriginalsCopy());
                cachedRevision = RM_MineralPolicy.Revision;
            }
            return cachedTargets;
        }

        private static bool OverValue(ThingDef mineable, float maxValue)
        {
            ThingDef item = mineable?.building?.mineableThing;
            return item != null && item.BaseMarketValue > maxValue;
        }

        internal static void Begin(GenStep_RocksFromGrid step, Map map)
        {
            depth++;
            ctxShare = 1f; ctxVanillaBefore = ctxVanillaAfter = -1;
            // the same value rule as vanilla's own scatter (decompiled 1.6): the cap is lifted only for an Odyssey gravship landing
            ctxMaxValue = (ModsConfig.OdysseyActive && IgnoreMaxIfGravship(step) && map.wasSpawnedViaGravShipLanding) ? float.MaxValue : MaxMineableValue(step);
            float? ob = OverrideBlotches(step);
            ctxBlotches = ob ?? GenStep_RocksFromGrid.GetResourceBlotchesPer10KCellsForMap(map);
        }

        internal static void End() { if (depth > 0) depth--; }

        internal static bool InRocks => depth > 0;

        /// <summary>Scale vanilla's internal scatter count by the live share of the original weight it may pick from.</summary>
        internal static int KeepShare(int vanillaCount)
        {
            if (!RM_MineralsSettings.enabled || vanillaCount <= 0) return vanillaCount;
            var pairs = new List<KeyValuePair<float, float>>();
            foreach (ThingDef t in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (t?.building == null || OverValue(t, ctxMaxValue)) continue;
                float cur = t.building.mineableScatterCommonality;
                MineralDefInfo o = RM_MineralPolicy.Original(t.defName);
                float orig = o != null ? o.Scatter : cur;
                if (cur > 0f || orig > 0f) pairs.Add(new KeyValuePair<float, float>(cur, orig));
            }
            ctxShare = RM_MineralSurfaceKernel.KeptShare(pairs);
            ctxVanillaBefore = vanillaCount;
            ctxVanillaAfter = ctxShare >= 1f ? vanillaCount : RM_MineralSurfaceKernel.StochasticRound(vanillaCount * ctxShare, Rand.Value);
            return ctxVanillaAfter;
        }

        internal static void Place(Map map, GenStepParams parms)
        {
            if (!RM_MineralsSettings.enabled || map?.Biome == null || map.TileInfo == null || map.TileInfo.WaterCovered) return;
            string biome = map.Biome.defName;
            float nomadic = map.IsStartingMap ? 1f : Find.Storyteller.difficulty.nomadicMineableResourcesFactor;
            var queue = new List<ThingDef>();
            var perRow = new StringBuilder();
            foreach (SurfaceTarget t in Targets())
            {
                float? epm = RM_MineralPolicy.EffectiveValue(t.MaterialId, biome, RM_MineralsSettings.veinMultiplier);
                if (epm == null || !(epm.Value > 0f)) continue;
                var pool = new List<KeyValuePair<string, float>>();
                foreach (KeyValuePair<string, float> m in t.Mineables)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(m.Key);
                    if (d?.building != null && !OverValue(d, ctxMaxValue)) pool.Add(m);
                }
                if (pool.Count == 0) continue;
                int n = RM_MineralSurfaceKernel.StochasticRound(
                    RM_MineralSurfaceKernel.ExpectedLumps(epm.Value, t.UnitsPerCell, ctxBlotches, map.Area, nomadic), Rand.Value);
                for (int i = 0; i < n; i++)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(RM_MineralSurfaceKernel.PickMineable(pool, Rand.Value));
                    if (d != null) queue.Add(d);
                }
                perRow.Append(perRow.Length > 0 ? "," : "").Append(t.MaterialId).Append(':').Append(n);
            }
            int placedLumps = 0, placedCells = 0;
            if (queue.Count > 0)
            {
                queue.Shuffle();
                var step = new RM_GenStep_RegistryLumps { lumps = queue, count = queue.Count };
                step.Generate(map, parms);
                placedLumps = step.placedLumps; placedCells = step.placedCells;
            }
            int rock = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                Building e = map.edificeGrid[c];
                if (e?.def?.building != null && e.def.building.isNaturalRock) rock++;
            }
            LastMapReport = "map=" + map.uniqueID + ";biome=" + biome + ";blotches=" + ctxBlotches.ToString("0.##", CultureInfo.InvariantCulture)
                          + ";nomadic=" + nomadic.ToString("0.##", CultureInfo.InvariantCulture)
                          + ";share=" + ctxShare.ToString("0.000", CultureInfo.InvariantCulture)
                          + ";vanilla=" + ctxVanillaBefore + "->" + ctxVanillaAfter
                          + ";attempted=" + queue.Count + ";placed=" + placedLumps + ";cells=" + placedCells
                          + ";per1000rock=" + RM_MineralSurfaceKernel.OrePer1000Rock(placedCells, rock).ToString("0.0", CultureInfo.InvariantCulture)
                          + ";rows=" + perRow;
            if (queue.Count > 0 || ctxShare < 1f)
                Log.Message("[RM Minerals] surface (" + map + "): " + LastMapReport);
        }
    }

    /// <summary>Vanilla lump machinery with a fixed, pre-drawn list of defs: one lump per entry, natural rock only, minSpacing 5.</summary>
    public class RM_GenStep_RegistryLumps : GenStep_ScatterLumpsMineable
    {
        public List<ThingDef> lumps = new List<ThingDef>();
        public int placedLumps, placedCells;
        private int next;

        public override int SeedPart => 1489310227;

        protected override int CalculateFinalCount(Map map) { return count; }   // nomadic and hilliness are already in the count

        protected override ThingDef ChooseThingDef()
        {
            return next < lumps.Count ? lumps[next++] : null;
        }

        protected override void ScatterAt(IntVec3 c, Map map, GenStepParams parms, int stackCount = 1)
        {
            base.ScatterAt(c, map, parms, stackCount);
            if (recentLumpCells.Count > 0) { placedLumps++; placedCells += recentLumpCells.Count; recentLumpCells.Clear(); }
        }
    }

    [HarmonyPatch(typeof(GenStep_RocksFromGrid), nameof(GenStep_RocksFromGrid.Generate))]
    [RimMandrake.Shared.PatchFeature("Per-biome vein placement (surface adapter)")]
    public static class Patch_RocksFromGridSurface
    {
        public static void Prefix(GenStep_RocksFromGrid __instance, Map map) { RM_MineralSurface.Begin(__instance, map); }

        public static void Postfix(Map map, GenStepParams parms)
        {
            try { RM_MineralSurface.Place(map, parms); }
            catch (Exception e) { Log.Error("[RM Minerals] surface placement failed on " + map + ": " + e); }
        }

        public static void Finalizer() { RM_MineralSurface.End(); }
    }

    [HarmonyPatch(typeof(GenStep_ScatterLumpsMineable), "CalculateFinalCount")]
    [RimMandrake.Shared.PatchFeature("Unregistered ores keep their vanilla vein count")]
    public static class Patch_ScatterLumpsKeptShare
    {
        public static void Postfix(GenStep_ScatterLumpsMineable __instance, ref int __result)
        {
            // only vanilla's own internal scatter inside RocksFromGrid: exact type, no forced def
            if (!RM_MineralSurface.InRocks || __instance.GetType() != typeof(GenStep_ScatterLumpsMineable) || __instance.forcedDefToScatter != null) return;
            __result = RM_MineralSurface.KeepShare(__result);
        }
    }

    /// <summary>Bridge proof hooks for Minerals/validation.py (jawa/static_call).</summary>
    public static class RM_MineralSurfaceProof
    {
        /// <summary>"registered=0|1;placer=0|1;targets=a,b;map=&lt;id|none&gt;;biome=..;share=..;vanilla=a->b;attempted=..;placed=..;cells=..;per1000rock=..;rows=mat:n,.." (last map generated).</summary>
        public static string ProofState(string unused)
        {
            List<SurfaceTarget> t = RM_MineralSurfaceKernel.SurfaceTargets(RM_MineralPolicy.Rows, RM_MineralPolicy.LastDecisions, RM_MineralPolicy.OriginalsCopy());
            return "registered=" + (RM_MineralSurface.Registered ? 1 : 0) + ";placer=" + (RM_MineralPolicy.SurfacePlacerActive ? 1 : 0)
                 + ";targets=" + string.Join(",", t.Select(x => x.MaterialId)) + ";" + RM_MineralSurface.LastMapReport;
        }
    }
}
