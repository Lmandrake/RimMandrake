using System;
using Verse;
using HarmonyLib;

namespace RimMandrake.TerminalBiomes
{
    // GREYSEA_SALTDOME_SCATTER_OOB_1
    // ════════════════════════════════════════════════════════════════════
    // Vanilla defect, MEASURED against the decompiled 1.6 engine (RimSage,
    // 2026-09-27), in Verse.GenStep_ScatterThings.TryFindScatterCell:
    //
    //   if (clusterSize > 1) {
    //       if (leftInCluster <= 0) {
    //           if (!base.TryFindScatterCell(map, out clusterCenter))
    //               Log.Error("Could not find cluster center to scatter " + thingDef);
    //           leftInCluster = clusterSize;
    //       }
    //       leftInCluster--;
    //       result = CellFinder.RandomClosewalkCellNear(clusterCenter, map, 4, ...);
    //       return result.IsValid;
    //   }
    //
    // On a failed cluster-centre search it LOGS and keeps going instead of
    // bailing — `clusterCenter` is left at IntVec3.Invalid
    // ((-1000,-1000,-1000), per CellFinderLoose's own failure convention)
    // and gets fed straight into CellFinder.RandomClosewalkCellNear, whose
    // internal reachability walk (CellFinder.TryFindRandomReachableNearbyCell)
    // trips ThingGrid.ThingsListAt's own defensive bounds guard:
    // "Got ThingsListAt out of bounds: (-1000, -1000, -1000)"
    // (Verse/ThingGrid.cs, Log.ErrorOnce). Non-fatal, but log spam on every
    // map generation where the cluster search can fail — which our own
    // RM_GreySeaScatterShoreDomes (RM_GreySeaShoreScatter.xml) does on EVERY
    // non-Grey-Sea map, because its terrain filter (RM_GreySaltCrust) exists
    // nowhere else and is registered globally onto Base_Player.
    //
    // This is engine code, not ours to hand-edit — fixed here with Harmony,
    // same pattern this mod already uses for RM_Patch_GravEngineLaunchGate
    // (PatchAll'd from RM_TerminalBiomesMod's constructor; no extra wiring
    // needed for this class).
    //
    // THE FIX: force the method's own EXISTING safe branch
    // (`return base.TryFindScatterCell(map, out result);`) to run instead of
    // the buggy cluster branch whenever a fresh cluster centre is needed, by
    // presenting clusterSize as 1 for just that one call (Prefix), then
    // reading the result back (Postfix) — a genuinely found cell becomes the
    // cluster centre for subsequent calls in the same cluster; a genuine
    // failure bails immediately (debug-only log, no throw) with no cell ever
    // reaching CellFinder.RandomClosewalkCellNear. The mid-cluster reuse path
    // (`leftInCluster > 0`) is untouched by this patch and is safe by
    // construction: clusterCenter is only ever written here, only when found
    // valid.
    // ════════════════════════════════════════════════════════════════════
    [HarmonyPatch(typeof(GenStep_ScatterThings), "TryFindScatterCell")]
    internal static class RM_Patch_ScatterThingsClusterCenterGuard
    {
        private static readonly AccessTools.FieldRef<GenStep_ScatterThings, int> LeftInClusterRef =
            AccessTools.FieldRefAccess<GenStep_ScatterThings, int>("leftInCluster");

        private static readonly AccessTools.FieldRef<GenStep_ScatterThings, IntVec3> ClusterCenterRef =
            AccessTools.FieldRefAccess<GenStep_ScatterThings, IntVec3>("clusterCenter");

        // Set only while we have temporarily forced clusterSize to 1 for the
        // single call in flight; the value is the real clusterSize to
        // restore. RimWorld map generation is synchronous/single-threaded
        // (each GenStepDef's genStep instance is a shared singleton re-run
        // per new map, never concurrently), so a plain static is sufficient.
        private static int? forcedFromClusterSize;

        [HarmonyPrefix]
        private static bool Prefix(GenStep_ScatterThings __instance, Verse.Map map, ref IntVec3 result)
        {
            if (__instance.clusterSize <= 1)
            {
                return true; // vanilla non-cluster path; this bug cannot occur here.
            }

            if (LeftInClusterRef(__instance) > 0)
            {
                return true; // mid-cluster: clusterCenter was already validated in our own Postfix.
            }

            // A fresh cluster centre is needed. Route through the method's
            // own safe (non-cluster) branch instead of the buggy one.
            forcedFromClusterSize = __instance.clusterSize;
            __instance.clusterSize = 1;
            return true;
        }

        [HarmonyPostfix]
        private static void Postfix(GenStep_ScatterThings __instance, ref IntVec3 result, ref bool __result)
        {
            if (!forcedFromClusterSize.HasValue)
            {
                return;
            }

            int realClusterSize = forcedFromClusterSize.Value;
            forcedFromClusterSize = null;
            __instance.clusterSize = realClusterSize;

            if (!__result || !result.IsValid)
            {
                // Genuine failure, or another patch refused the cell (e.g. this map lays none of the required
                // terrain) — bail here rather than let anything downstream
                // feed IntVec3.Invalid to a bounds-checked cell search.
                if (Prefs.DevMode)
                {
                    Log.Message("[RimMandrake] GenStep_ScatterThings: no cluster centre for "
                        + __instance.thingDef?.defName + " (def " + __instance.def?.defName
                        + ") on this map — skipping this scatter attempt.");
                }
                LeftInClusterRef(__instance) = 0;
                __result = false;
                return;
            }

            // Found a genuine, CanScatterAt-validated cell: adopt it as the
            // cluster centre for this and the remaining clusterSize-1
            // placements, exactly as the (now-bypassed) vanilla branch
            // intended. `result` — this call's own placement — is the
            // centre cell itself, which is already a valid spot.
            ClusterCenterRef(__instance) = result;
            LeftInClusterRef(__instance) = realClusterSize - 1;
            __result = true;
        }

        // Defensive only: if the forced (single-cell) search itself throws,
        // make sure clusterSize is never left stuck at 1 on the instance.
        // Returns the original exception unchanged — this Finalizer exists
        // purely to restore state, never to swallow a real error.
        [HarmonyFinalizer]
        private static Exception Finalizer(GenStep_ScatterThings __instance, Exception __exception)
        {
            if (forcedFromClusterSize.HasValue)
            {
                __instance.clusterSize = forcedFromClusterSize.Value;
                forcedFromClusterSize = null;
            }
            return __exception;
        }
    }
}
