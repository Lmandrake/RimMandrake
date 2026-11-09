using System.Collections.Generic;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// Colonists step round a live fallen wire when there is a way round (pass 12, played on a generated colony: after a mortar
    /// dropped a lamp mast, its neighbours' live wires lay across the yard and colonists walked into them again and again, three of
    /// six knocked out at once). A cell a live fallen strand lies across is perceived as costly ground, the way vanilla prices a
    /// ground fire (+1000 on its cell, PathGrid.CalculatedCostAt's perceivedStatic branch): +600, so a pawn takes a detour of some
    /// forty cells rather than step on it, and still crosses when there is no other way (the re-string worker reaches his cut).
    /// Only while shocks are on: a harmless wire is just floor. The cost lives in the static perceived grid, so it is kept in step
    /// by RecalculatePerceivedPathCostAt on each cell whose state changed (<see cref="Sync"/>, after every contact rebuild).
    /// </summary>
    [RimMandrake.Shared.PatchFeature("Live fallen wires: colonists step round them", typeof(AerialSettings), "fallenWireShock")]
    [HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
    public static class RM_LiveWirePathCost
    {
        public const int Cost = 600;
        private static readonly Dictionary<int, HashSet<int>> byMap = new Dictionary<int, HashSet<int>>();
        public static int recalcs;

        public static void Postfix(PathGrid __instance, IntVec3 c, bool perceivedStatic, ref int __result)
        {
            if (!perceivedStatic || __result >= 10000) return;
            Map map = __instance.map;
            if (map == null || !byMap.TryGetValue(map.uniqueID, out HashSet<int> cells) || cells.Count == 0) return;
            if (cells.Contains(map.cellIndices.CellToIndex(c))) __result += Cost;
        }

        /// <summary>Bring the priced cells of <paramref name="map"/> to its live contacts, re-pricing only the cells that changed.</summary>
        public static void Sync(Map map, Dictionary<int, IntVec3> contacts)
        {
            if (map == null) return;
            if (!byMap.TryGetValue(map.uniqueID, out HashSet<int> cur)) byMap[map.uniqueID] = cur = new HashSet<int>();
            bool on = AerialSettings.fallenWireShock;
            var changed = new List<int>();
            foreach (int i in cur) if (!on || !contacts.ContainsKey(i)) changed.Add(i);
            if (on) foreach (int i in contacts.Keys) if (!cur.Contains(i)) changed.Add(i);
            if (changed.Count == 0) return;
            foreach (int i in changed) { if (!cur.Remove(i)) cur.Add(i); }
            foreach (int i in changed)
            {
                map.pathing.RecalculatePerceivedPathCostAt(map.cellIndices.IndexToCell(i));
                recalcs++;
            }
        }

        public static int CountOn(Map map) => map != null && byMap.TryGetValue(map.uniqueID, out HashSet<int> s) ? s.Count : 0;

        /// <summary>A new game or a load: map ids repeat, so the last game's priced cells must not price this one's.</summary>
        public static void Clear() => byMap.Clear();
    }
}
