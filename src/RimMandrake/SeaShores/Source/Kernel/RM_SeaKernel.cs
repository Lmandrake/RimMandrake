using System;
using System.Collections.Generic;

namespace RimMandrake.SeaShores
{
    // Verse-free decisions of mandrake.rm.seashores: which sea a terrain / a tile / a cell belongs to, which catch band answers, whether a
    // frozen-world tile is healed. RM_SeaShoreUtility, the Harmony patches and the healer call these; the seeded fuzz under Source/SelfTest
    // compiles THIS file directly (a `using Verse;` here breaks that build).
    public static class RM_SeaKernel
    {
        /// <summary>First non-null of the four-step resolution: the extension's own field, the sea's ocean pair, its water pair, the vanilla pair (lazy: the vanilla DefOf is only touched when every earlier rung is empty).</summary>
        public static T FirstNonNull<T>(T extension, T oceanPair, T waterPair, Func<T> vanilla) where T : class
        {
            return extension ?? oceanPair ?? waterPair ?? vanilla();
        }

        public struct SeaTerrains<TSea, TTerrain> where TSea : class where TTerrain : class
        {
            public TSea Sea; public TTerrain Deep, Shallow;
        }

        /// <summary>Terrain -> sea, but ONLY for terrain no other sea and no `ambiguous` (vanilla / shared) water uses. Two seas laying the same
        /// terrain drop it from the map entirely; the order the seas are given in must not change the answer.</summary>
        public static Dictionary<TTerrain, TSea> BuildTerrainKeys<TSea, TTerrain>(IEnumerable<SeaTerrains<TSea, TTerrain>> seas, IEnumerable<TTerrain> initiallyAmbiguous)
            where TSea : class where TTerrain : class
        {
            var terrainToSea = new Dictionary<TTerrain, TSea>();
            var ambiguous = new HashSet<TTerrain>(initiallyAmbiguous);
            foreach (SeaTerrains<TSea, TTerrain> s in seas)
            {
                Register(terrainToSea, s.Deep, s.Sea, ambiguous);
                Register(terrainToSea, s.Shallow, s.Sea, ambiguous);
            }
            foreach (TTerrain t in ambiguous) terrainToSea.Remove(t);
            return terrainToSea;
        }

        private static void Register<TSea, TTerrain>(Dictionary<TTerrain, TSea> map, TTerrain terrain, TSea sea, HashSet<TTerrain> ambiguous)
            where TSea : class where TTerrain : class
        {
            if (terrain == null || ambiguous.Contains(terrain)) return;
            TSea existing;
            if (map.TryGetValue(terrain, out existing) && existing != sea)
            {
                ambiguous.Add(terrain);
                return;
            }
            map[terrain] = sea;
        }

        /// <summary>The sea a land tile faces: the one holding the most of its neighbours (`neighbourSeas` has null for a neighbour that is not a sea).
        /// Ties break on the lower ordinal defName so a repaint of the same planet lays the same shore twice.</summary>
        public static TSea PrimarySea<TSea>(IList<TSea> neighbourSeas, Func<TSea, string> nameOf) where TSea : class
        {
            TSea best = null;
            int bestCount = 0;
            for (int i = 0; i < neighbourSeas.Count; i++)
            {
                TSea biome = neighbourSeas[i];
                if (biome == null) continue;
                int count = 0;
                for (int j = 0; j < neighbourSeas.Count; j++)
                    if (neighbourSeas[j] == biome) count++;
                if (count > bestCount || (count == bestCount && best != null && string.CompareOrdinal(nameOf(biome), nameOf(best)) < 0))
                {
                    best = biome;
                    bestCount = count;
                }
            }
            return best;
        }

        /// <summary>Which sea's water a map cell is: its own terrain if that terrain belongs to exactly one sea (`keyed`), otherwise the sea the tile
        /// faces - but only when the cell really carries that sea's deep or shallow water.</summary>
        public static TSea CellSea<TSea>(TSea keyed, TSea facedSea, bool terrainKnown, bool terrainIsFacedDeep, bool terrainIsFacedShallow) where TSea : class
        {
            if (terrainKnown && keyed != null) return keyed;
            if (facedSea == null || !terrainKnown) return null;
            return (terrainIsFacedDeep || terrainIsFacedShallow) ? facedSea : null;
        }

        /// <summary>The empty-band rule vanilla has no equivalent of: an EMPTY preferred band falls back to the other salt/fresh pair (RUT_TheScald keeps
        /// its salt catches under freshwater_*). Never returns null.</summary>
        public static List<T> BandFor<T>(List<T> preferred, List<T> fallback, List<T> empty)
        {
            if (preferred != null && preferred.Count > 0) return preferred;
            return fallback ?? empty;
        }

        /// <summary>Whether a sea's catch table answers a fishing cell / water body instead of the land biome's.</summary>
        public static bool CatchTableApplies(bool settingOn, bool hasMap, bool seaFound, bool seaHasFishTypes, bool providesCatch)
        {
            return settingOn && hasMap && seaFound && seaHasFishTypes && providesCatch;
        }

        /// <summary>Vanilla returns before rolling shouldHaveFish when the LAND biome has no fishTypes at all - the common case beside a sea.</summary>
        public static bool RollShouldHaveFish(bool landBiomeHasFishTypes)
        {
            return !landBiomeHasFishTypes;
        }

        public static bool ShoreSuppressed(bool generateSeaShoresSetting, bool seaKnown, bool seaGeneratesShore)
        {
            if (!generateSeaShoresSetting) return true;
            return seaKnown && !seaGeneratesShore;
        }

        public enum HealAction { Skip, Already, Heal, Replace }

        /// <summary>What the frozen-world healer does to one land tile.</summary>
        public static HealAction Heal(bool buildableLand, bool facesSea, bool hasVanillaCoastMutator, bool hasVanillaOceanNeighbour, bool hasAnyCoastCategoryMutator)
        {
            if (!buildableLand || !facesSea) return HealAction.Skip;
            bool stale = hasVanillaCoastMutator && !hasVanillaOceanNeighbour;
            if (hasAnyCoastCategoryMutator && !stale) return HealAction.Already;
            return stale ? HealAction.Replace : HealAction.Heal;
        }

        /// <summary>Distinct directions in first-seen order, from the neighbours whose sea counts as coast.</summary>
        public static List<TDir> CoastDirections<TDir>(IList<TDir> directions, IList<bool> countsAsCoast)
        {
            var dirs = new List<TDir>();
            for (int i = 0; i < directions.Count; i++)
            {
                if (!countsAsCoast[i]) continue;
                if (!dirs.Contains(directions[i])) dirs.Add(directions[i]);
            }
            return dirs;
        }
    }
}
