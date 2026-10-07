using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1. PriceKey grammar (design §3 "Multiplier store"):
    /// a bucket is a per-def override (<c>def:X</c>, only where a rule names a
    /// specific def), a trade tag (<c>tag:X</c>) or a ThingCategory
    /// (<c>cat:X</c>). Buckets keep memory sane on a 600-mod item pool.
    /// </summary>
    public static class RM_BazaarPriceKeys
    {
        public static string DefKey(string defName) => "def:" + defName;
        public static string TagKey(string tag) => "tag:" + tag;
        public static string CategoryKey(string cat) => "cat:" + cat;

        private static readonly Dictionary<ThingDef, List<string>> cache = new Dictionary<ThingDef, List<string>>();

        /// <summary>Candidate keys for a def, most specific first: the def
        /// itself, its trade tags, then its categories walked up to the
        /// root. The first key a tile actually has a bucket for wins.</summary>
        public static List<string> KeysFor(ThingDef def)
        {
            if (def == null) return null;
            List<string> keys;
            if (cache.TryGetValue(def, out keys)) return keys;
            keys = new List<string> { DefKey(def.defName) };
            if (def.tradeTags != null)
            {
                for (int i = 0; i < def.tradeTags.Count; i++) keys.Add(TagKey(def.tradeTags[i]));
            }
            if (def.thingCategories != null)
            {
                for (int i = 0; i < def.thingCategories.Count; i++)
                {
                    int guard = 0;
                    for (ThingCategoryDef c = def.thingCategories[i]; c != null && guard < 16; c = c.parent, guard++)
                    {
                        string k = CategoryKey(c.defName);
                        if (!keys.Contains(k)) keys.Add(k);
                    }
                }
            }
            cache[def] = keys;
            return keys;
        }
    }

    /// <summary>
    /// The tags a settlement tile carries, for seed-rule matching. Every
    /// source is null-tolerant: FlowWorks absent, RimUtinni absent, a tile
    /// with no biome — each just contributes nothing.
    /// </summary>
    public static class RM_BazaarTags
    {
        /// <summary>Rainfall (mm/yr) below which a tile reads as arid.
        /// Vanilla's arid shrubland sits above this and desert below it.</summary>
        public const float AridRainfall = 400f;
        public const float HotTemperature = 25f;
        public const float ColdTemperature = 0f;

        /// <summary>
        /// The seam RimUtinni (or any campaign layer) uses to add settlement
        /// economy tags without this mod depending on it. Register from a
        /// [StaticConstructorOnStartup]; a provider that throws is logged once
        /// and dropped.
        /// </summary>
        public static readonly List<Func<PlanetTile, Faction, IEnumerable<string>>> providers =
            new List<Func<PlanetTile, Faction, IEnumerable<string>>>();

        public static void RegisterProvider(Func<PlanetTile, Faction, IEnumerable<string>> provider)
        {
            if (provider != null && !providers.Contains(provider)) providers.Add(provider);
        }

        public static HashSet<string> TagsFor(PlanetTile tile, Faction faction)
        {
            HashSet<string> tags = new HashSet<string>();
            if (!tile.Valid) return tags;

            Tile info = null;
            try { info = Find.WorldGrid[tile]; } catch { info = null; }
            if (info != null)
            {
                BiomeDef biome = info.PrimaryBiome;
                if (biome != null) tags.Add("biome:" + biome.defName);
                if (info.rainfall < AridRainfall) tags.Add("climate:arid");
                if (info.temperature > HotTemperature) tags.Add("climate:hot");
                if (info.temperature < ColdTemperature) tags.Add("climate:cold");
            }

            if (faction != null && faction.def != null) tags.Add("faction:" + faction.def.defName);

            AddLiquidTags(tile, tags);

            for (int i = providers.Count - 1; i >= 0; i--)
            {
                try
                {
                    IEnumerable<string> extra = providers[i](tile, faction);
                    if (extra != null) foreach (string t in extra) if (!t.NullOrEmpty()) tags.Add(t);
                }
                catch (Exception ex)
                {
                    Log.Error("[The Bazaar] A settlement tag provider threw and was removed: " + ex);
                    providers.RemoveAt(i);
                }
            }
            return tags;
        }

        // ── FlowWorks liquid tags, by reflection so there is no hard dependency ──
        // RM_WorldComponent_LiquidTags.TagForTile(PlanetTile) -> LiquidDef or null
        // (WORLDMAP_LIQUID_TAGS_1). A settlement sits on land; its liquid is the
        // tagged water on its own tile or an adjacent one ("brine-adjacent").
        private static bool liquidResolved;
        private static MethodInfo tagForTile;
        private static readonly List<PlanetTile> neighbours = new List<PlanetTile>();

        private static void AddLiquidTags(PlanetTile tile, HashSet<string> tags)
        {
            if (!liquidResolved)
            {
                liquidResolved = true;
                Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.LiquidTypes.RM_WorldComponent_LiquidTags");
                if (t != null)
                {
                    tagForTile = t.GetMethod("TagForTile", BindingFlags.Public | BindingFlags.Static, null,
                        new[] { typeof(PlanetTile) }, null);
                }
            }
            if (tagForTile == null) return;

            try
            {
                AddLiquid(tile, tags);
                neighbours.Clear();
                Find.WorldGrid.GetTileNeighbors(tile, neighbours);
                for (int i = 0; i < neighbours.Count; i++) AddLiquid(neighbours[i], tags);
            }
            catch (Exception ex)
            {
                Log.ErrorOnce("[The Bazaar] FlowWorks liquid-tag lookup failed; seeding continues without liquid tags: " + ex, 0x6BA2A1);
                tagForTile = null;
            }
        }

        private static void AddLiquid(PlanetTile tile, HashSet<string> tags)
        {
            Def liquid = tagForTile.Invoke(null, new object[] { tile }) as Def;
            if (liquid != null) tags.Add("liquid:" + liquid.defName);
        }
    }
}
