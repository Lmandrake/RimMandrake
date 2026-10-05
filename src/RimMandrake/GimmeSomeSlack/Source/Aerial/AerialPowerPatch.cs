using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// Real power across distance (design 2.2). VERIFIED in decompiled 1.6 (RimSage, 2026-10-02):
    /// PowerNetMaker.ContiguousPowerBuildings flood-fills over GenAdj.CellsAdjacentCardinal(Building), and its only
    /// entry is NewPowerNetStartingFrom, called only from PowerNetManager.TryCreateNetAt inside
    /// UpdatePowerNetsAndConnections_First (whose first pass also destroys the nets at the Thing-overload ring of a
    /// registering transmitter). Every net build -- spawn, despawn, map load/FinalizeInit, GenStep_Power, gravship
    /// landing, map deinit -- runs through those two methods. So: while (and only while) one of them is on the stack,
    /// the Thing overload of CellsAdjacentCardinal also returns the cells of an anchor's linked partners. Outside that
    /// scope the vanilla list is returned untouched, so no unrelated caller (FogGrid, ShipUtility, BuildingGroundSpawner,
    /// the nutrient paste dispenser ...) ever sees a remote "neighbour".
    /// </summary>
    internal static class AerialPowerScope
    {
        [ThreadStatic] internal static int depth;
        /// <summary>Probe-visible: postfix calls that appended partners (proves the hook fires live).</summary>
        public static int appendedCalls;
    }

    [HarmonyPatch(typeof(PowerNetManager), nameof(PowerNetManager.UpdatePowerNetsAndConnections_First))]
    internal static class Patch_PowerNetManager_UpdateFirst_Scope
    {
        private static void Prefix() => AerialPowerScope.depth++;
        private static Exception Finalizer(Exception __exception) { AerialPowerScope.depth--; return __exception; }
    }

    [HarmonyPatch(typeof(PowerNetMaker), nameof(PowerNetMaker.NewPowerNetStartingFrom))]
    internal static class Patch_PowerNetMaker_NewNet_Scope
    {
        private static void Prefix() => AerialPowerScope.depth++;
        private static Exception Finalizer(Exception __exception) { AerialPowerScope.depth--; return __exception; }
    }

    [HarmonyPatch(typeof(GenAdj), nameof(GenAdj.CellsAdjacentCardinal), new[] { typeof(Thing) })]
    internal static class Patch_GenAdj_CellsAdjacentCardinal_AerialLinks
    {
        private static void Postfix(Thing t, ref IEnumerable<IntVec3> __result)
        {
            if (AerialPowerScope.depth <= 0 || t == null || !CompAerialAnchor.IsAnchorDef(t.def)) return;
            CompAerialAnchor a = CompAerialAnchor.Of(t);
            if (a == null || a.links.Count == 0) return;
            List<IntVec3> extra = null;
            foreach (CompAerialAnchor p in a.LivePartners)
                (extra ??= new List<IntVec3>()).Add(p.Position);
            if (extra == null) return;
            AerialPowerScope.appendedCalls++;
            var all = new List<IntVec3>(__result);
            all.AddRange(extra);
            __result = all;
        }
    }
}
